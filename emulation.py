from utils import *
from monitor import *
from multiprocessing import Process
import time
import json





class Emulation:
    def __init__(self, network, network_config = None, traffic_config = None, path='.'):
        self.network = network
        self.network_config = network_config
        self.traffic_config = traffic_config
       
        
        self.waitoutput = []
        self.call_first = []
        self.call_second = []
        self.path = path
        self.qmonitors = []
        self.tcp_probe = False
        self.cpu_usage = False

        self.orca_flows_counter = 0

    def configure_network(self, network_config=None):
        if network_config:
            if not self.network_config:
                self.network_config = network_config
            else:
                print("WARNING: exp already has a network config set. Overriding.")

        if not self.network_config:
            print("ERROR: no network config set for this experiment")
            exit(-1)

        # Configuration is a list of namedTuples that contain: source, dest, bw, delay, qsize
        for config in self.network_config:
            links = self.network.linksBetween(self.network.get(config.node1), self.network.get(config.node2))
            for link in links:
                self.configure_link(link, config.bw, config.delay, config.qsize, config.bidir)
    
    def configure_link(self, link, bw, delay, qsize, bidir):
        interfaces = [link.intf1, link.intf2]
        if bidir:
            n = 2
        else:
            n = 1
        for i in range(n):
            intf_name = interfaces[i].name
            node = interfaces[i].node
            
            if delay and not bw:
                cmd = 'sudo tc qdisc add dev %s root handle 1:0 netem delay %sms' % (intf_name, delay)
            elif bw and not delay:
                burst = int(10*bw*(2**20)/250/8)
                cmd = 'sudo tc qdisc add dev %s root handle 1:0 tbf rate %smbit burst %s limit %s' % (intf_name, bw, burst, qsize)
            elif delay and bw:
                burst = int(10*bw*(2**20)/250/8)
                cmd = 'sudo tc qdisc add dev %s root handle 1:0 netem delay %sms limit %s && sudo tc qdisc add dev %s parent 1:1 handle 10:0 tbf rate %smbit burst %s limit %s' % (intf_name, delay,  max(1000, 2*int(qsize/1500)), intf_name, bw, burst, qsize)
            else:
                print("ERROR: either the delay or bandiwdth must be specified")

            if 's' in intf_name:
                print("Running the following command in root terminal: %s" % cmd)
                os.system("sudo tc qdisc del dev %s  root 2> /dev/null" % intf_name)
                os.system(cmd)
            else:
                print("Running the following command in %s's terminal: %s" % (node.name, cmd))
                node.cmd("sudo tc qdisc del dev %s  root 2> /dev/null" % intf_name)
                node.cmd(cmd)

    def configure_traffic(self, traffic_config=None):
        '''
        This function should return two iterables:
        - One containing the list of set-up calls for each flow's server
        - One containing the list of set-up calls for each flow client
        '''
        if traffic_config:
            if not self.traffic_config:
                self.traffic_config = traffic_config
            else:
                print("WARNING: exp already has a network config set. Overriding.")

        if not self.traffic_config:
            print("ERROR: no network config set for this experiment")
            exit(-1)

        previous_start_time = 0

        for flowconfig in self.traffic_config:
            start_time = flowconfig.start
            duration = flowconfig.duration
            source_node = flowconfig.source
            destination = flowconfig.dest
            protocol = flowconfig.proto

            self.waitoutput.append(source_node)
            self.waitoutput.append(destination)

            if protocol == 'orca':
                params = (source_node,duration)
                command = self.start_orca_sender
                self.call_first.append(Command(command, params, None))

                params = (destination,source_node)
                command = self.start_orca_receiver
                self.call_second.append(Command(command, params, start_time - previous_start_time))
              
            elif protocol == 'cubic':
                # Create server start up call
                params = (destination,)
                command = self.start_iperf_server
                self.call_first.append(Command(command, params, None))

                # Create client start up call
                params = (source_node,destination,duration)
                command = self.start_iperf_client
                self.call_second.append(Command(command, params, start_time - previous_start_time))

            previous_start_time = start_time

    def run(self):
        for call in self.call_first:
            call.command(*call.params)

        for monitor in self.qmonitors:
            monitor.start()

        if self.tcp_probe:
            start_tcpprobe(self.path,"tcp_probe.txt")

        if self.cpu_usage:
            cpu_monitor = Process(target=monitor_cpu, args=(0.5,'%s/cpu' % (self.path)))
            cpu_monitor.start()


        for call in self.call_second:
            time.sleep(call.waiting_time)
            call.command(*call.params)

        for node_name in self.waitoutput:
            host = self.network.get(node_name)
            output = host.waitOutput()
            
            mkdirp(self.path)
            with open( '%s/%s_output.txt' % (self.path, node_name), 'w') as fout:
                fout.write(output)
        
        for monitor in self.qmonitors:
            if monitor is not None:
                monitor.terminate()

        if self.cpu_usage:
            if cpu_monitor is not None:
                cpu_monitor.terminate()

        if self.tcp_probe:
            stop_tcpprobe()


    def set_monitors(self, monitors, interval_sec=1):
        if "tcp_probe" in monitors:
            self.tcp_probe = True
            monitors.remove("tcp_probe")

        if "cpu_usage" in monitors:
            self.cpu_usage = True
            monitors.remove("cpu_usage")

        for monitor in monitors:
            node, interface = monitor.split('-')
            if 's' in node:
                iface = '%s-%s' % (node, interface)
                monitor = Process(target=monitor_qlen, args=(iface, interval_sec,'%s/queues' % (self.path)))
                self.qmonitors.append(monitor)
                

    def start_iperf_server(self, node_name, port=5201, monitor_interval=1):
        node = self.network.get(node_name)
        iperfArgs = 'iperf3 -p %d -i %s --one-off --json ' % (port, 5)
        cmd = iperfArgs + '-s' 
        print("Sending command '%s' to host %s" % (cmd, node.name))
        node.sendCmd(cmd)

    def start_iperf_client(self, node_name, destination_name, duration, port=5201, monitor_interval=1):
        node = self.network.get(node_name)
        destination =  self.network.get(destination_name)
        iperfArgs = 'iperf3 -p %d -i %s --json ' % (port, monitor_interval)
        cmd = iperfArgs + '-t %d -c %s' % (duration, destination.IP())
        print("Sending command '%s' to host %s" % (cmd, node.name))
        node.sendCmd(cmd)

    def start_orca_sender(self,node_name, duration, port=4444):
        node = self.network.get(node_name)
        orcacmd = 'sudo -u luca /home/luca/Orca/sender.sh %s %s %s' % (port,  self.orca_flows_counter, duration)
        print("Sending command '%s' to host %s" % (orcacmd, node.name))
        node.sendCmd(orcacmd)
        self.orca_flows_counter+= 1 

    def start_orca_receiver(self, node_name, destination_name, port=4444):
        node = self.network.get(node_name)
        destination = self.network.get(destination_name)
        orcacmd = 'sudo -u luca /home/luca/Orca/receiver.sh %s %s %s' % (destination.IP(), port, 0)
        print("Sending command '%s' to host %s" % (orcacmd, node.name))
        node.sendCmd(orcacmd)

    def dump_info(self):
        emulation_info = {}
        emulation_info['topology'] = str(self.network.topo)
        flows = []
        for config in self.traffic_config:
            flow = [config.source, config.dest, self.network.get(config.source).IP(), self.network.get(config.dest).IP(), config.start, config.proto]
            flows.append(flow)
        emulation_info['flows'] = flows
        with open(self.path + "/emulation_info.json", 'w') as fout:
            json.dump(emulation_info,fout)
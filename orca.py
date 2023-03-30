from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.util import waitListening
from subprocess import Popen, PIPE
from multiprocessing import Process
import matplotlib.pyplot as plt
import pandas as pd
import time
import re
import os
import json
from time import sleep, time
from subprocess import *
import subprocess
import re
from topologies import *


default_dir = '.'

def monitor_qlen(iface, interval_sec = 1, fname='%s/qlen.txt' % default_dir):
    pat_queued = re.compile(r'backlog\s[^\s]+\s([\d]+)p')
    cmd = "tc -s qdisc show dev %s" % (iface)
    ret = []
    open(fname, 'w').write('')
    open(fname + '.2', 'w').write('')
    while 1:
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.stdout.read()
        # Not quite right, but will do for now
        matches = pat_queued.findall(output)
        if matches:
            ret.append(matches[1])
            t = "%f" % time()
            open(fname, 'a').write(t + ',' + matches[0] + '\n')
            if len(matches) > 1: 
                open(fname + '.2', 'a').write(t + ',' + matches[1] + '\n')
        sleep(interval_sec)
    #open('qlen.txt', 'w').write('\n'.join(ret))
    return

def monitor_devs_ng(fname="%s/txrate.txt" % default_dir, interval_sec=0.01):
    """Uses bwm-ng tool to collect iface tx rate stats.  Very reliable."""
    cmd = ("sleep 1; bwm-ng -t %s -o csv "
           "-u bits -T rate -C ',' > %s" %
           (interval_sec * 1000, fname))
    Popen(cmd, shell=True).wait()

def start_tcpprobe(path,outfile="cwnd.txt"):
    os.system("rmmod tcp_probe; modprobe tcp_probe full=1;")
    Popen("cat /proc/net/tcpprobe > %s/%s" % (path, outfile),
          shell=True)

def stop_tcpprobe():
    Popen("killall -9 cat", shell=True).wait()

def start_qmon(iface, interval_sec=0.1, outfile="q.txt"):
    monitor = Process(target=monitor_qlen,
                      args=(iface, interval_sec, outfile))
    monitor.start()
    return monitor

def mkdirp( path ):
    try:
        os.makedirs( path )
    except OSError:
        if not os.path.isdir( path ):
            raise


def convert_to_mega_units(string):
    value, units = string.split(" ")
    if "K" in units:
        return float(value)/(2**10)
    elif "M" in units:
        return float(value)
    elif "G" in units:
        return float(value)*(2**10)
    else:
        return float(value)/(2**20)

def save_results(results, path):
    for key, value in results.items():
        with open('%s/keys.txt' % (path), 'w') as fout:
            fout.write('%s\n' % key)
        value.to_csv('%s/%s.csv' % (path, key))
    with open('%s/sysctl.txt' % (path), 'w') as fout:
        fout.write(subprocess.check_output(['sysctl', 'net.core.netdev_max_backlog']) + '\n')
        fout.write(subprocess.check_output(['sysctl', 'net.ipv4.tcp_rmem']) + '\n')
        fout.write(subprocess.check_output(['sysctl', 'net.ipv4.tcp_wmem']) + '\n')
        fout.write(subprocess.check_output(['sysctl', 'net.ipv4.tcp_mem']) + '\n')
        fout.write(subprocess.check_output(['sysctl', 'net.ipv4.tcp_window_scaling']) + 'n')

    uid = int(os.environ.get('SUDO_UID'))
    gid = int(os.environ.get('SUDO_GID'))

    os.chown('%s/keys.txt' % (path), uid, gid)
    os.chown('%s/sysctl.txt' % (path), uid, gid)


def plot_results(results, path):
    # Find all clients and servers
    clients = []
    servers = []
    for elem in results.keys():
        if 'c' in elem:
            clients.append(elem)
        elif 'x' in elem:
            servers.append(elem)

    # Throughput plot
    fig, ax = plt.subplots(1, 1)
    
    for server in servers:
        line = ax.plot(results[server]['time'], results[server]['bandwidth'], label='(%s,%s) - Receiver' % (server.replace('x', 'c'),server))
        ax.plot(results[server.replace('x', 'c')]['time'], results[server.replace('x', 'c')]['bandwidth'], c=line[-1].get_color(), label='(%s,%s) - Sender' % (server.replace('x', 'c'),server), linestyle='dashed')
    ax.set_xlabel('time (s)')
    ax.set_ylabel('Throughput (Mbit/sec)')
    ax.legend()
    ax.grid()

    plt.savefig("%s/throughput.png" % (path), dpi=720)

    # Cwnd plot
    fig, ax = plt.subplots(1, 1)
    
    for i, client in enumerate(clients):
        ax.plot(results[client]['time'], results[client]['cwnd'], label='Flow %s' % (i+1))
    

    ax.set_xlabel('time (s)')
    ax.set_ylabel('cwnd (pkts)')
    ax.legend()
    ax.grid()

    plt.savefig("%s/cwnd.png" % (path), dpi=720)

    # RTT plot
    fig, ax = plt.subplots(1, 1)
    
    for i, client in enumerate(clients):
        ax.plot(results[client]['time'], results[client]['rtt'], label='Flow %s' % (i+1))
    

    ax.set_xlabel('time (s)')
    ax.set_ylabel('rtt (ms)')
    ax.legend()
    ax.grid()

    plt.savefig("%s/rtt.png" % (path), dpi=720)

    # Queues plots

    LOGS = ['q_s1']
    q_dfs = {}
    for log in LOGS:
        data = pd.read_csv("%s/%s.txt" % (path,log), header=0, names=['time', 'value'])
        q_dfs[log] = data
    
    initial_values = []
    for key, value in q_dfs.items():
        initial_values.append(value.loc[0, 'time'])
    
    min_value = min(initial_values)

        
    fig, ax = plt.subplots(1, 1)

    for key, value in q_dfs.items():
       value['time'] = value['time'] - min_value

       ax.plot(value['time'], value['value'], label='%s' % (key))
    
    ax.set_xlabel('time (s)')
    ax.set_ylabel('Queue size (pkts)')
    ax.legend()
    ax.grid()

    plt.savefig("%s/queues.png" % (path), dpi=720)

    LOGS = ['q_s1.txt.2']
    q_dfs = {}
    for log in LOGS:
        data = pd.read_csv("%s/%s" % (path,log), header=0, names=['time', 'value'])
        q_dfs[log] = data
    
    initial_values = []
    for key, value in q_dfs.items():
        initial_values.append(value.loc[0, 'time'])
    
    min_value = min(initial_values)

        
    fig, ax = plt.subplots(1, 1)

    for key, value in q_dfs.items():
       value['time'] = value['time'] - min_value

       ax.plot(value['time'], value['value'], label='%s' % (key))
    
    ax.set_xlabel('time (s)')
    ax.set_ylabel('Queue size (pkts)')
    ax.legend()
    ax.grid()

    plt.savefig("%s/queues2.png" % (path), dpi=720)



    uid = int(os.environ.get('SUDO_UID'))
    gid = int(os.environ.get('SUDO_GID'))

    os.chown("%s/throughput.png" % (path), uid, gid)
    os.chown("%s/cwnd.png" % (path), uid, gid)
    os.chown("%s/rtt.png" % (path), uid, gid)
    os.chown("%s/queues.png" % (path), uid, gid)
    os.chown("%s/queues2.png" % (path), uid, gid)

def parse_tcp_probe(file, host_map):
    # Define the column names for the DataFrame
    columns = ['time', 'source', 'destination', 'packet_length', 'sequence_number', 'ack_number', 'cwnd', 'ssthresh', 'snd_wnd' ,'srtt', 'rcv_wnd']

    # Read the tcp_probe output file into a list of lines
    with open(file, 'r') as f:
        lines = f.readlines()


    # Split each line by whitespace and create a list of lists
    data = [line.strip().split() for line in lines]

    # Convert the list of lists into a pandas DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Convert the data types of the columns as needed
    df['time'] = df['time'].astype(float)
    df['sequence_number'] = df['sequence_number'].apply(lambda x: int(x,0))
    df['ack_number'] = df['ack_number'].apply(lambda x: int(x,0))
    df['cwnd'] = df['cwnd'].astype(int)
    df['ssthresh'] = df['ssthresh'].astype(int)
    df['snd_wnd'] = df['snd_wnd'].astype(int)
    df['srtt'] = df['srtt'].astype(float)
    df['rcv_wnd'] = df['rcv_wnd'].astype(int)

    results = {}
    for host, address in host_map.items():
        results[host] = df[df['source'] == address][['time','cwnd','snd_wnd','srtt']].copy()
    
    return results

def parseOrca(orcaOutput, offset):

    start_index = orcaOutput.find("----START----")
    end_index = orcaOutput.find("----END----")
    orcaOutput = orcaOutput[start_index:end_index]
 
    lines = orcaOutput.strip().split("\n")
    lines = [line for line in lines if line.strip() != '']
    
    
    # Extract the relevant information
    data = [line.split(",") for line in lines[1:]]
    columns = ["time", "bandwidth", "bytes"] if len(data[0]) == 3 else ["time", "bandwidth", "bytes", "totalgoodput"]
    
    # Create a pandas DataFrame
    df = pd.DataFrame(data, columns=columns)
    # Convert columns to appropriate types
    df["time"] = df["time"].astype(float)
    if len(columns) > 3:
        df["time"] = df["time"] + offset
    df["bandwidth"] = df["bandwidth"].astype(float) / 1000000
    df["bytes"] = df["bytes"].astype(float)
    if len(columns) > 3:
        df["totalgoodput"] = df["totalgoodput"].astype(float)
    
    return df


def parseIperf( iperfOutput, mode='last', time_offset = None):
    """Parse iperf output and return bandwidth.
        iperfOutput: string
        returns: result string"""
    
    r_client =  r"\[\s*(\d+)\]\s+(\d+\.?\d*-\d+\.?\d*)\s+sec\s+(\d+\.?\d*\s+[KMG]?Bytes)\s+(\d+\.?\d*\s+[KMG]?bits/sec)\s+(\d+)\s+(\d+\.?\d*\s+[KMG]?Bytes)"
    values_client = re.findall(r_client, iperfOutput )
    
    r_server =  r"\[\s*(\d+)\]\s+(\d+\.?\d*-\d+\.?\d*)\s+sec\s+(\d+\.?\d*\s+[KMG]?Bytes)\s+(\d+\.?\d*\s+[KMG]?bits/sec)"
    values_server = re.findall(r_server, iperfOutput )

    if len(values_client) > 2:
        if mode == 'last':
            # TODO:
            return values_client[-1]
        elif mode == 'series':
            ids = []
            time = []
            transferred = []
            bandwidth = []
            retr = []
            cwnd = []
            for x in values_client:
                ids.append(x[0])
                time.append(float(x[1].split('-')[-1]) + time_offset)
                transferred.append(convert_to_mega_units(x[2]))
                bandwidth.append(convert_to_mega_units(x[3]))
                retr.append(x[4])
                cwnd.append(convert_to_mega_units(x[5])*(2**20)/1500)

            return [time, transferred, bandwidth, retr, cwnd]
        else:
            print( 'mode not accepted')
    elif len(values_server) > 2:
        if mode == 'last':
            # TODO:
            return values_server[-1]
        elif mode == 'series':
            ids = []
            time = []
            transferred = []
            bandwidth = []
            for x in values_server:
                ids.append(x[0])
                time.append(float(x[1].split('-')[-1]) + time_offset)
                transferred.append(convert_to_mega_units(x[2]))
                bandwidth.append(convert_to_mega_units(x[3]))

            return [time, transferred, bandwidth]
        else:
            print( 'mode not accepted')
    
    else:
        # was: raise Exception(...)
        print( 'could not parse iperf output: ' + iperfOutput )
        return ''

def json_to_df( iperfOutput, time_offset = 0):
    snd_mss = iperfOutput['start']['tcp_mss_default']

    time = []
    transferred = []
    bandwidth = []
    retr = []
    cwnd = []
    rtt = []

    for interval in iperfOutput['intervals']:
        interval_data = interval['streams'][0]
        time.append(interval_data['end'] + time_offset)
        transferred.append(interval_data['bytes'] / (2**20))
        bandwidth.append(interval_data['bits_per_second'] / (2**20))
        if 'retransmits' in list(interval_data.keys()):
            retr.append(interval_data['retransmits'])
        if 'snd_cwnd' in list(interval_data.keys()):
            cwnd.append(interval_data['snd_cwnd'] / snd_mss)
        if 'rtt' in list(interval_data.keys()):
            rtt.append(interval_data['rtt'] / 1000)

    data_dict = {'time': time, 'transferred': transferred, 'bandwidth': bandwidth}
    if len(retr) > 0:
        data_dict['retr'] = retr
    if len(cwnd) > 0:
        data_dict['cwnd'] = cwnd
    if len(rtt) > 0:
        data_dict['rtt'] = rtt

    df = pd.DataFrame(data_dict)
    return df


def iperf(hosts, seconds, offsets, port=5201, monitor_interval=1, path='.'):
    """Run iperf between hosts.
        hosts: list of pair of hosts
        seconds: list of iperf time to transmit
        offsets: offset in starting time
        port: iperf port
        returns: two-element array of [ server, client ] speeds
        note: send() is buffered, so client rate can be much higher than
        the actual transmission rate; on an unloaded system, server
        rate should be much closer to the actual receive rate"""

    # Configure links host to switch:
    for client, server in hosts:
        burst = int(1*(10**9)/250/8)
        minburst = 1500*250
        client.cmd('sudo tc qdisc add dev %s-eth0 root tbf rate %sgbit burst  %s limit  %s ' % (client.name,1, burst, 1500*1000))
        server.cmd('sudo tc qdisc add dev %s-eth0 root tbf rate %sgbit burst  %s limit  %s ' % (server.name,1, burst, 1500*1000))

    # Start the servers
    for _, server in hosts:
        iperfArgs = 'iperf3 -p %d -i %s --one-off --json ' % (port, monitor_interval)
        cmd = iperfArgs + '-s' 
        print("Sending command '%s' to host %s" % (cmd, server.name))
        server.sendCmd(cmd)

    # Start the clients
    print([x + [y] + [z] for x, y, z in zip(hosts,seconds,offsets)])
    for client,server,s,f in [x + [y] + [z] for x, y, z in zip(hosts,seconds,offsets)]:
        sleep(f)
        iperfArgs = 'iperf3 -p %d -i %s --json ' % (port, monitor_interval)
        cmd = iperfArgs + '-t %d -c %s' % (s, server.IP())
        print("Sending command '%s' to host %s" % (cmd, client.name))
        client.sendCmd(cmd)
   

    results = {}
    offset_counter = 1
    for client, server in hosts:
        cliout = client.waitOutput()
        servout = server.waitOutput()

        with open('%s/%s.out' % (path, client.name), 'w') as fout:
            fout.write(cliout)

        with open('%s/%s.out' % (path, server.name), 'w') as fout:
            fout.write(servout)

        # results[client.name] = parseIperf( cliout, mode='series', time_offset= sum(offsets[:offset_counter]))
        # results[server.name] = parseIperf( servout, mode='series', time_offset= sum(offsets[:offset_counter]))
        results[client.name] = json_to_df(json.loads(cliout), time_offset= sum(offsets[:offset_counter]))
        results[server.name] = json_to_df(json.loads(servout), time_offset= sum(offsets[:offset_counter]))
        offset_counter += 1

    return results

def orca(hosts, seconds, offsets, port=5201, monitor_interval=1, path='.'):
    """Run iperf between hosts.
        hosts: list of pair of hosts
        seconds: list of iperf time to transmit
        offsets: offset in starting time
        port: iperf port
        returns: two-element array of [ server, client ] speeds
        note: send() is buffered, so client rate can be much higher than
        the actual transmission rate; on an unloaded system, server
        rate should be much closer to the actual receive rate"""

    sender_counter = 0
    host_address_map = {}
    for sender, receiver in hosts:
        orcacmd = 'sudo -u luca /home/luca/Orca/sender.sh %s %s %s' % (port + sender_counter, sender_counter+1, seconds[sender_counter])
        print("Sending command '%s' to host %s" % (orcacmd, sender.name))
        sender.sendCmd(orcacmd)
        host_address_map[sender.name] = '%s:%s' % (sender.IP(),port + sender_counter)
        sender_counter+=1
        sleep(1)

    # Start the senders
    flow_counter = 0
    for sender,receiver,s,f in [x + [y] + [z] for x, y, z in zip(hosts,seconds,offsets)]:
        sleep(f)
        orcacmd = 'sudo -u luca /home/luca/Orca/receiver.sh %s %s %s' % (sender.IP(), port + flow_counter, flow_counter + 1)
        print("Sending command '%s' to host %s" % (orcacmd, receiver.name))
        receiver.sendCmd(orcacmd)
        flow_counter+=1
        

    results = {}
    offset_counter = 1
    for client, server in hosts:
        cliout = client.waitOutput()
        servout = server.waitOutput()

        with open('%s/%s.out' % (path, client.name), 'w') as fout:
            fout.write(cliout)

        with open('%s/%s.out' % (path, server.name), 'w') as fout:
            fout.write(servout)

        results[client.name] = parseOrca( cliout, sum(offsets[:offset_counter]))
        results[server.name] = parseOrca( servout, sum(offsets[:offset_counter]))
        offset_counter+=1

    return results, host_address_map



def runPerf(net, hosts, seconds, offsets, monitor_interval, path):
    '''
    hosts: list of sender/receiver names pairs
    seconds: list of duration in seconds of each flow
    monitor_interval: period of iperf report
    offsets: list of offsets, i.e. how long to wait from last flow start before next start
    '''

    hosts = [net.get(sender, receiver) for sender,receiver in hosts]
    return iperf(hosts, seconds, offsets, monitor_interval= monitor_interval, path=path)

def runOrca(net, hosts, seconds, offsets, monitor_interval, path, port):
    '''
    hosts: list of sender/receiver names pairs
    seconds: list of duration in seconds of each flow
    monitor_interval: period of iperf report
    offsets: list of offsets, i.e. how long to wait from last flow start before next start
    '''

    hosts = [net.get(sender, receiver) for sender,receiver in hosts]
    return orca(hosts, seconds, offsets, monitor_interval= monitor_interval, path=path, port=port)
 

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    run = 0
    bw = 12
    DELAY = 10
    BDP = int(bw*(2**20)*DELAY*(10**(-3))*2/8)
    QSIZE = BDP 
    hostlinkrate = '1gbps'
    HOSTS=[('c1', 'x1'), ('c2', 'x2')]

    
    ROOT_PATH = "/home/luca/mininetproject/orca/run%s/%smbps_%s_%sqsize" % (run + 1, bw, DELAY, QSIZE/1500)
    mkdirp(ROOT_PATH)
    uid = int(os.environ.get('SUDO_UID'))
    gid = int(os.environ.get('SUDO_GID'))

    os.chown(ROOT_PATH, uid, gid)

    topo = DumbellTopo(n=2)
    net = Mininet(topo=topo)

    net.start()

    # --- Configure bottleneck link (both ways)
    os.system('sudo tc qdisc add dev s1-eth1 root handle 1: netem delay %sms' % (DELAY))
    os.system('sudo tc qdisc add dev s2-eth1 root handle 1: netem delay %sms' % (DELAY))


    # Burst calculation: tbf requires setting a burst value when limiting the rate. This value
    # must be high enough to allow your configured rate. Specifically, it must be at least the
    # specified rate / HZ, where HZ is clock rate, configured as a kernel parameter, and can be
    # extracted using the command shown below.
    #                egrep '^CONFIG_HZ_[0-9]+' /boot/config-$(uname -r)

    burst = int(bw*(10**6)/250/8)
    minburst = 1500*250

    os.system('sudo tc qdisc add dev s1-eth1 parent 1: handle 2: tbf rate %smbit burst %s limit %s ' % (bw, burst, QSIZE))
    os.system('sudo tc qdisc add dev s2-eth1 parent 1: handle 2: tbf rate %smbit burst %s limit %s ' % (bw, burst, QSIZE))

    # --- Configure links switch to host
    if hostlinkrate == '1gbps':
        burst = int(1*(10**9)/250/8)
    else:
        burst = int(bw*(10**6)/250/8)

    os.system('sudo tc qdisc add dev s1-eth2 root tbf rate %s burst  %s limit  %s ' % (hostlinkrate, burst, 1500*1000) )
    os.system('sudo tc qdisc add dev s1-eth3 root tbf rate %s burst  %s limit  %s ' % (hostlinkrate, burst, 1500*1000))

    os.system('sudo tc qdisc add dev s2-eth2 root tbf rate %s burst  %s limit  %s ' % (hostlinkrate, burst, 1500*1000))
    os.system('sudo tc qdisc add dev s2-eth3 root tbf rate %s burst  %s limit  %s ' % (hostlinkrate, burst, 1500*1000))
    
    hosts = [net.get(sender, receiver) for sender,receiver in HOSTS]

    # Configure links host to switch:
    for client, server in hosts:
        if hostlinkrate == '1gbps':
            burst = int(1*(10**9)/250/8)
        else:
            burst = int(bw*(10**6)/250/8)
        client.cmd('tc qdisc add dev %s-eth0 root tbf rate %s burst  %s limit  %s ' % (client.name,hostlinkrate, burst, 1500*1000))
        server.cmd('tc qdisc add dev %s-eth0 root tbf rate %s burst  %s limit  %s ' % (server.name,hostlinkrate, burst, 1500*1000))

    print( "Dumping host connections" )
    dumpNodeConnections(net.hosts)
    start_tcpprobe(ROOT_PATH,"cwnd.txt")
    qmon_switch = start_qmon(iface='s1-eth1', outfile='%s/q_s1.txt' % (ROOT_PATH))
    # qmon_sender = start_qmon(iface='c1-eth0', outfile='%s/q_c1.txt' % (ROOT_PATH))

    durations = [60,30]
    offsets = [0,30]

    results, host_address_map = runOrca(net, HOSTS, durations, offsets, 1 ,ROOT_PATH, port=4444)
    tcp_probe_results = parse_tcp_probe("%s/cwnd.txt" % ROOT_PATH, host_address_map)
    stop_tcpprobe()
    if qmon_switch is not None:
        qmon_switch.terminate()

    net.stop()


    # Cwnd plot
    fig, ax = plt.subplots(1, 1)
    
    for key, value in tcp_probe_results.items():
        ax.plot(value['time'], value['cwnd'], label='%s' % (key))
    

    ax.set_xlabel('time (s)')
    ax.set_ylabel('cwnd (pkts)')
    ax.axhline(y=2*BDP/1500, color='r', linestyle='--')
    ax.legend()
    ax.grid()

    plt.savefig("%s/cwnd.png" % (ROOT_PATH), dpi=720)


    # Cwnd plot
    fig, ax = plt.subplots(1, 1)
    
    for key, value in tcp_probe_results.items():
        data = value[(value['time'] >= 32) & (value['time'] <= 33)]
        ax.plot(data['time'] , data['cwnd'], label='%s' % (key), marker='.', linewidth=0.1)
    

    ax.set_xlabel('time (s)')
    ax.set_ylabel('cwnd (pkts)')
    ax.axhline(y=2*BDP/1500, color='r', linestyle='--')
    ax.legend()
    ax.grid()

    plt.savefig("%s/cwnd_zoomed.png" % (ROOT_PATH), dpi=720)



    # save_results(results, ROOT_PATH)
    plot_results(results, ROOT_PATH)

import os
import sys

script_dir = os.path.dirname( __file__ )
mymodule_dir = os.path.join( script_dir, '..')
sys.path.append( mymodule_dir )


from core.topologies import *
from mininet.net import Mininet
from core.analysis import *

import json
from core.utils import *
from core.emulation import *
from core.config import *


def run_emulation(topology, protocol, params, bw, delay, qmult, tcp_buffer_mult=3, run=0, aqm='fifo', loss=None, n_flows=2):
    if topology == 'Dumbell':
        topo = DumbellTopo(**params)
    else:
        print("ERROR: topology \'%s\' not recognised" % topology)

    bdp_in_bytes = int(bw * (2 ** 20) * 2 * delay * (10 ** -3) / 8)
    qsize_in_bytes = max(int(qmult * bdp_in_bytes), 1500)

    duration = int((2*delay*1000)/1000)

    
    net = Mininet(topo=topo)
    path = "%s/mininettestbed/nooffload/results_fairness_intra_rtt_async/%s/%s_%smbit_%sms_%spkts_%sloss_%sflows_%stcpbuf_%s/run%s" % (HOME_DIR,aqm, topology, bw, delay, int(qsize_in_bytes/1500), loss, n_flows, tcp_buffer_mult, protocol, run)
    mkdirp(path)
    subprocess.call(['chown', '-R' ,USERNAME, path])




    #  Configure size of TCP buffers
    #  TODO: check if this call can be put after starting mininet
    #  TCP buffers should account for QSIZE as well
    tcp_buffers_setup(bdp_in_bytes + qsize_in_bytes, multiplier=tcp_buffer_mult)
    

    net.start()

    disable_offload(net)

    network_config = [NetworkConf('s1', 's2', None, 2*delay, 3*bdp_in_bytes, False, 'fifo', loss),
                      NetworkConf('s2', 's3', bw, None, qsize_in_bytes, False, aqm, None)]
    
    if n_flows == 1:
        traffic_config = [TrafficConf('c1', 'x1', 0, 60, protocol)]
                        #   TrafficConf('c2', 'x2', 25, 75, protocol),
                        #   TrafficConf('c3', 'x3', 50, 50, protocol),
                        #   TrafficConf('c4', 'x4', 75, 25, protocol)]
    elif n_flows == 2:
        traffic_config = [TrafficConf('c1', 'x1', 0, 2*duration, protocol),
                           TrafficConf('c2', 'x2', int(duration/2), int(duration/2)+duration, protocol)]
    elif n_flows == 3:
        traffic_config = [TrafficConf('c1', 'x1', 0, 100, protocol),
                         TrafficConf('c2', 'x2', 25, 125, protocol),
                         TrafficConf('c3', 'x3', 50, 150, protocol)]
    elif n_flows == 4:
        traffic_config = [TrafficConf('c1', 'x1', 0, 100, protocol),
                         TrafficConf('c2', 'x2', 25, 125, protocol),
                         TrafficConf('c3', 'x3', 50, 150, protocol),
                         TrafficConf('c4', 'x4', 75, 175, protocol)]


    
    em = Emulation(net, network_config, traffic_config, path)

    em.configure_network()
    em.configure_traffic()
    monitors = ['s1-eth1', 's2-eth2', 'sysstat']
    if protocol != 'aurora':
        monitors.append('tcp_probe')
        
    em.set_monitors(monitors)
    em.run()
    em.dump_info()
    net.stop()
    
    change_all_user_permissions(path)

    # Process raw outputs into csv files
    process_raw_outputs(path)

if __name__ == '__main__':

    topology = 'Dumbell'
    
    delay = int(sys.argv[1])
    bw = int(sys.argv[2])
    qmult = float(sys.argv[3])
    protocol = sys.argv[4]
    run = int(sys.argv[5])
    aqm = sys.argv[6]
    loss = sys.argv[7]
    n_flows = int(sys.argv[8])
    params = {'n':n_flows}

    # Same sysctl as original Orca
    # os.system('sudo sysctl -w net.ipv4.tcp_wmem="4096 32768 4194304"')
    os.system('sudo sysctl -w net.ipv4.tcp_low_latency=1')
    os.system('sudo sysctl -w net.ipv4.tcp_autocorking=0')
    os.system('sudo sysctl -w net.ipv4.tcp_no_metrics_save=1')
    # os.system('sudo sysctl -w fs.inotify.max_user_watches=524288')
    # os.system('sudo sysctl -w fs.inotify.max_user_instances=524288')

    print('Loss is %s' % loss)
    run_emulation(topology, protocol, params, bw, delay, qmult, 22, run, aqm, loss, n_flows) #Qsize should be at least 1 MSS.

    # Plot results
    # plot_results(path)
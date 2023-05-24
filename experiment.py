from topologies import *
from mininet.net import Mininet
from analysis import *
from plot import *

import json
from utils import *
import os
from emulation import *
import sys

def run_emulation(topology, protocol, params, bw, delay, qmult, tcp_buffer_mult=3, run=0, aqm='fifo'):
    if topology == 'Dumbell':
        topo = DumbellTopo(**params)
    else:
        print("ERROR: topology \'%s\' not recognised" % topology)
    
    net = Mininet(topo=topo)
    path = "/home/luca/mininettestbed/results/%s/%s_%smbit_%sms_%spkts_%stcpbuf_%s/run%s" % (aqm, topology, bw, delay, int(qsize_in_bytes/1500), tcp_buffer_mult, protocol, run)
    mkdirp(path)

    bdp_in_bytes = int(bw*(2**20)*2*delay*(10**-3)/8)

    #  Configure size of TCP buffers
    #  TODO: check if this call can be put after starting mininet
    #  TCP buffers should account for QSIZE as well
    qsize_in_bytes = max(int(qmult * bdp_in_bytes), 1510)
    tcp_buffers_setup(bdp_in_bytes + qsize_in_bytes, multiplier=tcp_buffer_mult)



    net.start()

    network_config = [NetworkConf('s1', 's2', None, 2*delay, 3*bdp_in_bytes, False, 'fifo'),
                      NetworkConf('s2', 's3', bw, None, qsize_in_bytes, False, aqm)]
    
    traffic_config = [TrafficConf('c1', 'x1', 0, 60, protocol)]
                    #   TrafficConf('c2', 'x2', 25, 75, protocol),
                    #   TrafficConf('c3', 'x3', 50, 50, protocol),
                    #   TrafficConf('c4', 'x4', 75, 25, protocol)]
    
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
    params = {'n':1}
    delay = int(sys.argv[1])
    bw = int(sys.argv[2])
    qmult = float(sys.argv[3])
    protocol = sys.argv[4]
    run = int(sys.argv[5])
    if len(sys.argv) > 6:
        aqm = sys.argv[6]
    else:
        aqm = 'fifo'
    bdp_in_bytes = int(bw*(2**20)*2*delay*(10**-3)/8)

    # Same sysctl as original Orca
    # os.system('sudo sysctl -w net.ipv4.tcp_wmem="4096 32768 4194304"')
    os.system('sudo sysctl -w net.ipv4.tcp_low_latency=1')
    os.system('sudo sysctl -w net.ipv4.tcp_autocorking=0')
    os.system('sudo sysctl -w net.ipv4.tcp_no_metrics_save=1')
    # os.system('sudo sysctl -w fs.inotify.max_user_watches=524288')
    # os.system('sudo sysctl -w fs.inotify.max_user_instances=524288')

    run_emulation(topology, protocol, params, bw, delay, max(int(qmult*bdp_in_bytes), 1510), 22, run, aqm) #Qsize should be at least 1 MSS. 

    # Plot results
    # plot_results(path)
from topologies import *
from mininet.net import Mininet
from analysis import *
from plot import *

import json
from utils import *
import os
from emulation import *
import sys
import random
import numpy as np
def  generate_traffic_shape(seed, qsize_in_bytes):
    random.seed(seed)
    RUN_LENGTH = 300 #s
    CHANGE_PERIOD = 10 #s
    start_time = CHANGE_PERIOD
    traffic_config = []
    for i in range(int(RUN_LENGTH/CHANGE_PERIOD)):
        start_time = (CHANGE_PERIOD*i)
        random_bw = random.randint(1,100) # Mbps
        random_loss = round(random.uniform(0,5),2) # ms
        traffic_config.append(TrafficConf('s2', 's3', start_time, CHANGE_PERIOD, 'tbf', 
                                      (('s2', 's3'), random_bw, None, qsize_in_bytes, False, 'fifo', None, 'change')))
        traffic_config.append(TrafficConf('s1', 's2', start_time, CHANGE_PERIOD, 'netem', 
                                      (('s1', 's2'), None, 100, qsize_in_bytes, False, 'fifo', random_loss, 'change')))
            
    return traffic_config


def run_emulation(topology, protocol, params, bw, delay, qsize_in_bytes, tcp_buffer_mult=3, run=0, aqm='fifo', loss=None, n_flows=2):
    if topology == 'Dumbell':
        topo = DumbellTopo(**params)
    else:
        print("ERROR: topology \'%s\' not recognised" % topology)
    
    net = Mininet(topo=topo)
    path = "/media/luca/LaCie1/mininettestbed/nooffload/results_responsiveness/%s/%s_%smbit_%sms_%spkts_%sloss_%sflows_%stcpbuf_%s/run%s" % (aqm, topology, bw, delay, int(qsize_in_bytes/1500), loss, n_flows, tcp_buffer_mult, protocol, run)
    mkdirp(path)

    bdp_in_bytes = int(10*(2**20)*2*delay*(10**-3)/8)

    #  Configure size of TCP buffers
    #  TODO: check if this call can be put after starting mininet
    #  TCP buffers should account for QSIZE as well
    tcp_buffers_setup(bdp_in_bytes + qsize_in_bytes, multiplier=tcp_buffer_mult)
    

    net.start()


    disable_offload(net)

    network_config = [NetworkConf('s1', 's2', None, 2*delay, 3*bdp_in_bytes, False, 'fifo', loss),
                      NetworkConf('s2', 's3', bw, None, qsize_in_bytes, False, aqm, None)]
    
    if n_flows == 1:
        traffic_config = [TrafficConf('c1', 'x1', 0, 300, protocol)]
        traffic_config.extend(generate_traffic_shape(run, qsize_in_bytes))
    else:
        print("ERROR: number of flows greater than 1")
        exit()

    # TODO: create the scheduled changes in network configuration

    
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
    bdp_in_bytes = int(bw*(2**20)*2*delay*(10**-3)/8)
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
    run_emulation(topology, protocol, params, bw, delay, max(int(qmult*bdp_in_bytes), 1510), 22, run, aqm, loss, n_flows) #Qsize should be at least 1 MSS. 

    # Plot results
    # plot_results(path)
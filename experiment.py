from topologies import *
from mininet.net import Mininet
from analysis import *
from plot import *

import json
from utils import *
import os
from emulation import *
import sys

def run_emulation(topology, protocol, params, bw, delay, qsize_in_bytes, tcp_buffer_mult=3, run=0):
    if topology == 'Dumbell':
        topo = DumbellTopo(**params)
    else:
        print("ERROR: topology \'%s\' not recognised" % topology)
    
    net = Mininet(topo=topo)
    path = "%s/mininettestbed/results/%s_%smbit_%sms_%spkts_%stcpbuf_%s/run%s" % (os.getenv("HOME"), topology, bw, delay, int(qsize_in_bytes/1500), tcp_buffer_mult, protocol, run)
    mkdirp(path)

    bdp_in_bytes = int(10*(2**20)*2*delay*(10**-3)/8)

    #  Configure size of TCP buffers
    #  TODO: check if this call can be put after starting mininet
    #  TCP buffers should account for QSIZE as well
    tcp_buffers_setup(bdp_in_bytes + qsize_in_bytes, multiplier=tcp_buffer_mult)
    

    net.start()

    network_config = [NetworkConf('s1', 's2', bw, 2*delay, qsize_in_bytes, False)]
    
    traffic_config = [TrafficConf('c1', 'x1', 0, 60, protocol),
                      TrafficConf('c2', 'x2', 30, 30, protocol)]
    
    em = Emulation(net, network_config, traffic_config, path)

    em.configure_network()
    em.configure_traffic()
    em.set_monitors(['tcp_probe', 's1-eth1'])
    em.run()
    em.dump_info()
    net.stop()
    
    change_all_user_permissions(path)

    # Process raw outputs into csv files
    process_raw_outputs(path)

if __name__ == '__main__':

    topology = 'Dumbell'
    params = {'n':2}
    delay = int(sys.argv[1])
    bw = int(sys.argv[2])
    qmult = int(sys.argv[3])
    protocol = sys.argv[4]
    run = int(sys.argv[5])
    bdp_in_bytes = int(bw*(2**20)*2*delay*(10**-3)/8)

    # Same sysctl as original Orca
    # os.system('sudo sysctl -w net.ipv4.tcp_wmem="4096 32768 4194304"')
    # os.system('sudo sysctl -w net.ipv4.tcp_low_latency=1')
    # os.system('sudo sysctl -w net.ipv4.tcp_autocorking=0')
    # os.system('sudo sysctl -w net.ipv4.tcp_no_metrics_save=1')
    # os.system('sudo sysctl -w fs.inotify.max_user_watches=524288')
    # os.system('sudo sysctl -w fs.inotify.max_user_instances=524288')

    run_emulation(topology, protocol, params, bw, delay, qmult*bdp_in_bytes, 0, run)

    # Plot results
    # plot_results(path)
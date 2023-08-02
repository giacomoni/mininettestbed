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
        
    bdp_in_bytes = int(bw*(2**20)*2*delay*(10**-3)/8)
    qsize_in_bytes = max(int(qmult * bdp_in_bytes), 1510)
    
    net = Mininet(topo=topo)
    path = "%s/mininettestbed/nooffload/results_fairness_aqm/%s/%s_%smbit_%sms_%spkts_%sloss_%sflows_%stcpbuf_%s/run%s" % (HOME_DIR,aqm, topology, bw, delay, int(qsize_in_bytes/1500), loss, n_flows, tcp_buffer_mult, protocol, run)
    mkdirp(path)




    #  Configure size of TCP buffers
    #  TCP buffers should account for QSIZE as well
    tcp_buffers_setup(bdp_in_bytes + qsize_in_bytes, multiplier=tcp_buffer_mult)
    
    # Set up mininet 
    net.start()

    # Disable segmentation offloading
    disable_offload(net)

    # Network links configuration
    network_config = [NetworkConf('s1', 's2', None, 2*delay, 3*bdp_in_bytes, False, 'fifo', loss),
                      NetworkConf('s2', 's3', bw, None, qsize_in_bytes, False, aqm, None)]
    
    # Traffic configuration
    # Note that the order of elements in the config list MUST be increasing by starting time. Current code does not check for that.
    if n_flows == 1:
        traffic_config = [TrafficConf('c1', 'x1', 0, 60, protocol)]

    elif n_flows == 2:
        traffic_config = [TrafficConf('c1', 'x1', 0, 600, protocol),
                           TrafficConf('c2', 'x2', 100, 700, protocol)]
    elif n_flows == 3:
        traffic_config = [TrafficConf('c1', 'x1', 0, 600, protocol),
                         TrafficConf('c2', 'x2', 100, 700, protocol),
                         TrafficConf('c3', 'x3', 200, 800, protocol)]
    elif n_flows == 4:
        traffic_config = [TrafficConf('c1', 'x1', 0, 100, protocol),
                         TrafficConf('c2', 'x2', 25, 100, protocol),
                         TrafficConf('c3', 'x3', 50, 100, protocol),
                         TrafficConf('c4', 'x4', 75, 100, protocol)]


    # Create an emulation handler with links and traffic config
    em = Emulation(net, network_config, traffic_config, path)

    # Use tbf and netem to set up the network links as per config
    em.configure_network()

    # Schedule start and termination of traffic events 
    em.configure_traffic()

    # Set up system monitoring on the outgoing router's network interfaces  and set up sysstat monitoring for all nodes
    monitors = ['s1-eth1', 's2-eth2', 'sysstat']

    # If using TCP, then set up tcp_probe monitoring
    if protocol != 'aurora':
        monitors.append('tcp_probe')
 
    em.set_monitors(monitors)

    # Run the emulation
    em.run()

    # Store traffic config into json file
    em.dump_info()

    # Stop emulation
    net.stop()

    # Change user permissions for created directory and files since script was called as root
    # TODO: chech if call is effective
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

    # Same kernel setting as original Orca
    os.system('sudo sysctl -w net.ipv4.tcp_low_latency=1')
    os.system('sudo sysctl -w net.ipv4.tcp_autocorking=0')
    os.system('sudo sysctl -w net.ipv4.tcp_no_metrics_save=1')

    run_emulation(topology, protocol, params, bw, delay, qmult, 22, run, aqm, loss, n_flows) 

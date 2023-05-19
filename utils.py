import os
import subprocess
from collections import namedtuple

NetworkConf = namedtuple("NetworkConf", ['node1', 'node2', 'bw', 'delay', 'qsize', 'bidir', 'aqm', 'loss'])
TrafficConf = namedtuple("TrafficConf", ['source', 'dest', 'start', 'duration', 'proto'])
Command = namedtuple("Command", ['command', 'params', 'waiting_time'])
default_dir = '.'


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

def dump_system_config(path):
    with open('%s/sysctl.txt' % (path), 'w') as fout:
        fout.write(subprocess.check_output(['sysctl', 'net.core.netdev_max_backlog']) + '\n')
        fout.write(subprocess.check_output(['sysctl', 'net.ipv4.tcp_rmem']) + '\n')
        fout.write(subprocess.check_output(['sysctl', 'net.ipv4.tcp_wmem']) + '\n')
        fout.write(subprocess.check_output(['sysctl', 'net.ipv4.tcp_mem']) + '\n')
        fout.write(subprocess.check_output(['sysctl', 'net.ipv4.tcp_window_scaling']) + '\n')

def change_all_user_permissions(path):
    subprocess.call(['chmod', '-R', 'u+w', path])
    subprocess.call(['chmod', '-R', 'u+r', path])

def tcp_buffers_setup(target_bdp_bytes, multiplier=3):
    # --- Configure TCP Buffers on all senders and receivers
    # The send and receive buffer sizes should be set to at least
    # 2BDP (if BBR is used as the congestion control algorithm, this should be set to even a
    # larger value). We also want to account for the router/switch buffer size, makingsure
    # the tcp buffere is not the bottleneck.

    if multiplier:
        os.system('sysctl -w net.ipv4.tcp_rmem=\'10240 87380 %s\'' % (multiplier*(target_bdp_bytes)))
        os.system('sysctl -w net.ipv4.tcp_wmem=\'10240 87380 %s\'' % (multiplier*(target_bdp_bytes)))



from subprocess import Popen, PIPE
from parsers import *
from multiprocessing import Process
from time import sleep, time
import subprocess
import os
import re
from utils import *



def monitor_qlen(iface, interval_sec = 1, path = default_dir):
    mkdirp(path)
    fname='%s/%s.txt' % (path, iface)
    pat_queued = re.compile(r'backlog\s+([\d]+\w+)\s+\d+p')
    pat_dropped = re.compile(r'dropped\s+([\d]+)') 
    cmd = "tc -s qdisc show dev %s" % (iface)
    f = open(fname, 'w')
    f.write('time,root_pkts,root_drp,child_pkts,child_drp\n')
    f.close()
    while 1:
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.stdout.read()
        tmp = ''
        matches_queued = pat_queued.findall(output)
        matches_dropped = pat_dropped.findall(output)
        if len(matches_queued) != len(matches_dropped):
            print("WARNING: Two mathces have different lengths!")
            print(output)
        if matches_queued and matches_dropped:
            tmp += '%f,%s,%s' % (time(), matches_queued[0],matches_dropped[0])
            if len(matches_queued) > 1 and len(matches_dropped)> 1: 
                tmp += ',%s,%s\n' % (matches_queued[1], matches_dropped[1])
            else:
                tmp += ',,,\n'
        f = open(fname, 'a')
        f.write(tmp)
        f.close
        sleep(interval_sec)
    return

def monitor_ifconfig(iface, interval_sec = 1, path = default_dir):
    mkdirp(path)
    fname='%s/%s.txt' % (path, iface)
    pat_queued = re.compile(r'backlog\s+\d+\w+\s+([\d]+)p')
    pat_dropped = re.compile(r'dropped\s+([\d]+)') 
    cmd = "ifconfig %s" % (iface)
    # f = open(fname, 'w')
    # f.write('time,root_pkts,root_drp,child_pkts,child_drp\n')
    # f.close()
    while 1:
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.stdout.read()
        # tmp = ''
        # matches_queued = pat_queued.findall(output)
        # matches_dropped = pat_dropped.findall(output)
        # if len(matches_queued) != len(matches_dropped):
        #     print("WARNING: Two mathces have different lengths!")
        #     print(output)
        # if matches_queued and matches_dropped:
        #     tmp += '%f,%s,%s' % (time(), matches_queued[0],matches_dropped[0])
        #     if len(matches_queued) > 1 and len(matches_dropped)> 1: 
        #         tmp += ',%s,%s\n' % (matches_queued[1], matches_dropped[1])
        #     else:
        #         tmp += ',,,\n'
        # f = open(fname, 'a')
        # f.write(tmp)
        # f.close
        sleep(interval_sec)
    return


def monitor_devs_ng(fname="%s/txrate.txt" % default_dir, interval_sec=1):
    """Uses bwm-ng tool to collect iface tx rate stats.  Very reliable."""
    cmd = ("sleep 1; bwm-ng -t %s -o csv "
           "-u bits -T rate -C ',' > %s" %
           (interval_sec, fname))
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


def start_sysstat(interval, count, folder, node=None):
    mkdirp("%s/sysstat" % (folder))
    if node == None:
        cmd = "sudo /usr/lib/sysstat/sadc -S SNMP %s %s %s/sysstat/datafile_root.log &" % (interval, count, folder)
        os.system(cmd)
    else:
        cmd = "sudo /usr/lib/sysstat/sadc -S SNMP %s %s %s/sysstat/datafile_%s.log &" % (interval, count, folder, node.name )
        print("Sending command %s to node %s" % (cmd, node.name))
        node.popen(cmd,shell=True)


def stop_sysstat(folder, sending_nodes):
    Popen("killall -9 sadc", shell=True).wait()
    # Run sadf to generate CSV like (semi-colon separated) file
    cmd = "sadf -d -U -- -n DEV %s/sysstat/datafile_root.log > %s/sysstat/dev_root.log" % (folder,folder)
    Popen(cmd, shell=True).wait()
    cmd = "sadf -d -U -- -n EDEV %s/sysstat/datafile_root.log > %s/sysstat/edev_root.log" % (folder,folder)
    Popen(cmd, shell=True).wait()
    for node_name in sending_nodes:
        # Run sadf to generate CSV like (semi-colon separated) file
        cmd = "sadf -d -U -- -n DEV %s/sysstat/datafile_%s.log > %s/sysstat/dev_%s.log" % (folder,node_name,folder, node_name)
        Popen(cmd, shell=True).wait()
        cmd = "sadf -d -U -- -n EDEV %s/sysstat/datafile_%s.log > %s/sysstat/edev_%s.log" % (folder,node_name,folder, node_name)
        Popen(cmd, shell=True).wait()
        cmd = "sadf -d -U -- -n ETCP %s/sysstat/datafile_%s.log > %s/sysstat/etcp_%s.log" % (folder,node_name,folder, node_name)
        Popen(cmd, shell=True).wait()
        cmd = "sadf -d -U -- -n UDP %s/sysstat/datafile_%s.log > %s/sysstat/udp_%s.log" % (folder,node_name,folder, node_name)
        Popen(cmd, shell=True).wait()

    return
    

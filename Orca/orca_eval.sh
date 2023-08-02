#!/bin/sh

#Setup

sudo sysctl -q net.ipv4.tcp_wmem="4096 32768 4194304" #Doubling the default value from 16384 to 32768
sudo sysctl -w -q net.ipv4.tcp_low_latency=1
sudo sysctl -w -q net.ipv4.tcp_autocorking=0
sudo sysctl -w -q net.ipv4.tcp_no_metrics_save=1
sudo sysctl -w -q net.ipv4.ip_forward=1
#Mahimahi Issue: it couldn't make enough interfaces
#Solution: increase max of inotify
sudo sysctl -w -q fs.inotify.max_user_watches=524288
sudo sysctl -w -q fs.inotify.max_user_instances=524288

#Start Sender
port=4444
path=/home/luca/Orca/rl-module
period=20
scheme="cubic"
id=0
finish_time=60
max_it=0


#Bring up the actor i:
$path/orca-server-mahimahi $port $path ${period} $scheme $id $finish_time $max_it &

sleep 3


#Start Receiver
mm-delay 10 mm-link $path/../traces/wired12 $path/../traces/wired12 --downlink-log=test_down.txt --uplink-queue=droptail --uplink-queue-args=\"packets=200\" --downlink-queue=droptail --downlink-queue-args=\"packets=200\" -- sh -c 'iperf3 -c $MAHIMAHI_BASE -R -p 4444 -i 0.1 --logfile test.txt -t 60' &


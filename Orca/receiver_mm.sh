#!/bin/bash
if [ $# != 6 ]
then
    echo -e "usage:$0 port delay trace logfile qsize flowid"
    exit
fi



port=$1
delay=$2
trace=$3
log=$4
qsize=$5
flownum=${FLOW_NUM}
flowid=$((flownum + 1))
export FLOW_NUM=flowid

mm-delay ${delay} mm-link ${trace}  ${trace} --downlink-log=${log} --uplink-queue=droptail --uplink-queue-args=\"packets=${qsize}\" --downlink-queue=droptail --downlink-queue-args=\"packets=${qsize}\" -- sh -c "/home/luca/Orca/rl-module/client \$MAHIMAHI_BASE ${flowid} ${port} & sleep 10 && iperf3 -c \$MAHIMAHI_BASE -p 5201 -i 1 -R"

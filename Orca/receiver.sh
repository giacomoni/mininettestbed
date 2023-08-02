#!/bin/bash
ip=$1
port=$2
flow_id=$3

/home/luca/pantheon/third_party/orca/rl-module/clientThr ${ip} ${flow_id} ${port} 0.5

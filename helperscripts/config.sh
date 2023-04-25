# !/bin/bash

sudo tc qdisc add dev s1-eth1 root handle 1:0 netem delay 20ms limit 349
# sudo tc qdisc add dev s2-eth2 root handle 1:0 tbf rate 50mbit burst 262144 limit 130500
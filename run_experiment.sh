#!/bin/bash

# Run two competing flows in a Dumbel topology with 100Mbps and varying RTT. Repeat the experiment for three different buffer sizes. 
# The two flows should co-exist long enough to allow cubic to converge. We let the coexist for 1000x RTTs. The first flow lives for 500 RTTs, second flow enters
#  and coexist with first flow for 1000 RTTs

PROTOCOLS="cubic orca aurora"
BANDWIDTHS="100"
DELAYS="10 20 30 40 50 60 70 80 90 100"
RUNS="1 2 3 4 5"
QMULTS="0.2 1 4"
FLOWS="2"

for bw in $BANDWIDTHS
do
for del in $DELAYS
do
for qmult in $QMULTS
do
for flow in $FLOWS
do
    for protocol in $PROTOCOLS
    do
        for run in $RUNS
        do
            sudo python fairness_intra_rtt_async.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done

#  We repeat the experiment but with a bottleneck bandwidth of 10Mbps
PROTOCOLS="cubic orca aurora"
BANDWIDTHS="10"
DELAYS="10 20 30 40 50 60 70 80 90 100"
RUNS="1 2 3 4 5"
QMULTS="0.2 1 4"
FLOWS="2"

for bw in $BANDWIDTHS
do
for del in $DELAYS
do
for qmult in $QMULTS
do
for flow in $FLOWS
do
    for protocol in $PROTOCOLS
    do
        for run in $RUNS
        do
            sudo python fairness_intra_rtt_async.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done


    
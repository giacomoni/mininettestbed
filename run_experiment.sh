#!/bin/bash


# PROTOCOLS="orca aurora cubic"
# BANDWIDTHS="100"
# DELAYS="41"
# RUNS="1 2 3 4 5"  
# LOSS="0.02 0.04 0.06 0.08 0.1 0.2 0.4 0.6 0.8 1 2 4"


# for bw in $BANDWIDTHS
# do
# for del in $DELAYS
# do
# for loss in $LOSS
# do
#     for protocol in $PROTOCOLS
#     do
#         for run in $RUNS
#         do
#             sudo python efficiency_one_flow_loss.py $del $bw 1 $protocol $run fifo $loss
#         done
#     done
#     done
#     done
# done


# PROTOCOLS="orca aurora cubic"
# BANDWIDTHS="100"
# DELAYS="10 20 30 40 50 60 70 80 90 100"
# RUNS="1 2 3 4 5"  


# for bw in $BANDWIDTHS
# do
# for del in $DELAYS
# do

#     for protocol in $PROTOCOLS
#     do
#         for run in $RUNS
#         do
#             sudo python efficiency_intra_rtt.py $del $bw 1 $protocol $run fifo
#         done
#     done
#     done
# done



# PROTOCOLS="orca aurora cubic"
# BANDWIDTHS="100"
# DELAYS="41"
# RUNS="1 2 3 4 5"  
# QMULTS="0.02 0.04 0.06 0.08 0.1 0.2 0.4 0.6 0.8 1 2 4 6 8 10"


# for bw in $BANDWIDTHS
# do
# for del in $DELAYS
# do
# for qmult in $QMULTS
# do
#     for protocol in $PROTOCOLS
#     do
#         for run in $RUNS
#         do
#             sudo python efficiency_two_flows_on_cubic.py $del $bw $qmult $protocol $run fifo
#         done
#     done
#     done
#     done
# done

# PROTOCOLS="orca aurora cubic"
# BANDWIDTHS="100"
# DELAYS="10 20 30 40 50 60 70 80 90 100"
# RUNS="1 2 3 4 5"  


# for bw in $BANDWIDTHS
# do
# for del in $DELAYS
# do

#     for protocol in $PROTOCOLS
#     do
#         for run in $RUNS
#         do
#             sudo python efficiency_intra_rtt_2.py $del $bw 0.1 $protocol $run fifo
#         done
#     done
#     done
# done

#PROTOCOLS="orca aurora cubic"
#BANDWIDTHS="100"
#DELAYS="40 50 60 70 80 90 100"
#RUNS="1 2 3 4 5"  

#for bw in $BANDWIDTHS
#do
#for del in $DELAYS
#do

#    for protocol in $PROTOCOLS
#    do
#        for run in $RUNS
#        do
#            sudo python efficiency_intra_rtt_3.py $del $bw 10 $protocol $run fifo
#        done
#    done
#    done
#done

#PROTOCOLS="orca aurora cubic"
#BANDWIDTHS="100"
#DELAYS="10 100"
#RUNS="1 2 3 4 5"  
#QMULTS="0.1 1 10"
#FLOWS='4 3 2'


#for bw in $BANDWIDTHS
#do
#for del in $DELAYS
#do
#for qmult in $QMULTS
#do
#for flow in $FLOWS
#do
#    for protocol in $PROTOCOLS
#    do
#        for run in $RUNS
#        do
#            sudo python fairness_async.py $del $bw $qmult $protocol $run fifo 0 $flow
#        done
#    done
#    done
#    done
#    done
#done

#PROTOCOLS="orca aurora cubic"
#BANDWIDTHS="100"
#DELAYS="10 20 30 40 50 60 70 80 90 100"
#RUNS="1 2 3 4 5"


#for bw in $BANDWIDTHS
#do
#for del in $DELAYS
#do
#for protocol in $PROTOCOLS
#do
#  for run in $RUNS
#  do
#    sudo python efficiency_one_flow_2.py $del $bw 1 $protocol $run fifo
#  done
# done
# done
#done

 #PROTOCOLS="orca aurora cubic"
 #BANDWIDTHS="100"
 #DELAYS="10"
 #RUNS="1 2 3 4 5"
 #LOSS="0.02 0.04 0.06 0.08 0.1 0.2 0.4 0.6 0.8 1 2 4"


 #for bw in $BANDWIDTHS
 #do
 #for del in $DELAYS
 #do
 #for loss in $LOSS
 #do
 #    for protocol in $PROTOCOLS
 #    do
 #        for run in $RUNS
 #        do
 #            sudo python efficiency_one_flow_loss_2.py $del $bw 1 $protocol $run fifo $loss 1
 #        done
  #   done
  #   done
  #   done
# done


#PROTOCOLS="orca aurora cubic"
#BANDWIDTHS="100"
#DELAYS="10 20 30 40 50 60 70 80 90 100"
#RUNS="1 2 3 4 5"
#QMULTS="1"
#FLOWS="2"
#
#for bw in $BANDWIDTHS
#do
#for del in $DELAYS
#do
#for qmult in $QMULTS
#do
#for flow in $FLOWS
#do
#    for protocol in $PROTOCOLS
#    do
#        for run in $RUNS
#        do
#            sudo python fairness_async_2.py $del $bw $qmult $protocol $run fifo 0 $flow
#        done
#    done
#    done
#    done
#    done
#    done
#
#PROTOCOLS="orca aurora cubic"
#BANDWIDTHS="100"
#DELAYS="10 100"
#RUNS="1 2 3 4 5"
#QMULTS="0.1 1 10"
#FLOWS="2"
#
#for bw in $BANDWIDTHS
#do
#for del in $DELAYS
#do
#for qmult in $QMULTS
#do
#for flow in $FLOWS
#do
#    for protocol in $PROTOCOLS
#    do
#        for run in $RUNS
#        do
#            sudo python fairness_async_3.py $del $bw $qmult $protocol $run fifo 0 $flow
#        done
#    done
#    done
#    done
#    done
#    done
#
#PROTOCOLS="orca aurora cubic"
#BANDWIDTHS="100"
#DELAYS="10 100"
#RUNS="1 2 3 4 5"
#QMULTS="0.1 1 10"
#FLOWS="2"
#
#for bw in $BANDWIDTHS
#do
#for del in $DELAYS
#do
#for qmult in $QMULTS
#do
#for flow in $FLOWS
#do
#    for protocol in $PROTOCOLS
#    do
#        for run in $RUNS
#        do
#            sudo python fairness_async_4.py $del $bw $qmult $protocol $run fifo 0 $flow
#        done
#    done
#    done
#    done
#    done
#    done
#
#PROTOCOLS="orca aurora cubic"
#BANDWIDTHS="100"
#DELAYS="10 20 30 40 50 60 70 80 90 100"
#RUNS="1 2 3 4 5"
#QMULTS="1"
#FLOWS="2"
#
#for bw in $BANDWIDTHS
#do
#for del in $DELAYS
#do
#for qmult in $QMULTS
#do
#for flow in $FLOWS
#do
#    for protocol in $PROTOCOLS
#    do
#        for run in $RUNS
#        do
#            sudo python fairness_async_5.py $del $bw $qmult $protocol $run fifo 0 $flow
#        done
#    done
#    done
#    done
#    done
#    done
#
#
#PROTOCOLS="orca aurora cubic"
#BANDWIDTHS="100"
#DELAYS="20 30 40 50 60 70 80 90 100"
#RUNS="1 2 3 4 5"
#QMULTS="1"
#FLOWS="2"
#
#for bw in $BANDWIDTHS
#do
#for del in $DELAYS
#do
#for qmult in $QMULTS
#do
#for flow in $FLOWS
#do
#    for protocol in $PROTOCOLS
#    do
#        for run in $RUNS
#        do
#            sudo python fairness_inter_rtt_async.py $del $bw $qmult $protocol $run fifo 0 $flow
#        done
#    done
#    done
#    done
#    done
#    done
#
#PROTOCOLS="orca aurora cubic"
#BANDWIDTHS="100"
#DELAYS="20 30 40 50 60 70 80 90 100"
#RUNS="1 2 3 4 5"
#QMULTS="1"
#FLOWS="2"
#
#for bw in $BANDWIDTHS
#do
#for del in $DELAYS
#do
#for qmult in $QMULTS
#do
#for flow in $FLOWS
#do
#    for protocol in $PROTOCOLS
#    do
#        for run in $RUNS
#        do
#            sudo python fairness_inter_rtt_sync.py $del $bw $qmult $protocol $run fifo 0 $flow
#        done
#    done
#    done
#    done
#    done
#    done
#
#PROTOCOLS="orca aurora cubic"
#BANDWIDTHS="100"
#DELAYS="20 30 40 50 60 70 80 90 100"
#RUNS="1 2 3 4 5"
#QMULTS="1"
#FLOWS="2"
#
#for bw in $BANDWIDTHS
#do
#for del in $DELAYS
#do
#for qmult in $QMULTS
#do
#for flow in $FLOWS
#do
#    for protocol in $PROTOCOLS
#    do
#        for run in $RUNS
#        do
#            sudo python fairness_inter_rtt_async_2.py $del $bw $qmult $protocol $run fifo 0 $flow
#        done
#    done
#    done
#    done
#    done
#    done
#

#PROTOCOLS="orca aurora cubic"
#BANDWIDTHS="20 40 60 80 100 200 400 600 800 1000"
#DELAYS="30"
#RUNS="1 2 3 4 5"
#QMULTS="1"
#FLOWS="2"
#
#for bw in $BANDWIDTHS
#do
#for del in $DELAYS
#do
#for qmult in $QMULTS
#do
#for flow in $FLOWS
#do
#    for protocol in $PROTOCOLS
#    do
#        for run in $RUNS
#        do
#            sudo python fairness_bw_sync.py $del $bw $qmult $protocol $run fifo 0 $flow
#        done
#    done
#    done
#    done
#    done
#    done

#PROTOCOLS="orca aurora cubic"
#BANDWIDTHS="2 6 10 20 60 100 200 600 1000"
#DELAYS="25"
#RUNS="1 2 3 4 5"
#QMULTS="1"
#FLOWS="2"
#
#for bw in $BANDWIDTHS
#do
#for del in $DELAYS
#do
#for qmult in $QMULTS
#do
#for flow in $FLOWS
#do
#    for protocol in $PROTOCOLS
#    do
#        for run in $RUNS
#        do
#            sudo python fairness_bw_async.py $del $bw $qmult $protocol $run fifo 0 $flow
#        done
#    done
#    done
#    done
#    done
#    done

PROTOCOLS="orca aurora cubic"
BANDWIDTHS="100"
DELAYS="5 15 25 35 45 55 65 75 80"
RUNS="1 2 3 4 5"
QMULTS="0.2"
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
            sudo python fairness_inter_rtt_async_0.2BDP.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done

PROTOCOLS="orca aurora cubic"
BANDWIDTHS="100"
DELAYS="5 15 25 35 45 55 65 75 80"
RUNS="1 2 3 4 5"
QMULTS="0.2"
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
            sudo python fairness_inter_rtt_async_2_0.2BDP.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done

PROTOCOLS="orca aurora cubic"
BANDWIDTHS="100"
DELAYS="5 15 25 35 45 55 65 75 80"
RUNS="1 2 3 4 5"
QMULTS="0.2"
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
            sudo python fairness_inter_rtt_sync_0.2BDP.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done

PROTOCOLS="orca aurora cubic"
BANDWIDTHS="100"
DELAYS="5 15 25 35 45 55 65 75 80"
RUNS="1 2 3 4 5"
QMULTS="0.2"
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
            sudo python fairness_inter_rtt_async_2MB.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done

PROTOCOLS="orca aurora cubic"
BANDWIDTHS="100"
DELAYS="5 15 25 35 45 55 65 75 80"
RUNS="1 2 3 4 5"
QMULTS="0.2"
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
            sudo python fairness_inter_rtt_async_2_2MB.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done

PROTOCOLS="orca aurora cubic"
BANDWIDTHS="100"
DELAYS="5 15 25 35 45 55 65 75 80"
RUNS="1 2 3 4 5"
QMULTS="0.2"
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
            sudo python fairness_inter_rtt_sync_2MB.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done




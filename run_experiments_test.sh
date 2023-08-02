#!/bin/bash
#  PROTOCOLS="cubic"
#  BANDWIDTHS="100"
#  DELAYS="10"
#  RUNS="1"
#  QMULTS="1"
#  FLOWS="2"

#  for bw in $BANDWIDTHS
#  do
#  for del in $DELAYS
#  do
#  for qmult in $QMULTS
#  do
#  for flow in $FLOWS
#  do
#      for protocol in $PROTOCOLS
#      do
#          for run in $RUNS
#          do
#              sudo python experiments/fairness_intra_rtt_async.py $del $bw $qmult $protocol $run fifo 0 $flow
#          done
#      done
#      done
#      done
#      done
#      done

#  PROTOCOLS="cubic"
#  BANDWIDTHS="100"
#  DELAYS="10"
#  RUNS="1"
#  QMULTS="1"
#  FLOWS="2"


#  for bw in $BANDWIDTHS
#  do
#  for del in $DELAYS
#  do
#  for qmult in $QMULTS
#  do
#  for flow in $FLOWS
#  do
#     for protocol in $PROTOCOLS
#     do
#         for run in $RUNS
#         do
#             sudo python experiments/fairness_bw_async.py $del $bw $qmult $protocol $run fifo 0 $flow
#         done
#     done
#     done
#     done
#     done
#     done


 PROTOCOLS="cubic"
 BANDWIDTHS="100"
 DELAYS="10"
 RUNS="1"
 QMULTS="1"
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
            sudo python experiments/fairness_friendly_rtt_async.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done

 PROTOCOLS="cubic"
 BANDWIDTHS="100"
 DELAYS="10"
 RUNS="1"
 QMULTS="1"
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
            sudo python experiments/fairness_friendly_rtt_async_inverse.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done


 PROTOCOLS="cubic"
 BANDWIDTHS="100"
 DELAYS="10"
 RUNS="1"
 QMULTS="1"
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
           sudo python experiments/fairness_friendly_bw_async.py $del $bw $qmult $protocol $run fifo 0 $flow
       done
   done
   done
   done
   done
   done

 PROTOCOLS="cubic"
 BANDWIDTHS="100"
 DELAYS="10"
 RUNS="1"
 QMULTS="1"
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
            sudo python experiments/fairness_inter_rtt_async.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done
  


 PROTOCOLS="cubic"
 BANDWIDTHS="100"
 DELAYS="10"
 RUNS="1"
 QMULTS="1"
 FLOWS="4"
 AQMS='fifo'


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
   for aqm in $AQMS
   do
       for run in $RUNS
       do
           sudo python experiments/fairness_aqm.py $del $bw $qmult $protocol $run $aqm 0 $flow
       done
   done
   done
   done
   done
   done
done



 PROTOCOLS="cubic"
 BANDWIDTHS="50"
 DELAYS="50"
 RUNS="1"
 QMULTS="1"
 FLOWS="1"
 AQMS='fifo'



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
   for aqm in $AQMS
   do
       for run in $RUNS
       do
           sudo python experiments/responsiveness_bw_rtt.py $del $bw $qmult $protocol $run $aqm 0 $flow
       done
   done
   done
   done
   done
   done
done


 PROTOCOLS="cubic"
 BANDWIDTHS="50"
 DELAYS="50"
 RUNS="1"
 QMULTS="1"
 FLOWS="1"
 AQMS='fifo'



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
   for aqm in $AQMS
   do
       for run in $RUNS
       do
           sudo python experiments/responsiveness_loss.py $del $bw $qmult $protocol $run $aqm 0 $flow
       done
   done
   done
   done
   done
   done
done
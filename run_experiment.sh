#!/bin/bash
# PROTOCOLS="aurora"
#  BANDWIDTHS="100"
#  DELAYS="40"
#  RUNS="1 2 3 4 5"
#  QMULTS="4"
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
#              sudo python fairness_intra_rtt_async.py $del $bw $qmult $protocol $run fifo 0 $flow
#          done
#      done
#      done
#      done
#      done
#      done

#  PROTOCOLS="aurora"
#  BANDWIDTHS="100"
#  DELAYS="50 60 70 80 90 100"
#  RUNS="1 2 3 4 5"
#  QMULTS="0.2 1 4"
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
#              sudo python fairness_intra_rtt_async.py $del $bw $qmult $protocol $run fifo 0 $flow
#          done
#      done
#      done
#      done
#      done
#      done


# # # # Run two competing flows in a Dumbel topology with 100Mbps and varying RTT. Repeat the experiment for three different buffer sizes. 
# # # # The two flows should co-exist long enough to allow cubic to converge. We let the coexist for 1000x RTTs. The first flow lives for 500 RTTs, second flow enters
# # # #  and coexist with first flow for 1000 RTTs





#  PROTOCOLS="aurora"
#  BANDWIDTHS="10 20 30 40 50 60 70 80 90 100"
#  DELAYS="20"
#  RUNS="1 2 3 4 5"
#  QMULTS="0.2 1 4"
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
#             sudo python fairness_bw_async.py $del $bw $qmult $protocol $run fifo 0 $flow
#         done
#     done
#     done
#     done
#     done
#     done

# # # --------------------- NEW EXPS START FROM HERE --------------------

# # # PROTOCOLS="cubic orca aurora"
# # # BANDWIDTHS="100 50 10"
# # # DELAYS="10 50 100"
# # # RUNS="1 2 3 4 5"
# # # QMULTS="0.2 1 4"
# # # FLOWS="5"

# # # for bw in $BANDWIDTHS
# # # do
# # # for del in $DELAYS
# # # do
# # # for qmult in $QMULTS
# # # do
# # # for flow in $FLOWS
# # # do
# # #     for protocol in $PROTOCOLS
# # #     do
# # #         for run in $RUNS
# # #         do
# # #             sudo python efficiency_parkinglot.py $del $bw $qmult $protocol $run fifo 0 $flow
# # #         done
# # #     done
# # #     done
# # #     done
# # #     done
# # #     done



# PROTOCOLS="aurora"
# BANDWIDTHS="100"
# DELAYS="10 20 30 40 50 60 70 80 90 100"
# RUNS="1 2 3 4 5"
# QMULTS="0.2 1 4"
# FLOWS="2"

# for bw in $BANDWIDTHS
# do
# for del in $DELAYS
# do
# for qmult in $QMULTS
# do
# for flow in $FLOWS
# do
#     for protocol in $PROTOCOLS
#     do
#         for run in $RUNS
#         do
#             sudo python fairness_friendly_rtt_async.py $del $bw $qmult $protocol $run fifo 0 $flow
#         done
#     done
#     done
#     done
#     done
#     done



# PROTOCOLS="aurora"
# BANDWIDTHS="10 20 30 40 50 60 70 80 90 100"
# DELAYS="20"
# RUNS="1 2 3 4 5"
# QMULTS="0.2 1 4"
# FLOWS="2"

# for bw in $BANDWIDTHS
# do
# for del in $DELAYS
# do
# for qmult in $QMULTS
# do
# for flow in $FLOWS
# do
#    for protocol in $PROTOCOLS
#    do
#        for run in $RUNS
#        do
#            sudo python fairness_friendly_bw_async.py $del $bw $qmult $protocol $run fifo 0 $flow
#        done
#    done
#    done
#    done
#    done
#    done

# PROTOCOLS="aurora"
# BANDWIDTHS="100"
# DELAYS="10 20 30 40 50 60 70 80 90 100"
# RUNS="1 2 3 4 5"
# QMULTS="4"
# FLOWS="2"

# for bw in $BANDWIDTHS
# do
# for del in $DELAYS
# do
# for qmult in $QMULTS
# do
# for flow in $FLOWS
# do
#     for protocol in $PROTOCOLS
#     do
#         for run in $RUNS
#         do
#             sudo python fairness_inter_rtt_async.py $del $bw $qmult $protocol $run fifo 0 $flow
#         done
#     done
#     done
#     done
#     done
#     done
  



# PROTOCOLS="aurora"
# BANDWIDTHS="100"
# DELAYS="10 100"
# RUNS="1 2 3 4 5"  
# QMULTS="0.2 1 4"
# AQMS='fifo'
# FLOWS='4'


# for bw in $BANDWIDTHS
# do
# for del in $DELAYS
# do
# for qmult in $QMULTS
# do
# for flow in $FLOWS
# do
#    for protocol in $PROTOCOLS
#    do
#    for aqm in $AQMS
#    do
#        for run in $RUNS
#        do
#            sudo python fairness_aqm.py $del $bw $qmult $protocol $run $aqm 0 $flow
#        done
#    done
#    done
#    done
#    done
#    done
# done


# PROTOCOLS="aurora"
# BANDWIDTHS="2 6"
# DELAYS="50"
# RUNS="1 2 3 4 5"  
# QMULTS="1"
# AQMS='fifo'
# FLOWS='4'


# for bw in $BANDWIDTHS
# do
# for del in $DELAYS
# do
# for qmult in $QMULTS
# do
# for flow in $FLOWS
# do
#    for protocol in $PROTOCOLS
#    do
#    for aqm in $AQMS
#    do
#        for run in $RUNS
#        do
#            sudo python aurora_best.py $del $bw $qmult $protocol $run $aqm 0 $flow
#        done
#    done
#    done
#    done
#    done
#    done
# done

# PROTOCOLS="cubic orca aurora"
# BANDWIDTHS="50"
# DELAYS="50"
# RUNS="1"  
# QMULTS="1"
# AQMS='fifo'
# FLOWS='1'


# for bw in $BANDWIDTHS
# do
# for del in $DELAYS
# do
# for qmult in $QMULTS
# do
# for flow in $FLOWS
# do
#    for protocol in $PROTOCOLS
#    do
#    for aqm in $AQMS
#    do
#        for run in {1..50}
#        do
#            sudo python responsiveness_bw_rtt.py $del $bw $qmult $protocol $run $aqm 0 $flow
#        done
#    done
#    done
#    done
#    done
#    done
# done

PROTOCOLS="cubic orca aurora"
BANDWIDTHS="50"
DELAYS="10"
RUNS="16"  
QMULTS="1"
AQMS='fifo'
FLOWS='1'


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
           sudo python responsiveness_bw.py $del $bw $qmult $protocol $run $aqm 0 $flow
       done
   done
   done
   done
   done
   done
done
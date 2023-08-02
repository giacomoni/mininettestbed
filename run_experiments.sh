#!/bin/bash
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
             sudo python experiments/fairness_intra_rtt_async.py $del $bw $qmult $protocol $run fifo 0 $flow
         done
     done
     done
     done
     done
     done

 PROTOCOLS="cubic orca aurora"
 BANDWIDTHS="10 20 30 40 50 60 70 80 90 100"
 DELAYS="20"
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
            sudo python experiments/fairness_bw_async.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done


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
            sudo python experiments/fairness_friendly_rtt_async.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done

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
            sudo python experiments/fairness_friendly_rtt_async_inverse.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done


PROTOCOLS="cubic orca aurora"
BANDWIDTHS="10 20 30 40 50 60 70 80 90 100"
DELAYS="20"
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
           sudo python experiments/fairness_friendly_bw_async.py $del $bw $qmult $protocol $run fifo 0 $flow
       done
   done
   done
   done
   done
   done

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
            sudo python experiments/fairness_inter_rtt_async.py $del $bw $qmult $protocol $run fifo 0 $flow
        done
    done
    done
    done
    done
    done
  

PROTOCOLS="cubic orca aurora"
BANDWIDTHS="100"
DELAYS="10 100"
RUNS="1 2 3 4 5"  
QMULTS="0.2 1 4"
AQMS='fifo'
FLOWS='4'


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


PROTOCOLS="cubic orca aurora"
BANDWIDTHS="50"
DELAYS="50"
RUNS="1"  
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
       for run in {1..50}
       do
           sudo python experiments/responsiveness_bw_rtt.py $del $bw $qmult $protocol $run $aqm 0 $flow
       done
   done
   done
   done
   done
   done
done

PROTOCOLS="cubic orca aurora"
BANDWIDTHS="50"
DELAYS="50"
RUNS="1"  
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
       for run in {1..50}
       do
           sudo python experiments/responsiveness_loss.py $del $bw $qmult $protocol $run $aqm 0 $flow
       done
   done
   done
   done
   done
   done
done
#Evaluate Orca, Cubic and Reno
#Results are stored in text files with name: [protocol]/bw_rtt.txt


rtts=( 10 100 )
bws=( 12 300 )
qsize=20
orcapath=/home/luca/pantheon/third_party/orca
resultspath=/home/luca/eval


#Orca evaluation. 
#Single flow
for rtt in "${rtts[@]}"
do
  for bw in "${bws[@]}"
	do
  	  duration=$((3 * rtt * 2))
	  sudo killall -s15 python
	  sudo killall -s15 orca-server-mahimahi
	  sudo killall -s15 clientThr
	  $orcapath/rl-module/orca-server-mahimahi 12000 $orcapath/rl-module 20 cubic 0 $duration 0 &
	  sleep 3
	  mkdir -p $resultspath/orca
          mm-delay ${rtt} mm-link --downlink-log=${resultspath}/orca/down-${rtt}-${bw} --uplink-queue=droptail --uplink-queue-args="packets=${qsize}" --downlink-queue=droptail --downlink-queue-args="packets=${qsize}" ${orcapath}/traces/wired${bw} $orcapath/traces/wired${bw} -- sh -c "${orcapath}/rl-module/clientThr \$MAHIMAHI_BASE 1 12000 2 >  ${resultspath}/orca/${bw}_${rtt}.txt"
         
	done
done




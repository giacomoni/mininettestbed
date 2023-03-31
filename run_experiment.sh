#!/bin/bash



# sudo python experiment.py 10 10 1 cubic 1
# sudo python experiment.py 10 10 1 orca 1
# sudo python experiment.py 100 10 1 orca 1
# sudo python experiment.py 100 10 1 cubic 1   

# sudo python experiment.py 10 10 2 orca 1
# sudo python experiment.py 10 10 2 cubic 1
# sudo python experiment.py 100 10 2 orca 1
# sudo python experiment.py 100 10 2 cubic 1

# sudo python experiment.py 10 10 3 orca 1
# sudo python experiment.py 10 10 3 cubic 1
# sudo python experiment.py 100 10 3 orca 1
# sudo python experiment.py 100 10 3 cubic 1

# sudo python experiment.py 10 10 4 orca 1
# sudo python experiment.py 10 10 4 cubic 1
# sudo python experiment.py 100 10 4 orca 1
# sudo python experiment.py 100 10 4 cubic 1

# sudo python experiment.py 10 10 5 orca 1
# sudo python experiment.py 10 10 5 cubic 1
# sudo python experiment.py 100 10 5 orca 1
# sudo python experiment.py 100 10 5 cubic 1


# sudo python experiment.py 10 10 1 orca 2
# sudo python experiment.py 10 10 1 cubic 2
# sudo python experiment.py 100 10 1 orca 2
# sudo python experiment.py 100 10 1 cubic 2

# sudo python experiment.py 10 10 2 orca 2
# sudo python experiment.py 10 10 2 cubic 2
# sudo python experiment.py 100 10 2 orca 2
# sudo python experiment.py 100 10 2 cubic 2

# sudo python experiment.py 10 10 3 orca 2
# sudo python experiment.py 10 10 3 cubic 2
# sudo python experiment.py 100 10 3 orca 2
# sudo python experiment.py 100 10 3 cubic 2

# sudo python experiment.py 10 10 4 orca 2
# sudo python experiment.py 10 10 4 cubic 2
# sudo python experiment.py 100 10 4 orca 2
# sudo python experiment.py 100 10 4 cubic 2

# sudo python experiment.py 10 10 5 orca 2
# sudo python experiment.py 10 10 5 cubic 2
# sudo python experiment.py 100 10 5 orca 2
# sudo python experiment.py 100 10 5 cubic 2



RUNS="1"
BANDWIDTHS="10 100 1000" 
for n in `seq 2 2 50`;
do
    for bw in $BANDWIDTHS:
    do
        for run in $RUNS
        do
            sudo python experiment.py 10 $bw 2 cubic $run $n

        done
    done
done



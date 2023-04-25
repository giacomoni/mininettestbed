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


PROTOCOLS="aurora"
AQMS="fifo"
RUNS="1"

for aqm in $AQMS
do
    for protocol in $PROTOCOLS
    do
        for run in $RUNS
        do
            sudo python experiment.py 10 50 1 $protocol $run $aqm
            sudo python experiment.py 100 50 1 $protocol $run $aqm
            sudo python experiment.py 10 50 2 $protocol  $run $aqm
            sudo python experiment.py 100 50 2 $protocol $run $aqm
        done
    done
done



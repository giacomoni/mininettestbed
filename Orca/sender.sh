#!/bin/bash
port=$1
path=/home/luca/Orca/rl-module
period=20
scheme="cubic"
id=0
finish_time=600
max_it=0


#Bring up the actor i:
echo "will be done in $finish_time seconds ..."
echo "$path/orca-server-mahimahi $port $path ${period} $scheme $id $finish_time $max_it"

$path/orca-server-mahimahi $port $path ${period} $scheme $id $finish_time $max_it

echo "Finished."


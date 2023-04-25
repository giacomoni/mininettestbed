# !/bin/bash

sudo -u luca LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/luca/PCC-Uspace/src/core /home/luca/PCC-Uspace/src/app/pccclient send $1 9000 1 $2  --pcc-rate-control=python3 -pyhelper=loaded_client -pypath=/home/luca/PCC-RL/src/udt-plugins/testing/ --history-len=10 --pcc-utility-calc=linear --model-path=/home/luca/pcc_saved_models/model_B

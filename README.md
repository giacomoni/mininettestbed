# mininettestbed
Code for the evaluation of RL-based protocols using Mininet

## System requirements
### Operating System
Code has been run on Debian 9 (Stretch) with Linux Kernel 4.13. 

Using other Linux kernels may be problematic due to:
- Cubic implementation may differ from the one used by Orca
- tcp_probe (kernel module used in our testbed) has been discontinued in favor of tcp kernel event tracing

### Python
The Python version used to run the code is 2.6 and all modules versions can be found in requirements2.6.txt
The RL agents of Orca and Aurora run on Python 3.

### System config
TODO

## Installation

Download Orca and follow the repo's instruction to install it.
Download PCC-Uspace and PCC-RL and follow the repo's instruction to install Aurora.

Install python interpreter for Orca's agent using venv:
TODO: commands

## Configuration
Set your username in

core/config.py

Make sure installation location of Orca, PCC-RL and PCC-Uspace match the path set in core/config.py (home directory)

## Running the experiments
TODO: commands

The experiments folder contain one script per experiment

To run them all, just execute

sudo ./run_rexperiments.sh

## Plotting results
All plots on the paper can be reproduced by running the corresponding script in the plots folder. The scripts assume that results are stored in:

mininetestbed/nooffload

You can also reproduce the plots without having to rerun the experiment by downloading the dataset available at TODO:figshare. Make sure to move the data into the expected location or change the path(s) in the python scripts

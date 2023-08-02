# mininettestbed
Code for the evaluation of RL-based protocols using Mininet

## System requirements
### Operating System
Code has been run on Debian 9 (Stretch) with Linux Kernel 4.13. 

Using other Linux kernels may be problematic due to:
- Cubic implementation may slightly differ from the one used by Orca, especially the Slow Start phase.
- tcp_probe (kernel module used in our testbed) has been discontinued in favor of tcp kernel event tracing.


### Python
The Python version used to run the code is Python 2.7.13 and all modules versions can be found in *requirements27.txt*
The RL agents of Orca and Aurora run on Python 3 and all modules versions can be found in *requirements35.txt*

### System config
All kernel configuration parameters can be found in *sysctl.txt*, although they are the default ones. Note that when setting up the emulation, some of these values (e.g. TCP buffers and segmentation offload) are changed. Refer to the code for details.

## Installation

Download and install [Mininet](http://mininet.org/).
Download [Orca](https://github.com/temp2691317/Orca) and follow the repo's instruction to install it.
Download [PCC-Uspace](https://github.com/temp2691317/PCC-Uspace) and [PCC-RL](https://github.com/temp2691317/PCC-RL) and follow the repo's instruction to install Aurora.


Install python interpreter (3.5) for Orca's agent using venv:

```bash
cd
python3 -m venv venv
```


## Configuration
Set your username in *core/config.py*

```python
USERNAME=None
```

Make sure installation location of Orca, PCC-RL and PCC-Uspace match the path set in core/config.py (home directory)

## Running the experiments
The experiments folder contain one script per experiment. The destination folder of the results 

To run them all, just execute

```bash
sudo ./run_rexperiments.sh
```

## Data collected
A detailed explanation of the data collected during emulation can be found in the *figshare* database.

## Plotting results
All plots on the paper can be reproduced by running the corresponding script in the plots folder. The scripts assume that results are stored in *mininetestbed/nooffload*.

You can also reproduce the plots without having to rerun the experiment by downloading the dataset available at TODO:figshare. Make sure to move the data into the expected location or change the path(s) in the python scripts

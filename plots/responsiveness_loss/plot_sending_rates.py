import pandas as pd
import matplotlib.pyplot as plt
import scienceplots
plt.style.use('science')
import json
import os
import matplotlib as mpl
pd.set_option('display.max_rows', None)
import numpy as np
from matplotlib.pyplot import figure

ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_responsiveness/fifo"
PROTOCOLS = ['cubic', 'orca', 'aurora']
BW = 50
DELAY = 50
QMULT = 1
RUNS = list(range(1,51))
LOSSES=[0]
BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
BDP_IN_PKTS = BDP_IN_BYTES / 1500
start_time = 10
end_time = 290
LINEWIDTH = 0.5


for RUN in RUNS:
    fig, axes = plt.subplots(nrows=1, ncols=1,figsize=(3,1.5))
    ax = axes

    for protocol in PROTOCOLS:
        PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_1flows_22tcpbuf_%s/run%s' % (BW, DELAY, int(QMULT * BDP_IN_PKTS), protocol, RUN)
        # Compute the average optimal throughput
        with open(PATH + '/emulation_info.json', 'r') as fin:
            emulation_info = json.load(fin)

        bw_capacities = list(filter(lambda elem: elem[4] >= start_time and elem[4] <= end_time, emulation_info['flows']))
        bw_capacities = list(filter(lambda elem: elem[5] == 'tbf', bw_capacities))
        bw_capacities = [x[-1][1] for x in bw_capacities]


        if os.path.exists(PATH + '/csvs/c1.csv'):
            sender = pd.read_csv(PATH + '/csvs/c1.csv').reset_index(drop=True)

            sender['time'] = sender['time'].apply(lambda x: int(float(x)))

            sender = sender[
                (sender['time'] > start_time) & (sender['time'] < end_time)]

            sender = sender.drop_duplicates('time')

            sender = sender.set_index('time')
            ax.plot(sender.index + 1, sender['bandwidth'],linewidth=LINEWIDTH, label=protocol)



    ax.step(list(range(start_time,end_time+1,10)),bw_capacities,where='post', color='black',linewidth=LINEWIDTH, label='capacity',  alpha=0.75)

    ax.set(xlabel="time (s)", ylabel="Sending Rate (Mbps)")
    fig.legend(ncol=3, loc='upper center',bbox_to_anchor=(0.5, 1.17),columnspacing=1,handletextpad=1)
    fig.savefig("runs/responsiveness_sending_rates_run%s_start%s_end%s.png" % (RUN,start_time,end_time), dpi=720)

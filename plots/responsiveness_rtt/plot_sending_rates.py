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

ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_responsiveness_bw_orcaexp3/fifo"
PROTOCOLS = ['cubic', 'orca', 'aurora']
BW = 50
DELAY = 10
QMULT = 1
RUNS = [16]
LOSSES=[0]
BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
BDP_IN_PKTS = BDP_IN_BYTES / 1500
start_time = 0
end_time = 70
LINEWIDTH = 0.5


for RUN in RUNS:
    fig, axes = plt.subplots(nrows=1, ncols=1,figsize=(6,3))
    ax = axes
    # ax2 = ax.twinx()

    for protocol in PROTOCOLS:
        PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_1flows_22tcpbuf_%s/run%s' % (BW, DELAY, int(QMULT * BDP_IN_PKTS), protocol, RUN)
        # Compute the average optimal throughput
        with open(PATH + '/emulation_info.json', 'r') as fin:
            emulation_info = json.load(fin)

        bw_capacities = list(filter(lambda elem: elem[4] >= start_time and elem[4] <= end_time, emulation_info['flows']))
        bw_capacities = list(filter(lambda elem: elem[5] == 'tbf', bw_capacities))
        bw_capacities = [x[-1][1] for x in bw_capacities]

        # min_rtts = list(filter(lambda elem: elem[4] >= start_time and elem[4] <= end_time, emulation_info['flows']))
        # min_rtts = list(filter(lambda elem: elem[5] == 'netem', min_rtts))
        # min_rtts = [x[-1][2] for x in min_rtts]

        if os.path.exists(PATH + '/csvs/c1.csv'):
            sender = pd.read_csv(PATH + '/csvs/c1.csv').reset_index(drop=True)

            sender['time'] = sender['time'].apply(lambda x: int(float(x)))

            sender = sender[
                (sender['time'] > start_time) & (sender['time'] < end_time)]

            sender = sender.drop_duplicates('time')

            sender = sender.set_index('time')
            ax.plot(sender.index, sender['bandwidth'],linewidth=LINEWIDTH, label=protocol)



    ax.step(list(range(start_time,end_time+1,10)),bw_capacities,where='post', color='black',linewidth=LINEWIDTH, label='capacity',  alpha=0.75)
    # ax2.step(list(range(start_time,end_time+1,10)),min_rtts,where='post', color='red',linewidth=LINEWIDTH, label='RTT', linestyle='dashed', alpha=0.5)
    # ax2.set_ylabel('min RTT (ms)')

    ax.set(xlabel="time (s)", ylabel="Sending Rate (Mbps)")
    fig.legend(ncol=3, loc='upper center',bbox_to_anchor=(0.5, 1.17),columnspacing=1,handletextpad=1)
    fig.savefig("runs2/responsiveness_sending_rates_run%s_start%s_end%s3.png" % (RUN,start_time,end_time), dpi=720)

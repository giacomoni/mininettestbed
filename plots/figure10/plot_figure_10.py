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
import statistics
from core.config import *



def get_df(ROOT_PATH, PROTOCOLS, RUNS, BW, DELAY, QMULT):
    BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
    BDP_IN_PKTS = BDP_IN_BYTES / 1500
    start_time = 0
    end_time = 300

    # List containing each data point (each run). Values for each datapoint: protocol, run_number, average_goodput, optimal_goodput
    data = []


    for protocol in PROTOCOLS:
        optimals = []
        for run in RUNS:
            PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_1flows_22tcpbuf_%s/run%s' % (BW, DELAY, int(QMULT * BDP_IN_PKTS), protocol, run)
            # Compute the average optimal throughput
            with open(PATH + '/emulation_info.json', 'r') as fin:
                emulation_info = json.load(fin)

            bw_capacities = list(filter(lambda elem: elem[5] == 'tbf', emulation_info['flows']))
            bw_capacities = [x[-1][1] for x in bw_capacities]
            optimal_mean = sum(bw_capacities)/len(bw_capacities)

            if protocol != 'aurora':
                if os.path.exists(PATH + '/sysstat/etcp_c1.log'):
                    systat1 = pd.read_csv(PATH + '/sysstat/etcp_c1.log', sep=';').rename(
                        columns={"# hostname": "hostname"})
                    retr1 = systat1[['timestamp', 'retrans/s']]

                    diff = retr1.diff()
                    ind = diff.index[diff['timestamp'] >= 10].tolist()
                    if len(ind) > 0:
                        ind = ind[0]
                        if ind >= 0:
                            retr1 = retr1.loc[ind+1:,:]

                    start_timestamp = retr1['timestamp'].iloc[0]


                    time_diff = retr1['timestamp'].iloc[-1] - start_timestamp
                    if not (time_diff <= 300):
                        continue


                    retr1['timestamp'] = retr1['timestamp'] - start_timestamp + 1

                    retr1 = retr1.rename(columns={'timestamp': 'time'})
                    valid = True

                else:
                    valid = False
            else:
                if os.path.exists(PATH + '/csvs/c1.csv'):
                    systat1 = pd.read_csv(PATH + '/csvs/c1.csv').rename(
                        columns={"retr": "retrans/s"})
                    retr1 = systat1[['time', 'retrans/s']]
                    valid = True
                else:
                    valid = False

            if valid:
                retr1['time'] = retr1['time'].apply(lambda x: int(float(x)))

                retr1 = retr1.drop_duplicates('time')

                retr1_total = retr1[(retr1['time'] > start_time) & (retr1['time'] < end_time)]
                retr1_total = retr1_total.set_index('time')
                data.append([protocol, run, retr1_total.mean()['retrans/s']*1500*8/(1024*1024)])

    COLUMNS = ['protocol', 'run_number', 'average_retr_rate']
    return pd.DataFrame(data, columns=COLUMNS)

COLOR = {'cubic': '#0C5DA5',
             'orca': '#00B945',
             'aurora': '#FF9500'}

PROTOCOLS = ['cubic', 'orca', 'aurora']
BW = 50
DELAY = 50
QMULT = 1
RUNS = list(range(1,51))

bw_rtt_data = get_df("%s/mininettestbed/nooffload/results_responsiveness_bw_rtt/fifo" % HOME_DIR, PROTOCOLS, RUNS, BW, DELAY, QMULT)
loss_data =  get_df("%s/mininettestbed/nooffload/results_responsiveness_loss/fifo" % HOME_DIR, PROTOCOLS, RUNS, BW, DELAY, QMULT)

BINS = 50
fig, axes = plt.subplots(nrows=1, ncols=1,figsize=(3,1.5))
ax = axes

for protocol in PROTOCOLS:
    avg_goodputs = bw_rtt_data[bw_rtt_data['protocol'] == protocol]['average_retr_rate']

    values, base = np.histogram(avg_goodputs, bins=BINS)
    # evaluate the cumulative
    cumulative = np.cumsum(values)
    # plot the cumulative function
    ax.plot(base[:-1], cumulative/50*100, label="%s-rtt" % protocol, c=COLOR[protocol])

    avg_goodputs = loss_data[loss_data['protocol'] == protocol]['average_retr_rate']
    values, base = np.histogram(avg_goodputs, bins=BINS)
    # evaluate the cumulative
    cumulative = np.cumsum(values)
    # plot the cumulative function
    ax.plot(base[:-1], cumulative / 50 * 100, label="%s-loss" % protocol, c=COLOR[protocol], linestyle='dashed')

ax.set(xlabel="Average Retr. Rate (Mbps)", ylabel="Percentage of Trials (\%)")

fig.legend(ncol=3, loc='upper center',bbox_to_anchor=(0.5, 1.19),columnspacing=0.5,handletextpad=0.5, handlelength=1)
for format in ['pdf', 'png']:
    fig.savefig("joined_retr_cdf.%s" % format, dpi=720)
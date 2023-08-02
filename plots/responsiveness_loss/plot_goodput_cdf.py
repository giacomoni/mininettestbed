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

ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_responsiveness_loss/fifo"
PROTOCOLS = ['cubic', 'orca', 'aurora']
BW = 50
DELAY = 50
QMULT = 1
RUNS = list(range(1,51))
LOSSES=[0]
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

        if os.path.exists(PATH + '/csvs/x1.csv'):
            receiver = pd.read_csv(PATH + '/csvs/x1.csv').reset_index(drop=True)

            receiver['time'] = receiver['time'].apply(lambda x: int(float(x)))

            receiver = receiver[
                (receiver['time'] > start_time) & (receiver['time'] < end_time)]

            receiver = receiver.drop_duplicates('time')

            receiver = receiver.set_index('time')
            protocol_mean = receiver.mean()['bandwidth']
            data.append([protocol,run,protocol_mean,optimal_mean])

        # min_rtts = list(filter(lambda elem: elem[5] == 'netem', emulation_info['flows']))
        # min_rtts = [x[-1][2] for x in min_rtts]

COLUMNS = ['protocol', 'run_number', 'average_goodput', 'optimal_goodput']
data_df = pd.DataFrame(data, columns=COLUMNS)
BINS = 50
figure(figsize=(3, 1.5), dpi=720)

fig, axes = plt.subplots(nrows=1, ncols=1,figsize=(3,1.5))
ax = axes

optimals = data_df[data_df['protocol'] == 'cubic']['optimal_goodput']
values, base = np.histogram(optimals, bins=BINS)
# evaluate the cumulative
cumulative = np.cumsum(values)
# plot the cumulative function
ax.plot(base[:-1], cumulative/50*100, c='black', label='optimal')

for protocol in PROTOCOLS:
    avg_goodputs = data_df[data_df['protocol'] == protocol]['average_goodput']
    values, base = np.histogram(avg_goodputs, bins=BINS)
    # evaluate the cumulative
    cumulative = np.cumsum(values)
    # plot the cumulative function
    ax.plot(base[:-1], cumulative/50*100, label=protocol)

ax.set(xlabel="Average Goodput (Mbps)", ylabel="Percentage of Trials (\%)")
fig.legend(ncol=2, loc='upper center',bbox_to_anchor=(0.5, 1.17),columnspacing=1,handletextpad=1)
fig.savefig("goodput_cdf.png", dpi=720)

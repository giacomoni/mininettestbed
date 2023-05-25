import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import scienceplots
plt.style.use('science')
import os
from matplotlib.ticker import ScalarFormatter
import numpy as np

ROOT_PATH = "/home/luca/mininettestbed/results_big_backup/results_intra_rtt/fifo"
PROTOCOLS = ['cubic', 'orca', 'aurora']
BWS = [100]
DELAYS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
QMULTS = [1]
RUNS = [1, 2, 3, 4, 5]
LOSSES=[0]

data = []


flow_duration = 100
keep_last_seconds = 20
start_time=0
end_time=100
for protocol in PROTOCOLS:
  for bw in BWS:
     for delay in DELAYS:
        for mult in QMULTS:

           BDP_IN_BYTES = int(bw * (2 ** 20) * 2 * delay * (10 ** -3) / 8)
           BDP_IN_PKTS = BDP_IN_BYTES / 1500

           goodput_ratios_20 = []
           goodput_ratios_total = []

           for run in RUNS:
              PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_22tcpbuf_%s/run%s' % (bw,delay,int(mult * BDP_IN_PKTS),protocol,run)
              if os.path.exists(PATH + '/csvs/x1.csv') and os.path.exists(PATH + '/csvs/x2.csv'):
                 receiver1_total = pd.read_csv(PATH + '/csvs/x1.csv').reset_index(drop=True)
                 receiver2_total = pd.read_csv(PATH + '/csvs/x2.csv').reset_index(drop=True)

                 receiver1_total['time'] = receiver1_total['time'].apply(lambda x: int(float(x)))
                 receiver2_total['time'] = receiver2_total['time'].apply(lambda x: int(float(x)))


                 receiver1_total = receiver1_total[(receiver1_total['time'] > start_time) & (receiver1_total['time'] < end_time)]
                 receiver2_total = receiver2_total[(receiver2_total['time'] > start_time) & (receiver2_total['time'] < end_time)]

                 receiver1_total = receiver1_total.drop_duplicates('time')
                 receiver2_total = receiver2_total.drop_duplicates('time')

                 receiver1 = receiver1_total[receiver1_total['time'] >= end_time - keep_last_seconds].reset_index(drop=True)
                 receiver2 = receiver2_total[receiver2_total['time'] >= end_time - keep_last_seconds].reset_index(drop=True)

                 receiver1_total = receiver1_total.set_index('time')
                 receiver2_total = receiver2_total.set_index('time')

                 receiver1 = receiver1.set_index('time')
                 receiver2 = receiver2.set_index('time')

                 total = receiver1_total.join(receiver2_total, how='inner', lsuffix='1', rsuffix='2')[['bandwidth1', 'bandwidth2']]
                 partial = receiver1.join(receiver2, how='inner', lsuffix='1', rsuffix='2')[['bandwidth1', 'bandwidth2']]

                 total = total.dropna()
                 partial = partial.dropna()

                 goodput_ratios_20.append(partial.min(axis=1)/partial.max(axis=1))
                 goodput_ratios_total.append(total.min(axis=1)/total.max(axis=1))
              else:
                 avg_goodput = None
                 std_goodput = None
                 jain_goodput_20 = None
                 jain_goodput_total = None

           goodput_ratios_20 = np.concatenate(goodput_ratios_20, axis=0)
           goodput_ratios_total = np.concatenate(goodput_ratios_total, axis=0)

           data_entry = [protocol, bw, delay, mult, goodput_ratios_20.mean(), goodput_ratios_20.std(), goodput_ratios_total.mean(), goodput_ratios_total.std()]
           data.append(data_entry)

summary_data = pd.DataFrame(data,
                           columns=['protocol', 'bandwidth', 'delay', 'qmult', 'goodput_ratio_20_mean',
                                    'goodput_ratio_20_std', 'goodput_ratio_total_mean', 'goodput_ratio_total_std'])

orca_data = summary_data[summary_data['protocol'] == 'orca'].set_index('delay')
cubic_data = summary_data[summary_data['protocol'] == 'cubic'].set_index('delay')
aurora_data = summary_data[summary_data['protocol'] == 'aurora'].set_index('delay')

LINEWIDTH = 1
ELINEWIDTH = 0.75
CAPTHICK = ELINEWIDTH
CAPSIZE= 2

fig, axes = plt.subplots(nrows=1, ncols=1)
ax = axes



markers, caps, bars = ax.errorbar(cubic_data.index, cubic_data['goodput_ratio_20_mean'], yerr=cubic_data['goodput_ratio_20_std'],marker='x',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK, label='cubic')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]
markers, caps, bars = ax.errorbar(orca_data.index,orca_data['goodput_ratio_20_mean'], yerr=orca_data['goodput_ratio_20_std'],marker='^',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,label='orca', linestyle='--')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]
markers, caps, bars = ax.errorbar(aurora_data.index,aurora_data['goodput_ratio_20_mean'], yerr=aurora_data['goodput_ratio_20_std'],marker='+',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,label='aurora', linestyle='-.')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]

ax.set(yscale='log',xlabel='One way delay ratio', ylabel='Goodput Ratio')
for axis in [ax.xaxis, ax.yaxis]:
    axis.set_major_formatter(ScalarFormatter())
ax.legend()
ax.grid()

plt.savefig('goodput_ratio_20.png', dpi=720)



fig, axes = plt.subplots(nrows=1, ncols=1)
ax = axes



markers, caps, bars = ax.errorbar(cubic_data.index,cubic_data['goodput_ratio_total_mean'], yerr=cubic_data['goodput_ratio_total_std'],marker='x',elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,linewidth=LINEWIDTH, label='cubic')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]
markers, caps, bars = ax.errorbar(orca_data.index,orca_data['goodput_ratio_total_mean'], yerr=cubic_data['goodput_ratio_total_std'],marker='^',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,label='orca', linestyle='--')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]
markers, caps, bars = ax.errorbar(aurora_data.index,aurora_data['goodput_ratio_total_mean'], yerr=aurora_data['goodput_ratio_total_std'],marker='+',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,label='aurora', linestyle='-.')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]

ax.set(yscale='log',xlabel='One way delay ratio', ylabel='Goodput Ratio')
for axis in [ax.xaxis, ax.yaxis]:
    axis.set_major_formatter(ScalarFormatter())
ax.legend()
ax.grid()

plt.savefig('goodput_ratio.png', dpi=720)

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import scienceplots
plt.style.use('science')
import os
from matplotlib.ticker import ScalarFormatter
import numpy as np

ROOT_PATH = "/Users/luca/Desktop/PhD/MininetEvaluationPaper/data/twoflows/results/fifo"
PROTOCOLS = ['cubic', 'orca', 'aurora']
BWS = [100]
DELAYS = [41]
QMULTS = [0.02,0.04,0.06,0.08, 0.1, 0.2,0.4,0.6,0.8,1,2,4,6,8,10]
RUNS = [1, 2, 3, 4, 5]
LOSSES=[0]

data = []
for protocol in PROTOCOLS:
  for bw in BWS:
     for delay in DELAYS:
        duration = 2*delay
        start_time = 2*delay
        end_time = 3*delay
        keep_last_seconds = int(0.25*delay)
        for mult in QMULTS:
           BDP_IN_BYTES = int(bw * (2 ** 20) * 2 * delay * (10 ** -3) / 8)
           BDP_IN_PKTS = BDP_IN_BYTES / 1500

           rtt_20 = []
           rtt_total = []

           for run in RUNS:
              PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_22tcpbuf_%s/run%s' % (bw,delay,int(mult * BDP_IN_PKTS),protocol,run)
              if protocol != 'aurora':
                 if os.path.exists(PATH + '/csvs/c1_probe.csv') and os.path.exists(PATH + '/csvs/c2_probe.csv'):
                    # Compute the avg and std rtt across all samples of both flows
                    sender1_total = pd.read_csv(PATH + '/csvs/c1_probe.csv').reset_index(drop=True)
                    sender2_total = pd.read_csv(PATH + '/csvs/c2_probe.csv').reset_index(drop=True)

                    sender1_total['srtt'] = sender1_total['srtt']/1000
                    sender2_total['srtt'] = sender2_total['srtt']/1000
              else:
                 if os.path.exists(PATH + '/csvs/c1.csv') and os.path.exists(PATH + '/csvs/c2.csv'):
                    sender1_total = pd.read_csv(PATH + '/csvs/c1.csv').reset_index(drop=True)
                    sender2_total = pd.read_csv(PATH + '/csvs/c2.csv').reset_index(drop=True)

                    sender1_total = sender1_total.rename(columns={'rtt': 'srtt'})
                    sender2_total = sender2_total.rename(columns={'rtt': 'srtt'})


              sender1_total = sender1_total[(sender1_total['time'] > start_time) & (sender1_total['time'] < end_time)]
              sender2_total = sender2_total[(sender2_total['time'] > start_time) & (sender2_total['time'] < end_time)]


              sender1 = sender1_total[sender1_total['time'] >= end_time - keep_last_seconds].reset_index(drop=True)
              sender2 = sender2_total[sender2_total['time'] >= end_time - keep_last_seconds].reset_index(drop=True)


              total = pd.concat([sender1_total, sender2_total])[['srtt']]
              partial = pd.concat([sender1, sender2])[['srtt']]

              rtt_20.append(partial)
              rtt_total.append(total)

           if len(rtt_20) > 0 and len(rtt_total) > 0:
              rtt_20 = np.concatenate(rtt_20, axis=0)
              rtt_total = np.concatenate(rtt_total, axis=0)

              data_entry = [protocol, bw, delay, mult, rtt_20.mean()/(2*delay), rtt_20.std()/(2*delay), rtt_total.mean()/(2*delay), rtt_total.std()/(2*delay)]
              data.append(data_entry)

summary_data = pd.DataFrame(data,
                           columns=['protocol', 'bandwidth', 'delay', 'qmult', 'rtt_20_mean',
                                    'rtt_20_std', 'rtt_total_mean', 'rtt_total_std'])

orca_data = summary_data[summary_data['protocol'] == 'orca'].set_index('qmult')
cubic_data = summary_data[summary_data['protocol'] == 'cubic'].set_index('qmult')
aurora_data = summary_data[summary_data['protocol'] == 'aurora'].set_index('qmult')

LINEWIDTH = 1
ELINEWIDTH = 0.75
CAPTHICK = ELINEWIDTH
CAPSIZE= 2

fig, axes = plt.subplots(nrows=1, ncols=1,figsize=(4,2))
ax = axes



markers, caps, bars = ax.errorbar(cubic_data.index, cubic_data['rtt_20_mean'], yerr=cubic_data['rtt_20_std'],marker='x',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK, label='cubic')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]
markers, caps, bars = ax.errorbar(orca_data.index,orca_data['rtt_20_mean'], yerr=orca_data['rtt_20_std'],marker='^',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,label='orca', linestyle='--')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]
markers, caps, bars = ax.errorbar(aurora_data.index,aurora_data['rtt_20_mean'], yerr=aurora_data['rtt_20_std'],marker='+',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,label='aurora', linestyle='-.')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]

ax.set(xlabel='Buffer Size (xBDP)', ylabel='Avg. RTT Gain', xscale='log')
for axis in [ax.xaxis, ax.yaxis]:
    axis.set_major_formatter(ScalarFormatter())
ax.legend(loc=2)
# ax.grid()

plt.savefig('rtt_gain_async_intra_20_over_bdp.png', dpi=720)



fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(4,2))
ax = axes



markers, caps, bars = ax.errorbar(cubic_data.index,cubic_data['rtt_total_mean'], yerr=cubic_data['rtt_total_std'],marker='x',elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,linewidth=LINEWIDTH, label='cubic')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]
markers, caps, bars = ax.errorbar(orca_data.index,orca_data['rtt_total_mean'], yerr=cubic_data['rtt_total_std'],marker='^',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,label='orca', linestyle='--')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]
markers, caps, bars = ax.errorbar(aurora_data.index,aurora_data['rtt_total_mean'], yerr=aurora_data['rtt_total_std'],marker='+',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,label='aurora', linestyle='-.')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]

ax.set(xlabel='Buffer Size (xBDP)', ylabel='Avg. RTT Gain', xscale='log')
for axis in [ax.xaxis, ax.yaxis]:
    axis.set_major_formatter(ScalarFormatter())
ax.legend(loc=2)
# ax.grid()

plt.savefig('rtt_gain_async_intra_over_bdp_linear.png', dpi=720)

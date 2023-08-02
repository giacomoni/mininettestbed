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
QMULTS = [0.02,0.04,0.06,0.08,0.1,0.2,0.4,0.6,0.8,1,2,4,6,8,10]
RUNS = [1, 2, 3, 4, 5]
LOSSES=[0]

data = []
for protocol in PROTOCOLS:
  for bw in BWS:
     for delay in DELAYS:
        for mult in QMULTS:
           BDP_IN_BYTES = int(bw * (2 ** 20) * 2 * delay * (10 ** -3) / 8)
           BDP_IN_PKTS = BDP_IN_BYTES / 1500

           retr_total = []

           for run in RUNS:
              PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_22tcpbuf_%s/run%s' % (bw,delay,int(mult * BDP_IN_PKTS),protocol,run)
              if protocol != 'aurora':
                 if os.path.exists(PATH + '/sysstat/etcp_c1.log'):
                    systat1 = pd.read_csv(PATH + '/sysstat/etcp_c1.log', sep=';').rename(
                       columns={"# hostname": "hostname"})
                    retr1 = systat1[['timestamp', 'retrans/s']]
                    systat2 = pd.read_csv(PATH + '/sysstat/etcp_c2.log', sep=';').rename(
                       columns={"# hostname": "hostname"})
                    retr2 = systat2[['timestamp', 'retrans/s']]
                    if retr1['timestamp'].iloc[0] <= retr2['timestamp'].iloc[0]:
                       start_timestamp = retr1['timestamp'].iloc[0]
                    else:
                       start_timestamp = retr2['timestamp'].iloc[0]

                    retr1['timestamp'] = retr1['timestamp'] - start_timestamp + 1
                    retr2['timestamp'] = retr2['timestamp'] - start_timestamp + 1

                    retr1 = retr1.rename(columns={'timestamp': 'time'})
                    retr2 = retr2.rename(columns={'timestamp': 'time'})
                    valid = True

                 else:
                    valid=False
              else:
                 if os.path.exists(PATH + '/csvs/c1.csv'):
                    systat1 = pd.read_csv(PATH + '/csvs/c1.csv').rename(
                       columns={"retr": "retrans/s"})
                    retr1 = systat1[['time', 'retrans/s']]
                    systat2 = pd.read_csv(PATH + '/csvs/c1.csv').rename(
                       columns={"retr": "retrans/s"})
                    retr2 = systat2[['time', 'retrans/s']]
                    valid = True
                 else:
                    valid = False

              if valid:
                 retr1['time'] = retr1['time'].apply(lambda x: int(float(x)))
                 retr2['time'] = retr2['time'].apply(lambda x: int(float(x)))

                 retr1 = retr1.drop_duplicates('time')
                 retr2 = retr2.drop_duplicates('time')

                 retr1_total = retr1[(retr1['time'] > 0) & (retr1['time'] < 100)]
                 retr2_total = retr2[(retr2['time'] > 0) & (retr2['time'] < 100)]

                 retr1_total = retr1_total.set_index('time')
                 retr2_total = retr2_total.set_index('time')


                 total = retr1_total.join(retr2_total, how='inner', lsuffix='1', rsuffix='2')[
                    ['retrans/s1', 'retrans/s2']]

                 retr_total.append(total.sum(axis=1))

           if len(retr_total) > 0:
            retr_total = np.concatenate(retr_total, axis=0)


           if len(retr_total) > 0:
              data_entry = [protocol, bw, delay, delay/10, mult, retr_total.mean(), retr_total.std()]
              data.append(data_entry)

summary_data = pd.DataFrame(data,
                           columns=['protocol', 'bandwidth', 'delay', 'delay_ratio','qmult', 'retr_total_mean', 'retr_total_std'])

orca_data = summary_data[summary_data['protocol'] == 'orca'].set_index('qmult')
cubic_data = summary_data[summary_data['protocol'] == 'cubic'].set_index('qmult')
aurora_data = summary_data[summary_data['protocol'] == 'aurora'].set_index('qmult')

LINEWIDTH = 1
ELINEWIDTH = 0.75
CAPTHICK = ELINEWIDTH
CAPSIZE= 2

fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(4,2))
ax = axes



markers, caps, bars = ax.errorbar(cubic_data.index,cubic_data['retr_total_mean'], yerr=cubic_data['retr_total_std'],marker='x',elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,linewidth=LINEWIDTH, label='cubic')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]
markers, caps, bars = ax.errorbar(orca_data.index,orca_data['retr_total_mean'], yerr=cubic_data['retr_total_std'],marker='^',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,label='orca', linestyle='--')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]
markers, caps, bars = ax.errorbar(aurora_data.index,aurora_data['retr_total_mean'], yerr=aurora_data['retr_total_std'],marker='+',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,label='aurora', linestyle='-.')
[bar.set_alpha(0.5) for bar in bars]
[cap.set_alpha(0.5) for cap in caps]

ax.set(xlabel='Buffer Size (xBDP)', ylabel='Retr. Rate (segments/s)',yscale='log', xscale='log')
for axis in [ax.xaxis, ax.yaxis]:
    axis.set_major_formatter(ScalarFormatter())
ax.legend(loc=1, prop={'size': 8})
# ax.grid()

plt.savefig('retr_async_intra_over_bdp_log.png', dpi=720)

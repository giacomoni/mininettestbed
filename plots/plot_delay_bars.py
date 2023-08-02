import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import scienceplots
plt.style.use('science')
import os
from matplotlib.ticker import ScalarFormatter
import numpy as np
import matplotlib as mpl
mpl.rcParams['hatch.linewidth'] = 0.1  # previous pdf hatch linewidth

ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_fairness_intra_rtt_async/fifo"
PROTOCOLS = ['cubic', 'orca', 'aurora']
BWS = [100]
DELAYS = [10, 20, 30, 40, 50, 60, 70, 80, 100]
QMULTS = [0.2,1,4]
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
              PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_2flows_22tcpbuf_%s/run%s' % (bw,delay,int(mult * BDP_IN_PKTS),protocol,run)
              if protocol != 'aurora':
                 if os.path.exists(PATH + '/csvs/c1_probe.csv') and os.path.exists(PATH + '/csvs/c2_probe.csv'):
                    # Compute the avg and std rtt across all samples of both flows
                    sender1_total = pd.read_csv(PATH + '/csvs/c1_probe.csv').reset_index(drop=True)
                    sender2_total = pd.read_csv(PATH + '/csvs/c2_probe.csv').reset_index(drop=True)

                    sender1_total['srtt'] = sender1_total['srtt'] / 1000
                    sender2_total['srtt'] = sender2_total['srtt'] / 1000
              else:
                 if os.path.exists(PATH + '/csvs/c1.csv') and os.path.exists(PATH + '/csvs/c2.csv'):
                    sender1_total = pd.read_csv(PATH + '/csvs/c1.csv').reset_index(drop=True)
                    sender2_total = pd.read_csv(PATH + '/csvs/c2.csv').reset_index(drop=True)

                    sender1_total = sender1_total.rename(columns={'rtt': 'srtt'})
                    sender2_total = sender2_total.rename(columns={'rtt': 'srtt'})

              sender1_total = sender1_total[
                 (sender1_total['time'] > start_time) & (sender1_total['time'] < end_time)]
              sender2_total = sender2_total[
                 (sender2_total['time'] > start_time) & (sender2_total['time'] < end_time)]

              sender1 = sender1_total[sender1_total['time'] >= end_time - keep_last_seconds].reset_index(drop=True)
              sender2 = sender2_total[sender2_total['time'] >= end_time - keep_last_seconds].reset_index(drop=True)

              total = pd.concat([sender1_total, sender2_total])[['srtt']]
              partial = pd.concat([sender1, sender2])[['srtt']]

              rtt_20.append(partial)
              rtt_total.append(total)

           if len(rtt_20) > 0 and len(rtt_total) > 0:
              rtt_20 = np.concatenate(rtt_20, axis=0)
              rtt_total = np.concatenate(rtt_total, axis=0)

              data_entry = [protocol, bw, delay, mult, rtt_20.mean() / (2 * delay), rtt_20.std() / (2 * delay),
                            rtt_total.mean() / (2 * delay), rtt_total.std() / (2 * delay)]
              data.append(data_entry)


summary_data = pd.DataFrame(data,
                           columns=['protocol', 'bandwidth', 'delay', 'qmult', 'rtt_20_mean',
                                    'rtt_20_std', 'rtt_total_mean', 'rtt_total_std'])

orca_data = summary_data[summary_data['protocol'] == 'orca'].groupby('qmult').mean()
cubic_data = summary_data[summary_data['protocol'] == 'cubic'].groupby('qmult').mean()
aurora_data = summary_data[summary_data['protocol'] == 'aurora'].groupby('qmult').mean()

LINEWIDTH = 1
ELINEWIDTH = 0.75
CAPTHICK = ELINEWIDTH
CAPSIZE= 2

fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(3,1.5))
ax = axes

ind = np.arange(len(cubic_data.index))
width = 0.25

bar1 = ax.bar(ind, cubic_data['rtt_20_mean'], width,yerr=cubic_data['rtt_20_std'],error_kw={"elinewidth":ELINEWIDTH, "capsize":CAPSIZE, "capthick":CAPTHICK})
# ax.bar(ind, cubic_data['retr_20_mean']*(1-cubic_data['retr_ratio_20_mean']), width, bottom=cubic_data['retr_20_mean']*cubic_data['retr_ratio_20_mean'], color=bar1.patches[0].get_facecolor(),  hatch='...')

bar2 = ax.bar(ind + width, orca_data['rtt_20_mean'], width, yerr=orca_data['rtt_20_std'],error_kw={"elinewidth":ELINEWIDTH, "capsize":CAPSIZE, "capthick":CAPTHICK})
# ax.bar(ind + width, orca_data['retr_20_mean']*(1-orca_data['retr_ratio_20_mean']), width, bottom=orca_data['retr_20_mean']*orca_data['retr_ratio_20_mean'], color=bar2.patches[0].get_facecolor(),  hatch='...')


bar3 = ax.bar(ind + width * 2, aurora_data['rtt_20_mean'], width, yerr=aurora_data['rtt_20_std'],error_kw={"elinewidth":ELINEWIDTH, "capsize":CAPSIZE, "capthick":CAPTHICK})
# ax.bar(ind + width * 2, aurora_data['retr_20_mean']*(1-aurora_data['retr_ratio_20_mean']), width, bottom=aurora_data['retr_20_mean']*aurora_data['retr_ratio_20_mean'], color=bar3.patches[0].get_facecolor(),  hatch='...')



ax.set(yscale='linear',xlabel='Buffer size (\%BDP)', ylabel='RTT/RTT_{min}')

ax.set_xticks(ind + width, ['20\%', '100\%', '400\%'])
ax.legend((bar1, bar2, bar3), ('cubic', 'orca', 'aurora'), loc=2)
plt.savefig('delay_gain_async_intra_20_%s.png' % mult, dpi=720)



fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(3,1.5))
ax = axes



ind = np.arange(len(cubic_data.index))
width = 0.25

bar1 = ax.bar(ind, cubic_data['rtt_total_mean'], width, yerr=cubic_data['rtt_total_std'],error_kw={"elinewidth": ELINEWIDTH, "capsize": CAPSIZE, "capthick": CAPTHICK})
# ax.bar(ind, cubic_data['retr_total_mean']*(1-cubic_data['retr_ratio_total_mean']), width, bottom=cubic_data['retr_total_mean']*cubic_data['retr_ratio_total_mean'], color=bar1.patches[0].get_facecolor(), hatch='...')


bar2 = ax.bar(ind + width, orca_data['rtt_total_mean'], width, yerr=orca_data['rtt_total_std'],error_kw={"elinewidth": ELINEWIDTH, "capsize": CAPSIZE, "capthick": CAPTHICK})
# ax.bar(ind + width, orca_data['retr_total_mean']*(1-orca_data['retr_ratio_total_mean']), width, bottom=orca_data['retr_total_mean']*orca_data['retr_ratio_total_mean'], color=bar2.patches[0].get_facecolor(),  hatch='...')

bar3 = ax.bar(ind + width * 2, aurora_data['rtt_total_mean'], width, yerr=aurora_data['rtt_total_std'],error_kw={"elinewidth":ELINEWIDTH, "capsize":CAPSIZE, "capthick":CAPTHICK})
# ax.bar(ind + width * 2, aurora_data['retr_total_mean']*(1-aurora_data['retr_ratio_total_mean']), width, bottom=aurora_data['retr_total_mean']*aurora_data['retr_ratio_total_mean'], color=bar3.patches[0].get_facecolor(),  hatch='...')


ax.set(yscale='linear',xlabel='Buffer size (\%BDP)',  ylabel='RTT/RTT_{min}')

ax.set_xticks(ind + width, ['20\%', '100\%', '400\%'])
ax.legend((bar1, bar2, bar3), ('cubic', 'orca', 'aurora'),loc=2 )

plt.savefig('delay_gain_async_intra_total_%s.png' % mult, dpi=720)
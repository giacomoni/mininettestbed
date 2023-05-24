import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import scienceplots
plt.style.use('science')
import os
from matplotlib.ticker import ScalarFormatter

ROOT_PATH = "/home/luca/mininettestbed/results_big_backup/results_fairness_async/fifo"
PROTOCOLS = ['cubic', 'orca', 'aurora']
BW = 100
DELAY = 10
QMULTS = 1
RUNS = [1, 2, 3, 4, 5]
FLOWS = 2


data = {'cubic':
           {1: pd.DataFrame([], columns=['time','mean', 'std']),
            2: pd.DataFrame([], columns=['time','mean', 'std']),
            3: pd.DataFrame([], columns=['time','mean', 'std']),
            4: pd.DataFrame([], columns=['time','mean', 'std'])},
        'orca':
           {1: pd.DataFrame([], columns=['time', 'mean', 'std']),
            2: pd.DataFrame([], columns=['time', 'mean', 'std']),
            3: pd.DataFrame([], columns=['time', 'mean', 'std']),
            4: pd.DataFrame([], columns=['time', 'mean', 'std'])},
        'aurora':
           {1: pd.DataFrame([], columns=['time', 'mean', 'std']),
            2: pd.DataFrame([], columns=['time', 'mean', 'std']),
            3: pd.DataFrame([], columns=['time', 'mean', 'std']),
            4: pd.DataFrame([], columns=['time', 'mean', 'std'])}
        }

start_time = 0
end_time = 100
# Plot throughput over time
for protocol in PROTOCOLS:
   BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
   BDP_IN_PKTS = BDP_IN_BYTES / 1500
   senders = {1: [], 2: [], 3: [], 4:[]}
   receivers = {1: [], 2: [], 3: [], 4:[]}
   for run in RUNS:
      PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_2flows_22tcpbuf_%s/run%s' % (BW,DELAY,int(QMULTS * BDP_IN_PKTS),protocol,run)
      for n in range(FLOWS):
         if os.path.exists(PATH + '/csvs/c%s.csv' % (n+1)):
            sender = pd.read_csv(PATH +  '/csvs/c%s.csv' % (n+1))
            senders[n+1].append(sender)

         if os.path.exists(PATH + '/csvs/x%s.csv' % (n+1)):
            receiver_total = pd.read_csv(PATH + '/csvs/x%s.csv' % (n+1)).reset_index(drop=True)
            receiver_total = receiver_total[['time', 'bandwidth']]
            receiver_total['time'] = receiver_total['time'].apply(lambda x: int(float(x)))
            receiver_total['bandwidth'] = receiver_total['bandwidth'].ewm(alpha=7/8).mean()

            receiver_total = receiver_total[(receiver_total['time'] >= (start_time+n*25)) & (receiver_total['time'] <= (end_time+n*25))]
            receiver_total = receiver_total.drop_duplicates('time')
            receiver_total = receiver_total.set_index('time')
            receivers[n+1].append(receiver_total)

   # For each flow, receivers contains a list of dataframes with a time and bandwidth column. These dataframes SHOULD have
   # exactly the same index. Now I can concatenate and compute mean and std
   for n in range(FLOWS):
      for df in receivers[n+1]:
         print(len(df))
      data[protocol][n+1]['mean'] = pd.concat(receivers[n+1], axis=1).mean(axis=1)
      data[protocol][n+1]['std'] = pd.concat(receivers[n+1], axis=1).std(axis=1)
      data[protocol][n+1].index = pd.concat(receivers[n+1], axis=1).index


LINEWIDTH = 1
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(10, 3))

for i,protocol in enumerate(PROTOCOLS):
   ax = axes[i]
   for n in range(FLOWS):
      ax.plot(data[protocol][n+1].index, data[protocol][n+1]['mean'], linewidth=LINEWIDTH, label=protocol)
      ax.fill_between(data[protocol][n+1].index, data[protocol][n+1]['mean'] - data[protocol][n+1]['std'], data[protocol][n+1]['mean'] + data[protocol][n+1]['std'], alpha=0.2)

   ax.set(ylabel='Goodput (Mbps)', xlabel='time (s)', ylim=[0,100])
   ax.set(title='%s' % protocol)

fig.suptitle("%s Mbps, %s RTT, %sxBDP" % (BW, 2*DELAY, QMULTS))
fig.tight_layout()
fig.subplots_adjust(top=0.88)
plt.savefig('goodput_over_time_%smbps_%sms_%sbuf_%s.png' % (BW,DELAY,QMULTS,FLOWS), dpi=720)





















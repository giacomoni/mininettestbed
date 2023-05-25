import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import scienceplots
plt.style.use('science')
import os
from matplotlib.ticker import ScalarFormatter

# Plot congestion window, or sending rate
ROOT_PATH =  "/home/luca/mininettestbed/results_fairness_inter_rtt_async_2_correct/fifo"
PROTOCOLS = ['cubic', 'orca', 'aurora']
BW = 100
DELAY = 100
QMULT = 1
RUNS = [1, 2, 3, 4, 5]
BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
BDP_IN_PKTS = BDP_IN_BYTES / 1500

fig, axes = plt.subplots(nrows=5, ncols=3, figsize=(10, 6))

sending = {'cubic': [], 'orca': [], 'aurora': []}

for protocol in PROTOCOLS:

  BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
  BDP_IN_PKTS = BDP_IN_BYTES / 1500

  for run in RUNS:
     series = {'c1': None, 'c2': None}
     PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_2flows_22tcpbuf_%s/run%s' % (
     BW, DELAY, int(QMULT * BDP_IN_PKTS), protocol, run)
     if protocol != 'aurora':
        if os.path.exists(PATH + '/csvs/c1_probe.csv') and os.path.exists(PATH + '/csvs/c2_probe.csv'):
           sender1 = pd.read_csv(PATH + '/csvs/c1_probe.csv').reset_index(drop=True)
           sender2 = pd.read_csv(PATH + '/csvs/c2_probe.csv').reset_index(drop=True)

           sender1 = sender1[['time', 'cwnd']]
           sender2 = sender2[['time', 'cwnd']]

           sender1['time'] = sender1['time'].apply(lambda x: float(x))
           sender2['time'] = sender2['time'].apply(lambda x: float(x))
     else:
        if os.path.exists(PATH + '/csvs/c1.csv') and os.path.exists(PATH + '/csvs/c2.csv'):
           sender1 = pd.read_csv(PATH + '/csvs/c1.csv').reset_index(drop=True)
           sender2 = pd.read_csv(PATH + '/csvs/c2.csv').reset_index(drop=True)

           sender1 = sender1[['time', 'bandwidth']]
           sender2 = sender2[['time', 'bandwidth']]

           sender1['time'] = sender1['time'].apply(lambda x: float(x))
           sender2['time'] = sender2['time'].apply(lambda x: float(x))

           sender1['bandwidth'] = sender1['bandwidth'].ewm(alpha=0.5).mean()
           sender2['bandwidth'] = sender2['bandwidth'].ewm(alpha=0.5).mean()

     series['c1'] = sender1
     series['c2'] = sender2

     sending[protocol].append(series)
LINEWIDTH = 1

for i, protocol in enumerate(PROTOCOLS):
  for run in RUNS:
     ax = axes[run - 1][i]
     x1 = sending[protocol][run - 1]['c1']['time']
     x2 = sending[protocol][run - 1]['c2']['time']

     if protocol != 'aurora':
        y1 = sending[protocol][run - 1]['c1']['cwnd']
        y2 = sending[protocol][run - 1]['c2']['cwnd']

     else:
        y1 = sending[protocol][run - 1]['c1']['bandwidth']
        y2 = sending[protocol][run - 1]['c2']['bandwidth']

     ax.plot(x1, y1, linewidth=LINEWIDTH, alpha=0.75)
     ax.plot(x2, y2, linewidth=LINEWIDTH, alpha=0.75)
     if protocol != 'aurora':
        ax.set(ylabel='cwnd (pkts)', ylim=[10,3000], yscale='log')
        ax.axhline(y=2*BDP_IN_PKTS, color='r', linestyle='--', alpha=0.5)
        ax.axhline(y=BDP_IN_PKTS, color='r', linestyle='--', alpha=0.5)


     else:
        ax.set(ylabel='Send Rate (Mbps)', ylim=[0,200], yscale='linear')
        ax.axhline(y=100, color='r', linestyle='--', alpha=0.5)
        ax.axhline(y=50, color='r', linestyle='--', alpha=0.5)


     if run == 5:
        ax.set(xlabel='time (s)')
     ax.set_title('%s - Run %s' % (protocol, run))

     ax.set(xlim=[0,125])

     ax.grid()

plt.tight_layout()
plt.savefig("sending_%s.png" % DELAY, dpi=720)
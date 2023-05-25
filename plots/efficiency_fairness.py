import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import scienceplots
plt.style.use('science')
import os
from matplotlib.ticker import ScalarFormatter

def fairness_and_efficiency(ROOT_PATH, PROTOCOLS, BW, DELAY, QMULT, RUNS, sync=True):

   ratios = {'cubic': None, 'orca': None, 'aurora': None}
   sums = {'cubic': None, 'orca': None, 'aurora': None}

   for protocol in PROTOCOLS:

      BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
      BDP_IN_PKTS = BDP_IN_BYTES / 1500

      ratios_runs = []
      sums_runs = []

      for run in RUNS:
         PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_22tcpbuf_%s/run%s' % (BW, DELAY, int(QMULT * BDP_IN_PKTS), protocol, run)
         if os.path.exists(PATH + '/csvs/x1.csv') and os.path.exists(PATH + '/csvs/x2.csv'):
            receiver1 = pd.read_csv(PATH + '/csvs/x1.csv').reset_index(drop=True)
            receiver2 = pd.read_csv(PATH + '/csvs/x2.csv').reset_index(drop=True)

            receiver1 = receiver1[['time', 'bandwidth']]
            receiver2 = receiver2[['time', 'bandwidth']]

            receiver1['time'] = receiver1['time'].apply(lambda x: int(float(x)))
            receiver2['time'] = receiver2['time'].apply(lambda x: int(float(x)))

            receiver1 = receiver1.drop_duplicates('time')
            receiver2 = receiver2.drop_duplicates('time')

            receiver1['bandwidth'] = receiver1['bandwidth'].ewm(alpha=0.5).mean()
            receiver2['bandwidth'] = receiver2['bandwidth'].ewm(alpha=0.5).mean()

            if sync:
               receiver1 = receiver1[(receiver1['time'] > 0) & (receiver1['time'] <= 100)]
               receiver2 = receiver2[(receiver2['time'] > 0) & (receiver2['time'] <= 100)]

               tmp = receiver1.merge(receiver2, how='inner', on='time')

               tmp = tmp.set_index('time')

               ratios_runs.append(tmp.min(axis=1)/tmp.max(axis=1))
               sums_runs.append(tmp.sum(axis=1) / 100)
            else:
               receiver1_middle = receiver1[(receiver1['time'] > 25) & (receiver1['time'] <= 100)]
               receiver2_middle = receiver2[(receiver2['time'] > 25) & (receiver2['time'] <= 100)]


               receiver1_middle = receiver1_middle.set_index('time')
               receiver2_middle = receiver2_middle.set_index('time')

               # Find which flow starts first
               if len(receiver1[receiver1['time'] < 25]) > 0:
                 receiver_start = receiver1[receiver1['time'] <= 25]
                 receiver_end = receiver2[receiver2['time'] > 100]
               else:
                 receiver_start = receiver2[receiver2['time'] <= 25]
                 receiver_end = receiver1[receiver1['time'] > 100]


               tmp_middle = receiver1_middle.merge(receiver2_middle, how='inner', on='time')
               receiver_start = receiver_start.set_index('time')
               receiver_end = receiver_end.set_index('time')

               sum_tmp = pd.concat([receiver_start/100,tmp_middle.sum(axis=1)/100, receiver_end/100])
               ratio_tmp =  pd.concat([receiver_start/receiver_start,tmp_middle.min(axis=1)/tmp_middle.max(axis=1), receiver_end/receiver_end])

               ratios_runs.append(ratio_tmp)
               sums_runs.append(sum_tmp)

      ratios[protocol] = pd.concat(ratios_runs, axis=1)
      sums[protocol] = pd.concat(sums_runs, axis=1)

   return sums, ratios

if __name__ == '__main__':
    ROOT_PATH = "/home/luca/mininettestbed/results_big_backup/results_intra_rtt/fifo"
    PROTOCOLS = ['cubic', 'orca', 'aurora']
    BW = 100
    DELAYS = [10,20,30,40,50]
    QMULT = 1
    RUNS = [1, 2, 3, 4, 5]
    SYNC = True

    fig, axes = plt.subplots(nrows=2, ncols=5, figsize=(15, 4))

    for i, delay in enumerate(DELAYS):
        sums, ratios = fairness_and_efficiency(ROOT_PATH, PROTOCOLS, BW, delay, QMULT, RUNS, SYNC)
        # Sum plot
        ax = axes[0][i]
        LINEWIDTH = 1
        for protocol in PROTOCOLS:
            x = sums[protocol].index
            y = sums[protocol].mean(axis=1)
            err = sums[protocol].std(axis=1)
            ax.plot(x, y, linewidth=LINEWIDTH, label=protocol)
            ax.fill_between(x, y - err, y + err, alpha=0.2)
            if i == 0:
                ax.set(ylabel='Normalised Aggregate Goodput')
            ax.set(ylim=[0, 1.25], xlim=[0, 125])
            ax.set_title('%s ms' % (delay ))
            ax.legend()
            ax.grid()

        # Fairness plot
        ax = axes[1][i]
        for protocol in PROTOCOLS:
            x = ratios[protocol].index
            y = ratios[protocol].mean(axis=1)
            err = ratios[protocol].std(axis=1)
            ax.plot(x, y, linewidth=LINEWIDTH, label=protocol)
            ax.fill_between(x, y - err, y + err, alpha=0.2)
            if i == 0:
                ax.set(ylabel='Goodputs Ratio')
            ax.set(xlabel='time (s)', xlim=[0, 125], yscale='log')
            ax.legend()
            ax.grid()

    plt.tight_layout()
    plt.savefig("first_five.png", dpi=720)

    # Plot the efficiency, fairness over time (last 5)
    DELAYS = [60, 70, 80, 90, 100]

    fig, axes = plt.subplots(nrows=2, ncols=5, figsize=(15, 4))

    for i, delay in enumerate(DELAYS):
        sums, ratios = fairness_and_efficiency(ROOT_PATH, PROTOCOLS, BW, delay, QMULT, RUNS, SYNC)
        # Sum plot
        ax = axes[0][i]
        LINEWIDTH = 1
        for protocol in PROTOCOLS:
            x = sums[protocol].index
            y = sums[protocol].mean(axis=1)
            err = sums[protocol].std(axis=1)
            ax.plot(x, y, linewidth=LINEWIDTH, label=protocol)
            ax.fill_between(x, y - err, y + err, alpha=0.2)
            if i == 0:
                ax.set(ylabel='Normalised Aggregate Goodput')

            ax.set(ylim=[0, 1.25], xlim=[0, 125])
            ax.set_title('%s ms' % delay )
            ax.legend()
            ax.grid()

        # Fairness plot
        ax = axes[1][i]
        for protocol in PROTOCOLS:
            x = ratios[protocol].index
            y = ratios[protocol].mean(axis=1)
            err = ratios[protocol].std(axis=1)
            ax.plot(x, y, linewidth=LINEWIDTH, label=protocol)
            ax.fill_between(x, y - err, y + err, alpha=0.2)
            if i == 0:
                ax.set(ylabel='Goodputs Ratio')
            ax.set(xlabel='time (s)', xlim=[0, 125], yscale='log')
            ax.legend()
            ax.grid()

    plt.tight_layout()
    plt.savefig("last_five.png", dpi=720)


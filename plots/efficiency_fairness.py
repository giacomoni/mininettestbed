import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import scienceplots
plt.style.use('science')
import os
from matplotlib.ticker import ScalarFormatter



def fairness_and_efficiency(ROOT_PATH, PROTOCOLS, BW, DELAY, QMULT, RUNS, sync=True):
   duration = 2*DELAY
   start_second_flow = DELAY
   end_first_flow = 2*2*DELAY
   end_second_flow =  2*2*DELAY

   # start_second_flow = 50
   # end_first_flow = 600
   # end_second_flow = 600

   ratios = {'cubic': None, 'orca': None, 'aurora': None}
   sums = {'cubic': None, 'orca': None, 'aurora': None}
   losses = {'cubic': None, 'orca': None, 'aurora': None}

   for protocol in PROTOCOLS:

      BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
      BDP_IN_PKTS = BDP_IN_BYTES / 1500

      ratios_runs = []
      sums_runs = []
      losses_runs=[]

      for run in RUNS:
         PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_2flows_22tcpbuf_%s/run%s' % (BW, DELAY, int(QMULT * BDP_IN_PKTS), protocol, run)
         if os.path.exists(PATH + '/csvs/x1.csv') and os.path.exists(PATH + '/csvs/x2.csv'):
            receiver1 = pd.read_csv(PATH + '/csvs/x1.csv').reset_index(drop=True)
            receiver2 = pd.read_csv(PATH + '/csvs/x2.csv').reset_index(drop=True)

            receiver1 = receiver1[['time', 'bandwidth']]
            receiver2 = receiver2[['time', 'bandwidth']]

            receiver1['time'] = receiver1['time'].apply(lambda x: int(float(x)))
            receiver2['time'] = receiver2['time'].apply(lambda x: int(float(x)))

            receiver1 = receiver1.drop_duplicates('time')
            receiver2 = receiver2.drop_duplicates('time')

            # receiver1['bandwidth'] = receiver1['bandwidth'].ewm(alpha=0.5).mean()
            # receiver2['bandwidth'] = receiver2['bandwidth'].ewm(alpha=0.5).mean()

            if sync:
               receiver1 = receiver1[(receiver1['time'] > 0) & (receiver1['time'] <= 100)]
               receiver2 = receiver2[(receiver2['time'] > 0) & (receiver2['time'] <= 100)]

               tmp = receiver1.merge(receiver2, how='inner', on='time')

               tmp = tmp.set_index('time')

               ratios_runs.append(tmp.min(axis=1)/tmp.max(axis=1))
               sums_runs.append(tmp.sum(axis=1) / BW)
            else:
               receiver1_middle = receiver1[(receiver1['time'] > start_second_flow) & (receiver1['time'] <= end_second_flow)]
               receiver2_middle = receiver2[(receiver2['time'] > start_second_flow) & (receiver2['time'] <= end_second_flow)]


               receiver1_middle = receiver1_middle.set_index('time')
               receiver2_middle = receiver2_middle.set_index('time')

               # Find which flow starts first
               if len(receiver1[receiver1['time'] < start_second_flow]) > 0:
                 receiver_start = receiver1[receiver1['time'] <= start_second_flow]
                 receiver_end = receiver2[receiver2['time'] > end_first_flow]
               else:
                 receiver_start = receiver2[receiver2['time'] <= start_second_flow]
                 receiver_end = receiver1[receiver1['time'] > end_first_flow]


               # receiver_start = receiver1[receiver1['time'] <= start_second_flow]
               # receiver_end = receiver1[receiver1['time'] > end_second_flow]

               tmp_middle = receiver1_middle.merge(receiver2_middle, how='inner', on='time')
               receiver_start = receiver_start.set_index('time')
               receiver_end = receiver_end.set_index('time')

               sum_tmp = pd.concat([receiver_start/BW,tmp_middle.sum(axis=1)/BW, receiver_end/BW])
               ratio_tmp =  pd.concat([receiver_start/receiver_start,tmp_middle.min(axis=1)/tmp_middle.max(axis=1), receiver_end/receiver_end])

               ratios_runs.append(ratio_tmp)
               sums_runs.append(sum_tmp)


         if protocol != 'aurora':
             if os.path.exists(PATH + '/sysstat/etcp_c1.log'):
                systat1 = pd.read_csv(PATH + '/sysstat/etcp_c1.log', sep=';').rename(
                   columns={"# hostname": "hostname"})
                retr1 = systat1[['timestamp','retrans/s']]
                systat2 = pd.read_csv(PATH + '/sysstat/etcp_c2.log', sep=';').rename(
                   columns={"# hostname": "hostname"})
                retr2 = systat2[['timestamp','retrans/s']]
                if retr1['timestamp'].iloc[0] <= retr2['timestamp'].iloc[0]:
                   start_timestamp = retr1['timestamp'].iloc[0]
                else:
                   start_timestamp = retr2['timestamp'].iloc[0]

                retr1['timestamp'] = retr1['timestamp'] - start_timestamp + 1
                retr2['timestamp'] = retr2['timestamp'] - start_timestamp + 1

                retr1 = retr1.rename(columns={'timestamp': 'time'})
                retr2 = retr2.rename(columns={'timestamp': 'time'})

             else:
                print("Folder %s not found" % (PATH))
         else:
             if os.path.exists(PATH + '/csvs/c1.csv'):
                systat1 = pd.read_csv(PATH + '/csvs/c1.csv').rename(
                   columns={"retr": "retrans/s"})
                retr1 = systat1[['time','retrans/s']]
                systat2 = pd.read_csv(PATH + '/csvs/c1.csv').rename(
                   columns={"retr": "retrans/s"})
                retr2 = systat2[['time','retrans/s']]

         retr1['time'] = retr1['time'].apply(lambda x: int(float(x)))
         retr2['time'] = retr2['time'].apply(lambda x: int(float(x)))

         retr1 = retr1.drop_duplicates('time')
         retr2 = retr2.drop_duplicates('time')

         # retr1['retrans/s'] = retr1['retrans/s'].ewm(alpha=0.5).mean()
         # retr2['retrans/s'] = retr2['retrans/s'].ewm(alpha=0.5).mean()

         if sync:
             print("sync")
         else:
             retr1_middle = retr1[
                 (retr1['time'] > start_second_flow) & (retr1['time'] <= end_second_flow)]
             retr2_middle = retr2[
                 (retr2['time'] > start_second_flow) & (retr2['time'] <= end_second_flow)]

             retr1_middle = retr1_middle.set_index('time')
             retr2_middle = retr2_middle.set_index('time')

             # Find which flow starts first
             if len(retr1[retr1['time'] < start_second_flow]) > 0:
                 retr_start = retr1[retr1['time'] <= start_second_flow]
                 retr_end = retr2[retr2['time'] > end_first_flow]
             else:
                 retr_start = retr2[retr2['time'] <= start_second_flow]
                 retr_end = retr1[retr1['time'] > end_first_flow]

             # retr_start = retr1[retr1['time'] <= start_second_flow]
             # retr_end = retr1[retr1['time'] > end_second_flow]

             tmp_middle = retr1_middle.merge(retr2_middle, how='inner', on='time')
             retr_start = retr_start.set_index('time')
             retr_end = retr_end.set_index('time')

             loss_tmp = pd.concat([retr_start, tmp_middle.sum(axis=1), retr_end])

             losses_runs.append(loss_tmp)

      ratios[protocol] = pd.concat(ratios_runs, axis=1)
      sums[protocol] = pd.concat(sums_runs, axis=1)
      losses[protocol] = pd.concat(losses_runs, axis=1)

   return sums, ratios, losses

def plot_all():
    ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_fairness_intra_rtt_async/fifo"
    PROTOCOLS = ['cubic', 'orca', 'aurora']
    BW = 100
    DELAYS = [10, 20, 30, 40, 50]
    QMULT = 0.2
    RUNS = [1, 2, 3, 4, 5]
    SYNC = False
    SCALE='linear'
    fig, axes = plt.subplots(nrows=3, ncols=5, figsize=(15, 5))
    for i, delay in enumerate(DELAYS):
        duration = 2 * delay
        XLIM = [duration, 2 * duration]
        # XLIM = [0, 600]

        sums, ratios, losses = fairness_and_efficiency(ROOT_PATH, PROTOCOLS, BW, delay, QMULT, RUNS, SYNC)
        # Sum plot
        ax = axes[0][i]
        LINEWIDTH = 1
        for protocol in PROTOCOLS:
            x = sums[protocol].index
            y = sums[protocol].mean(axis=1)
            err = sums[protocol].std(axis=1)
            # Clip error to 90th percentile
            quantile = err.quantile(q=0.5)
            err = err.clip(0, quantile)

            ax.plot(x, y, linewidth=LINEWIDTH, label=protocol)
            ax.fill_between(x, y - err, y + err, alpha=0.2)
            if i == 0:
                ax.set(ylabel='Norm. Aggr. Goodput')
            ax.set(ylim=[0, 1.25], xlim=XLIM)
            ax.set_title('RTT %s ms' % (2 * delay))
            ax.grid()

        # Fairness plot
        ax = axes[1][i]
        for protocol in PROTOCOLS:
            x = ratios[protocol].index
            y = ratios[protocol].mean(axis=1)
            err = ratios[protocol].std(axis=1)
            # Clip error to 90th percentile
            quantile = err.quantile(q=0.5)
            err = err.clip(0, quantile)
            ax.plot(x, y, linewidth=LINEWIDTH, label=protocol)
            ax.fill_between(x, y - err, y + err, alpha=0.2)
            if i == 0:
                ax.set(ylabel='Goodputs Ratio')
            ax.set(xlabel='time (s)', xlim=XLIM, yscale=SCALE)
            ax.grid()

        ax = axes[2][i]
        for protocol in PROTOCOLS:
            x = losses[protocol].index
            y = losses[protocol].mean(axis=1)
            err = losses[protocol].std(axis=1)
            # Clip error to 90th percentile
            quantile = err.quantile(q=0.5)
            err = err.clip(0, quantile)
            ax.plot(x, y, linewidth=LINEWIDTH, label=protocol)
            ax.fill_between(x, y - err, y + err, alpha=0.2)
            if i == 0:
                ax.set(ylabel='Aggr. Retrans/s')
            ax.set(xlabel='time (s)', xlim=XLIM, yscale=SCALE)
            ax.grid()

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3, borderaxespad=-0.3)
    plt.tight_layout()
    plt.savefig("first_five_async_inter_%s.png" % QMULT, dpi=720)

    # Plot the efficiency, fairness over time (last 5)
    DELAYS = [60, 70, 80,  100]

    fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(15, 5))
    for i, delay in enumerate(DELAYS):
        duration = 2 * delay
        XLIM = [duration, 2 * duration]

        # XLIM = [0, 600]
        sums, ratios, losses = fairness_and_efficiency(ROOT_PATH, PROTOCOLS, BW, delay, QMULT, RUNS, SYNC)
        # Sum plot
        ax = axes[0][i]
        LINEWIDTH = 1
        for protocol in PROTOCOLS:
            x = sums[protocol].index
            y = sums[protocol].mean(axis=1)
            err = sums[protocol].std(axis=1)
            # Clip error to 90th percentile
            quantile = err.quantile(q=0.5)
            err = err.clip(0, quantile)
            ax.plot(x, y, linewidth=LINEWIDTH, label=protocol)
            ax.fill_between(x, y - err, y + err, alpha=0.2)
            if i == 0:
                ax.set(ylabel='Norm. Aggr. Goodput')

            ax.set(ylim=[0, 1.25], xlim=XLIM)
            ax.set_title('%s ms' % (2 * delay))
            ax.grid()

        # Fairness plot
        ax = axes[1][i]
        for protocol in PROTOCOLS:
            x = ratios[protocol].index
            y = ratios[protocol].mean(axis=1)
            err = ratios[protocol].std(axis=1)
            # Clip error to 90th percentile
            quantile = err.quantile(q=0.5)
            err = err.clip(0, quantile)
            ax.plot(x, y, linewidth=LINEWIDTH, label=protocol)
            ax.fill_between(x, y - err, y + err, alpha=0.2)
            if i == 0:
                ax.set(ylabel='Goodputs Ratio')
            ax.set(xlabel='time (s)', xlim=XLIM, yscale=SCALE)
            ax.grid()

        ax = axes[2][i]
        for protocol in PROTOCOLS:
            x = losses[protocol].index
            y = losses[protocol].mean(axis=1)
            err = losses[protocol].std(axis=1)
            # Clip error to 90th percentile
            quantile = err.quantile(q=0.5)
            err = err.clip(0, quantile)

            ax.plot(x, y, linewidth=LINEWIDTH, label=protocol)
            ax.fill_between(x, y - err, y + err, alpha=0.2)
            if i == 0:
                ax.set(ylabel='Aggr. Retrans/s')
            ax.set(xlabel='time (s)', xlim=XLIM, yscale=SCALE)
            ax.grid()

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3, borderaxespad=-0.3)
    plt.tight_layout()
    plt.savefig("last_five_async_inter_%s.png" % QMULT, dpi=720)

def plot_one():
    ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_fairness_intra_rtt_async/fifo"
    PROTOCOLS = ['cubic', 'orca', 'aurora']
    BW = 100
    DELAY = 40
    QMULT = 1
    RUNS = [1, 2, 3, 4, 5]
    SYNC = False
    FIGSIZE = (4,2)
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=FIGSIZE)

    duration = 2 * DELAY
    XLIM = [DELAY, 2 * duration]

    sums, ratios, losses = fairness_and_efficiency(ROOT_PATH, PROTOCOLS, BW, DELAY, QMULT, RUNS, SYNC)
    ax = axes
    LINEWIDTH = 1
    for protocol in PROTOCOLS:
        x = sums[protocol].index
        y = sums[protocol].mean(axis=1)
        err = sums[protocol].std(axis=1)
        # Clip error to 90th percentile
        # quantile = err.quantile(q=0.5)
        # err = err.clip(0, quantile)
        ax.plot(x, y, linewidth=LINEWIDTH, label=protocol)
        ax.fill_between(x, y - err, y + err, alpha=0.2)
        ax.set(ylabel='Norm. Aggr. Goodput')
        ax.set(xlabel='time (s)', xlim=XLIM, yscale='linear')
        ax.set(ylim=[0.5, 1.25], xlim=XLIM)
        ax.grid()

    plt.tight_layout()
    plt.savefig("efficiency_paper_1bdp.png", dpi=720)

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=FIGSIZE)
    # Fairness plot
    ax = axes
    for protocol in PROTOCOLS:
        x = ratios[protocol].index
        y = ratios[protocol].mean(axis=1)
        err = ratios[protocol].std(axis=1)
        # Clip error to 90th percentile
        # quantile = err.quantile(q=0.5)
        # err = err.clip(0, quantile)
        ax.plot(x, y, linewidth=LINEWIDTH, label=protocol)
        ax.fill_between(x, y - err, y + err, alpha=0.2)
        ax.set(ylabel='Goodputs Ratio')
        ax.set(xlabel='time (s)', xlim=XLIM, yscale='linear')
        ax.grid()

    ax.legend(loc='lower center', ncol=3)
    plt.tight_layout()
    plt.savefig("fairness_paper_1bdp.png", dpi=720)

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=FIGSIZE)
    ax = axes
    for protocol in PROTOCOLS:
        x = losses[protocol].index
        y = losses[protocol].mean(axis=1)
        err = losses[protocol].std(axis=1)
        # Clip error to 90th percentile
        # quantile = err.quantile(q=0.5)
        # err = err.clip(0, quantile)

        ax.plot(x, y, linewidth=LINEWIDTH, label=protocol)
        ax.fill_between(x, y - err, y + err, alpha=0.2)
        ax.set(ylabel='Aggr. Retrans/s')
        ax.set(xlabel='time (s)', xlim=XLIM, yscale='linear')
        ax.grid()


    plt.tight_layout()
    plt.savefig("retrans_paper_1bdp.png", dpi=720)


if __name__ == '__main__':
    # plot_all()
    plot_one()
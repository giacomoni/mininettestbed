import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import scienceplots
plt.style.use('science')
import os
from matplotlib.ticker import ScalarFormatter


def parse_orca_output(file, offset):
    with open(file, 'r') as fin:
        orcaOutput = fin.read()
    start_index = orcaOutput.find("----START----")
    end_index = orcaOutput.find("----END----")
    orcaOutput = orcaOutput[start_index:end_index]

    lines = orcaOutput.strip().split("\n")
    lines = [line for line in lines if line.strip() != '']

    # Extract the relevant information
    data = [line.split(",") for line in lines[1:]]
    columns = ["time", "bandwidth", "bytes"] if len(data[0]) == 3 else ["time", "bandwidth", "bytes", "totalgoodput"]

    # Create a pandas DataFrame
    df = pd.DataFrame(data, columns=columns)
    # Convert columns to appropriate types
    df["time"] = df["time"].astype(float)
    if len(columns) > 3:
        df["time"] = df["time"] + offset
    df["bandwidth"] = df["bandwidth"].astype(float) / 1000000
    df["bytes"] = df["bytes"].astype(float)
    if len(columns) > 3:
        df["totalgoodput"] = df["totalgoodput"].astype(float)

    return df


def fairness_and_efficiency(ROOT_PATH, PROTOCOLS, BW, DELAY, QMULT, RUNS, NFLOWS,sync=True):
   # STarting and ending  times of all flows. We are interested in the tie period when all flows are active
   start_flow_2 = 100
   start_flow_3 = 200
   start_flow_4 = 300
   end_flow_1 = 600
   end_flow_2 = 700
   end_flow_3 = 800
   end_flow_4 = 900

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
         PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (BW, DELAY, int(QMULT * BDP_IN_PKTS), NFLOWS,protocol, run)
         if not os.path.exists(PATH + '/csvs/x1.csv'):
             if os.path.exists(PATH + '/x1_output.txt'):
                 df = parse_orca_output(PATH + '/x1_output.txt',0)
                 df.to_csv(PATH + '/csvs/x1.csv', index=False)
         if not os.path.exists(PATH + '/csvs/x2.csv'):
             if os.path.exists(PATH + '/x2_output.txt'):
                 df = parse_orca_output(PATH + '/x2_output.txt', 0)
                 df.to_csv(PATH + '/csvs/x2.csv', index=False)
         if not os.path.exists(PATH + '/csvs/x3.csv'):
             if os.path.exists(PATH + '/x3_output.txt'):
                 df = parse_orca_output(PATH + '/x3_output.txt', 0)
                 df.to_csv(PATH + '/csvs/x3.csv', index=False)
         # if not os.path.exists(PATH + '/csvs/x4.csv'):
         #     if os.path.exists(PATH + '/x4_output.txt'):
         #         df = parse_orca_output(PATH + '/x4_output.txt', 0)
         #         df.to_csv(PATH + '/csvs/x4.csv', index=False)


         if os.path.exists(PATH + '/csvs/x1.csv') and os.path.exists(PATH + '/csvs/x2.csv'):
            receiver1 = pd.read_csv(PATH + '/csvs/x1.csv').reset_index(drop=True)
            receiver2 = pd.read_csv(PATH + '/csvs/x2.csv').reset_index(drop=True)
            receiver3 = pd.read_csv(PATH + '/csvs/x3.csv').reset_index(drop=True)
            # receiver4 = pd.read_csv(PATH + '/csvs/x4.csv').reset_index(drop=True)

            receiver1 = receiver1[['time', 'bandwidth']]
            receiver2 = receiver2[['time', 'bandwidth']]
            receiver3 = receiver3[['time', 'bandwidth']]
            # receiver4 = receiver4[['time', 'bandwidth']]

            receiver1['time'] = receiver1['time'].apply(lambda x: int(float(x)))
            receiver2['time'] = receiver2['time'].apply(lambda x: int(float(x)))
            receiver3['time'] = receiver3['time'].apply(lambda x: int(float(x)))
            # receiver4['time'] = receiver4['time'].apply(lambda x: int(float(x)))

            receiver1 = receiver1.drop_duplicates('time')
            receiver2 = receiver2.drop_duplicates('time')
            receiver3 = receiver3.drop_duplicates('time')
            # receiver4 = receiver4.drop_duplicates('time')

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
               receiver1_middle = receiver1[(receiver1['time'] > start_flow_4) & (receiver1['time'] <= end_flow_1)]
               receiver2_middle = receiver2[(receiver2['time'] > start_flow_4) & (receiver2['time'] <= end_flow_1)]
               receiver3_middle = receiver3[(receiver3['time'] > start_flow_4) & (receiver3['time'] <= end_flow_1)]
               # receiver4_middle = receiver4[(receiver4['time'] > start_flow_4) & (receiver4['time'] <= end_flow_1)]


               receiver1_middle = receiver1_middle.set_index('time')
               receiver2_middle = receiver2_middle.set_index('time')
               receiver3_middle = receiver3_middle.set_index('time')
               # receiver4_middle = receiver4_middle.set_index('time')

               # # Find which flow starts first
               # if len(receiver1[receiver1['time'] < start_second_flow]) > 0:
               #   receiver_start = receiver1[receiver1['time'] <= start_second_flow]
               #   receiver_end = receiver2[receiver2['time'] > end_first_flow]
               # else:
               #   receiver_start = receiver2[receiver2['time'] <= start_second_flow]
               #   receiver_end = receiver1[receiver1['time'] > end_first_flow]


               # receiver_start = receiver1[receiver1['time'] <= start_second_flow]
               # receiver_end = receiver1[receiver1['time'] > end_second_flow]

               tmp_middle = receiver1_middle.merge(receiver2_middle, how='inner', on='time').merge(receiver3_middle, how='inner', on='time')
               # receiver_start = receiver_start.set_index('time')
               # receiver_end = receiver_end.set_index('time')

               sum_tmp = tmp_middle.sum(axis=1)/BW
               ratio_tmp =  tmp_middle.min(axis=1)/tmp_middle.max(axis=1)

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
                systat3 = pd.read_csv(PATH + '/sysstat/etcp_c3.log', sep=';').rename(
                   columns={"# hostname": "hostname"})
                retr3 = systat3[['timestamp','retrans/s']]
                # systat4 = pd.read_csv(PATH + '/sysstat/etcp_c4.log', sep=';').rename(
                #    columns={"# hostname": "hostname"})
                # retr4 = systat4[['timestamp','retrans/s']]

                start_timestamp = retr1['timestamp'].iloc[0]

                retr1['timestamp'] = retr1['timestamp'] - start_timestamp + 1
                retr2['timestamp'] = retr2['timestamp'] - start_timestamp + 1
                retr3['timestamp'] = retr3['timestamp'] - start_timestamp + 1
                # retr4['timestamp'] = retr4['timestamp'] - start_timestamp + 1

                retr1 = retr1.rename(columns={'timestamp': 'time'})
                retr2 = retr2.rename(columns={'timestamp': 'time'})
                retr3 = retr3.rename(columns={'timestamp': 'time'})
                # retr4 = retr4.rename(columns={'timestamp': 'time'})

             else:
                print("Folder %s not found" % (PATH))
         else:
             if os.path.exists(PATH + '/csvs/c1.csv'):
                systat1 = pd.read_csv(PATH + '/csvs/c1.csv').rename(
                   columns={"retr": "retrans/s"})
                retr1 = systat1[['time','retrans/s']]
                systat2 = pd.read_csv(PATH + '/csvs/c2.csv').rename(
                   columns={"retr": "retrans/s"})
                retr2 = systat2[['time','retrans/s']]
                systat3 = pd.read_csv(PATH + '/csvs/c3.csv').rename(
                    columns={"retr": "retrans/s"})
                retr3 = systat3[['time', 'retrans/s']]
                # systat4 = pd.read_csv(PATH + '/csvs/c4.csv').rename(
                #     columns={"retr": "retrans/s"})
                # retr4 = systat4[['time', 'retrans/s']]

         retr1['time'] = retr1['time'].apply(lambda x: int(float(x)))
         retr2['time'] = retr2['time'].apply(lambda x: int(float(x)))
         retr3['time'] = retr3['time'].apply(lambda x: int(float(x)))
         # retr4['time'] = retr4['time'].apply(lambda x: int(float(x)))

         retr1 = retr1.drop_duplicates('time')
         retr2 = retr2.drop_duplicates('time')
         retr3 = retr3.drop_duplicates('time')
         # retr4 = retr4.drop_duplicates('time')

         # retr1['retrans/s'] = retr1['retrans/s'].ewm(alpha=0.5).mean()
         # retr2['retrans/s'] = retr2['retrans/s'].ewm(alpha=0.5).mean()

         if sync:
             print("sync")
         else:
             retr1_middle = retr1[
                 (retr1['time'] > start_flow_4) & (retr1['time'] <= end_flow_1)]
             retr2_middle = retr2[
                 (retr2['time'] > start_flow_4) & (retr2['time'] <= end_flow_1)]
             retr3_middle = retr3[
                 (retr3['time'] > start_flow_4) & (retr3['time'] <= end_flow_1)]
             # retr4_middle = retr4[
             #     (retr4['time'] > start_flow_4) & (retr4['time'] <= end_flow_1)]

             retr1_middle = retr1_middle.set_index('time')
             retr2_middle = retr2_middle.set_index('time')
             retr3_middle = retr3_middle.set_index('time')
             # retr4_middle = retr4_middle.set_index('time')

             # # Find which flow starts first
             # if len(retr1[retr1['time'] < start_second_flow]) > 0:
             #     retr_start = retr1[retr1['time'] <= start_second_flow]
             #     retr_end = retr2[retr2['time'] > end_first_flow]
             # else:
             #     retr_start = retr2[retr2['time'] <= start_second_flow]
             #     retr_end = retr1[retr1['time'] > end_first_flow]

             # retr_start = retr1[retr1['time'] <= start_second_flow]
             # retr_end = retr1[retr1['time'] > end_second_flow]

             tmp_middle = retr1_middle.merge(retr2_middle, how='inner', on='time').merge(retr3_middle, how='inner', on='time')
             # retr_start = retr_start.set_index('time')
             # retr_end = retr_end.set_index('time')

             loss_tmp = tmp_middle.sum(axis=1)

             losses_runs.append(loss_tmp)

      ratios[protocol] = pd.concat(ratios_runs, axis=1)
      sums[protocol] = pd.concat(sums_runs, axis=1)
      losses[protocol] = pd.concat(losses_runs, axis=1)

   return sums, ratios, losses

def plot_all():
    ROOT_PATH = "/Volumes/LaCie/mininettestbed/results_fairness_intra_rtt_async_final/fifo"
    PROTOCOLS = ['cubic', 'orca', 'aurora']
    BW = 100
    DELAYS = [10, 20, 30, 40, 50]
    QMULT = 0.2
    RUNS = [1, 2, 3, 4, 5]
    SYNC = False
    fig, axes = plt.subplots(nrows=3, ncols=5, figsize=(15, 5))
    for i, delay in enumerate(DELAYS):
        duration = 2 * delay
        XLIM = [0, 2 * duration]
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
            ax.set(xlabel='time (s)', xlim=XLIM, yscale='log')
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
            ax.set(xlabel='time (s)', xlim=XLIM, yscale='log')
            ax.grid()

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3, borderaxespad=-0.3)
    plt.tight_layout()
    plt.savefig("first_five_async_inter_%s.png" % QMULT, dpi=720)

    # Plot the efficiency, fairness over time (last 5)
    DELAYS = [60, 70, 80, 90, 100]

    fig, axes = plt.subplots(nrows=3, ncols=5, figsize=(15, 5))
    for i, delay in enumerate(DELAYS):
        duration = 2 * delay
        XLIM = [0, 2 * duration]

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
            ax.set(xlabel='time (s)', xlim=XLIM, yscale='log')
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
            ax.set(xlabel='time (s)', xlim=XLIM, yscale='log')
            ax.grid()

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3, borderaxespad=-0.3)
    plt.tight_layout()
    plt.savefig("last_five_async_inter_%s.png" % QMULT, dpi=720)

def plot_one():
    ROOT_PATH = "/Volumes/LaCie/mininettestbed/results_fairness_async_final_no_offload_routers/fifo"
    PROTOCOLS = ['cubic', 'orca', 'aurora']
    BW = 100
    DELAY = 10
    QMULT = 0.2
    RUNS = [1, 2, 3]
    SYNC = False
    FIGSIZE = (4,2)
    NFLOWS = 3
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=FIGSIZE)

    XLIM = [300, 600]

    sums, ratios, losses = fairness_and_efficiency(ROOT_PATH, PROTOCOLS, BW, DELAY, QMULT, RUNS, NFLOWS, SYNC)
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
        # ax.fill_between(x, y - err, y + err, alpha=0.2)
        ax.set(ylabel='Norm. Aggr. Goodput')
        ax.set(xlabel='time (s)', xlim=XLIM, yscale='linear')
        ax.set(ylim=[0.5, 1.25], xlim=XLIM)
        ax.grid()

    plt.tight_layout()
    plt.savefig("efficiency_paper_%sbdp_%sflows_no_offload_routers.png" % (QMULT, NFLOWS), dpi=720)

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
        # ax.fill_between(x, y - err, y + err, alpha=0.2)
        ax.set(ylabel='Goodputs Ratio')
        ax.set(xlabel='time (s)', xlim=XLIM, yscale='linear')
        ax.grid()

    ax.legend(loc='upper center', ncol=3)
    plt.tight_layout()
    plt.savefig("fairness_paper_%sbdp_%sflows_no_offload_routers.png"% (QMULT, NFLOWS), dpi=720)

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
        # ax.fill_between(x, y - err, y + err, alpha=0.2)
        ax.set(ylabel='Aggr. Retrans')
        ax.set(xlabel='time (s)', xlim=XLIM, yscale='log')
        ax.grid()


    plt.tight_layout()
    plt.savefig("retrans_paper_%sbdp_%sflows_no_offload_routers.png"% (QMULT, NFLOWS), dpi=720)


if __name__ == '__main__':
    # plot_all()
    plot_one()
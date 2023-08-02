import pandas as pd
import matplotlib.pyplot as plt
import scienceplots
plt.style.use('science')
import os
import matplotlib as mpl
mpl.rcParams['agg.path.chunksize'] = 10000
pd.set_option('display.max_rows', None)
from functools import reduce
import numpy as np
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms

def confidence_ellipse(x, y, ax, n_std=1.0, facecolor='none', **kwargs):
    """
    Create a plot of the covariance confidence ellipse of *x* and *y*.

    Parameters
    ----------
    x, y : array-like, shape (n, )
        Input data.

    ax : matplotlib.axes.Axes
        The axes object to draw the ellipse into.

    n_std : float
        The number of standard deviations to determine the ellipse's radiuses.

    **kwargs
        Forwarded to `~matplotlib.patches.Ellipse`

    Returns
    -------
    matplotlib.patches.Ellipse
    """
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
    # Using a special case to obtain the eigenvalues of this
    # two-dimensional dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor=facecolor, **kwargs)

    # Calculating the standard deviation of x from
    # the squareroot of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    # calculating the standard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)

def data_to_df(folder, delays, bandwidths, qmults, aqms, protocols):
    data=[]
    efficiency_fairness_data = []
    start_time = 0
    end_time = 100
    for aqm in aqms:
        for qmult in qmults:
            for delay in delays:
                for BW in bandwidths:
                    for protocol in protocols:
                        BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * delay * (10 ** -3) / 8)
                        BDP_IN_PKTS = BDP_IN_BYTES / 1500
                        for run in RUNS:
                            PATH = folder + '/%s/Dumbell_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (
                            aqm, BW, delay, int(qmult * BDP_IN_PKTS), 4, protocol, run)
                            flows = []
                            retr_flows = []
                            delay_flows = []
                            for n in range(4):
                                if os.path.exists(PATH + '/csvs/x%s.csv' % (n + 1)):
                                    receiver_total = pd.read_csv(PATH + '/csvs/x%s.csv' % (n + 1)).reset_index(drop=True)
                                    receiver_total = receiver_total[['time', 'bandwidth']]
                                    receiver_total['time'] = receiver_total['time'].apply(lambda x: int(float(x)))

                                    receiver_total = receiver_total[(receiver_total['time'] >= (start_time + n * 25)) & (
                                                receiver_total['time'] <= (end_time + n * 25))]
                                    receiver_total = receiver_total.drop_duplicates('time')
                                    receiver_total = receiver_total.set_index('time')
                                    flows.append(receiver_total)
                                    bandwidth_mean = receiver_total.mean().values[0]
                                    bandwidth_std = receiver_total.std().values[0]
                                else:
                                    print("Folder %s not found" % PATH)
                                    receiver_total = None
                                    bandwidth_mean = None
                                    bandwidth_std = None

                                if protocol != 'aurora':
                                    if os.path.exists(PATH + '/csvs/c%s_probe.csv' % (n + 1)):
                                        # Compute the avg and std rtt across all samples of both flows
                                        sender = pd.read_csv(PATH + '/csvs/c%s_probe.csv' % (n + 1)).reset_index(
                                            drop=True)
                                        sender = sender[['time', 'srtt']]
                                        sender['srtt'] = sender['srtt'] / 1000
                                        sender = sender[(sender['time'] >= (start_time + n * 25)) & (
                                                    sender['time'] <= (end_time + n * 25))]

                                        # We need to resample this data to 1 Hz frequency: Truncate time value to seconds, groupby.mean()
                                        sender['time'] = sender['time'].apply(lambda x: int(x))
                                        sender = sender.groupby('time').mean()
                                        if len(sender) > 0:
                                            delay_flows.append(sender)
                                        delay_mean = sender.mean().values[0]
                                        delay_std = sender.std().values[0]
                                    else:
                                        sender = None
                                        delay_mean = None
                                        delay_std = None

                                    if os.path.exists(PATH + '/sysstat/etcp_c%s.log' % (n + 1)):
                                        systat = pd.read_csv(PATH + '/sysstat/etcp_c%s.log' % (n + 1), sep=';').rename(
                                            columns={"# hostname": "hostname"})
                                        retr = systat[['timestamp', 'retrans/s']]

                                        if n == 0:
                                            start_timestamp = retr['timestamp'].iloc[0]

                                        retr['timestamp'] = retr['timestamp'] - start_timestamp + 1

                                        retr = retr.rename(columns={'timestamp': 'time'})
                                        retr['time'] = retr['time'].apply(lambda x: int(float(x)))
                                        retr = retr[(retr['time'] >= (start_time + n * 25)) & (
                                                    retr['time'] <= (end_time + n * 25))]
                                        retr = retr.drop_duplicates('time')

                                        retr = retr.set_index('time')
                                        retr_flows.append(retr*1500*8/(1024*1024))
                                        retr_mean = retr.mean().values[0]
                                        retr_std = retr.std().values[0]

                                    else:
                                        print("Folder %s not found" % (PATH))
                                        retr = None
                                        retr_mean = None
                                        retr_std = None

                                else:
                                    if os.path.exists(PATH + '/csvs/c%s.csv' % (n + 1)):
                                        sender = pd.read_csv(PATH + '/csvs/c%s.csv' % (n + 1)).reset_index(drop=True)
                                        sender = sender[['time', 'rtt']]
                                        sender = sender.rename(columns={'rtt': 'srtt'})
                                        sender = sender[(sender['time'] >= (start_time + n * 25)) & (
                                                    sender['time'] <= (end_time + n * 25))]
                                        sender['time'] = sender['time'].apply(lambda x: int(x))
                                        sender = sender.drop_duplicates('time')
                                        sender = sender.set_index('time')
                                        if len(sender) > 0:
                                            delay_flows.append(sender)
                                        delay_mean = sender.mean().values[0]
                                        delay_std = sender.std().values[0]
                                    else:
                                        sender = None
                                        delay_mean = None
                                        delay_std = None

                                    if os.path.exists(PATH + '/csvs/c%s.csv' % (n + 1)):
                                        systat = pd.read_csv(PATH + '/csvs/c%s.csv' % (n + 1)).rename(
                                            columns={"retr": "retrans/s"})
                                        retr = systat[['time', 'retrans/s']]
                                        retr['time'] = retr['time'].apply(lambda x: int(float(x)))
                                        retr = retr[
                                            (retr['time'] >= (start_time + n * 25)) & (retr['time'] <= (end_time + n * 25))]
                                        retr = retr.drop_duplicates('time')
                                        retr = retr.set_index('time')
                                        retr_flows.append(retr*1500*8/(1024*1024))
                                        retr_mean = retr.mean().values[0]
                                        retr_std = retr.std().values[0]
                                    else:
                                        retr = None
                                        retr_mean = None
                                        retr_std = None

                                if os.path.exists(PATH + '/sysstat/dev_root.log'):
                                    systat = pd.read_csv(PATH + '/sysstat/dev_root.log', sep=';').rename(
                                        columns={"# hostname": "hostname"})
                                    util = systat[['timestamp', 'IFACE', 'txkB/s', '%ifutil']]

                                    start_timestamp = util['timestamp'].iloc[0]

                                    util['timestamp'] = util['timestamp'] - start_timestamp + 1

                                    util = util.rename(columns={'timestamp': 'time'})
                                    util['time'] = util['time'].apply(lambda x: int(float(x)))
                                    util = util[(util['time'] >= (start_time)) & (util['time'] < (end_time))]
                                    util_if = util[util['IFACE'] == "s2-eth2"]
                                    util_if = util_if[['time', 'txkB/s']]
                                    util_if = util_if.set_index('time')
                                    util_mean = util_if.mean().values[0]*8/1024
                                    util_std = util_if.std().values[0]*8/1024
                                else:
                                    util_mean = None
                                    util_std = None


                                data_point = [aqm, qmult, delay, BW, protocol, run, n, bandwidth_mean, bandwidth_std, delay_mean, delay_std, retr_mean, retr_std, util_mean, util_std]
                                data.append(data_point)

                            if len(flows) > 0:
                                if os.path.exists(PATH + '/sysstat/dev_root.log'):
                                    systat = pd.read_csv(PATH + '/sysstat/dev_root.log', sep=';').rename(
                                        columns={"# hostname": "hostname"})
                                    util = systat[['timestamp', 'IFACE', 'txkB/s', '%ifutil']]

                                    start_timestamp = util['timestamp'].iloc[0]

                                    util['timestamp'] = util['timestamp'] - start_timestamp + 1

                                    util = util.rename(columns={'timestamp': 'time'})
                                    util['time'] = util['time'].apply(lambda x: int(float(x)))
                                    util = util[(util['time'] >= (start_time)) & (util['time'] < (end_time))]
                                    util_if = util[util['IFACE'] == "s2-eth2"]
                                    util_if = util_if[['time', 'txkB/s']]
                                    util_if = util_if.set_index('time')
                                    util_mean = util_if.mean().values[0] * 8 / 1024
                                    util_std = util_if.std().values[0] * 8 / 1024
                                else:
                                    util_mean = None
                                    util_std = None

                                df_merged = reduce(lambda left, right: pd.merge(left, right, on=['time'],
                                                                                how='inner'), flows)
                                df_merged_sum = df_merged.sum(axis=1)
                                df_merged_ratio = df_merged.min(axis=1) / df_merged.max(axis=1)

                                df_retr_merged = reduce(lambda left, right: pd.merge(left, right, on=['time'],
                                                                                     how='inner'), retr_flows)
                                df_retr_merged_sum = df_retr_merged.sum(axis=1)
                                df_delay_merged = reduce(lambda left, right: pd.merge(left, right, on=['time'],
                                                                                     how='inner'), delay_flows)
                                df_delay_merged_mean = df_delay_merged.mean(axis=1)

                                efficiency_metric1 = (df_merged_sum/BW) / (
                                            df_delay_merged_mean / (2 * delay))
                                efficiency_metric2 = (df_merged_sum/BW - df_retr_merged_sum/BW)/(df_delay_merged_mean/(2*delay))

                                efficiency_fairness_data.append([aqm, qmult, delay, BW, protocol, run, df_delay_merged_mean.mean(), df_merged_sum.mean(),df_merged_sum.std(),df_merged_ratio.mean(),df_merged_ratio.std(),df_retr_merged_sum.mean(),df_retr_merged_sum.std(), efficiency_metric1.mean(), efficiency_metric1.std(), efficiency_metric2.mean(), efficiency_metric2.std(), util_mean, util_std])

    COLUMNS1 = ['aqm', 'qmult', 'min_delay', 'bandwidth', 'protocol', 'run', 'flow','goodput_mean', 'goodput_std', 'delay_mean', 'delay_std', 'retr_mean', 'retr_std', 'util_mean', 'util_std']
    COLUMNS2 = ['aqm', 'qmult', 'min_delay', 'bandwidth', 'protocol', 'run', 'delay_mean' ,'efficiency_mean','efficiency_std', 'fairness_mean', 'fairness_std', 'retr_mean', 'retr_std', 'efficiency1_mean', 'efficiency1_std', 'efficiency2_mean', 'efficiency2_std', 'util_mean', 'util_std']

    return pd.DataFrame(data,columns=COLUMNS1), pd.DataFrame(efficiency_fairness_data,columns=COLUMNS2),

def get_aqm_data(aqm, delay, qmult):

    # Fetch per flow goodput
    goodput_data = {'cubic':
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
    for protocol in PROTOCOLS:
        BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * delay * (10 ** -3) / 8)
        BDP_IN_PKTS = BDP_IN_BYTES / 1500
        senders = {1: [], 2: [], 3: [], 4:[]}
        receivers = {1: [], 2: [], 3: [], 4:[]}
        for run in RUNS:
           PATH = ROOT_PATH + '/%s/Dumbell_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (aqm,BW,delay,int(qmult * BDP_IN_PKTS),4,protocol,run)
           for n in range(4):
              if os.path.exists(PATH + '/csvs/c%s.csv' % (n+1)):
                 sender = pd.read_csv(PATH +  '/csvs/c%s.csv' % (n+1))
                 senders[n+1].append(sender)
              else:
                 print("Folder not found")

              if os.path.exists(PATH + '/csvs/x%s.csv' % (n+1)):
                 receiver_total = pd.read_csv(PATH + '/csvs/x%s.csv' % (n+1)).reset_index(drop=True)
                 receiver_total = receiver_total[['time', 'bandwidth']]
                 receiver_total['time'] = receiver_total['time'].apply(lambda x: int(float(x)))
                 # receiver_total['bandwidth'] = receiver_total['bandwidth']

                 receiver_total = receiver_total[(receiver_total['time'] >= (start_time+n*25)) & (receiver_total['time'] <= (end_time+n*25))]
                 receiver_total = receiver_total.drop_duplicates('time')
                 receiver_total = receiver_total.set_index('time')
                 receivers[n+1].append(receiver_total)
              else:
                 print("Folder %s not found" % PATH)

        # For each flow, receivers contains a list of dataframes with a time and bandwidth column. These dataframes SHOULD have
        # exactly the same index. Now I can concatenate and compute mean and std
        for n in range(4):
           goodput_data[protocol][n+1]['mean'] = pd.concat(receivers[n+1], axis=1).mean(axis=1)
           goodput_data[protocol][n+1]['std'] = pd.concat(receivers[n+1], axis=1).std(axis=1)
           goodput_data[protocol][n+1].index = pd.concat(receivers[n+1], axis=1).index

    # Fetch per flow delay
    delay_data = {'cubic':
                        {1: pd.DataFrame([], columns=['time', 'mean', 'std']),
                         2: pd.DataFrame([], columns=['time', 'mean', 'std']),
                         3: pd.DataFrame([], columns=['time', 'mean', 'std']),
                         4: pd.DataFrame([], columns=['time', 'mean', 'std'])},
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
    for protocol in PROTOCOLS:
        BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * delay * (10 ** -3) / 8)
        BDP_IN_PKTS = BDP_IN_BYTES / 1500
        senders = {1: [], 2: [], 3: [], 4: []}
        receivers = {1: [], 2: [], 3: [], 4: []}
        for run in RUNS:
            PATH = ROOT_PATH + '/%s/Dumbell_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (
            aqm, BW, delay, int(qmult * BDP_IN_PKTS), 4, protocol, run)
            for n in range(4):
                if protocol != 'aurora':
                    if os.path.exists(PATH + '/csvs/c%s_probe.csv' % (n+1)) :
                        # Compute the avg and std rtt across all samples of both flows
                        sender = pd.read_csv(PATH + '/csvs/c%s_probe.csv' % (n+1)).reset_index(drop=True)
                        sender = sender[['time', 'srtt']]
                        sender['srtt'] = sender['srtt'] / 1000
                        sender = sender[(sender['time'] >= (start_time + n * 25)) & (sender['time'] <= (end_time + n * 25))]

                        # We need to resample this data to 1 Hz frequency: Truncate time value to seconds, groupby.mean()
                        sender['time'] = sender['time'].apply(lambda x: int(x))
                        sender = sender.groupby('time').mean()

                        # sender = sender.drop_duplicates('time')
                        # sender = sender.set_index('time')
                        senders[n + 1].append(sender)
                else:
                    if os.path.exists(PATH + '/csvs/c%s.csv' % (n+1)) :
                        sender = pd.read_csv(PATH + '/csvs/c%s.csv' % (n+1)).reset_index(drop=True)
                        sender = sender[['time', 'rtt']]
                        sender = sender.rename(columns={'rtt': 'srtt'})
                        sender = sender[(sender['time'] >= (start_time + n * 25)) & (sender['time'] <= (end_time + n * 25))]
                        sender = sender.drop_duplicates('time')
                        sender = sender.set_index('time')
                        senders[n + 1].append(sender)


        # For each flow, receivers contains a list of dataframes with a time and bandwidth column. These dataframes SHOULD have
        # exactly the same index. Now I can concatenate and compute mean and std
        for n in range(4):
            delay_data[protocol][n + 1]['mean'] = pd.concat(senders[n + 1], axis=1).mean(axis=1)
            delay_data[protocol][n + 1]['std'] = pd.concat(senders[n + 1], axis=1).std(axis=1)
            delay_data[protocol][n + 1].index = pd.concat(senders[n + 1], axis=1).index

    # Fetch per flow retransmissions
    retr_data = {'cubic':
                      {1: pd.DataFrame([], columns=['time', 'mean', 'std']),
                       2: pd.DataFrame([], columns=['time', 'mean', 'std']),
                       3: pd.DataFrame([], columns=['time', 'mean', 'std']),
                       4: pd.DataFrame([], columns=['time', 'mean', 'std'])},
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
    for protocol in PROTOCOLS:
        BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * delay * (10 ** -3) / 8)
        BDP_IN_PKTS = BDP_IN_BYTES / 1500
        senders = {1: [], 2: [], 3: [], 4: []}
        receivers = {1: [], 2: [], 3: [], 4: []}
        for run in RUNS:
            PATH = ROOT_PATH + '/%s/Dumbell_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (
                aqm, BW, delay, int(qmult * BDP_IN_PKTS), 4, protocol, run)
            start_timestamp = 0
            for n in range(4):
                if protocol != 'aurora':
                    if os.path.exists(PATH + '/sysstat/etcp_c%s.log' % (n+1)):
                        systat = pd.read_csv(PATH + '/sysstat/etcp_c%s.log' % (n+1), sep=';').rename(
                            columns={"# hostname": "hostname"})
                        retr = systat[['timestamp', 'retrans/s']]

                        if n == 0:
                            start_timestamp =  retr['timestamp'].iloc[0]

                        retr['timestamp'] = retr['timestamp'] - start_timestamp + 1

                        retr = retr.rename(columns={'timestamp': 'time'})
                        retr['time'] = retr['time'].apply(lambda x: int(float(x)))
                        retr = retr[(retr['time'] >= (start_time + n * 25)) & (retr['time'] <= (end_time + n * 25))]
                        retr = retr.drop_duplicates('time')
                        retr = retr.set_index('time')
                        senders[n + 1].append(retr)

                    else:
                        print("Folder %s not found" % (PATH))
                else:
                    if os.path.exists(PATH + '/csvs/c%s.csv' % (n+1)):
                        systat = pd.read_csv(PATH + '/csvs/c%s.csv' % (n+1)).rename(
                            columns={"retr": "retrans/s"})
                        retr = systat[['time', 'retrans/s']]
                        retr['time'] = retr['time'].apply(lambda x: int(float(x)))
                        retr = retr[(retr['time'] >= (start_time + n * 25)) & (retr['time'] <= (end_time + n * 25))]
                        retr = retr.drop_duplicates('time')
                        retr = retr.set_index('time')
                        senders[n + 1].append(retr)


        # For each flow, receivers contains a list of dataframes with a time and bandwidth column. These dataframes SHOULD have
        # exactly the same index. Now I can concatenate and compute mean and std
        for n in range(4):
            retr_data[protocol][n + 1]['mean'] = pd.concat(senders[n + 1], axis=1).mean(axis=1)
            retr_data[protocol][n + 1]['std'] = pd.concat(senders[n + 1], axis=1).std(axis=1)
            retr_data[protocol][n + 1].index = pd.concat(senders[n + 1], axis=1).index


    return goodput_data, delay_data, retr_data


def plot_data(data, filename, ylim=None):
    COLOR = {'cubic': '#0C5DA5',
             'orca': '#00B945',
             'aurora': '#FF9500'}
    LINEWIDTH = 1
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(4, 3), sharex=True, sharey=True)

    for i, protocol in enumerate(PROTOCOLS):
        ax = axes[i]
        for n in range(4):
            ax.plot(data['fifo'][protocol][n + 1].index, data['fifo'][protocol][n + 1]['mean'],
                    linewidth=LINEWIDTH, label=protocol)
            try:
                ax.fill_between(data['fifo'][protocol][n + 1].index,
                                data['fifo'][protocol][n + 1]['mean'] - data['fifo'][protocol][n + 1]['std'],
                                data['fifo'][protocol][n + 1]['mean'] + data['fifo'][protocol][n + 1]['std'],
                                alpha=0.2)
            except:
                print('Protocol: %s' % protocol)
                print(data['fifo'][protocol][n + 1]['mean'])
                print(data['fifo'][protocol][n + 1]['std'])

        if ylim:
            ax.set(ylim=ylim)

        if i == 2:
            ax.set(xlabel='time (s)')
        # ax.set(title='%s' % protocol)
        ax.text(70, 1.8, '%s' % protocol, va='center', c=COLOR[protocol])
        ax.grid()

    # fig.suptitle("%s Mbps, %s RTT, %sxBDP" % (BW, 2*DELAY, QMULTS))

    plt.savefig(filename, dpi=720)



if __name__ == "__main__":
    ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_fairness_aqm"
    PROTOCOLS = ['cubic', 'orca', 'aurora']
    DELAYS = [10,100]
    RUNS = [1, 2, 3, 4, 5]
    QMULTS = [0.2,1,4]

    AQM_LIST = ['fifo', 'codel', 'fq']
    df1,df2 = data_to_df(ROOT_PATH, DELAYS, [100], QMULTS, AQM_LIST, PROTOCOLS)
    df1.to_csv('aqm_data.csv', index=False)
    df2.to_csv('aqm_efficiency_fairness.csv', index=False)
    df = pd.read_csv('../aqm_efficiency_fairness.csv', index_col=None).dropna()
    df = df[df['aqm'] == 'fifo']
    data = df.groupby(['min_delay','qmult','protocol']).mean()


    COLOR_MAP = {'cubic': 'blue',
                 'orca': 'green',
                 'aurora': 'orange'}
    MARKER_MAP = {10: '^',
                 100: '*'}

    for CONTROL_VAR in [0.2,1,4]:

        fig, axes = plt.subplots(figsize=(3,1.5))
        for protocol in PROTOCOLS:
            for delay in DELAYS:
                if not (delay == 100 and protocol == 'aurora' and CONTROL_VAR == 4):
                    axes.scatter(data.loc[delay,CONTROL_VAR, protocol]['delay_mean']/ (delay*2), data.loc[delay,CONTROL_VAR, protocol]['util_mean']/100 - data.loc[delay,CONTROL_VAR, protocol]['retr_mean']/100, edgecolors=COLOR_MAP[protocol], marker=MARKER_MAP[delay], facecolors='none', alpha=0.25)
                    axes.scatter(data.loc[delay,CONTROL_VAR, protocol]['delay_mean']/ (delay*2), data.loc[delay,CONTROL_VAR, protocol]['util_mean']/100, edgecolors=COLOR_MAP[protocol], marker=MARKER_MAP[delay], facecolors='none', label=f'{protocol}-{2*delay}')
                    subset = df[(df['protocol'] == protocol) & (df['qmult'] == CONTROL_VAR)  & (df['min_delay'] == delay)]
                    y = subset['util_mean'].values/100
                    x = subset['delay_mean'].values/(delay*2)

                    confidence_ellipse(x, y, axes, facecolor=COLOR_MAP[protocol], edgecolor='none', alpha=0.25)

        handles, labels = axes.get_legend_handles_labels()
        legend = fig.legend(handles, labels, ncol=3, loc='upper center', bbox_to_anchor=(0.5, 1.2), columnspacing=0.001,
                            handletextpad=0.001)
        axes.set( ylabel="Norm. Throughput", xlabel="Norm. Delay", ylim=[0,1])
        axes.invert_xaxis()
        for format in ['pdf', 'png']:
            plt.savefig(f'{CONTROL_VAR}qmult_scatter1_and_2.{format}', dpi=720)















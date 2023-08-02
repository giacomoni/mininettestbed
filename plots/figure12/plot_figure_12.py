import pandas as pd
import matplotlib.pyplot as plt
import scienceplots
plt.style.use('science')
import os
import matplotlib as mpl
mpl.rcParams['agg.path.chunksize'] = 10000
pd.set_option('display.max_rows', None)
from core.config import *



def get_aqm_data(BW,aqm, delay, qmult):

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
        ax.text(70, 90, '%s' % protocol, va='center', c=COLOR[protocol])
        ax.grid()

    # fig.suptitle("%s Mbps, %s RTT, %sxBDP" % (BW, 2*DELAY, QMULTS))

    plt.savefig(filename, dpi=720)



if __name__ == "__main__":
    ROOT_PATH = "%s/mininettestbed/nooffload/results_fairness_aqm" % HOME_DIR
    PROTOCOLS = ['cubic', 'orca', 'aurora']
    BW = 100
    DELAY = 10
    RUNS = [1, 2, 3, 4, 5]
    QMULTS = [0.2,1,4]
    AQM = 'fifo'
    AQM_LIST = ['fifo', 'fq', 'codel']

    for QMULT in QMULTS:
        goodput_data = {}
        delay_data = {}
        retr_data = {}
        for aqm in AQM_LIST:
            goodput, delay, retr = get_aqm_data(BW,aqm, DELAY, QMULT)
            goodput_data[aqm] = goodput
            delay_data[aqm] = delay
            retr_data[aqm] = retr

        for format in ['pdf', 'png']:
            plot_data(goodput_data, 'aqm_goodput_%smbps_%sms_%smult.%s' % (BW, DELAY, QMULT, format), ylim=[0, 100])
            # plot_data(delay_data, 'aqm_delay_%smbps_%sms_%smult.png' % (BW, DELAY, QMULTS))
            # plot_data(retr_data, 'aqm_retr_%smbps_%sms_%smult.png' % (BW, DELAY, QMULTS))















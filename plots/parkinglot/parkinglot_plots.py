import pandas as pd
import matplotlib.pyplot as plt
import scienceplots
plt.style.use('science')
import os
import matplotlib as mpl
mpl.rcParams['agg.path.chunksize'] = 10000
pd.set_option('display.max_rows', None)

def init_dict(n_flows):
    ret = {}
    for n in range(n_flows):
        ret[n+1] = pd.DataFrame([], columns=['time','mean', 'std'])
    return ret

# def get_starting_times(path, n_flows):
#     starting_times = {}
#     for run in RUNS:
#         PATH = path + '/run%s' % (run)
#         starting_times[run] = {}
#         for n in range(n_flows):
#             if os.path.exists(PATH + '/csvs/x%s.csv' % (n + 1)):
#                 receiver = pd.read_csv(PATH + '/csvs/x%s.csv' % (n + 1)).reset_index(drop=True)
#                 receiver = receiver[['time', 'bandwidth']]
#                 receiver['time'] = receiver['time'].apply(lambda x: int(float(x)))
#                 receiver = receiver.drop_duplicates('time')
#                 starting_times[run][n+1] = receiver['time'].iloc[0]
#             else:
#                 print("Folder %s not found" % PATH)

# Find the latest starting time for the last flow in all runs and use it for the plots of all flows
def get_starting_time(path, n_flows):
    starting_times = []
    for run in RUNS:
        PATH = path + '/run%s' % (run)
        for n in range(n_flows):
            if os.path.exists(PATH + '/csvs/x%s.csv' % (n + 1)):
                receiver = pd.read_csv(PATH + '/csvs/x%s.csv' % (n + 1)).reset_index(drop=True)
                receiver = receiver[['time', 'bandwidth']]
                receiver['time'] = receiver['time'].apply(lambda x: int(float(x)))
                receiver = receiver.drop_duplicates('time')
                starting_times.append(receiver['time'].iloc[0])
            else:
                print("Folder %s not found" % PATH)

    return max(starting_times)

def get_ending_time(path, n_flows):
    starting_times = []
    for run in RUNS:
        PATH = path + '/run%s' % (run)
        for n in range(n_flows):
            if os.path.exists(PATH + '/csvs/x%s.csv' % (n + 1)):
                receiver = pd.read_csv(PATH + '/csvs/x%s.csv' % (n + 1)).reset_index(drop=True)
                receiver = receiver[['time', 'bandwidth']]
                receiver['time'] = receiver['time'].apply(lambda x: int(float(x)))
                receiver = receiver.drop_duplicates('time')
                starting_times.append(receiver['time'].iloc[-1])
            else:
                print("Folder %s not found" % PATH)

    return min(starting_times)

def get_util_data(n_links, column='txkB/s'):

    util_data = {'cubic': init_dict(n_links),
                    'orca': init_dict(n_links),
                    'aurora':init_dict(n_links)
             }
    for protocol in PROTOCOLS:
        BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
        BDP_IN_PKTS = BDP_IN_BYTES / 1500
        links = {}
        for n in range(n_links):
            links[n + 1] = []

        start_time = 0
        end_time = 150

        for run in RUNS:
           PATH = ROOT_PATH + '/fifo/ParkingLot_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (BW,DELAY,int(QMULTS * BDP_IN_PKTS),5,protocol,run)
           if os.path.exists(PATH + '/sysstat/dev_root.log'):
               systat = pd.read_csv(PATH + '/sysstat/dev_root.log', sep=';').rename(
                   columns={"# hostname": "hostname"})
               util = systat[['timestamp', 'IFACE', 'txkB/s', '%ifutil']]

               start_timestamp = util['timestamp'].iloc[0]

               util['timestamp'] = util['timestamp'] - start_timestamp + 1

               util = util.rename(columns={'timestamp': 'time'})
               util['time'] = util['time'].apply(lambda x: int(float(x)))
               util = util[(util['time'] >= (start_time)) & (util['time'] < (end_time))]
               # util = util.drop_duplicates('time')

               for n in range(n_links):
                   util_if = util[util['IFACE'] == "s%s-eth2" % (n+2)]
                   util_if = util_if[['time', column]]
                   util_if = util_if.set_index('time')
                   links[n + 1].append(util_if)

        # For each flow, receivers contains a list of dataframes with a time and bandwidth column. These dataframes SHOULD have
        # exactly the same index. Now I can concatenate and compute mean and std
        for n in range(n_links):
           util_data[protocol][n+1]['mean'] = (pd.concat(links[n+1], axis=1).mean(axis=1)*8)/1024
           util_data[protocol][n+1]['std'] = (pd.concat(links[n+1], axis=1).std(axis=1)*8)/1024
           util_data[protocol][n+1].index = pd.concat(links[n+1], axis=1).index
           util_data[protocol][n + 1] = util_data[protocol][n+1][['mean', 'std']]


    return util_data
def get_flows_data(n_flows):

    # Fetch per flow goodput
    goodput_data = {'cubic': init_dict(n_flows),
                    'orca': init_dict(n_flows),
                    'aurora':init_dict(n_flows)
             }

    for protocol in PROTOCOLS:
        BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
        BDP_IN_PKTS = BDP_IN_BYTES / 1500
        senders = {}
        receivers = {}
        for n in range(n_flows):
            senders[n + 1] = []
            receivers[n + 1] = []
        start_time = get_starting_time(ROOT_PATH + '/fifo/ParkingLot_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s'%(BW,DELAY,int(QMULTS * BDP_IN_PKTS),n_flows,protocol), 5)
        end_time = get_ending_time(ROOT_PATH + '/fifo/ParkingLot_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s'%(BW,DELAY,int(QMULTS * BDP_IN_PKTS),n_flows,protocol), 5)

        for run in RUNS:
           PATH = ROOT_PATH + '/fifo/ParkingLot_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (BW,DELAY,int(QMULTS * BDP_IN_PKTS),n_flows,protocol,run)
           for n in range(n_flows):
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

                 receiver_total = receiver_total[(receiver_total['time'] >= (start_time)) & (receiver_total['time'] <= (end_time))]
                 receiver_total = receiver_total.drop_duplicates('time')
                 receiver_total = receiver_total.set_index('time')
                 receivers[n+1].append(receiver_total)
              else:
                 print("Folder %s not found" % PATH)

        # For each flow, receivers contains a list of dataframes with a time and bandwidth column. These dataframes SHOULD have
        # exactly the same index. Now I can concatenate and compute mean and std
        for n in range(n_flows):
           goodput_data[protocol][n+1]['mean'] = pd.concat(receivers[n+1], axis=1).mean(axis=1)
           goodput_data[protocol][n+1]['std'] = pd.concat(receivers[n+1], axis=1).std(axis=1)
           goodput_data[protocol][n+1].index = pd.concat(receivers[n+1], axis=1).index

    # Fetch per flow delay
    delay_data = {'cubic': init_dict(5),
                    'orca': init_dict(5),
                    'aurora': init_dict(5)
                    }



    for protocol in PROTOCOLS:
        BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
        BDP_IN_PKTS = BDP_IN_BYTES / 1500
        senders = {}
        receivers = {}

        for n in range(n_flows):
            senders[n + 1] = []
            receivers[n + 1] = []

        start_time = get_starting_time(
            ROOT_PATH + '/fifo/ParkingLot_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s' % (
            BW, DELAY, int(QMULTS * BDP_IN_PKTS), n_flows, protocol), 5)
        end_time = get_ending_time(ROOT_PATH + '/fifo/ParkingLot_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s' % (
        BW, DELAY, int(QMULTS * BDP_IN_PKTS), n_flows, protocol), 5)

        for run in RUNS:
            PATH = ROOT_PATH + '/fifo/ParkingLot_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (BW, DELAY, int(QMULTS * BDP_IN_PKTS), n_flows, protocol, run)
            for n in range(n_flows):
                if protocol != 'aurora':
                    if os.path.exists(PATH + '/csvs/c%s_probe.csv' % (n+1)) :
                        # Compute the avg and std rtt across all samples of both flows
                        sender = pd.read_csv(PATH + '/csvs/c%s_probe.csv' % (n+1)).reset_index(drop=True)
                        sender = sender[['time', 'srtt']]
                        sender['srtt'] = sender['srtt'] / 1000
                        sender = sender[(sender['time'] >= (start_time)) & (sender['time'] <= (end_time))]

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
                        sender = sender[(sender['time'] >= (start_time)) & (sender['time'] <= (end_time))]
                        sender = sender.drop_duplicates('time')
                        sender = sender.set_index('time')
                        senders[n + 1].append(sender)


        # For each flow, receivers contains a list of dataframes with a time and bandwidth column. These dataframes SHOULD have
        # exactly the same index. Now I can concatenate and compute mean and std
        for n in range(n_flows):
            delay_data[protocol][n + 1]['mean'] = pd.concat(senders[n + 1], axis=1).mean(axis=1)
            delay_data[protocol][n + 1]['std'] = pd.concat(senders[n + 1], axis=1).std(axis=1)
            delay_data[protocol][n + 1].index = pd.concat(senders[n + 1], axis=1).index

    # Fetch per flow retransmissions
    retr_data = {'cubic': init_dict(5),
                  'orca': init_dict(5),
                  'aurora': init_dict(5)
                  }


    for protocol in PROTOCOLS:
        BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
        BDP_IN_PKTS = BDP_IN_BYTES / 1500
        senders = {}
        receivers = {}
        for n in range(n_flows):
            senders[n + 1] = []
            receivers[n + 1] = []

        start_time = get_starting_time(ROOT_PATH + '/fifo/ParkingLot_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s' % (
        BW, DELAY, int(QMULTS * BDP_IN_PKTS), n_flows, protocol), 5)
        end_time = get_ending_time(ROOT_PATH + '/fifo/ParkingLot_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s' % (
        BW, DELAY, int(QMULTS * BDP_IN_PKTS), n_flows, protocol), 5)

        for run in RUNS:
            PATH = ROOT_PATH + '/fifo/ParkingLot_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (BW, DELAY, int(QMULTS * BDP_IN_PKTS), n_flows, protocol, run)
            start_timestamp = 0
            for n in range(n_flows):
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
                        retr = retr[(retr['time'] >= (start_time)) & (retr['time'] <= (end_time))]
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
                        retr = retr[(retr['time'] >= (start_time)) & (retr['time'] <= (end_time))]
                        retr = retr.drop_duplicates('time')
                        retr = retr.set_index('time')
                        senders[n + 1].append(retr)


        # For each flow, receivers contains a list of dataframes with a time and bandwidth column. These dataframes SHOULD have
        # exactly the same index. Now I can concatenate and compute mean and std
        for n in range(n_flows):
            retr_data[protocol][n + 1]['mean'] = pd.concat(senders[n + 1], axis=1).mean(axis=1)
            retr_data[protocol][n + 1]['std'] = pd.concat(senders[n + 1], axis=1).std(axis=1)
            retr_data[protocol][n + 1].index = pd.concat(senders[n + 1], axis=1).index


    return goodput_data, delay_data, retr_data


def plot_flows_data(data, filename, n_flows, ylim=None):
    LINEWIDTH = 1
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(6,2),sharex=True, sharey=True)

    for i, protocol in enumerate(PROTOCOLS):
        ax = axes[i]
        for n in range(n_flows):
            ax.plot(data[protocol][n + 1].index, data[protocol][n + 1]['mean'],
                    linewidth=LINEWIDTH, label='Flow %s' % (n+1))
            try:
                ax.fill_between(data[protocol][n + 1].index,
                                data[protocol][n + 1]['mean'] - data[protocol][n + 1]['std'],
                                data[protocol][n + 1]['mean'] + data[protocol][n + 1]['std'],
                                alpha=0.2)
            except:
                print('Protocol: %s' % protocol)
                print(data[protocol][n + 1]['mean'])
                print(data[protocol][n + 1]['std'])

        if ylim:
            ax.set(ylim=ylim)

        if i == 1:
            ax.set(xlabel='time (s)')

        ax.set(title='%s' % protocol)
        ax.grid()
        # ax.legend()
        handles, labels = ax.get_legend_handles_labels()


    # fig.suptitle("%s Mbps, %s RTT, %sxBDP" % (BW, 2*DELAY, QMULTS))
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.1), ncol=5)
    fig.tight_layout()
    plt.savefig(filename, dpi=720)

def plot_util_data(data, filename, n_links, ylim=None):
    LINEWIDTH = 1
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(6,2),sharex=True, sharey=True)

    for i, protocol in enumerate(PROTOCOLS):
        ax = axes[i]
        for n in range(n_links):
            ax.plot(data[protocol][n + 1].index, data[protocol][n + 1]['mean'],
                    linewidth=LINEWIDTH, label='Link %s' % (n+1))
            try:
                ax.fill_between(data[protocol][n + 1].index,
                                data[protocol][n + 1]['mean'] - data[protocol][n + 1]['std'],
                                data[protocol][n + 1]['mean'] + data[protocol][n + 1]['std'],
                                alpha=0.2)
            except:
                print('Protocol: %s' % protocol)
                print(data[protocol][n + 1]['mean'])
                print(data[protocol][n + 1]['std'])

        if ylim:
            ax.set(ylim=ylim)

        if i == 1:
            ax.set(xlabel='time (s)')

        ax.set(title='%s' % protocol)
        ax.grid()
        # ax.legend()
        handles, labels = ax.get_legend_handles_labels()



    # fig.suptitle("%s Mbps, %s RTT, %sxBDP" % (BW, 2*DELAY, QMULTS))
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.1), ncol=5)
    fig.tight_layout()
    plt.savefig(filename, dpi=720)

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(3, 1.5))

    for i, protocol in enumerate(PROTOCOLS):
        ax = axes
        x = data[protocol][1].index
        y = (data[protocol][1]['mean'] + data[protocol][2]['mean'])/200
        ax.plot(x,y,
                linewidth=LINEWIDTH, label='%s' % protocol)
        try:
            ax.fill_between(data[protocol][1].index,
                            (data[protocol][1]['mean'] + data[protocol][2]['mean'] - data[protocol][1]['std'] - data[protocol][2]['std'])/200,
                            (data[protocol][1]['mean'] + data[protocol][2]['mean'] + data[protocol][1]['std'] + data[protocol][2]['std'])/200,
                            alpha=0.2)
        except:
            print('Protocol: %s' % protocol)

        if ylim:
            ax.set(ylim=[0,1])

        if i == 1:
            ax.set(xlabel='time (s)')

        ax.set(title='%s' % protocol)
        ax.grid()
        # ax.legend()
        handles, labels = ax.get_legend_handles_labels()

    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.1), ncol=5)
    fig.tight_layout()
    filename = filename.split('.')[0] + '_total.png'
    plt.savefig(filename, dpi=720)


if __name__ == "__main__":
    ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/parkinglot_test"
    PROTOCOLS = ['cubic', 'orca', 'aurora']
    BW = 100
    DELAY = 100
    RUNS = [1, 2, 3, 4, 5]
    QMULTS = 0.2
    N_FLOWS = 5
    N_LINKS = 2
    AQM = 'fifo'

    # goodput, delay, retr = get_flows_data(N_FLOWS)
    #
    # plot_flows_data(goodput, 'parkinglot_goodput_%smbps_%sms_%smult.png' % (BW,DELAY,QMULTS), N_FLOWS,ylim=[0,100])
    # plot_flows_data(delay, 'parkinglot_delay_%smbps_%sms_%smult.png' % (BW, DELAY, QMULTS),N_FLOWS)
    # plot_flows_data(retr, 'parkinglot_retr_%smbps_%sms_%smult.png' % (BW, DELAY, QMULTS),N_FLOWS)

    util = get_util_data(2)


    plot_util_data(util, 'parkinglot_util_mbps_%smbps_%sms_%smult.png' % (BW,DELAY,QMULTS), N_LINKS, ylim=[0,100])


















import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import scienceplots
plt.style.use('science')
import os
from matplotlib.ticker import ScalarFormatter

def get_dynamics(root_path, protocols, bw, delay, qmult, runs, sync, flows):
    goodputs = {'cubic': None, 'orca': None, 'aurora': None}
    losses = {'cubic': None, 'orca': None, 'aurora': None}
    time_start = 0
    time_end = 600 + (flows -1)*100

    for protocol in PROTOCOLS:

        BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
        BDP_IN_PKTS = BDP_IN_BYTES / 1500

        goodputs_runs = {"1": [], "2": [], "3": [], "4": []}
        losses_runs = []

        for run in RUNS:
            PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (
            BW, DELAY, int(QMULT * BDP_IN_PKTS), flows, protocol, run)
            for i in range(flows):
                if os.path.exists(PATH + '/csvs/x%s.csv' % (i+1)):
                    receiver = pd.read_csv(PATH + '/csvs/x%s.csv' % (i+1)).reset_index(drop=True)

                    receiver = receiver[['time', 'bandwidth']]

                    receiver['time'] = receiver['time'].apply(lambda x: int(float(x)))

                    receiver = receiver.drop_duplicates('time')

                    # receiver['bandwidth'] = receiver['bandwidth'].ewm(alpha=0.5).mean()

                    receiver = receiver[(receiver['time'] > time_start) & (receiver['time'] <= time_end)]

                    receiver = receiver.set_index('time')

                    goodputs_runs.append(receiver)

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

                    else:
                        print("Folder %s not found" % (PATH))
                else:
                    if os.path.exists(PATH + '/csvs/c1.csv'):
                        systat1 = pd.read_csv(PATH + '/csvs/c1.csv').rename(
                            columns={"retr": "retrans/s"})
                        retr1 = systat1[['time', 'retrans/s']]
                        systat2 = pd.read_csv(PATH + '/csvs/c1.csv').rename(
                            columns={"retr": "retrans/s"})
                        retr2 = systat2[['time', 'retrans/s']]

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




if __name__ == '__main__':
    ROOT_PATH = "/Volumes/LaCie/mininettestbed/results_fairness_async_final/fifo"
    PROTOCOLS = ['cubic', 'orca', 'aurora']
    BW = 100
    DELAY = 20
    QMULT = 0.2
    RUNS = [1, 2, 3, 4, 5]
    FLOWS = 4
    SYNC = False
    FIGSIZE = (4, 2)
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=FIGSIZE)



    sums, ratios, losses = get_dynamics(ROOT_PATH, PROTOCOLS, BW, DELAY, QMULT, RUNS, SYNC, FLOWS)


import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('science')
import os
import matplotlib
matplotlib.rcParams.update({'font.size': 8})




PROTOCOLS = ['cubic','orca','aurora']
BW = 100
RUNS = [1,2,3]
FLOWS = 3
DELAY = 10
QMULTS = 0.2



# Process and plot the root_cpu file
data = {'cubic': {
                    'mean': pd.DataFrame([], columns=list(range(-1,12))),
                    'std': pd.DataFrame([], columns=list(range(-1,12)))

                },
        'orca': {
                    'mean': pd.DataFrame([], columns=list(range(-1,12))),
                    'std': pd.DataFrame([], columns=list(range(-1,12)))
        },
        'aurora': {
                    'mean': pd.DataFrame([], columns=list(range(-1,12))),
                    'std': pd.DataFrame([], columns=list(range(-1,12)))
        }
}

modes = ['offload', 'no_offload', 'no_offload_routers']
TITLES = {'offload': 'offload', 'no_offload': 'no offload', 'no_offload_routers': 'partial offload'}
start_time = 0
end_time = 900
# Plot throughput over time
fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(6,2.5), sharex=True)
# for cpu in range(-1,12):
for j,mode in enumerate(modes):
    ROOT_PATH = "/Volumes/LaCie/mininettestbed/results_fairness_async_final/fifo" if mode == 'offload' else "/Volumes/LaCie/mininettestbed/results_fairness_async_final_%s/fifo" % mode
    # ax = axes[cpu + 1][j]
    ax = axes[0][j]
    goodput_data = {'cubic':
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
    for protocol in PROTOCOLS:
        BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
        BDP_IN_PKTS = BDP_IN_BYTES / 1500
        cpus_runs = []
        senders = {1: [], 2: [], 3: [], 4: []}
        receivers = {1: [], 2: [], 3: [], 4: []}
        for run in RUNS:
           PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (BW,DELAY,int(QMULTS * BDP_IN_PKTS),FLOWS,protocol,run)
           if os.path.exists(PATH + '/sysstat/root_cpu.log'):
                 root_cpu = pd.read_csv(PATH + '/sysstat/root_cpu.log', sep=';')
                 root_cpu = root_cpu.rename(columns={'timestamp': 'time'})
                 root_cpu['time'] = root_cpu['time'] - root_cpu['time'].iloc[0]+1
                 root_cpu['total'] = root_cpu['%user'] + root_cpu['%nice'] + root_cpu['%system']
                 root_cpu = root_cpu[(root_cpu['time']>start_time) & (root_cpu['time']<end_time)]
                 cpus_grouped = root_cpu.groupby('CPU')

                 # df_all = cpus_grouped.get_group(cpu)
                 df_all = cpus_grouped.get_group(-1)

                 df_all = df_all[['time', 'total']]
                 df_all = df_all.set_index('time')
                 cpus_runs.append(df_all)
           for n in range(FLOWS):
               if os.path.exists(PATH + '/csvs/c%s.csv' % (n + 1)):
                   sender = pd.read_csv(PATH + '/csvs/c%s.csv' % (n + 1))
                   senders[n + 1].append(sender)
               else:
                   print("Folder not found")

               if os.path.exists(PATH + '/csvs/x%s.csv' % (n + 1)):
                   receiver_total = pd.read_csv(PATH + '/csvs/x%s.csv' % (n + 1)).reset_index(drop=True)
                   receiver_total = receiver_total[['time', 'bandwidth']]
                   receiver_total['time'] = receiver_total['time'].apply(lambda x: int(float(x)))
                   receiver_total['bandwidth'] = receiver_total['bandwidth'].ewm(alpha=0.5).mean()

                   receiver_total = receiver_total[(receiver_total['time'] >= (start_time + n * 100)) & (
                               receiver_total['time'] <= (end_time + n * 100))]
                   receiver_total = receiver_total.drop_duplicates('time')
                   receiver_total = receiver_total.set_index('time')
                   receivers[n + 1].append(receiver_total)
               else:
                   print("Folder not found")
        # For each flow, receivers contains a list of dataframes with a time and bandwidth column. These dataframes SHOULD have
        # exactly the same index. Now I can concatenate and compute mean and std
        for n in range(FLOWS):
           goodput_data[protocol][n + 1]['mean'] = pd.concat(receivers[n + 1], axis=1).mean(axis=1)
           goodput_data[protocol][n + 1]['std'] = pd.concat(receivers[n + 1], axis=1).std(axis=1)
           goodput_data[protocol][n + 1].index = pd.concat(receivers[n + 1], axis=1).index

        data = pd.concat(cpus_runs, axis=1)
        avg_data = data.mean(axis=1)
        std_data = data.std(axis=1)
        ax.plot(data.index,avg_data,label=protocol, linewidth=0.5, alpha=0.75)
        ax.fill_between(data.index, avg_data - std_data, avg_data + std_data, alpha=0.2)
        ax.set(title=TITLES[mode],ylim=[0,25])

        if j == 0:
          ax.set(ylabel = '\% CPU')

    for k,protocol in enumerate(PROTOCOLS):
        ax = axes[k+1][j]
        for n in range(FLOWS):
           ax.plot(goodput_data[protocol][n+1].index, goodput_data[protocol][n+1]['mean'], linewidth=0.5, label=protocol)
           # ax.fill_between(data[protocol][n+1].index, data[protocol][n+1]['mean'] - data[protocol][n+1]['std'], data[protocol][n+1]['mean'] + data[protocol][n+1]['std'], alpha=0.2)

        if j == 0:
            ax.set(ylabel=protocol)
        ax.set( ylim=[0,100])
        if k == 2:
            ax.set(xlabel='time (s)')

        ax.grid()

    # ax.legend()
# plt.tight_layout()
plt.savefig("cpu_-1_sumary_and_goodput.png", dpi=720)






import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import scienceplots
plt.style.use('science')
import os
from matplotlib.ticker import ScalarFormatter
import numpy as np
import matplotlib as mpl


def parse_aurora_output(file, offset):
   with open(file, 'r') as fin:
      auroraOutput = fin.read()

   start_index = auroraOutput.find("new connection")
   if start_index == -1:
      start_index = auroraOutput.find("No connection established within")
      if start_index == -1:
         # Client case
         start_index = auroraOutput.find("finished connect")
         if start_index == -1:
            case = "client"
            success = False
         else:
            case = "client"
            success = True

      else:
         case = "server"
         success = False
   else:
      case = "server"
      success = True

   if success:
      auroraOutput = auroraOutput[start_index:]
      auroraOutput = auroraOutput.replace("send/recv: Non-blocking call failure: no buffer available for sending.\n",
                                          "")
      end_index = auroraOutput.find("recv:Connection was broken.")
      if end_index != -1:
         auroraOutput = auroraOutput[:end_index]
      end_index = auroraOutput.find("recv:Non-blocking call failure: no data available for reading")
      if end_index != -1:
         auroraOutput = auroraOutput[:end_index]
      lines = auroraOutput.strip().split("\n")
      lines = [line for line in lines if line.strip() != '']
      lines = lines[1:]  # Remove the first line containing "new connection...."
      columns = lines[0].split(",")

      # Extract the relevant information
      data = [line.split(",") for line in lines[1:]]
      data = data[1:]  # Remove first data point containing uniitialised values

      data = [[float(val) for val in sublist] for sublist in data]
      # Create a pandas DataFrame
      df = pd.DataFrame(data, columns=columns)
      # Convert columns to appropriate types
      df["time"] = df["time"] / 1000000
      df["time"] = df["time"] + offset
   else:
      if case == 'client':
         df = pd.DataFrame([], columns=['time', 'bandwidth', 'rtt', 'sent', 'lost', 'retr'])
      elif case == 'server':
         df = pd.DataFrame([], columns=['time', 'bandwidth'])

   return df
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

ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_fairness_intra_rtt_async/fifo"
PROTOCOLS = ['cubic', 'orca', 'aurora']
BWS = [100]
DELAYS = [10, 20, 30, 40, 50, 60, 70, 80, 100]
QMULTS = [0.2,1,4]
RUNS = [1, 2, 3, 4, 5]
LOSSES=[0]

data = []
for protocol in PROTOCOLS:
  for bw in BWS:
     for delay in DELAYS:
        duration = 2*delay
        start_time = 2*delay
        end_time = 3*delay
        keep_last_seconds = int(0.25*delay)
        for mult in QMULTS:
           BDP_IN_BYTES = int(bw * (2 ** 20) * 2 * delay * (10 ** -3) / 8)
           BDP_IN_PKTS = BDP_IN_BYTES / 1500

           goodput_ratios_20 = []
           goodput_ratios_total = []
           retr_20 = []
           retr_total = []
           retr_ratio_20 = []
           retr_ratio_total = []


           for run in RUNS:
              PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_2flows_22tcpbuf_%s/run%s' % (bw,delay,int(mult * BDP_IN_PKTS),protocol,run)
              if not os.path.exists(PATH + '/csvs/x1.csv'):
                 if os.path.exists(PATH + '/x1_output.txt'):
                    if protocol == 'orca':
                       df = parse_orca_output(PATH + '/x1_output.txt',0)
                       df.to_csv(PATH + '/csvs/x1.csv', index=False)
                    if protocol == 'aurora':
                       df = parse_aurora_output(PATH + '/x1_output.txt', 0)
                       df.to_csv(PATH + '/csvs/x1.csv', index=False)
              if not os.path.exists(PATH + '/csvs/x2.csv'):
                 if os.path.exists(PATH + '/x2_output.txt'):
                    if protocol == 'orca':
                       df = parse_orca_output(PATH + '/x2_output.txt',delay)
                       df.to_csv(PATH + '/csvs/x2.csv', index=False)
                    if protocol == 'aurora':
                       df = parse_aurora_output(PATH + '/x2_output.txt', delay)
                       df.to_csv(PATH + '/csvs/x2.csv', index=False)
              if os.path.exists(PATH + '/csvs/x1.csv') and os.path.exists(PATH + '/csvs/x2.csv'):
                 receiver1_total = pd.read_csv(PATH + '/csvs/x1.csv').reset_index(drop=True)
                 receiver2_total = pd.read_csv(PATH + '/csvs/x2.csv').reset_index(drop=True)

                 receiver1_total['time'] = receiver1_total['time'].apply(lambda x: int(float(x)))
                 receiver2_total['time'] = receiver2_total['time'].apply(lambda x: int(float(x)))


                 receiver1_total = receiver1_total[(receiver1_total['time'] > start_time) & (receiver1_total['time'] < end_time)]
                 receiver2_total = receiver2_total[(receiver2_total['time'] > start_time) & (receiver2_total['time'] < end_time)]

                 receiver1_total = receiver1_total.drop_duplicates('time')
                 receiver2_total = receiver2_total.drop_duplicates('time')

                 receiver1 = receiver1_total[receiver1_total['time'] >= end_time - keep_last_seconds].reset_index(drop=True)
                 receiver2 = receiver2_total[receiver2_total['time'] >= end_time - keep_last_seconds].reset_index(drop=True)

                 receiver1_total = receiver1_total.set_index('time')
                 receiver2_total = receiver2_total.set_index('time')

                 receiver1 = receiver1.set_index('time')
                 receiver2 = receiver2.set_index('time')

                 total = receiver1_total.join(receiver2_total, how='inner', lsuffix='1', rsuffix='2')[['bandwidth1', 'bandwidth2']]
                 partial = receiver1.join(receiver2, how='inner', lsuffix='1', rsuffix='2')[['bandwidth1', 'bandwidth2']]

                 # total = total.dropna()
                 # partial = partial.dropna()

                 goodput_ratios_20.append(partial.min(axis=1)/partial.max(axis=1))
                 goodput_ratios_total.append(total.min(axis=1)/total.max(axis=1))
              else:
                 avg_goodput = None
                 std_goodput = None
                 jain_goodput_20 = None
                 jain_goodput_total = None
                 print("Folder %s not found." % PATH)

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
                    systat2 = pd.read_csv(PATH + '/csvs/c2.csv').rename(
                       columns={"retr": "retrans/s"})
                    retr2 = systat2[['time', 'retrans/s']]


              if len(retr1) > 0 and len(retr2) > 0:

                 retr1['time'] = retr1['time'].apply(lambda x: int(float(x)))
                 retr2['time'] = retr2['time'].apply(lambda x: int(float(x)))

                 retr1 = retr1.drop_duplicates('time')
                 retr2 = retr2.drop_duplicates('time')

                 retr1_total = retr1[(retr1['time'] > start_time) & (retr1['time'] < end_time)]
                 retr2_total = retr2[(retr2['time'] > start_time) & (retr2['time'] < end_time)]



                 retr1 = retr1_total[retr1_total['time'] >= end_time - keep_last_seconds].reset_index(
                    drop=True)
                 retr2 = retr2_total[retr2_total['time'] >= end_time - keep_last_seconds].reset_index(
                    drop=True)

                 retr1_total = retr1_total.set_index('time')
                 retr2_total = retr2_total.set_index('time')

                 retr1 = retr1.set_index('time')
                 retr2 = retr2.set_index('time')

                 total = retr1_total.join(retr2_total, how='inner', lsuffix='1', rsuffix='2')[
                    ['retrans/s1', 'retrans/s2']]
                 partial = retr1.join(retr2, how='inner', lsuffix='1', rsuffix='2')[['retrans/s1', 'retrans/s2']]

                 # total = total.dropna()
                 # partial = partial.dropna()

                 retr_20.append(partial.sum(axis=1))
                 retr_total.append(total.sum(axis=1))
                 retr_ratio_20.append(partial.min(axis=1)/partial.max(axis=1))
                 retr_ratio_total.append(total.min(axis=1)/total.max(axis=1))

           if len(goodput_ratios_20) > 0 and len(goodput_ratios_total) > 0:
              goodput_ratios_20 = np.concatenate(goodput_ratios_20, axis=0)
              goodput_ratios_total = np.concatenate(goodput_ratios_total, axis=0)

           if len(retr_20) > 0:
            retr_20 = np.concatenate(retr_20, axis=0)
           if len(retr_total) > 0:
            retr_total = np.concatenate(retr_total, axis=0)
           if len( retr_ratio_20) > 0:
            retr_ratio_20 = np.concatenate(retr_ratio_20, axis=0)
           if len(retr_ratio_total) > 0:
            retr_ratio_total = np.concatenate(retr_ratio_total, axis=0)

           if len(goodput_ratios_20) > 0 and len(goodput_ratios_total) > 0:
              data_entry = [protocol, bw, delay, delay/10, mult, goodput_ratios_20.mean(), goodput_ratios_20.std(), goodput_ratios_total.mean(), goodput_ratios_total.std(),
                            retr_20.mean(), retr_20.std(), retr_total.mean(), retr_total.std(),  retr_ratio_20.mean(), retr_ratio_20.std(), retr_ratio_total.mean(), retr_ratio_total.std()]
              data.append(data_entry)

summary_data = pd.DataFrame(data,
                           columns=['protocol', 'bandwidth', 'delay', 'delay_ratio','qmult', 'goodput_ratio_20_mean',
                                    'goodput_ratio_20_std', 'goodput_ratio_total_mean', 'goodput_ratio_total_std',
                                    'retr_20_mean', 'retr_20_std', 'retr_total_mean', 'retr_total_std', 'retr_ratio_20_mean',
                                    'retr_ratio_20_std', 'retr_ratio_total_mean', 'retr_ratio_total_std'])

orca_data = summary_data[summary_data['protocol'] == 'orca'].groupby('qmult').mean()
cubic_data = summary_data[summary_data['protocol'] == 'cubic'].groupby('qmult').mean()
aurora_data = summary_data[summary_data['protocol'] == 'aurora'].groupby('qmult').mean()

LINEWIDTH = 1
ELINEWIDTH = 0.75
CAPTHICK = ELINEWIDTH
CAPSIZE= 2

fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(3,1.5))
ax = axes

ind = np.arange(len(cubic_data.index))
width = 0.25

bar1 = ax.bar(ind, cubic_data['retr_20_mean'], width,yerr=cubic_data['retr_20_std'],error_kw={"elinewidth":ELINEWIDTH, "capsize":CAPSIZE, "capthick":CAPTHICK})
# ax.bar(ind, cubic_data['retr_20_mean']*(1-cubic_data['retr_ratio_20_mean']), width, bottom=cubic_data['retr_20_mean']*cubic_data['retr_ratio_20_mean'], color=bar1.patches[0].get_facecolor(),  hatch='...')

bar2 = ax.bar(ind + width, orca_data['retr_20_mean'], width, yerr=orca_data['retr_20_std'],error_kw={"elinewidth":ELINEWIDTH, "capsize":CAPSIZE, "capthick":CAPTHICK})
# ax.bar(ind + width, orca_data['retr_20_mean']*(1-orca_data['retr_ratio_20_mean']), width, bottom=orca_data['retr_20_mean']*orca_data['retr_ratio_20_mean'], color=bar2.patches[0].get_facecolor(),  hatch='...')


bar3 = ax.bar(ind + width * 2, aurora_data['retr_20_mean'], width, yerr=aurora_data['retr_20_std'],error_kw={"elinewidth":ELINEWIDTH, "capsize":CAPSIZE, "capthick":CAPTHICK})
# ax.bar(ind + width * 2, aurora_data['retr_20_mean']*(1-aurora_data['retr_ratio_20_mean']), width, bottom=aurora_data['retr_20_mean']*aurora_data['retr_ratio_20_mean'], color=bar3.patches[0].get_facecolor(),  hatch='...')



ax.set(yscale='linear',xlabel='Buffer size (\%BDP)', ylabel='Retr. Rate  (segments/s)',ylim=[0.1,3000])

ax.set_xticks(ind + width, ['20\%', '100\%', '400\%'])
ax.legend((bar1, bar2, bar3), ('cubic', 'orca', 'aurora'), loc=1)
plt.savefig('retr_async_intra_20_%s.png' % mult, dpi=720)



fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(3,1.5))
ax = axes



ind = np.arange(len(cubic_data.index))
width = 0.25

bar1 = ax.bar(ind, cubic_data['retr_total_mean'], width, yerr=cubic_data['retr_total_std'],error_kw={"elinewidth": ELINEWIDTH, "capsize": CAPSIZE, "capthick": CAPTHICK})
# ax.bar(ind, cubic_data['retr_total_mean']*(1-cubic_data['retr_ratio_total_mean']), width, bottom=cubic_data['retr_total_mean']*cubic_data['retr_ratio_total_mean'], color=bar1.patches[0].get_facecolor(), hatch='...')


bar2 = ax.bar(ind + width, orca_data['retr_total_mean'], width, yerr=orca_data['retr_total_std'],error_kw={"elinewidth": ELINEWIDTH, "capsize": CAPSIZE, "capthick": CAPTHICK})
# ax.bar(ind + width, orca_data['retr_total_mean']*(1-orca_data['retr_ratio_total_mean']), width, bottom=orca_data['retr_total_mean']*orca_data['retr_ratio_total_mean'], color=bar2.patches[0].get_facecolor(),  hatch='...')

bar3 = ax.bar(ind + width * 2, aurora_data['retr_total_mean'], width, yerr=aurora_data['retr_total_std'],error_kw={"elinewidth":ELINEWIDTH, "capsize":CAPSIZE, "capthick":CAPTHICK})
# ax.bar(ind + width * 2, aurora_data['retr_total_mean']*(1-aurora_data['retr_ratio_total_mean']), width, bottom=aurora_data['retr_total_mean']*aurora_data['retr_ratio_total_mean'], color=bar3.patches[0].get_facecolor(),  hatch='...')


ax.set(yscale='linear',xlabel='Buffer size (\%BDP)', ylabel='Avg. Retransmissions/s', ylim=[0.1,3000])

ax.set_xticks(ind + width, ['20\%', '100\%', '400\%'])
ax.legend((bar1, bar2, bar3), ('cubic', 'orca', 'aurora'),loc=1 )

plt.savefig('retr_async_intra_total_%s.png' % mult, dpi=720)
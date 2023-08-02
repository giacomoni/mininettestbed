import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import scienceplots
plt.style.use('science')
import os
from matplotlib.ticker import ScalarFormatter
import numpy as np
from mpl_toolkits.axes_grid1 import ImageGrid
import numpy as np

ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_friendly_intra_rtt_async/fifo"
PROTOCOLS = ['cubic', 'orca', 'aurora']
BWS = [100]
DELAYS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
QMULTS = [0.2,1,4]
RUNS = [1, 2, 3, 4, 5]
LOSSES=[0]

for mult in QMULTS:
   data = []
   for protocol in PROTOCOLS:
     for bw in BWS:
        for delay in DELAYS:
           duration = 2*delay
           start_time = delay
           end_time = 4*delay
           keep_last_seconds = int(0.25*delay)

           BDP_IN_BYTES = int(bw * (2 ** 20) * 2 * delay * (10 ** -3) / 8)
           BDP_IN_PKTS = BDP_IN_BYTES / 1500

           goodput_ratios_20 = []
           goodput_ratios_total = []

           for run in RUNS:
              PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_2flows_22tcpbuf_%s/run%s' % (bw,delay,int(mult * BDP_IN_PKTS),protocol,run)
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

                 # partial['result'] = (1 +partial['bandwidth2'])/(1+ partial['bandwidth1'])
                 # total['result'] =  (1+total['bandwidth2'])/ (1+total['bandwidth1'])

                 partial['result'] = (partial.min(axis=1)+1)/(partial.max(axis=1)+1)
                 total['result'] =  (total.min(axis=1)+1)/ (total.max(axis=1)+1)

                 goodput_ratios_20.append(partial['result'])
                 goodput_ratios_total.append(total['result'])
              else:
                 avg_goodput = None
                 std_goodput = None
                 jain_goodput_20 = None
                 jain_goodput_total = None
                 print("Folder %s not found." % PATH)

           if len(goodput_ratios_20) > 0 and len(goodput_ratios_total) > 0:
              goodput_ratios_20 = np.concatenate(goodput_ratios_20, axis=0)
              goodput_ratios_total = np.concatenate(goodput_ratios_total, axis=0)

              if len(goodput_ratios_20) > 0 and len(goodput_ratios_total) > 0:
                 data_entry = [protocol, bw, delay, delay/10, mult, goodput_ratios_20.mean(), goodput_ratios_20.std(), goodput_ratios_total.mean(), goodput_ratios_total.std()]
                 data.append(data_entry)

   summary_data = pd.DataFrame(data,
                              columns=['protocol', 'bandwidth', 'delay', 'delay_ratio','qmult', 'goodput_ratio_20_mean',
                                       'goodput_ratio_20_std', 'goodput_ratio_total_mean', 'goodput_ratio_total_std'])

   orca_data = summary_data[summary_data['protocol'] == 'orca'].set_index('delay')
   cubic_data = summary_data[summary_data['protocol'] == 'cubic'].set_index('delay')
   aurora_data = summary_data[summary_data['protocol'] == 'aurora'].set_index('delay')

   LINEWIDTH = 0.15
   ELINEWIDTH = 0.75
   CAPTHICK = ELINEWIDTH
   CAPSIZE= 2

   fig, axes = plt.subplots(nrows=1, ncols=1,figsize=(3,1.2))
   ax = axes



   markers, caps, bars = ax.errorbar(cubic_data.index*2, cubic_data['goodput_ratio_20_mean'], yerr=cubic_data['goodput_ratio_20_std'],marker='x',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK, label='cubic')
   [bar.set_alpha(0.5) for bar in bars]
   [cap.set_alpha(0.5) for cap in caps]
   markers, caps, bars = ax.errorbar(orca_data.index*2,orca_data['goodput_ratio_20_mean'], yerr=orca_data['goodput_ratio_20_std'],marker='^',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,label='orca')
   [bar.set_alpha(0.5) for bar in bars]
   [cap.set_alpha(0.5) for cap in caps]
   markers, caps, bars = ax.errorbar(aurora_data.index*2,aurora_data['goodput_ratio_20_mean'], yerr=aurora_data['goodput_ratio_20_std'],marker='+',linewidth=LINEWIDTH, elinewidth=ELINEWIDTH, capsize=CAPSIZE, capthick=CAPTHICK,label='aurora')
   [bar.set_alpha(0.5) for bar in bars]
   [cap.set_alpha(0.5) for cap in caps]

   ax.set(yscale='linear',xlabel='RTT (ms)', ylabel='Goodput Ratio')
   for axis in [ax.xaxis, ax.yaxis]:
       axis.set_major_formatter(ScalarFormatter())
   handles, labels = ax.get_legend_handles_labels()
   # remove the errorbars
   handles = [h[0] for h in handles]

   legend = fig.legend(handles, labels,ncol=3, loc='upper center',bbox_to_anchor=(0.5, 1.08),columnspacing=0.8,handletextpad=0.5)
   # ax.grid()

   for format in ['pdf', 'png']:
      plt.savefig('goodput_ratio_async_friendly_20_%s.%s' % (mult, format), dpi=720)

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


# ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_friendly_intra_rtt_async2/fifo"
# PROTOCOLS = ['orca', 'aurora']
# BW = 100
# RUNS = [1,2,3,4,5]
# DELAYS = [50]
#
# LINEWIDTH = 1
# fig, axes = plt.subplots(nrows=len(DELAYS)+1, ncols=3, figsize=(10, 20))
#
# for FLOWS in [2]:
#    for j,DELAY in enumerate(DELAYS):
#       for QMULTS in [0.2]:
#
#          data = {'cubic':
#                     {1: pd.DataFrame([], columns=['time','mean', 'std']),
#                      2: pd.DataFrame([], columns=['time','mean', 'std']),
#                      3: pd.DataFrame([], columns=['time','mean', 'std']),
#                      4: pd.DataFrame([], columns=['time','mean', 'std'])},
#                  'orca':
#                     {1: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      2: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      3: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      4: pd.DataFrame([], columns=['time', 'mean', 'std'])},
#                  'aurora':
#                     {1: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      2: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      3: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      4: pd.DataFrame([], columns=['time', 'mean', 'std'])}
#                  }
#
#          start_time = DELAY
#          end_time = 4*DELAY
#          # Plot throughput over time
#          for protocol in PROTOCOLS:
#             BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
#             BDP_IN_PKTS = BDP_IN_BYTES / 1500
#             senders = {1: [], 2: [], 3: [], 4:[]}
#             receivers = {1: [], 2: [], 3: [], 4:[]}
#             for run in RUNS:
#                PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (BW,DELAY,int(QMULTS * BDP_IN_PKTS),FLOWS,protocol,run)
#                for n in range(FLOWS):
#                   if not os.path.exists(PATH + '/csvs/c%s.csv' % (n+1)):
#                       try:
#                           if protocol == 'orca':
#                               df = parse_orca_output(PATH + '/x%s_output.txt' % (n+1), 0 if n == 0 else DELAY)
#                               df.to_csv(PATH + '/csvs/x%s.csv' % (n+1), index=False)
#                           if protocol == 'aurora':
#                               df = parse_aurora_output(PATH + '/x%s_output.txt' % (n+1), 0 if n == 0 else DELAY)
#                               df.to_csv(PATH + '/csvs/x%s.csv' % (n+1), index=False)
#                       except:
#                           print("Error parsing")
#                   if os.path.exists(PATH + '/csvs/c%s.csv' % (n+1)):
#                      sender = pd.read_csv(PATH +  '/csvs/c%s.csv' % (n+1))
#                      senders[n+1].append(sender)
#                   else:
#                      print("Folder not found")
#
#                   if os.path.exists(PATH + '/csvs/x%s.csv' % (n+1)):
#                      receiver_total = pd.read_csv(PATH + '/csvs/x%s.csv' % (n+1)).reset_index(drop=True)
#                      receiver_total = receiver_total[['time', 'bandwidth']]
#                      receiver_total['time'] = receiver_total['time'].apply(lambda x: int(float(x)))
#                      receiver_total['bandwidth'] = receiver_total['bandwidth'].ewm(alpha=0.5).mean()
#
#                      receiver_total = receiver_total[(receiver_total['time'] >= (start_time)) & (receiver_total['time'] <= (end_time))]
#                      receiver_total = receiver_total.drop_duplicates('time')
#                      receiver_total = receiver_total.set_index('time')
#                      receivers[n+1].append(receiver_total)
#                   else:
#                      print("Folder not found")
#
#             # For each flow, receivers contains a list of dataframes with a time and bandwidth column. These dataframes SHOULD have
#             # exactly the same index. Now I can concatenate and compute mean and std
#             for n in range(FLOWS):
#                 if len(receivers[n+1]) > 0:
#                    data[protocol][n+1]['mean'] = pd.concat(receivers[n+1], axis=1).mean(axis=1)
#                    data[protocol][n+1]['std'] = pd.concat(receivers[n+1], axis=1).std(axis=1)
#                    data[protocol][n+1].index = pd.concat(receivers[n+1], axis=1).index
#
#
#
#          # fig.subplots_adjust(top=0.8)
#
#          for i,protocol in enumerate(PROTOCOLS):
#             ax = axes[j][i]
#             for n in range(FLOWS):
#                ax.plot(data[protocol][n+1].index, data[protocol][n+1]['mean'], linewidth=LINEWIDTH, label=protocol if n == 1 else 'cubic')
#                try:
#                    ax.fill_between(data[protocol][n+1].index, data[protocol][n+1]['mean'] - data[protocol][n+1]['std'], data[protocol][n+1]['mean'] + data[protocol][n+1]['std'], alpha=0.2)
#                except:
#                    print("Fill between error")
#             if i == 0:
#                 ax.set(ylabel='Goodput (Mbps)')
#             ax.set( ylim=[0,100])
#             if i == 1:
#                 ax.set(xlabel='time (s)')
#
#             ax.set(title='%s - %sms' % (protocol,2*DELAY))
#             ax.legend()
#             ax.grid()
#
#
#          fig.suptitle("%sxBDP" % (QMULTS))
#          plt.savefig('goodput_over_time_%smbps_%sbuf_%s_no_offload_routers.png' % (BW,QMULTS,FLOWS), dpi=720)



#  Plot one RTT per immage
# COLORMAP = {'orca':  '#00B945',
#             'aurora': '#FF9500'}
# LEGENDMAP = {}
# ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_friendly_intra_rtt_async_inverse/fifo"
# PROTOCOLS = ['orca', 'aurora']
# BW = 100
# RUNS = [1,2,3,4,5]
# DELAYS = [50]
#
# LINEWIDTH = 1
# fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(8, 2), sharex=True, sharey=True)
#
# for FLOWS in [2]:
#    for DELAY in DELAYS:
#       for j,QMULTS in enumerate([0.2,1,4]):
#
#          data = {'cubic':
#                     {1: pd.DataFrame([], columns=['time','mean', 'std']),
#                      2: pd.DataFrame([], columns=['time','mean', 'std']),
#                      3: pd.DataFrame([], columns=['time','mean', 'std']),
#                      4: pd.DataFrame([], columns=['time','mean', 'std'])},
#                  'orca':
#                     {1: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      2: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      3: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      4: pd.DataFrame([], columns=['time', 'mean', 'std'])},
#                  'aurora':
#                     {1: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      2: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      3: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      4: pd.DataFrame([], columns=['time', 'mean', 'std'])}
#                  }
#
#          start_time = 0
#          end_time = 4*DELAY -2
#          # Plot throughput over time
#          for protocol in PROTOCOLS:
#             BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
#             BDP_IN_PKTS = BDP_IN_BYTES / 1500
#             senders = {1: [], 2: [], 3: [], 4:[]}
#             receivers = {1: [], 2: [], 3: [], 4:[]}
#             for run in RUNS:
#                PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (BW,DELAY,int(QMULTS * BDP_IN_PKTS),FLOWS,protocol,run)
#                for n in range(FLOWS):
#                   if not os.path.exists(PATH + '/csvs/c%s.csv' % (n+1)):
#                       try:
#                           if protocol == 'orca':
#                               df = parse_orca_output(PATH + '/x%s_output.txt' % (n+1), 0 if n == 0 else DELAY)
#                               df.to_csv(PATH + '/csvs/x%s.csv' % (n+1), index=False)
#                           if protocol == 'aurora':
#                               df = parse_aurora_output(PATH + '/x%s_output.txt' % (n+1), 0 if n == 0 else DELAY)
#                               df.to_csv(PATH + '/csvs/x%s.csv' % (n+1), index=False)
#                       except:
#                           print("Error parsing")
#                   if os.path.exists(PATH + '/csvs/c%s.csv' % (n+1)):
#                      sender = pd.read_csv(PATH +  '/csvs/c%s.csv' % (n+1))
#                      senders[n+1].append(sender)
#                   else:
#                      print("Folder not found")
#
#                   if os.path.exists(PATH + '/csvs/x%s.csv' % (n+1)):
#                      receiver_total = pd.read_csv(PATH + '/csvs/x%s.csv' % (n+1)).reset_index(drop=True)
#                      receiver_total = receiver_total[['time', 'bandwidth']]
#                      receiver_total['time'] = receiver_total['time'].apply(lambda x: int(float(x)))
#                      receiver_total['bandwidth'] = receiver_total['bandwidth'].ewm(alpha=0.5).mean()
#
#                      receiver_total = receiver_total[(receiver_total['time'] >= (start_time)) & (receiver_total['time'] <= (end_time))]
#                      receiver_total = receiver_total.drop_duplicates('time')
#                      receiver_total = receiver_total.set_index('time')
#                      receivers[n+1].append(receiver_total)
#                   else:
#                      print("Folder not found")
#
#             # For each flow, receivers contains a list of dataframes with a time and bandwidth column. These dataframes SHOULD have
#             # exactly the same index. Now I can concatenate and compute mean and std
#             for n in range(FLOWS):
#                 if len(receivers[n+1]) > 0:
#                    data[protocol][n+1]['mean'] = pd.concat(receivers[n+1], axis=1).mean(axis=1)
#                    data[protocol][n+1]['std'] = pd.concat(receivers[n+1], axis=1).std(axis=1)
#                    data[protocol][n+1].index = pd.concat(receivers[n+1], axis=1).index
#
#
#
#          # fig.subplots_adjust(top=0.8)
#
#          for i,protocol in enumerate(PROTOCOLS):
#             ax = axes[i][j]
#             for n in range(FLOWS):
#                ax.plot(data[protocol][n+1].index, data[protocol][n+1]['mean'], linewidth=LINEWIDTH, label=protocol if n == 0 else 'cubic', color='#0C5DA5' if n == 1 else COLORMAP[protocol])
#                try:
#                    ax.fill_between(data[protocol][n+1].index, data[protocol][n+1]['mean'] - data[protocol][n+1]['std'], data[protocol][n+1]['mean'] + data[protocol][n+1]['std'], alpha=0.2,  fc='#0C5DA5' if n == 1 else COLORMAP[protocol])
#                except:
#                    print("Fill between error")
#
#             ax.set( ylim=[0,100])
#
#             if i == 0:
#                ax.set(title="%sxBDP"%QMULTS)
#
#             # ax.legend()
#             ax.grid()
#
#             handles, labels = ax.get_legend_handles_labels()
#             for handle, label in zip(handles, labels):
#                if not LEGENDMAP.get(label,None):
#                   LEGENDMAP[label] = handle
#
#
#          fig.text(0.5, -0.05, 'time (s)', ha='center')
#          fig.text(0.065, 0.5, 'Goodput (Mbps)', va='center', rotation='vertical')
#
#
#          fig.legend(list(LEGENDMAP.values()), list(LEGENDMAP.keys()), loc='lower center',bbox_to_anchor=(0.5, -0.2),ncol=3)
#
#
#
#          plt.savefig('goodput_friendly_%sms_inverse.png' % DELAY , dpi=720)


#
# Use ImageGrid to plot everything together
# fig = plt.figure(figsize=(10,4))
#
# # This Grid will contain Orca Vs Cubic. Top row is cubic first, second row is orca first
# grid1 = ImageGrid(fig, 211,  # similar to subplot(111)
#                  nrows_ncols=(2, 3),  # creates 2x3 grid of axes
#                  aspect=False,
#                  share_all=True,
#                  label_mode="L",
#                  axes_pad=(0.2, 0.1)
#                  # pad between axes in inch.
#                  )
#
#
#
# grid2 = ImageGrid(fig, 212,  # similar to subplot(111)
#                  nrows_ncols=(2, 3),  # creates 2x2 grid of axes
#                  aspect=False,
#                  share_all=True,
#                  label_mode="L",
#                  axes_pad=(0.2,0.1)
#                  # pad between axes in inch.
#                  )
#
#
# COLORMAP = {'orca':  '#00B945',
#             'aurora': '#FF9500'}
# LEGENDMAP = {}
# EXP_TYPE = ['normal', 'inverse']
# PROTOCOLS = ['orca', 'aurora']
# BW = 100
# RUNS = [1,2,3,4,5]
# DELAY = 50
#
# LINEWIDTH = 1
#
# for i,type in enumerate(EXP_TYPE):
#    ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_friendly_intra_rtt_async_inverse/fifo" if type == 'inverse' else "/Volumes/LaCie/mininettestbed/nooffload/results_friendly_intra_rtt_async2/fifo"
#    for j,QMULTS in enumerate([0.2,1,4]):
#       for FLOWS in [2]:
#          data = {'cubic':
#                     {1: pd.DataFrame([], columns=['time','mean', 'std']),
#                      2: pd.DataFrame([], columns=['time','mean', 'std']),
#                      3: pd.DataFrame([], columns=['time','mean', 'std']),
#                      4: pd.DataFrame([], columns=['time','mean', 'std'])},
#                  'orca':
#                     {1: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      2: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      3: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      4: pd.DataFrame([], columns=['time', 'mean', 'std'])},
#                  'aurora':
#                     {1: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      2: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      3: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                      4: pd.DataFrame([], columns=['time', 'mean', 'std'])}
#                  }
#
#          start_time = 0
#          end_time = 4*DELAY -2
#          # Plot throughput over time
#          for protocol in PROTOCOLS:
#             BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
#             BDP_IN_PKTS = BDP_IN_BYTES / 1500
#             senders = {1: [], 2: [], 3: [], 4:[]}
#             receivers = {1: [], 2: [], 3: [], 4:[]}
#             for run in RUNS:
#                PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (BW,DELAY,int(QMULTS * BDP_IN_PKTS),FLOWS,protocol,run)
#                for n in range(FLOWS):
#                   if not os.path.exists(PATH + '/csvs/c%s.csv' % (n+1)):
#                       try:
#                           if protocol == 'orca':
#                               df = parse_orca_output(PATH + '/x%s_output.txt' % (n+1), 0 if n == 0 else DELAY)
#                               df.to_csv(PATH + '/csvs/x%s.csv' % (n+1), index=False)
#                           if protocol == 'aurora':
#                               df = parse_aurora_output(PATH + '/x%s_output.txt' % (n+1), 0 if n == 0 else DELAY)
#                               df.to_csv(PATH + '/csvs/x%s.csv' % (n+1), index=False)
#                       except:
#                           print("Error parsing")
#                   if os.path.exists(PATH + '/csvs/c%s.csv' % (n+1)):
#                      sender = pd.read_csv(PATH +  '/csvs/c%s.csv' % (n+1))
#                      senders[n+1].append(sender)
#                   else:
#                      print("Folder not found")
#
#                   if os.path.exists(PATH + '/csvs/x%s.csv' % (n+1)):
#                      receiver_total = pd.read_csv(PATH + '/csvs/x%s.csv' % (n+1)).reset_index(drop=True)
#                      receiver_total = receiver_total[['time', 'bandwidth']]
#                      receiver_total['time'] = receiver_total['time'].apply(lambda x: int(float(x)))
#                      receiver_total['bandwidth'] = receiver_total['bandwidth'].ewm(alpha=0.5).mean()
#
#                      receiver_total = receiver_total[(receiver_total['time'] >= (start_time)) & (receiver_total['time'] <= (end_time))]
#                      receiver_total = receiver_total.drop_duplicates('time')
#                      receiver_total = receiver_total.set_index('time')
#                      receivers[n+1].append(receiver_total)
#                   else:
#                      print("Folder not found")
#
#             # For each flow, receivers contains a list of dataframes with a time and bandwidth column. These dataframes SHOULD have
#             # exactly the same index. Now I can concatenate and compute mean and std
#             for n in range(FLOWS):
#                 if len(receivers[n+1]) > 0:
#                    data[protocol][n+1]['mean'] = pd.concat(receivers[n+1], axis=1).mean(axis=1)
#                    data[protocol][n+1]['std'] = pd.concat(receivers[n+1], axis=1).std(axis=1)
#                    data[protocol][n+1].index = pd.concat(receivers[n+1], axis=1).index
#
#       for protocol in PROTOCOLS:
#          if protocol == 'orca':
#             ax = grid1[3*i+j]
#          else:
#             ax = grid2[3 * i + j]
#
#          for n in range(FLOWS):
#             if type == 'normal':
#                ax.plot(data[protocol][n+1].index, data[protocol][n+1]['mean'], linewidth=LINEWIDTH, label=protocol if n == 1 else 'cubic', color='#0C5DA5' if n == 0 else COLORMAP[protocol])
#                try:
#                   ax.fill_between(data[protocol][n+1].index, data[protocol][n+1]['mean'] - data[protocol][n+1]['std'], data[protocol][n+1]['mean'] + data[protocol][n+1]['std'], alpha=0.2,  fc='#0C5DA5' if n == 0 else COLORMAP[protocol])
#                except:
#                   print("Fill between error")
#             else:
#                ax.plot(data[protocol][n + 1].index, data[protocol][n + 1]['mean'], linewidth=LINEWIDTH,
#                        label=protocol if n == 0 else 'cubic', color='#0C5DA5' if n == 1 else COLORMAP[protocol])
#                try:
#                   ax.fill_between(data[protocol][n + 1].index,
#                                   data[protocol][n + 1]['mean'] - data[protocol][n + 1]['std'],
#                                   data[protocol][n + 1]['mean'] + data[protocol][n + 1]['std'], alpha=0.2,
#                                   fc='#0C5DA5' if n == 1 else COLORMAP[protocol])
#                except:
#                   print("Fill between error")
#
#          ax.set( ylim=[0,100])
#          if i == 0 and protocol == 'orca':
#             ax.set(title="%sxBDP"%QMULTS)
#
#          ax.grid()
#
#          handles, labels = ax.get_legend_handles_labels()
#          for handle, label in zip(handles, labels):
#             if not LEGENDMAP.get(label,None):
#                LEGENDMAP[label] = handle
#
# fig.text(0.5, 0.04, 'time (s)', ha='center')
# fig.text(0.075, 0.5, 'Goodput (Mbps)', va='center', rotation='vertical')
#
#
# fig.legend(list(LEGENDMAP.values()), list(LEGENDMAP.keys()), loc='lower center',bbox_to_anchor=(0.5, -0.03),ncol=3)
#
# plt.savefig('goodput_friendly_%sms_all.png' % DELAY , dpi=720)

# fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(5,2.5), sharex=True)
#
# COLORMAP = {'orca':  '#00B945',
#             'aurora': '#FF9500'}
# LEGENDMAP = {}
# BW = 100
# DELAY = 50
# QMULT = 4
# PROTOCOLS = ['orca', 'aurora']
# RUNS = [1,2,3,4,5]
#
# LINEWIDTH = 1
#
#
# ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_friendly_intra_rtt_async_inverse/fifo"
# for FLOWS in [2]:
#    data = {'cubic':
#               {1: pd.DataFrame([], columns=['time','mean', 'std']),
#                2: pd.DataFrame([], columns=['time','mean', 'std']),
#                3: pd.DataFrame([], columns=['time','mean', 'std']),
#                4: pd.DataFrame([], columns=['time','mean', 'std'])},
#            'orca':
#               {1: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                2: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                3: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                4: pd.DataFrame([], columns=['time', 'mean', 'std'])},
#            'aurora':
#               {1: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                2: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                3: pd.DataFrame([], columns=['time', 'mean', 'std']),
#                4: pd.DataFrame([], columns=['time', 'mean', 'std'])}
#            }
#
#    start_time = 0
#    end_time = 4*DELAY-2
#    # Plot throughput over time
#    for protocol in PROTOCOLS:
#       BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
#       BDP_IN_PKTS = BDP_IN_BYTES / 1500
#       senders = {1: [], 2: [], 3: [], 4:[]}
#       receivers = {1: [], 2: [], 3: [], 4:[]}
#       for run in RUNS:
#          PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_%sflows_22tcpbuf_%s/run%s' % (BW,DELAY,int(QMULT * BDP_IN_PKTS),FLOWS,protocol,run)
#          for n in range(FLOWS):
#             if not os.path.exists(PATH + '/csvs/c%s.csv' % (n+1)):
#                 try:
#                     if protocol == 'orca':
#                         df = parse_orca_output(PATH + '/x%s_output.txt' % (n+1), 0 if n == 0 else DELAY)
#                         df.to_csv(PATH + '/csvs/x%s.csv' % (n+1), index=False)
#                     if protocol == 'aurora':
#                         df = parse_aurora_output(PATH + '/x%s_output.txt' % (n+1), 0 if n == 0 else DELAY)
#                         df.to_csv(PATH + '/csvs/x%s.csv' % (n+1), index=False)
#                 except:
#                     print("Error parsing")
#             if os.path.exists(PATH + '/csvs/c%s.csv' % (n+1)):
#                sender = pd.read_csv(PATH +  '/csvs/c%s.csv' % (n+1))
#                senders[n+1].append(sender)
#             else:
#                print("Folder not found")
#
#             if os.path.exists(PATH + '/csvs/x%s.csv' % (n+1)):
#                receiver_total = pd.read_csv(PATH + '/csvs/x%s.csv' % (n+1)).reset_index(drop=True)
#                receiver_total = receiver_total[['time', 'bandwidth']]
#                receiver_total['time'] = receiver_total['time'].apply(lambda x: int(float(x)))
#                receiver_total['bandwidth'] = receiver_total['bandwidth'].ewm(alpha=0.5).mean()
#
#                receiver_total = receiver_total[(receiver_total['time'] >= (start_time)) & (receiver_total['time'] <= (end_time))]
#                receiver_total = receiver_total.drop_duplicates('time')
#                receiver_total = receiver_total.set_index('time')
#                receivers[n+1].append(receiver_total)
#             else:
#                print("Folder not found")
#
#       # For each flow, receivers contains a list of dataframes with a time and bandwidth column. These dataframes SHOULD have
#       # exactly the same index. Now I can concatenate and compute mean and std
#       for n in range(FLOWS):
#           if len(receivers[n+1]) > 0:
#              data[protocol][n+1]['mean'] = pd.concat(receivers[n+1], axis=1).mean(axis=1)
#              data[protocol][n+1]['std'] = pd.concat(receivers[n+1], axis=1).std(axis=1)
#              data[protocol][n+1].index = pd.concat(receivers[n+1], axis=1).index
#
# for i,protocol in enumerate(PROTOCOLS):
#    ax = axes[i]
#
#    for n in range(FLOWS):
#       ax.plot(data[protocol][n+1].index, data[protocol][n+1]['mean'], linewidth=LINEWIDTH, label=protocol if n == 0 else 'cubic', color='#0C5DA5' if n == 1 else COLORMAP[protocol])
#       try:
#          ax.fill_between(data[protocol][n+1].index, data[protocol][n+1]['mean'] - data[protocol][n+1]['std'], data[protocol][n+1]['mean'] + data[protocol][n+1]['std'], alpha=0.2,  fc='#0C5DA5' if n == 1 else COLORMAP[protocol])
#       except:
#          print("Fill between error")
#
#
#    ax.set( ylim=[0,100])
#
#    ax.grid()
#
#    handles, labels = ax.get_legend_handles_labels()
#    for handle, label in zip(handles, labels):
#       if not LEGENDMAP.get(label,None):
#          LEGENDMAP[label] = handle
#
# fig.text(0.5, 0.01, 'time (s)', ha='center')
# fig.text(0.045, 0.5, 'Goodput (Mbps)', va='center', rotation='vertical')
#
#
# fig.legend(list(LEGENDMAP.values()), list(LEGENDMAP.keys()), loc='upper center',ncol=3)
#
# plt.savefig('goodput_friendly_%sms_%s_inverse.png' % (DELAY, QMULT), dpi=720)


















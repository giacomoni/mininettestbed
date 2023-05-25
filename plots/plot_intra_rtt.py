import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import scienceplots
plt.style.use('science')
import os
from matplotlib.ticker import ScalarFormatter
import numpy as np

ROOT_PATH = "/home/luca/mininettestbed/results_fairness_async_2/fifo"
PROTOCOLS = ['cubic', 'orca', 'aurora']
BWS = [100]
DELAYS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
QMULTS = [1]
RUNS = [1, 2, 3, 4, 5]
LOSSES=[0]

data = []


flow_duration = 100
keep_last_seconds = 20
start_time=25
end_time=100

for protocol in PROTOCOLS:
  for bw in BWS:
     for delay in DELAYS:
        for mult in QMULTS:

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


                 receiver1_total = receiver1_total[(receiver1_total['time'] > start_time) & (receiver1_total['time'] <= end_time)]
                 receiver2_total = receiver2_total[(receiver2_total['time'] > start_time) & (receiver2_total['time'] <= end_time)]



                 if(len(receiver1_total['bandwidth']) != len(receiver2_total['bandwidth'])):
                     print(receiver1_total['time'])
                     print(receiver2_total['time'])

                 receiver1 = receiver1_total[receiver1_total['time'] >= end_time - keep_last_seconds].reset_index(drop=True)
                 receiver2 = receiver2_total[receiver2_total['time'] >= end_time - keep_last_seconds].reset_index(drop=True)

                 if(len(receiver1['bandwidth']) != len(receiver2['bandwidth'])):
                     print(receiver1['bandwidth'])
                     print(receiver2['bandwidth'])
                 goodput_ratios_20.append(np.minimum(receiver1['bandwidth'].to_numpy(),receiver2['bandwidth'].to_numpy())/np.maximum(receiver1['bandwidth'].to_numpy(),receiver2['bandwidth'].to_numpy()))
                 goodput_ratios_total.append(np.minimum(receiver1_total['bandwidth'].to_numpy(),receiver2_total['bandwidth'].to_numpy())/np.maximum(receiver1_total['bandwidth'].to_numpy(),receiver2_total['bandwidth'].to_numpy()))
              else:
                 avg_goodput = None
                 std_goodput = None
                 jain_goodput_20 = None
                 jain_goodput_total = None

           goodput_ratios_20 = np.concatenate(goodput_ratios_20, axis=0)
           goodput_ratios_total = np.concatenate(goodput_ratios_total, axis=0)

           data_entry = [protocol, bw, delay, mult, goodput_ratios_20.mean(), goodput_ratios_20.std(), goodput_ratios_total.mean(), goodput_ratios_total.std()]
           data.append(data_entry)

summary_data = pd.DataFrame(data,
                           columns=['protocol', 'bandwidth', 'delay', 'qmult', 'goodput_ratio_20_mean',
                                    'goodput_ratio_20_std', 'goodput_ratio_total_mean', 'goodput_ratio_total_std'])

print(summary_data)
# summary_data[['avg_retr', 'std_retr']] = summary_data[['avg_retr', 'std_retr']].fillna(value=0)
# summary_data = summary_data.dropna()
#
# orca_summary_data = summary_data[summary_data['protocol'] == 'orca']
# cubic_summary_data = summary_data[summary_data['protocol'] == 'cubic']
# aurora_summary_data = summary_data[summary_data['protocol'] == 'aurora']
#
# orca_data = orca_summary_data.groupby('delay').mean()
# cubic_data = cubic_summary_data.groupby('delay').mean()
# aurora_data = aurora_summary_data.groupby('delay').mean()
#
# orca_error = orca_summary_data.groupby('delay').std()
# cubic_error = cubic_summary_data.groupby('delay').std()
# aurora_error = aurora_summary_data.groupby('delay').std()

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import scienceplots
plt.style.use('science')
import os
from matplotlib.ticker import ScalarFormatter


def parse_one_flow_data(ROOT_PATH, PROTOCOLS, BWS, DELAYS, QMULTS,LOSSES, RUNS):
   data = []
   flow_duration = 60
   keep_last_seconds = 20

   for protocol in PROTOCOLS:
      for bw in BWS:
         for delay in DELAYS:
            for mult in QMULTS:
               BDP_IN_BYTES = int(bw * (2 ** 20) * 2 * delay * (10 ** -3) / 8)
               BDP_IN_PKTS = BDP_IN_BYTES / 1500
               for loss in LOSSES:
                  for run in RUNS:
                     PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_%sloss_22tcpbuf_%s/run%s' % (bw,delay,int(mult * BDP_IN_PKTS),loss,protocol,run)
                     if os.path.exists(PATH + '/csvs/c1.csv'):
                        sender = pd.read_csv(PATH + '/csvs/c1.csv').tail(keep_last_seconds)

                     if os.path.exists(PATH + '/csvs/x1.csv'):
                        receiver = pd.read_csv(PATH + '/csvs/x1.csv').tail(keep_last_seconds)
                        avg_goodput = receiver['bandwidth'].mean()
                        std_goodput = receiver['bandwidth'].std()
                        efficiency_gdp = avg_goodput / bw
                     else:
                        avg_goodput = None
                        std_goodput = None
                        efficiency_gdp = None

                     if protocol != 'aurora':
                        if os.path.exists(PATH + '/csvs/c1_probe.csv'):
                           sender_rtt = pd.read_csv(PATH + '/csvs/c1_probe.csv')
                           sender_rtt = sender_rtt[sender_rtt['time'] > (flow_duration - keep_last_seconds)]
                           avg_srtt = (sender_rtt['srtt'] / 1000).mean()
                           std_srtt = (sender_rtt['srtt'] / 1000).std()
                           efficiency_rtt = (2 * delay) / avg_srtt

                        else:
                           avg_srtt = None
                           std_srtt = None
                           efficiency_rtt = None
                     else:
                        if os.path.exists(PATH + '/csvs/c1.csv'):
                           sender = pd.read_csv(PATH + '/csvs/c1.csv').tail(keep_last_seconds)
                           avg_srtt = (sender['rtt']).mean()
                           std_srtt = (sender['rtt']).std()
                           efficiency_rtt = (2 * delay) / avg_srtt
                        else:
                           avg_srtt = None
                           std_srtt = None
                           efficiency_rtt = None

                     if os.path.exists(PATH + '/sysstat/dev_root.log'):
                        systat = pd.read_csv(PATH + '/sysstat/dev_root.log', sep=';').rename(
                           columns={"# hostname": "hostname"})
                        s2eth2 = systat[systat['IFACE'] == 's2-eth2'].tail(keep_last_seconds)
                        s2eth2['txMbps'] = s2eth2['txkB/s'] / 1000 * 8

                        s2eth1 = systat[systat['IFACE'] == 's2-eth1'].tail(keep_last_seconds)

                        s2eth1['rxMbps'] = s2eth1['rxkB/s'] / 1000 * 8

                        avg_thr = s2eth2['txMbps'].mean()
                        std_thr = s2eth2['txMbps'].std()
                        efficiency_thr = avg_thr / bw

                        efficiency_q_avg = (s2eth1['rxMbps'].reset_index(drop=True).divide(bw)).mean()
                        efficiency_q_std = (s2eth1['rxMbps'].reset_index(drop=True).divide(bw)).std()

                     else:
                        avg_thr = None
                        std_thr = None
                        efficiency_thr = None
                        efficiency_q_avg = None
                        efficiency_q_std = None

                     if protocol != 'aurora':
                        if os.path.exists(PATH + '/sysstat/etcp_c1.log'):
                           systat = pd.read_csv(PATH + '/sysstat/etcp_c1.log', sep=';').rename(
                              columns={"# hostname": "hostname"})
                           retr = systat['retrans/s'].tail(keep_last_seconds)
                           retr = retr * 1500 * 8 / 100000000
                           avg_retr = retr.mean()
                           std_retr = retr.std()
                        else:
                           avg_retr = None
                           std_retr = None
                     else:
                        if os.path.exists(PATH + '/csvs/c1.csv'):
                           sender = pd.read_csv(PATH + '/csvs/c1.csv').tail(keep_last_seconds)
                           retr = sender['retr']
                           retr = retr * 1500 * 8 / 100000000
                           avg_retr = retr.mean()
                           std_retr = retr.std()

                     data_entry = [protocol, bw, delay, mult, loss, run, avg_thr, avg_goodput, avg_srtt, std_thr, std_goodput,
                                   std_srtt, avg_retr, std_retr, efficiency_thr, efficiency_gdp, efficiency_rtt,
                                   efficiency_q_avg, efficiency_q_std]
                     data.append(data_entry)

   summary_data = pd.DataFrame(data,
                               columns=['protocol', 'bandwidth', 'delay', 'qmult', 'loss', 'run', 'avg_thr', 'avg_goodput',
                                        'avg_srtt', 'std_thr', 'std_goodput', 'std_srtt', 'avg_retr', 'std_retr',
                                        'efficiency_thr', 'efficiency_gdp', 'efficiency_rtt', 'efficiency_q_avg',
                                        'efficiency_q_std'])

   summary_data.to_csv("summary_data.csv", index=None)

def  parse_many_flows_data(ROOT_PATH, PROTOCOLS, BWS, DELAYS, QMULTS, RUNS):

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
               for loss in LOSSES:

                  for run in RUNS:
                     PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_%sloss_2flows_22tcpbuf_%s/run%s' % (bw,delay,int(mult * BDP_IN_PKTS),loss,protocol,run)
                     if os.path.exists(PATH + '/csvs/c1.csv') and os.path.exists(PATH + '/csvs/c2.csv'):
                        sender1 = pd.read_csv(PATH + '/csvs/c1.csv').tail(keep_last_seconds)
                        sender2 = pd.read_csv(PATH + '/csvs/c2.csv').tail(keep_last_seconds)

                     if os.path.exists(PATH + '/csvs/x1.csv') and os.path.exists(PATH + '/csvs/x2.csv'):
                        receiver1_total = pd.read_csv(PATH + '/csvs/x1.csv').reset_index(drop=True)
                        receiver2_total = pd.read_csv(PATH + '/csvs/x2.csv').reset_index(drop=True)
                        receiver1_total['time'] = receiver1_total['time'].apply(lambda x: int(float(x)))
                        receiver2_total['time'] = receiver2_total['time'].apply(lambda x: int(float(x)))

                        receiver1_total = receiver1_total[(receiver1_total['time'] > start_time) & (receiver1_total['time'] < end_time)]
                        receiver2_total = receiver2_total[(receiver2_total['time'] > start_time) & (receiver2_total['time'] < end_time)]



                        receiver1 = receiver1_total[receiver1_total['time'] >= end_time - keep_last_seconds].reset_index(drop=True)
                        receiver2 = receiver2_total[receiver2_total['time'] >= end_time - keep_last_seconds].reset_index(drop=True)
                        avg_goodput = (receiver1['bandwidth'] + receiver2['bandwidth']).mean()
                        std_goodput = (receiver1['bandwidth'] + receiver2['bandwidth']).std()
                        jain_goodput_20 = receiver1['bandwidth'].mean()/receiver2['bandwidth'].mean()
                        jain_goodput_total = receiver1_total['bandwidth'].mean()/receiver2_total[
                           'bandwidth'].mean()

                        efficiency_gdp = avg_goodput / bw
                     else:
                        avg_goodput = None
                        std_goodput = None
                        efficiency_gdp = None
                        jain_goodput_20 = None
                        jain_goodput_total = None

                     if protocol != 'aurora':
                        if os.path.exists(PATH + '/csvs/c1_probe.csv') and os.path.exists(
                                PATH + '/csvs/c2_probe.csv'):
                           sender1_rtt = pd.read_csv(PATH + '/csvs/c1_probe.csv')
                           sender1_rtt = sender1_rtt[
                              sender1_rtt['time'] > (flow_duration - keep_last_seconds)].reset_index(drop=True)
                           sender2_rtt = pd.read_csv(PATH + '/csvs/c2_probe.csv')
                           sender2_rtt = sender2_rtt[
                              sender2_rtt['time'] > (flow_duration - keep_last_seconds)].reset_index(drop=True)
                           if len(sender2_rtt) > len(sender1_rtt):
                              sender2_rtt = sender2_rtt.tail(len(sender1_rtt)).reset_index(drop=True)
                           else:
                              sender1_rtt = sender1_rtt.tail(len(sender2_rtt)).reset_index(drop=True)
                           avg_srtt = ((sender1_rtt['srtt'] + sender2_rtt['srtt']) / (2 * 1000)).mean()
                           std_srtt = ((sender1_rtt['srtt'] + sender2_rtt['srtt']) / (2 * 1000)).std()
                           efficiency_rtt = (2 * delay) / avg_srtt

                        else:
                           avg_srtt = None
                           std_srtt = None
                           efficiency_rtt = None
                     else:
                        if os.path.exists(PATH + '/csvs/c1.csv') and os.path.exists(PATH + '/csvs/c2.csv'):
                           sender1 = pd.read_csv(PATH + '/csvs/c1.csv').tail(keep_last_seconds).reset_index(drop=True)
                           sender2 = pd.read_csv(PATH + '/csvs/c2.csv').tail(keep_last_seconds).reset_index(drop=True)

                           avg_srtt = ((sender1['rtt'] + sender2['rtt']) / 2).mean()
                           std_srtt = ((sender1['rtt'] + sender2['rtt']) / 2).std()
                           efficiency_rtt = (2 * delay) / avg_srtt
                        else:
                           avg_srtt = None
                           std_srtt = None
                           efficiency_rtt = None

                     if os.path.exists(PATH + '/sysstat/dev_root.log'):
                        systat = pd.read_csv(PATH + '/sysstat/dev_root.log', sep=';').rename(
                           columns={"# hostname": "hostname"})
                        s2eth2 = systat[systat['IFACE'] == 's2-eth2'].tail(keep_last_seconds)
                        s2eth2['txMbps'] = s2eth2['txkB/s'] / 1000 * 8

                        s2eth1 = systat[systat['IFACE'] == 's2-eth1'].tail(keep_last_seconds)

                        s2eth1['rxMbps'] = s2eth1['rxkB/s'] / 1000 * 8

                        avg_thr = s2eth2['txMbps'].mean()
                        std_thr = s2eth2['txMbps'].std()
                        efficiency_thr = avg_thr / bw

                        efficiency_q_avg = (s2eth1['rxMbps'].reset_index(drop=True).divide(bw)).mean()
                        efficiency_q_std = (s2eth1['rxMbps'].reset_index(drop=True).divide(bw)).std()

                     else:
                        avg_thr = None
                        std_thr = None
                        efficiency_thr = None
                        efficiency_q_avg = None
                        efficiency_q_std = None

                     if protocol != 'aurora':
                        if os.path.exists(PATH + '/sysstat/etcp_c1.log') and os.path.exists(
                                PATH + '/sysstat/etcp_c2.log'):
                           systat1 = pd.read_csv(PATH + '/sysstat/etcp_c1.log', sep=';').rename(
                              columns={"# hostname": "hostname"})
                           systat2 = pd.read_csv(PATH + '/sysstat/etcp_c2.log', sep=';').rename(
                              columns={"# hostname": "hostname"})

                           retr1 = systat1['retrans/s'].tail(keep_last_seconds)
                           retr1 = retr1 * 1500 * 8 / 100000000

                           retr2 = systat2['retrans/s'].tail(keep_last_seconds)
                           retr2 = retr2 * 1500 * 8 / 100000000

                           avg_retr = (retr1 + retr2).mean()
                           std_retr = (retr1 + retr2).std()
                        else:
                           avg_retr = None
                           std_retr = None
                     else:
                        if os.path.exists(PATH + '/csvs/c1.csv') and os.path.exists(PATH + '/csvs/c2.csv'):
                           sender1 = pd.read_csv(PATH + '/csvs/c1.csv').tail(keep_last_seconds)
                           sender2 = pd.read_csv(PATH + '/csvs/c2.csv').tail(keep_last_seconds)
                           retr1 = sender1['retr']
                           retr1 = retr1 * 1500 * 8 / 100000000
                           retr2 = sender2['retr']
                           retr2 = retr2 * 1500 * 8 / 100000000
                           avg_retr = (retr1 + retr2).mean()
                           std_retr = (retr1 + retr2).std()

                     data_entry = [protocol, bw, delay, mult, loss, run, avg_thr, avg_goodput, avg_srtt, std_thr, std_goodput,
                                   std_srtt, avg_retr, std_retr, efficiency_thr, efficiency_gdp, efficiency_rtt,
                                   efficiency_q_avg, efficiency_q_std, jain_goodput_20, jain_goodput_total]
                     data.append(data_entry)

   summary_data = pd.DataFrame(data,
                               columns=['protocol', 'bandwidth', 'delay', 'qmult','loss', 'run', 'avg_thr', 'avg_goodput',
                                        'avg_srtt', 'std_thr', 'std_goodput', 'std_srtt', 'avg_retr', 'std_retr',
                                        'efficiency_thr', 'efficiency_gdp', 'efficiency_rtt', 'efficiency_q_avg',
                                        'efficiency_q_std', 'jain_goodput_20', 'jain_goodput_total'])

   summary_data.to_csv("summary_data.csv", index=None)

if __name__ == "__main__":
   # ROOT_PATH = "/home/luca/mininettestbed/results_one_flow_loss/fifo"
   # PROTOCOLS = ['cubic', 'orca', 'aurora']
   # BWS = [100]
   # DELAYS = [41]
   # QMULTS = [1]
   # RUNS = [1, 2, 3, 4, 5]
   # LOSSES = [0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.4, 0.6, 0.8, 1, 2, 4]
   #
   ROOT_PATH = "/home/luca/mininettestbed/results_fairness_async_2/fifo"
   PROTOCOLS = ['cubic', 'orca', 'aurora']
   BWS = [100]
   DELAYS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
   QMULTS = [1]
   RUNS = [1, 2, 3, 4, 5]
   LOSSES=[0]



   # parse_one_flow_data(ROOT_PATH, PROTOCOLS, BWS, DELAYS, QMULTS, LOSSES, RUNS)
   parse_many_flows_data(ROOT_PATH, PROTOCOLS, BWS, DELAYS, QMULTS, RUNS)

   summary_data = pd.read_csv("summary_data.csv").dropna()

   orca_summary_data = summary_data[summary_data['protocol'] == 'orca']
   cubic_summary_data = summary_data[summary_data['protocol'] == 'cubic']
   aurora_summary_data = summary_data[summary_data['protocol'] == 'aurora']

   orca_data = orca_summary_data.groupby('delay').mean()
   cubic_data = cubic_summary_data.groupby('delay').mean()
   aurora_data = aurora_summary_data.groupby('delay').mean()

   orca_error = orca_summary_data.groupby('delay').std()
   cubic_error = cubic_summary_data.groupby('delay').std()
   aurora_error = aurora_summary_data.groupby('delay').std()

#    LINEWIDTH = 1
#    YLIM = [0, 100]
#
#    fig, axes = plt.subplots(nrows=1, ncols=1)
#
#    ax = axes
#
#    ax.errorbar(cubic_data.index, cubic_data['avg_goodput'], yerr=cubic_error['avg_goodput'], marker='x',
#                linewidth=LINEWIDTH, label='cubic')
#    ax.errorbar(orca_data.index, orca_data['avg_goodput'], yerr=orca_error['avg_goodput'], marker='^',
#                linewidth=LINEWIDTH, label='orca', linestyle='--')
#    ax.errorbar(aurora_data.index, aurora_data['avg_goodput'], yerr=aurora_error['avg_goodput'], marker='+',
#                linewidth=LINEWIDTH, label='aurora', linestyle='-.')
#    ax.set(ylim=YLIM, xscale='log', xlabel='Loss rate (\%)', ylabel='Goodput (Mbps)')
#    for axis in [ax.xaxis, ax.yaxis]:
#       axis.set_major_formatter(ScalarFormatter())
#
#    ax.legend()
#    ax.grid()
#
#    plt.savefig('goodput_loss.png', dpi=720)
#
#    LINEWIDTH = 1
#
#    fig, axes = plt.subplots(nrows=1, ncols=1)
#    ax = axes
#
#    ax.errorbar(cubic_data.index, cubic_data['avg_thr'], yerr=cubic_error['avg_thr'], marker='x', linewidth=LINEWIDTH,
#                label='cubic')
#    ax.errorbar(orca_data.index, orca_data['avg_thr'], yerr=orca_error['avg_thr'], marker='^', linewidth=LINEWIDTH,
#                label='orca', linestyle='--')
#    ax.errorbar(aurora_data.index, aurora_data['avg_thr'], yerr=aurora_error['avg_thr'], marker='+', linewidth=LINEWIDTH,
#                label='aurora', linestyle='-.')
#    ax.set(xscale='log', xlabel='Loss rate (\%)', ylabel='Link utilisation (\%)')
#    for axis in [ax.xaxis, ax.yaxis]:
#       axis.set_major_formatter(ScalarFormatter())
#    ax.legend()
#    ax.grid()
#
#    plt.savefig('link_util_loss.png', dpi=720)
#
#    LINEWIDTH = 1
#
#    fig, axes = plt.subplots(nrows=1, ncols=1)
#    ax = axes
#
#    ax.errorbar(cubic_data.index, cubic_data['avg_retr'], yerr=cubic_error['avg_retr'], marker='x', linewidth=LINEWIDTH,
#                label='cubic')
#    ax.errorbar(orca_data.index, orca_data['avg_retr'], yerr=orca_error['avg_retr'], marker='^', linewidth=LINEWIDTH,
#                label='orca', linestyle='--')
#    ax.errorbar(aurora_data.index, aurora_data['avg_retr'], yerr=aurora_error['avg_retr'], marker='+',
#                linewidth=LINEWIDTH, label='aurora', linestyle='-.')
#    ax.set(xscale='log', xlabel='Loss rate (\%)', ylabel='Fraction of bandwidth used for retransmissions')
#    for axis in [ax.xaxis, ax.yaxis]:
#       axis.set_major_formatter(ScalarFormatter())
#    ax.legend()
#    ax.grid()
#
#    plt.savefig('norm_retr_rate_lin_scale_loss.png', dpi=720)
#
#    LINEWIDTH = 1
#
#    fig, axes = plt.subplots(nrows=1, ncols=1)
#    ax = axes
#
#    ax.errorbar(cubic_data.index, cubic_data['avg_retr'], yerr=cubic_error['avg_retr'], marker='x', linewidth=LINEWIDTH,
#                label='cubic')
#    ax.errorbar(orca_data.index, orca_data['avg_retr'], yerr=orca_error['avg_retr'], marker='^', linewidth=LINEWIDTH,
#                label='orca', linestyle='--')
#    ax.errorbar(aurora_data.index, aurora_data['avg_retr'], yerr=aurora_error['avg_retr'], marker='+',
#                linewidth=LINEWIDTH, label='aurora', linestyle='-.')
#    ax.set(xscale='log', yscale='log', xlabel='Loss rate (\%)', ylabel='Fraction of bandwidth used for retransmissions')
#    for axis in [ax.xaxis, ax.yaxis]:
#       axis.set_major_formatter(ScalarFormatter())
#    ax.legend()
#    ax.grid()
#
#    plt.savefig('norm_retr_rate_log_scale_loss.png', dpi=720)
#
# LINEWIDTH = 1
#
# fig, axes = plt.subplots(nrows=1, ncols=1)
# ax = axes
#
#
# ax.errorbar(cubic_data.index,cubic_data['avg_srtt'], yerr=cubic_error['avg_srtt'],marker='x',linewidth=LINEWIDTH, label='cubic')
# ax.errorbar(orca_data.index,orca_data['avg_srtt'], yerr=orca_error['avg_srtt'],marker='^',linewidth=LINEWIDTH, label='orca', linestyle='--')
# ax.errorbar(aurora_data.index,aurora_data['avg_srtt'], yerr=aurora_error['avg_srtt'],marker='+',linewidth=LINEWIDTH, label='aurora', linestyle='-.')
# ax.set(xscale='log', xlabel='Loss rate (\%)', ylabel='Avg. RTT (ms)')
#
# for axis in [ax.xaxis, ax.yaxis]:
#     axis.set_major_formatter(ScalarFormatter())
# ax.legend()
# ax.grid()
#
# plt.savefig('avg_rtt_loss.png', dpi=720)


LINEWIDTH = 1

fig, axes = plt.subplots(nrows=1, ncols=1)
ax = axes



ax.errorbar(cubic_data.index, cubic_data['jain_goodput_20'], yerr=cubic_error['jain_goodput_20'],marker='x',linewidth=LINEWIDTH, label='cubic')
ax.errorbar(orca_data.index,orca_data['jain_goodput_20'], yerr=orca_error['jain_goodput_20'],marker='^',linewidth=LINEWIDTH, label='orca', linestyle='--')
ax.errorbar(aurora_data.index,aurora_data['jain_goodput_20'], yerr=aurora_error['jain_goodput_20'],marker='+',linewidth=LINEWIDTH, label='aurora', linestyle='-.')
ax.set(xscale='log',yscale='log',xlabel='Buffer Capacity (xBDP)', ylabel='Goodput Ratio')
for axis in [ax.xaxis, ax.yaxis]:
    axis.set_major_formatter(ScalarFormatter())
ax.legend()
ax.grid()

plt.savefig('jain_friendly_20.png', dpi=720)

LINEWIDTH = 1

fig, axes = plt.subplots(nrows=1, ncols=1)
ax = axes



ax.errorbar(cubic_data.index,cubic_data['jain_goodput_total'], yerr=cubic_error['jain_goodput_total'],marker='x',linewidth=LINEWIDTH, label='cubic')
ax.errorbar(orca_data.index,orca_data['jain_goodput_total'], yerr=orca_error['jain_goodput_total'],marker='^',linewidth=LINEWIDTH, label='orca', linestyle='--')
ax.errorbar(aurora_data.index,aurora_data['jain_goodput_total'], yerr=aurora_error['jain_goodput_total'],marker='+',linewidth=LINEWIDTH, label='aurora', linestyle='-.')
ax.set(xscale='log',yscale='log',xlabel='Buffer Capacity (xBDP)', ylabel='Goodput Ratio')
for axis in [ax.xaxis, ax.yaxis]:
    axis.set_major_formatter(ScalarFormatter())
ax.legend()
ax.grid()

plt.savefig('jain_frindly_total.png', dpi=720)








import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import scienceplots
plt.style.use('science')
import os
from matplotlib.ticker import ScalarFormatter
import matplotlib
import matplotlib.collections as mcol
from matplotlib.legend_handler import HandlerLineCollection, HandlerTuple
from matplotlib.lines import Line2D
import numpy as np
import matplotlib.patches as mpatches



class HandlerDashedLines(HandlerLineCollection):
   """
   Custom Handler for LineCollection instances.
   """

   def create_artists(self, legend, orig_handle,
                      xdescent, ydescent, width, height, fontsize, trans):
      # figure out how many lines there are
      numlines = len(orig_handle.get_segments())
      xdata, xdata_marker = self.get_xdata(legend, xdescent, ydescent,
                                           width, height, fontsize)
      leglines = []
      # divide the vertical space where the lines will go
      # into equal parts based on the number of lines
      ydata = np.full_like(xdata, height / (numlines + 1))
      # for each line, create the line at the proper location
      # and set the dash pattern
      for i in range(numlines):
         legline = Line2D(xdata, ydata * (numlines - i) - ydescent)
         self.update_prop(legline, orig_handle, legend)
         # set color, dash pattern, and linewidth to that
         # of the lines in linecollection
         try:
            color = orig_handle.get_colors()[i]
         except IndexError:
            color = orig_handle.get_colors()[0]
         try:
            dashes = orig_handle.get_dashes()[i]
         except IndexError:
            dashes = orig_handle.get_dashes()[0]
         try:
            lw = orig_handle.get_linewidths()[i]
         except IndexError:
            lw = orig_handle.get_linewidths()[0]
         if dashes[1] is not None:
            legline.set_dashes(dashes[1])
         legline.set_color(color)
         legline.set_transform(trans)
         legline.set_linewidth(lw)
         leglines.append(legline)
      return leglines


def plot_all():
   # Plot congestion window, or sending rate
   ROOT_PATH =  "/Volumes/LaCie/mininettestbed/nooffload/results_fairness_intra_rtt_async/fifo"
   PROTOCOLS = ['cubic', 'orca', 'aurora']
   BW = 100
   DELAY = 40
   QMULT = 4
   RUNS = [ 1,2,3,4,5]
   SCALE = 'linear'

   fig, axes = plt.subplots(nrows=len(RUNS), ncols=3, figsize=(10, 6))

   sending = {'cubic': [], 'orca': [], 'aurora': []}

   for protocol in PROTOCOLS:

     BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
     BDP_IN_PKTS = BDP_IN_BYTES / 1500

     for j,run in enumerate(RUNS):
        series = {'c1': None, 'c2': None}
        PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_2flows_22tcpbuf_%s/run%s' % (
        BW, DELAY, int(QMULT * BDP_IN_PKTS), protocol, run)
        found = False
        if protocol != 'aurora':
           if os.path.exists(PATH + '/csvs/c1_probe.csv') and os.path.exists(PATH + '/csvs/c2_probe.csv'):
              found = True
              sender1 = pd.read_csv(PATH + '/csvs/c1_probe.csv').reset_index(drop=True)
              sender2 = pd.read_csv(PATH + '/csvs/c2_probe.csv').reset_index(drop=True)
              # sender3 = pd.read_csv(PATH + '/csvs/c3_probe.csv').reset_index(drop=True)


              sender1 = sender1[['time', 'cwnd']]
              sender2 = sender2[['time', 'cwnd']]
              # sender3 = sender3[['time', 'cwnd']]

              sender1['time'] = sender1['time'].apply(lambda x: float(x))
              sender2['time'] = sender2['time'].apply(lambda x: float(x))
              # sender3['time'] = sender3['time'].apply(lambda x: float(x))

           else:
               print("Folder %s not found" % (PATH))
        else:
           if os.path.exists(PATH + '/csvs/c1.csv') and os.path.exists(PATH + '/csvs/c2.csv') :
              found=True
              sender1 = pd.read_csv(PATH + '/csvs/c1.csv').reset_index(drop=True)
              sender2 = pd.read_csv(PATH + '/csvs/c2.csv').reset_index(drop=True)
              # sender3 = pd.read_csv(PATH + '/csvs/c3.csv').reset_index(drop=True)


              sender1 = sender1[['time', 'bandwidth']]
              sender2 = sender2[['time', 'bandwidth']]
              # sender3 = sender3[['time', 'bandwidth']]


              sender1['time'] = sender1['time'].apply(lambda x: float(x))
              sender2['time'] = sender2['time'].apply(lambda x: float(x))
              # sender3['time'] = sender3['time'].apply(lambda x: float(x))


              sender1['bandwidth'] = sender1['bandwidth'].ewm(alpha=0.5).mean()
              sender2['bandwidth'] = sender2['bandwidth'].ewm(alpha=0.5).mean()
              # sender3['bandwidth'] = sender3['bandwidth'].ewm(alpha=0.5).mean()

           else:
               print("Folder %s not found" % (PATH))


        if found:
           series['c1'] = sender1
           series['c2'] = sender2
        # series['c3'] = sender3
        else:
              series['c1'] = None
              series['c2'] = None


        sending[protocol].append(series)
   LINEWIDTH = 0.7

   for i, protocol in enumerate(PROTOCOLS):
     for j,run in enumerate(RUNS):
        ax = axes[j][i]
        c1 = sending[protocol][j]['c1']
        c2 = sending[protocol][j]['c2']
        if c1 is not None and c2 is not None:
        # c3 = sending[protocol][j]['c3']


        # c1 = c1[(c1['time'] >= 3*DELAY) & (c1['time'] < 4*DELAY)]
        # c2 = c2[(c2['time'] >= 3 * DELAY) & (c2['time'] < 4 * DELAY)]
        # c3 = c3[(c3['time'] >= 3 * DELAY) & (c3['time'] < 4 * DELAY)]


           x1 = c1['time']
           x2 = c2['time']
           # x3 = c3['time']



           if protocol != 'aurora':
              y1 = c1['cwnd']
              y2 = c2['cwnd']
              # y3 = c3['cwnd']
              if protocol != 'aurora':
                 y1_2 = c1['cwnd'].mean()
                 y2_2 = c2['cwnd'].mean()
                 # y3_2 = c3['cwnd'].mean()

           else:
              y1 = c1['bandwidth']
              y2 = c2['bandwidth']
              # y3 = c3['bandwidth']
           if protocol != 'orca':
              line = ax.plot(x1, y1, linewidth=LINEWIDTH, alpha=0.75)
              line = ax.plot(x2, y2, linewidth=LINEWIDTH, alpha=0.75)
              # line = ax.plot(x3, y3, linewidth=LINEWIDTH, alpha=0.75)
              # line = ax.axhline(y=y1_2 + y2_2,  linestyle='-', alpha=1)

           else:
              line = ax.plot(x1, y1, linewidth=LINEWIDTH, alpha=0.75)
              # line = ax.axhline(y=y1_2, color=line[-1].get_color(), linestyle='-',alpha=1)
              line = ax.plot(x2, y2, linewidth=LINEWIDTH, alpha=0.75)
              # line = ax.axhline(y=y2_2, color=line[-1].get_color(), linestyle='-',alpha=1)
              # line = ax.plot(x3, y3, linewidth=LINEWIDTH, alpha=0.75)
              # line = ax.axhline(y=y1_2+y2_2, linestyle='-',alpha=1)

           if protocol != 'aurora':
              ax.set(ylabel='cwnd (pkts)', yscale=SCALE,ylim=[0,BDP_IN_PKTS+QMULT*BDP_IN_PKTS])
              # ax.axhline(y=BDP_IN_PKTS+int(QMULT*BDP_IN_PKTS), color='r', linestyle='--', alpha=0.5)
              # ax.axhline(y=BDP_IN_PKTS+int(QMULT*BDP_IN_PKTS), color='r', linestyle='--', alpha=0.5)



           else:
              ax.set(ylabel='Send Rate (Mbps)', yscale=SCALE)
              # ax.axhline(y=100, color='r', linestyle='--', alpha=0.5)
              # ax.axhline(y=50, color='r', linestyle='--', alpha=0.5)


           if run == 5:
              ax.set(xlabel='time (s)')
           ax.set_title('%s - Run %s' % (protocol, run))

           # ax.set(xlim=[0,4*DELAY])

           ax.grid()

   plt.tight_layout()
   plt.savefig("cwnd_%s_%s.png" % (DELAY, QMULT), dpi=720)


def plot_one(QMULT, RUN):
   # Plot congestion window, or sending rate
   ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_fairness_intra_rtt_async/fifo"
   BW = 100
   DELAY = 40
   SCALE = 'linear'
   LINEWIDTH = 1
   FIGSIZE = (4, 3)
   COLOR = {'cubic': '#0C5DA5',
            'orca': '#00B945',
            'aurora': '#FF9500'}
   LINESTYLE = 'dashed'
   XLIM = [2*DELAY+DELAY,4*DELAY-1]

   PROTOCOLS = ['cubic', 'orca', 'aurora']

   BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
   BDP_IN_PKTS = BDP_IN_BYTES / 1500

   PROTOCOL_DATA = {'cubic': {'x1': None, 'y1': None,'x2': None, 'y2': None},
                    'orca': {'x1': None, 'y1': None,'x2': None, 'y2': None},
                    'aurora': {'x1': None, 'y1': None,'x2': None, 'y2': None}}
   # Get the data:
   for protocol in PROTOCOLS:
      PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_2flows_22tcpbuf_%s/run%s' % (
         BW, DELAY, int(QMULT * BDP_IN_PKTS), protocol, RUN)
      if protocol != 'aurora':
         if os.path.exists(PATH + '/csvs/c1_probe.csv') and os.path.exists(PATH + '/csvs/c2_probe.csv'):
            sender1 = pd.read_csv(PATH + '/csvs/c1_probe.csv').reset_index(drop=True)
            sender2 = pd.read_csv(PATH + '/csvs/c2_probe.csv').reset_index(drop=True)

            sender1 = sender1[['time', 'cwnd']]
            sender2 = sender2[['time', 'cwnd']]

            sender1['time'] = sender1['time'].apply(lambda x: float(x))
            sender2['time'] = sender2['time'].apply(lambda x: float(x))
         else:
            print("Folder %s not found" % (PATH))
      else:
         if os.path.exists(PATH + '/csvs/c1.csv') and os.path.exists(PATH + '/csvs/c2.csv'):
            sender1 = pd.read_csv(PATH + '/csvs/c1.csv').reset_index(drop=True)
            sender2 = pd.read_csv(PATH + '/csvs/c2.csv').reset_index(drop=True)

            sender1 = sender1[['time', 'bandwidth']]
            sender2 = sender2[['time', 'bandwidth']]

            sender1['time'] = sender1['time'].apply(lambda x: float(x))
            sender2['time'] = sender2['time'].apply(lambda x: float(x))

            sender1['bandwidth'] = sender1['bandwidth'].ewm(alpha=0.5).mean()
            sender2['bandwidth'] = sender2['bandwidth'].ewm(alpha=0.5).mean()
         else:
            print("Folder %s not found" % (PATH))

      c1 = sender1
      c2 = sender2

      c1 = c1[(c1['time'] >= 3 * DELAY) & (c1['time'] < 4 * DELAY)]
      c2 = c2[(c2['time'] >= 3 * DELAY) & (c2['time'] < 4 * DELAY)]

      x1 = c1['time']
      x2 = c2['time']

      if protocol != 'aurora':
         y1 = c1['cwnd']
         y2 = c2['cwnd']
         if protocol != 'aurora':
            y1_2 = c1['cwnd'].mean()
            y2_2 = c2['cwnd'].mean()

      else:
         y1 = c1['bandwidth']
         y2 = c2['bandwidth']

      PROTOCOL_DATA[protocol]['x1'] = x1
      PROTOCOL_DATA[protocol]['x2'] = x2
      PROTOCOL_DATA[protocol]['y1'] = y1
      PROTOCOL_DATA[protocol]['y2'] = y2

   fig, axes = plt.subplots(nrows=3, ncols=1, figsize=FIGSIZE, sharex=True)

   # get the max vlue for ylim
   max_cubic_y = max(PROTOCOL_DATA['cubic']['y1'].max(), PROTOCOL_DATA['cubic']['y2'].max())
   max_orca_y = max(PROTOCOL_DATA['orca']['y1'].max(), PROTOCOL_DATA['orca']['y2'].max())
   max_y = max(max_cubic_y, max_orca_y)

   for i,protocol in enumerate(PROTOCOLS):
      ax = axes[i]
      flow1, = ax.plot(PROTOCOL_DATA[protocol]['x1'], PROTOCOL_DATA[protocol]['y1'], linewidth=LINEWIDTH, alpha=1,color=COLOR[protocol], label=protocol)
      flow2, = ax.plot(PROTOCOL_DATA[protocol]['x2'], PROTOCOL_DATA[protocol]['y2'], linewidth=LINEWIDTH, alpha=0.75,color=COLOR[protocol], linestyle=LINESTYLE)
      ax.set(yscale=SCALE, xlim=XLIM)
      ax.grid()

      if protocol == 'aurora':
         ax.set(ylabel='Rate (Mbps)')
         ax.axhline(50, c='red', linestyle='dashed')
         ax.set(xlabel="time (s)")



      else:
         ax.set(ylabel='cwnd (pkts)')
         ax.set(ylim=[0, max_y])
         redline = ax.axhline(BDP_IN_PKTS/2, c='red', linestyle='dashed')
         # ax.axhline((BDP_IN_PKTS + int(QMULT * BDP_IN_PKTS))/2, c='red', linestyle='dashed')


   # Create Legend
   line = [[(0, 0)]]
   # set up the proxy artist
   linecollections = []
   for protocol in PROTOCOLS:
      styles = ['solid', 'dashed']
      colors = [COLOR[protocol],COLOR[protocol]]
      lc = mcol.LineCollection(2 * line, linestyles=styles, colors=colors)
      linecollections.append(lc)

   linecollections.append(redline)
   PROTOCOLS.append('optimal')
   # fig.legend(linecollections, PROTOCOLS, handler_map={type(lc): HandlerDashedLines()},
   #           handlelength=2, handleheight=1, loc='lower center',bbox_to_anchor=(0.5, -0.1),ncol=4)
   fig.legend(linecollections, PROTOCOLS, handler_map={type(lc): HandlerDashedLines()},
             handlelength=1, handleheight=0.5, ncol=4, columnspacing=0.8,handletextpad=0.5, loc='upper center', bbox_to_anchor=(0.5, 0.98))

   # plt.tight_layout()
   # fig.text(0.017, 0.33/1.3, 'Sending Rate (Mbps)', va='center', rotation='vertical')
   for format in ['png', 'pdf']:
      plt.savefig("sending_%srtt_%sqmult_run%s.%s" % (DELAY*2, QMULT, RUN, format), dpi=720)


def run_number(delay,qmult):
   if delay == 40 and qmult == 1:
      return 3
   elif delay == 40:
      return 2
   else:
      return 1
def plot_single_figure():
   # Plot congestion window, or sending rate
   ROOT_PATH = "/Volumes/LaCie/mininettestbed/nooffload/results_fairness_intra_rtt_async/fifo"
   BW = 100
   DELAYS = [10,40]
   QMULTS = [0.2,1,4]
   SCALE = 'linear'
   LINEWIDTH = 1
   FIGSIZE = (12, 9)
   COLOR = {'cubic': '#0C5DA5',
            'orca': '#00B945',
            'aurora': '#FF9500'}
   LINESTYLE = 'dashed'
   PROTOCOLS = ['cubic', 'orca', 'aurora']



   PROTOCOL_DATA = {'cubic': {'x1': None, 'y1': None,'x2': None, 'y2': None},
                    'orca': {'x1': None, 'y1': None,'x2': None, 'y2': None},
                    'aurora': {'x1': None, 'y1': None,'x2': None, 'y2': None}}
   BUFFER_DATA = {0.2: PROTOCOL_DATA.copy(), 1: PROTOCOL_DATA.copy(), 10: PROTOCOL_DATA.copy()}
   DATA = {10: BUFFER_DATA.copy(), 40: BUFFER_DATA.copy()}


   for QMULT in QMULTS:
      for DELAY in DELAYS:
         BDP_IN_BYTES = int(BW * (2 ** 20) * 2 * DELAY * (10 ** -3) / 8)
         BDP_IN_PKTS = BDP_IN_BYTES / 1500
         RUN = run_number(DELAY, QMULT)
         # Get the data:
         for protocol in PROTOCOLS:
            PATH = ROOT_PATH + '/Dumbell_%smbit_%sms_%spkts_0loss_2flows_22tcpbuf_%s/run%s' % (
               BW, DELAY, int(QMULT * BDP_IN_PKTS), protocol, RUN)
            if protocol != 'aurora':
               if os.path.exists(PATH + '/csvs/c1_probe.csv') and os.path.exists(PATH + '/csvs/c2_probe.csv'):
                  sender1 = pd.read_csv(PATH + '/csvs/c1_probe.csv').reset_index(drop=True)
                  sender2 = pd.read_csv(PATH + '/csvs/c2_probe.csv').reset_index(drop=True)

                  sender1 = sender1[['time', 'cwnd']]
                  sender2 = sender2[['time', 'cwnd']]

                  sender1['time'] = sender1['time'].apply(lambda x: float(x))
                  sender2['time'] = sender2['time'].apply(lambda x: float(x))
               else:
                  print("Folder %s not found" % (PATH))
            else:
               if os.path.exists(PATH + '/csvs/c1.csv') and os.path.exists(PATH + '/csvs/c2.csv'):
                  sender1 = pd.read_csv(PATH + '/csvs/c1.csv').reset_index(drop=True)
                  sender2 = pd.read_csv(PATH + '/csvs/c2.csv').reset_index(drop=True)

                  sender1 = sender1[['time', 'bandwidth']]
                  sender2 = sender2[['time', 'bandwidth']]

                  sender1['time'] = sender1['time'].apply(lambda x: float(x))
                  sender2['time'] = sender2['time'].apply(lambda x: float(x))

                  sender1['bandwidth'] = sender1['bandwidth'].ewm(alpha=0.5).mean()
                  sender2['bandwidth'] = sender2['bandwidth'].ewm(alpha=0.5).mean()
               else:
                  print("Folder %s not found" % (PATH))

            c1 = sender1
            c2 = sender2

            c1 = c1[(c1['time'] >= 3 * DELAY) & (c1['time'] < 4 * DELAY)]
            c2 = c2[(c2['time'] >= 3 * DELAY) & (c2['time'] < 4 * DELAY)]

            x1 = c1['time']
            x2 = c2['time']

            if protocol != 'aurora':
               y1 = c1['cwnd']
               y2 = c2['cwnd']
               if protocol != 'aurora':
                  y1_2 = c1['cwnd'].mean()
                  y2_2 = c2['cwnd'].mean()

            else:
               y1 = c1['bandwidth']
               y2 = c2['bandwidth']

            DATA[DELAY][QMULT][protocol]['x1'] = x1
            DATA[DELAY][QMULT][protocol]['x2'] = x2
            DATA[DELAY][QMULT][protocol]['y1'] = y1
            DATA[DELAY][QMULT][protocol]['y2'] = y2

   fig, axes = plt.subplots(nrows=3, ncols=1, figsize=FIGSIZE, sharex=True)

   XLIM = [2 * DELAY + DELAY, 4 * DELAY - 1]

   # get the max vlue for ylim
   max_cubic_y = max(PROTOCOL_DATA['cubic']['y1'].max(), PROTOCOL_DATA['cubic']['y2'].max())
   max_orca_y = max(PROTOCOL_DATA['orca']['y1'].max(), PROTOCOL_DATA['orca']['y2'].max())
   max_y = max(max_cubic_y, max_orca_y)

   for i,protocol in enumerate(PROTOCOLS):
      ax = axes[i]
      flow1, = ax.plot(PROTOCOL_DATA[protocol]['x1'], PROTOCOL_DATA[protocol]['y1'], linewidth=LINEWIDTH, alpha=1,color=COLOR[protocol], label=protocol)
      flow2, = ax.plot(PROTOCOL_DATA[protocol]['x2'], PROTOCOL_DATA[protocol]['y2'], linewidth=LINEWIDTH, alpha=0.75,color=COLOR[protocol], linestyle=LINESTYLE)
      ax.set(yscale=SCALE, xlim=XLIM)
      ax.grid()

      if protocol == 'aurora':
         ax.set(ylabel='Rate (Mbps)')
         ax.axhline(50, c='red', linestyle='dashed')
         ax.set(xlabel="time (s)")



      else:
         ax.set(ylabel='cwnd (pkts)')
         ax.set(ylim=[0, max_y])
         redline = ax.axhline(BDP_IN_PKTS/2, c='red', linestyle='dashed')
         # ax.axhline((BDP_IN_PKTS + int(QMULT * BDP_IN_PKTS))/2, c='red', linestyle='dashed')


   # Create Legend
   line = [[(0, 0)]]
   # set up the proxy artist
   linecollections = []
   for protocol in PROTOCOLS:
      styles = ['solid', 'dashed']
      colors = [COLOR[protocol],COLOR[protocol]]
      lc = mcol.LineCollection(2 * line, linestyles=styles, colors=colors)
      linecollections.append(lc)

   linecollections.append(redline)
   PROTOCOLS.append('BDP/2')
   fig.legend(linecollections, PROTOCOLS, handler_map={type(lc): HandlerDashedLines()},
             handlelength=2, handleheight=1,ncol=4)

   # plt.tight_layout()
   # fig.text(0.017, 0.33/1.3, 'Sending Rate (Mbps)', va='center', rotation='vertical')
   plt.savefig("sending_%srtt_%sqmult_run%s.png" % (DELAY*2, QMULT, RUN), dpi=720)

if __name__ == "__main__":
   # plot_all()
   for mult,run in zip([0.2,1,4],[2,3,2]):
      plot_one(mult,run)
   # plot_single_figure()
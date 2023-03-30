import json
import pandas as pd
from utils import *
import matplotlib.pyplot as plt

def plot_results(path, cwnd=True, snd_wnd=True, rtt=True, thr=True, qlen=False):
    # Find all clients and servers
    with open(path + '/emulation_info.json') as fin:
        info=json.load(fin)
    flows = info['flows']
    clients = [c for c,s, c_ip, s_ip, t, p in flows]
    servers = [s for c,s, c_ip, s_ip, t, p in flows]
    
    plot_path = path + "/plots"
    mkdirp(plot_path)
    change_all_user_permissions(path)
    
    if thr:
        # Throughput plot
        fig, ax = plt.subplots(1, 1)
        
        for i,server in enumerate(servers):
            results_server = pd.read_csv(path+'/csvs/%s.csv' % server)
            results_client = pd.read_csv(path+'/csvs/%s.csv' % server.replace('x', 'c'))
            line = ax.plot(results_server['time'], results_server['bandwidth'], label='Flow %d - Receiver' % (i+1))
            ax.plot(results_client['time'], results_client['bandwidth'], label='Flow %d - Sender' % (i+1), c=line[-1].get_color(), linestyle='dashed')
        
        ax.set_xlabel('time (s)')
        ax.set_ylabel('Throughput (Mbit/sec)')
        ax.set(yscale='log')
        ax.legend()
        ax.grid()

        plt.savefig("%s/throughput.png" % (plot_path), dpi=720)

    if cwnd:
        # Cwnd plot
        fig, ax = plt.subplots(1, 1)
        
        for i, client in enumerate(clients):
            results_client = pd.read_csv(path+'/csvs/%s_probe.csv' % client)
            line = ax.plot(results_client['time'], results_client['cwnd'], label='Flow %s - cwnd' % (i+1))
            if snd_wnd:
                ax.plot(results_client['time'], results_client['snd_wnd'], label='Flow %s - snd_wnd' % (i+1), c=line[-1].get_color(), linestyle='dashed')
        
        ax.set_xlabel('time (s)')
        ax.set_ylabel('cwnd (pkts)')
        ax.set(yscale='log')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.175),
          ncol=3, fancybox=True, shadow=True)
        ax.grid()

        plt.savefig("%s/cwnd.png" % (plot_path), dpi=720)

    # RTT plot
    if rtt:
        fig, ax = plt.subplots(1, 1)
        
        for i, client in enumerate(clients):
            results_client = pd.read_csv(path+'/csvs/%s_probe.csv' % client)
            line = ax.plot(results_client['time'], results_client['srtt']/1000, label='Flow %s' % (i+1))
            

        ax.set_xlabel('time (s)')
        ax.set_ylabel('srtt (ms)')
        ax.legend()
        ax.grid()

        plt.savefig("%s/srtt.png" % (plot_path), dpi=720)

    # Queues plots
    if qlen:
        LOGS = ['q_s1']
        q_dfs = {}
        for log in LOGS:
            data = pd.read_csv("%s/%s.txt" % (path,log), header=0, names=['time', 'value'])
            q_dfs[log] = data

        initial_values = []
        for key, value in q_dfs.items():
            initial_values.append(value.loc[0, 'time'])

        min_value = min(initial_values)

            
        fig, ax = plt.subplots(1, 1)

        for key, value in q_dfs.items():
            value['time'] = value['time'] - min_value

            ax.plot(value['time'], value['value'], label='%s' % (key))

        ax.set_xlabel('time (s)')
        ax.set_ylabel('Queue size (pkts)')
        ax.legend()
        ax.grid()

        plt.savefig("%s/queues.png" % (path), dpi=720)

        LOGS = ['q_s1.txt.2']
        q_dfs = {}
        for log in LOGS:
            data = pd.read_csv("%s/%s" % (path,log), header=0, names=['time', 'value'])
            q_dfs[log] = data

        initial_values = []
        for key, value in q_dfs.items():
            initial_values.append(value.loc[0, 'time'])

        min_value = min(initial_values)

            
        fig, ax = plt.subplots(1, 1)

        for key, value in q_dfs.items():
            value['time'] = value['time'] - min_value

            ax.plot(value['time'], value['value'], label='%s' % (key))

        ax.set_xlabel('time (s)')
        ax.set_ylabel('Queue size (pkts)')
        ax.legend()
        ax.grid()

        plt.savefig("%s/queues2.png" % (path), dpi=720)



    # uid = int(os.environ.get('SUDO_UID'))
    # gid = int(os.environ.get('SUDO_GID'))

    # os.chown("%s/throughput.png" % (path), uid, gid)
    # os.chown("%s/cwnd.png" % (path), uid, gid)
    # os.chown("%s/rtt.png" % (path), uid, gid)
    # os.chown("%s/queues.png" % (path), uid, gid)
    # os.chown("%s/queues2.png" % (path), uid, gid)
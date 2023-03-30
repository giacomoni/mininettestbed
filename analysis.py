import json
from parsers import *
from utils import *
import pandas as pd

def process_raw_outputs(path):
    with open(path + '/emulation_info.json', 'r') as fin:
        emulation_info = json.load(fin)

    flows = emulation_info['flows']
    flows.sort(key=lambda x: x[-2])

    csv_path = path + "/csvs"
    mkdirp(csv_path)
    change_all_user_permissions(path)

    for flow in flows:
        sender = flow[0]
        receiver = flow[1]
        sender_ip = flow[2]
        receiver_ip = flow[3]

        if flow[-1] == 'cubic':
            port=5201

            # Convert sender output into csv
            df = parse_iperf_json(path+"/%s_output.txt" % sender, flow[-2])
            df.to_csv("%s/%s.csv" % (csv_path,sender), index=False)

            # Convert receiver output into csv
            df = parse_iperf_json(path+"/%s_output.txt" % receiver, flow[-2])
            df.to_csv("%s/%s.csv" % (csv_path, receiver), index=False)
            print("Address for probe is: %s:%s" % (receiver_ip, port))
            probe_df = parse_tcp_probe_output(path + "/tcp_probe.txt", '%s:%s' % (receiver_ip, port), key='destination')
            probe_df.to_csv("%s/%s_probe.csv" % (csv_path, sender),index=False)

        elif flow[-1] == 'orca':
            port=4444
            # Convert sender output into csv
            df = parse_orca_output(path+"/%s_output.txt" % sender, flow[-2])
            df.to_csv("%s/%s.csv" %  (csv_path, sender), index=False)

            # Convert receiver output into csv
            df = parse_orca_output(path+"/%s_output.txt" % receiver, flow[-2])
            df.to_csv("%s/%s.csv" %  (csv_path, receiver),index=False)


            probe_df = parse_tcp_probe_output(path + "/tcp_probe.txt", '%s:%s' % (sender_ip, port),  key='source')
            probe_df.to_csv("%s/%s_probe.csv" % (csv_path, sender),index=False)


if __name__ == "__main__":
    method = 1
    bw = 10
    DELAYS = [10, 100]
    RUNS = [1]
    QMULTS = [1,2]
    METHODS = [6]
    COLUMNS = ['max_srtt', 'max_cwnd', 'max_thr' ,'max_qsize_root', 'max_qsize_child' ,'bdp', 'buffer', 'rate', 'delay']


    for method in METHODS:
        df_mean = pd.DataFrame([], columns=COLUMNS)
        df_std = pd.DataFrame([], columns=COLUMNS)
        for delay in DELAYS:
            for qmult in QMULTS:
                bdp_in_bytes = int(bw*(2**20)*2*delay*(10**-3)/8) 
                qsize_in_bytes = qmult * bdp_in_bytes
                runs = pd.DataFrame([], columns=COLUMNS)
                for run in RUNS:
                    path = "/home/luca/mininetproject/method%s/Dumbell_%smbit_%sms_%spkts_%stcpbuf_%s/run%s" % (method,bw,delay, int(qsize_in_bytes/1500), 0, 'cubic', run)
                    #  Get max srtt of first flow
                    max_srtt = pd.read_csv(path+"/csvs/c1_probe.csv", index_col = False)['srtt'].max()/1000
                    max_cwnd = pd.read_csv(path+"/csvs/c1_probe.csv", index_col = False)['cwnd'].max()
                    max_qsize = pd.read_csv(path+"/queues/s2-eth2.txt", index_col = False)['root_pkts'].max()
                    if method == 4 or method == 5:
                        max_qsize_child = pd.read_csv(path+"/queues/s2-eth2.txt", index_col = False)['child_pkts'].max()
                    else:
                        max_qsize_child = 0
                    max_thr = pd.read_csv(path+"/csvs/x1.csv", index_col = False)['bandwidth'].rolling(5).mean().max()
                    bdp = int(bdp_in_bytes/1500)
                    buffer = qmult
                    rate = bw

                    entry = [max_srtt, max_cwnd, max_thr, max_qsize,max_qsize_child, bdp, buffer, rate, delay]

                    runs = pd.concat([runs, pd.DataFrame([entry], columns=COLUMNS)])
                   
        
                df_mean = pd.concat([df_mean, runs.mean().to_frame().T])
                df_std = pd.concat([df_std,  runs.std().to_frame().T])

        df_mean.to_csv("/home/luca/mininetproject/method%s/mean.csv" % (method))
        df_std.to_csv("/home/luca/mininetproject/method%s/std.csv" % (method))

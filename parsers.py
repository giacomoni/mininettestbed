import re
import pandas as pd
import json

def parse_tc_show_output(output):
    '''
    Parse tc show dev output. Assumes that dev can only have one netem and/or one tbf. 
    Returns a dict where key is type of qdisc and value is another dict with dropped, bytes queues and pkts queued.
    '''
    ret = {}
    input_string = output.split('\n')
    for index,line in enumerate(input_string):
        if "netem" in line or "tbf" in line:
            if "netem" in line:
                qdisc_type = 'netem'
                # Get number of dropped pkts from this qdisc
            elif "tbf" in line:
                qdisc_type = 'tbf'


            dropped = 0
            bytes_queued = 0
            packets_queued = 0

            pattern = re.compile(r'.*\(dropped (\d+),')    
            
            matches = pattern.findall(input_string[index+1])
            if matches:
                dropped = int(matches[0][0])

            pattern = re.compile(r'.*backlog\s+(\d+)b\s+(\d+)p')    
            matches = pattern.findall(input_string[index+2])
            
            if matches:
                bytes_queued = int(matches[0][0])
                packets_queued = int(matches[0][1])
            
            ret[qdisc_type] = {'dropped': dropped, 'bytes': bytes_queued, 'pkts': packets_queued}
    
    return ret

def parse_tcp_probe_output(file, address, key='source'):
    # Define the column names for the DataFrame
    columns = ['time', 'source', 'destination', 'packet_length', 'sequence_number', 'ack_number', 'cwnd', 'ssthresh', 'snd_wnd' ,'srtt', 'rcv_wnd']

    # Read the tcp_probe output file into a list of lines
    with open(file, 'r') as f:
        lines = f.readlines()


    # Split each line by whitespace and create a list of lists
    data = [line.strip().split() for line in lines]

    # Convert the list of lists into a pandas DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Convert the data types of the columns as needed
    df['time'] = df['time'].astype(float)
    df['sequence_number'] = df['sequence_number'].apply(lambda x: int(x,0))
    df['ack_number'] = df['ack_number'].apply(lambda x: int(x,0))
    df['cwnd'] = df['cwnd'].astype(int)
    df['ssthresh'] = df['ssthresh'].astype(int)
    df['snd_wnd'] = df['snd_wnd'].astype(int)
    df['srtt'] = df['srtt'].astype(float)
    df['rcv_wnd'] = df['rcv_wnd'].astype(int)
       
    return df[df[key] == address][['time','cwnd','sequence_number','ssthresh','snd_wnd','srtt']].copy()
    

def parse_iperf_output(output):
    """Parse iperf output and return bandwidth.
    iperfOutput: string
    returns: result string"""
    
    r_client =  r"\[\s*(\d+)\]\s+(\d+\.?\d*-\d+\.?\d*)\s+sec\s+(\d+\.?\d*\s+[KMG]?Bytes)\s+(\d+\.?\d*\s+[KMG]?bits/sec)\s+(\d+)\s+(\d+\.?\d*\s+[KMG]?Bytes)"
    values_client = re.findall(r_client, iperfOutput )
    
    r_server =  r"\[\s*(\d+)\]\s+(\d+\.?\d*-\d+\.?\d*)\s+sec\s+(\d+\.?\d*\s+[KMG]?Bytes)\s+(\d+\.?\d*\s+[KMG]?bits/sec)"
    values_server = re.findall(r_server, iperfOutput )

    if len(values_client) > 2:
        if mode == 'last':
            # TODO:
            return values_client[-1]
        elif mode == 'series':
            ids = []
            time = []
            transferred = []
            bandwidth = []
            retr = []
            cwnd = []
            for x in values_client:
                ids.append(x[0])
                time.append(float(x[1].split('-')[-1]) + time_offset)
                transferred.append(convert_to_mega_units(x[2]))
                bandwidth.append(convert_to_mega_units(x[3]))
                retr.append(x[4])
                cwnd.append(convert_to_mega_units(x[5])*(2**20)/1500)

            return [time, transferred, bandwidth, retr, cwnd]
        else:
            print( 'mode not accepted')
    elif len(values_server) > 2:
        if mode == 'last':
            # TODO:
            return values_server[-1]
        elif mode == 'series':
            ids = []
            time = []
            transferred = []
            bandwidth = []
            for x in values_server:
                ids.append(x[0])
                time.append(float(x[1].split('-')[-1]) + time_offset)
                transferred.append(convert_to_mega_units(x[2]))
                bandwidth.append(convert_to_mega_units(x[3]))

            return [time, transferred, bandwidth]
        else:
            print( 'mode not accepted')
    
    else:
        # was: raise Exception(...)
        print( 'could not parse iperf output: ' + iperfOutput )
        return ''

def parse_iperf_json(file, offset):

    with open(file, 'r') as fin:
        iperfOutput = json.load(fin)
    
    snd_mss = iperfOutput['start']['tcp_mss_default']

    time = []
    transferred = []
    bandwidth = []
    retr = []
    cwnd = []
    rtt = []

    for interval in iperfOutput['intervals']:
        interval_data = interval['streams'][0]
        time.append(interval_data['end'] + offset)
        transferred.append(interval_data['bytes'] / (2**20))
        bandwidth.append(interval_data['bits_per_second'] / (2**20))
        if 'retransmits' in list(interval_data.keys()):
            retr.append(interval_data['retransmits'])
        if 'snd_cwnd' in list(interval_data.keys()):
            cwnd.append(interval_data['snd_cwnd'] / snd_mss)
        if 'rtt' in list(interval_data.keys()):
            rtt.append(interval_data['rtt'] / 1000)

    data_dict = {'time': time, 'transferred': transferred, 'bandwidth': bandwidth}
    if len(retr) > 0:
        data_dict['retr'] = retr
    if len(cwnd) > 0:
        data_dict['cwnd'] = cwnd
    if len(rtt) > 0:
        data_dict['rtt'] = rtt

    df = pd.DataFrame(data_dict)
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

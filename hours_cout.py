
# Results_fairness_intra_rtt

seconds = 0
flows = 0
for protocol in ['cubic', 'orca', 'aurora']:
    for buffer_size in [0.2,1,4]:
        for rtt in [20,40,60,80,100,120,140,160,180,200]:
            for run in [1,2,3,4,5]:
                seconds += (rtt*2)
                flows += 2

# Results_fairness_inter_rtt
for protocol in ['cubic', 'orca', 'aurora']:
    for buffer_size in [0.2,1,4]:
        for rtt in [20,40,60,80,100,120,140,160,180,200]:
            for run in [1,2,3,4,5]:
                seconds += (rtt*2)
                flows += 2

# Results_fairness_bw_async
for protocol in ['cubic', 'orca', 'aurora']:
    for buffer_size in [0.2,1,4]:
        for rtt in [20,40,60,80,100,120,140,160,180,200]:
            for run in [1,2,3,4,5]:
                seconds += 125
                flows += 2

# Results_friendly_intra_rtt
for protocol in ['cubic', 'orca', 'aurora']:
    for buffer_size in [0.2,1,4]:
        for rtt in [20,40,60,80,100,120,140,160,180,200]:
            for run in [1,2,3,4,5]:
                seconds += (rtt*2)
                flows += 2

# Results_friendly_bw
for protocol in ['cubic', 'orca', 'aurora']:
    for buffer_size in [0.2,1,4]:
        for rtt in [20,40,60,80,100,120,140,160,180,200]:
            for run in [1,2,3,4,5]:
                seconds += 125
                flows += 2

# Results_friendly_bw
for protocol in ['cubic', 'orca', 'aurora']:
    for buffer_size in [0.2,1,4]:
        for rtt in [20,40,60,80,100,120,140,160,180,200]:
            for run in [1,2,3,4,5]:
                seconds += 125
                flows += 2

#  AQM
for protocol in ['cubic', 'orca', 'aurora']:
    for aqm in ['fifo']:
        for bw in [100,10]:
            for buffer in [0.2,1,4]:
                for rtt in [20,200]:
                    seconds += 175
                    flows += 4
for protocol in ['cubic', 'orca', 'aurora']:
    seconds += 50*300
    flows += 50
for protocol in ['cubic', 'orca', 'aurora']:
    seconds += 50*300
    flows += 50

print(seconds/3600)
print(flows)
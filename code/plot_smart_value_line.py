#!/usr/bin/env python3

import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import numpy as np
import pandas
import datetime
from sklearn.utils import resample

# CONFIG {
data_file = "../data/data_Q1_2023_clean.csv"
figure_store = "../results/"
sample_size = 0 # 0 means no sample
smart_features = [
    'smart_5_raw',
    'smart_187_raw',
    'smart_188_raw',
    'smart_197_raw',
    'smart_198_raw'
]
smart_key_map = {
    'smart_5_raw' : 'Reallocated Sectors Count',
    'smart_187_raw': 'Reported Uncorrectable Errors',
    'smart_188_raw': 'Command Timeout',
    'smart_197_raw': 'Current Pending Sector Count',
    'smart_198_raw': 'Uncorrectable Sector Count'
}
# CONFIG }

print("Loading data csv. It may takes a while.")
data = pandas.read_csv(data_file)
if sample_size != 0:
    data = resample(data, n_samples=sample_size)

print("Filtering failed disks")
failed_disk = set(data[data['failure'] == 1]['serial_number'])
data = data[data['serial_number'].isin(failed_disk)]
smart_value_max = dict()

for index, row in tqdm(data.iterrows()):
    if row['serial_number'] not in smart_value_max:
        smart_value_max[row['serial_number']] = {
            'failed_date': row['date']
        }
        for x in smart_features:
            smart_value_max[row['serial_number']][x] = row[x]
    else:
        for x in smart_features:
            smart_value_max[row['serial_number']][x] = max(row[x], smart_value_max[row['serial_number']][x])

smart_history = [(list(),list()) for i in range(len(smart_features))]
for index, row in tqdm(data.iterrows()):
    smart_values = smart_value_max[row['serial_number']]
    for i in range(len(smart_features)):
        cur_date = datetime.datetime.strptime(row['date'], '%Y-%m-%d')
        fail_date = datetime.datetime.strptime(smart_values['failed_date'], '%Y-%m-%d')
        x_val = max((cur_date - fail_date).days,0)
        y_val = 0 if smart_values[smart_features[i]] == 0 else row[smart_features[i]] / smart_values[smart_features[i]]
        y_val_percentage = int(y_val * 1000) / 1000
        smart_history[i][0].append(x_val)
        smart_history[i][1].append(y_val_percentage)
            

for i in tqdm(range(len(smart_features))):
    plt.figure()
    plt.title(smart_key_map[smart_features[i]])
    plt.xlabel("Days to Failure")
    plt.ylabel("Value normalized")
    sns.kdeplot(x=smart_history[i][0], y=smart_history[i][1], fill=True, cmap='Spectral', cbar=True)
    plt.savefig(figure_store + smart_features[i] + ".svg",format='svg',bbox_inches = "tight")
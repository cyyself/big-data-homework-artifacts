#!/usr/bin/env python3

from config import clean_csv, figure_store, features_to_draw, smart_key_map

import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import numpy as np
import pandas
import datetime

print("Loading data csv. It may takes a while.")
data = pandas.read_csv(clean_csv)

print("Filtering failed disks")
failed_disk = set(data[data['failure'] == 1]['serial_number'])
data = data[data['serial_number'].isin(failed_disk)]
smart_value_max = dict()

for index, row in tqdm(data.iterrows()):
    if row['serial_number'] not in smart_value_max:
        smart_value_max[row['serial_number']] = {
            'failed_date': row['date']
        }
        for x in features_to_draw:
            smart_value_max[row['serial_number']][x] = row[x]
    else:
        for x in features_to_draw:
            smart_value_max[row['serial_number']][x] = max(row[x], smart_value_max[row['serial_number']][x])

smart_history = [(list(),list()) for i in range(len(features_to_draw))]
for index, row in tqdm(data.iterrows()):
    smart_values = smart_value_max[row['serial_number']]
    for i in range(len(features_to_draw)):
        cur_date = datetime.datetime.strptime(row['date'], '%Y-%m-%d')
        fail_date = datetime.datetime.strptime(smart_values['failed_date'], '%Y-%m-%d')
        x_val = max((cur_date - fail_date).days,0)
        y_val = 0 if smart_values[features_to_draw[i]] == 0 else row[features_to_draw[i]] / smart_values[features_to_draw[i]]
        y_val_percentage = int(y_val * 1000) / 1000
        smart_history[i][0].append(x_val)
        smart_history[i][1].append(y_val_percentage)
            

for i in tqdm(range(len(features_to_draw))):
    plt.figure()
    plt.title(smart_key_map[features_to_draw[i]])
    plt.xlabel("Days to Failure")
    plt.ylabel("Value normalized")
    sns.kdeplot(x=smart_history[i][0], y=smart_history[i][1], fill=True, cmap='Spectral', cbar=True)
    plt.savefig(figure_store + features_to_draw[i] + ".svg",format='svg',bbox_inches = "tight")
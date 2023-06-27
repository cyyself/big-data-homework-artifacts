#!/usr/bin/env python3

from config import clean_csv, train_csv, test_csv, classes, max_date, sample_size_each, train_set_proportion

from tqdm import tqdm
import pandas
import datetime
import numpy as np
from sklearn.utils import resample

print("Loading data csv. It may takes a while.")
data = pandas.read_csv(clean_csv)

failed_date = dict() # failed_date sn=>date_str

for id, row in tqdm(data[data['failure'] == 1].iterrows()):
    failed_date[row['serial_number']] = row['date']

# For date > max_date, we must delete to eusure they will not fail in 20 days
data = data[data['date'] <= max_date]

# Update data
for id, row in tqdm(data[data['serial_number'].isin(failed_date)].iterrows()):
    cur_date  = datetime.datetime.strptime(row['date'], '%Y-%m-%d')
    fail_date = datetime.datetime.strptime(failed_date[row['serial_number']], '%Y-%m-%d')
    days_to_fail = (fail_date - cur_date).days
    cur_class = 0
    for i in range(len(classes)-1,0,-1):
        if days_to_fail <= classes[i][0]:
            cur_class = i
            break
    data.at[id, 'failure'] = cur_class

# resample each class and split train and test set
# Warn: same SN must not be in the both test and train set
each_class = []
sn = set()
for i in range(len(classes)):
    cur_class = resample(data[data['failure'] == i], n_samples=sample_size_each)
    sn = sn.union(set(cur_class['serial_number']))
    each_class.append(cur_class)

sn_list = list(sn)
split_pos = int(len(sn_list) * train_set_proportion)
train_sn = set(sn_list[:split_pos])
test_sn = set(sn_list[split_pos:])

print("Train SN size:",len(train_sn))
print("Test SN size:",len(test_sn))
print("Train SN union Test SN size:", len(train_sn.union(test_sn)))
print("Train SN inter Test SN size:", len(train_sn) + len(test_sn) - len(train_sn.union(test_sn)))

assert(len(train_sn) + len(test_sn) - len(set(train_sn).union(set(test_sn))) == 0)

# Save train and test set
train_set = None
test_set = None
for i in range(len(classes)):
    cur_class = each_class[i]
    cur_train = cur_class[cur_class['serial_number'].isin(train_sn)]
    cur_test = cur_class[cur_class['serial_number'].isin(test_sn)]
    train_set = cur_train if train_set is None else pandas.concat( (train_set, cur_train), ignore_index=True)
    test_set  = cur_test  if test_set  is None else pandas.concat( (test_set , cur_test ), ignore_index=True)

for i in range(len(classes)):
    print("Class {} size of train_set is {}, test_set is {}".format(i, len(train_set[train_set['failure']==i]), len(test_set[test_set['failure']==i])))

train_set.to_csv(train_csv)
test_set.to_csv(test_csv)
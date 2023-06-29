#!/usr/bin/env python3

from config import clean_csv, train_csv, test_csv, classes, max_date, sample_size_each, train_size, test_size, use_real_failure_rate_for_each_class, random_state

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
if use_real_failure_rate_for_each_class:
    normal_class = resample(data[data['failure'] == 0], n_samples=sample_size_each, random_state=random_state)
    failed_class = resample(data[data['failure'] != 0], n_samples=sample_size_each, random_state=random_state)
    sn = sn.union(set(normal_class['serial_number']).union(set(failed_class['serial_number'])))
    each_class = [normal_class, failed_class]
else:
    for i in range(len(classes)):
        cur_class = resample(data[data['failure'] == i], n_samples=sample_size_each, random_state=random_state)
        sn = sn.union(set(cur_class['serial_number']))
        each_class.append(cur_class)

sn_list = list(sn)
train_sn = set()
test_sn = set()
for idx in range(len(sn_list)):
    if (idx % (train_size + test_size)) < train_size:
        train_sn.add(sn_list[idx])
    else:
        test_sn.add(sn_list[idx])

print("Train SN size:",len(train_sn))
print("Test SN size:",len(test_sn))
print("Train SN union Test SN size:", len(train_sn.union(test_sn)))
print("Train SN inter Test SN size:", len(train_sn) + len(test_sn) - len(train_sn.union(test_sn)))

assert(len(train_sn) + len(test_sn) - len(set(train_sn).union(set(test_sn))) == 0)

# Save train and test set
train_set = None
test_set = None
for i in range(len(each_class)):
    cur_class = each_class[i]
    cur_train = cur_class[cur_class['serial_number'].isin(train_sn)]
    cur_test = cur_class[cur_class['serial_number'].isin(test_sn)]
    train_set = cur_train if train_set is None else pandas.concat( (train_set, cur_train), ignore_index=True)
    test_set  = cur_test  if test_set  is None else pandas.concat( (test_set , cur_test ), ignore_index=True)

for i in range(len(classes)):
    print("Class {} size of train_set is {}, test_set is {}".format(i, len(train_set[train_set['failure']==i]), len(test_set[test_set['failure']==i])))

train_set.to_csv(train_csv)
test_set.to_csv(test_csv)
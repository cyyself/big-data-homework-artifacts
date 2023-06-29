#!/usr/bin/env python3

from config import clean_csv, classes, max_date, sample_size_each, train_size, test_size, use_real_failure_rate_for_each_class, features

from tqdm import tqdm
import pandas
import datetime
import numpy as np
from sklearn.utils import resample
from sklearn.ensemble import RandomForestClassifier
import sys

random_state = int(sys.argv[1])


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

sn_list = sorted(list(sn))
train_sn = set()
test_sn = set()
for idx in range(len(sn_list)):
    if (idx % (train_size + test_size)) < train_size:
        train_sn.add(sn_list[idx])
    else:
        test_sn.add(sn_list[idx])

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


classifier = RandomForestClassifier(verbose=True, random_state=random_state)

train_data = train_set
test_data  = test_set

def drop_unused_features(data_set):
    to_drop = [each_feature for each_feature in data_set if each_feature not in features]
    data_set.drop(to_drop, inplace=True, axis=1)

def train(data_set, clasf):
    X = data_set.drop('failure', axis=1)
    Y = data_set['failure']
    clasf.fit(X, Y)
    return (X, Y)

def predict(clasf, data_set):
    X = data_set.drop('failure', axis=1)
    Y = data_set['failure']
    return (X, clasf.predict(X), Y)

def evaluate(predict_Y, test_Y):
    # print("Random Forest classifier")
    # print(classes)
    nr_correct = (test_Y == predict_Y).sum()
    nr_bool_corrent = (np.array(predict_Y != 0) == np.array(test_Y != 0)).sum()
    nr_failed = (test_Y != 0).sum()
    nr_recall = sum([(predict_Y[i] != 0) == (test_Y[i] != 0) and test_Y[i] != 0 for i in range(len(test_Y))])
    nr_all = len(test_Y)
    
    acc_rate = nr_correct / nr_all
    # print("The accuracy rate is {}".format(acc_rate))

    fail_acc_rate = nr_bool_corrent / nr_all
    # print("The predict fail acc rate is {}".format(fail_acc_rate))

    recall_rate = nr_recall / nr_failed
    # print("The recall rate is {}".format(recall_rate))
    
    print("{},{},{},{}".format(random_state, acc_rate, fail_acc_rate, recall_rate))

drop_unused_features(train_data)
train_X, train_Y = train(train_data, classifier)
# plot_tree_to_file(classifier, train_X)
drop_unused_features(test_data)
test_X, predict_Y, test_Y = predict(classifier, test_data)
evaluate(predict_Y, test_Y)
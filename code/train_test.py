#!/usr/bin/env python3

import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np
import pandas
from sklearn.tree import plot_tree

from config import train_csv, test_csv, classes, features, features, classifier

train_data = pandas.read_csv(train_csv)
test_data  = pandas.read_csv(test_csv)

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

def plot_tree_to_file(clasf, train_X):
    plt.figure()
    plot_tree(clasf.estimators_[0],feature_names=train_X.keys(),class_names=[x[1] for x in classes])
    plt.savefig('tree.svg',format='svg',bbox_inches = "tight")

def evaluate(predict_Y, test_Y):
    print("Random Forest classifier")
    print(classes)
    nr_correct = (test_Y == predict_Y).sum()
    nr_bool_corrent = (np.array(predict_Y != 0) == np.array(test_Y != 0)).sum()
    nr_failed = (test_Y != 0).sum()
    nr_recall = sum([(predict_Y[i] != 0) == (test_Y[i] != 0) and test_Y[i] != 0 for i in range(len(test_Y))])
    nr_all = len(test_Y)
    
    acc_rate = nr_correct / nr_all
    print("The accuracy rate is {}".format(acc_rate))

    fail_acc_rate = nr_bool_corrent / nr_all
    print("The predict fail acc rate is {}".format(fail_acc_rate))

    recall_rate = nr_recall / nr_failed
    print("The recall rate is {}".format(recall_rate))

drop_unused_features(train_data)
train_X, train_Y = train(train_data, classifier)
# plot_tree_to_file(classifier, train_X)
drop_unused_features(test_data)
test_X, predict_Y, test_Y = predict(classifier, test_data)
evaluate(predict_Y, test_Y)
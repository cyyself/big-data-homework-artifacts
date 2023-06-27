#!/usr/bin/env python3

from config import data_dir, clean_csv, preserve_features

import os
import pandas
from tqdm import tqdm

failed_disk_set = set()

cur_csv = None
for root, dirs, files in os.walk(data_dir):
    for name in tqdm(sorted(files)):
        if name.endswith('.csv'):
            cur_file = pandas.read_csv(os.path.join(root, name))
            features_to_drop = [each_feature for each_feature in cur_file if each_feature not in preserve_features]
            cur_file = cur_file[~cur_file['serial_number'].isin(failed_disk_set)]
            cur_file.drop(features_to_drop, inplace=True, axis=1)
            cur_file.fillna(0, inplace=True)
            if cur_csv is None:
                cur_csv = cur_file
            else:
                cur_csv = pandas.concat( (cur_csv, cur_file), ignore_index=True)
            cur_failed_list = cur_file[cur_file['failure'] == 1]['serial_number']
            for x in cur_failed_list:
                failed_disk_set.add(x)
print("Saving cleaned data to csv")
cur_csv.to_csv(clean_csv)
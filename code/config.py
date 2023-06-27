from sklearn.ensemble import RandomForestClassifier

# Do not change {
# These values are not protected by Makefile, if you make changes to these values, you should manually clean the files.
data_dir = '../data/data_Q1_2023'
clean_csv = '../data/data_Q1_2023_clean.csv'
train_csv = '../data/data_Q1_2023_train.csv'
test_csv  = '../data/data_Q1_2023_test.csv'
figure_store = "../results/"
smart_key_map = {
    'smart_5_raw' : 'Reallocated Sectors Count',
    'smart_187_raw': 'Reported Uncorrectable Errors',
    'smart_188_raw': 'Command Timeout',
    'smart_197_raw': 'Current Pending Sector Count',
    'smart_198_raw': 'Uncorrectable Sector Count'
}
preserve_features = [
    'date',
    'serial_number',
    'model',
    'capacity_bytes',
    'failure',
    'smart_5_raw',
    'smart_187_raw',
    'smart_188_raw',
    'smart_197_raw',
    'smart_198_raw'
]
features_to_draw = [
    'smart_5_raw',
    'smart_187_raw',
    'smart_188_raw',
    'smart_197_raw',
    'smart_198_raw'
]
# Do not change }

classes = [
    (0, "Normal"),
    (20, "Likely to fail in 20 days"),
    (7, "Likely to fail in 7 days"),
    (3, "Likely to fail in 3 days")
]

features = [
    'failure',
    'smart_5_raw',
    'smart_187_raw',
    'smart_188_raw',
    'smart_197_raw',
    'smart_198_raw'
]
classifier = RandomForestClassifier(verbose=True)
max_date = "2023-03-11"
sample_size_each = int(1e5)
train_set_proportion = 0.9
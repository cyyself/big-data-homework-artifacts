all: results/smart_198_raw.svg

data/data_Q1_2023/2023-03-31.csv:
	cd data && make data_Q1_2023

data/data_Q1_2023_clean.csv: code/clean_data.py data/data_Q1_2023/2023-03-31.csv
	cd code && python3 clean_data.py

results/smart_198_raw.svg: code/plot_smart_value_line.py data/data_Q1_2023_clean.csv
	cd code && python3 plot_smart_value_line.py

data/data_Q1_2023_test.csv: code/split_data.py data/data_Q1_2023_clean.csv
	cd code && python3 split_data.py
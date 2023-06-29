test_range = range(1,10001)
print("all : {}".format(" ".join(["../results/random-{}.csv".format(i) for i in test_range])))
for i in range(1,10000):
    print("../results/random-{}.csv:\n\tpython3 test_param.py {} > $@".format(i,i))
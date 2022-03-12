import pandas as pd
data= pd.read_csv("datapts.csv")
data
data.columns
# extracting time
data.tc
import time
def increase_value_evrey_t_sec(initail_value, interval, increase_by,stop_after = -1):
    counter = 0
    values = []
    while counter < stop_after or stop_after == -1:
        time.sleep(interval)
        initail_value += increase_by
        print(initail_value)
        values.append(initail_value)
        counter += 1

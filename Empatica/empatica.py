from scipy.signal import butter, filtfilt
import csv
import datetime as time
import numpy as np
import matplotlib.pyplot as plt

def analyze(filename, plotting=True, printing=False):
    with open(filename) as file:
        reader = csv.reader(file, delimiter=",")
        datalist = list(reader)

        datalist = [float(item) for sublist in datalist for item in sublist]

        # Time and date
        timestamp = int(datalist[0])
        start_time = time.datetime.fromtimestamp(timestamp)
        freq = datalist[1]

        datalist = datalist[2:]
        n = len(datalist)

        duration = int(n/freq)
        end_time = start_time + time.timedelta(seconds=duration)        
        
        if printing:
            print(datalist)
        
        if plotting:
            x = list(range(n))

            y = butter_lowpass_filter(datalist, 0.05, 1, freq)
            
            plt.plot(x, datalist)
            plt.plot(x, y)
            
            plt.title(str(start_time.date()) + "\n" + str(start_time.time()) + " - " + str(end_time.time()))
            plt.show()


def butter_lowpass_filter(data, cutoff, order, freq):
    normal_cutoff = cutoff / (freq * 1)
    # Get the filter coefficients 
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

analyze("EDA.csv")
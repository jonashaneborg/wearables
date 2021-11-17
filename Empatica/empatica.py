from scipy.signal import butter, filtfilt
from scipy import interpolate
import csv
import datetime as time
import numpy as np
import matplotlib.pyplot as plt

def EDA(filename, plotting=False):
    with open(filename) as file:
        reader = csv.reader(file, delimiter=",")
        datalist = list(reader)
        datalist = [float(item) for sublist in datalist for item in sublist]

        timestamp = int(datalist[0])
        freq = datalist[1]
        datalist = datalist[2:]        

        # Butter lowpass filter
        cutoff = 5
        norm_cutoff = cutoff/(freq/2)
        order = 1
        lowpassed = butter_filter(datalist, norm_cutoff, order, freq)

        # Butter highpass filter
        cutoff = 0.05
        norm_cutoff = cutoff/(freq/2)
        order = 2
        highpassed = butter_filter(lowpassed, norm_cutoff, order, freq, btype='high')

        # Downsample to 1 Hz
        downsampled = []
        sum = 0
        for i in range(len(highpassed)):
            sum += highpassed[i]

            if (i+1)%4==0:
                downsampled.append(sum)
                sum = 0

        n = len(downsampled)  
        x = list(range(n))
        
        # Cubic spline 
        tck = interpolate.splrep(x, downsampled)
        y = interpolate.splev(x, tck, der=2)

        ampl_scores = amplitude_increase(y)
        rise_scores = rising_time(y)
        resp_scores = response_slope(y)

        scores = [a + b + c for a,b,c in zip(ampl_scores, rise_scores, resp_scores)]
    
        # Time
        start_time = time.datetime.fromtimestamp(timestamp)
        duration = int(4*n/freq)
        end_time = start_time + time.timedelta(seconds=duration)

        if plotting:
            plot_data(x, y, start_time, end_time, scores)
            
        return downsampled

def amplitude_increase(y):
    n = len(y)
    scores = [0]*n

    for i in range(n):
        pointer = i + 1
        counter = 0
        while pointer - i <= 6 and pointer < n:
            if y[pointer] > y[pointer-1]:
                counter += 1
            else:
                if 2 <= counter <= 5:
                    scores[i] = 1.0
                elif counter > 5:
                    scores[i] = 0.5 
                break

            pointer+=1

    return scores

def find_extrema(y):
    n = len(y)
    extrema = [0]*n
    for i in range(1, n-1):
        if y[i-1] < y[i] > y[i+1]:
            extrema[i] = 1
        elif y[i-1] > y[i] < y[i+1]:
            extrema[i] = -1

    return extrema

def rising_time(y):
    n = len(y)
    scores = [0]*n
    extrema = find_extrema(y)

    for i in range(n):
        if extrema[i] == -1:
            pointer = i+1
            while pointer - i <= 10 and pointer < n:
                if extrema[pointer] == 1:
                    if 1 < pointer-i <= 5:
                        scores[i] = 1.0
                    elif pointer-i > 5:
                        scores[i] = 0.5
                    break

                pointer += 1
        
    return scores


def response_slope(y):
    n = len(y)
    scores = [0]*n
    extrema = find_extrema(y)

    for i in range(n):
        if extrema[i] == -1:
            pointer = i+1
            while pointer - i <= 10 and pointer < n:
                if extrema[pointer] == 1:
                    if 1 < (y[pointer]-y[i])/(pointer-i) >= 2.777:
                        scores[i] = 1.0
                    elif 1 < (y[pointer]-y[i])/(pointer-i) > 2.222:
                        scores[i] = 0.5
                    break

                pointer += 1

    return scores

def butter_filter(data, cutoff, order, freq, btype='low'):
    normal_cutoff = cutoff / (freq * 1)
    # Get the filter coefficients 
    b, a = butter(order, normal_cutoff, btype, analog=False)
    y = filtfilt(b, a, data)
    return y

def plot_data(x, y, start, end, a):
    plt.plot(x, y)        
    plt.plot(x, a)
    plt.title(str(start.date()) + "\n" + str(start.time()) + " - " + str(end.time()))
    plt.show()


y = EDA("Empatica/Data/EDA.csv", plotting=True)

    
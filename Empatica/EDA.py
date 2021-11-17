from scipy.signal import butter, filtfilt
from scipy import interpolate
from reader import *
import matplotlib.pyplot as plt

class EDA:
    reader = None
    data = []
    sampling_rate = 0
    start_time = 0
    end_time = 0
    duration = 0
    num = 0

    scores = []

    def __init__(self, filepath):
        self.reader = Reader(filepath)
        self.data = self.reader.data
        self.sampling_rate = self.reader.sampling_rate
        self.start_time = self.reader.start_time
        self.end_time = self.reader.end_time
        self.num = self.reader.n

    def detect_MOS(self, plotting=False):  
        # Butter lowpass filter
        cutoff = 5
        norm_cutoff = cutoff/(self.sampling_rate/2)
        lowpassed = self.butter_filter(self.data, norm_cutoff, 1, self.sampling_rate)

        # Butter highpass filter
        cutoff = 0.05
        norm_cutoff = cutoff/(self.sampling_rate/2)
        highpassed = self.butter_filter(lowpassed, norm_cutoff, 2, self.sampling_rate, btype='high')
    
        # Downsample to 1 Hz
        downsampled = self.down_sample(highpassed, self.sampling_rate)
        n = len(downsampled)  
        x = list(range(n))
    
        # Cubic spline 
        tck = interpolate.splrep(x, downsampled)
        y = interpolate.splev(x, tck, der=3)
    
        ampl_scores = self.amplitude_increase(y)
        rise_scores = self.rising_time(y)
        resp_scores = self.response_slope(y)

        scores = [a + b + c for a,b,c in zip(ampl_scores, rise_scores, resp_scores)]

        if plotting:
            self.plot_data(x, y, scores)
            
        return downsampled

    
    def down_sample(self, list, freq):
        ''' Averaging values using a ``freq`` window size.

        Parameters:
        -----------
        list : array_like
            List of data to be downsampled
        freq : int
            The original sample rate in Hz
        '''
        downsampled = []
        sum = 0
        for i in range(len(list)):
            sum += list[i]

            if (i+1)%freq==0:
                downsampled.append(sum)
                sum = 0

        return downsampled

    def amplitude_increase(self, y):
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

    def find_extrema(self, y):
        n = len(y)
        extrema = [0]*n
        for i in range(1, n-1):
            if y[i-1] < y[i] > y[i+1]:
                extrema[i] = 1
            elif y[i-1] > y[i] < y[i+1]:
                extrema[i] = -1

        return extrema

    def rising_time(self, y):
        n = len(y)
        scores = [0]*n
        extrema = self.find_extrema(y)

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


    def response_slope(self, y):
        n = len(y)
        scores = [0]*n
        extrema = self.find_extrema(y)

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

    def butter_filter(self, data, cutoff, order, freq, btype='low'):
        normal_cutoff = cutoff / (freq * 1)
        # Get the filter coefficients 
        b, a = butter(order, normal_cutoff, btype, analog=False)
        y = filtfilt(b, a, data)
        return y

    def plot_data(self, x, y, scores):
        plt.plot(x, y)        
        plt.plot(x, scores)
        plt.title(self.reader.getDate(self.start_time) + "\n" + self.reader.getTime(self.start_time) + " - " + self.reader.getTime(self.end_time))
        plt.show()


eda = EDA("Empatica/Data/EDA.csv")
eda.detect_MOS(plotting=True)

    
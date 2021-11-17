import csv
import datetime as time

class Reader:
    data = []
    sampling_rate = 0
    start_time = 0
    end_time = 0
    duration = 0
    n = 0

    def __init__(self, filepath):
        with open(filepath) as file:
            reader = csv.reader(file, delimiter=",")
            datalist = list(reader)
            datalist = [float(item) for sublist in datalist for item in sublist]

            timestamp = int(datalist[0])
            self.sampling_rate = datalist[1]
            self.data = datalist[2:]
            self.n = len(self.data)  

            # Time
            self.start_time = time.datetime.fromtimestamp(timestamp)
            self.duration = int(self.n/self.sampling_rate)
            self.end_time = self.start_time + time.timedelta(seconds=self.duration)

    def getDate(self, time):
        return str(time.date())

    def getTime(self, time):
        return str(time.time())
    



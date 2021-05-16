from datetime import datetime, timedelta
from pandas import date_range


class Timer():
    def __init__(self, pastHours=24, futureHours=24):
        self.generateTime()
        self.generateFormat()

    def generateTime(self, pastHours=24, futureHours=24):
        self.nowTime = datetime.now().replace(minute=0, second=0, microsecond=0)
        self.startTime = self.nowTime - timedelta(hours=pastHours)
        self.endTime = self.nowTime + timedelta(hours=futureHours)

    def generateFormat(self):
        self.obsDateRange = date_range(self.startTime, self.nowTime, freq='H')
        self.nowDateRange = date_range(self.nowTime, self.endTime, freq='H')[0]
        self.simDateRange = date_range(
            self.nowTime, self.endTime, freq='H')[1:]
        self.allDateRange = date_range(self.startTime, self.endTime, freq='H')

        self.nowFormat = self.nowTime.strftime('%Y%m%d%H')
        self.obsFormat = [i.strftime('%Y-%m-%dT%H:00:00+08:00')
                          for i in self.obsDateRange]
        self.simFormat = [i.strftime('%Y%m%d%H') for i in self.simDateRange]


if __name__ == '__main__':
    times = Timer()
    print(times.obsDateRange)

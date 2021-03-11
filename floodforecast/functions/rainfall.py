from ..databases.url_database import _url
from ..databases.rainstation_database import _stationData
from ..functions.timer import Timer
import os
import collections
from zipfile import ZipFile
from urllib.request import urlopen
from io import BytesIO
import json
import re
import pandas as pd
from numpy import mean, nan


class Rain():

    def __init__(
            self,
            stationNameList, nowFormat, obsFormat, simFormat,
            obsUrl='CWB', simUrl='QPESUMSWRF'
    ):
        self.stationNameList = stationNameList
        self.nowFormat = nowFormat
        self.obsFormat = obsFormat
        self.simFormat = simFormat
        self.obsUrl = _url[obsUrl]
        self.simUrl = _url[simUrl]
        self.rainDict, self.simRainDict = self.generateRainDicts()

    def generateRainDicts(self):
        self.rainDict = {}
        self.simRainDict = collections.defaultdict(list)

        zipName = 'grid_rain_0000.0{:0>2d}{}'
        # extract obs data from thinktron's api
        for stcode in self.stationNameList:
            data = urlopen(self.obsUrl.format(stcode)).read().decode('utf-8')
            output = json.loads(data)
            obsSeries = []
            for i in self.obsFormat:
                value = nan
                for j in range(len(output)):
                    if output[j]['time'] == i:
                        value = output[j]['01h']
                        pass
                if value is nan:
                    print('station: {} in {} has No value'.format(stcode, i))
                    obsSeries.append(-9999)
                else:
                    obsSeries.append(value)
            self.rainDict[stcode] = obsSeries

        # extract sim data from QPESUMS
        for num in range(len(self.simFormat)):
            try:
                data = urlopen(os.path.join(
                    self.simUrl, self.nowFormat, zipName.format(num + 1, '.zip')))
                zipfile = ZipFile(BytesIO(data.read()))
                rawFile = []

                for line in zipfile.open(zipName.format(num + 1, '')).readlines():
                    rawData = re.split('\r|    |  ', line.decode('utf-8'))[0:3]
                    rawFile.append(rawData)
                simRainDataFrame = pd.DataFrame(
                    rawFile[5:], columns=['Longtitude', 'Latitude', 'intensity (mm/hr)'])

                for stcode in self.stationNameList:
                    forecastPoint = [
                        int(i) for i in _stationData[stcode]['points']
                        ]
                    value = round(mean(
                        [float(i) for i in simRainDataFrame.loc[forecastPoint].iloc[:, 2]]
                        ), 2)
                    self.rainDict[stcode].append(value)
                    self.simRainDict[stcode].append(value)
            except:
                self.rainDict[stcode].append(-9999)
                self.simRainDict[stcode].append(-9999)

        return self.rainDict, self.simRainDict

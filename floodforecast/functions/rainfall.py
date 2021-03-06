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

from datetime import datetime, timedelta
import numpy as np


class Rain():

    def __init__(
            self,
            stationNameList, nowFormat, obsFormat, simFormat,
            obsUrl='CWB'
    ):
        self.stationNameList = stationNameList
        self.nowFormat = nowFormat
        self.obsFormat = obsFormat
        self.simFormat = simFormat
        self.obsUrl = _url[obsUrl]

        self.obsRainDict = self.generateObsRainDict()

    def generateObsRainDict(self):
        obsRainDict = {}

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

            obsRainDict[stcode] = obsSeries

        return obsRainDict

    def generateSimRainDict(self, simUrl):
        simRainDict = collections.defaultdict(list)

        zipName = 'grid_rain_0000.0{:0>2d}{}'
        # extract sim data
        for num in range(len(self.simFormat)):
            try:
                data = urlopen(os.path.join(
                    _url[simUrl], self.nowFormat, zipName.format(num + 1, '.zip')))
                zipfile = ZipFile(BytesIO(data.read()))
                rawFile = []

                for line in zipfile.open(zipName.format(num + 1, '')).readlines():
                    rawData = re.split('\r|    |  ', line.decode('utf-8'))[0:3]
                    rawFile.append(rawData)
                simRainDataFrame = pd.DataFrame(
                    rawFile[5:], columns=['Longtitude', 'Latitude', 'intensity (mm/hr)']
                )

                simFlag = True
            
            except:
                simFlag = False
            

            # append simRainDict's value
            for stcode in self.stationNameList:
                if simFlag:
                    forecastPoint = [int(i) for i in _stationData[stcode]['points']]
                    value = round(mean([float(i) for i in simRainDataFrame.loc[forecastPoint].iloc[:, 2]]), 2)
                    simRainDict[stcode].append(value)
                else:
                    simRainDict[stcode].append(-9999)
        
        
        return simRainDict
    
    def generateRainDict(self, obsRainDict, simRainDict):
        
        rainDict = obsRainDict.copy()
        for stcode in rainDict.keys():
            rainDict[stcode].extend(simRainDict[stcode])

        return rainDict

# ??????????????????
    def rainwarning(self, simRainDict):
        warning = simRainDict
        warningStation = []
        dic_values = warning.values()
        dic_keys = warning.keys()

        # mode='w'?????????txt?????????,???????????????????????????
        rain_file = open("rainfallWarn.txt", mode='w', encoding='utf-8')
        rain_file.close()

        for datas in dic_values:
            sum = 0
            # print(datas)
            for data_24hrs in datas:   # ??????24hrs????????????
                key = list(dic_keys)[list(dic_values).index(datas)]
                sum += data_24hrs
                if sum >= 500:      # ????????????????????????????????????24hr???????????????500mm
                    warningStation.append(key)
                    data_sum = 0
                    with open("rainfallWarn.txt", mode='a', encoding='utf-8') as rain_file:  # mode='a'????????????
                        rain_file.write(' \n')
                        rain_file.write('{}??????({})'.format(
                            _stationData[key]['chineseName'], key))
                        rain_file.write(' \n')
                        rain_file.write('????????????????????????????????????(24?????????????????????500mm)')
                        rain_file.write(' \n')
                        rain_file.write(
                            '--------------------------------------------------------------------------------')
                        rain_file.write(' \n')
                        rain_file.write('???????????? : {}'.format(
                            datetime.now().replace(minute=0, second=0, microsecond=0)))
                        rain_file.write(' \n')
                        rain_file.write(' \n')

                    for i, data in enumerate(datas):
                        data_sum += data
                        result = "%.2f" % data_sum
                        nowdatatime = datetime.now().replace(
                            minute=0, second=0, microsecond=0) + timedelta(hours=i)
                        with open("rainfallWarn.txt", mode='a', encoding='utf-8') as rain_file:
                            rain_file.write(
                                '{}, {} mm/hr, ???????????? {} mm'.format(nowdatatime.strftime("%m-%d, %H:%M"), data, result))
                            rain_file.write(' \n')
                    break

                elif sum >= 350:    # ?????????????????????????????????24hr???????????????350mm & 3hr???????????????200mm
                    warningStation.append(key)
                    data_sum = 0
                    with open("rainfallWarn.txt", mode='a', encoding='utf-8') as rain_file:
                        rain_file.write(' \n')
                        rain_file.write('{}??????({})'.format(
                            _stationData[key]['chineseName'], key))
                        rain_file.write(' \n')
                        rain_file.write('?????????????????????????????????(24?????????????????????350mm)')
                        rain_file.write(' \n')
                        rain_file.write(
                            '--------------------------------------------------------------------------------')
                        rain_file.write(' \n')
                        rain_file.write('???????????? : {}'.format(
                            datetime.now().replace(minute=0, second=0, microsecond=0)))
                        rain_file.write(' \n')
                        rain_file.write(' \n')

                    for i, data in enumerate(datas):
                        data_sum += data
                        result = "%.2f" % data_sum
                        nowdatatime = datetime.now().replace(
                            minute=0, second=0, microsecond=0) + timedelta(hours=i)
                        with open("rainfallWarn.txt", mode='a', encoding='utf-8') as rain_file:
                            rain_file.write(
                                '{}, {} mm/hr, ???????????? {} mm'.format(nowdatatime.strftime("%m-%d, %H:%M"), data, result))
                            rain_file.write(' \n')
                    break

                elif sum >= 200:    # ??????????????????????????????24hr???????????????200mm & 3hr???????????????100mm
                    warningStation.append(key)
                    data_sum = 0
                    with open("rainfallWarn.txt", mode='a', encoding='utf-8') as rain_file:
                        rain_file.write(' \n')
                        rain_file.write('{}??????({})'.format(
                            _stationData[key]['chineseName'], key))
                        rain_file.write(' \n')
                        rain_file.write('??????????????????????????????(24?????????????????????200mm)')
                        rain_file.write(' \n')
                        rain_file.write(
                            '--------------------------------------------------------------------------------')
                        rain_file.write(' \n')
                        rain_file.write('???????????? : {}'.format(
                            datetime.now().replace(minute=0, second=0, microsecond=0)))
                        rain_file.write(' \n')
                        rain_file.write(' \n')

                    for i, data in enumerate(datas):
                        data_sum += data
                        result = "%.2f" % data_sum
                        nowdatatime = datetime.now().replace(
                            minute=0, second=0, microsecond=0) + timedelta(hours=i)
                        with open("rainfallWarn.txt", mode='a', encoding='utf-8') as rain_file:
                            rain_file.write(
                                '{}, {} mm/hr, ???????????? {} mm'.format(nowdatatime.strftime("%m-%d, %H:%M"), data, result))
                            rain_file.write(' \n')
                    break

                elif sum >= 80:    # ??????????????????????????????24hr???????????????80mm & 1hr???????????????40mm
                    warningStation.append(key)
                    data_sum = 0
                    with open("rainfallWarn.txt", mode='a', encoding='utf-8') as rain_file:
                        rain_file.write(' \n')
                        rain_file.write('{}??????({})'.format(
                            _stationData[key]['chineseName'], key))
                        rain_file.write(' \n')
                        rain_file.write('??????????????????????????????(24?????????????????????80mm)')
                        rain_file.write(' \n')
                        rain_file.write(
                            '--------------------------------------------------------------------------------')
                        rain_file.write(' \n')
                        rain_file.write('???????????? : {}'.format(
                            datetime.now().replace(minute=0, second=0, microsecond=0)))
                        rain_file.write(' \n')
                        rain_file.write(' \n')

                    for i, data in enumerate(datas):
                        data_sum += data
                        result = "%.2f" % data_sum
                        nowdatatime = datetime.now().replace(
                            minute=0, second=0, microsecond=0) + timedelta(hours=i)
                        with open("rainfallWarn.txt", mode='a', encoding='utf-8') as rain_file:
                            rain_file.write(
                                '{}, {} mm/hr, ???????????? {} mm'.format(nowdatatime.strftime("%m-%d, %H:%M"), data, result))
                            rain_file.write(' \n')
                    break

            for data_3hrs in range(len(datas)):          # ??????3hrs????????????
                if data_3hrs == 0 or data_3hrs == 1:
                    continue
                rain_sum = np.sum(
                    (datas[data_3hrs], datas[data_3hrs-1], datas[data_3hrs-2]))   # ???????????????????????????
                key = list(dic_keys)[list(dic_values).index(datas)]
                if rain_sum > 200:                    # ??????3hr???????????????200mm
                    warningStation.append(key)
                    data_sum = 0
                    with open("rainfallWarn.txt", mode='a', encoding='utf-8') as rain_file:  # mode='a'????????????
                        rain_file.write(' \n')
                        rain_file.write('{}??????({})'.format(
                            _stationData[key]['chineseName'], key))
                        rain_file.write(' \n')
                        rain_file.write('?????????????????????????????????(3?????????????????????200mm)')
                        rain_file.write(' \n')
                        rain_file.write(
                            '--------------------------------------------------------------------------------')
                        rain_file.write(' \n')
                        rain_file.write('???????????? : {}'.format(
                            datetime.now().replace(minute=0, second=0, microsecond=0)))
                        rain_file.write(' \n')
                        rain_file.write(' \n')

                    for i, data in enumerate(datas):
                        data_sum += data
                        result = "%.2f" % data_sum
                        nowdatatime = datetime.now().replace(
                            minute=0, second=0, microsecond=0) + timedelta(hours=i)
                        with open("rainfallWarn.txt", mode='a', encoding='utf-8') as rain_file:
                            rain_file.write(
                                '{}, {} mm/hr, ???????????? {} mm'.format(nowdatatime.strftime("%m-%d, %H:%M"), data, result))
                            rain_file.write(' \n')
                    break

                elif rain_sum > 100:                  # ??????3hr???????????????100mm
                    warningStation.append(key)
                    data_sum = 0
                    with open("rainfallWarn.txt", mode='a', encoding='utf-8') as rain_file:
                        rain_file.write(' \n')
                        rain_file.write('{}??????({})'.format(
                            _stationData[key]['chineseName'], key))
                        rain_file.write(' \n')
                        rain_file.write('??????????????????????????????(3?????????????????????100mm)')
                        rain_file.write(' \n')
                        rain_file.write(
                            '--------------------------------------------------------------------------------')
                        rain_file.write(' \n')
                        rain_file.write('???????????? : {}'.format(
                            datetime.now().replace(minute=0, second=0, microsecond=0)))
                        rain_file.write(' \n')
                        rain_file.write(' \n')

                    for i, data in enumerate(datas):
                        data_sum += data
                        result = "%.2f" % data_sum
                        nowdatatime = datetime.now().replace(
                            minute=0, second=0, microsecond=0) + timedelta(hours=i)
                        with open("rainfallWarn.txt", mode='a', encoding='utf-8') as rain_file:
                            rain_file.write(
                                '{}, {} mm/hr, ???????????? {} mm'.format(nowdatatime.strftime("%m-%d, %H:%M"), data, result))
                            rain_file.write(' \n')
                    break

            for data_1hr in datas:                       # ??????1hr???????????????40mm
                key = list(dic_keys)[list(dic_values).index(datas)]
                if float(data_1hr) > 40:
                    warningStation.append(key)
                    data_sum = 0
                    with open("rainfallWarn.txt", mode='a', encoding='utf-8') as rain_file:
                        rain_file.write(' \n')
                        rain_file.write('{}??????({})'.format(
                            _stationData[key]['chineseName'], key))
                        rain_file.write(' \n')
                        rain_file.write('??????????????????????????????(1???????????????40mm)')
                        rain_file.write(' \n')
                        rain_file.write(
                            '--------------------------------------------------------------------------------')
                        rain_file.write(' \n')
                        rain_file.write('???????????? : {}'.format(
                            datetime.now().replace(minute=0, second=0, microsecond=0)))
                        rain_file.write(' \n')
                        rain_file.write(' \n')

                    for i, data in enumerate(datas):
                        data_sum += data
                        result = "%.2f" % data_sum
                        nowdatatime = datetime.now().replace(
                            minute=0, second=0, microsecond=0) + timedelta(hours=i)
                        with open("rainfallWarn.txt", mode='a', encoding='utf-8') as rain_file:
                            rain_file.write(
                                '{}, {} mm/hr, ???????????? {} mm'.format(nowdatatime.strftime("%m-%d, %H:%M"), data, result))
                            rain_file.write(' \n')
                    break

        with open('rainfallWarn.txt', mode='r+', encoding='utf-8') as rain_file:   # ?????????????????????????????????
            data = rain_file.read()
            if data == "":
                rain_file.write("24????????????????????????????????????")
            pass

        return warningStation

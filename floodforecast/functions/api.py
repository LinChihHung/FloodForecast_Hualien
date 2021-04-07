import os
import json


class API():

    def __init__(self, path, nowDateRange, simDateRange, simRainDict, waterLevelDict):
        self.path = os.path.join(path, 'json')
        self.nowDateRange = nowDateRange
        self.simDateRange = simDateRange
        self.apiTimeDict = self.apiTime()

        self.simRainDict = simRainDict
        self.apiRainDict = self.apiRain()

        self.waterLevelDict = waterLevelDict
        self.apiWaterLevelDict = self.apiWaterLevel()

    def apiTime(self):
        self.apiTimeDict = {}
        self.apiTimeDict['predict_time'] = str(self.nowDateRange)
        self.apiTimeDict['time'] = self.simDateRange.to_native_types().tolist()

        return self.apiTimeDict

    def apiRain(self):
        apiRainDict = [{**self.apiTimeDict, **self.simRainDict}]

        rainPath = os.path.join(self.path, 'rainfall.json')
        with open(rainPath, 'w') as jsonFile:
            json.dump(apiRainDict, jsonFile)

        return apiRainDict

    def apiWaterLevel(self):
        apiWaterLevelDict = [{**self.apiTimeDict, **self.waterLevelDict}]

        waterLevelPath = os.path.join(self.path, 'waterLevel.json')
        with open(waterLevelPath, 'w') as jsonFile:
            json.dump(apiWaterLevelDict, jsonFile)

        return apiWaterLevelDict

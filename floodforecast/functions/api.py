import os
import json

class API():

    def __init__(self, nowDateRange, simDateRange, simRainDict):
        self.path = os.path.join(os.getcwd(), 'json')
        self.nowDateRange = nowDateRange
        self.simDateRange = simDateRange
        self.apiTimeDict = self.apiTime()
        
        self.simRainDict = simRainDict
        self.apiRainDict = self.apiRain()


    def apiTime(self):
        self.apiTimeDict = {}
        self.apiTimeDict['predict_time'] = str(self.nowDateRange)
        self.apiTimeDict['time'] = self.simDateRange.to_native_types().tolist()

        return self.apiTimeDict


    def apiRain(self):
        apiRainDict = [{**self.apiTimeDict, **self.simRainDict}]

        rainPath = os.path.join(self.path, 'rainfall.json')
        with open(rainPath, 'w') as json_file:
            json.dump(apiRainDict, json_file)

        return apiRainDict
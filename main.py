# from functions.timer import Timer
# from functions.hechms import HecHms
# from functions.rainfall import Rain
# from functions.hecras import HecRas
# from databases.hechms_database import _stationData
from floodforecast.functions.timer import Timer
from floodforecast.functions.rainfall import Rain
from floodforecast.functions.plotrain import PlotRain
from floodforecast.databases.rainstation_database import _stationData
from floodforecast.databases.hualienras_database import _hualienCrossSection
from floodforecast.functions.api import API
import os
import time
from flask import Flask
from datetime import datetime

def main():
    stationNameList = list(_stationData.keys())

    times = Timer()
    rain = Rain(
        stationNameList=stationNameList, nowFormat=times.nowFormat, obsFormat=times.obsFormat, simFormat=times.simFormat
    )
    rainDict = rain.rainDict
    simRainDict = rain.simRainDict

    # PlotRain(stationNameList=stationNameList, simRainDict=simRainDict,
    #      nowTime=times.nowTime, nowFormat=times.nowFormat, dateRange=times.simDateRange)    

    api = API(
        nowDateRange=times.nowDateRange, simDateRange=times.simDateRange, simRainDict=simRainDict
    )

    hualienCrossSectionList = list(_hualienCrossSection.keys())
if __name__ == '__main__':
    main()
from floodforecast.functions.timer import Timer
from floodforecast.functions.rainfall import Rain
from floodforecast.functions.plot import Plot
from floodforecast.databases.rainstation_database import _stationData
from floodforecast.databases.hualienras_database import _hualienBoundaryXS, _hualienWaterLevelXS
from floodforecast.functions.api import API
from floodforecast.functions.hechms import HecHms
from floodforecast.functions.hecras import HecRas
from floodforecast.functions.email import Email
import os
import time
from flask import Flask
from datetime import datetime


def main():
    PROJECTPATH = os.getcwd()
    stationNameList = list(_stationData.keys())

    times = Timer()
    rain = Rain(
        stationNameList=stationNameList, nowFormat=times.nowFormat, obsFormat=times.obsFormat, simFormat=times.simFormat
    )
    obsRainDict = rain.obsRainDict
    simRainDict = rain.generateSimRainDict(simUrl='QPESUMSWRF')
    # print(simRainDict)

    rainDict = rain.generateRainDict(obsRainDict, simRainDict)
    print(rainDict)
    # warningStation = rain.warningStation

    # plot = Plot(nowFormat=times.nowFormat)
    # plot.plotRain(
    #     stationNameList=stationNameList, simRainDict=simRainDict, nowTime=times.nowTime, dateRange=times.simDateRange
    # )

    # 寄發Email通知
    # 如果有測站達警戒值就發信件通知
    # if not warningStation:
    #     pass
    # else:
    #     PlotRain(
    #         stationNameList=warningStation, simRainDict=simRainDict, nowTime=times.nowTime, nowFormat=times.nowFormat, dateRange=times.simDateRange
    #     )
    # email = Email(
    #     prjPath=PROJECTPATH, nowFormat=times.nowFormat, warningStation=warningStation
    # )

    # hualienBoundaryXSList = list(_hualienBoundaryXS.keys())
    # hualienHmsModelPath = r'D:\2020_Flood_Forecasting\HualienRiver\HEC\HEC_HMS\HualienRiver_HMS_0917'
    # hecHms = HecHms(
    #     path=PROJECTPATH,
    #     stationNameList=stationNameList,
    #     crossSectionList=hualienBoundaryXSList,
    #     rainDict=rainDict,
    #     startTime=times.startTime,
    #     endTime=times.endTime,
    #     hmsModelPath=hualienHmsModelPath
    # )
    # time.sleep(3)

    # hualienRasModelPath = r'D:\2020_Flood_Forecasting\HualienRiver\HEC\HEC-RAS\0902HL'
    # hecRas = HecRas(
    #     rasModelPath=hualienRasModelPath,
    #     rasInputName='0902HL.q03',
    #     rasPrjName='0902HL.prj',
    #     boundaryXS=_hualienBoundaryXS,
    #     waterLevelXS=_hualienWaterLevelXS,
    #     resultDict=hecHms.resultsDict,
    #     startTime=times.startTime,
    #     endTime=times.endTime)
    # waterLevelDict = hecRas.waterLevelDict
    # time.sleep(3)

    # api = API(
    #     path=PROJECTPATH,
    #     nowDateRange=times.nowDateRange, simDateRange=times.simDateRange,
    #     simRainDict=simRainDict,
    #     waterLevelDict=waterLevelDict
    # )

    # print('--------------------------------------------------------------')
    # print('--------------------------------------------------------------')
    # print('')
    # print(f"Executive Time {datetime.now().strftime('%Y-%m-%d %H:%M:00')}")


if __name__ == '__main__':
    main()

    # while True:
    #     current = datetime.now()
    #     # print(current.minute)
    #     if current.minute == 10 or current.minute == 30 or current.minute == 50:
    #         main()
    #         time.sleep(5*60)

from pydsstools.heclib.dss import HecDss
from pydsstools.core import TimeSeriesContainer
import os
import numpy as np
# from ..functions.hmsrun import hmsrun


class HecHms():
    """A class for operating hechms model"""

    def __init__(
            self, path, stationNameList, crossSectionList, rainDict,
            startTime, endTime,
            hmsModelPath, controlName='Current', rainfallFileName='rainfallHms.dss'
    ):
        self.path = path
        self.stationNameList = stationNameList
        self.crossSectionList = crossSectionList
        self.rainDict = rainDict
        self.startTime = startTime
        self.endTime = endTime
        self.hmsModelPath = hmsModelPath
        # rainfallFileName default rainfallHms.dss
        self.rainfallFileName = rainfallFileName
        self.controlName = controlName  # controlName default 'Current'
        self.gagePath, self.rainfallPath, self.controlPath, self.resultPath = self.hmssetup()
        self.hmsrain()
        self.hmsgage()
        self.hmscontrol()
        self.hmsrun()
        # self.hmsresults()

    def hmssetup(self):
        '''
        Some pre setup for hms
        1. find path of gage file from model path
        2. find path of rain file from model path
        3. find path of control file from model path and read th name of control
        4. find path of reslut file from model path according to controlName
        5. delete all data in result file 
        '''

        # list all file name in hms model path
        listDir = os.listdir(self.hmsModelPath)

        # find path of gage file from model path
        gageFileName = [i for i in listDir if i.endswith('.gage')]
        gageFilePath = os.path.join(self.hmsModelPath, gageFileName[0])

        # find path of rain file from model path
        rainfallFilePath = os.path.join(
            self.hmsModelPath, self.rainfallFileName)

        # find path of control file from model path and read th name of control
        controlFileName = [i for i in listDir if i.endswith('.control')]
        controlFilePath = os.path.join(self.hmsModelPath, controlFileName[0])

        # find path of reslut file from model path according to controlName
        resultFileName = [i for i in listDir if i == f'{self.controlName}.dss']
        resultFilePath = os.path.join(self.hmsModelPath, resultFileName[0])

        # delete all data in result file
        fid = HecDss.Open(resultFilePath)
        listPath = fid.getPathnameList(pathname='/*/*/*/*/*/*/')
        for pathname in listPath:
            fid.deletePathname(pathname)

        return gageFilePath, rainfallFilePath, controlFilePath, resultFilePath

    def pathname(
            self, location,
            group='Hualien', parameter='PRECIP-INC', interval='1HOUR', description='RainGage',
            dss=True, flow=False):
        # hec pathname = /A/B/C/D/E/F/
        # A = group, B = location, C = parameter, D = window, E = interval, F = description
        # pathname example: /Hualien/stationName/PRECIP-INC/10Nov2020 - 11Nov2020/1HOUR/RainGage/

        if dss == True and flow == False:
            # pathname for "input" dss file
            # pathname format: /A/B/C//E/F/
            # input *.dss doesn't contain D part
            pathname = f'/{group}/{location}/{parameter}//{interval}/{description}/'

        elif dss == True and flow == True:
            # pathname for "output" dss file
            # pathname format: //B/C//E/F/
            # output *.dss is create by hechms model.
            # Pathnames don't contain A and D part, parameter and description will change as well.
            parameter = 'FLOW-COMBINE'
            description = f'RUN:{self.controlName.upper()}'
            pathname = f'//{location}/{parameter}//{interval}/{description}/'

        elif dss == False and flow == False:
            # pathname for gage file
            # pathname format: /A/B/C/D/E/F/
            # *.gage contain D part in pathname, D part is the time window of rainfall
            window = ' '.join([self.startTime.strftime(
                '%d%b%Y'), '-', self.endTime.strftime('%d%b%Y')])
            pathname = f'/{group}/{location}/{parameter}/{window}/{interval}/{description}/'

        else:
            raise Exception("not the right combination")

        return pathname

    def hmsrain(self, units='MM', type='PER-CUM'):
        # input rainfall data into dss file
        for stcode in self.stationNameList:

            rainPathname = self.pathname(location=stcode, dss=True, flow=False)
            shape = len(self.rainDict[stcode])
            values = self.rainDict[stcode]

            # write data into dss file
            tsc = TimeSeriesContainer()
            tsc.pathname = rainPathname
            tsc.startDateTime = '{}:00:00'.format(
                self.startTime.strftime('%d%b%Y %H'))
            tsc.units = units
            tsc.type = type
            tsc.numberValues = shape
            tsc.values = values

            fid = HecDss.Open(self.rainfallPath)
            fid.deletePathname(tsc.pathname)
            fid.put_ts(tsc)
            ts = fid.read_ts(rainPathname)
            fid.close()

        return

    def hmsgage(self):

        with open(self.gagePath, 'r') as f:
            gageText = f.readlines()
        for stcode in self.stationNameList:
            gagePathname = self.pathname(location=stcode, dss=False)
            try:
                index = gageText.index('Gage: {}\n'.format(stcode))
                DSSFileNameIndex = next(gageText.index(
                    i) for i in gageText[index:] if i.find('DSS File Name') != -1)
                DSSPathnameIndex = next(gageText.index(
                    i) for i in gageText[index:] if i.find('DSS Pathname') != -1)
                StartTimeIndex = next(gageText.index(
                    i) for i in gageText[index:] if i.find('Start Time') != -1)
                EndTimeIndex = next(gageText.index(
                    i) for i in gageText[index:] if i.find('End Time') != -1)

                gageText[DSSFileNameIndex] = f'       DSS File Name: {self.rainfallPath}\n'
                gageText[DSSPathnameIndex] = f'       DSS Pathname: {gagePathname}\n'
                gageText[
                    StartTimeIndex] = f'       Start Time: {self.startTime.strftime("%d %B %Y, %H:00 ")}\n'
                gageText[EndTimeIndex] = f'       End Time: {self.endTime.strftime("%d %B %Y, %H:00 ")}\n'
            except:
                pass
        with open(self.gagePath, 'w') as f:
            for item in gageText:
                f.write(item)

    def hmscontrol(self):

        with open(self.controlPath, 'r') as f:
            controlText = f.readlines()

        startDateIndex = next(controlText.index(i)
                              for i in controlText if i.find('Start Date') != -1)
        startTimeIndex = next(controlText.index(i)
                              for i in controlText if i.find('Start Time') != -1)
        endDateIndex = next(controlText.index(i)
                            for i in controlText if i.find('End Date') != -1)
        endTimeIndex = next(controlText.index(i)
                            for i in controlText if i.find('End Time') != -1)

        controlText[startDateIndex] = f'     Start Date: {self.startTime.strftime("%d %B %Y")}\n'
        controlText[startTimeIndex] = f'     Start Time: {self.startTime.strftime("%H:00")}\n'
        controlText[endDateIndex] = f'     End Date: {self.endTime.strftime("%d %B %Y")}\n'
        controlText[endTimeIndex] = f'     End Time: {self.endTime.strftime("%H:00")}\n'

        with open(self.controlPath, 'w') as f:
            for item in controlText:
                f.write(item)

    def hmsresults(self):
        self.resultsDict = {}
        for crossSection in self.crossSectionList:
            try:
                resultPathname = self.pathname(
                    location=crossSection, dss=True, flow=True)
                print(resultPathname)
                start = self.startTime.strftime('%d %B %Y, %H:00 ')
                end = self.endTime.strftime('%d %B %Y, %H:00 ')

                fid = HecDss.Open(self.resultPath)
                ts = fid.read_ts(resultPathname, window=(
                    start, end), trim_missing=True)
                values = ts.values.tolist()
                self.resultsDict[crossSection] = values
            except:
                pass

            fid.close()

        return self.resultsDict

    def hmsrun(self):
        executefilePath = os.path.abspath(
            r"floodforecast\functions\hmsengine.py")
        os.chdir(r'C:\Program Files\HEC\HEC-HMS\4.5')
        os.system(r'.\HEC-HMS.cmd -script {}'.format(executefilePath))
        os.chdir(self.path)

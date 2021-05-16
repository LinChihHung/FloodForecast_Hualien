import matplotlib.pyplot as plt
import matplotlib.dates as mdate
from datetime import timedelta
from pandas import date_range
import numpy as np
from ..databases.rainstation_database import _stationData
import os


class Plot():
    def __init__(self, nowFormat):
        self.nowFormat = nowFormat
        self.imgPath = self.mkImgDir()

    def mkImgDir(self):
        # create a folder to save rainfall images
        imgPath = os.path.join(os.getcwd(), 'images', self.nowFormat)
        if os.path.exists(imgPath):
            pass
        else:
            os.mkdir(imgPath)

        return imgPath

    def plotRain(self, stationNameList, simRainDict, nowTime, dateRange):
        rainImgPath = os.path.join(self.imgPath, 'rain')
        if os.path.exists(rainImgPath):
            pass
        else:
            os.mkdir(rainImgPath)

        for stcode in stationNameList:
            simRain = simRainDict[stcode]
            cumSimRain = np.cumsum(simRain)

            fig, ax = plt.subplots(figsize=(16, 9))
            plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
            plt.rcParams['xtick.labelsize'] = 16
            plt.rcParams['ytick.labelsize'] = 16
            plt.rcParams['axes.axisbelow'] = True

            #### First axis for rainfall bar #####
            width = np.min(np.diff(mdate.date2num(dateRange)))
            if all(i <= 50 for i in simRain) is True:
                bar = ax.bar(dateRange, simRain, width=width,
                             label='降雨量', edgecolor='k')
                ax.set_yticks(np.arange(0, 55, 5))
            else:
                bar = ax.bar(dateRange, simRain, width=width,
                             label='降雨量', edgecolor='k')

            ax.set_xlabel('時間 (mm-dd hh)', fontsize=24, weight="bold")
            ax.set_ylabel("降雨量 (mm)", fontsize=24, weight="bold")
            ax.set_title('{}測站({})雨量預報'.format(_stationData[stcode]['chineseName'], stcode), fontsize=32,
                         weight="bold")
            ax.grid()

            #### Second axis for cumulative rainfall ####
            ax2 = ax.twinx()
            if all(i <= 50 for i in cumSimRain) is True:
                ax2.plot(dateRange, cumSimRain, label='累積雨量',
                         color=[0.8500, 0.3250, 0.0980], linewidth=3, linestyle='dashed')
                ax2.set_ylim(ymax=50)
            else:
                ax2.plot(dateRange, cumSimRain, label='累積雨量',
                         color=[0.8500, 0.3250, 0.0980], linewidth=3, linestyle='dashed')

            ax2.set_ylabel("累積雨量 (mm)", fontsize=24, weight="bold")
            ax2.set_ylim(ymin=0)

            # Set legend for ax & ax2
            handles1, labels1 = ax.get_legend_handles_labels()
            handles2, labels2 = ax2.get_legend_handles_labels()
            handles = [handles1[0], handles2[0]]
            labels = [labels1[0], labels2[0]]
            ax.legend(handles, labels, loc="upper left", bbox_to_anchor=(0, 1), bbox_transform=ax.transAxes,
                      fontsize=16, edgecolor='k')

            ax3 = ax.twinx()
            ax3.yaxis.set_visible(False)
            ax3.plot([], [], ' ', label='時間: {}'.format(nowTime))
            ax3.plot([], [], 'ko',
                     label='未來一小時累積雨量: {:.1f} mm'.format(cumSimRain[0]))
            ax3.plot([], [], 'ko',
                     label='未來三小時累積雨量: {:.1f} mm'.format(cumSimRain[2]))
            ax3.plot([], [], 'ko',
                     label='未來六小時累積雨量: {:.1f} mm'.format(cumSimRain[5]))
            ax3.legend(loc='upper center', bbox_to_anchor=(0, -1.1, 1, 1), fontsize=16, ncol=4, mode='expand',
                       columnspacing=1, handlelength=0.5, handletextpad=0.5, edgecolor='k')

            fig.tight_layout()

            saveName = os.path.join(
                rainImgPath, stcode+'-' + _stationData[stcode]['chineseName']
            )
            fig.savefig(f'{saveName}.jpg', dpi=330)
            plt.close(fig)

    def plotWaterLevel(self, stationNameList, obsWaterDict, simWaterDict, obsDateRange, simDateRange, xsSection):
        waterlevelImgPath = os.path.join(self.imgPath, 'waterlevel')
        if os.path.exists(waterlevelImgPath):
            pass
        else:
            os.mkdir(waterlevelImgPath)

        fig, ax = plt.subplots(figsize=(16, 9))
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        plt.rcParams['xtick.labelsize'] = 16
        plt.rcParams['ytick.labelsize'] = 16

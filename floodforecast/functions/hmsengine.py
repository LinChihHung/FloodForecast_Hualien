from hms.model import Project
from hms import Hms


myProject = Project.open(r"D:\2020_Flood_Forecasting\HualienRiver\HEC\HEC_HMS\HualienRiver_HMS_0917\HualienRiver_0917.hms")
myProject.computeRun('Current')
myProject.close()

Hms.shutdownEngine()
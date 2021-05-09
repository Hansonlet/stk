#from win32api import GetSystemMetrics
import comtypes
from comtypes.gen import STKUtil
from comtypes.gen import STKObjects
from comtypes.client import GetActiveObject
import time
import _thread
import random
import numpy as np

def modify(keplerian, a1, a2, a3, a4, a5, a6):
    # 半长轴长度
    keplerian.SizeShape.QueryInterface(STKObjects.IAgClassicalSizeShapeSemimajorAxis).SemiMajorAxis = a1
    # 偏心率
    keplerian.SizeShape.QueryInterface(STKObjects.IAgClassicalSizeShapeSemimajorAxis).Eccentricity = a2
    # degrees 倾角
    keplerian.Orientation.Inclination = a3
    # degrees 近地点
    keplerian.Orientation.ArgOfPerigee = a4
    # RANN 设置轨道位置
    keplerian.Orientation.AscNode.QueryInterface(STKObjects.IAgOrientationAscNodeRAAN).Value = a5
    # 设置卫星在该轨道中的“相位”
    keplerian.Location.QueryInterface(STKObjects.IAgClassicalLocationTrueAnomaly).Value = a6


startTime = time.time()
# init
uiApplication = GetActiveObject('STK10.Application')
uiApplication.Visible = False
root = uiApplication.Personality2
sc = root.CurrentScenario
sc2 = sc.QueryInterface(STKObjects.IAgScenario)

# 获取星座
constellationTemp = sc.Children.Item('satellites')
constellation = constellationTemp.QueryInterface(STKObjects.IAgConstellation)

# 获取赤道、南极、月背点
chidaoTemp = sc.Children.Item('chidao')
chidao = chidaoTemp.QueryInterface(STKObjects.IAgPlace)
yuebeiTemp = sc.Children.Item('yuebei')
yuebei = chidaoTemp.QueryInterface(STKObjects.IAgPlace)
nanjiTemp = sc.Children.Item('nanji')
nanji = chidaoTemp.QueryInterface(STKObjects.IAgPlace)

# 获取卫星1&2
satTemp1 = sc.Children.Item('sat1')
sat1 = satTemp1.QueryInterface(STKObjects.IAgSatellite)
satTemp2 = sc.Children.Item('sat2')
sat2 = satTemp2.QueryInterface(STKObjects.IAgSatellite)

# 获取链路
chainTemp1 = sc.Children.Item("ChainChidao")
chain1 = chainTemp1.QueryInterface(STKObjects.IAgChain)
chainTemp2 = sc.Children.Item("ChainNanji")
chain2 = chainTemp2.QueryInterface(STKObjects.IAgChain)
chainTemp3 = sc.Children.Item("ChainYuebei")
chain3 = chainTemp3.QueryInterface(STKObjects.IAgChain)

# 获取卫星1参数修改句柄
sat1.SetPropagatorType(STKObjects.ePropagatorJ4Perturbation)
J4Propagator1 = sat1.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation)
keplerian1 = J4Propagator1.InitialState.Representation.ConvertTo(STKUtil.eOrbitStateClassical).QueryInterface(STKObjects.IAgOrbitStateClassical)
keplerian1.SizeShapeType = STKObjects.eSizeShapeSemimajorAxis
keplerian1.Orientation.AscNodeType = STKObjects.eAscNodeRAAN
keplerian1.LocationType = STKObjects.eLocationTrueAnomaly

# 卫星2
sat2.SetPropagatorType(STKObjects.ePropagatorJ4Perturbation)
J4Propagator2 = sat2.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation)
keplerian2 = J4Propagator2.InitialState.Representation.ConvertTo(STKUtil.eOrbitStateClassical).QueryInterface(STKObjects.IAgOrbitStateClassical)
keplerian2.SizeShapeType = STKObjects.eSizeShapeSemimajorAxis
keplerian2.Orientation.AscNodeType = STKObjects.eAscNodeRAAN
keplerian2.LocationType = STKObjects.eLocationTrueAnomaly

# 初始化参数
banchangzhou = [6500]                                           # 3000-5000，可优化
pianxinlv = [0, 0.1, 0.2, 0.3, 0.4, 0.5]                        # 0-0.5
qingjiao = []                                                   # 0-90
jindidian = [90, 270]                                           # 0-360
shengjiaodian = [0, 60, 120, 180, 240, 300]                     # 0-360
xiangwei = [45, 90, 135, 180, 225, 270, 315]                    # 0-360
totalTime = 27 * 24 * 60 * 60 + 7 * 60 * 60                     # 2358000
txtCount = 0

# 采集最终数据
txtStr = "data" + str(txtCount) + ".txt"
myFo = open(txtStr, "w")
for i in range(100000):
    a1 = 6500
    a3 = random.random()*12.9+39.24
    a2 = np.sqrt((1-5/3*np.cos(a3/180*np.pi)*np.cos(a3/180*np.pi)))
    if(random.random()>0.5):
        a4=90
    else:
        a4=270
    a5=random.random()*360
    a6=0
    modify(keplerian1, a1,a2,a3,a4,a5,a6)
    sat1.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation).InitialState.Representation.Assign(keplerian1)
    sat1.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation).Propagate()

    aa1 = 6500
    aa3 = random.random()*12.9+39.24
    aa2 = np.sqrt((1-5/3*np.cos(aa3/180*np.pi)*np.cos(aa3/180*np.pi)))
    if(random.random()>0.5):
        aa4=90
    else:
        aa4=270
    aa5=random.random()*360
    aa6=random.random()*360
    modify(keplerian2, aa1,aa2,aa3,aa4,aa5,aa6)
    sat2.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation).InitialState.Representation.Assign(keplerian2)
    sat2.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation).Propagate()
                                        
    # calculate
    chain1.ComputeAccess()
    chain2.ComputeAccess()
    chain3.ComputeAccess()

    chainResults1 = chainTemp1.DataProviders.GetDataPrvIntervalFromPath("Complete Access").Exec(sc2.StartTime, sc2.StopTime)
    chainResults2 = chainTemp2.DataProviders.GetDataPrvIntervalFromPath("Complete Access").Exec(sc2.StartTime, sc2.StopTime)
    chainResults3 = chainTemp3.DataProviders.GetDataPrvIntervalFromPath("Complete Access").Exec(sc2.StartTime, sc2.StopTime)
    if chainResults1.DataSets.Count != 0:
        coverage1 = sum(chainResults1.DataSets.GetDataSetByName("Duration").GetValues()) / totalTime * 100
    else:
        coverage1 = 0
    if chainResults2.DataSets.Count != 0:
        coverage2 = sum(chainResults2.DataSets.GetDataSetByName("Duration").GetValues()) / totalTime * 100
    else:
        coverage2 = 0
    if chainResults3.DataSets.Count != 0:
        coverage3 = sum(chainResults3.DataSets.GetDataSetByName("Duration").GetValues()) / totalTime * 100
    else:
        coverage3 = 0 
    myFo.write("%.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.3f %.3f %.3f\n" % (a2,a3,a4,a5,aa2,aa3,aa4,aa5,aa6,coverage1,coverage2,coverage3))

    if i%5000 == 0:
        print("======================================== ", i)
        endTime = time.time()
        print((endTime-startTime)/60/60," hours passed\n")


myFo.close()        
endTime = time.time()
print("================ end of simulation ================/n", endTime-startTime/60/60, "hours passed")
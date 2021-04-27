#from win32api import GetSystemMetrics
import comtypes
from comtypes.gen import STKUtil
from comtypes.gen import STKObjects
from comtypes.client import GetActiveObject
import time
import _thread
import random

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
pianxinlv = [0, 0.15, 0.3]                                     # 0-0.4
qingjiao = [0, 25, 50, 75]                                         # 0-90
jindidian = [0, 90, 180, 270]                             # 0-360
shengjiaodian = [0, 90, 180, 270]                         # 0-360
xiangwei = [45, 135, 215]                                       # 0-360
totalTime = 27 * 24 * 60 * 60 + 7 * 60 * 60                     # 2358000
txtCount = 100

# 采集最终数据
#for a1 in banchangzhou:
a1 = 6500
for a2 in pianxinlv:
    for a3 in qingjiao:
        print("========================", a2, a3)
        txtCount = txtCount + 1
        txtStr = "data" + str(txtCount) + ".txt"
        myFo = open(txtStr, "w")
        for a4 in jindidian:
            for a5 in shengjiaodian:
                b1=a1
                b2=a2+random.random()/10
                b3=a3+random.random()*15
                b4=a4+random.random()*90
                b5=a5+random.random()*90
                b6=0
                modify(keplerian1, b1,b2,b3,b4,b5,b6)
                sat1.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation).InitialState.Representation.Assign(keplerian1)
                sat1.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation).Propagate()
                for aa2 in pianxinlv:
                    for aa3 in qingjiao:
                        for aa4 in jindidian:
                            for aa5 in shengjiaodian:
                                for aa6 in xiangwei:
                                    bb1=a1
                                    bb2=aa2+random.random()/10
                                    bb3=aa3+random.random()*15
                                    bb4=aa4+random.random()*90
                                    bb5=aa5+random.random()*90
                                    bb6=aa6+random.random()*90
                                    modify(keplerian2, bb1,bb2,bb3,bb4,bb5,bb6)
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
                                    myFo.write("%.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.3f %.3f %.3f\n" % (b2,b3,b4,b5,bb2,bb3,bb4,bb5,bb6,coverage1,coverage2,coverage3))

        endTime = time.time()
        print((endTime-startTime)/60/60," hours passed")
        print("%.2f %.2f %.2f %.2f\t\t%.2f %.2f %.2f %.2f %.2f\tdone" % (b2,b3,b4,b5,bb2,bb3,bb4,bb5,bb6))
        myFo.close()
                
endTime = time.time()
print("================ end of simulation ================/n", endTime-startTime/60/60, "hours passed")
#from win32api import GetSystemMetrics
import comtypes
from comtypes.gen import STKUtil
from comtypes.gen import STKObjects
from comtypes.client import GetActiveObject
import time

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
uiApplication.Visible = True
root = uiApplication.Personality2
sc = root.CurrentScenario
sc2 = sc.QueryInterface(STKObjects.IAgScenario)

# 获取星座，当前应为空
constellationTemp = sc.Children.Item('satellites')
constellation = constellationTemp.QueryInterface(STKObjects.IAgConstellation)

# 获取赤道、南极、月背点
chidaoTemp = sc.Children.Item('chidao')
chidao = chidaoTemp.QueryInterface(STKObjects.IAgPlace)
yuebeiTemp = sc.Children.Item('yuebei')
yuebei = chidaoTemp.QueryInterface(STKObjects.IAgPlace)
nanjiTemp = sc.Children.Item('nanji')
nanji = chidaoTemp.QueryInterface(STKObjects.IAgPlace)

# 获取卫星1,加入星座
satTemp1 = sc.Children.Item('sat1')
sat1 = satTemp1.QueryInterface(STKObjects.IAgSatellite)
satTemp2 = sc.Children.Item('sat2')
sat2 = satTemp2.QueryInterface(STKObjects.IAgSatellite)
satTemp3 = sc.Children.Item('sat3')
sat3 = satTemp3.QueryInterface(STKObjects.IAgSatellite)
# constellation.Objects.AddObject(sat1)
constellation.Objects.AddObject(sat2)
constellation.Objects.AddObject(sat3)

# 获取链路
chainTemp1 = sc.Children.Item("ChainChidao")
chain1 = chainTemp1.QueryInterface(STKObjects.IAgChain)
# chain1.Objects.AddObject(constellationTemp)
# chain1.Objects.AddObject(chidaoTemp)
chainTemp2 = sc.Children.Item("ChainYuebei")
chain2 = chainTemp2.QueryInterface(STKObjects.IAgChain)
# chain2.Objects.AddObject(constellationTemp)
# chain2.Objects.AddObject(yuebeiTemp)
chainTemp3 = sc.Children.Item("ChainNanji")
chain3 = chainTemp3.QueryInterface(STKObjects.IAgChain)
# chain3.Objects.AddObject(constellationTemp)
# chain3.Objects.AddObject(nanjiTemp)

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

# 卫星3
sat3.SetPropagatorType(STKObjects.ePropagatorJ4Perturbation)
J4Propagator3 = sat3.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation)
keplerian3 = J4Propagator3.InitialState.Representation.ConvertTo(STKUtil.eOrbitStateClassical).QueryInterface(STKObjects.IAgOrbitStateClassical)
keplerian3.SizeShapeType = STKObjects.eSizeShapeSemimajorAxis
keplerian3.Orientation.AscNodeType = STKObjects.eAscNodeRAAN
keplerian3.LocationType = STKObjects.eLocationTrueAnomaly

# 初始化参数
banchangzhou = [4737, 5237, 5737, 6237, 6737, 7237]     # 3000-6000
pianxinlv = [0, 0.1, 0.2, 0.3, 0.4, 0.5]                # 0-0.5
qingjiao = [0, 15, 30, 45, 60, 75, 90]                  # 0-90
jindidian = [0, 40, 80, 120, 160, 200, 240, 280, 320]   # 0-360
shengjiaodian = [0, 15, 30, 45, 60, 75, 90]             # 0-90
xiangwei = [0, 60, 120, 180, 240, 300]                  # 0-360
totalTime = 27*24*60*60 + 4*60*60
txtCount = 0

# 一星计算
for a1 in banchangzhou:
    for a2 in pianxinlv：
        for a3 in qingjiao:
            for a4 in jindidian:
                for a5 in shengjiaodian:
                    modify(keplerian1, a1, a2, a3, a4, a5, 0)
                    sat1.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation).InitialState.Representation.Assign(keplerian1)
                    sat1.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation).Propagate()
                    for aa1 in banchangzhou:
                        if aa1 > a1:
                            break
                        txtCount = txtCount+1
                        txtStr = "data"+str(txtCount)+".txt"
                        fo = open(txtStr, "w")
                        for aa2 in pianxinlv：
                            for aa3 in qingjiao:
                                for aa4 in jindidian:
                                    for aa5 in shengjiaodian:
                                        for aa6 in xiangwei:
                                        modify(keplerian2, aa1, aa2, aa3, aa4, aa5, aa6)
                                        sat2.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation).InitialState.Representation.Assign(keplerian2)
                                        sat2.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation).Propagate()
                                        for aaa1 in banchangzhou:
                                            if aaa1 > aa1:
                                            break
                                            for aaa2 in pianxinlv：
                                                for aaa3 in qingjiao:
                                                    for aaa4 in jindidian:
                                                        for aaa5 in shengjiaodian:
                                                            for aaa6 in xiangwei:
                                                                modify(keplerian3, aaa1, aaa2, aaa3, aaa4, aaa5, aaa6)
                                                                sat3.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation).InitialState.Representation.Assign(keplerian3)
                                                                sat3.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation).Propagate()
                                                                
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
                        fo.close()                                                          

















                    
                    
                    

                    print(coverage1)
                    print(coverage2)
                    print(coverage3)
                    print("------------------------")
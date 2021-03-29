#from win32api import GetSystemMetrics
import comtypes
from comtypes.gen import STKUtil
from comtypes.gen import STKObjects
from comtypes.client import GetActiveObject
import time

def setSatellites(constellation):
    orbitPlaneNum = 1
    satNum = 10
    numOrbitPlanes = 72
    numSatsPerPlane = 22
    hight = 550
    Inclination = 53
    
    #sat = root.CurrentScenario.Children.New(18, 'MySatellite')  # eSatellite
    satTemp = sc.Children.Item('Lunar_Sat_h_3000km11')
    sat = satTemp.QueryInterface(STKObjects.IAgSatellite)
    sat.SetPropagatorType(STKObjects.ePropagatorJ4Perturbation)
    J4Propagator = sat.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation)
    keplarian = J4Pro pagator.InitialState.Representation.ConvertTo(STKUtil.eOrbitStateClassical).QueryInterface(STKObjects.IAgOrbitStateClassical)
    
    # 半长轴长度
    keplarian.SizeShapeType = STKObjects.eSizeShapeSemimajorAxis
    keplarian.SizeShape.QueryInterface(STKObjects.IAgClassicalSizeShapeSemimajorAxis).SemiMajorAxis = hight + 3371
    # 偏心率
    keplarian.SizeShape.QueryInterface(STKObjects.IAgClassicalSizeShapeSemimajorAxis).Eccentricity = 0
    # degrees 倾角
    keplarian.Orientation.Inclination = int(Inclination)
    # degrees 近地点
    keplarian.Orientation.ArgOfPerigee = 0
    # degrees 设置轨道位置
    keplarian.Orientation.AscNodeType = STKObjects.eAscNodeRAAN
    RAAN = 360 / numOrbitPlanes * orbitPlaneNum
    keplarian.Orientation.AscNode.QueryInterface(STKObjects.IAgOrientationAscNodeRAAN).Value = RAAN
    # 设置卫星在该轨道中的“相位”
    keplarian.LocationType = STKObjects.eLocationTrueAnomaly
    trueAnomaly = 360 / numSatsPerPlane * satNum
    keplarian.Location.QueryInterface(STKObjects.IAgClassicalLocationTrueAnomaly).Value = trueAnomaly
    
    # Propagate
    sat.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation).InitialState.Representation.Assign(keplarian)
    sat.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ4Perturbation).Propagate()
    
    # 加入星座
    #constellation.Objects.AddObject(sat)

startTime = time.time()
uiApplication = GetActiveObject('STK10.Application')
uiApplication.Visible = True
root = uiApplication.Personality2
sc = root.CurrentScenario
sc2 = sc.QueryInterface(STKObjects.IAgScenario)
# 星座
constellationTemp = sc.Children.Item('satellites')
constellation = constellationTemp.QueryInterface(STKObjects.IAgConstellation)

satTemp = sc.Children.Item('Lunar_Sat_h_3000km12')
sat = satTemp.QueryInterface(STKObjects.IAgSatellite)
#constellation.Objects.AddObject(sat)

setSatellites(constellation)
chidaoTemp = sc.Children.Item('chidao')
chidao = chidaoTemp.QueryInterface(STKObjects.IAgPlace)
# 连接
chainTemp = sc.Children.Item("Chain")
chain = chainTemp.QueryInterface(STKObjects.IAgChain)
chain.Objects.AddObject(constellationTemp)
chain.Objects.AddObject(chidaoTemp)

############################################################################
# Constellations and Chains
############################################################################
splitTime = time.time()
chain.ComputeAccess()
chainResults = chainTemp.DataProviders.GetDataPrvIntervalFromPath("Complete Access").Exec(sc2.StartTime, sc2.StopTime)

durations = chainResults.DataSets.GetDataSetByName("Duration").GetValues()
startTimes = chainResults.DataSets.GetDataSetByName("Start Time").GetValues()
stopTimes = chainResults.DataSets.GetDataSetByName("Stop Time").GetValues()


#print(durations)
#print(startTimes)
#print(stopTimes)
print("\n")
print("\n")
print("\n")




    
############################################################################
# Coverage
############################################################################

# # Create coverage definition
# coverageDef = sc.Children.New(STKObjects.eCoverageDefinition, "CoverageDefinition")
# coverageDef2 = coverageDef.QueryInterface(STKObjects.IAgCoverageDefinition)

# # Set grid bounds type
# grid = coverageDef2.Grid
# grid.BoundsType = STKObjects.eBoundsCustomRegions

# # Add US shapefile to bounds
# bounds = coverageDef2.Grid.Bounds
# bounds2 = bounds.QueryInterface(STKObjects.IAgCvBoundsCustomRegions)
# #bounds2.RegionFiles.Add("C:\\Program Files\\AGI\\STK 12\\Data\\Shapefiles\\Countries\\United_States\\United_States.shp")

# # Set resolution
# grid.ResolutionType = STKObjects.eResolutionDistance
# resolution = grid.Resolution
# resolution2 = resolution.QueryInterface(STKObjects.IAgCvResolutionDistance)
# resolution2.Distance = 75

# # Add constellation as asset
# coverageDef2.AssetList.Add("Constellation/SatConstellation")
# coverageDef2.ComputeAccesses()

# # Creat  Merit.DataProviders.GetDataPrvFixedFromPath("Overall Value")
# fomResults = fomDataProvider.Exec()


# minAccessDuration = fomResults.DataSets.GetDataSetByName("Minimum").GetValues()[0]
# maxAccessDuration = fomResults.DataSets.GetDataSetByName("Maximum").GetValues()[0]
# avgAccessDuration = fomResults.DataSets.GetDataSetByName("Average").GetValues()[0]

# print("\nThe minimum coverage duration is {a:4.2f} min.".format(a=minAccessDuration))
# print("The maximum coverage duration is {a:4.2f} min.".format(a=maxAccessDuration))
# print("The average coverage duration is {a:4.2f} min.".format(a=avgAccessDuration))


# def calculateTime():
# # Print computation time
# totalTime = time.time() - startTime
# sectionTime = time.time() - splitTime
# print("--- Coverage computation: {a:4.2f} sec\t\tTotal time: {b:4.2f} sec ---".format(a=sectionTime, b=totalTime))
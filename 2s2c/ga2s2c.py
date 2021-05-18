import random
import time
import numpy as np
import matplotlib.pyplot as plt
import comtypes
from comtypes.gen import STKUtil
from comtypes.gen import STKObjects
from comtypes.client import GetActiveObject
import cProfile, pstats, io

# 火焰图
pr = cProfile.Profile()
pr.enable()

# gobal parms
item_size = 500
gen = 200
cross_rate = 0.5
variation_rate = 0.4
totalTime = 27 * 24 * 60 * 60 + 7 * 60 * 60                 # 2358000
startTime = time.time()

print("---------------- begin STK init ----------------")
# init STK
uiApplication = GetActiveObject('STK10.Application')
uiApplication.Visible = False
root = uiApplication.Personality2
sc = root.CurrentScenario
sc2 = sc.QueryInterface(STKObjects.IAgScenario)

# 获取卫星
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

# 获取卫星参数修改句柄
sat1.SetPropagatorType(STKObjects.ePropagatorJ4Perturbation)
J4Propagator1 = sat1.Propagator.QueryInterface(
    STKObjects.IAgVePropagatorJ4Perturbation)
keplerian1 = J4Propagator1.InitialState.Representation.ConvertTo(
    STKUtil.eOrbitStateClassical).QueryInterface(STKObjects.IAgOrbitStateClassical)
keplerian1.SizeShapeType = STKObjects.eSizeShapeSemimajorAxis
keplerian1.Orientation.AscNodeType = STKObjects.eAscNodeRAAN
keplerian1.LocationType = STKObjects.eLocationTrueAnomaly
sat2.SetPropagatorType(STKObjects.ePropagatorJ4Perturbation)
J4Propagator2 = sat2.Propagator.QueryInterface(
    STKObjects.IAgVePropagatorJ4Perturbation) 
keplerian2 = J4Propagator2.InitialState.Representation.ConvertTo(
    STKUtil.eOrbitStateClassical).QueryInterface(STKObjects.IAgOrbitStateClassical)
keplerian2.SizeShapeType = STKObjects.eSizeShapeSemimajorAxis
keplerian2.Orientation.AscNodeType = STKObjects.eAscNodeRAAN
keplerian2.LocationType = STKObjects.eLocationTrueAnomaly
print("---------------- finish STK init ----------------")


# def import_init_data():
#     data = []
#     fo = open("ga_good_init_data.txt", "r")
#     for line in fo:
#         line_data = line.split(" ")
#         line_data[-1] = line_data[-1][0 : -1]
#         line_data = list(map(float, line_data))
#         data.append(line_data[0 : 10])
#     fo.close()
#     np.random.shuffle(data) 
#     return data[0:item_size]


def modify(keplerian, a1, a2, a3, a4, a5, a6):
    # 半长轴长度
    keplerian.SizeShape.QueryInterface(STKObjects.IAgClassicalSizeShapeSemimajorAxis).SemiMajorAxis = a1
    # 偏心率
    keplerian.SizeShape.QueryInterface(STKObjects.IAgClassicalSizeShapeSemimajorAxis).Eccentricity = np.sqrt((1-5/3*np.cos(a3/180*np.pi)*np.cos(a3/180*np.pi)))
    # degrees 倾角
    keplerian.Orientation.Inclination = a3
    # degrees 近地点
    keplerian.Orientation.ArgOfPerigee = a4
    # RANN 设置轨道位置
    keplerian.Orientation.AscNode.QueryInterface(STKObjects.IAgOrientationAscNodeRAAN).Value = a5
    # 设置卫星在该轨道中的“相位”
    keplerian.Location.QueryInterface(STKObjects.IAgClassicalLocationTrueAnomaly).Value = a6


def cal(group, scores):
    # todo xzh
    for i in range(item_size):
        # 调整
        modify(keplerian1, 6500, 0, group[i][0], group[i][1], group[i][2], 0)
        sat1.Propagator.QueryInterface(
            STKObjects.IAgVePropagatorJ4Perturbation).InitialState.Representation.Assign(keplerian1)
        sat1.Propagator.QueryInterface(
            STKObjects.IAgVePropagatorJ4Perturbation).Propagate()
        modify(keplerian2, 6500, 0, group[i][3], group[i][4], group[i][5], group[i][6])
        sat2.Propagator.QueryInterface(
            STKObjects.IAgVePropagatorJ4Perturbation).InitialState.Representation.Assign(keplerian2)
        sat2.Propagator.QueryInterface(
            STKObjects.IAgVePropagatorJ4Perturbation).Propagate()

        # 计算
        chain1.ComputeAccess()
        chain2.ComputeAccess()
        chain3.ComputeAccess()
        chainResults1 = chainTemp1.DataProviders.GetDataPrvIntervalFromPath(
            "Complete Access").Exec(sc2.StartTime, sc2.StopTime)
        chainResults2 = chainTemp2.DataProviders.GetDataPrvIntervalFromPath(
            "Complete Access").Exec(sc2.StartTime, sc2.StopTime)
        chainResults3 = chainTemp3.DataProviders.GetDataPrvIntervalFromPath(
            "Complete Access").Exec(sc2.StartTime, sc2.StopTime)
        if chainResults1.DataSets.Count != 0:
            coverage1 = sum(chainResults1.DataSets.GetDataSetByName(
                "Duration").GetValues()) / totalTime * 100
        else:
            coverage1 = 0
        if chainResults2.DataSets.Count != 0:
            coverage2 = sum(chainResults2.DataSets.GetDataSetByName(
                "Duration").GetValues()) / totalTime * 100
        else:
            coverage2 = 0
        if chainResults3.DataSets.Count != 0:
            coverage3 = sum(chainResults3.DataSets.GetDataSetByName(
                "Duration").GetValues()) / totalTime * 100
        else:
            coverage3 = 0

        # 得分
        scores[i] = coverage1 + coverage2 + coverage3
    return scores

def cal_once(group):
    # 调整
    modify(keplerian1, 6500, 0, group[0], group[1], group[2], 0)
    sat1.Propagator.QueryInterface(
        STKObjects.IAgVePropagatorJ4Perturbation).InitialState.Representation.Assign(keplerian1)
    sat1.Propagator.QueryInterface(
        STKObjects.IAgVePropagatorJ4Perturbation).Propagate()
    modify(keplerian2, 6500, 0, group[3], group[4], group[5], group[6])
    sat2.Propagator.QueryInterface(
        STKObjects.IAgVePropagatorJ4Perturbation).InitialState.Representation.Assign(keplerian2)
    sat2.Propagator.QueryInterface(
        STKObjects.IAgVePropagatorJ4Perturbation).Propagate()

    # 计算
    chain1.ComputeAccess()
    chain2.ComputeAccess()
    chain3.ComputeAccess()
    chainResults1 = chainTemp1.DataProviders.GetDataPrvIntervalFromPath(
        "Complete Access").Exec(sc2.StartTime, sc2.StopTime)
    chainResults2 = chainTemp2.DataProviders.GetDataPrvIntervalFromPath(
        "Complete Access").Exec(sc2.StartTime, sc2.StopTime)
    chainResults3 = chainTemp3.DataProviders.GetDataPrvIntervalFromPath(
        "Complete Access").Exec(sc2.StartTime, sc2.StopTime)
    if chainResults1.DataSets.Count != 0:
        coverage1 = sum(chainResults1.DataSets.GetDataSetByName(
            "Duration").GetValues()) / totalTime * 100
    else:
        coverage1 = 0
    if chainResults2.DataSets.Count != 0:
        coverage2 = sum(chainResults2.DataSets.GetDataSetByName(
            "Duration").GetValues()) / totalTime * 100
    else:
        coverage2 = 0
    if chainResults3.DataSets.Count != 0:
        coverage3 = sum(chainResults3.DataSets.GetDataSetByName(
            "Duration").GetValues()) / totalTime * 100
    else:
        coverage3 = 0

    # 得分
    score = coverage1 + coverage2 + coverage3
    return score


def init():
    print("---------------- begin GA init ----------------")
    group = [[0 for col in range(7)] for row in range(item_size)]
    for i in range(item_size):
        while 1:
            # 半长轴 6500
            # 偏心率 0 ~ 0.61
            # 倾角,39.24~52.14
            group[i][0] = random.random()*12.9+39.24
            group[i][3] = random.random()*12.9+39.24
            # 近地点,0-180
            if random.random()>0.5:
                group[i][1] = 90
            else:
                group[i][1] = 270
            if random.random()>0.5:
                group[i][4] = 90
            else:
                group[i][4] = 270
            # 升交点,0-360
            group[i][2] = random.random()*360
            group[i][5] = random.random()*360
            # 相位，0-360
            group[i][6] = random.random()*360
            break

    # group = import_init_data()
    scores = [0 for col in range(item_size)]
    scores = cal(group, scores)
    print("==== init scores:", scores)

    print("---------------- finish GA init ----------------")
    return [group, scores]


def choose(group, scores):
    new_group = [[0 for col in range(7)] for row in range(item_size)]
    p_choose = [0 for col in range(item_size)]
    min_scores = min(scores)
    for i in range(item_size):
        scores[i] -= min_scores
    sum_score = sum(scores)
    accumulate = 0
    # 轮盘 init
    for i in range(item_size):
        accumulate += scores[i]
        p_choose[i] = accumulate / sum_score

    # 轮盘 do
    for i in range(item_size-2):
        rand_num = random.random()
        for j in range(item_size):
            if rand_num <= p_choose[j]:
                new_group[i][:] = group[j][:]
                break

    # 保留最优解，一个不动，两个参与交叉变异
    best_item = group[scores.index(max(scores))][:]
    new_group[item_size-1][:] = best_item
    new_group[item_size-2][:] = best_item
    return [best_item, new_group]


def cross(group):
    for i in range(int(item_size/2)):
        if random.random()>cross_rate:
            continue
        num_a = i*2
        num_b = i*2+1
        temp_pos1 = random.randint(0, 6)
        temp_pos2 = random.randint(0, 6)
        pos1 = min(temp_pos1, temp_pos2)
        pos2 = max(temp_pos1, temp_pos2)

        temp = group[num_a][pos1:pos2+1]
        group[num_a][pos1:pos2+1] = group[num_b][pos1:pos2+1]
        group[num_b][pos1:pos2+1] = temp
    return group


def variation(group):
    times = int(item_size * variation_rate)
    for i in range(times):
        num = random.randint(0, item_size-1)
        pos = random.randint(0, 6)
        if (pos == 0 | pos == 3):
            group[num][pos] = random.random()*13+39.24
        elif (pos == 1 | pos == 4):
            group[num][pos] = (group[num][pos]+180) % 360
        elif (pos == 2 | pos == 5):
            group[num][pos] = random.random()*360
        elif (pos == 6):
            group[num][pos] = random.random()*360

    return group

def main_ga():
    [group, scores] = init()
    best_scores = [0 for col in range(gen+1)]
    ave_scores = [0 for col in range(gen+1)]
    best_items = [[0 for col in range(7)] for row in range(gen+1)]
    best_scores[0] = max(scores)
    ave_scores[0] = np.mean(scores)
    best_items[0][:] = group[scores.index(max(scores))][:]
    print("---------------- begin GA ----------------")
    for i in range(gen):
        print(i, "================================================")
        # 选择
        [best_item, group] = choose(group, scores)
        # 交叉
        group = cross(group)
        # 变异
        group = variation(group)
        # take best
        group[item_size-1][:] = best_item
        # 适应度
        scores = cal(group, scores)
        # record & print
        best_scores[i+1] = max(scores)
        ave_scores[i+1] = np.mean(scores)
        best_items[i+1][:] = group[scores.index(max(scores))][:]
        print(best_scores[i+1])
        print(ave_scores[i+1])
        print(best_items[i+1][:])
        print("================================================\n\n")
        print((best_scores[i+1]-ave_scores[i+1])/best_scores[i+1]*100, "%")
        if (best_scores[i+1]-ave_scores[i+1])/best_scores[i+1]*100 < 5:
            break

    endTime = time.time()
    print("time: ", endTime - startTime)
    return [best_scores, ave_scores, best_items, endTime]
    


[best_scores, ave_scores, best_items, endTime] = main_ga()

# 火焰图
# pr.disable()
# pr.dump_stats("C:\\ProgramData\\Anaconda3\\Lib\\site-packages\\__pycache__\\request.prof")
# pr.dump_stats("request.prof")
# s = io.StringIO()
# sortby = "cumtime"  # 仅适用于 3.6, 3.7 把这里改成常量了
# ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
# ps.print_stats()
# print(s.getvalue())


# plot
fig1 = plt.figure(1)
plt.plot(best_scores)
plt.xlabel('gen')
plt.ylabel('best_score')
plt.title('best_score of GA')
fig1.savefig('ga2s2c_best_ori.png')

fig2 = plt.figure(2)
plt.plot(ave_scores)
plt.xlabel('gen')
plt.ylabel('average_score')
plt.title('average_score of GA')
fig2.savefig('ga2s2c_average_ori.png')

print("================================")
print("best: ", best_scores)
print("ave: ", ave_scores)
print("items: ", best_items)
plt.show()

txtStr = "ga2s2c_ori.txt"
myFo = open(txtStr, "w")

myFo.write("time_cost\n")
myFo.write(str(endTime - startTime))
myFo.write("\n")
myFo.write("best_score\n")
myFo.write(str(best_scores))
myFo.write("\n")
myFo.write("ave_score\n")
myFo.write(str(ave_scores))
myFo.write("\n")
myFo.write("best_items\n")
myFo.write(str(best_items))

myFo.close()

# 火焰图执行步骤
# python -m cProfile -s cumtime ga.py
# cd C:\ProgramData\Anaconda3\Lib\site-packages\__pycache__
# python flameprof.cpython-37.pyc request.prof > c:\stk\requests.svg
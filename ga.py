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
gen = 150
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


def modify(keplerian, a2, a3, a4, a5):
    # 半长轴长度
    # keplerian.SizeShape.QueryInterface(STKObjects.IAgClassicalSizeShapeSemimajorAxis).SemiMajorAxis = a1
    # 偏心率
    keplerian.SizeShape.QueryInterface(STKObjects.IAgClassicalSizeShapeSemimajorAxis).Eccentricity = a2
    # degrees 倾角
    keplerian.Orientation.Inclination = a3
    # degrees 近地点
    keplerian.Orientation.ArgOfPerigee = a4
    # RANN 设置轨道位置
    keplerian.Orientation.AscNode.QueryInterface(
        STKObjects.IAgOrientationAscNodeRAAN).Value = a5
    # 设置卫星在该轨道中的“相位”
    # keplerian.Location.QueryInterface(STKObjects.IAgClassicalLocationTrueAnomaly).Value = a6


def cal(group, scores):
    for i in range(item_size):
        # 调整
        modify(keplerian1, group[i][1], group[i][2], group[i][3], group[i][4])
        sat1.Propagator.QueryInterface(
            STKObjects.IAgVePropagatorJ4Perturbation).InitialState.Representation.Assign(keplerian1)
        sat1.Propagator.QueryInterface(
            STKObjects.IAgVePropagatorJ4Perturbation).Propagate()
        modify(keplerian2, group[i][6], group[i][7], group[i][8], group[i][9])
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
    modify(keplerian1, group[1], group[2], group[3], group[4])
    sat1.Propagator.QueryInterface(
        STKObjects.IAgVePropagatorJ4Perturbation).InitialState.Representation.Assign(keplerian1)
    sat1.Propagator.QueryInterface(
        STKObjects.IAgVePropagatorJ4Perturbation).Propagate()
    modify(keplerian2, group[6], group[7], group[8], group[9])
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
    group = [[0 for col in range(10)] for row in range(item_size)]
    for i in range(item_size):
        while 1:
            # 半长轴
            group[i][0] = 6500
            group[i][5] = 6500
            # 偏心率,0-0.5
            group[i][1] = random.random()/2
            group[i][6] = random.random()/2
            # 倾角,0-90
            group[i][2] = random.random()*90
            group[i][7] = random.random()*90
            # 近地点,0-180
            group[i][3] = random.random()*180
            group[i][8] = random.random()*180
            # 升交点,0-180
            group[i][4] = random.random()*180
            group[i][9] = random.random()*180
            if (i>item_size/50) | (cal_once(group[i])>210):
                break
        print(i)

    # group[0][0]=6500
    # group[0][1]=0.49
    # group[0][2]=54
    # group[0][3]=96
    # group[0][4]=1
    # group[0][5]=6500
    # group[0][6]=0.49
    # group[0][7]=60
    # group[0][8]=89
    # group[0][9]=178
    scores = [0 for col in range(item_size)]
    scores = cal(group, scores)

    print("---------------- finish GA init ----------------")
    return [group, scores]


def choose(group, scores):
    new_group = [[0 for col in range(10)] for row in range(item_size)]
    p_choose = [0 for col in range(item_size)]
    sum_score = sum(scores)
    accumulate = 0
    # 轮盘 init
    for i in range(item_size):
        accumulate += scores[i]
        p_choose[i] = accumulate / sum_score

    # 轮盘 do
    for i in range(item_size-3):
        rand_num = random.random()
        for j in range(item_size):
            if rand_num <= p_choose[j]:
                new_group[i][:] = group[j][:]
                break

    # 保留最优解，一个不动，两个参与交叉变异
    new_group[item_size-1][:] = group[scores.index(max(scores))][:]
    new_group[item_size-2][:] = group[scores.index(max(scores))][:]
    new_group[item_size-3][:] = group[scores.index(max(scores))][:]
    # new_group[item_size-4][:] = group[scores.index(max(scores))][:]
    # new_group[item_size-5][:] = group[scores.index(max(scores))][:]
    return new_group


def cross(group):
    times = int(item_size / 100 * 40)
    for i in range(times):
        num_a = random.randint(0, item_size-2)
        num_b = random.randint(0, item_size-2)
        times_per_cross = random.randint(1, 2)
        for j in range(times_per_cross):
            pos = random.randint(0, 9)
            temp = group[num_a][pos]
            group[num_a][pos] = group[num_b][pos]
            group[num_b][pos] = temp
    return group


def variation(group):
    times = int(item_size / 100 * 40)
    for i in range(times):
        num = random.randint(0, item_size-2)
        pos = random.randint(0, 9)
        if (pos == 0) | (pos == 5):
            continue
        elif (pos == 1) | (pos == 6):
            group[num][pos] = random.random()/2
        elif (pos == 2) | (pos == 7):
            group[num][pos] = random.random()*90
        elif (pos == 3) | (pos == 8):
            group[num][pos] = random.random()*180
        elif (pos == 4) | (pos == 9):
            group[num][pos] = random.random()*180
    return group

def main_ga():
    [group, scores] = init()
    best_scores = [0 for col in range(gen+1)]
    ave_scores = [0 for col in range(gen+1)]
    best_items = [[0 for col in range(10)] for row in range(gen+1)]
    best_scores[0] = max(scores)
    ave_scores[0] = np.mean(scores)
    best_items[0][:] = group[scores.index(max(scores))][:]
    print("---------------- begin GA ----------------")
    for i in range(gen):
        print(i, "================================================")
        # 这里可以强行传一下最优的
        # 选择
        group = choose(group, scores)
        # 交叉
        group = cross(group)
        # 变异
        group = variation(group)
        # 适应度
        scores = cal(group, scores)
        best_scores[i+1] = max(scores)
        ave_scores[i+1] = np.mean(scores)
        best_items[i+1][:] = group[scores.index(max(scores))][:]
        print(best_scores[i+1])
        print(ave_scores[i+1])
        print(best_items[i+1][:])

    endTime = time.time()
    print("time: ", endTime - startTime)
    return [best_scores, ave_scores, best_items]

    

    


[best_scores, ave_scores, best_items] = main_ga()

# 火焰图
pr.disable()
pr.dump_stats("C:\\ProgramData\\Anaconda3\\Lib\\site-packages\\__pycache__\\request.prof")
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
fig1.savefig('best.png')

fig2 = plt.figure(2)
plt.plot(ave_scores)
plt.xlabel('gen')
plt.ylabel('average_score')
plt.title('average_score of GA')
fig2.savefig('average.png')

print("================================")
print("best: ", best_scores)
print("ave: ", ave_scores)
print("items: ", best_items)
plt.show()



# 火焰图执行步骤
# python -m cProfile -s cumtime ga.py
# cd C:\ProgramData\Anaconda3\Lib\site-packages\__pycache__
# python flameprof.cpython-37.pyc request.prof > c:\stk\requests.svg
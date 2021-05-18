import random
import time
import numpy as np
import matplotlib.pyplot as plt
import os
import tensorflow as tf
from tensorflow.keras.models import load_model

# gobal parms
item_size = 500
gen = 200
cross_rate = 0.5
variation_rate = 0.4
totalTime = 27 * 24 * 60 * 60 + 7 * 60 * 60                 # 2358000
startTime = time.time()

# load dnn
model = load_model('3s3c.h5')
print("---------------- finished import dnn ----------------")


def cal(group, scores):
    group_to_cal = [[0 for col in range(14)] for row in range(item_size)]
    # 调整
    for i in range(item_size):
        group_to_cal[i][0]= np.sqrt((1-5/3*np.cos(group[i][0]/180*np.pi)*np.cos(group[i][0]/180*np.pi)))
        group_to_cal[i][1] = group[i][0]
        group_to_cal[i][2] = group[i][1]
        group_to_cal[i][3] = group[i][2]
        group_to_cal[i][4] = np.sqrt((1-5/3*np.cos(group[i][3]/180*np.pi)*np.cos(group[i][3]/180*np.pi)))
        group_to_cal[i][5] = group[i][3]
        group_to_cal[i][6] = group[i][4]
        group_to_cal[i][7] = group[i][5]
        group_to_cal[i][8] = group[i][6]
        group_to_cal[i][9] = np.sqrt((1-5/3*np.cos(group[i][7]/180*np.pi)*np.cos(group[i][7]/180*np.pi)))
        group_to_cal[i][10] = group[i][7]
        group_to_cal[i][11] = group[i][8]
        group_to_cal[i][12] = group[i][9]
        group_to_cal[i][13] = group[i][10]
    # 计算
    group_to_cal = np.array(group_to_cal)
    scores_np = model.predict(group_to_cal)
    scores = [0 for col in range(item_size)]
    for i in range(item_size):
        scores[i] = scores_np[i]
    return scores


def init():
    print("---------------- begin GA init ----------------")
    group = [[0 for col in range(11)] for row in range(item_size)]
    for i in range(item_size):
        while 1:
            # 半长轴 6500
            # 偏心率 0 ~ 0.61
            # 倾角,39.24~52.14
            group[i][0] = random.random()*12.9+39.24
            group[i][3] = random.random()*12.9+39.24
            group[i][7] = random.random()*12.9+39.24
            # 近地点,0-180
            if random.random()>0.5:
                group[i][1] = 90
            else:
                group[i][1] = 270
            if random.random()>0.5:
                group[i][4] = 90
            else:
                group[i][4] = 270
            if random.random()>0.5:
                group[i][8] = 90
            else:
                group[i][8] = 270
            # 升交点,0-360
            group[i][2] = random.random()*360
            group[i][5] = random.random()*360
            group[i][9] = random.random()*360
            # 相位，0-360
            group[i][6] = random.random()*360
            group[i][10] = random.random()*360
            break


    scores = [0 for col in range(item_size)]
    scores = cal(group, scores)
    print("==== init scores:", scores)

    print("---------------- finish GA init ----------------")
    return [group, scores]


def choose(group, scores):
    new_group = [[0 for col in range(11)] for row in range(item_size)]
    p_choose = [0 for col in range(item_size)]
    sum_score = sum(scores)
    accumulate = 0
    # 轮盘 init
    for i in range(item_size):
        accumulate += scores[i]
        p_choose[i] = accumulate / sum_score

    # 轮盘 do
    for i in range(item_size):
        rand_num = random.random()
        for j in range(item_size):
            if rand_num <= p_choose[j]:
                new_group[i][:] = group[j][:]
                break

    # 保留最优解
    best_item = group[scores.index(max(scores))][:]
    new_group[0][:] = best_item
    return [best_item, new_group]


def cross(group):
    for i in range(int(item_size/2)):
        if random.random()>cross_rate:
            continue
        num_a = i*2
        num_b = i*2+1
        temp_pos1 = random.randint(0, 10)
        temp_pos2 = random.randint(0, 10)
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
        pos = random.randint(0, 10)
        if (pos == 0 | pos == 3 | pos == 7 ):
            group[num][pos] = random.random()*13+39.24
        elif (pos == 1 | pos == 4 | pos == 8):
            group[num][pos] = (group[num][pos]+180) % 360
        elif (pos == 2 | pos == 5 | pos == 9):
            group[num][pos] = random.random()*360
        elif (pos == 6 | pos == 10):
            group[num][pos] = random.random()*360

    return group

def main_ga():  
    [group, scores] = init()
    best_scores = [0 for col in range(gen+1)]
    ave_scores = [0 for col in range(gen+1)]
    best_items = [[0 for col in range(11)] for row in range(gen+1)]
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
    best_scores_to_print = [0 for col in range(gen+1)]
    for i in range(gen+1):
        best_scores_to_print[i] = float(best_scores[i])
    return [best_scores_to_print, ave_scores, best_items, endTime, group]

    

[best_scores, ave_scores, best_items, endTime, group] = main_ga()

# plot
fig1 = plt.figure(1)
plt.plot(best_scores)
plt.xlabel('gen')
plt.ylabel('best_score')
plt.title('best_score of GA')
fig1.savefig('ga3s3c_best_fore.png')

fig2 = plt.figure(2)
plt.plot(ave_scores)
plt.xlabel('gen')
plt.ylabel('average_score')
plt.title('average_score of GA')
fig2.savefig('ga3s3c_average_fore.png')

print("================================")
print("best: ", best_scores)
# print("ave: ", ave_scores)
# print("items: ", best_items)
plt.show()

txtStr = "ga3s3c_fore.txt"
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
myFo.write("best_item\n")
myFo.write(str(best_items))
myFo.write("\n")
myFo.write("group\n")
myFo.write(str(group))
myFo.close()

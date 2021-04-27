import tensorflow as tf
import os
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import regularizers

def import_data():
    path = "./data/"
    files = os.listdir(path)
    train = []
    label = []
    training_data = []
    training_label = []
    test_data = []
    test_label = []
    for file in files:
        file = path + file
        fo = open(file, "r")
        for line in fo:
            line_data = line.split(" ")
            line_data[-1] = line_data[-1][0 : -1]
            line_data = list(map(float, line_data))
            line_data[0]=line_data[1]
            line_data[1]=line_data[2]
            line_data[2]=line_data[3]
            line_data[3]=line_data[4]
            line_data[4]=line_data[6]
            line_data[5]=line_data[7]
            line_data[6]=line_data[8]
            line_data[7]=line_data[9]

            line_data[10] = line_data[10]+line_data[11]+line_data[12]
            
            if line_data[0]==0.2:
                test_data.append(line_data[0 : 8])
                test_label.append(line_data[10])
            else:
                training_data.append(line_data[0 : 8])
                training_label.append(line_data[10])
            # train.append(line_data[0 : 8])
            # label.append(line_data[10])
            # if(line_data[10]>210)&(line_data[10]<220):
            #     myFo.write("%d %.1f %d %d %d %d %.1f %d %d %d\n" % (line_data[0], line_data[1],line_data[2],line_data[3],line_data[4],line_data[5],line_data[6],line_data[7],line_data[8],line_data[9]))
            #     num1+=1
            # if(line_data[10]>230):
            #     num+=1
        fo.close()
    # np.random.shuffle(train)
    # np.random.shuffle(label)
    # train_amount = round(len(train)*0.9)
    # training_data = train[0 : train_amount]
    # training_label = label[0 : train_amount]
    # test_data = train[train_amount : len(train)]
    # test_label = label[train_amount : len(label)]
    return training_data, training_label, test_data, test_label



training_data = []
training_label = []
test_data = []
test_label = []
[training_data, training_label, test_data, test_label] = import_data()
training_data = np.array(training_data)
training_label = np.array(training_label)
test_data = np.array(test_data)
test_label = np.array(test_label)

print(training_data[0])
print(training_data[1])
print(training_data[2])
print(training_label[0])
print(training_label[1])
print(training_label[2])
print("================================")
print("label max:", max(training_label), max(test_label))
print("label min:", min(training_label), min(test_label))
print("================================")
print("load ", len(training_data), " training data")
print("load ", len(training_label), " training label")
print("load ", len(test_data), " test data")
print("load ", len(test_label), " test label")
print("================================")
print("data: ", training_data[1])
print("label: ", training_label[1])

# nerual network
model = Sequential()
model.add(Dense(units=16, activation='relu', input_dim=8))#kernel_regularizer=regularizers.l2(0.1)
for i in range(3):
      model.add(Dense(units=64, activation='relu'))
#     model.add(tf.keras.layers.Dropout(0.5))
model.add(Dense(units=8, activation='relu'))
model.add(Dense(units=1, activation='linear'))
model.compile(optimizer='adam', loss='mse', metrics=['mae']) 

history = model.fit(training_data, training_label, epochs=100, batch_size=64, verbose=1)# 
# validation_data=(test_data,test_label), validation_freq=1) 
# print(model.summary())
print("===================================================")
print(model.predict(test_data))

loss_and_metrics = model.evaluate(test_data, test_label, batch_size=32)
fore_data = model.predict(test_data, batch_size=32)  # 通过predict函数输出网络的预测值

fig1=plt.figure(1) # 图像1显示测试数据的房价和网络利用测试数据得到的预测房价
plt.plot(test_label, label='real data')
plt.plot(fore_data, label='forecasting data')
plt.xlabel('epochs')
plt.ylabel('housing price')
plt.title('predict housing price')
plt.legend()
fig1.savefig('f1.png')

fig2=plt.figure(2) # 图像2显示网络训练过程中的损失值变化
plt.plot(history.history['loss'])
plt.title('loss')
fig2.savefig('f2.png')

fig3=plt.figure(3) # 图像3显示网络训练过程中的绝对值误差变化
plt.plot(history.history['mean_absolute_error'])
plt.title('mean absolute error')
fig3.savefig('f3.png')
plt.show()#导出输入的形状等于上一层输出的形状

import tensorflow as tf
import os
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import regularizers
import random

def import_data():
    path = "./forzen_data_3s1c/"
    files = os.listdir(path)
    train = []
    label = []
    num=0
    for file in files:
        file = path + file
        fo = open(file, "r")
        for line in fo:
            line_data = line.split(" ")
            line_data[-1] = line_data[-1][0 : -1]
            line_data = list(map(float, line_data))

            line_data[6] = line_data[6]+line_data[7]+line_data[8]
            train.append(line_data[0 : 6])
            label.append(line_data[6])
            if(line_data[6]>270):
                 num+=1
        fo.close()
    # np.random.shuffle(train)
    # np.random.shuffle(label)
    print("better than 270: ", 100*num/len(train), "%\n")
    train_amount = round(len(train)*0.5)
    training_data = train[0 : train_amount]
    training_label = label[0 : train_amount]
    test_data = train[train_amount : len(train)]
    test_label = label[train_amount : len(label)]
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


print("================================")
print("label max:", max(training_label), max(test_label))
print("label min:", min(training_label), min(test_label))
print("================================")
print("load ", len(training_data), " training data")
print("load ", len(training_label), " training label")
print("load ", len(test_data), " test data")
print("load ", len(test_label), " test label")
print("================================")
print("data: ", training_data[0])
print("label: ", training_label[0])
print("================================")


# nerual network
model = Sequential()
model.add(Dense(units=256, activation='relu', input_dim=6))#kernel_regularizer=regularizers.l2(0.1)
for i in range(2):
      model.add(Dense(units=256, activation='relu'))
    #   model.add(tf.keras.layers.Dropout(0.5))
model.add(Dense(units=1, activation='linear'))
model.compile(optimizer='adam', loss='mse', metrics=['mape','mae']) 

history = model.fit(training_data, training_label, epochs=200,  batch_size=64, verbose=1)# 
# validation_data=(test_data,test_label), validation_freq=1) 
# print(model.summary())
print("===================================================")
print(model.predict(test_data))

loss_and_metrics = model.evaluate(test_data, test_label, batch_size=32)
fore_data = model.predict(test_data, batch_size=32)  # 通过predict函数输出网络的预测值

# record
myFo = open("3s1c_dnn_record", "w")
myFo.write("loss_and_metrics\n")
myFo.write(str(loss_and_metrics))
myFo.write("\nhistory mspe\n")
myFo.write(str(history.history['mean_absolute_percentage_error']))
myFo.close()

fig1=plt.figure(1)
plt.plot(history.history['mean_absolute_percentage_error'])
plt.xlabel('迭代次数')
plt.ylabel('mspe')
plt.title('mean absolute percentage error')
fig1.savefig('3s3c_mspe.png')
plt.show()

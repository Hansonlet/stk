import tensorflow as tf
import os
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import regularizers
import random
import time

def import_data():
    path = "./3s3c_data/"
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

            line_data[14] = line_data[14]+line_data[15]+line_data[16]
            train.append(line_data[0 : 14])
            label.append(line_data[14])
            if(line_data[14]>290):
                 num+=1
        fo.close()
    # np.random.shuffle(train)
    # np.random.shuffle(label)
    train_amount = 10000 * 10
    test_amount = int(train_amount/4)
    training_data = train[0 : train_amount]
    training_label = label[0 : train_amount]
    test_data = train[train_amount : train_amount+test_amount]
    test_label = label[train_amount : train_amount+test_amount]
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
model.add(Dense(units=256, activation='relu', input_dim=14))#kernel_regularizer=regularizers.l2(0.1)
for i in range(2):
      model.add(Dense(units=256, activation='relu'))
    #   model.add(tf.keras.layers.Dropout(0.5))
model.add(Dense(units=1, activation='linear'))
model.compile(optimizer='adam', loss='mse', metrics=['mape','mae']) 

startTime = time.time()
history = model.fit(training_data, training_label, epochs=200,  batch_size=64, verbose=1)# 
endTime = time.time()
print("================ time cost: ", endTime-startTime)
# validation_data=(test_data,test_label), validation_freq=1) 
# print(model.summary())
print("===================================================")
print(model.predict(test_data))

loss_and_metrics = model.evaluate(test_data, test_label, batch_size=32)
fore_data = model.predict(test_data, batch_size=32)  # 通过predict函数输出网络的预测值

# record
model.save("3s3c.h5")

myFo = open("3s3c_dnn_record", "w")
myFo.write("loss_and_metrics\n")
myFo.write(str(loss_and_metrics))
myFo.write("\nhistory mspe\n")
myFo.write(str(history.history['mean_absolute_percentage_error']))
myFo.close()

fig1=plt.figure(1)
plt.plot(history.history['mean_absolute_percentage_error'])
plt.xlabel('iterations')
plt.ylabel('mspe')
plt.title('mean absolute percentage error')
fig1.savefig('3s3c_mspe.png')
plt.show()
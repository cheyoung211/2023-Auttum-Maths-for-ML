# -*- coding: utf-8 -*-
"""CNN-Carrots-Rockets-Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Fea_eXjKIW2BjIbLVdoxcD1BKPSTIYeO

숙제 1. [단순 cnn] 2점



아래 kaggle dataset은 당근과 로켓의 사진들로 두 가지를 구분하는 것을 CNN으로 구현하는 것을 하도록 하겠습니다.



https://www.kaggle.com/datasets/mikoajfish99/carrots-vs-rockets-image-classification



대량 300장의 사진이므로 test set 대신 validatation만 10%정도 띄어 놓고 earliy stopping 하면 좋을 것같습니다.



본 dataset에 related notebook의 confunsion matrix을 보니 90%이상의 정확도를 가진 것으로 보입니다. 그리고 해당 노트북을 참고하셔도 좋습니다.



-주석은 가능한 자세하게 써 주세요.



숙제 2. [Transfer learning] 2점



위의 dataset을 ResNet이나 VGG 등을 사용해서 숙제1번과 같은 작업을 하는 transfer learning을 진행해 보세요. 아마 좋은 결과를 얻기가 어려울 수도 있으니 fine tuning의 범위도 잘 결정해서 진행해 보세요.



* 당연히 GPU를 사용하시고, 생각보다 오래 걸릴 수도 있으니 일찍 시작해 주세요.
"""

#from google.colab import drive
#drive.mount('/content/drive')

"""#1.CNN

##Importing Module
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os.path
import torch
import tensorflow as tf

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D,BatchNormalization
from tensorflow.keras.callbacks import ModelCheckpoint,EarlyStopping

"""##Loading Datasets"""

#이미지 파일이 있는 디렉토리
directory = Path('/content/drive/MyDrive/Colab Notebooks/Images')

#이미지 파일의 경로
path = list(directory.glob('*/*.jpg'))

labels = list(map(lambda x: os.path.split(os.path.split(x)[0])[1], path))

path = pd.Series(path, name = 'Path').astype(str)
labels = pd.Series(labels, name = 'Label')

path

labels

image_df = pd.concat([path, labels], axis = 1)

image_df

"""##Image Preprocessing"""

#training set과 validation set으로 나누기
#image_dataset_from_directory를 사용하면 batchdataset으로 나옴
training, validation = tf.keras.utils.image_dataset_from_directory(
    directory, labels = 'inferred', label_mode = 'categorical',
    shuffle = True, seed = 1,
    class_names = ['Carrots','Rockets'], color_mode = 'rgb',
    validation_split = 0.1, subset = 'both')

#class_names : 라벨들
names = training.class_names
print(names)

plt.figure(figsize = (10,10))
for images, labels in training.take(1):
  for i in range(9):
    ax = plt.subplot(3,3,i+1)
    plt.imshow(images[i].numpy().astype('uint8'))
    if labels[i].numpy().astype('uint8')[0] == 0:
      tt = 'Rockets'
    else:
      tt = 'Carrots'
    plt.title(tt)
    plt.axis('off')
#이미지 몇 개 보여주기

#데이터 사이즈 확인
for image_batch, labels_batch in training:
  print(image_batch.shape)
  print(labels_batch.shape)
  break

"""##CNN Model"""

#모델 생성
#RBG 값은 0~255 사이이므로 rescaling을 이용하여 normalize
model = tf.keras.Sequential([
  tf.keras.layers.Rescaling(1./255),
  tf.keras.layers.Conv2D(32, 3, activation='relu'),
  tf.keras.layers.MaxPooling2D(),
  tf.keras.layers.Conv2D(32, 3, activation='relu'),
  tf.keras.layers.MaxPooling2D(),
  tf.keras.layers.Conv2D(32, 3, activation='relu'),
  tf.keras.layers.MaxPooling2D(),
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dense(128, activation='relu'),
  tf.keras.layers.Dropout(0.5),
  tf.keras.layers.Dense(64, activation = 'relu'),
  tf.keras.layers.Dropout(0.5),
  tf.keras.layers.Dense(32, activation = 'relu'),
  tf.keras.layers.Dense(2)
])

model.compile(loss = 'categorical_crossentropy', optimizer = 'adam')

#모델 저장 경로 및 earlystop 설정
model_path = '/Carror-Rocket-classification.h5'
checkpointer = ModelCheckpoint(filepath = model_path, monitor = 'val_loss',verbose = 1, mode = 'min')
early_stopping_callback = EarlyStopping(monitor = 'val_loss', mode = 'min', verbose = 1,patience = 5)

history = model.fit(
  training,
  validation_data = validation,
  epochs=30,
  callbacks = [early_stopping_callback, checkpointer]
)

model.summary()
#모델 요약

#결과 시각화
y_vloss = history.history['val_loss']
x_len = np.arange(1,1+len(y_vloss))
plt.plot(x_len, y_vloss, marker = '.', c = 'red', label = 'Validation_loss')
plt.legend(loc = 'upper right')
plt.grid()
plt.xlabel('epoch')
plt.ylabel('loss')
plt.show()

"""#2. Transfer Learning - VGG

##Importing modules
"""

from tensorflow.keras.applications import VGG16

"""##Transfer model"""

#VGG 모델 가져오기 - include_top 옵션을 False으로 설정해 신경망을 붙일 수 있도록
transfer_model = VGG16(weights = 'imagenet', include_top = False, input_shape = (256,256,3))
transfer_model.trainable = False

#VGG 모델 요약
transfer_model.summary()

"""##ANN Model"""

from keras.layers import Rescaling

#VGG 모델에 FC layer 붙이기
model1 = Sequential()
model1.add(Rescaling(1./255))
model1.add(transfer_model)
model1.add(Flatten())
model1.add(Dense(128, activation = 'relu'))
model1.add(Dropout(0.5))
model1.add(Dense(128, activation = 'relu'))
model1.add(Dropout(0.5))
model1.add(Dense(64, activation = 'relu'))
model1.add(Dropout(0.5))
model1.add(Dense(32, activation = 'relu'))
model1.add(Dropout(0.5))
model1.add(Dense(2, activation = 'sigmoid'))

model1.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
early_stopping_callback = EarlyStopping(monitor='val_loss', mode = 'min', verbose = 1,patience = 3)
history1 = model1.fit(
       training,
       epochs=20,
       validation_data = validation,
       callbacks=[early_stopping_callback, checkpointer])

#validation loss 시각화
y_vloss1 = history1.history['val_loss']
x_len1 = np.arange(len(y_vloss1))
plt.plot(x_len1, y_vloss1, marker = '.', c = 'red', label = 'Validation_loss')
plt.legend(loc = 'upper right')
plt.grid()
plt.xlabel('epoch')
plt.ylabel('loss')
plt.show()

"""# 2.Transfer Learning - ResNet
결과가 좋지 않음
"""

training, validation = tf.keras.utils.image_dataset_from_directory(
    directory, labels = 'inferred', label_mode = 'categorical',
    shuffle = True, seed = 1,
    class_names = ['Carrots','Rockets'], color_mode = 'rgb',
    validation_split = 0.1, subset = 'both')

#ResNet 불러오기
from keras.applications.resnet_v2 import ResNet50V2, ResNet101V2, ResNet152V2

#fine tunning을 할 구간 설정하기
resnet = ResNet152V2(include_top = False, weights = 'imagenet', input_shape = (256,256,3))
resnet.trainable = True
for layer in resnet.layers[:80]:
  layer.trainable =  False

#ResNet 모델 요약 - 너무 길어서 삭제
#resnet.summary()

model2 = Sequential()
model2.add(Rescaling(1./255))
model2.add(resnet)
model2.add(Flatten())
model2.add(Dense(128, activation = 'relu'))
model2.add(Dropout(0.5))
model2.add(Dense(64, activation = 'relu'))
model2.add(Dropout(0.5))
model2.add(Dense(2, activation = 'sigmoid'))

#컴파일
model2.compile(loss = 'categorical_crossentropy',optimizer = 'adam', metrics = ['accuracy'])

early_stopping_callback2 = EarlyStopping(monitor = 'val_loss', mode = 'min', verbose = 1, patience = 5)

history2 = model2.fit(
    training,
    epochs = 20,
    validation_data = validation,
    callbacks = [early_stopping_callback2]
)

#validation loss 시각화
y_vloss2 = history2.history['val_loss']
x_len2 = np.arange(len(y_vloss2))
plt.plot(x_len2, y_vloss2, marker = '.', c = 'red', label = 'Validation_loss')
plt.legend(loc = 'upper right')
plt.grid()
plt.xlabel('epoch')
plt.ylabel('loss')
plt.show()


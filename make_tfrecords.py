# -*- coding:utf-8 -*-
import tensorflow as tf
import os
import random
import math
import numpy as np
import cv2

def get_tfdata_path(tfrecords_path, split_name):
    if not os.path.exists(tfrecords_path):
        os.mkdir(tfrecords_path)
    tfrecords_filename = tfrecords_path + split_name
    return tfrecords_filename

# Helper functions for defining tf types
def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def _image_to_tfexample(image_data, height, width, depth, label):
    return tf.train.Example(features=tf.train.Features(feature={
        'image/encoded': _bytes_feature(image_data),
        # 'image/format': _bytes_feature(image_format),
        'image/height': _int64_feature(height),
        'image/width': _int64_feature(width),
        'image/depth': _int64_feature(depth),
        'image/class/label': _int64_feature(label)}))

def to_tfrecords(txt_path, tf_path,train_ratio):#
    with open(txt_path, 'r') as f:
        txt_list = f.readlines()
        #txt_list = txt_list[0:len(txt_list)]
        #random.shuffle(txt_list)
        num =len(txt_list)
        num_train = int(math.floor(train_ratio * num))
        num_test = num - num_train
        print('num_train and num_test is %d, %d'% (num_train, num_test))
        write_tf_data(num_train, num_test, txt_list, tf_path, 'train')


def write_tf_data(num_train, num_test, txt_list, tfrecords_path, split_name):
    tfrecords_filename = get_tfdata_path(tfrecords_path, split_name)
    with tf.python_io.TFRecordWriter(tfrecords_filename) as tfrecords_writer:
        if split_name == 'train':
            num_begin = 0
            num_end = num_train

        for i in range(num_begin, num_end):
            rpath = txt_list[i].split(' ')[0]
            spath = txt_list[i].split(' ')[1]
            label = 0

            data = cv2.imread(rpath)
            seg = cv2.imread(spath)
            
            data = cv2.resize(data,(128,128))
            seg = cv2.resize(seg,(128,128))
            (T, seg) = cv2.threshold(seg, 0, 255, cv2.THRESH_BINARY)
            
            if seg.max() == 255:
                data1 = np.zeros([128,128,4],dtype = np.uint8)
                data1[:,:,0] = data[:,:,2] 
                data1[:,:,1] = data[:,:,1] 
                data1[:,:,2] = data[:,:,0]
                data1[:,:,3] = seg[:,:,0]

                rows, cols, depth = data1.shape
                data_str = data1.tostring()
                example = _image_to_tfexample(data_str, rows, cols, depth, label)
                tfrecords_writer.write(example.SerializeToString())  
                print(split_name, txt_list[i])  
            else:
                print('pass!')

        print(i+1)

    
txt_path = './txt/train_txt.txt'
tf_path = './skin2018/tfrecord/'
train_ratio = 1
to_tfrecords(txt_path, tf_path, train_ratio)
        

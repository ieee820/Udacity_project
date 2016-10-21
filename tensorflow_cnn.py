from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import input_data
import argparse
import logging
import sys
import json
#import config
import os
import tensorflow as tf

log = logging.getLogger()

parser = argparse.ArgumentParser(description = "path name")	
parser.add_argument("--data_dir")
parser.add_argument("--train_file")
parser.add_argument("--test_file")
parser.add_argument("--train_label")
parser.add_argument("--test_label")
parser.add_argument("--config_file")
parser.add_argument('--train', dest='train', action='store_true')
parser.add_argument('--no_train', dest='train', action='store_false')
parser.set_defaults(train=True)
parser.add_argument("--logging_level",type=int)
parser.set_defaults(logging_level = logging.INFO)
args = parser.parse_args()
train = args.train
data_dir = args.data_dir
train_file = args.train_file
test_file = args.test_file
train_label = args.train_label
test_label = args.test_label
conf_f = args.config_file

j = input_data.read_config(conf_f)
print("it is",j)
no_classes = j['tensorflow']['no_classes']


streamhandler = logging.StreamHandler(sys.stdout)

if args.logging_level==10:
   streamhandler.setLevel(logging.INFO)
   log.setLevel(logging.INFO)
if args.logging_level==20:
   streamhandler.setLevel(logging.DEBUG)
   log.setLevel(logging.DEBUG)

filehandler = logging.FileHandler("logging")
formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

streamhandler.setFormatter(formatter)
log.addHandler(streamhandler)
#config.read_config(config_file) # config_file will be a command line argument
data_sets = input_data.read_data_sets(data_dir, no_classes,fake_data=False, one_hot=False,train_only=False, train_file=train_file, test_file=test_file,train_label=train_label,test_label=test_label)



def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')
#flags = tf.app.flags
#FLAGS = flags.FLAGS
#flags.DEFINE_string('data_dir', '/home/ubuntu/tests/', 'Directory for storing data')

#mnist = input_data.read_data_sets(FLAGS.data_dir, one_hot=True)

sess = tf.InteractiveSession()


# Create the model
x = tf.placeholder(tf.float32, [None, 784])
W = tf.Variable(tf.zeros([784, no_classes]))
b = tf.Variable(tf.zeros([no_classes]))
y = tf.nn.softmax(tf.matmul(x, W) + b)

W_conv1 = weight_variable([5, 5, 1, 32])
b_conv1 = bias_variable([32])
x_image = tf.reshape(x, [-1,28,28,1])

h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = max_pool_2x2(h_conv1)

W_conv2 = weight_variable([5, 5, 32, 64])
b_conv2 = bias_variable([64])

h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = max_pool_2x2(h_conv2)

W_fc1 = weight_variable([7 * 7 * 64, 1024])
b_fc1 = bias_variable([1024])


h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

keep_prob = tf.placeholder(tf.float32)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

W_fc2 = weight_variable([1024, no_classes])
b_fc2 = bias_variable([no_classes])

y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

# Define loss and optimizer
y_ = tf.placeholder(tf.float32, [None, no_classes])
#cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))
#train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)


cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y_conv), reduction_indices=[1]))
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
sess.run(tf.initialize_all_variables())

#you will write another function in input_data called next_batch(batch_size)


saver = tf.train.Saver()

if train:
    for i in range(3000):
	batch = data_sets.train.next_batch(50)
	if i%100 == 0:
	    saver.save(sess, 'checkpoint.chk')
	    train_accuracy = accuracy.eval(feed_dict={
	    x:batch[0], y_: batch[1], keep_prob: 1.0})
	    print("step %d, training accuracy %g"%(i, train_accuracy))
	train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})

    print("test accuracy %g"%accuracy.eval(feed_dict={
    x: data_sets.test._images, y_: data_sets.test._labels, keep_prob: 1.0}))
else:	
    ckpt = tf.train.get_checkpoint_state('checkpoint.chk')
    if ckpt and ckpt.model_checkpoint_path:
         saver.restore(sess, ckpt.model_checkpoint_path)
         #feed x's and get y
         batch_x = data_sets.train.next_batch(5)
         predictions = sess.run(y_conv, feed_dict={x: batch_x})
         print("predictions = ",predictions)

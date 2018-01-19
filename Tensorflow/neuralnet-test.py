import tensorflow as tf
import numpy as np
from tensorflow.examples.tutorials.mnist import input_data

#mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)

n_nodes_hl1 = 500
n_nodes_hl2 = 500
n_nodes_hl3 = 500


n_classes = 10
batch_size = 100

x = tf.placeholder('float', [None, 784])
y = tf.placeholder('float')

def neural_network_model(data):
    hidden_1_layer = {'weight': tf.variable(tf.random_normal([784, n_nodes_hl1])),
                      'biases': tf.variable(tf.random_normal(n_nodes_hl1))}


    hidden_2_layer = {'weight': tf.variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
                      'biases': tf.variable(tf.random_normal(n_nodes_hl2))}


    hidden_3_layer = {'weight': tf.variable(tf.random_normal([n_nodes_hl2, n_nodes_hl3])),
                      'biases': tf.variable(tf.random_normal(n_nodes_hl3))}


    output_layer = {'weight': tf.variable(tf.random_normal([n_nodes_hl3, n_classes])),
                      'biases': tf.variable(tf.random_normal(n_classes))}

    # (input_data * weights) + biases

    l1 = tf.add(tf.multiply(data, hidden_1_layer['weights']) + hiddem_1_layer['biases'])
    l1 = tf.nn.relu(l1)

    l2 = tf.add(tf.multiply(l1, hidden_2_layer['weights']) + hiddem_2_layer['biases'])
    l2 = tf.nn.relu(l2)
    
    l3 = tf.add(tf.multiply(l2, hidden_3_layer['weights']) + hiddem_3_layer['biases'])
    l3 = tf.nn.relu(l3)

    output = tf.multiply(l3, output_layer['weights']) + output_layer['biases']

    return output





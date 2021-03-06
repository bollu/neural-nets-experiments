import tensorflow as tf
from tensorflow.python import debug as tf_debug
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns

# NOTE TO SELF
# ------------

# Tensorflow uses row vectors, so I can exploit batches by using
# (?, vector_len) interpretation. Which means, when writing matmul,
# you gotta use (1, vector_len) (1 row, vector_len columns) which are
# **row vectors**.

# saves
SAVEFOLDER = 'saves/'
SAVENAME = 'linalg-model'

LOGSPATH = 'logs/'

SAVEFILEPATH = os.path.join(SAVEFOLDER, SAVENAME)

# meta variables / hyperparameters
LEARNING_RATE = 0.2
NUM_TRANING_STEPS = 1000000


# model variables
# a_i x^i
# polynomial: (x + 20)(x + 10)(x - 30)(x - 70 )
# simplified:x^4 -70x^3 - 700x^2 + 43000x + 420 000
CONSTANTS = [420000, 43000, -700, -70, 1]

INPUT_DIM = 1
HIDDEN_DIMS = [10, 10, 10, 10, 10, 10]
OUTPUT_DIM = INPUT_DIM

BATCH_SIZE = 80

def is_running_in_ipython():
    return "get_ipython" in dir()

def mk_input():
    xs = np.random.uniform(-50, 90, size=(BATCH_SIZE, INPUT_DIM))
    ys = np.zeros(shape=(BATCH_SIZE, INPUT_DIM))
    for (i, c) in enumerate(CONSTANTS):
        ys = ys + c * np.power(xs, i)

    return (xs, ys)


def mk_vars():
    # *** HACK!! refactor this to not mutate
    HIDDEN_DIMS.insert(0, INPUT_DIM)
    HIDDEN_DIMS.append(OUTPUT_DIM)

    var_weights = []
    var_biases = []

    STDDEV = 2
    MEAN = 0
    for i in range(1, len(HIDDEN_DIMS)):
        var_weights.append(tf.Variable(tf.random_normal([HIDDEN_DIMS[i - 1], HIDDEN_DIMS[i]], MEAN, STDDEV), name="hw_%s" % i))
        var_biases.append(tf.Variable(tf.random_normal([HIDDEN_DIMS[i]], MEAN, STDDEV), name="hb_%s" % i))

    return (var_weights, var_biases)


def mk_placeholders():
    x = tf.placeholder(tf.float32, [None, INPUT_DIM], name="xinput")
    y = tf.placeholder(tf.float32, [None, OUTPUT_DIM], name="yinput")

    return (x, y)


def axpy(a, x, y, i):
    with tf.name_scope("axpy_%s" % i):
        ax = tf.matmul(a, x, name="x_mul_w")
        return tf.add(ax, y, name="x_mul_w_plus_b")

def mk_nn(ph_x, var_weights, var_biases):
    current = ph_x
    for i in range(0, len(HIDDEN_DIMS) - 1):
        with tf.name_scope("layer_%s" % i):
            next = axpy(current, var_weights[i], var_biases[i], i);

            # last layer should not have relu
            if i < len(HIDDEN_DIMS) - 2:
                next = tf.nn.relu(next)
            current = next

    return current


def mk_cost(ph_y, var_y):
    errs = tf.losses.mean_squared_error(ph_y, var_y)
    return errs


def mk_optimiser(var_cost, learning_rate):
    optimizer = \
        tf.train.AdagradOptimizer(learning_rate=learning_rate).minimize(var_cost)
    return optimizer


class Plotter:
    def __init__(self):
        plt.ion()
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111)
        plt.show()

    def plot_data(self, real_xs, real_ys, train_ys):
        self.ax1.cla()
        real = self.ax1.scatter(real_xs, real_ys, alpha=0.5, label="real", color="b")
        train = self.ax1.scatter(real_xs, train_ys, alpha=0.5, label="train", color="r")
        self.ax1.legend(handles=[real, train])
        plt.pause(0.05)



def run_save_vars(saver, sess, savefolder, savepath):
    print("*** saving data...")

    if not os.path.exists(savefolder):
        os.makedirs(savefolder)

    saver.save(sess, savepath)


# if the savefolder directory exists, pull data from it
def run_restore_vars(saver, sess, savefolder, savepath):
    if os.path.exists(savefolder):
        should_restore = input("restore?>")

        if should_restore.lower() == "y":
            saver.restore(sess, savepath)

            for var in tf.global_variables():
                varval = sess.run([var])
                print("%s:\n%s\n%s\n" %
                      (var.name, "-" * len(var.name), varval))

            should_use_restore = input("use restored?>")
            if should_use_restore.lower() == "y":
                return

    print("*** unable to restore!")
    global_init = tf.global_variables_initializer()
    sess.run(global_init)


def mk_summary_writer(logs_path):
    tf.summary.FileWriter(logs_path, graph=tf.get_default_graph())


def mk_session_debug(sess):
    sess = tf_debug.LocalCLIDebugWrapperSession(sess)
    sess.add_tensor_filter("has_inf_or_nan", tf_debug.has_inf_or_nan)


if __name__ == "__main__" and not is_running_in_ipython():
    np.seterr("raise")
    if len(sys.argv) == 1:

        (var_weights, var_biases) = mk_vars()
        (ph_x, ph_y) = mk_placeholders()

        var_y = mk_nn(ph_x, var_weights, var_biases)

        var_cost = mk_cost(ph_y, var_y)
        optimizer = mk_optimiser(var_cost, LEARNING_RATE)

        saver = tf.train.Saver()

        mk_summary_writer(LOGSPATH)

        sess = tf.Session()

        with sess:

            run_restore_vars(saver, sess, SAVEFOLDER, SAVEFILEPATH)
            plotter = Plotter()
            prev_cost = None

            for i in range(NUM_TRANING_STEPS):
                (xs, ys) = mk_input()
                nn_out_ys, cost, weights, biases, _ = \
                    sess.run([var_y, var_cost, var_weights, var_biases, optimizer],
                             feed_dict={ph_x: xs, ph_y: ys})
                
                if i % 5000 == 0:
                    run_save_vars(saver, sess, SAVEFOLDER, SAVEFILEPATH)

                if i % 1000 == 0:
                    print("cost: %s" % cost)
                
                if prev_cost is None:
                    prev_cost = cost
                    
                if abs(cost - prev_cost) / cost >= 0.3:
                    plotter.plot_data(xs, ys, nn_out_ys)
                    prev_cost = cost


            run_save_vars(saver, sess, SAVEFOLDER, SAVEFILEPATH)

            weights = sess.run(var_weights)
            biases = sess.run(var_biases)

            print("final output\n%s" % ("-" * 10))
            print("eights: %s\nbiases: %s" % (weights, biases))

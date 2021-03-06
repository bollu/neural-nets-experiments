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
LEARNING_RATE = 0.02
NUM_TRANING_STEPS = 1000000


# model variables
# a_i x^i
CONSTANTS = [10, 3, 10]

STATE_UNROLL = 2

INPUT_DIM = 1
STATE_DIM = 10
OUTPUT_DIM = 1

BATCH_SIZE = 50

def is_running_in_ipython():
    return "get_ipython" in dir()

def mk_input():
    xs = np.random.uniform(-5, 5, size=(BATCH_SIZE, STATE_UNROLL, INPUT_DIM))
    ys = np.zeros(shape=(BATCH_SIZE, OUTPUT_DIM))
    for (i, c) in enumerate(CONSTANTS):
        ys = ys + c * np.power(xs[:, -1, :], i)

    return (xs, ys)


def mk_vars():
    vars = {}

    vars["input_ws"] = tf.Variable(tf.random_normal([INPUT_DIM, STATE_DIM]), name="input_ws")
    vars["input_bs"] = tf.Variable(tf.random_normal([STATE_DIM]), name="input_bs")

    vars["state_ws"] = tf.Variable(tf.random_normal([STATE_DIM, STATE_DIM]), name="state_ws")
    vars["state_bs"] = tf.Variable(tf.random_normal([STATE_DIM]), name="state_bs")


    vars["state_to_output_ws"] = tf.Variable(tf.random_normal([STATE_DIM, OUTPUT_DIM]), name="state_to_output_ws")
    vars["state_to_output_bs"] = tf.Variable(tf.random_normal([OUTPUT_DIM]), name="state_to_output_bs")

    return vars


def mk_placeholders():
    x = tf.placeholder(tf.float32, [None, STATE_UNROLL, INPUT_DIM], name="xinput")
    y = tf.placeholder(tf.float32, [None, OUTPUT_DIM], name="yinput")

    return (x, y)


def axpy(a, x, y, varname):
    with tf.name_scope("axpy_%s" % varname):
        ax = tf.matmul(a, x, name="%s_mul_w" % varname)
        return tf.add(ax, y, name="%s_mul_w_plus_b" % varname)



def mk_rnn_cell(past_state_vec, state_ws, state_bs,
                input_vec, input_ws, input_bs,
                state_to_output_ws, state_to_output_bs, i):
    with tf.name_scope("rnn_cell_%s" % i):
        input_factor = axpy(input_vec, input_ws, input_bs, "inp")

        next_state = tf.add(axpy(past_state_vec, state_ws, state_bs, "state"), input_factor)
        next_state = tf.nn.relu(next_state, name="relu_next_state_vec")

        output = axpy(next_state, state_to_output_ws, state_to_output_bs, "output")
        # output = tf.nn.softmax(output)

    return (next_state, output)

def mk_nn(ph_x, vars):
    
    var_y = None
    s = tf.zeros([1, STATE_DIM])

    for i in range(STATE_UNROLL):
        s, y = mk_rnn_cell(s, vars["state_ws"], vars["state_bs"],
                           ph_x[:, i, :], vars["input_ws"], vars["input_bs"],
                        vars["state_to_output_ws"], vars["state_to_output_bs"],
                        i + 1)
        # var_y will be the final y
        var_y = y

    assert var_y is not None

    return var_y


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

        vars = mk_vars()
        (ph_x, ph_y) = mk_placeholders()

        var_y = mk_nn(ph_x, vars)

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
                nn_out_ys, cost, _ = \
                        sess.run([var_y, var_cost, optimizer],
                                 feed_dict={ph_x: xs, ph_y: ys})

                if i % 5000 == 0:
                    run_save_vars(saver, sess, SAVEFOLDER, SAVEFILEPATH)

                if i % 1000 == 0:
                    print("f(%s) = real(%s) | ideal(%s)" %
                          (xs, nn_out_ys, ys))

                    print("cost: %s" % cost)

                if prev_cost is None:
                    prev_cost = cost

                if abs(cost - prev_cost) / cost >= 0.8:
                    plotter.plot_data(xs[:, -1, :], ys, nn_out_ys)
                    prev_cost = cost

            run_save_vars(saver, sess, SAVEFOLDER, SAVEFILEPATH)

            weights = sess.run(var_weights)
            biases = sess.run(var_biases)

            print("final output\n%s" % ("-" * 10))
            print("eights: %s\nbiases: %s" % (weights, biases))

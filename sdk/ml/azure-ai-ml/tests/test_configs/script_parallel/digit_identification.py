# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import os
import numpy as np
import argparse
import tensorflow as tf
from PIL import Image
from azureml.core import Model


def init():
    global g_tf_sess

    parser = argparse.ArgumentParser(allow_abbrev=False, description="ParallelRunStep Agent")
    parser.add_argument("--model", type=str, default=0)
    args, _ = parser.parse_known_args()

    # pull down model from workspace
    model_path = args.model

    # contruct graph to execute
    tf.reset_default_graph()
    saver = tf.train.import_meta_graph(os.path.join(model_path, "mnist-tf.model.meta"))
    g_tf_sess = tf.Session(config=tf.ConfigProto(device_count={"GPU": 0}))
    saver.restore(g_tf_sess, os.path.join(model_path, "mnist-tf.model"))


def run(mini_batch):
    print(f"run method start: {__file__}, run({mini_batch})")
    resultList = []
    in_tensor = g_tf_sess.graph.get_tensor_by_name("network/X:0")
    output = g_tf_sess.graph.get_tensor_by_name("network/output/MatMul:0")

    for image in mini_batch:
        # prepare each image
        data = Image.open(image)
        np_im = np.array(data).reshape((1, 784))
        # perform inference
        inference_result = output.eval(feed_dict={in_tensor: np_im}, session=g_tf_sess)
        # find best probability, and add to result list
        best_result = np.argmax(inference_result)
        resultList.append("{}: {}".format(os.path.basename(image), best_result))

    return resultList

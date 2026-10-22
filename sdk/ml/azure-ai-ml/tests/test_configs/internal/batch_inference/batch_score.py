import argparse
import os
from uuid import uuid4

import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image


def init():
    global g_tf_sess
    global output_folder

    # Get model from the model dir
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path")
    parser.add_argument("--scored_dataset")
    args, _ = parser.parse_known_args()
    model_path = args.model_path
    output_folder = args.scored_dataset

    # contruct graph to execute
    tf.reset_default_graph()
    saver = tf.train.import_meta_graph(os.path.join(model_path, "mnist-tf.model.meta"))
    g_tf_sess = tf.Session(config=tf.ConfigProto(device_count={"GPU": 0}))
    saver.restore(g_tf_sess, os.path.join(model_path, "mnist-tf.model"))


def run(mini_batch):
    print(f"run method start: {__file__}, run({mini_batch})")
    in_tensor = g_tf_sess.graph.get_tensor_by_name("network/X:0")
    output = g_tf_sess.graph.get_tensor_by_name("network/output/MatMul:0")
    results = []

    for image in mini_batch:
        # prepare each image
        data = Image.open(image)
        np_im = np.array(data).reshape((1, 784))
        # perform inference
        inference_result = output.eval(feed_dict={in_tensor: np_im}, session=g_tf_sess)
        # find best probability, and add to result list
        best_result = np.argmax(inference_result)
        results.append([os.path.basename(image), best_result])
    # Write the dataframe to parquet file in the output folder.
    result_df = pd.DataFrame(results, columns=["Filename", "Class"])
    print("Result:")
    print(result_df)
    output_file = os.path.join(output_folder, f"{uuid4().hex}.parquet")
    result_df.to_parquet(output_file, index=False)
    return result_df

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This module will load mlflow model and do prediction."""

import argparse
import os

from mlflow.sklearn import load_model

MODEL_NAME = "iris_model"


def init():
    print("Environment variables start ****")
    for key, val in os.environ.items():
        print(key, val)
    print("Environment variables end ****")

    parser = argparse.ArgumentParser(allow_abbrev=False, description="ParallelRunStep Agent")
    parser.add_argument("--model", type=str, default=0)
    args, _ = parser.parse_known_args()

    model_path = args.model + "/" + MODEL_NAME
    global iris_model

    iris_model = load_model(model_path)


def run(input_data):
    num_rows, num_cols = input_data.shape
    pred = iris_model.predict(input_data).reshape((num_rows, 1))

    # cleanup output
    result = input_data.drop(input_data.columns[4:], axis=1)
    result["variety"] = pred

    return result

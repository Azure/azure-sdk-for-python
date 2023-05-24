# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import json
import os
import time


from azureml.core import Run

import mlflow
import mlflow.sklearn

# Based on example:
# https://docs.microsoft.com/en-us/azure/machine-learning/how-to-train-cli
# which references
# https://github.com/Azure/azureml-examples/tree/main/cli/jobs/train/lightgbm/iris


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--model_input_path", type=str, help="Path to input model")
    parser.add_argument("--model_base_name", type=str, help="Name of the registered model")

    # parse args
    args = parser.parse_args()
    print("Path: " + args.model_input_path)
    # return args
    return args


def main(args):
    """
    Register Model Example
    """
    # Set Tracking URI
    current_experiment = Run.get_context().experiment
    tracking_uri = current_experiment.workspace.get_mlflow_tracking_uri()
    print("tracking_uri: {0}".format(tracking_uri))
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(current_experiment.name)

    # Get Run ID from model path
    print("Getting model path")
    mlmodel_path = os.path.join(args.model_input_path, "MLmodel")
    runid = ""
    with open(mlmodel_path, "r") as modelfile:
        for line in modelfile:
            if "run_id" in line:
                runid = line.split(":")[1].strip()

    # Construct Model URI from run ID extract previously
    model_uri = "runs:/{}/outputs/".format(runid)
    print("Model URI: " + model_uri)

    # Register the model with Model URI and Name of choice
    registered_name = args.model_base_name
    print(f"Registering model as {registered_name}")
    mlflow.register_model(model_uri, registered_name)


# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    main(args)

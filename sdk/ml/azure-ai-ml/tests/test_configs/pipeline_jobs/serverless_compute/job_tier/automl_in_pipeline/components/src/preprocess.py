# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import argparse
import datetime
from pathlib import Path
import yaml
from mltable import load


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--train_data", type=str)
    parser.add_argument("--validation_data", type=str)
    parser.add_argument("--preprocessed_train_data", type=str)
    parser.add_argument("--preprocessed_validation_data", type=str)
    # parse args
    args = parser.parse_args()
    print("args received ", args)
    # return args
    return args


def get_preprocessed_data(text):
    """
    Do preprocessing as needed
    Currently we are just passing text file as it is
    """
    return text


def main(args):
    """
    Preprocessing of training/validation data
    """
    train_data_path = os.path.join(args.train_data, "train.txt")
    with open(train_data_path) as f:
        train_data = f.read()
    preprocessed_train_data = get_preprocessed_data(train_data)

    # write preprocessed train txt file
    preprocessed_train_data_path = os.path.join(args.preprocessed_train_data, "train.txt")
    with open(preprocessed_train_data_path, "w") as f:
        f.write(preprocessed_train_data)

    validation_data_path = os.path.join(args.validation_data, "valid.txt")
    with open(validation_data_path) as f:
        validation_data = f.read()
    preprocessed_validation_data = get_preprocessed_data(validation_data)

    # write preprocessed validation txt file
    preprocessed_validation_data_path = os.path.join(args.preprocessed_validation_data, "valid.txt")
    with open(preprocessed_validation_data_path, "w") as f:
        f.write(preprocessed_validation_data)

    # Write MLTable yaml file as well in output folder
    # Since in this example we are not doing any preprocessing, we are just copying same yaml file from input,change it if needed

    # read and write MLModel yaml file for train data
    train_data_mltable_path = os.path.join(args.train_data, "MLTable")
    preprocessed_train_data_mltable_path = os.path.join(args.preprocessed_train_data, "MLTable")
    with open(train_data_mltable_path, "r") as file:
        yaml_file = yaml.safe_load(file)
    with open(preprocessed_train_data_mltable_path, "w") as file:
        yaml.dump(yaml_file, file)

    # read and write MLModel yaml file for validation data
    validation_data_mltable_path = os.path.join(args.validation_data, "MLTable")
    preprocessed_validation_data_mltable_path = os.path.join(args.preprocessed_validation_data, "MLTable")
    with open(validation_data_mltable_path, "r") as file:
        yaml_file = yaml.safe_load(file)
    with open(preprocessed_validation_data_mltable_path, "w") as file:
        yaml.dump(yaml_file, file)


# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    main(args)

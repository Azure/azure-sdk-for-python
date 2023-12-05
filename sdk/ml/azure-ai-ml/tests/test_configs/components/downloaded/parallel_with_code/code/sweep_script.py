import argparse
from random import random

from azureml.core import Run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lr", required=True)
    parser.add_argument("--conv_size", required=True)
    parser.add_argument("--dropout_rate", required=True)

    args = parser.parse_args()
    print("validated")
    print(args.lr)
    print(args.conv_size)
    print(args.dropout_rate)

    run = Run.get_context()
    run.log("accuracy", random())


if __name__ == "__main__":
    main()

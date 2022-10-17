import argparse

import mlflow.sklearn
import numpy as np
from sklearn.svm import SVC


def parse_args():
    parser = argparse.ArgumentParser(description="SVM example")
    parser.add_argument(
        "-c",
        type=float,
        default=1.0,
        help="SVM Cost Parameter",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    mlflow.sklearn.autolog()
    X = np.array([[-1, -1], [-3, -1], [0, 1], [1, 1], [5, 4]])
    y = np.array([0, 0, 0, 1, 1])

    # junk test data so we can log a metric. accuracy should be bad due to not many training points
    test_data = np.random.rand(10, 2)
    test_labels = np.random.randint(2, size=10)
    clf = SVC(C=args.c)
    with mlflow.start_run():
        clf.fit(X, y)
        pred = clf.predict(test_data)
        accuracy = np.sum(test_labels == pred) / 10
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_param("a_param", 1)
        mlflow.log_param("another_param", 2)


if __name__ == "__main__":
    main()

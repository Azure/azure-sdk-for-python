# coding: utf-8
import json

import lightgbm as lgb
import numpy as np
import pandas as pd
from mlflow.models.signature import infer_signature
from sklearn.metrics import mean_squared_error

try:
    import cPickle as pickle
except BaseException:
    import pickle

import argparse

import mlflow

# mlflow.lightgbm.autolog()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lr", default=0.05)
    parser.add_argument("--feature_fraction", default=0.9)
    parser.add_argument("--bagging_fraction", default=0.8)
    args = parser.parse_args()

    print("Loading data...")
    # load or create your dataset
    df_train = pd.read_csv("./binary_classification/binary.train", header=None, sep="\t")
    df_test = pd.read_csv("./binary_classification/binary.test", header=None, sep="\t")
    W_train = pd.read_csv("./binary_classification/binary.train.weight", header=None)[0]
    W_test = pd.read_csv("./binary_classification/binary.test.weight", header=None)[0]

    y_train = df_train[0]
    y_test = df_test[0]
    X_train = df_train.drop(0, axis=1)
    X_test = df_test.drop(0, axis=1)

    num_train, num_feature = X_train.shape

    # create dataset for lightgbm
    # if you want to re-use data, remember to set free_raw_data=False
    lgb_train = lgb.Dataset(X_train, y_train, weight=W_train, free_raw_data=False)
    lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train, weight=W_test, free_raw_data=False)

    # specify your configurations as a dict
    params = {
        "boosting_type": "gbdt",
        "objective": "binary",
        "metric": "binary_logloss",
        "num_leaves": 31,
        "learning_rate": args.lr,
        "feature_fraction": args.feature_fraction,
        "bagging_fraction": args.bagging_fraction,
        "bagging_freq": 5,
        "verbose": 0,
    }

    # generate feature names
    feature_name = ["feature_" + str(col) for col in range(num_feature)]

    print("Starting training...")
    # feature_name and categorical_feature
    gbm = lgb.train(
        params,
        lgb_train,
        num_boost_round=10,
        valid_sets=[lgb_train],  # eval training data
        valid_names="train",
        feature_name=feature_name,
        early_stopping_rounds=10,
        categorical_feature=[21],
    )

    print("Finished first 10 rounds...")
    # check feature name
    print("7th feature name is:", lgb_train.feature_name[6])

    print("Saving model...")
    # save model to file
    gbm.save_model("model.txt")

    print("Dumping model to JSON...")
    # dump model to JSON (and save to file)
    model_json = gbm.dump_model()

    with open("model.json", "w+") as f:
        json.dump(model_json, f, indent=4)

    # feature names
    print("Feature names:", gbm.feature_name())

    # feature importances
    print("Feature importances:", list(gbm.feature_importance()))

    print("Loading model to predict...")
    # load model to predict
    bst = lgb.Booster(model_file="model.txt")
    # can only predict with the best iteration (or the saving iteration)
    y_pred = bst.predict(X_test)
    # eval with loaded model
    print("The rmse of loaded model's prediction is:", mean_squared_error(y_test, y_pred) ** 0.5)

    print("Dumping and loading model with pickle...")
    # dump model with pickle
    with open("model.pkl", "wb") as fout:
        pickle.dump(gbm, fout)
    # load model with pickle to predict
    with open("model.pkl", "rb") as fin:
        pkl_bst = pickle.load(fin)
    # can predict with any iteration when loaded in pickle way
    y_pred = pkl_bst.predict(X_test, num_iteration=7)
    # eval with loaded model
    print("The rmse of pickled model's prediction is:", mean_squared_error(y_test, y_pred) ** 0.5)

    # continue training
    # init_model accepts:
    # 1. model file name
    # 2. Booster()
    gbm = lgb.train(params, lgb_train, num_boost_round=10, init_model="model.txt", valid_sets=lgb_eval)

    print("Finished 10 - 20 rounds with model file...")

    # decay learning rates
    # learning_rates accepts:
    # 1. list/tuple with length = num_boost_round
    # 2. function(curr_iter)
    gbm = lgb.train(
        params,
        lgb_train,
        num_boost_round=10,
        init_model=gbm,
        learning_rates=lambda iter: 0.05 * (0.99**iter),
        valid_sets=lgb_eval,
    )

    print("Finished 20 - 30 rounds with decay learning rates...")

    # change other parameters during training
    gbm = lgb.train(
        params,
        lgb_train,
        num_boost_round=10,
        init_model=gbm,
        valid_sets=lgb_eval,
        callbacks=[lgb.reset_parameter(bagging_fraction=[0.7] * 5 + [0.6] * 5)],
    )

    print("Finished 30 - 40 rounds with changing bagging_fraction...")

    # self-defined objective function
    # f(preds: array, train_data: Dataset) -> grad: array, hess: array
    # log likelihood loss
    def loglikelihood(preds, train_data):
        labels = train_data.get_label()
        preds = 1.0 / (1.0 + np.exp(-preds))
        grad = preds - labels
        hess = preds * (1.0 - preds)
        return grad, hess

    # self-defined eval metric
    # f(preds: array, train_data: Dataset) -> name: string, eval_result: float, is_higher_better: bool
    # binary error
    # NOTE: when you do customized loss function, the default prediction value is margin
    # This may make built-in evalution metric calculate wrong results
    # For example, we are doing log likelihood loss, the prediction is score before logistic transformation
    # Keep this in mind when you use the customization
    def binary_error(preds, train_data):
        labels = train_data.get_label()
        preds = 1.0 / (1.0 + np.exp(-preds))
        return "error", np.mean(labels != (preds > 0.5)), False

    gbm = lgb.train(
        params,
        lgb_train,
        num_boost_round=10,
        init_model=gbm,
        fobj=loglikelihood,
        feval=binary_error,
        valid_sets=lgb_eval,
    )

    print("Finished 40 - 50 rounds with self-defined objective function and eval metric...")

    input_sample = X_train.head(1)
    signature = infer_signature(input_sample, y_pred)

    mlflow.lightgbm.log_model(
        gbm,
        "lightgbm_artifact",
        signature=signature,
        input_example=input_sample,
        registered_model_name="lightgbm_predict",
    )

    # another self-defined eval metric
    # f(preds: array, train_data: Dataset) -> name: string, eval_result: float, is_higher_better: bool
    # accuracy
    # NOTE: when you do customized loss function, the default prediction value is margin
    # This may make built-in evalution metric calculate wrong results
    # For example, we are doing log likelihood loss, the prediction is score before logistic transformation
    # Keep this in mind when you use the customization
    def accuracy(preds, train_data):
        labels = train_data.get_label()
        preds = 1.0 / (1.0 + np.exp(-preds))
        return "accuracy", np.mean(labels == (preds > 0.5)), True


if __name__ == "__main__":
    main()

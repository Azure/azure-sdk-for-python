# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import abc
import pandas as pd


class BaseHandler(metaclass=abc.ABCMeta):

    def __init__(self, asset, test_data, prediction_data=None, ground_truth=None, **kwargs):
        self._prediction_data = None
        self.asset = asset

        test_data_df = pd.DataFrame(test_data)

        if isinstance(prediction_data, str) and prediction_data in test_data_df.columns:
            self._prediction_data = test_data_df[[prediction_data]]
            test_data_df = test_data_df.drop(prediction_data, axis=1)

        self._ground_truth = None
        if isinstance(ground_truth, str) and ground_truth in test_data_df.columns:
            self._ground_truth = test_data_df[[ground_truth]]
            test_data_df = test_data_df.drop(ground_truth, axis=1)

        self._test_data = test_data_df

        self.params_dict = kwargs.pop("params_dict", None)

    @property
    def test_data(self):
        return self._test_data

    @property
    def prediction_data(self):
        if self._prediction_data is None:
            prediction_data = self.generate_prediction_data()
            prediction_data_df = pd.DataFrame(prediction_data)
            self._prediction_data = prediction_data_df
        return self._prediction_data

    @property
    def ground_truth(self):
        return self._ground_truth

    @abc.abstractmethod
    def generate_prediction_data(self):
        """
        Abstract method to generated prediction data.
        Should be implemented by all subclasses.
        """

    def get_test_data_as_jsonl(self):
        if self.params_dict:
            return self.test_data.assign(**self.params_dict).to_dict("records")
        return self.test_data.to_dict("records")

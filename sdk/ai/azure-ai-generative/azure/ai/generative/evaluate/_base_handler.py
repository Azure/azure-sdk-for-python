# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import abc
import pandas as pd


class BaseHandler(metaclass=abc.ABCMeta):
    # pylint: disable=unused-argument
    def __init__(self, asset, test_data, prediction_data=None, ground_truth=None, **kwargs):
        self._prediction_data = None
        self._input_output_data = None
        self.asset = asset

        test_data_df = pd.DataFrame(test_data)
        if self.asset is None:
            self._input_output_data = test_data_df
            self._prediction_data = test_data_df

        if isinstance(prediction_data, str) and prediction_data in test_data_df.columns:
            self._prediction_data = test_data_df[[prediction_data]]
            test_data_df = test_data_df.drop(prediction_data, axis=1)

        self._test_data = test_data_df

        self.params_dict = kwargs.pop("params_dict", None)

    @property
    def test_data(self):
        return self._test_data

    @property
    def prediction_data(self):
        if self._prediction_data is None:
            self.execute_target()
        return self._prediction_data

    @property
    def input_output_data(self):
        if self._input_output_data is None:
            self.execute_target()
        return self._input_output_data


    @abc.abstractmethod
    def execute_target(self):
        """
        Abstract method to generated prediction data and input output data.
        Should be implemented by all subclasses.
        """

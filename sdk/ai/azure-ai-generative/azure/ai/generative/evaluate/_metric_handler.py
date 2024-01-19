# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import pandas as pd

from os import path
from typing import Dict
from promptflow import PFClient

from azure.ai.generative.evaluate._constants import TYPE_TO_KWARGS_MAPPING
from azure.ai.generative.evaluate._constants import TASK_TYPE_TO_METRICS_MAPPING
from ._utils import run_pf_flow_with_dict_list, df_to_dict_list

class MetricHandler(object):

    def __init__(
            self,
            task_type,
            prediction_data: pd.DataFrame,
            test_data,
            truth_data=None,
            prediction_data_column_name=None,
            ground_truth_column_name=None,
            metrics_mapping=None,
            metrics=None,
            type_to_kwargs=None,
            data_mapping: Dict=None,
    ):
        self.task_type = task_type
        self.prediction_data = prediction_data
        self.truth_data = truth_data
        self.test_data = test_data
        self.metrics_mapping = metrics_mapping
        self.prediction_data_column_name = prediction_data_column_name
        self.ground_truth_column_name = ground_truth_column_name
        self._metrics_mapping_to_log = {}
        self.metrics = metrics
        self._type_to_kwargs = type_to_kwargs if type_to_kwargs is not None else TYPE_TO_KWARGS_MAPPING[self.task_type]
        self.data_mapping = data_mapping

    def _get_data_for_metrics(self):
        metrics_mapping = copy.deepcopy(self.metrics_mapping)
        metrics_mapping_to_log = {}
        metrics_data = {}
        data_mapping = metrics_mapping["data_mapping"]
        data_columns = self._type_to_kwargs
        for data_column in data_columns:
            if data_column in data_mapping.keys():
                data_source = None
                if data_mapping[data_column] in self.test_data.columns.values:
                    data_source = self.test_data
                elif data_mapping[data_column] in self.prediction_data.columns:
                    data_source = self.prediction_data
                elif self.truth_data is not None and data_mapping[data_column] in self.truth_data.columns:
                    data_source = self.truth_data

                if data_column is None:
                    raise Exception(f"{data_column} data needed for metric calculation not found")

                if data_source is not None:
                    metrics_data.update(
                        {
                            data_column: data_source[data_mapping[data_column]].values.tolist()
                        }
                    )

        self._metrics_mapping_to_log = metrics_mapping_to_log

        return metrics_data
    
    def _get_data_for_pf(self) -> pd.DataFrame:
        if self.data_mapping:
            rename_map = {v: k for k, v in self.data_mapping.items()}
            return self.prediction_data.rename(columns=rename_map)
        else:
            return self.prediction_data

    def calculate_metrics(self):

        metrics_calculation_data = self._get_data_for_pf()

        metrics = self.metrics if self.metrics is not None else TASK_TYPE_TO_METRICS_MAPPING[self.task_type].DEFAULT_LIST
        
        dict_list = df_to_dict_list(metrics_calculation_data, {"metrics": metrics}) # The PF eval template expects metrics names to be passed in as a input parameter 
        
        flow_path = path.join(path.dirname(__file__), "pf_templates", "built_in_metrics")
        pf_run = run_pf_flow_with_dict_list(flow_path, dict_list)

        pf_client = PFClient()
        result_df = pf_client.get_details(pf_run.name)

        return result_df

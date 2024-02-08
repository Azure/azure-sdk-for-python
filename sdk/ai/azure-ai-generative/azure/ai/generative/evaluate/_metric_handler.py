# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import mlflow
import pandas as pd
import logging

from os import path
from typing import Dict, Optional

from azure.ai.generative.evaluate._constants import TASK_TYPE_TO_METRICS_MAPPING, CHAT
from ._user_agent import USER_AGENT

from ._utils import run_pf_flow_with_dict_list, df_to_dict_list, wait_for_pf_run_to_complete

LOGGER = logging.getLogger(__name__)

NODE_LIST_BY_TASK = {
    "qa": ["gpt_coherence", "gpt_similarity", "gpt_relevance", "gpt_fluency", "gpt_groundedness"],
    "chat": ["evaluate_chat_rag", "evaluate_coherence_fluency"]
}


class MetricHandler(object):

    def __init__(
            self,
            task_type,
            prediction_data: pd.DataFrame,
            input_output_data: pd.DataFrame,
            test_data,
            metrics_mapping=None,
            metrics=None,
            data_mapping: Optional[Dict]=None,
    ):
        self.task_type = task_type
        self.prediction_data = prediction_data
        self.input_output_data = input_output_data
        self.test_data = test_data
        self.metrics_mapping = metrics_mapping
        self.metrics = metrics
        self.data_mapping = data_mapping
    
    def _get_data_for_pf(self) -> pd.DataFrame:
        if self.data_mapping:
            rename_map = {v: k for k, v in self.data_mapping.items()}
            return self.input_output_data.rename(columns=rename_map)
        else:
            return self.input_output_data

    def _get_data_for_pf_by_task_type(self, metrics):
        metrics_calculation_data = self._get_data_for_pf()
        metrics = metrics if metrics is not None else TASK_TYPE_TO_METRICS_MAPPING[
            self.task_type].DEFAULT_LIST

        extra_inputs = {"metrics": ','.join(metrics)}

        if self.task_type == CHAT:
            extra_inputs.update({"deployment_name": self.metrics_mapping["openai_params"]["deployment_id"]})

        # The PF eval template expects metrics names to be passed in as a input parameter
        return df_to_dict_list(metrics_calculation_data, extra_inputs)


    def calculate_metrics(self) -> Dict:

        metrics = self.metrics if self.metrics is not None else TASK_TYPE_TO_METRICS_MAPPING[
            self.task_type].DEFAULT_LIST
        dict_list = self._get_data_for_pf_by_task_type(metrics)

        flow_path = path.join(path.dirname(__file__), "pf_templates", "built_in_metrics", self.task_type)

        from promptflow import PFClient
        from promptflow.entities import AzureOpenAIConnection, OpenAIConnection

        pf_client = PFClient(
            user_agent=USER_AGENT
        )

        openai_config = self.metrics_mapping["openai_params"]
        conn_name = "openai_connection"
        deployment_id = openai_config["deployment_id"]
        if not openai_config["api_type"] or openai_config["api_type"] == "azure":

            connection = AzureOpenAIConnection(
                name=conn_name,
                api_key=openai_config["api_key"],
                api_base=openai_config["api_base"],
                api_type="azure",
                api_version=openai_config["api_version"],
            )
        else:
            connection = OpenAIConnection(
                name=conn_name,
                api_key=openai_config["api_key"],
            )
        pf_client.connections.create_or_update(connection)
        
        connection_override = {
            "connection": conn_name,
            "deployment_name": deployment_id,
        }
        nodes_list = NODE_LIST_BY_TASK[self.task_type]

        if self.task_type == CHAT:
            pf_run = run_pf_flow_with_dict_list(flow_path, dict_list)
        else:
            pf_run = run_pf_flow_with_dict_list(flow_path, dict_list, flow_params={"connections": {node: connection_override for node in nodes_list}})
        wait_for_pf_run_to_complete(pf_run.name)

        result_df = pf_client.get_details(pf_run.name, all_results=True)
        result_metrics = pf_client.get_metrics(pf_run.name)

        # Drop unselected output columns
        columns_to_drop = [col for col in result_df.columns if col.replace("outputs.", "") not in metrics]
        result_df.drop(columns_to_drop, axis=1, inplace=True)

        # Rename inputs/outputs columns. E.g. inputs.question -> question, outputs.gpt_fluency -> gpt_fluency
        column_mapping = {col: col.replace("outputs.", "").replace("inputs.", "") for col in result_df.columns}
        result_df.rename(columns=column_mapping, inplace=True)

        artifacts = {col: result_df[col].tolist() for col in result_df.columns}

        return {
            "metrics": result_metrics,
            "artifacts": artifacts
        }

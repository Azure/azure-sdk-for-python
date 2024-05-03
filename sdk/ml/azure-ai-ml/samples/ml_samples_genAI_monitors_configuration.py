# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_genAI_monitors_configuration.py
DESCRIPTION:
    These samples demonstrate how to set up monitors in GenAI
USAGE:
    python ml_samples_genAI_monitors_configuration.py

"""
import os
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    MonitorSchedule,
    CronTrigger,
    MonitorDefinition,
    ServerlessSparkCompute,
    MonitoringTarget,
    GenerationTokenStatisticsSignal,
    GenerationTokenStatisticsMonitorMetricThreshold,
    GenerationSafetyQualitySignal,
    GenerationSafetyQualityMonitoringMetricThreshold,
    BaselineDataRange,
    AlertNotification,
    LlmData,
)
from azure.ai.ml.entities._inputs_outputs import Input

from azure.ai.ml.constants import MonitorTargetTasks, MonitorDatasetContext

# Authentication package
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
resource_group = os.environ["RESOURCE_GROUP_NAME"]
workspace_name = "test-ws1"
aoai_connection_name = "INSERT_YOUR_AOAI_CONNECTION_NAME"
aoai_deployment_name = "INSERT_YOUR_AOAI_DEPLOYMENT_NAME"
endpoint_name = "INSERT_YOUR_ENDPOINT_NAME"
deployment_name = "INSERT_YOUR_DEPLOYMENT_NAME"
app_trace_name = "app_traces"
app_trace_Version = "1"

# Default Monitor configuration for GenAI apps - Enable monitoring with minimal configurations
ml_client = MLClient(
    credential=credential,
    subscription_id=subscription_id,
    resource_group_name=resource_group,
    workspace_name=workspace_name,
)


class GenAIMonitoringSamples(object):
    def ml_gen_ai_monitor_default(self):
        # [START default_monitoring]
        spark_compute = ServerlessSparkCompute(instance_type="standard_e4s_v3", runtime_version="3.3")
        monitoring_target = MonitoringTarget(
            ml_task=MonitorTargetTasks.QUESTION_ANSWERING,
            endpoint_deployment_id=f"azureml:{endpoint_name}:{deployment_name}",
        )
        monitoring_target = MonitoringTarget(
            ml_task=MonitorTargetTasks.QUESTION_ANSWERING,
            endpoint_deployment_id=f"azureml:{endpoint_name}:{deployment_name}",
        )
        monitor_settings = MonitorDefinition(compute=spark_compute, monitoring_target=monitoring_target)
        model_monitor = MonitorSchedule(
            name="qa_model_monitor", trigger=CronTrigger(expression="15 10 * * *"), create_monitor=monitor_settings
        )
        ml_client.schedules.begin_create_or_update(model_monitor)
        # [END default_monitoring]

    def ml_gen_ai_monitor_advance(self):
        # [START advance_monitoring]
        spark_compute = ServerlessSparkCompute(instance_type="standard_e4s_v3", runtime_version="3.3")
        monitoring_target = MonitoringTarget(
            ml_task=MonitorTargetTasks.QUESTION_ANSWERING,
            endpoint_deployment_id=f"azureml:{endpoint_name}:{deployment_name}",
        )
        token_statistics_signal = GenerationTokenStatisticsSignal()
        generation_quality_thresholds = GenerationSafetyQualityMonitoringMetricThreshold(
            fluency={"acceptable_fluency_score_per_instance": 4, "aggregated_fluency_pass_rate": 0.5},
            coherence={"acceptable_coherence_score_per_instance": 4, "aggregated_coherence_pass_rate": 0.5},
        )
        input_data = Input(
            type="uri_folder",
            path=f"{endpoint_name}-{deployment_name}-{app_trace_name}:{app_trace_Version}",
        )
        data_window = BaselineDataRange(lookback_window_size="P7D", lookback_window_offset="P0D")
        production_data = LlmData(
            data_column_names={"prompt_column": "question", "completion_column": "answer"},
            input_data=input_data,
            data_window=data_window,
        )

        generation_quality_signal = GenerationSafetyQualitySignal(
            connection_id=f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}/connections/{aoai_connection_name}",
            metric_thresholds=generation_quality_thresholds,
            production_data=[production_data],
            sampling_rate=1.0,
            properties={
                "aoai_deployment_name": aoai_deployment_name,
                "enable_action_analyzer": "false",
                "azureml.modelmonitor.gsq_thresholds": '[{"metricName":"average_fluency","threshold":{"value":4}},{"metricName":"average_coherence","threshold":{"value":4}}]',
            },
        )

        monitoring_signals = {
            "token-usage-signal": token_statistics_signal,
            "gsq-signal": generation_quality_signal,
        }

        alert_notification = AlertNotification(emails=["test@example.com", "def@example.com"])

        monitor_settings = MonitorDefinition(
            compute=spark_compute,
            monitoring_target=monitoring_target,
            monitoring_signals=monitoring_signals,
            alert_notification=alert_notification,
        )

        model_monitor = MonitorSchedule(
            name="monitor-name-2", trigger=CronTrigger(expression="15 10 * * *"), create_monitor=monitor_settings
        )

        ml_client.schedules.begin_create_or_update(model_monitor)


if __name__ == "__main__":
    sample = GenAIMonitoringSamples()
    sample.ml_gen_ai_monitor_default()
    sample.ml_gen_ai_monitor_advance()

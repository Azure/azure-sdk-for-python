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

# Get a handle to the workspace. You can find the info on the workspace tab on ml.azure.com
ml_client = MLClient(
    credential=credential,
    subscription_id="2d385bf4-0756-4a76-aa95-28bf9ed3b625",  # os.environ["AZURE_SUBSCRIPTION_ID"],  # this will look like xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    resource_group_name=os.environ["RESOURCE_GROUP_NAME"],
    workspace_name="test-ws1",
)

spark_compute = ServerlessSparkCompute(instance_type="standard_e4s_v3", runtime_version="3.3")

monitoring_target = MonitoringTarget(
    ml_task=MonitorTargetTasks.QUESTION_ANSWERING,
    endpoint_deployment_id="azureml:endpoint:deployment",
)

token_statistics_metrics = GenerationTokenStatisticsMonitorMetricThreshold(
    totaltoken={"total_token_count": 0, "total_token_count_per_group": 0}
)
token_statistics_signal = GenerationTokenStatisticsSignal(metric_thresholds=token_statistics_metrics, sampling_rate=0.1)

# Thresholds for GSQ signal
generation_quality_thresholds = GenerationSafetyQualityMonitoringMetricThreshold(  # need to confirm which one is used, current understanding only one of them is used
    fluency={"acceptable_fluency_score_per_instance": 3.5, "aggregated_fluency_pass_rate": 2.5},
    coherence={"acceptable_coherence_score_per_instance": 3.5, "aggregated_coherence_pass_rate": 3.5},
    groundedness={"aggregated_groundedness_pass_rate": 3.5, "acceptable_groundedness_score_per_instance": 2.5},
    relevance={"acceptable_relevance_score_per_instance": 3.5, "aggregated_relevance_pass_rate": 2.5},
)

input_data = Input(
    type="uri_folder",
    # not mandatory
    path="app traces path",
)
data_window = BaselineDataRange(lookback_window_size="P7D", lookback_window_offset="P0D")


production_data = LlmData(
    data_column_names={"prompt_column": "question", "completion_column": "answer"},  # data column needs to be provided
    input_data=input_data,
    # data_context=MonitorDatasetContext.TEST, --- is not used by backend
    data_window=data_window,
)

# GSQ signal configuration
generation_quality_signal = GenerationSafetyQualitySignal(
    # open question - how customer can grab this?
    workspace_connection_id="<work space connection id>",
    metric_thresholds=generation_quality_thresholds,
    production_data=[production_data],
    sampling_rate=1.0,
    properties={
        "aoai_deployment_name": "gpt-35-turbo-16k",  # mandatory field
        "enable_action_analyzer": "false",
        "azureml.modelmonitor.gsq_thresholds": '[{"metricName":"average_fluency","threshold":{"value":3.5}},{"metricName":"average_coherence","threshold":{"value":3.5}}]',
    },
)

monitoring_signals = {
    "token_statistics_signal": token_statistics_signal,
    "generation_quality_signal": generation_quality_signal,
}

# Emails to send alerts to
alert_notification = AlertNotification(emails=["achauhan@microsoft.com", "def@example.com"])

monitor_settings = MonitorDefinition(
    compute=spark_compute,
    monitoring_target=monitoring_target,
    monitoring_signals=monitoring_signals,
    alert_notification=alert_notification,
)

model_monitor = MonitorSchedule(
    name="monitor-name", trigger=CronTrigger(expression="15 10 * * *"), create_monitor=monitor_settings
)

ml_client.schedules.begin_create_or_update(model_monitor)

###TODO

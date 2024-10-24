# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_evaluations_schedules.py

DESCRIPTION:
    This sample demonstrates how to create a basic evaluation schedule from
    the Online Evaluation Service using a synchronous client.

USAGE:
    python sample_evaluations_schedules.py

    Before running the sample:

    pip install azure-identity
    pip install "git+https://github.com/Azure/azure-sdk-for-python.git@users/singankit/ai_project_utils#egg=azure-ai-client&subdirectory=sdk/ai/azure-ai-client"
    pip install "git+https://github.com/Azure/azure-sdk-for-python.git@users/singankit/demo_evaluators_id#egg=azure-ai-evaluation&subdirectory=sdk/evaluation/azure-ai-evaluation"

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
    Make sure the application_insights access is setup correctly, please refer to the documentation for more details on how to get resource_id and other configs needed.
"""

import os
from azure.ai.project import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.project.models import ApplicationInsightsConfiguration, EvaluatorConfiguration, SamplingStrategy, EvaluationSchedule, CronTrigger, RecurrenceTrigger, Frequency, RecurrenceSchedule
import pprint

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str="<project_connection_string>",
)

# Sample for creating an evaluation schedule with recurrence trigger of daily frequency
app_insights_config = ApplicationInsightsConfiguration(
    resource_id="<sample-resource-id>",
    query="<sample-query>",
    service_name="" # this is not being used, keep empty for now
)
f1_evaluator_config = EvaluatorConfiguration(
    id="<sample-evaluator-id>",
    init_params={},
    data_mapping={"response": "${data.message}", "ground_truth": "${data.itemType}"}
)
recurrence_trigger = RecurrenceTrigger(frequency=Frequency.DAY, interval=1)
evaluators = {
    "<evaluator-name>": f1_evaluator_config,
}

sampling_strategy = SamplingStrategy(rate=0.7)
name = "<sample-name-prefix-with-alias>"
description = "<sample-description>"
tags = {"<tag-key>": "<tag-value>"}
properties = {"Environment": "<sample-environment>"}

evaluation_schedule = EvaluationSchedule(
    data=app_insights_config,
    evaluators=evaluators,
    trigger=recurrence_trigger,
    sampling_strategy=sampling_strategy,
    description=description,
    tags=tags,
    properties=properties
)
# Comment the below sections to run CRUD operations on Online Evaluation Schedule
# -------CREATE ONLINE EVALUATION SCHEDULE-------------
evaluation_schedule = project_client.evaluations.create_or_replace_schedule(name, evaluation_schedule)
pprint.pprint(evaluation_schedule)
# -----------------------------------------------------

# -------GET ONLINE EVALUATION SCHEDULE BY NAME --------------
# evaluation_schedule = project_client.evaluations.get_schedule(name)
# pprint.pprint(evaluation_schedule)
# ------------------------------------------------------------

# -------LIST ONLINE EVALUATION SCHEDULES-------------
# count = 0
# for evaluation_schedule in project_client.evaluations.list_schedule():
#     pprint.pprint(evaluation_schedule)
#     count+=1
# print(f"Total evaluation schedules: {count}")
# -----------------------------------------------------

# ------SOFT DELETE (DISABLE) ONLINE EVALUATION SCHEDULE-------------
# project_client.evaluations.delete_schedule(name)
# print("Successfully Soft Deleted (Disabled) the online evaluation schedule - {}".format(name))
# -------------------------------------------------------------------

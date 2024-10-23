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
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

# Sample for creating an evaluation schedule with recurrence trigger of daily frequency
app_insights_config = ApplicationInsightsConfiguration(
    resource_id="<sample-resource-id>",
    query="<sample-query>",
    service_name="<sample_service_name>"
)
f1_evaluator_config = EvaluatorConfiguration(
    id="azureml://registries/model-evaluation-dev-01/models/F1ScoreEval/versions/1",
    init_params={
        "column_mapping": {
            "response": "${data.message}",
            "ground_truth": "${data.itemType}"
        }
    }
)
recurrence_trigger = RecurrenceTrigger(frequency=Frequency.DAY, interval=1)
evaluators = {
    "f1_score": f1_evaluator_config,
}

sampling_strategy = SamplingStrategy(rate=0.7)
name = "<sample-name>"
description = "<sample-description>"
tags = {"<tag-key>": "<tag-value>"}
properties = {"Environment": "/subscriptions/72c03bf3-4e69-41af-9532-dfcdc3eefef4/resourceGroups/apeddau-rg-eastus2euap/providers/Microsoft.MachineLearningServices/workspaces/apeddau-ws-canary-eastus2euap/environments/ws-online-eval-env/versions/1"}

evaluation_schedule = EvaluationSchedule(
    data=app_insights_config,
    evaluators=evaluators,
    trigger=recurrence_trigger,
    sampling_strategy=sampling_strategy,
    description=description,
    tags=tags,
    properties=properties
)
evaluation_schedule = project_client.evaluations.create_or_replace_schedule(name, evaluation_schedule)
pprint.pprint(evaluation_schedule)

# Below gives examples of other schedule actions available


# # Sample for get an evaluation schedule with name
# evaluation_schedule = project_client.evaluations.get_schedule("<sample-name>")
# pprint.pprint(evaluation_schedule)

# # Sample for list evaluation schedules
# count = 0
# for evaluation_schedule in project_client.evaluations.list_schedule():
#     pprint.pprint(evaluation_schedule)
#     count+=1
# print(f"Total evaluation schedules: {count}")

# # Sample for delete an evaluation schedule with name
# project_client.evaluations.delete_schedule("<sample-name>")
# print("Deleted the evaluation schedule")

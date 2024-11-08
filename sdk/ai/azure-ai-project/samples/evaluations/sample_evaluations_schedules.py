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
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import (
    ApplicationInsightsConfiguration,
    EvaluatorConfiguration,
    EvaluationSchedule,
    RecurrenceTrigger,
    Frequency
)
from azure.ai.evaluation import F1ScoreEvaluator, RelevanceEvaluator
import pprint

# Variables
# Change the values of the below constants
SAMPLE_NAME = "<sample-name>"

# Copy the values from bug bash document
PROJECT_CONNECTION_STRING = "<project_connection_string>"
SAMPLE_RESOURCE_ID = "<sample-resource-id>"
SAMPLE_QUERY = "<sample-query>"
SERVICE_NAME = "<service-name>"


# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=PROJECT_CONNECTION_STRING
)

# Sample for creating an evaluation schedule with recurrence trigger of daily frequency
app_insights_config = ApplicationInsightsConfiguration(
    resource_id=SAMPLE_RESOURCE_ID,
    query=SAMPLE_QUERY,
    service_name=SERVICE_NAME,
    # connection_string=APP_INSIGHTS_CONNECTION_STRING
)

# F1ScoreEvaluator
f1_evaluator_config = EvaluatorConfiguration(
    id=F1ScoreEvaluator.id,
    init_params={},
    data_mapping={
        "response": "${data.message}",
        "ground_truth": "${data.ground_truth}"
    }
)

# Azure OpenAI Service Connection Details
deployment_name = "gpt-4"
api_version = "2024-08-01-preview"
default_connection = project_client.connections._get_connection(
    "onlineevaluati5132847906_aoai"
)
model_config = {
    "azure_deployment": deployment_name,
    "api_version": api_version,
    "type": "azure_openai",
    "azure_endpoint": default_connection.properties["target"]
}
# RelevanceEvaluator
relevance_evaluator_config = EvaluatorConfiguration(
    id=RelevanceEvaluator.id,
    init_params={"model_config": model_config},
    data_mapping={"query": "${data.query}", "response": "${data.response}"}
)

recurrence_trigger = RecurrenceTrigger(frequency=Frequency.DAY, interval=2)
evaluators = {
    "f1_score": f1_evaluator_config
    # "relevance": relevance_evaluator_config
}

name = SAMPLE_NAME
description = f"{SAMPLE_NAME} description"
tags = {"project": "online-eval-bug-bash"}
properties = {"AzureMSIClientId": "f67be261-fdc3-4eab-ba3b-ed38b28b2a3c"}


def create_schedule():
    try:
        evaluation_schedule = EvaluationSchedule(
            data=app_insights_config,
            evaluators=evaluators,
            trigger=recurrence_trigger,
            description=description,
            tags=tags,
            properties=properties
        )
        created_evaluation_schedule = project_client.evaluations.create_or_replace_schedule(
            name, evaluation_schedule
        )
        print(f"Successfully submitted the online evaluation schedule creation request - {created_evaluation_schedule.name}, currently in {created_evaluation_schedule.provisioning_state} state.")
        print("Please use get_schedule to fetch back the evaluation schedule details.")
    except Exception as e:
        print(f"Error occurred while submitting the online evaluation schedule creation request - {name}, Error={e}")


def get_schedule(name):
    try:
        get_evaluation_schedule = project_client.evaluations.get_schedule(name)
        print(f"Successfully fetched the online evaluation schedule - "
              f"{get_evaluation_schedule.name}")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(get_evaluation_schedule.as_dict())
    except Exception as e:
        print(f"Error occurred while fetching the online evaluation schedule - {name},"
              f"Error={e}")


def list_schedules():
    try:
        count = 0
        for evaluation_schedule in project_client.evaluations.list_schedule():
            count += 1
            print(f"{count}. {evaluation_schedule.name} "
                  f"[IsEnabled: {evaluation_schedule.is_enabled}]")
        print(f"Total evaluation schedules: {count}")
    except Exception as e:
        print(
            f"\nError occurred while fetching the online evaluation schedules,"
            f"Error={e}"
        )


def disable_schedule(name):
    try:
        project_client.evaluations.disable_schedule(name)
        print(f"Successfully Disabled the online evaluation schedule - {name}")
    except Exception as e:
        print(f"Error occurred while disabling the online evaluation schedule - {name}, Error={e}")


# Comment the below sections to run CRUD operations on Online Evaluation Schedule
# -------CREATE ONLINE EVALUATION SCHEDULE-------------
create_schedule()
# -----------------------------------------------------

# -------GET ONLINE EVALUATION SCHEDULE BY NAME --------------
# get_schedule(name)
# ------------------------------------------------------------

# -------LIST ONLINE EVALUATION SCHEDULES-------------
# list_schedules()
# -----------------------------------------------------

# ------SOFT DELETE (DISABLE) ONLINE EVALUATION SCHEDULE-------------
# disable_schedule(name)
# -------------------------------------------------------------------

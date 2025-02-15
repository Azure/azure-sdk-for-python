# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Installation Instructions

pip install azure-identity azure-ai-projects azure-ai-ml

# Optionally, you can `pip install azure-ai-evaluation` if you want a code-first experience to fetch evaluator id for built-in evaluators in code
# refer to https://learn.microsoft.com/en-us/azure/ai-studio/how-to/online-evaluation for more details
"""
import pprint
from azure.ai.projects import AIProjectClient 
from azure.identity import DefaultAzureCredential 
from azure.ai.projects.models import ( 
    ApplicationInsightsConfiguration,
    EvaluatorConfiguration,
    EvaluationSchedule,
    RecurrenceTrigger,
    Frequency
)
from azure.ai.evaluation import CoherenceEvaluator  

# This sample includes the setup for an online evaluation schedule using the Azure AI Projects SDK and Azure AI Evaluation SDK
# The schedule is configured to run daily over the collected trace data while running two evaluators: CoherenceEvaluator and RelevanceEvaluator
# This sample can be modified to fit your application's requirements

# Name of your online evaluation schedule
SAMPLE_NAME = "online_eval_name"

# Name of your generative AI application (will be available in trace data in Application Insights)
SERVICE_NAME = "service_name"

# Connection string to your Azure AI Foundry project
# Currently, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# You can copy this connection string in the Azure AI Foundry portal > Project Overview > Project details > Project connection string
PROJECT_CONNECTION_STRING = "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"

# Your Application Insights resource ID
APPLICATION_INSIGHTS_RESOURCE_ID = "appinsights_resource_id"

# Kusto Query Language (KQL) query to query data from Application Insights resource
# This query is compatible with data logged by the Azure AI Inference SDK (https://learn.microsoft.com/en-us/azure/ai-studio/how-to/develop/trace-local-sdk?tabs=python)
# You can modify it depending on your data schema
# The KQL query must output these required columns: operation_ID, operation_ParentID, and gen_ai_response_id
# You can choose which other columns to output as required by the evaluators you are using
# cspell:disable-next-line
KUSTO_QUERY = "let gen_ai_spans=(dependencies | where isnotnull(customDimensions[\"gen_ai.system\"]) | extend response_id = tostring(customDimensions[\"gen_ai.response.id\"]) | project id, operation_Id, operation_ParentId, timestamp, response_id); let gen_ai_events=(traces | where message in (\"gen_ai.choice\", \"gen_ai.user.message\", \"gen_ai.system.message\") or tostring(customDimensions[\"event.name\"]) in (\"gen_ai.choice\", \"gen_ai.user.message\", \"gen_ai.system.message\") | project id= operation_ParentId, operation_Id, operation_ParentId, user_input = iff(message == \"gen_ai.user.message\" or tostring(customDimensions[\"event.name\"]) == \"gen_ai.user.message\", parse_json(iff(message == \"gen_ai.user.message\", tostring(customDimensions[\"gen_ai.event.content\"]), message)).content, \"\"), system = iff(message == \"gen_ai.system.message\" or tostring(customDimensions[\"event.name\"]) == \"gen_ai.system.message\", parse_json(iff(message == \"gen_ai.system.message\", tostring(customDimensions[\"gen_ai.event.content\"]), message)).content, \"\"), llm_response = iff(message == \"gen_ai.choice\", parse_json(tostring(parse_json(tostring(customDimensions[\"gen_ai.event.content\"])).message)).content, iff(tostring(customDimensions[\"event.name\"]) == \"gen_ai.choice\", parse_json(parse_json(message).message).content, \"\")) | summarize operation_ParentId = any(operation_ParentId), Input = maxif(user_input, user_input != \"\"), System = maxif(system, system != \"\"), Output = maxif(llm_response, llm_response != \"\") by operation_Id, id); gen_ai_spans | join kind=inner (gen_ai_events) on id, operation_Id | project Input, System, Output, operation_Id, operation_ParentId, gen_ai_response_id = response_id"

# Connect to Azure AI Studio Project
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=PROJECT_CONNECTION_STRING
)

# Set config to connect to Application Insights resource
app_insights_config = ApplicationInsightsConfiguration(
    resource_id=APPLICATION_INSIGHTS_RESOURCE_ID,
    query=KUSTO_QUERY,
    service_name=SERVICE_NAME
)

# Set Config to connect to AOAI resource
deployment_name = "gpt-4"
api_version = "2024-08-01-preview"
# This is your AOAI connection name, which can be found in your AI Foundry project under the 'Models + Endpoints' tab
default_connection = project_client.connections._get_connection(
    "aoai_connection_name"
)
model_config = {
    "azure_deployment": deployment_name,
    "api_version": api_version,
    "type": "azure_openai",
    "azure_endpoint": default_connection.properties["target"]
}

# Configure your evaluators

# RelevanceEvaluator
relevance_evaluator_config = EvaluatorConfiguration(
    id="azureml://registries/azureml-staging/models/Relevance-Evaluator/versions/4",
    init_params={"model_config": model_config},
    data_mapping={"query": "${data.Input}", "response": "${data.Output}"}
)

# CoherenceEvaluator
coherence_evaluator_config = EvaluatorConfiguration(
    id=CoherenceEvaluator.id,
    init_params={"model_config": model_config},
    data_mapping={"query": "${data.Input}", "response": "${data.Output}"}
)

# Frequency to run the schedule
recurrence_trigger = RecurrenceTrigger(frequency=Frequency.DAY, interval=1)

# ## Dictionary of evaluators
evaluators = {
    "relevance": relevance_evaluator_config,
    "coherence": coherence_evaluator_config
}

# Helper functions
def create_schedule(name, evaluation_schedule):
    try:
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

def list_schedule_runs(name):
    try:
        count = 0
        for run in project_client.evaluations.list(params = {"scheduleName":name}):
            count += 1
            print(f"{count}. {run.display_name} "
                  f"[Status: {run.status}]")
        print(f"Total evaluation schedule runs: {count}")
    except Exception as e:
        print(
            f"\nError occurred while fetching the online evaluation schedule runs,"
            f"Error={e}"
        )

# Configure the online evaluation schedule
name = SAMPLE_NAME
description = f"{SAMPLE_NAME} description"

# AzureMSIClientId is the clientID of the User-assigned managed identity created during set-up - see documentation for how to find it
properties = {"AzureMSIClientId": "your_client_id"}

evaluation_schedule = EvaluationSchedule(
    data=app_insights_config,
    evaluators=evaluators,
    trigger=recurrence_trigger,
    description=description,
    properties=properties)

# Create the evaluation schedule
create_schedule(name, evaluation_schedule)

# Get Online Evaluation Schedule by Name
# get_schedule(name)

# List Online Evaluation Schedules
# list_schedules()

# Soft Delete (Disable) Online Evaluation Schedule
# disable_schedule(name)

# List of Schedule Runs
# list_schedule_runs(name)
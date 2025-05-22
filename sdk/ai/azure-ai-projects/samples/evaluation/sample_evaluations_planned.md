# Overview

This page demonstrates how to use methods to configure, create, get, and list cloud evaluations using the Azure AI Project SDK.

## Prerequisites

Before running this notebook, ensure you have the following:
- Python 3.8 or later.
- The Azure AI Project SDK installed. You can install it using the following command:
  ```bash
  pip install azure-ai-projects azure-identity
  ```
- Set the following environment variables with your own values:
  - `PROJECT_ENDPOINT`: The Azure AI Project endpoint, as found in the overview page of your Azure AI Foundry project.
  - `DATASET_NAME`: The name of the dataset to create and use in this sample.

# Import required libraries
```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    Evaluation,
    InputDataset,
    EvaluatorConfiguration,
    EvaluatorIds
)
```

## Set Environment Variables

Ensure the following environment variables are set before proceeding.

```python
# Set environment variables
endpoint = os.environ["PROJECT_ENDPOINT"]  # Example: https://<account_name>.services.ai.azure.com/api/projects/<project_name>
model_endpoint = os.environ["MODEL_ENDPOINT"]  # Example: https://<account_name>.services.ai.azure.com
model_api_key = os.environ["MODEL_API_KEY"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]  # Example: gpt-4o-mini
dataset_name = os.environ["DATASET_NAME"]
```

## Authenticate and Initialize the Client

```python
# Authenticate and initialize the client
credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
project_client = AIProjectClient(endpoint=endpoint, credential=credential)
```

## Evaluation configuration

```python
# Agent continuous evaluation configuration
project_client.evaluations.create_or_update_config(
    type="agent",
    config={
        "agent_id": "agent_1",
        "sampling_percent": 30,
        "hourly_token_limit": 10000, # aka "max_request_rate"
    }
)
```

## Create evaluation with dataset (batch)

### Upload a Dataset

Upload a single file and create a new dataset to reference the file. Here, we explicitly specify the dataset version.

```python
print("Uploading dataset...")
dataset = project_client.datasets.upload_file(
    name=dataset_name,
    version="1",
    file="./samples_folder/sample_data_evaluation.jsonl",
)
print("Dataset uploaded:", dataset)
```

### Create an Evaluation(basic)

Create an evaluation with default options(project, data mapping etc.) and built-in evaluators.

```python
# Define deployment configuration for all evaluators.
common_init_params = {
    "deployment_name": model_deployment_name,
}

# Create an evaluation
evaluation = Evaluation(
    display_name="Sample Cloud Evaluation",
    description="Sample cloud evaluation with built-in evaluators",
    data=InputDataset(id="<>"),    
    init_params=common_init_params,
    evaluators={
        "relevance": EvaluatorConfiguration(
            id=EvaluatorIds.RELEVANCE.value,
        ),
        "violence": EvaluatorConfiguration(
            id=EvaluatorIds.VIOLENCE.value,
        ),
        "bleu_score": EvaluatorConfiguration(
            id=EvaluatorIds.BLEU_SCORE.value,
        ),
    },
)

evaluation_response = project_client.evaluations.create(evaluation)

print("Evaluation created:", evaluation_response)
```

### Create an Evaluation(advanced)

Create an evaluation with custom parameters and custom evaluators. Details of how to define a custom evaluator are [here](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-evaluators/custom-evaluators) 

Define common data mapping and initialization parameters

```python
common_data_mapping = {
    "query": "${data.query}",
    "response": "${data.response}",
}

common_init_params = {
    "deployment_name": model_deployment_name,
}

# Create and register a custom evaluator.
custom_evaluator = Evaluator(
    id ="custom://friendliness",
    path="<local_folder_path>",
    name="Custom friendliness evaluator",
    description="prompt-based evaluator measuring response friendliness.",
)
registered_evaluator = project_client.evaluators.create_or_update(custom_evaluator)
print("Registered evaluator id:", registered_evaluator.id);

data = InputDataset(id="<>")

# Create an evaluation
evaluation = Evaluation(
    display_name="Sample Evaluation Test",
    description="Sample evaluation for testing",
    data=data,
    data_mapping=common_data_mapping,
    init_params=common_init_params,
    evaluators={
        "relevance": EvaluatorConfiguration(
            id=EvaluatorIds.RELEVANCE.value,
            data_mapping={
                        "query": "${data.query}",
                        "response": "${data.response}",
                        "context": "${data.context}",
                        },
        ),
        "violence": EvaluatorConfiguration(
            id=EvaluatorIds.VIOLENCE.value,
            
        ),
        "bleu_score": EvaluatorConfiguration(
            id=EvaluatorIds.BLEU_SCORE.value,
        ),
        "friendliness": EvaluatorConfiguration(
            id=registered_evaluator.id,
        ),
)

evaluation_response = project_client.evaluations.create(evaluation)

print("Evaluation created:", evaluation_response)
```

## Create evaluation with raw data(single run)

### Evaluation input data options

#### Option 1: non-agentic evaluation

```python
raw_data = {
    "query": "sample query",
    "response": "sample response",
    "context": "sample context",
    "groundtruth": "sample groundtruth",
}
data = InputRawData(raw_data=raw_data)
```

#### Option 2: agent evaluation

```python
query = [{
        "role": "system",
        "content": "You are a friendly and helpful customer service agent."
    }, {
        "createdAt": "2025-03-14T06:14:20Z",
        "role": "user",
        "content": [{
            "type": "text",
            "text": "Hi, I need help with the last 2 orders on my account #888. Could you please update me on their status?"
        }]
    }
]

response = [{
    "createdAt": "2025-03-14T06:14:35Z",
    "run_id": "0",
    "role": "assistant",
    "content": [{
        "type": "tool_call",
        "tool_call_id": "tool_call_20250310_001",
        "name": "get_orders",
        "arguments": {
            "account_number": "888"
        }
    }]
}, {
    "createdAt": "2025-03-14T06:15:05Z",
    "run_id": "0",
    "role": "assistant",
    "content": [{
        "type": "text",
        "text": "<orders-summary-for-the-account>"
    }]
}]

tool_definitions = [{
    "name": "get_orders",
    "description": "Get the list of orders for a given account number.",
    "parameters": {
        "type": "object",
        "properties": {
            "account_number": {
                "type": "string",
                "description": "The account number to get the orders for."
            }
        }
    }
}]

data = InputRawData(query=query, response=response, tool_definitions=tool_definitions)
```

#### Option 3: Semantic Kernel evaluation

```python
query = "my sample query"
response = "my sample response"

search_wikipedia = KernelFunctionFromPrompt(
    function_name="search_wikipedia",
    prompt=f"""Sample prompt""",
)

query = AIAgentConverter.convert_query(query)
response = AIAgentConverter.convert_response(response)
tool_definitions = AIAgentConverter.convert_semantickernel_tools([search_wikipedia])

data = InputRawData(query=query, response=response, tool_definitions=tool_definitions)
```

#### Option 4: LangChain evaluation

```python
from langchain_core.tools import tool

query = "my sample query"
response = "my sample response"

@tool
def search_wikipedia(term: str) -> str:
    """Search wikipedia for the term provided"""
    pass

query = AIAgentConverter.convert_query(query)
response = AIAgentConverter.convert_response(response)
tool_definitions = AIAgentConverter.convert_langchain_tools([search_wikipedia])

data = InputRawData(query=query, response=response, tool_definitions=tool_definitions)
```

### Create an evaluation with raw data

```python
# Create an evaluation
evaluation = Evaluation(
    display_name="Sample Evaluation Test",
    description="Sample evaluation for testing",
    data=data,
    init_params={
        "deployment_name": model_deployment_name,
    },
    evaluators={
        "relevance": EvaluatorConfiguration(
            id=EvaluatorIds.RELEVANCE.value,
        ),
        "violence": EvaluatorConfiguration(
            id=EvaluatorIds.VIOLENCE.value,
        ),
        "bleu_score": EvaluatorConfiguration(
            id=EvaluatorIds.BLEU_SCORE.value,
        ),
    },
)

evaluation_response = project_client.evaluations.create(
    evaluation,
    headers={
        "model-endpoint": model_endpoint,
        "api-key": model_api_key,
    },
)
print("Evaluation created:", evaluation_response)
```

## List Evaluations

List all evaluations in the project.

```python
# List all evaluations
# Sample URL: https://[resource-name].services.ai.azure.com/api/projects/[project-name]/evaluations?api-version=2025-05-15-preview
print("Listing all evaluations...")
for evaluation in project_client.evaluations.list():
    print(evaluation)

# Find evaluations for an agent run
# Sample URL: https://[resource-name].services.ai.azure.com/api/projects/[project-name]/evaluations?agent_run_id=[my-agent-run-id]&api-version=2025-05-15-preview
print("Find evaluations with agent run Id...")
for evaluation in project_client.evaluations.list(agent_run_id=agent_run_id):
    # A single agent run may have multiple evaluation runs (e.g. re-run evaluation)
    print(evaluation)
```

## Get an Evaluation

Retrieve the metadata of a created evaluation run.

```python
# Get evaluation details
print("Getting evaluation details...")
get_evaluation_response = project_client.evaluations.get(evaluation_response.name)
print("Evaluation details:", get_evaluation_response)
```

### Get Evaluation results for raw data input

Retrieve the evaluation results from an evaluation run. The response for raw data input will be raw data, based on the assumption: only the users wants to evaluation big data will use dataset, which results in big data as output in dataset

```python
# Get evaluation results
print("Getting evaluation results...")
get_evaluation_results = project_client.evaluations.get_results(evaluation_response.name)
print("Evaluation results:", get_evaluation_results)

# Sample output
# {
#     "id": "evaluation_run_id",
#     ...
#     "type": "raw",
#     "result": [{
#         "evaluator": "Intent Resolution Evaluator",
#         "evaluatorId": "azureai://built-in/evaluators/intent_resolution",
#         "score": 5.0,
#         "status": "Completed",
#         "reason": "The agent's response directly addresses the user's request for a joke by providing a humorous punchline. The joke is relevant and fulfills the user's intent to hear a joke.",
#         "version": "1",
#         "responseId": "thread_dtykPFfWERcAvifwrkuu67ki;run_yR09Fby0Neqo7Ip0evhYRuuP",
#         "messageId": "d14d3b1d-4f3d-4b5f-9a86-ee56928049a9",
#         "threadId": "thread_dtykPFfWERcAvifwrkuu67ki",
#         "runId": "run_yR09Fby0Neqo7Ip0evhYRuuP",
#         "error": null,
#         "additionalDetails": null
#   }],
#   "error": null
# }
```

### Get Evaluation results for dataset input

Retrieve the evaluation results from an evaluation run.

```python
# Get evaluation results
print("Getting evaluation results...")
get_evaluation_results = project_client.evaluations.get_results(evaluation_response.name)
print("Evaluation results:", get_evaluation_results)
# Sample output
# {
#     "id": "evaluation_run_id",
#     ...
#     "type": "blob",
#     "result": {
#         "dataset_name": "sample_dataset_name",
#         "dataset_version": "sample_dataset_version",
#     }
# }

# Get evaluation results with credentials
print("Getting evaluation results with credentials...")
get_evaluation_results = project_client.evaluations.get_results(evaluation_response.name, with_credentials=True)
print("Evaluation results:", get_evaluation_results)
# Sample output
# {
#     "id": "evaluation_run_id",
#     ...
#     "type": "blob",
#     "result": {
#         "dataset_name": "sample_dataset_name",
#         "dataset_version": "sample_dataset_version",
#         "credentials": {
#             "blob_uri": "https://myaccount.blob.core.windows.net/mycontainer/mypath1/mypath2/myblob",
#             ...
#             "sas_uri": "https://mystorageaccount.blob.core.windows.net/mycontainer/myblob?sv=2019-12-12&ss=bjqt&srt=sco&sp=rwdlacupx&se=2020-10-01T05:00:00Z&st=2020-09-30T17:00:00Z&spr=https&sig=my-sig",
#             "type": "SAS"
#         },
#     }
# }
# Download file
sas_uri = get_evaluation_results.result.blob_reference.credentials.sas_uri
with urlopen(sas_uri) as response:
    content = response.read().decode('utf-8')
    print("Evaluation results: ", content)
```

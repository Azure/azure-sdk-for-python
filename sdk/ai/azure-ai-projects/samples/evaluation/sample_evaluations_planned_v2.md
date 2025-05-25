- [Summary](#summary)
- [Setup authentication with AI Foundry Projects client](#setup-authentication-with-ai-foundry-projects-client)
- [Configure evaluations](#configure-evaluations)
- [Create evaluation runs](#create-evaluation-runs)
  - [Options for input data](#options-for-input-data)
    - [Input with batch data (dataset)](#input-with-batch-data-dataset)
    - [Input with single row](#input-with-single-row)
    - [Input with agentic data](#input-with-agentic-data)
  - [Create evaluation](#create-evaluation)
    - [Create evaluation without config](#create-evaluation-without-config)
    - [Create evaluation with config](#create-evaluation-with-config)
    - [Create evaluation with custom evaluators](#create-evaluation-with-custom-evaluators)
- [Get evaluation results](#get-evaluation-results)
  - [List evaluation metadata](#list-evaluation-metadata)
  - [Get evaluation metadata](#get-evaluation-metadata)
  - [Get evaluation result data](#get-evaluation-result-data)
    - [Get evaluation result in data blob](#get-evaluation-result-in-data-blob)
    - [Get evaluation result in plain text](#get-evaluation-result-in-plain-text)
- [Appendix](#appendix)
  - [Agentic data sample](#agentic-data-sample)
  - [Semantic Kernel as input data](#semantic-kernel-as-input-data)
  - [LangChain as input data](#langchain-as-input-data)
  - [Evaluation results blob example](#evaluation-results-blob-example)
  - [Evaluation results plain text example](#evaluation-results-plain-text-example)

# Summary

This document describes the setups and options to create evaluation and get evaluation results, with sample code and sample data in appendix.

# Setup authentication with AI Foundry Projects client
```python
endpoint = "https://<account_name>.services.ai.azure.com/api/projects/<project_name>"
credential = DefaultAzureCredential()
# Entra ID based AI Foundry Projects client
project_client = AIProjectClient(endpoint=endpoint, credential=credential)
```

# Configure evaluations
There are many different evaluation configuration types, we will only use agent continuous evaluation as an example. 
```python
project_client.evaluations.create_or_update_config(
    type="agent",
    config={
        "agent_id": "sample_agent_id",
        "sampling_percent": 30,
        "hourly_token_limit": 10000,
    }
)
```

# Create evaluation runs

## Options for input data
For large batch data evaluation, the user should upload the data as a dataset before running evaluation; for non-batch data evaluation, the user can send the data directly.

### Input with batch data (dataset)

```python
# Create dataset from a single file.
dataset = project_client.datasets.upload_file(
    name=dataset_name,
    version="1",
    file="./samples_folder/sample_data_evaluation.jsonl",
)
data = InputDataset(id=dataset.id)
```

### Input with single row

```python
raw_data = {
    "query": "sample query",
    "response": "sample response",
    "context": "sample context",
    "groundtruth": "sample groundtruth",
}
data = InputData(data=raw_data)
```

### Input with agentic data

Refer to appendix for more details:
* [Agentic data sample](#agentic-data-sample) for agent data sample
* [LangChain data sample](#langchain-as-input-data) for LangChain data as input data sample
* [SemanticKernel data sample](#semantic-kernel-as-input-data) for SemanticKernel data as input data sample

```python
query = [...]
response = [...]
tool_definitions = [...]
data = InputAgentData(query=query, response=response, tool_definitions=tool_definitions)
```

## Create evaluation

### Create evaluation without config

Both display name and description will be inferred from evaluator names

```python
evaluation = Evaluation(
    data=data,
    init_params={ "deployment_name": model_deployment_name },
    evaluators={
        "relevance": EvaluatorConfiguration(id=EvaluatorIds.RELEVANCE.value),
        "violence": EvaluatorConfiguration(id=EvaluatorIds.VIOLENCE.value),
    },
)
evaluation_response = project_client.evaluations.create(evaluation)
```

### Create evaluation with config

```python
common_data_mapping = {
    "query": "${data.request}",
    "response": "${data.response}",
}

evaluation = Evaluation(
    display_name="Sample Evaluation Test",
    description="Sample description",
    data=data,
    data_mapping=common_data_mapping,
    init_params={ "deployment_name": model_deployment_name },
    evaluators={
        "relevance": EvaluatorConfiguration(
            id=EvaluatorIds.RELEVANCE.value,
            data_mapping={
                "query": "${data.query}",
                "response": "${data.response}",
            },
        ),
        "violence": EvaluatorConfiguration(id=EvaluatorIds.VIOLENCE.value),
    },
)

evaluation_response = project_client.evaluations.create(evaluation)
```

### Create evaluation with custom evaluators

```python
common_data_mapping = { ... }

# Create and register a custom evaluator.
custom_evaluator = Evaluator(
    id ="custom://friendliness",
    path="<local_folder_path>",
    name="Custom friendliness evaluator",
    description="prompt-based evaluator measuring response friendliness.",
)
registered_custom_evaluator = project_client.evaluators.create_or_update(custom_evaluator)

evaluation = Evaluation(
    data=data,
    data_mapping=common_data_mapping,
    init_params={ "deployment_name": model_deployment_name },
    evaluators={
        "relevance": EvaluatorConfiguration(id=EvaluatorIds.RELEVANCE.value),
        "friendliness": EvaluatorConfiguration(id=regisregistered_custom_evaluatortered_evaluator.id),
    },
)

evaluation_response = project_client.evaluations.create(evaluation)
```

# Get evaluation results

## List evaluation metadata

```python
# List all evaluations
for evaluation in project_client.evaluations.list():
    print(evaluation)

# Find evaluations for an agent run, a single agent run may have multiple evaluation runs because of re-run
for evaluation in project_client.evaluations.list(agent_run_id=agent_run_id):
    print(evaluation)
```

## Get evaluation metadata

```python
get_evaluation_response = project_client.evaluations.get(evaluation_response.name)
```

## Get evaluation result data

### Get evaluation result in data blob

When the input data is batch data (in dataset), the evaluation result will be stored in blob because it could be as large as couple of GB.

Refer to appendix [Evaluation results blob example](#evaluation-results-blob-example) for JSON sample data.

```python
# Get evaluation results with blob information as well as credentials
get_evaluation_results = project_client.evaluations.get_results(evaluation_response.name, with_credentials=True)

# Download evaluation results from Azure Blob Storage
sas_uri = get_evaluation_results.result.blob_reference.credentials.sas_uri
with urlopen(sas_uri) as response:
    content = response.read().decode('utf-8')
```

### Get evaluation result in plain text

For non-dataset input, the evaluation result will be stored in blob storage as well, but get evaluation results API will get it as plain text.

Refer to appendix [Evaluation results plain text example](#evaluation-results-plain-text-example) for JSON sample data.

```python
get_evaluation_results = project_client.evaluations.get_results(evaluation_response.name)
```

# Appendix

## Agentic data sample

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
}]

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
```

## Semantic Kernel as input data

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

data = InputAgentData(query=query, response=response, tool_definitions=tool_definitions)
```

## LangChain as input data

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

data = InputAgentData(query=query, response=response, tool_definitions=tool_definitions)
```

## Evaluation results blob example

```json
{
    "id": "evaluation_run_id",
    ...
    "type": "blob",
    "result": {
        "dataset_name": "sample_dataset_name",
        "dataset_version": "sample_dataset_version",
        "credentials": {
            "blob_uri": "https://myaccount.blob.core.windows.net/mycontainer/mypath1/mypath2/myblob",
            ...
            "sas_uri": "https://mystorageaccount.blob.core.windows.net/mycontainer/myblob?sv=2019-12-12&ss=bjqt&srt=sco&sp=rwdlacupx&se=2020-10-01T05:00:00Z&st=2020-09-30T17:00:00Z&spr=https&sig=my-sig",
            "type": "SAS"
        },
    }
}
```

## Evaluation results plain text example

```json
{
    "id": "evaluation_run_id",
    ...
    "type": "raw",
    "result": [{
        "evaluator": "Intent Resolution Evaluator",
        "evaluatorId": "azureai://built-in/evaluators/intent_resolution",
        "score": 5.0,
        "status": "Completed",
        "reason": "The agent's response directly addresses the user's request for a joke by providing a humorous punchline. The joke is relevant and fulfills the user's intent to hear a joke.",
        "version": "1",
        "responseId": "thread_dtykPFfWERcAvifwrkuu67ki;run_yR09Fby0Neqo7Ip0evhYRuuP",
        "messageId": "d14d3b1d-4f3d-4b5f-9a86-ee56928049a9",
        "threadId": "thread_dtykPFfWERcAvifwrkuu67ki",
        "runId": "run_yR09Fby0Neqo7Ip0evhYRuuP",
        "error": null,
        "additionalDetails": null
  }],
  "error": null
}

```

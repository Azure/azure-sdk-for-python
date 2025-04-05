<!-- PIPY LONG DESCRIPTION BEGIN -->
# Azure AI Projects client library for Python

Use the AI Projects client library (in preview) to:

* **Enumerate AI Models** deployed to your Azure AI Foundry project.
* **Enumerate the connections** in your Azure AI Foundry project to other Azure resources, and get their properties.
For example, get the inference endpoint URL and credentials associated with your Azure OpenAI connection.
* **Create and enumerate Datasets** in your Azure AI Foundry project, referencing your documents stored in the cloud.
* **Create and enumerate Indexes** in your Azure AI Foundry project, referencing your embeddings.
* **Get an authenticated Inference client** to do chat completions, for the default Azure OpenAI or AI Services connections in your Azure AI Foundry project. Supports the AzureOpenAI client from the `openai` package, or clients from the `azure-ai-inference` package.'
* **Read a Prompty file or string** and render it as a list of messages to directly pass into a ChatCompletionsClient from the `azure-ai-inference` package.
* **Develop Agents using the Azure AI Agent Service**, leveraging an extensive ecosystem of models, tools, and capabilities from OpenAI, Microsoft, and other LLM providers. The Azure AI Agent Service enables the building of Agents for a wide range of generative AI use cases. The package is currently in preview.
* **Run Evaluations** to assess the performance of generative AI applications using various evaluators and metrics. It includes built-in evaluators for quality, risk, and safety, and allows custom evaluators for specific needs.
* **Enable OpenTelemetry tracing**.

[Product documentation](https://aka.ms/azsdk/azure-ai-projects/product-doc)
| [Samples][samples]
| [API reference documentation](https://aka.ms/azsdk/azure-ai-projects/python/reference)
| [Package (PyPI)](https://aka.ms/azsdk/azure-ai-projects/python/package)
| [SDK source code](https://aka.ms/azsdk/azure-ai-projects/python/code)
| [AI Starter Template](https://aka.ms/azsdk/azure-ai-projects/python/ai-starter-template)

## Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues). Mention the package name "azure-ai-projects" in the title or content.

## Table of contents

- [Getting started](#getting-started)
  - [Prerequisite](#prerequisite)
  - [Install the package](#install-the-package)
- [Key concepts](#key-concepts)
  - [Create and authenticate the client](#create-and-authenticate-the-client)
- [Examples](#examples)
  - [Enumerate connections](#enumerate-connections)
    - [Get properties of all connections](#get-properties-of-all-connections)
    - [Get properties of all connections of a particular type](#get-properties-of-all-connections-of-a-particular-type)
    - [Get properties of a default connection](#get-properties-of-a-default-connection)
    - [Get properties of a connection by its connection name](#get-properties-of-a-connection-by-its-connection-name)
  - [Get an authenticated ChatCompletionsClient](#get-an-authenticated-chatcompletionsclient)
  - [Get an authenticated AzureOpenAI client](#get-an-authenticated-azureopenai-client)
  - [Evaluation](#evaluation)
    - [Evaluator](#evaluator)
    - [Run Evaluation in the cloud](#run-evaluation-in-the-cloud)
      - [Evaluators](#evaluators)
      - [Data to be evaluated](#data-to-be-evaluated)
        - [[Optional] Azure OpenAI Model](#optional-azure-openai-model)
        - [Example Remote Evaluation](#example-remote-evaluation)
  - [Tracing](#tracing)
    - [Installation](#installation)
    - [How to enable tracing](#how-to-enable-tracing)
    - [How to trace your own functions](#how-to-trace-your-own-functions)
- [Troubleshooting](#troubleshooting)
  - [Exceptions](#exceptions)
  - [Logging](#logging)
  - [Reporting issues](#reporting-issues)
- [Next steps](#next-steps)
- [Contributing](#contributing)
<!-- PIPY LONG DESCRIPTION END -->
## Getting started

### Prerequisite

- Python 3.8 or later.
- An [Azure subscription][azure_sub].
- A [project in Azure AI Foundry](https://learn.microsoft.com/azure/ai-studio/how-to/create-projects).
- The project endpoint URL, of the form `https://<ai-services-resource-name>.services.ai.azure.com/api/projects/<project-name>`. It can be found in your Azure AI Foundry project overview page, under "Project details". Below we will assume the environment variable `PROJECT_ENDPOINT` was defined to hold this value.
- An Entra ID token for authentication. Your application needs an object that implements the [TokenCredential](https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.tokencredential) interface. Code samples here use [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential). To get that working, you will need:
  * An appropriate role assignment. see [Role-based access control in Azure AI Foundry portal](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-ai-foundry). Role assigned can be done via the "Access Control (IAM)" tab of your Azure AI Project resource in the Azure portal.
  * [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed.
  * You are logged into your Azure account by running `az login`.
  * Note that if you have multiple Azure subscriptions, the subscription that contains your Azure AI Project resource must be your default subscription. Run `az account list --output table` to list all your subscription and see which one is the default. Run `az account set --subscription "Your Subscription ID or Name"` to change your default subscription.

### Install the package

```bash
pip install azure-ai-projects
```

## Key concepts

### Create and authenticate the client with Entra ID

To construct a synchronous client:

```python
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ["PROJECT_ENDPOINT"],
)
```

To construct an asynchronous client, Install the additional package [aiohttp](https://pypi.org/project/aiohttp/):

```bash
pip install aiohttp
```

and update the code above to import `asyncio`, and import `AIProjectClient` from the `azure.ai.projects.aio` namespace:

```python
import os
import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.core.credentials import AzureKeyCredential

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
     endpoint=os.environ["PROJECT_ENDPOINT"],
)
```

## Examples

### Enumerate connections

Your Azure AI Foundry project has a "Management center". When you enter it, you will see a tab named "Connected resources" under your project. The `.connections` operations on the client allow you to enumerate the connections and get connection properties. Connection properties include the resource URL and authentication credentials, among other things.

Below are code examples of the connection operations. Full samples can be found under the "connetions" folder in the [package samples][samples].

#### Get properties of all connections

To list the properties of all the connections in the Azure AI Foundry project:

```python
connections = project_client.connections.list()
for connection in connections:
    print(connection)
```

#### Get properties of all connections of a particular type

To list the properties of connections of a certain type (here Azure OpenAI):

```python
connections = project_client.connections.list(
    connection_type=ConnectionType.AZURE_OPEN_AI,
)
for connection in connections:
    print(connection)

```

#### Get properties of a default connection

To get the properties of the default connection of a certain type (here Azure OpenAI),
with its authentication credentials:

```python
connection = project_client.connections.get_default(
    connection_type=ConnectionType.AZURE_OPEN_AI,
    include_credentials=True,  # Optional. Defaults to "False".
)
print(connection)
```

If the call was made with `include_credentials=True`, depending on the value of `connection.authentication_type`, either `connection.key` or `connection.token_credential`
will be populated. Otherwise both will be `None`.

#### Get properties of a connection by its connection name

To get the connection properties of a connection named `connection_name`:

```python
connection = project_client.connections.get(
    connection_name=connection_name,
    include_credentials=True  # Optional. Defaults to "False"
)
print(connection)
```

### Get an authenticated ChatCompletionsClient

Your Azure AI Foundry project may have one or more AI models deployed that support chat completions. These could be OpenAI models, Microsoft models, or models from other providers. Use the code below to get an already authenticated [ChatCompletionsClient](https://learn.microsoft.com/python/api/azure-ai-inference/azure.ai.inference.chatcompletionsclient) from the [azure-ai-inference](https://pypi.org/project/azure-ai-inference/) package, and execute a chat completions call.

First, install the package:

```bash
pip install azure-ai-inference
```

Then run this code (replace "gpt-4o" with your model deployment name):

```python
inference_client = project_client.inference.get_chat_completions_client()

response = inference_client.complete(
    model="gpt-4o", # Model deployment name
    messages=[UserMessage(content="How many feet are in a mile?")]
)

print(response.choices[0].message.content)
```

See the "inference" folder in the [package samples][samples] for additional samples, including getting an authenticated [EmbeddingsClient](https://learn.microsoft.com/python/api/azure-ai-inference/azure.ai.inference.embeddingsclient) and [ImageEmbeddingsClient](https://learn.microsoft.com/python/api/azure-ai-inference/azure.ai.inference.imageembeddingsclient).

### Get an authenticated AzureOpenAI client

Your Azure AI Foundry project may have one or more OpenAI models deployed that support chat completions. Use the code below to get an already authenticated [AzureOpenAI](https://github.com/openai/openai-python?tab=readme-ov-file#microsoft-azure-openai) from the [openai](https://pypi.org/project/openai/) package, and execute a chat completions call.

First, install the package:

```bash
pip install openai
```

Then run the code below. Replace `gpt-4o` with your model deployment name, and update the `api_version` value with one found in the "Data plane - inference" row [in this table](https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs).

```python
aoai_client = project_client.inference.get_azure_openai_client(api_version="2024-06-01")

response = aoai_client.chat.completions.create(
    model="gpt-4o", # Model deployment name
    messages=[
        {
            "role": "user",
            "content": "How many feet are in a mile?",
        },
    ],
)

print(response.choices[0].message.content)
```

See the "inference" folder in the [package samples][samples] for additional samples.

### Evaluation

Evaluation in Azure AI Project client library is designed to assess the performance of generative AI applications in the cloud. The output of Generative AI application is quantitively measured with mathematical based metrics, AI-assisted quality and safety metrics. Metrics are defined as evaluators. Built-in or custom evaluators can provide comprehensive insights into the application's capabilities and limitations.

#### Evaluator

Evaluators are custom or prebuilt classes or functions that are designed to measure the quality of the outputs from language models or generative AI applications.

Evaluators are made available via [azure-ai-evaluation][azure_ai_evaluation] SDK for local experience and also in [Evaluator Library][evaluator_library] in Azure AI Foundry for using them in the cloud.

More details on built-in and custom evaluators can be found [here][evaluators].

#### Run Evaluation in the cloud

To run evaluation in the cloud the following are needed:

- Evaluators
- Data to be evaluated
- [Optional] Azure Open AI model.

##### Evaluators

For running evaluator in the cloud, evaluator `ID` is needed. To get it via code you use [azure-ai-evaluation][azure_ai_evaluation]

```python
# pip install azure-ai-evaluation

from azure.ai.evaluation import RelevanceEvaluator

evaluator_id = RelevanceEvaluator.id
```

##### Data to be evaluated

Evaluation in the cloud supports data in form of `jsonl` file. Data can be uploaded via the helper method `upload_file` on the project client.

```python
# Upload data for evaluation and get dataset id
data_id, _ = project_client.upload_file("<data_file.jsonl>")
```

##### [Optional] Azure OpenAI Model

Azure AI Foundry project comes with a default Azure Open AI endpoint which can be easily accessed using following code. This gives you the endpoint details for you Azure OpenAI endpoint. Some of the evaluators need model that supports chat completion.

```python
default_connection = project_client.connections.get_default(connection_type=ConnectionType.AZURE_OPEN_AI)
```

##### Example Remote Evaluation

```python
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import Evaluation, Dataset, EvaluatorConfiguration, ConnectionType
from azure.ai.evaluation import F1ScoreEvaluator, RelevanceEvaluator, HateUnfairnessEvaluator


# Create project client
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

# Upload data for evaluation and get dataset id
data_id, _ = project_client.upload_file("<data_file.jsonl>")

deployment_name = "<deployment_name>"
api_version = "<api_version>"

# Create an evaluation
evaluation = Evaluation(
    display_name="Remote Evaluation",
    description="Evaluation of dataset",
    data=Dataset(id=data_id),
    evaluators={
        "f1_score": EvaluatorConfiguration(
            id=F1ScoreEvaluator.id,
        ),
        "relevance": EvaluatorConfiguration(
            id=RelevanceEvaluator.id,
            init_params={
                "model_config": default_connection.to_evaluator_model_config(
                    deployment_name=deployment_name, api_version=api_version
                )
            },
        ),
        "violence": EvaluatorConfiguration(
            id=ViolenceEvaluator.id,
            init_params={"azure_ai_project": project_client.scope},
        ),
    },
)


evaluation_response = project_client.evaluations.create(
    evaluation=evaluation,
)

# Get evaluation
get_evaluation_response = project_client.evaluations.get(evaluation_response.id)

print("----------------------------------------------------------------")
print("Created evaluation, evaluation ID: ", get_evaluation_response.id)
print("Evaluation status: ", get_evaluation_response.status)
if isinstance(get_evaluation_response.properties, dict):
    print("AI Foundry URI: ", get_evaluation_response.properties["AiStudioEvaluationUri"])
print("----------------------------------------------------------------")
```

NOTE: For running evaluators locally refer to [Evaluate with the Azure AI Evaluation SDK][evaluators].

### Tracing

You can add an Application Insights Azure resource to your Azure AI Foundry project. See the Tracing tab in your AI Foundry project. If one was enabled, you can get the Application Insights connection string, configure your Agents, and observe the full execution path through Azure Monitor. Typically, you might want to start tracing before you create an Agent.

#### Installation

Make sure to install OpenTelemetry and the Azure SDK tracing plugin via

```bash
pip install opentelemetry
pip install azure-ai-projects azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry
```

You will also need an exporter to send telemetry to your observability backend. You can print traces to the console or use a local viewer such as [Aspire Dashboard](https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone?tabs=bash).

To connect to Aspire Dashboard or another OpenTelemetry compatible backend, install OTLP exporter:

```bash
pip install opentelemetry-exporter-otlp
```

#### How to enable tracing

Here is a code sample that shows how to enable Azure Monitor tracing:

<!-- SNIPPET:sample_agents_basics_with_azure_monitor_tracing.enable_tracing -->

```python
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor

# Enable Azure Monitor tracing
application_insights_connection_string = project_client.telemetry.get_connection_string()
if not application_insights_connection_string:
    print("Application Insights was not enabled for this project.")
    print("Enable it via the 'Tracing' tab in your AI Foundry project page.")
    exit()
configure_azure_monitor(connection_string=application_insights_connection_string)

# enable additional instrumentations
project_client.telemetry.enable()

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span(scenario):
    with project_client:
```

<!-- END SNIPPET -->

In addition, you might find helpful to see the tracing logs in console. You can achieve by the following code:

```python
project_client.telemetry.enable(destination=sys.stdout)
```

#### How to trace your own functions

The decorator `trace_function` is provided for tracing your own function calls using OpenTelemetry. By default the function name is used as the name for the span. Alternatively you can provide the name for the span as a parameter to the decorator.

This decorator handles various data types for function parameters and return values, and records them as attributes in the trace span. The supported data types include:
* Basic data types: str, int, float, bool
* Collections: list, dict, tuple, set
    * Special handling for collections:
      - If a collection (list, dict, tuple, set) contains nested collections, the entire collection is converted to a string before being recorded as an attribute.
      - Sets and dictionaries are always converted to strings to ensure compatibility with span attributes.

Object types are omitted, and the corresponding parameter is not traced.

The parameters are recorded in attributes `code.function.parameter.<parameter_name>` and the return value is recorder in attribute `code.function.return.value`

## Troubleshooting

### Exceptions

Client methods that make service calls raise an [HttpResponseError](https://learn.microsoft.com/python/api/azure-core/azure.core.exceptions.httpresponseerror) exception for a non-success HTTP status code response from the service. The exception's `status_code` will hold the HTTP response status code (with `reason` showing the friendly name). The exception's `error.message` contains a detailed message that may be helpful in diagnosing the issue:

```python
from azure.core.exceptions import HttpResponseError

...

try:
    result = project_client.connections.list()
except HttpResponseError as e:
    print(f"Status code: {e.status_code} ({e.reason})")
    print(e.message)
```

For example, when you provide wrong credentials:

```text
Status code: 401 (Unauthorized)
Operation returned an invalid status 'Unauthorized'
```

### Logging

The client uses the standard [Python logging library](https://docs.python.org/3/library/logging.html). The SDK logs HTTP request and response details, which may be useful in troubleshooting. To log to stdout, add the following:

```python
import sys
import logging

# Acquire the logger for this client library. Use 'azure' to affect both
# 'azure.core` and `azure.ai.inference' libraries.
logger = logging.getLogger("azure")

# Set the desired logging level. logging.INFO or logging.DEBUG are good options.
logger.setLevel(logging.DEBUG)

# Direct logging output to stdout:
handler = logging.StreamHandler(stream=sys.stdout)
# Or direct logging output to a file:
# handler = logging.FileHandler(filename="sample.log")
logger.addHandler(handler)

# Optional: change the default logging format. Here we add a timestamp.
#formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
#handler.setFormatter(formatter)
```

By default logs redact the values of URL query strings, the values of some HTTP request and response headers (including `Authorization` which holds the key or token), and the request and response payloads. To create logs without redaction, add `logging_enable = True` to the client constructor:

```python
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
    logging_enable = True
)
```

Note that the log level must be set to `logging.DEBUG` (see above code). Logs will be redacted with any other log level.

Be sure to protect non redacted logs to avoid compromising security.

For more information, see [Configure logging in the Azure libraries for Python](https://aka.ms/azsdk/python/logging)

### Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues). Mention the package name "azure-ai-projects" in the title or content.

## Next steps

Have a look at the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples) folder, containing fully runnable Python code for synchronous and asynchronous clients.

Explore the [AI Starter Template](https://aka.ms/azsdk/azure-ai-projects/python/ai-starter-template). This template creates an Azure AI Foundry hub, project and connected resources including Azure OpenAI Service, AI Search and more. It also deploys a simple chat application to Azure Container Apps.

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[samples]: https://aka.ms/azsdk/azure-ai-projects/python/samples/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[entra_id]: https://learn.microsoft.com/azure/ai-services/authentication?tabs=powershell#authenticate-with-microsoft-entra-id
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/
[evaluators]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk
[azure_ai_evaluation]: https://learn.microsoft.com/python/api/overview/azure/ai-evaluation-readme
[evaluator_library]: https://learn.microsoft.com/azure/ai-studio/how-to/evaluate-generative-ai-app#view-and-manage-the-evaluators-in-the-evaluator-library
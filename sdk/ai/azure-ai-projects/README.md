# Azure AI Projects client library for Python

The AI Projects client library (in preview) is part of the Azure AI Foundry SDK, and provides easy access to
resources in your Azure AI Foundry Project. Use it to:

* **Create and run Agents** using methods on the `.agents` client property.
* **Get an AzureOpenAI client** using the `.get_openai_client()` client method.
* **Enumerate AI Models** deployed to your Foundry Project using methods on the `.deployments` client property.
* **Enumerate connected Azure resources** in your Foundry project using methods on the `.connections` client property.
* **Upload documents and create Datasets** to reference them using methods on the `.datasets` client property.
* **Create and enumerate Search Indexes** using methods on the `.indexes` client property.

The client library uses version `v1` of the AI Foundry [data plane REST APIs](https://aka.ms/azsdk/azure-ai-projects/ga-rest-api-reference).

[Product documentation](https://aka.ms/azsdk/azure-ai-projects/product-doc)
| [Samples][samples]
| [API reference documentation](https://aka.ms/azsdk/azure-ai-projects/python/reference)
| [Package (PyPI)](https://aka.ms/azsdk/azure-ai-projects/python/package)
| [SDK source code](https://aka.ms/azsdk/azure-ai-projects/python/code)

## Reporting issues

To report an issue with the client library, or request additional features, please open a [GitHub issue here](https://github.com/Azure/azure-sdk-for-python/issues). Mention the package name "azure-ai-projects" in the title or content.

## Getting started

### Prerequisite

- Python 3.9 or later.
- An [Azure subscription][azure_sub].
- A [project in Azure AI Foundry](https://learn.microsoft.com/azure/ai-studio/how-to/create-projects).
- The project endpoint URL of the form `https://your-ai-services-account-name.services.ai.azure.com/api/projects/your-project-name`. It can be found in your Azure AI Foundry Project overview page. Below we will assume the environment variable `PROJECT_ENDPOINT` was defined to hold this value.
- An Entra ID token for authentication. Your application needs an object that implements the [TokenCredential](https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.tokencredential) interface. Code samples here use [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential). To get that working, you will need:
  * An appropriate role assignment. see [Role-based access control in Azure AI Foundry portal](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-ai-foundry). Role assigned can be done via the "Access Control (IAM)" tab of your Azure AI Project resource in the Azure portal.
  * [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed.
  * You are logged into your Azure account by running `az login`.

### Install the package

```bash
pip install azure-ai-projects
```

Note that the dependent package [azure-ai-agents](https://pypi.org/project/azure-ai-agents/) will be install as a result, if not already installed, to support `.agent` operations on the client.

## Key concepts

### Create and authenticate the client with Entra ID

Entra ID is the only authentication method supported at the moment by the client.

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

and update the code above to import `asyncio`, import `AIProjectClient` from the `azure.ai.projects.aio` package, and import `DefaultAzureCredential` from the `azure.identity.aio` package:

```python
import os
import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ["PROJECT_ENDPOINT"],
)
```

**Note:** Support for project connection string and hub-based projects has been discontinued. We recommend creating a new Azure AI Foundry resource utilizing project endpoint. If this is not possible, please pin the version of `azure-ai-projects` to `1.0.0b10` or earlier.

## Examples

### Performing Agent operations

The `.agents` property on the `AIProjectsClient` gives you access to an authenticated `AgentsClient` from the `azure-ai-agents` package. Below we show how to create an Agent and delete it. To see what you can do with the Agent you created, see the [many samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/samples) and the [README.md](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents) file of the dependent `azure-ai-agents` package.

The code below assumes the following:

* `model_deployment_name` (a string) is defined. It's the deployment name of an AI model in your Foundry Project, as shown in the "Models + endpoints" tab, under the "Name" column.
* `connection_name` (a string) is defined. It's the name of the connection to a resource of type "Azure OpenAI", as shown in the "Connected resources" tab, under the "Name" column, in the "Management Center" of your Foundry Project.

<!-- SNIPPET:sample_agents.agents_sample -->

```python
agent = project_client.agents.create_agent(
    model=model_deployment_name,
    name="my-agent",
    instructions="You are helpful agent",
)
print(f"Created agent, agent ID: {agent.id}")

# Do something with your Agent!
# See samples here https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/samples

project_client.agents.delete_agent(agent.id)
print("Deleted agent")
```

<!-- END SNIPPET -->

### Get an authenticated AzureOpenAI client

Your Azure AI Foundry project may have one or more AI models deployed that support chat completions or responses.
These could be OpenAI models, Microsoft models, or models from other providers.
Use the code below to get an authenticated [AzureOpenAI](https://github.com/openai/openai-python?tab=readme-ov-file#microsoft-azure-openai)
from the [openai](https://pypi.org/project/openai/) package, and execute a chat completions or responses calls.

The code below assumes `model_deployment_name` (a string) is defined. It's the deployment name of an AI model in your
Foundry Project, or a connected Azure OpenAI resource. As shown in the "Models + endpoints" tab, under the "Name" column.

Update the `api_version` value with one found in the "Data plane - inference" row [in this table](https://learn.microsoft.com/azure/ai-foundry/openai/reference#api-specs).

#### Chat completions with AzureOpenAI client

<!-- SNIPPET:sample_chat_completions_with_azure_openai_client.aoai_chat_completions_sample-->

```python
print(
    "Get an authenticated Azure OpenAI client for the parent AI Services resource, and perform a chat completion operation:"
)
with project_client.get_openai_client(api_version="2024-10-21") as client:

    response = client.chat.completions.create(
        model=model_deployment_name,
        messages=[
            {
                "role": "user",
                "content": "How many feet are in a mile?",
            },
        ],
    )

    print(response.choices[0].message.content)

print(
    "Get an authenticated Azure OpenAI client for a connected Azure OpenAI service, and perform a chat completion operation:"
)
with project_client.get_openai_client(api_version="2024-10-21", connection_name=connection_name) as client:

    response = client.chat.completions.create(
        model=model_deployment_name,
        messages=[
            {
                "role": "user",
                "content": "How many feet are in a mile?",
            },
        ],
    )

    print(response.choices[0].message.content)
```

<!-- END SNIPPET -->

See the "inference" folder in the [package samples][samples] for additional samples.

#### Responses with AzureOpenAI client

<!-- SNIPPET:sample_responses_with_azure_openai_client.aoai_responses_sample-->

```python
print(
    "Get an authenticated Azure OpenAI client for the parent AI Services resource, and perform a 'responses' operation:"
)
with project_client.get_openai_client(api_version="2025-04-01-preview") as client:

    response = client.responses.create(
        model=model_deployment_name,
        input="How many feet are in a mile?",
    )

    print(response.output_text)

print(
    "Get an authenticated Azure OpenAI client for a connected Azure OpenAI service, and perform a 'responses' operation:"
)
with project_client.get_openai_client(
    api_version="2025-04-01-preview", connection_name=connection_name
) as client:

    response = client.responses.create(
        model=model_deployment_name,
        input="How many feet are in a mile?",
    )

    print(response.output_text)
```

<!-- END SNIPPET -->

See the "inference" folder in the [package samples][samples] for additional samples.

### Deployments operations

The code below shows some Deployments operations, which allow you to enumerate the AI models deployed to your AI Foundry Projects. These models can be seen in the "Models + endpoints" tab in your AI Foundry Project. Full samples can be found under the "deployment" folder in the [package samples][samples].

<!-- SNIPPET:sample_deployments.deployments_sample-->

```python
print("List all deployments:")
for deployment in project_client.deployments.list():
    print(deployment)

print(f"List all deployments by the model publisher `{model_publisher}`:")
for deployment in project_client.deployments.list(model_publisher=model_publisher):
    print(deployment)

print(f"List all deployments of model `{model_name}`:")
for deployment in project_client.deployments.list(model_name=model_name):
    print(deployment)

print(f"Get a single deployment named `{model_deployment_name}`:")
deployment = project_client.deployments.get(model_deployment_name)
print(deployment)

# At the moment, the only deployment type supported is ModelDeployment
if isinstance(deployment, ModelDeployment):
    print(f"Type: {deployment.type}")
    print(f"Name: {deployment.name}")
    print(f"Model Name: {deployment.model_name}")
    print(f"Model Version: {deployment.model_version}")
    print(f"Model Publisher: {deployment.model_publisher}")
    print(f"Capabilities: {deployment.capabilities}")
    print(f"SKU: {deployment.sku}")
    print(f"Connection Name: {deployment.connection_name}")
```

<!-- END SNIPPET -->

### Connections operations

The code below shows some Connection operations, which allow you to enumerate the Azure Resources connected to your AI Foundry Projects. These connections can be seen in the "Management Center", in the "Connected resources" tab in your AI Foundry Project. Full samples can be found under the "connections" folder in the [package samples][samples].

<!-- SNIPPET:sample_connections.connections_sample-->

```python
print("List all connections:")
for connection in project_client.connections.list():
    print(connection)

print("List all connections of a particular type:")
for connection in project_client.connections.list(
    connection_type=ConnectionType.AZURE_OPEN_AI,
):
    print(connection)

print("Get the default connection of a particular type, without its credentials:")
connection = project_client.connections.get_default(connection_type=ConnectionType.AZURE_OPEN_AI)
print(connection)

print("Get the default connection of a particular type, with its credentials:")
connection = project_client.connections.get_default(
    connection_type=ConnectionType.AZURE_OPEN_AI, include_credentials=True
)
print(connection)

print(f"Get the connection named `{connection_name}`, without its credentials:")
connection = project_client.connections.get(connection_name)
print(connection)

print(f"Get the connection named `{connection_name}`, with its credentials:")
connection = project_client.connections.get(connection_name, include_credentials=True)
print(connection)
```

<!-- END SNIPPET -->

### Dataset operations

The code below shows some Dataset operations. Full samples can be found under the "datasets"
folder in the [package samples][samples].

<!-- SNIPPET:sample_datasets.datasets_sample-->

```python
print(
    f"Upload a single file and create a new Dataset `{dataset_name}`, version `{dataset_version_1}`, to reference the file."
)
dataset: DatasetVersion = project_client.datasets.upload_file(
    name=dataset_name,
    version=dataset_version_1,
    file_path=data_file,
    connection_name=connection_name,
)
print(dataset)

print(
    f"Upload files in a folder (including sub-folders) and create a new version `{dataset_version_2}` in the same Dataset, to reference the files."
)
dataset = project_client.datasets.upload_folder(
    name=dataset_name,
    version=dataset_version_2,
    folder=data_folder,
    connection_name=connection_name,
    file_pattern=re.compile(r"\.(txt|csv|md)$", re.IGNORECASE),
)
print(dataset)

print(f"Get an existing Dataset version `{dataset_version_1}`:")
dataset = project_client.datasets.get(name=dataset_name, version=dataset_version_1)
print(dataset)

print(f"Get credentials of an existing Dataset version `{dataset_version_1}`:")
dataset_credential = project_client.datasets.get_credentials(name=dataset_name, version=dataset_version_1)
print(dataset_credential)

print("List latest versions of all Datasets:")
for dataset in project_client.datasets.list():
    print(dataset)

print(f"Listing all versions of the Dataset named `{dataset_name}`:")
for dataset in project_client.datasets.list_versions(name=dataset_name):
    print(dataset)

print("Delete all Dataset versions created above:")
project_client.datasets.delete(name=dataset_name, version=dataset_version_1)
project_client.datasets.delete(name=dataset_name, version=dataset_version_2)
```

<!-- END SNIPPET -->

### Indexes operations

The code below shows some Indexes operations. Full samples can be found under the "indexes"
folder in the [package samples][samples].

<!-- SNIPPET:sample_indexes.indexes_sample-->

```python
print(
    f"Create Index `{index_name}` with version `{index_version}`, referencing an existing AI Search resource:"
)
index = project_client.indexes.create_or_update(
    name=index_name,
    version=index_version,
    index=AzureAISearchIndex(connection_name=ai_search_connection_name, index_name=ai_search_index_name),
)
print(index)

print(f"Get Index `{index_name}` version `{index_version}`:")
index = project_client.indexes.get(name=index_name, version=index_version)
print(index)

print("List latest versions of all Indexes:")
for index in project_client.indexes.list():
    print(index)

print(f"Listing all versions of the Index named `{index_name}`:")
for index in project_client.indexes.list_versions(name=index_name):
    print(index)

print(f"Delete Index `{index_name}` version `{index_version}`:")
project_client.indexes.delete(name=index_name, version=index_version)
```

<!-- END SNIPPET -->

## Tracing

The AI Projects client library can be configured to emit OpenTelemetry traces for all its REST API calls. These can be viewed in the "Tracing" tab in your AI Foundry Project page, once you add an Application Insights resource and configured your application appropriately. Agent operations (via the `.agents` property) can also be instrumented, as well as OpenAI client library operations (client created by calling `get_openai_client()` method). For local debugging purposes, traces can also be omitted to the console. For more information see:

* [Trace AI applications using OpenAI SDK](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/trace-application)
* Chat-completion samples with console or Azure Monitor tracing enabled. See `samples\inference\azure-openai` folder.
* The Tracing section in the [README.md file of the azure-ai-agents package](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/README.md#tracing).

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

The client uses the standard [Python logging library](https://docs.python.org/3/library/logging.html). The SDK logs HTTP request and response details, which may be useful in troubleshooting. To log to stdout, add the following at the top of your Python script:

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

By default logs redact the values of URL query strings, the values of some HTTP request and response headers (including `Authorization` which holds the key or token), and the request and response payloads. To create logs without redaction, add `logging_enable=True` to the client constructor:

```python
project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ["PROJECT_ENDPOINT"],
    logging_enable=True
)
```

Note that the log level must be set to `logging.DEBUG` (see above code). Logs will be redacted with any other log level.

Be sure to protect non redacted logs to avoid compromising security.

For more information, see [Configure logging in the Azure libraries for Python](https://aka.ms/azsdk/python/logging)

### Reporting issues

To report an issue with the client library, or request additional features, please open a [GitHub issue here](https://github.com/Azure/azure-sdk-for-python/issues). Mention the package name "azure-ai-projects" in the title or content.

## Next steps

Have a look at the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples) folder, containing fully runnable Python code for synchronous and asynchronous clients.

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
[azure_sub]: https://azure.microsoft.com/free/

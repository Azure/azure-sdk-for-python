# Azure AI Projects client library for Python

Use the AI Projects client library (in preview) to:

* **Enumerate AI Models** deployed to your Azure AI Foundry project.
* **Enumerate connected Azure resources** and get their properties.
* **Upload documents and create Datasets** to reference them.
* **Create and enumerate search Indexes**.
* **Get an authenticated Assistant client**.
* **Get an authenticated Inference client** (Azure OpenAI or Azure AI Inference) for chat completions, text or image embeddings.
* **Read a Prompty file or string** and render messages for inference clients.
* **Run Evaluations** to assess the performance of generative AI applications.
* **Enable OpenTelemetry tracing**.

[Product documentation](https://aka.ms/azsdk/azure-ai-projects/product-doc)
| [Samples][samples]
| [API reference documentation](https://aka.ms/azsdk/azure-ai-projects/python/reference)
| [Package (PyPI)](https://aka.ms/azsdk/azure-ai-projects/python/package)
| [SDK source code](https://aka.ms/azsdk/azure-ai-projects/python/code)
| [AI Starter Template](https://aka.ms/azsdk/azure-ai-projects/python/ai-starter-template)

## Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues). Mention the package name "azure-ai-projects" in the title or content.

## Getting started

### Prerequisite

- Python 3.8 or later.
- An [Azure subscription][azure_sub].
- A [project in Azure AI Foundry](https://learn.microsoft.com/azure/ai-studio/how-to/create-projects).
- The project endpoint URL, of the form `https://<your-ai-services-account-name>.services.ai.azure.com/api/projects/<your-project-name>`. It can be found in your Azure AI Foundry project overview page, under "Project details". Below we will assume the environment variable `PROJECT_ENDPOINT` was defined to hold this value.
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

### Getting an authenticated Assistant client

Below is a code example of how to get an authenticated `AssistantsClient` from the `azure-ai-assistants` package.
Full samples can be found under the `assistants` folder in the [package samples][samples].

<!-- SNIPPET:sample_get_assistants_client.assistants_sample -->

```python
with project_client.assistants.get_client() as client:
    # TODO: Do something with the assistants client...
    pass
```

<!-- END SNIPPET -->

### Get an authenticated ChatCompletionsClient

Your Azure AI Foundry project may have one or more AI models deployed that support chat completions. These could be OpenAI models, Microsoft models, or models from other providers. Use the code below to get an authenticated [ChatCompletionsClient](https://learn.microsoft.com/python/api/azure-ai-inference/azure.ai.inference.chatcompletionsclient) from the [azure-ai-inference](https://pypi.org/project/azure-ai-inference/) package, and execute a chat completions call.

First, install the package:

```bash
pip install azure-ai-inference
```

Then run the code below. Here we assume `model_deployment_name` holds the model deployment name.

<!-- SNIPPET:sample_chat_completions_with_azure_ai_inference_client.inference_sample-->

```python
with project_client.inference.get_chat_completions_client() as client:

    response = client.complete(
        model=model_deployment_name, messages=[UserMessage(content="How many feet are in a mile?")]
    )

    print(response.choices[0].message.content)
```

<!-- END SNIPPET -->

See the "inference" folder in the [package samples][samples] for additional samples, including getting an authenticated [EmbeddingsClient](https://learn.microsoft.com/python/api/azure-ai-inference/azure.ai.inference.embeddingsclient) and [ImageEmbeddingsClient](https://learn.microsoft.com/python/api/azure-ai-inference/azure.ai.inference.imageembeddingsclient).


### Get an authenticated AzureOpenAI client

Your Azure AI Foundry project may have one or more OpenAI models deployed that support chat completions. Use the code below to get an authenticated [AzureOpenAI](https://github.com/openai/openai-python?tab=readme-ov-file#microsoft-azure-openai) from the [openai](https://pypi.org/project/openai/) package, and execute a chat completions call.

First, install the package:

```bash
pip install openai
```

Then run the code below. Here we assume `model_deployment_name` holds the model deployment name. Update the `api_version`
value with one found in the "Data plane - inference" row [in this table](https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs).
You also have the option (not shown) to explicitly specify the Azure OpenAI connection name in your AI Foundry Project, which
the `get_azure_openai_client` method will use to get the inference endpoint and authentication credentials.
If not present the default Azure OpenAI connection will be used.

<!-- SNIPPET:sample_chat_completions_with_azure_openai_client.aoai_sample-->

```python
with project_client.inference.get_azure_openai_client(api_version="2024-06-01") as client:

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

### Deployments operations

The code below shows some Deployments operations. Full samples can be found under the "deployment"
folder in the [package samples][samples].

<!-- SNIPPET:sample_deployments.deployments_sample-->

```python
print("List all deployments:")
for deployment in project_client.deployments.list():
    print(deployment)

print(f"List all deployments by the model publisher `{model_publisher}`:")
for deployment in project_client.deployments.list(model_publisher=model_publisher):
    print(deployment)

print(f"Get a single deployment named `{model_deployment_name}`:")
deployment = project_client.deployments.get(model_deployment_name)
print(deployment)
```

<!-- END SNIPPET -->

### Connections operations

The code below shows some Connection operations. Full samples can be found under the "connetions"
folder in the [package samples][samples].

<!-- SNIPPET:sample_connections.connections_sample-->

```python
print("List the properties of all connections:")
for connection in project_client.connections.list():
    print(connection)

print("List the properties of all connections of a particular type (in this case, Azure OpenAI connections):")
for connection in project_client.connections.list(
    connection_type=ConnectionType.AZURE_OPEN_AI,
):
    print(connection)

print(f"Get the properties of a connection named `{connection_name}`:")
connection = project_client.connections.get(connection_name)
print(connection)
```

<!-- END SNIPPET -->

### Dataset operations

The code below shows some Dataset operations. Full samples can be found under the "datasets"
folder in the [package samples][samples].

<!-- SNIPPET:sample_datasets.datasets_sample-->

```python
print(
    "Upload a single file and create a new Dataset to reference the file. Here we explicitly specify the dataset version."
)
dataset: DatasetVersion = project_client.datasets.upload_file_and_create(
    name=dataset_name,
    version="1",
    file="sample_folder/sample_file1.txt",
)
print(dataset)

"""
print("Upload all files in a folder (including subfolders) to the existing Dataset to reference the folder. Here again we explicitly specify the a new dataset version")
dataset = project_client.datasets.upload_folder_and_create(
    name=dataset_name,
    version="2",
    folder="sample_folder",
)
print(dataset)

print("Upload a single file to the existing dataset, while letting the service increment the version")
dataset: DatasetVersion = project_client.datasets.upload_file_and_create(
    name=dataset_name,
    file="sample_folder/file2.txt",
)
print(dataset)

print("Get an existing Dataset version `1`:")
dataset = project_client.datasets.get_version(name=dataset_name, version="1")
print(dataset)

print(f"Listing all versions of the Dataset named `{dataset_name}`:")
for dataset in project_client.datasets.list_versions(name=dataset_name):
    print(dataset)

print("List latest versions of all Datasets:")
for dataset in project_client.datasets.list_latest():
    print(dataset)

print("Delete all Dataset versions created above:")
project_client.datasets.delete_version(name=dataset_name, version="1")
project_client.datasets.delete_version(name=dataset_name, version="2")
project_client.datasets.delete_version(name=dataset_name, version="3")
"""
```

<!-- END SNIPPET -->

### Indexes operations

The code below shows some Indexes operations. Full samples can be found under the "indexes"
folder in the [package samples][samples].

<!-- SNIPPET:sample_indexes.indexes_sample-->

```python
print(f"Listing all versions of the Index named `{index_name}`:")
for index in project_client.indexes.list_versions(name=index_name):
    print(index)
exit()

print("Get an existing Index version `1`:")
index = project_client.indexes.get_version(name=index_name, version="1")
print(index)

print("List latest versions of all Indexes:")
for index in project_client.indexes.list_latest():
    print(index)

print("Delete the Index versions created above:")
project_client.indexes.delete_version(name=index_name, version="1")
project_client.indexes.delete_version(name=index_name, version="2")
```

<!-- END SNIPPET -->

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
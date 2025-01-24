
# Azure AI Projects client library for Python

Use the AI Projects client library (in preview) to:

* **Enumerate connections** in your Azure AI Foundry project and get connection properties.
For example, get the inference endpoint URL and credentials associated with your Azure OpenAI connection.
* **Get an authenticated Inference client** to do chat completions, for the default Azure OpenAI or AI Services connections in your Azure AI Foundry project. Supports the AzureOpenAI client from the `openai` package, or clients from the `azure-ai-inference` package.
* **Develop Agents using the Azure AI Agent Service**, leveraging an extensive ecosystem of models, tools, and capabilities from OpenAI, Microsoft, and other LLM providers. The Azure AI Agent Service enables the building of Agents for a wide range of generative AI use cases. The package is currently in private preview.
* **Run Evaluations** to assess the performance of generative AI applications using various evaluators and metrics. It includes built-in evaluators for quality, risk, and safety, and allows custom evaluators for specific needs.
* **Enable OpenTelemetry tracing**.

[Product documentation](https://aka.ms/azsdk/azure-ai-projects/product-doc)
| [Samples][samples]
| [API reference documentation](https://aka.ms/azsdk/azure-ai-projects/python/reference)
| [Package (PyPI)](https://aka.ms/azsdk/azure-ai-projects/python/package)
| [SDK source code](https://aka.ms/azsdk/azure-ai-projects/python/code)
| [AI Starter Template](https://aka.ms/azsdk/azure-ai-projects/python/ai-starter-template)

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
  - [Agents (Private Preview)](#agents-private-preview)
    - [Create an Agent](#create-agent) with:
      - [File Search](#create-agent-with-file-search)
      - [Enterprise File Search](#create-agent-with-enterprise-file-search)
      - [Code interpreter](#create-agent-with-code-interpreter)
      - [Bing grounding](#create-agent-with-bing-grounding)
      - [Azure AI Search](#create-agent-with-azure-ai-search)
      - [Function call](#create-agent-with-function-call)
      - [Azure Function Call](#create-agent-with-azure-function-call)
      - [OpenAPI](#create-agent-with-openapi)
    - [Create thread](#create-thread) with
      - [Tool resource](#create-thread-with-tool-resource)
    - [Create message](#create-message) with:
      - [File search attachment](#create-message-with-file-search-attachment)
      - [Code interpreter attachment](#create-message-with-code-interpreter-attachment)
    - [Execute Run, Run_and_Process, or Stream](#create-run-run_and_process-or-stream)
    - [Retrieve message](#retrieve-message)
    - [Retrieve file](#retrieve-file)
    - [Tear down by deleting resource](#teardown)
    - [Tracing](#tracing)
  - [Evaluation](#evaluation)
    - [Evaluator](#evaluator)
    - [Run Evaluation in the cloud](#run-evaluation-in-the-cloud)
      - [Evaluators](#evaluators)
      - [Data to be evaluated](#data-to-be-evaluated)
        - [[Optional] Azure OpenAI Model](#optional-azure-openai-model)
        - [Example Remote Evaluation](#example-remote-evaluation)
  - [Tracing](#tracing)
    - [Installation](#installation)
    - [Tracing example](#tracing-example)
- [Troubleshooting](#troubleshooting)
  - [Exceptions](#exceptions)
  - [Logging](#logging)
  - [Reporting issues](#reporting-issues)
- [Next steps](#next-steps)
- [Contributing](#contributing)

## Getting started

### Prerequisite

- Python 3.8 or later.
- An [Azure subscription][azure_sub].
- A [project in Azure AI Foundry](https://learn.microsoft.com/azure/ai-studio/how-to/create-projects).
- The project connection string. It can be found in your Azure AI Foundry project overview page, under "Project details". Below we will assume the environment variable `PROJECT_CONNECTION_STRING` was defined to hold this value.
- Entra ID is needed to authenticate the client. Your application needs an object that implements the [TokenCredential](https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.tokencredential) interface. Code samples here use [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential). To get that working, you will need:
  * The `Contributor` role. Role assigned can be done via the "Access Control (IAM)" tab of your Azure AI Project resource in the Azure portal.
  * [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed.
  * You are logged into your Azure account by running `az login`.
  * Note that if you have multiple Azure subscriptions, the subscription that contains your Azure AI Project resource must be your default subscription. Run `az account list --output table` to list all your subscription and see which one is the default. Run `az account set --subscription "Your Subscription ID or Name"` to change your default subscription.

### Install the package

```bash
pip install azure-ai-projects
```

## Key concepts

### Create and authenticate the client

The class factory method `from_connection_string` is used to construct the client. To construct a synchronous client:

```python
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
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
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
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

### Agents (Private Preview)

Agents in the Azure AI Projects client library are designed to facilitate various interactions and operations within your AI projects. They serve as the core components that manage and execute tasks, leveraging different tools and resources to achieve specific goals. The following steps outline the typical sequence for interacting with Agents. See the "agents" folder in the [package samples][samples] for additional Agent samples.

Agents are actively being developed. A sign-up form for private preview is coming soon.

#### Create Agent

Here is an example of how to create an Agent:
<!-- SNIPPET:sample_agents_basics.create_agent -->

```python
agent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-assistant",
    instructions="You are helpful assistant",
)
```

<!-- END SNIPPET -->

To allow Agents to access your resources or custom functions, you need tools. You can pass tools to `create_agent` by either `toolset` or combination of `tools` and `tool_resources`.

Here is an example of `toolset`:
<!-- SNIPPET:sample_agents_run_with_toolset.create_agent_toolset -->

```python
functions = FunctionTool(user_functions)
code_interpreter = CodeInterpreterTool()

toolset = ToolSet()
toolset.add(functions)
toolset.add(code_interpreter)

agent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-assistant",
    instructions="You are a helpful assistant",
    toolset=toolset,
)
```

<!-- END SNIPPET -->

Also notices that if you use asynchronous client, you use `AsyncToolSet` instead.  Additional information related to `AsyncFunctionTool` be discussed in the later sections.

Here is an example to use `tools` and `tool_resources`:
<!-- SNIPPET:sample_agents_vector_store_batch_file_search.create_agent_with_tools_and_tool_resources -->

```python
file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

# Notices that FileSearchTool as tool and tool_resources must be added or the assistant unable to search the file
agent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-assistant",
    instructions="You are helpful assistant",
    tools=file_search_tool.definitions,
    tool_resources=file_search_tool.resources,
)
```

<!-- END SNIPPET -->

In the following sections, we show you sample code in either `toolset` or combination of `tools` and `tool_resources`.

#### Create Agent with File Search

To perform file search by an Agent, we first need to upload a file, create a vector store, and associate the file to the vector store. Here is an example:

<!-- SNIPPET:sample_agents_file_search.upload_file_create_vector_store_and_agent_with_file_search_tool -->

```python
file = project_client.agents.upload_file_and_poll(file_path="product_info_1.md", purpose="assistants")
print(f"Uploaded file, file ID: {file.id}")

vector_store = project_client.agents.create_vector_store_and_poll(file_ids=[file.id], name="my_vectorstore")
print(f"Created vector store, vector store ID: {vector_store.id}")

# Create file search tool with resources followed by creating agent
file_search = FileSearchTool(vector_store_ids=[vector_store.id])

agent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-assistant",
    instructions="Hello, you are helpful assistant and can search information from uploaded files",
    tools=file_search.definitions,
    tool_resources=file_search.resources,
)
```

<!-- END SNIPPET -->

#### Create Agent with Enterprise File Search

We can upload file to Azure as it is shown in the example, or use the existing Azure blob storage. In the code below we demonstrate how this can be achieved. First we upload file to azure and create `VectorStoreDataSource`, which then is used to create vector store. This vector store is then given to the `FileSearchTool` constructor.

<!-- SNIPPET:sample_agents_enterprise_file_search.upload_file_and_create_agent_with_file_search -->

```python
# We will upload the local file to Azure and will use it for vector store creation.
_, asset_uri = project_client.upload_file("./product_info_1.md")

# Create a vector store with no file and wait for it to be processed
ds = VectorStoreDataSource(asset_identifier=asset_uri, asset_type=VectorStoreDataSourceAssetType.URI_ASSET)
vector_store = project_client.agents.create_vector_store_and_poll(data_sources=[ds], name="sample_vector_store")
print(f"Created vector store, vector store ID: {vector_store.id}")

# Create a file search tool
file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

# Notices that FileSearchTool as tool and tool_resources must be added or the assistant unable to search the file
agent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-assistant",
    instructions="You are helpful assistant",
    tools=file_search_tool.definitions,
    tool_resources=file_search_tool.resources,
)
```

<!-- END SNIPPET -->

We also can attach files to the existing vector store. In the code snippet below, we first create an empty vector store and add file to it.

<!-- SNIPPET:sample_agents_vector_store_batch_enterprise_file_search.attach_files_to_store -->

```python
# Create a vector store with no file and wait for it to be processed
vector_store = project_client.agents.create_vector_store_and_poll(data_sources=[], name="sample_vector_store")
print(f"Created vector store, vector store ID: {vector_store.id}")

ds = VectorStoreDataSource(asset_identifier=asset_uri, asset_type=VectorStoreDataSourceAssetType.URI_ASSET)
# Add the file to the vector store or you can supply data sources in the vector store creation
vector_store_file_batch = project_client.agents.create_vector_store_file_batch_and_poll(
    vector_store_id=vector_store.id, data_sources=[ds]
)
print(f"Created vector store file batch, vector store file batch ID: {vector_store_file_batch.id}")

# Create a file search tool
file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])
```

<!-- END SNIPPET -->

#### Create Agent with Code Interpreter

Here is an example to upload a file and use it for code interpreter by an Agent:

<!-- SNIPPET:sample_agents_code_interpreter.upload_file_and_create_agent_with_code_interpreter -->

```python
file = project_client.agents.upload_file_and_poll(
    file_path="nifty_500_quarterly_results.csv", purpose=FilePurpose.AGENTS
)
print(f"Uploaded file, file ID: {file.id}")

code_interpreter = CodeInterpreterTool(file_ids=[file.id])

# Create agent with code interpreter tool and tools_resources
agent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-assistant",
    instructions="You are helpful assistant",
    tools=code_interpreter.definitions,
    tool_resources=code_interpreter.resources,
)
```

<!-- END SNIPPET -->

#### Create Agent with Bing Grounding

To enable your Agent to perform search through Bing search API, you use `BingGroundingTool` along with a connection.

Here is an example:

<!-- SNIPPET:sample_agents_bing_grounding.create_agent_with_bing_grounding_tool -->

```python
bing_connection = project_client.connections.get(connection_name=os.environ["BING_CONNECTION_NAME"])
conn_id = bing_connection.id

print(conn_id)

# Initialize agent bing tool and add the connection id
bing = BingGroundingTool(connection_id=conn_id)

# Create agent with the bing tool and process assistant run
with project_client:
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
        tools=bing.definitions,
        headers={"x-ms-enable-preview": "true"},
    )
```

<!-- END SNIPPET -->

#### Create Agent with Azure AI Search

Azure AI Search is an enterprise search system for high-performance applications. It integrates with Azure OpenAI Service and Azure Machine Learning, offering advanced search technologies like vector search and full-text search. Ideal for knowledge base insights, information discovery, and automation

Here is an example to integrate Azure AI Search:

<!-- SNIPPET:sample_agents_azure_ai_search.create_agent_with_azure_ai_search_tool -->

```python
conn_list = project_client.connections.list()
conn_id = ""
for conn in conn_list:
    if conn.connection_type == "CognitiveSearch":
        conn_id = conn.id
        break

print(conn_id)

# Initialize agent AI search tool and add the search index connection id
ai_search = AzureAISearchTool(index_connection_id=conn_id, index_name="myindexname")

# Create agent with AI search tool and process assistant run
with project_client:
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
        tools=ai_search.definitions,
        tool_resources=ai_search.resources,
        headers={"x-ms-enable-preview": "true"},
    )
```

<!-- END SNIPPET -->

#### Create Agent with Function Call

You can enhance your Agents by defining callback functions as function tools. These can be provided to `create_agent` via either the `toolset` parameter or the combination of `tools` and `tool_resources`. Here are the distinctions:

- `toolset`: When using the `toolset` parameter, you provide not only the function definitions and descriptions but also their implementations. The SDK will execute these functions within `create_and_run_process` or `streaming` . These functions will be invoked based on their definitions.
- `tools` and `tool_resources`: When using the `tools` and `tool_resources` parameters, only the function definitions and descriptions are provided to `create_agent`, without the implementations. The `Run` or `event handler of stream` will raise a `requires_action` status based on the function definitions. Your code must handle this status and call the appropriate functions.

For more details about calling functions by code, refer to [`sample_agents_stream_eventhandler_with_functions.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/sample_agents_stream_eventhandler_with_functions.py) and [`sample_agents_functions.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/sample_agents_functions.py).

For more details about requirements and specification of functions, refer to [Function Tool Specifications](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/FunctionTool.md)

Here is an example to use [user functions](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/user_functions.py) in `toolset`:
<!-- SNIPPET:sample_agents_stream_eventhandler_with_toolset.create_agent_with_function_tool -->

```python
functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)

agent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-assistant",
    instructions="You are a helpful assistant",
    toolset=toolset,
)
```

<!-- END SNIPPET -->

For asynchronous functions, you must import `AIProjectClient` from `azure.ai.projects.aio` and use `AsyncFunctionTool`.   Here is an example using [asynchronous user functions](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/async_samples/user_async_functions.py):

```python
from azure.ai.projects.aio import AIProjectClient
```

<!-- SNIPPET:sample_agents_run_with_toolset_async.create_agent_with_async_function_tool -->

```python
functions = AsyncFunctionTool(user_async_functions)

toolset = AsyncToolSet()
toolset.add(functions)

agent = await project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-assistant",
    instructions="You are a helpful assistant",
    toolset=toolset,
)
```

<!-- END SNIPPET -->

#### Create Agent With Azure Function Call

The agent can handle Azure Function calls on the service side and return the result of the call. To use the function we need to create the `AzureFunctionTool`, which contains the input and output queues of azure function and the description of input parameters. Please note that in the prompt we are asking the model to invoke queue when the specific question ("What would foo say?") is being asked. 

<!-- SNIPPET sample_agents_azure_functions.create_agent_with_azure_function_tool -->

```python
azure_function_tool = AzureFunctionTool(
    name="foo",
    description="Get answers from the foo bot.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The question to ask."},
            "outputqueueuri": {"type": "string", "description": "The full output queue uri."},
        },
    },
    input_queue=AzureFunctionStorageQueue(
        queue_name="azure-function-foo-input",
        storage_service_endpoint=storage_service_endpoint,
    ),
    output_queue=AzureFunctionStorageQueue(
        queue_name="azure-function-tool-output",
        storage_service_endpoint=storage_service_endpoint,
    ),
)

agent = project_client.agents.create_agent(
    model="gpt-4",
    name="azure-function-agent-foo",
    instructions=f"You are a helpful support agent. Use the provided function any time the prompt contains the string 'What would foo say?'. When you invoke the function, ALWAYS specify the output queue uri parameter as '{storage_service_endpoint}/azure-function-tool-output'. Always responds with \"Foo says\" and then the response from the tool.",
    tools=azure_function_tool.definitions,
)
print(f"Created agent, agent ID: {agent.id}")
```

<!-- END SNIPPET -->

#### Create Agent With OpenAPI

OpenAPI specifications describe REST operations against a specific endpoint. Agents SDK can read an OpenAPI spec, create a function from it, and call that function against the REST endpoint without additional client-side execution.

Here is an example creating an OpenAPI tool (using anonymous authentication):

<!-- SNIPPET:sample_agents_openapi.create_agent_with_openapi -->

```python

with open("./weather_openapi.json", "r") as f:
    openapi_spec = jsonref.loads(f.read())

# Create Auth object for the OpenApiTool (note that connection or managed identity auth setup requires additional setup in Azure)
auth = OpenApiAnonymousAuthDetails()

# Initialize agent OpenApi tool using the read in OpenAPI spec
openapi = OpenApiTool(
    name="get_weather", spec=openapi_spec, description="Retrieve weather information for a location", auth=auth
)

# Create agent with OpenApi tool and process assistant run
with project_client:
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
        tools=openapi.definitions,
    )
```

<!-- END SNIPPET -->

#### Create Thread

For each session or conversation, a thread is required.   Here is an example:

<!-- SNIPPET:sample_agents_basics.create_thread -->

```python
thread = project_client.agents.create_thread()
```

<!-- END SNIPPET -->

#### Create Thread with Tool Resource

In some scenarios, you might need to assign specific resources to individual threads. To achieve this, you provide the `tool_resources` argument to `create_thread`. In the following example, you create a vector store and upload a file, enable an Agent for file search using the `tools` argument, and then associate the file with the thread using the `tool_resources` argument.

<!-- SNIPPET:sample_agents_with_resources_in_thread.create_agent_and_thread_for_file_search -->

```python
file = project_client.agents.upload_file_and_poll(file_path="product_info_1.md", purpose="assistants")
print(f"Uploaded file, file ID: {file.id}")

vector_store = project_client.agents.create_vector_store_and_poll(file_ids=[file.id], name="my_vectorstore")
print(f"Created vector store, vector store ID: {vector_store.id}")

# Create file search tool with resources followed by creating agent
file_search = FileSearchTool(vector_store_ids=[vector_store.id])

agent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-assistant",
    instructions="Hello, you are helpful assistant and can search information from uploaded files",
    tools=file_search.definitions,
)

print(f"Created agent, ID: {agent.id}")

# Create thread with file resources.
# If the agent has multiple threads, only this thread can search this file.
thread = project_client.agents.create_thread(tool_resources=file_search.resources)
```

<!-- END SNIPPET -->
#### Create Message

To create a message for assistant to process, you pass `user` as `role` and a question as `content`:

<!-- SNIPPET:sample_agents_basics.create_message -->

```python
message = project_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
```

<!-- END SNIPPET -->

#### Create Message with File Search Attachment

To attach a file to a message for content searching, you use `MessageAttachment` and `FileSearchTool`:

<!-- SNIPPET:sample_agents_with_file_search_attachment.create_message_with_attachment -->

```python
attachment = MessageAttachment(file_id=file.id, tools=FileSearchTool().definitions)
message = project_client.agents.create_message(
    thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?", attachments=[attachment]
)
```

<!-- END SNIPPET -->

#### Create Message with Code Interpreter Attachment

To attach a file to a message for data analysis, use `MessageAttachment` and `CodeInterpreterTool` classes. You must pass `CodeInterpreterTool` as `tools` or `toolset` in `create_agent` call or the file attachment cannot be opened for code interpreter.  

Here is an example to pass `CodeInterpreterTool` as tool:

<!-- SNIPPET:sample_agents_with_code_interpreter_file_attachment.create_agent_and_message_with_code_interpreter_file_attachment -->

```python
# Notice that CodeInterpreter must be enabled in the agent creation,
# otherwise the agent will not be able to see the file attachment for code interpretation
agent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-assistant",
    instructions="You are helpful assistant",
    tools=CodeInterpreterTool().definitions,
)
print(f"Created agent, agent ID: {agent.id}")

thread = project_client.agents.create_thread()
print(f"Created thread, thread ID: {thread.id}")

# Create an attachment
attachment = MessageAttachment(file_id=file.id, tools=CodeInterpreterTool().definitions)

# Create a message
message = project_client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="Could you please create bar chart in TRANSPORTATION sector for the operating profit from the uploaded csv file and provide file to me?",
    attachments=[attachment],
)
```

<!-- END SNIPPET -->

Azure blob storage can be used as a message attachment. In this case, use `VectorStoreDataSource` as a data source:

<!-- SNIPPET:sample_agents_code_interpreter_attachment_enterprise_search.upload_file_and_create_message_with_code_interpreter -->

```python
# We will upload the local file to Azure and will use it for vector store creation.
_, asset_uri = project_client.upload_file("./product_info_1.md")
ds = VectorStoreDataSource(asset_identifier=asset_uri, asset_type=VectorStoreDataSourceAssetType.URI_ASSET)

# Create a message with the attachment
attachment = MessageAttachment(data_source=ds, tools=code_interpreter.definitions)
message = project_client.agents.create_message(
    thread_id=thread.id, role="user", content="What does the attachment say?", attachments=[attachment]
)
```

<!-- END SNIPPET -->

#### Create Run, Run_and_Process, or Stream

To process your message, you can use `create_run`, `create_and_process_run`, or `create_stream`.

`create_run` requests the Agent to process the message without polling for the result. If you are using `function tools` regardless as `toolset` or not, your code is responsible for polling for the result and acknowledging the status of `Run`. When the status is `requires_action`, your code is responsible for calling the function tools. For a code sample, visit [`sample_agents_functions.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/sample_agents_functions.py).

Here is an example of `create_run` and poll until the run is completed:

<!-- SNIPPET:sample_agents_basics.create_run -->

```python
run = project_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)

# Poll the run as long as run status is queued or in progress
while run.status in ["queued", "in_progress", "requires_action"]:
    # Wait for a second
    time.sleep(1)
    run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
```

<!-- END SNIPPET -->

To have the SDK poll on your behalf and call `function tools`, use the `create_and_process_run` method. Note that `function tools` will only be invoked if they are provided as `toolset` during the `create_agent` call.

Here is an example:

<!-- SNIPPET:sample_agents_run_with_toolset.create_and_process_run -->

```python
run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
```

<!-- END SNIPPET -->

With streaming, polling need not be considered. If `function tools` are provided as `toolset` during the `create_agent` call, they will be invoked by the SDK.

Here is an example of streaming:

<!-- SNIPPET:sample_agents_stream_iteration.iterate_stream -->

```python
with project_client.agents.create_stream(thread_id=thread.id, assistant_id=agent.id) as stream:

    for event_type, event_data, _ in stream:

        if isinstance(event_data, MessageDeltaChunk):
            print(f"Text delta received: {event_data.text}")

        elif isinstance(event_data, ThreadMessage):
            print(f"ThreadMessage created. ID: {event_data.id}, Status: {event_data.status}")

        elif isinstance(event_data, ThreadRun):
            print(f"ThreadRun status: {event_data.status}")

        elif isinstance(event_data, RunStep):
            print(f"RunStep type: {event_data.type}, Status: {event_data.status}")

        elif event_type == AgentStreamEvent.ERROR:
            print(f"An error occurred. Data: {event_data}")

        elif event_type == AgentStreamEvent.DONE:
            print("Stream completed.")
            break

        else:
            print(f"Unhandled Event Type: {event_type}, Data: {event_data}")
```

<!-- END SNIPPET -->

In the code above, because an `event_handler` object is not passed to the `create_stream` function, the SDK will instantiate `AgentEventHandler` or `AsyncAgentEventHandler` as the default event handler and produce an iterable object with `event_type` and `event_data`.  `AgentEventHandler` and `AsyncAgentEventHandler` are overridable.  Here is an example:

<!-- SNIPPET:sample_agents_stream_eventhandler.stream_event_handler -->

```python
# With AgentEventHandler[str], the return type for each event functions is optional string.
class MyEventHandler(AgentEventHandler[str]):

    def on_message_delta(self, delta: "MessageDeltaChunk") -> Optional[str]:
        return f"Text delta received: {delta.text}"

    def on_thread_message(self, message: "ThreadMessage") -> Optional[str]:
        return f"ThreadMessage created. ID: {message.id}, Status: {message.status}"

    def on_thread_run(self, run: "ThreadRun") -> Optional[str]:
        return f"ThreadRun status: {run.status}"

    def on_run_step(self, step: "RunStep") -> Optional[str]:
        return f"RunStep type: {step.type}, Status: {step.status}"

    def on_error(self, data: str) -> Optional[str]:
        return f"An error occurred. Data: {data}"

    def on_done(self) -> Optional[str]:
        return "Stream completed."

    def on_unhandled_event(self, event_type: str, event_data: Any) -> Optional[str]:
        return f"Unhandled Event Type: {event_type}, Data: {event_data}"
```

<!-- END SNIPPET -->


<!-- SNIPPET:sample_agents_stream_eventhandler.create_stream -->

```python
with project_client.agents.create_stream(
    thread_id=thread.id, assistant_id=agent.id, event_handler=MyEventHandler()
) as stream:
    for event_type, event_data, func_return in stream:
        print(f"Received data.")
        print(f"Streaming receive Event Type: {event_type}")
        print(f"Event Data: {str(event_data)[:100]}...")
        print(f"Event Function return: {func_return}\n")
```

<!-- END SNIPPET -->

As you can see, this SDK parses the events and produces various event types similar to OpenAI assistants. In your use case, you might not be interested in handling all these types and may decide to parse the events on your own. To achieve this, please refer to [override base event handler](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/sample_agents_stream_with_base_override_eventhandler.py).

```
Note: Multiple streaming processes may be chained behind the scenes.

When the SDK receives a `ThreadRun` event with the status `requires_action`, the next event will be `Done`, followed by termination. The SDK will submit the tool calls using the same event handler. The event handler will then chain the main stream with the tool stream.

Consequently, when you iterate over the streaming using a for loop similar to the example above, the for loop will receive events from the main stream followed by events from the tool stream.
```


#### Retrieve Message

To retrieve messages from agents, use the following example:

<!-- SNIPPET:sample_agents_basics.list_messages -->

```python
messages = project_client.agents.list_messages(thread_id=thread.id)

# The messages are following in the reverse order,
# we will iterate them and output only text contents.
for data_point in reversed(messages.data):
    last_message_content = data_point.content[-1]
    if isinstance(last_message_content, MessageTextContent):
        print(f"{data_point.role}: {last_message_content.text.value}")
```

<!-- END SNIPPET -->

In addition, `messages` and `messages.data[]` offer helper properties such as `text_messages`, `image_contents`, `file_citation_annotations`, and `file_path_annotations` to quickly retrieve content from one message or all messages.

### Retrieve File

Files uploaded by Agents cannot be retrieved back. If your use case need to access the file content uploaded by the Agents, you are advised to keep an additional copy accessible by your application. However, files generated by Agents are retrievable by `save_file` or `get_file_content`.

Here is an example retrieving file ids from messages and save to the local drive:

<!-- SNIPPET:sample_agents_code_interpreter.get_messages_and_save_files -->

```python
messages = project_client.agents.list_messages(thread_id=thread.id)
print(f"Messages: {messages}")

for image_content in messages.image_contents:
    file_id = image_content.image_file.file_id
    print(f"Image File ID: {file_id}")
    file_name = f"{file_id}_image_file.png"
    project_client.agents.save_file(file_id=file_id, file_name=file_name)
    print(f"Saved image file to: {Path.cwd() / file_name}")

for file_path_annotation in messages.file_path_annotations:
    print(f"File Paths:")
    print(f"Type: {file_path_annotation.type}")
    print(f"Text: {file_path_annotation.text}")
    print(f"File ID: {file_path_annotation.file_path.file_id}")
    print(f"Start Index: {file_path_annotation.start_index}")
    print(f"End Index: {file_path_annotation.end_index}")
```

<!-- END SNIPPET -->

Here is an example to use `get_file_content`:

```python
from pathlib import Path

async def save_file_content(client, file_id: str, file_name: str, target_dir: Optional[Union[str, Path]] = None):
    # Determine the target directory
    path = Path(target_dir).expanduser().resolve() if target_dir else Path.cwd()
    path.mkdir(parents=True, exist_ok=True)

    # Retrieve the file content
    file_content_stream = await client.get_file_content(file_id)
    if not file_content_stream:
        raise RuntimeError(f"No content retrievable for file ID '{file_id}'.")

    # Collect all chunks asynchronously
    chunks = []
    async for chunk in file_content_stream:
        if isinstance(chunk, (bytes, bytearray)):
            chunks.append(chunk)
        else:
            raise TypeError(f"Expected bytes or bytearray, got {type(chunk).__name__}")

    target_file_path = path / file_name

    # Write the collected content to the file synchronously
    with open(target_file_path, "wb") as file:
        for chunk in chunks:
            file.write(chunk)
```

#### Teardown

To remove resources after completing tasks, use the following functions:

<!-- SNIPPET:sample_agents_file_search.teardown -->

```python
# Delete the file when done
project_client.agents.delete_vector_store(vector_store.id)
print("Deleted vector store")

project_client.agents.delete_file(file_id=file.id)
print("Deleted file")

# Delete the agent when done
project_client.agents.delete_agent(agent.id)
print("Deleted agent")
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

#### Tracing example

Here is a code sample to be included above `create_agent`:

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

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span(scenario):
    with project_client:
```

<!-- END SNIPPET -->

In additional, you might find helpful to see the tracing logs in console. You can achieve by the following code:

```python
project_client.telemetry.enable(destination=sys.stdout)
```

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

To report issues with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues)

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

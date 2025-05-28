<!-- PIPY LONG DESCRIPTION BEGIN -->
# Azure AI Agents client library for Python

Use the AI Agents client library to:

* **Develop Agents using the Azure AI Agents Service**, leveraging an extensive ecosystem of models, tools, and capabilities from OpenAI, Microsoft, and other LLM providers. The Azure AI Agents Service enables the building of Agents for a wide range of generative AI use cases.
* **Note:** While this package can be used independently, we recommend using the Azure AI Projects client library (azure-ai-projects) for an enhanced experience. 
The Projects library provides simplified access to advanced functionality, such as creating and managing agents, enumerating AI models, working with datasets and 
managing search indexes, evaluating generative AI performance, and enabling OpenTelemetry tracing.

[Product documentation](https://aka.ms/azsdk/azure-ai-agents/product-doc)
| [Samples][samples]
| [API reference documentation](https://aka.ms/azsdk/azure-ai-agents/python/reference)
| [Package (PyPI)](https://aka.ms/azsdk/azure-ai-agents/python/package)
| [SDK source code](https://aka.ms/azsdk/azure-ai-agents/python/code)
| [AI Starter Template](https://aka.ms/azsdk/azure-ai-agents/python/ai-starter-template)

## Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues). Mention the package name "azure-ai-agents" in the title or content.

## Table of contents

- [Getting started](#getting-started)
  - [Prerequisite](#prerequisite)
  - [Install the package](#install-the-package)
- [Key concepts](#key-concepts)
  - [Create and authenticate the client](#create-and-authenticate-the-client)
- [Examples](#examples)
  - [Create an Agent](#create-agent) with:
    - [File Search](#create-agent-with-file-search)
    - [Enterprise File Search](#create-agent-with-enterprise-file-search)
    - [Code interpreter](#create-agent-with-code-interpreter)
    - [Bing grounding](#create-agent-with-bing-grounding)
    - [Azure AI Search](#create-agent-with-azure-ai-search)
    - [Function call](#create-agent-with-function-call)
    - [Azure Function Call](#create-agent-with-azure-function-call)
    - [OpenAPI](#create-agent-with-openapi)
    - [Fabric data](#create-an-agent-with-fabric)
  - [Create thread](#create-thread) with
    - [Tool resource](#create-thread-with-tool-resource)
  - [Create message](#create-message) with:
    - [File search attachment](#create-message-with-file-search-attachment)
    - [Code interpreter attachment](#create-message-with-code-interpreter-attachment)
    - [Create Message with Image Inputs](#create-message-with-image-inputs)
  - [Execute Run, Run_and_Process, or Stream](#execute-run-run_and_process-or-stream)
  - [Retrieve message](#retrieve-message)
  - [Retrieve file](#retrieve-file)
  - [Tear down by deleting resource](#teardown)
  - [Tracing](#tracing)
    - [Installation](#installation)
    - [How to enable tracing](#how-to-enable-tracing)
    - [How to trace your own functions](#how-to-trace-your-own-functions)
- [Troubleshooting](#troubleshooting)
  - [Logging](#logging)
  - [Reporting issues](#reporting-issues)
- [Next steps](#next-steps)
- [Contributing](#contributing)
<!-- PIPY LONG DESCRIPTION END -->
## Getting started

### Prerequisite

- Python 3.9 or later.
- An [Azure subscription][azure_sub].
- A [project in Azure AI Foundry](https://learn.microsoft.com/azure/ai-studio/how-to/create-projects).
- The project endpoint string. It can be found in your Azure AI Foundry project overview page, under "Project details". Below we will assume the environment variable `PROJECT_ENDPOINT_STRING` was defined to hold this value.
- Entra ID is needed to authenticate the client. Your application needs an object that implements the [TokenCredential](https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.tokencredential) interface. Code samples here use [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential). To get that working, you will need:
  * An appropriate role assignment. see [Role-based access control in Azure AI Foundry portal](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-ai-foundry). Role assigned can be done via the "Access Control (IAM)" tab of your Azure AI Project resource in the Azure portal.
  * [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed.
  * You are logged into your Azure account by running `az login`.
  * Note that if you have multiple Azure subscriptions, the subscription that contains your Azure AI Project resource must be your default subscription. Run `az account list --output table` to list all your subscription and see which one is the default. Run `az account set --subscription "Your Subscription ID or Name"` to change your default subscription.

### Install the package

```bash
pip install azure-ai-agents
```

## Key concepts

### Create and authenticate the client

To construct a synchronous client:

```python
import os
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
```

To construct an asynchronous client, Install the additional package [aiohttp](https://pypi.org/project/aiohttp/):

```bash
pip install aiohttp
```

and update the code above to import `asyncio`, and import `AgentsClient` from the `azure.ai.agents.aio` namespace:

```python
import os
import asyncio
from azure.ai.agents.aio import AgentsClient
from azure.core.credentials import AzureKeyCredential

agent_client = AgentsClient(
   endpoint=os.environ["PROJECT_ENDPOINT"],
   credential=DefaultAzureCredential(),
)
```

## Examples

### Create Agent

Before creating an Agent, you need to set up Azure resources to deploy your model. [Create a New Agent Quickstart](https://learn.microsoft.com/azure/ai-services/agents/quickstart?pivots=programming-language-python-azure) details selecting and deploying your Agent Setup.

Here is an example of how to create an Agent:
<!-- SNIPPET:sample_agents_basics.create_agent -->

```python

    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are helpful agent",
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

# To enable tool calls executed automatically
agents_client.enable_auto_function_calls(toolset)

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are a helpful agent",
    toolset=toolset,
)
```

<!-- END SNIPPET -->

Also notices that if you use asynchronous client, you use `AsyncToolSet` instead.  Additional information related to `AsyncFunctionTool` be discussed in the later sections.

Here is an example to use `tools` and `tool_resources`:
<!-- SNIPPET:sample_agents_vector_store_batch_file_search.create_agent_with_tools_and_tool_resources -->

```python
file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

# Notices that FileSearchTool as tool and tool_resources must be added or the agent unable to search the file
agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are helpful agent",
    tools=file_search_tool.definitions,
    tool_resources=file_search_tool.resources,
)
```

<!-- END SNIPPET -->

In the following sections, we show you sample code in either `toolset` or combination of `tools` and `tool_resources`.

### Create Agent with File Search

To perform file search by an Agent, we first need to upload a file, create a vector store, and associate the file to the vector store. Here is an example:

<!-- SNIPPET:sample_agents_file_search.upload_file_create_vector_store_and_agent_with_file_search_tool -->

```python
file = agents_client.files.upload_and_poll(file_path=asset_file_path, purpose=FilePurpose.AGENTS)
print(f"Uploaded file, file ID: {file.id}")

vector_store = agents_client.vector_stores.create_and_poll(file_ids=[file.id], name="my_vectorstore")
print(f"Created vector store, vector store ID: {vector_store.id}")

# Create file search tool with resources followed by creating agent
file_search = FileSearchTool(vector_store_ids=[vector_store.id])

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="Hello, you are helpful agent and can search information from uploaded files",
    tools=file_search.definitions,
    tool_resources=file_search.resources,
)
```

<!-- END SNIPPET -->

### Create Agent with Enterprise File Search

We can upload file to Azure as it is shown in the example, or use the existing Azure blob storage. In the code below we demonstrate how this can be achieved. First we upload file to azure and create `VectorStoreDataSource`, which then is used to create vector store. This vector store is then given to the `FileSearchTool` constructor.

<!-- SNIPPET:sample_agents_enterprise_file_search.upload_file_and_create_agent_with_file_search -->

```python
# We will upload the local file to Azure and will use it for vector store creation.
asset_uri = os.environ["AZURE_BLOB_URI"]

# Create a vector store with no file and wait for it to be processed
ds = VectorStoreDataSource(asset_identifier=asset_uri, asset_type=VectorStoreDataSourceAssetType.URI_ASSET)
vector_store = agents_client.vector_stores.create_and_poll(data_sources=[ds], name="sample_vector_store")
print(f"Created vector store, vector store ID: {vector_store.id}")

# Create a file search tool
file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

# Notices that FileSearchTool as tool and tool_resources must be added or the agent unable to search the file
agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are helpful agent",
    tools=file_search_tool.definitions,
    tool_resources=file_search_tool.resources,
)
```

<!-- END SNIPPET -->

We also can attach files to the existing vector store. In the code snippet below, we first create an empty vector store and add file to it.

<!-- SNIPPET:sample_agents_vector_store_batch_enterprise_file_search.attach_files_to_store -->

```python
# Create a vector store with no file and wait for it to be processed
vector_store = agents_client.vector_stores.create_and_poll(data_sources=[], name="sample_vector_store")
print(f"Created vector store, vector store ID: {vector_store.id}")

ds = VectorStoreDataSource(asset_identifier=asset_uri, asset_type=VectorStoreDataSourceAssetType.URI_ASSET)
# Add the file to the vector store or you can supply data sources in the vector store creation
vector_store_file_batch = agents_client.vector_store_file_batches.create_and_poll(
    vector_store_id=vector_store.id, data_sources=[ds]
)
print(f"Created vector store file batch, vector store file batch ID: {vector_store_file_batch.id}")

# Create a file search tool
file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])
```

<!-- END SNIPPET -->

### Create Agent with Code Interpreter

Here is an example to upload a file and use it for code interpreter by an Agent:

<!-- SNIPPET:sample_agents_code_interpreter.upload_file_and_create_agent_with_code_interpreter -->

```python
file = agents_client.files.upload_and_poll(file_path=asset_file_path, purpose=FilePurpose.AGENTS)
print(f"Uploaded file, file ID: {file.id}")

code_interpreter = CodeInterpreterTool(file_ids=[file.id])

# Create agent with code interpreter tool and tools_resources
agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are helpful agent",
    tools=code_interpreter.definitions,
    tool_resources=code_interpreter.resources,
)
```

<!-- END SNIPPET -->

### Create Agent with Bing Grounding

To enable your Agent to perform search through Bing search API, you use `BingGroundingTool` along with a connection.

Here is an example:

<!-- SNIPPET:sample_agents_bing_grounding.create_agent_with_bing_grounding_tool -->

```python
conn_id = os.environ["AZURE_BING_CONNECTION_ID"]

# Initialize agent bing tool and add the connection id
bing = BingGroundingTool(connection_id=conn_id)

# Create agent with the bing tool and process agent run
with agents_client:
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        tools=bing.definitions,
    )
```

<!-- END SNIPPET -->

### Create Agent with Azure AI Search

Azure AI Search is an enterprise search system for high-performance applications. It integrates with Azure OpenAI Service and Azure Machine Learning, offering advanced search technologies like vector search and full-text search. Ideal for knowledge base insights, information discovery, and automation. Creating an Agent with Azure AI Search requires an existing Azure AI Search Index. For more information and setup guides, see [Azure AI Search Tool Guide](https://learn.microsoft.com/azure/ai-services/agents/how-to/tools/azure-ai-search?tabs=azurecli%2Cpython&pivots=overview-azure-ai-search).

Here is an example to integrate Azure AI Search:

<!-- SNIPPET:sample_agents_azure_ai_search.create_agent_with_azure_ai_search_tool -->

```python
conn_id = os.environ["AI_AZURE_AI_CONNECTION_ID"]

print(conn_id)

# Initialize agent AI search tool and add the search index connection id
ai_search = AzureAISearchTool(
    index_connection_id=conn_id, index_name="sample_index", query_type=AzureAISearchQueryType.SIMPLE, top_k=3, filter=""
)

# Create agent with AI search tool and process agent run
with agents_client:
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        tools=ai_search.definitions,
        tool_resources=ai_search.resources,
    )
```

<!-- END SNIPPET -->

If the agent has found the relevant information in the index, the reference
and annotation will be provided in the message response. In the example above, we replace
the reference placeholder by the actual reference and url. Please note, that to
get sensible result, the index needs to have "embedding", "token", "category" and "title" fields.

<!-- SNIPPET:sample_agents_azure_ai_search.populate_references_agent_with_azure_ai_search_tool -->

```python
# Fetch and log all messages
messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
for message in messages:
    if message.role == MessageRole.AGENT and message.url_citation_annotations:
        placeholder_annotations = {
            annotation.text: f" [see {annotation.url_citation.title}] ({annotation.url_citation.url})"
            for annotation in message.url_citation_annotations
        }
        for message_text in message.text_messages:
            message_str = message_text.text.value
            for k, v in placeholder_annotations.items():
                message_str = message_str.replace(k, v)
            print(f"{message.role}: {message_str}")
    else:
        for message_text in message.text_messages:
            print(f"{message.role}: {message_text.text.value}")
```

<!-- END SNIPPET -->

### Create Agent with Function Call

You can enhance your Agents by defining callback functions as function tools. These can be provided to `create_agent` via either the `toolset` parameter or the combination of `tools` and `tool_resources`. Here are the distinctions:

For more details about requirements and specification of functions, refer to [Function Tool Specifications](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/FunctionTool.md)

Here is an example to use [user functions](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/samples/utils/user_functions.py) in `toolset`:
<!-- SNIPPET:sample_agents_stream_eventhandler_with_toolset.create_agent_with_function_tool -->

```python
functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)
agents_client.enable_auto_function_calls(toolset)

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are a helpful agent",
    toolset=toolset,
)
```

<!-- END SNIPPET -->

For asynchronous functions, you must import `AgentsClient` from `azure.ai.agents.aio` and use `AsyncFunctionTool`.   Here is an example using [asynchronous user functions](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/samples/agents_async/sample_agents_functions_async.py):

```python
from azure.ai.agents.aio import AgentsClient
```

<!-- SNIPPET:sample_agents_run_with_toolset_async.create_agent_with_async_function_tool -->

```python
functions = AsyncFunctionTool(user_async_functions)

toolset = AsyncToolSet()
toolset.add(functions)
agents_client.enable_auto_function_calls(toolset)

agent = await agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are a helpful agent",
    toolset=toolset,
)
```

<!-- END SNIPPET -->

Notice that if `enable_auto_function_calls` is called, the SDK will invoke the functions automatically during `create_and_process` or streaming.  If you prefer to execute them manually, refer to [`sample_agents_stream_eventhandler_with_functions.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/samples/agents_streaming/sample_agents_stream_eventhandler_with_functions.py) or
[`sample_agents_functions.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/samples/agents_tools/sample_agents_functions.py)

### Create Agent With Azure Function Call

The AI agent leverages Azure Functions triggered asynchronously via Azure Storage Queues. To enable the agent to perform Azure Function calls, you must set up the corresponding `AzureFunctionTool`, specifying input and output queues as well as parameter definitions.

Example Python snippet illustrating how you create an agent utilizing the Azure Function Tool:

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

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="azure-function-agent-foo",
    instructions=f"You are a helpful support agent. Use the provided function any time the prompt contains the string 'What would foo say?'. When you invoke the function, ALWAYS specify the output queue uri parameter as '{storage_service_endpoint}/azure-function-tool-output'. Always responds with \"Foo says\" and then the response from the tool.",
    tools=azure_function_tool.definitions,
)
print(f"Created agent, agent ID: {agent.id}")
```

---

**Limitations**

Currently, the Azure Function integration for the AI Agent has the following limitations:

- Supported trigger for Azure Function is currently limited to **Queue triggers** only.
  HTTP or other trigger types and streaming responses are not supported at this time.

---

**Create and Deploy Azure Function**

Before you can use the agent with AzureFunctionTool, you need to create and deploy Azure Function.

Below is an example Python Azure Function responding to queue-triggered messages and placing responses on the output queue:

```python
import azure.functions as func
import logging
import json

app = func.FunctionApp()

@app.function_name(name="GetWeather")
@app.queue_trigger(arg_name="inputQueue",
                   queue_name="input",
                   connection="DEPLOYMENT_STORAGE_CONNECTION_STRING")
@app.queue_output(arg_name="outputQueue",
                  queue_name="output",
                  connection="DEPLOYMENT_STORAGE_CONNECTION_STRING")
def queue_trigger(inputQueue: func.QueueMessage, outputQueue: func.Out[str]):
    try:
        messagepayload = json.loads(inputQueue.get_body().decode("utf-8"))
        location = messagepayload["location"]
        weather_result = f"Weather is 82 degrees and sunny in {location}."

        response_message = {
            "Value": weather_result,
            "CorrelationId": messagepayload["CorrelationId"]
        }

        outputQueue.set(json.dumps(response_message))

        logger.info(f"Sent message to output queue with message {response_message}")
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        return
```

> **Important:** Both input and output payloads must contain the `CorrelationId`, which must match in request and response.

---

**Azure Function Project Creation and Deployment**

To deploy your function to Azure properly, follow Microsoft's official documentation step by step:

[Azure Functions Python Developer Guide](https://learn.microsoft.com/azure/azure-functions/create-first-function-cli-python?tabs=windows%2Cbash%2Cazure-cli%2Cbrowser)

**Summary of required steps:**

- Use the Azure CLI or Azure Portal to create an Azure Function App.
- Enable System Managed Identity for your Azure Function App.
- Assign appropriate permissions to your Azure Function App identity as outlined in the Role Assignments section below
- Create input and output queues in Azure Storage.
- Deploy your Function code.

---

**Verification and Testing Azure Function**

To ensure that your Azure Function deployment functions correctly:

1. Place the following style message manually into the input queue (`input`):

{
  "location": "Seattle",
  "CorrelationId": "42"
}

Check the output queue (`output`) and validate the structured message response:

{
  "Value": "The weather in Seattle is sunny and warm.",
  "CorrelationId": "42"
}

---

**Required Role Assignments (IAM Configuration)**

Clearly assign the following Azure IAM roles to ensure correct permissions:

1. **Azure Function App's identity:**
   - Enable system managed identity through Azure Function App > Settings > Identity.
   - Add permission to storage account:
     - Go to **Storage Account > Access control (IAM)** and add role assignment:
       - `Storage Queue Data Contributor` assigned to Azure Function managed identity

2. **Azure AI Project Identity:**

Ensure your Azure AI Project identity has the following storage account permissions:
- `Storage Account Contributor`
- `Storage Blob Data Contributor`
- `Storage File Data Privileged Contributor`
- `Storage Queue Data Contributor`
- `Storage Table Data Contributor`

---

**Additional Important Configuration Notes**

- The Azure Function configured above uses the `AzureWebJobsStorage` connection string for queue connectivity. You may alternatively use managed identity-based connections as described in the official Azure Functions Managed Identity documentation.
- Storage queues you specify (`input` & `output`) should already exist in the storage account before the Function deployment or invocation, created manually via Azure portal or CLI.
- When using Azure storage account connection strings, make sure the account has enabled storage account key access (`Storage Account > Settings > Configuration`).

---

With the above steps complete, your Azure Function integration with your AI Agent is ready for use.


### Create Agent With Logic Apps

Logic Apps allow HTTP requests to trigger actions. For more information, refer to the guide [Logic App Workflows for Function Calling](https://learn.microsoft.com/azure/ai-services/openai/how-to/assistants-logic-apps).

Your Logic App must be in the same resource group as your Azure AI Project, shown in the Azure Portal. Agents SDK accesses Logic Apps through Workflow URLs, which are fetched and called as requests in functions.

Below is an example of how to create an Azure Logic App utility tool and register a function with it.

<!-- SNIPPET:sample_agents_logic_apps.register_logic_app -->

```python

# Create the agents client
agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Extract subscription and resource group from the project scope
subscription_id = os.environ["SUBSCRIPTION_ID"]
resource_group = os.environ["resource_group_name"]

# Logic App details
logic_app_name = "<LOGIC_APP_NAME>"
trigger_name = "<TRIGGER_NAME>"

# Create and initialize AzureLogicAppTool utility
logic_app_tool = AzureLogicAppTool(subscription_id, resource_group)
logic_app_tool.register_logic_app(logic_app_name, trigger_name)
print(f"Registered logic app '{logic_app_name}' with trigger '{trigger_name}'.")

# Create the specialized "send_email_via_logic_app" function for your agent tools
send_email_func = create_send_email_function(logic_app_tool, logic_app_name)

# Prepare the function tools for the agent
functions_to_use: Set = {
    fetch_current_datetime,
    send_email_func,  # This references the AzureLogicAppTool instance via closure
}
```

<!-- END SNIPPET -->

After this the functions can be incorporated normally into code using `FunctionTool`.


### Create Agent With OpenAPI

OpenAPI specifications describe REST operations against a specific endpoint. Agents SDK can read an OpenAPI spec, create a function from it, and call that function against the REST endpoint without additional client-side execution.

Here is an example creating an OpenAPI tool (using anonymous authentication):

<!-- SNIPPET:sample_agents_openapi.create_agent_with_openapi -->

```python

with open(weather_asset_file_path, "r") as f:
    openapi_weather = jsonref.loads(f.read())

with open(countries_asset_file_path, "r") as f:
    openapi_countries = jsonref.loads(f.read())

# Create Auth object for the OpenApiTool (note that connection or managed identity auth setup requires additional setup in Azure)
auth = OpenApiAnonymousAuthDetails()

# Initialize agent OpenApi tool using the read in OpenAPI spec
openapi_tool = OpenApiTool(
    name="get_weather", spec=openapi_weather, description="Retrieve weather information for a location", auth=auth
)
openapi_tool.add_definition(
    name="get_countries", spec=openapi_countries, description="Retrieve a list of countries", auth=auth
)

# Create agent with OpenApi tool and process agent run
with agents_client:
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        tools=openapi_tool.definitions,
    )
```

<!-- END SNIPPET -->


### Create an Agent with Fabric

To enable your Agent to answer queries using Fabric data, use `FabricTool` along with a connection to the Fabric resource.

Here is an example:

<!-- SNIPPET:sample_agents_fabric.create_agent_with_fabric_tool -->

```python
conn_id = os.environ["FABRIC_CONNECTION_ID"]

print(conn_id)

# Initialize an Agent Fabric tool and add the connection id
fabric = FabricTool(connection_id=conn_id)

# Create an Agent with the Fabric tool and process an Agent run
with agents_client:
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        tools=fabric.definitions,
    )
```

<!-- END SNIPPET -->


### Create Thread

For each session or conversation, a thread is required.   Here is an example:

<!-- SNIPPET:sample_agents_basics.create_thread -->

```python
thread = agents_client.threads.create()
```

<!-- END SNIPPET -->

### Create Thread with Tool Resource

In some scenarios, you might need to assign specific resources to individual threads. To achieve this, you provide the `tool_resources` argument to `create_thread`. In the following example, you create a vector store and upload a file, enable an Agent for file search using the `tools` argument, and then associate the file with the thread using the `tool_resources` argument.

<!-- SNIPPET:sample_agents_with_resources_in_thread.create_agent_and_thread_for_file_search -->

```python
file = agents_client.files.upload_and_poll(file_path=asset_file_path, purpose=FilePurpose.AGENTS)
print(f"Uploaded file, file ID: {file.id}")

vector_store = agents_client.vector_stores.create_and_poll(file_ids=[file.id], name="my_vectorstore")
print(f"Created vector store, vector store ID: {vector_store.id}")

# Create file search tool with resources followed by creating agent
file_search = FileSearchTool(vector_store_ids=[vector_store.id])

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="Hello, you are helpful agent and can search information from uploaded files",
    tools=file_search.definitions,
)

print(f"Created agent, ID: {agent.id}")

# Create thread with file resources.
# If the agent has multiple threads, only this thread can search this file.
thread = agents_client.threads.create(tool_resources=file_search.resources)
```

<!-- END SNIPPET -->

#### List Threads

To list all threads attached to a given agent, use the list_threads API:

```python
threads = agents_client.threads.list()
```

### Create Message

To create a message for agent to process, you pass `user` as `role` and a question as `content`:

<!-- SNIPPET:sample_agents_basics.create_message -->

```python
message = agents_client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
```

<!-- END SNIPPET -->

### Create Message with File Search Attachment

To attach a file to a message for content searching, you use `MessageAttachment` and `FileSearchTool`:

<!-- SNIPPET:sample_agents_with_file_search_attachment.create_message_with_attachment -->

```python
attachment = MessageAttachment(file_id=file.id, tools=FileSearchTool().definitions)
message = agents_client.messages.create(
    thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?", attachments=[attachment]
)
```

<!-- END SNIPPET -->

### Create Message with Code Interpreter Attachment

To attach a file to a message for data analysis, use `MessageAttachment` and `CodeInterpreterTool` classes. You must pass `CodeInterpreterTool` as `tools` or `toolset` in `create_agent` call or the file attachment cannot be opened for code interpreter.

Here is an example to pass `CodeInterpreterTool` as tool:

<!-- SNIPPET:sample_agents_with_code_interpreter_file_attachment.create_agent_and_message_with_code_interpreter_file_attachment -->

```python
# Notice that CodeInterpreter must be enabled in the agent creation,
# otherwise the agent will not be able to see the file attachment for code interpretation
agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are helpful agent",
    tools=CodeInterpreterTool().definitions,
)
print(f"Created agent, agent ID: {agent.id}")

thread = agents_client.threads.create()
print(f"Created thread, thread ID: {thread.id}")

# Create an attachment
attachment = MessageAttachment(file_id=file.id, tools=CodeInterpreterTool().definitions)

# Create a message
message = agents_client.messages.create(
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
asset_uri = os.environ["AZURE_BLOB_URI"]
ds = VectorStoreDataSource(asset_identifier=asset_uri, asset_type=VectorStoreDataSourceAssetType.URI_ASSET)

# Create a message with the attachment
attachment = MessageAttachment(data_source=ds, tools=code_interpreter.definitions)
message = agents_client.messages.create(
    thread_id=thread.id, role="user", content="What does the attachment say?", attachments=[attachment]
)
```

<!-- END SNIPPET -->

### Create Message with Image Inputs

You can send messages to Azure agents with image inputs in following ways:

- **Using an image stored as a uploaded file**
- **Using a public image accessible via URL**
- **Using a base64 encoded image string**

The following examples demonstrate each method:

#### Create message using uploaded image file

```python
# Upload the local image file
image_file = agents_client.files.upload_and_poll(file_path="image_file.png", purpose="assistants")

# Construct content using uploaded image
file_param = MessageImageFileParam(file_id=image_file.id, detail="high")
content_blocks = [
    MessageInputTextBlock(text="Hello, what is in the image?"),
    MessageInputImageFileBlock(image_file=file_param),
]

# Create the message
message = agents_client.messages.create(
    thread_id=thread.id,
    role="user",
    content=content_blocks
)
```

#### Create message with an image URL input

```python
# Specify the public image URL
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

# Create content directly referencing image URL
url_param = MessageImageUrlParam(url=image_url, detail="high")
content_blocks = [
    MessageInputTextBlock(text="Hello, what is in the image?"),
    MessageInputImageUrlBlock(image_url=url_param),
]

# Create the message
message = agents_client.messages.create(
    thread_id=thread.id,
    role="user",
    content=content_blocks
)
```

#### Create message with base64-encoded image input

```python
import base64

def image_file_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Convert your image file to base64 format
image_base64 = image_file_to_base64("image_file.png")

# Prepare the data URL
img_data_url = f"data:image/png;base64,{image_base64}"

# Use base64 encoded string as image URL parameter
url_param = MessageImageUrlParam(url=img_data_url, detail="high")
content_blocks = [
    MessageInputTextBlock(text="Hello, what is in the image?"),
    MessageInputImageUrlBlock(image_url=url_param),
]

# Create the message
message = agents_client.messages.create(
    thread_id=thread.id,
    role="user",
    content=content_blocks
)
```

### Execute Run, Run_and_Process, or Stream

To process your message, you can use `runs.create`, `runs.create_and_process`, or `runs.stream`.

`create_run` requests the Agent to process the message without polling for the result. If you are using `function tools` regardless as `toolset` or not, your code is responsible for polling for the result and acknowledging the status of `Run`. When the status is `requires_action`, your code is responsible for calling the function tools. For a code sample, visit [`sample_agents_functions.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/samples/agents_tools/sample_agents_functions.py).

Here is an example of `runs.create` and poll until the run is completed:

<!-- SNIPPET:sample_agents_basics.create_run -->

```python
run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)

# Poll the run as long as run status is queued or in progress
while run.status in ["queued", "in_progress", "requires_action"]:
    # Wait for a second
    time.sleep(1)
    run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)
```

<!-- END SNIPPET -->

To have the SDK poll on your behalf and call `function tools`, use the `create_and_process` method. Note that `function tools` will only be invoked if they are provided as `toolset` during the `create_agent` call.

Here is an example:

<!-- SNIPPET:sample_agents_run_with_toolset.create_and_process_run -->

```python
run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
```

<!-- END SNIPPET -->

With streaming, polling need not be considered. If `function tools` are provided as `toolset` during the `create_agent` call, they will be invoked by the SDK.

Here is an example of streaming:

<!-- SNIPPET:sample_agents_basics_stream_iteration.iterate_stream -->

```python
with agents_client.runs.stream(thread_id=thread.id, agent_id=agent.id) as stream:

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

In the code above, because an `event_handler` object is not passed to the `stream` function, the SDK will instantiate `AgentEventHandler` or `AsyncAgentEventHandler` as the default event handler and produce an iterable object with `event_type` and `event_data`.  `AgentEventHandler` and `AsyncAgentEventHandler` are overridable.  Here is an example:

<!-- SNIPPET:sample_agents_basics_stream_eventhandler.stream_event_handler -->

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


<!-- SNIPPET:sample_agents_basics_stream_eventhandler.create_stream -->

```python
with agents_client.runs.stream(thread_id=thread.id, agent_id=agent.id, event_handler=MyEventHandler()) as stream:
    for event_type, event_data, func_return in stream:
        print(f"Received data.")
        print(f"Streaming receive Event Type: {event_type}")
        print(f"Event Data: {str(event_data)[:100]}...")
        print(f"Event Function return: {func_return}\n")
```

<!-- END SNIPPET -->

As you can see, this SDK parses the events and produces various event types similar to OpenAI agents. In your use case, you might not be interested in handling all these types and may decide to parse the events on your own. To achieve this, please refer to [override base event handler](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/samples/agents_streaming/sample_agents_stream_with_base_override_eventhandler.py).

```
Note: Multiple streaming processes may be chained behind the scenes.

When the SDK receives a `ThreadRun` event with the status `requires_action`, the next event will be `Done`, followed by termination. The SDK will submit the tool calls using the same event handler. The event handler will then chain the main stream with the tool stream.

Consequently, when you iterate over the streaming using a for loop similar to the example above, the for loop will receive events from the main stream followed by events from the tool stream.
```


### Retrieve Message

To retrieve messages from agents, use the following example:

<!-- SNIPPET:sample_agents_basics.list_messages -->

```python
messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
for msg in messages:
    if msg.text_messages:
        last_text = msg.text_messages[-1]
        print(f"{msg.role}: {last_text.text.value}")
```

<!-- END SNIPPET -->

In addition, `messages` and `messages.data[]` offer helper properties such as `text_messages`, `image_contents`, `file_citation_annotations`, and `file_path_annotations` to quickly retrieve content from one message or all messages.

### Retrieve File

Files uploaded by Agents cannot be retrieved back. If your use case need to access the file content uploaded by the Agents, you are advised to keep an additional copy accessible by your application. However, files generated by Agents are retrievable by `save_file` or `get_file_content`.

Here is an example retrieving file ids from messages and save to the local drive:

<!-- SNIPPET:sample_agents_code_interpreter.get_messages_and_save_files -->

```python
messages = agents_client.messages.list(thread_id=thread.id)
print(f"Messages: {messages}")

for msg in messages:
    # Save every image file in the message
    for img in msg.image_contents:
        file_id = img.image_file.file_id
        file_name = f"{file_id}_image_file.png"
        agents_client.files.save(file_id=file_id, file_name=file_name)
        print(f"Saved image file to: {Path.cwd() / file_name}")

    # Print details of every file-path annotation
    for ann in msg.file_path_annotations:
        print("File Paths:")
        print(f"  Type: {ann.type}")
        print(f"  Text: {ann.text}")
        print(f"  File ID: {ann.file_path.file_id}")
        print(f"  Start Index: {ann.start_index}")
        print(f"  End Index: {ann.end_index}")
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
    file_content_stream = await client.files.get_content(file_id)
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

### Teardown

To remove resources after completing tasks, use the following functions:

<!-- SNIPPET:sample_agents_file_search.teardown -->

```python
# Delete the file when done
agents_client.vector_stores.delete(vector_store.id)
print("Deleted vector store")

agents_client.files.delete(file_id=file.id)
print("Deleted file")

# Delete the agent when done
agents_client.delete_agent(agent.id)
print("Deleted agent")
```

<!-- END SNIPPET -->

## Tracing

You can add an Application Insights Azure resource to your Azure AI Foundry project. See the Tracing tab in your AI Foundry project. If one was enabled, you can get the Application Insights connection string, configure your Agents, and observe the full execution path through Azure Monitor. Typically, you might want to start tracing before you create an Agent.

### Installation

Make sure to install OpenTelemetry and the Azure SDK tracing plugin via

```bash
pip install opentelemetry
pip install azure-ai-agents azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry
```

You will also need an exporter to send telemetry to your observability backend. You can print traces to the console or use a local viewer such as [Aspire Dashboard](https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone?tabs=bash).

To connect to Aspire Dashboard or another OpenTelemetry compatible backend, install OTLP exporter:

```bash
pip install opentelemetry-exporter-otlp
```

### How to enable tracing

Here is a code sample that shows how to enable Azure Monitor tracing:

<!-- SNIPPET:sample_agents_basics_with_azure_monitor_tracing.enable_tracing -->

```python
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor

# Enable Azure Monitor tracing
application_insights_connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
configure_azure_monitor(connection_string=application_insights_connection_string)

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span(scenario):
    with agents_client:
```

<!-- END SNIPPET -->

In addition, you might find helpful to see the tracing logs in console. You can achieve by the following code:

```python
from azure.ai.agents.telemetry import enable_telemetry

enable_telemetry(destination=sys.stdout)
```
### How to trace your own functions

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
agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
    logging_enable = True
)
```

Note that the log level must be set to `logging.DEBUG` (see above code). Logs will be redacted with any other log level.

Be sure to protect non redacted logs to avoid compromising security.

For more information, see [Configure logging in the Azure libraries for Python](https://aka.ms/azsdk/python/logging)

### Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues). Mention the package name "azure-ai-agents" in the title or content.


## Next steps

Have a look at the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/samples) folder, containing fully runnable Python code for synchronous and asynchronous clients.

Explore the [AI Starter Template](https://aka.ms/azsdk/azure-ai-agents/python/ai-starter-template). This template creates an Azure AI Foundry hub, project and connected resources including Azure OpenAI Service, AI Search and more. It also deploys a simple chat application to Azure Container Apps.

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
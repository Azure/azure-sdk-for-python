# Azure AI Projects client library for Python

The AI Projects client library (in preview) is part of the Microsoft Foundry SDK, and provides easy access to
resources in your Microsoft Foundry Project. Use it to:

* **Create and run Agents** using methods on methods on the `.agents` client property.
* **Enhance Agents with specialized tools**:
  * Agent Memory Search
  * Agent-to-Agent (A2A)
  * Azure AI Search
  * Bing Custom Search
  * Bing Grounding
  * Browser Automation
  * Code Interpreter
  * Computer Use
  * File Search
  * Function Tool
  * Image Generation
  * Microsoft Fabric
  * Model Context Protocol (MCP)
  * OpenAPI
  * SharePoint
  * Web Search
* **Get an OpenAI client** using `.get_openai_client()` method to run Responses, Conversations, Evals and FineTuning operations with your Agent.
* **Manage memory stores** for Agent conversations, using the `.memory_stores` operations.
* **Explore additional evaluation tools** to assess the performance of your generative AI application, using the `.evaluation_rules`,
`.evaluation_taxonomies`, `.evaluators`, `.insights`, and `.schedules` operations.
* **Run Red Team scans** to identify risks associated with your generative AI application, using the ".red_teams" operations.
* **Fine tune** AI Models on your data.
* **Enumerate AI Models** deployed to your Foundry Project using the `.deployments` operations.
* **Enumerate connected Azure resources** in your Foundry project using the `.connections` operations.
* **Upload documents and create Datasets** to reference them using the `.datasets` operations.
* **Create and enumerate Search Indexes** using methods the `.indexes` operations.

The client library uses version `2025-11-15-preview` of the AI Foundry [data plane REST APIs](https://aka.ms/azsdk/azure-ai-projects-v2/api-reference-2025-11-15-preview).

[Product documentation](https://aka.ms/azsdk/azure-ai-projects-v2/product-doc)
| [Samples][samples]
| [API reference](https://aka.ms/azsdk/azure-ai-projects-v2/python/api-reference)
| [Package (PyPI)](https://aka.ms/azsdk/azure-ai-projects-v2/python/package)
| [SDK source code](https://aka.ms/azsdk/azure-ai-projects-v2/python/code)
| [Release history](https://aka.ms/azsdk/azure-ai-projects-v2/python/release-history)

## Reporting issues

To report an issue with the client library, or request additional features, please open a [GitHub issue here](https://github.com/Azure/azure-sdk-for-python/issues). Mention the package name "azure-ai-projects" in the title or content.

## Getting started

### Prerequisite

* Python 3.9 or later.
* An [Azure subscription][azure_sub].
* A [project in Microsoft Foundry](https://learn.microsoft.com/azure/ai-studio/how-to/create-projects).
* The project endpoint URL of the form `https://your-ai-services-account-name.services.ai.azure.com/api/projects/your-project-name`. It can be found in your Microsoft Foundry Project overview page. Below we will assume the environment variable `AZURE_AI_PROJECT_ENDPOINT` was defined to hold this value.
* An Entra ID token for authentication. Your application needs an object that implements the [TokenCredential](https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.tokencredential) interface. Code samples here use [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential). To get that working, you will need:
  * An appropriate role assignment. see [Role-based access control in Microsoft Foundry portal](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-ai-foundry). Role assigned can be done via the "Access Control (IAM)" tab of your Azure AI Project resource in the Azure portal.
  * [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed.
  * You are logged into your Azure account by running `az login`.

### Install the package

```bash
pip install --pre azure-ai-projects
```

Note that the packages [openai](https://pypi.org/project/openai) and [azure-identity](https://pypi.org/project/azure-identity) also need to be installed if you intend to call `get_openai_client()`:

```bash
pip install openai azure-identity
```

## Key concepts

### Create and authenticate the client with Entra ID

Entra ID is the only authentication method supported at the moment by the client.

To construct a synchronous client as a context manager:

```python
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as project_client,
):
```

To construct an asynchronous client, install the additional package [aiohttp](https://pypi.org/project/aiohttp/):

```bash
pip install aiohttp
```

and run:

```python
import os
import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

async with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as project_client,
):
```

## Examples

### Performing Responses operations using OpenAI client

Your Microsoft Foundry project may have one or more AI models deployed. These could be OpenAI models, Microsoft models, or models from other providers. Use the code below to get an authenticated [OpenAI](https://github.com/openai/openai-python?tab=readme-ov-file#usage) client from the [openai](https://pypi.org/project/openai/) package, and execute an example multi-turn "Responses" calls.

The code below assumes the environment variable `AZURE_AI_MODEL_DEPLOYMENT_NAME` is defined. It's the deployment name of an AI model in your Foundry Project, As shown in the "Models + endpoints" tab, under the "Name" column.

See the "responses" folder in the [package samples][samples] for additional samples, including streaming responses.

<!-- SNIPPET:sample_responses_basic.responses -->

```python
with project_client.get_openai_client() as openai_client:
    response = openai_client.responses.create(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        input="What is the size of France in square miles?",
    )
    print(f"Response output: {response.output_text}")

    response = openai_client.responses.create(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        input="And what is the capital city?",
        previous_response_id=response.id,
    )
    print(f"Response output: {response.output_text}")
```

<!-- END SNIPPET -->

### Performing Agent operations

The `.agents` property on the `AIProjectsClient` gives you access to all Agent operations. Agents use an extension of the OpenAI Responses protocol, so you will need to get an `OpenAI` client to do Agent operations, as shown in the example below.

The code below assumes environment variable `AZURE_AI_MODEL_DEPLOYMENT_NAME` is defined. It's the deployment name of an AI model in your Foundry Project, as shown in the "Models + endpoints" tab, under the "Name" column.

See the "agents" folder in the [package samples][samples] for an extensive set of samples, including streaming, tool usage and memory store usage.

<!-- SNIPPET:sample_agent_basic.prompt_agent_basic -->

```python
with project_client.get_openai_client() as openai_client:
    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant that answers general questions",
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    conversation = openai_client.conversations.create(
        items=[{"type": "message", "role": "user", "content": "What is the size of France in square miles?"}],
    )
    print(f"Created conversation with initial user message (id: {conversation.id})")

    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        input="",
    )
    print(f"Response output: {response.output_text}")

    openai_client.conversations.items.create(
        conversation_id=conversation.id,
        items=[{"type": "message", "role": "user", "content": "And what is the capital city?"}],
    )
    print(f"Added a second user message to the conversation")

    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        input="",
    )
    print(f"Response output: {response.output_text}")

    openai_client.conversations.delete(conversation_id=conversation.id)
    print("Conversation deleted")

project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("Agent deleted")
```

<!-- END SNIPPET -->

### Using Agent tools

Agents can be enhanced with specialized tools for various capabilities. Tools are organized by their connection requirements:

#### Built-in Tools

These tools work immediately without requiring external connections.

**Code Interpreter**

Write and run Python code in a sandboxed environment, process files and work with diverse data formats. [OpenAI Documentation](https://platform.openai.com/docs/guides/tools-code-interpreter)

<!-- SNIPPET:sample_agent_code_interpreter.tool_declaration -->

```python
# Load the CSV file to be processed
asset_file_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../assets/synthetic_500_quarterly_results.csv")
)

# Upload the CSV file for the code interpreter
file = openai_client.files.create(purpose="assistants", file=open(asset_file_path, "rb"))
tool = CodeInterpreterTool(container=CodeInterpreterToolAuto(file_ids=[file.id]))
```

<!-- END SNIPPET -->

*After calling `responses.create()`, check for generated files in response annotations (type `container_file_citation`) and download them using `openai_client.containers.files.content.retrieve()`.*

See the full sample code in [sample_agent_code_interpreter.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_code_interpreter.py).

**File Search**

Built-in RAG (Retrieval-Augmented Generation) tool to process and search through documents using vector stores for knowledge retrieval. [OpenAI Documentation](https://platform.openai.com/docs/assistants/tools/file-search)

<!-- SNIPPET:sample_agent_file_search.tool_declaration -->

```python
# Create vector store for file search
vector_store = openai_client.vector_stores.create(name="ProductInfoStore")
print(f"Vector store created (id: {vector_store.id})")

# Load the file to be indexed for search
asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/product_info.md"))

# Upload file to vector store
file = openai_client.vector_stores.files.upload_and_poll(
    vector_store_id=vector_store.id, file=open(asset_file_path, "rb")
)
print(f"File uploaded to vector store (id: {file.id})")

tool = FileSearchTool(vector_store_ids=[vector_store.id])
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_file_search.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_file_search.py).

**Image Generation**

Generate images based on text prompts with customizable resolution, quality, and style settings:

<!-- SNIPPET:sample_agent_image_generation.tool_declaration -->

```python
tool = ImageGenTool(quality="low", size="1024x1024")
```

<!-- END SNIPPET -->

After calling `responses.create()`, you can download file using the returned response:
<!-- SNIPPET:sample_agent_image_generation.download_image -->

```python
image_data = [output.result for output in response.output if output.type == "image_generation_call"]

if image_data and image_data[0]:
    print("Downloading generated image...")
    filename = "microsoft.png"
    file_path = os.path.abspath(filename)

    with open(file_path, "wb") as f:
        f.write(base64.b64decode(image_data[0]))
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_image_generation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_image_generation.py).


**Web Search**

Perform general web searches to retrieve current information from the internet. [OpenAI Documentation](https://platform.openai.com/docs/guides/tools-web-search)

<!-- SNIPPET:sample_agent_web_search.tool_declaration -->

```python
tool = WebSearchPreviewTool(user_location=ApproximateLocation(country="GB", city="London", region="London"))
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_web_search.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_web_search.py).

**Computer Use**

Enable agents to interact directly with computer systems for task automation and system operations:

<!-- SNIPPET:sample_agent_computer_use.tool_declaration -->

```python
tool = ComputerUsePreviewTool(display_width=1026, display_height=769, environment="windows")
```

<!-- END SNIPPET -->

*After calling `responses.create()`, process the response in an interaction loop. Handle `computer_call` output items and provide screenshots as `computer_call_output` with `computer_screenshot` type to continue the interaction.*

See the full sample code in [sample_agent_computer_use.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_computer_use.py).

**Model Context Protocol (MCP)**

Integrate MCP servers to extend agent capabilities with standardized tools and resources. [OpenAI Documentation](https://platform.openai.com/docs/guides/tools-connectors-mcp)

<!-- SNIPPET:sample_agent_mcp.tool_declaration -->

```python
mcp_tool = MCPTool(
    server_label="api-specs",
    server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
    require_approval="always",
)
```

<!-- END SNIPPET -->

*After calling `responses.create()`, check for `mcp_approval_request` items in the response output. Send back `McpApprovalResponse` with your approval decision to allow the agent to continue its work.*

See the full sample code in [sample_agent_mcp.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_mcp.py).

**OpenAPI**

Call external APIs defined by OpenAPI specifications without additional client-side code. [OpenAI Documentation](https://platform.openai.com/docs/guides/tools-openapi)

<!-- SNIPPET:sample_agent_openapi.tool_declaration-->

```python
with open(weather_asset_file_path, "r") as f:
    openapi_weather = jsonref.loads(f.read())

tool = OpenApiAgentTool(
    openapi=OpenApiFunctionDefinition(
        name="get_weather",
        spec=openapi_weather,
        description="Retrieve weather information for a location",
        auth=OpenApiAnonymousAuthDetails(),
    )
)
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_openapi.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_openapi.py).

**Function Tool**

Define custom functions that allow agents to interact with external APIs, databases, or application logic. [OpenAI Documentation](https://platform.openai.com/docs/guides/function-calling)

<!-- SNIPPET:sample_agent_function_tool.tool_declaration -->

```python
tool = FunctionTool(
    name="get_horoscope",
    parameters={
        "type": "object",
        "properties": {
            "sign": {
                "type": "string",
                "description": "An astrological sign like Taurus or Aquarius",
            },
        },
        "required": ["sign"],
        "additionalProperties": False,
    },
    description="Get today's horoscope for an astrological sign.",
    strict=True,
)
```

<!-- END SNIPPET -->

*After calling `responses.create()`, process `function_call` items from response output, execute your function logic with the provided arguments, and send back `FunctionCallOutput` with the results.*

See the full sample code in [sample_agent_function_tool.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_function_tool.py).

* **Memory Search Tool**

  The Memory Store Tool adds Memory to an Agent, allowing the Agent's AI model to search for past information related to the current user prompt.

  <!-- SNIPPET:sample_agent_memory_search.memory_search_tool_declaration -->
  ```python
  # Set scope to associate the memories with
  # You can also use "{{$userId}}" to take the oid of the request authentication header
  scope = "user_123"

  tool = MemorySearchTool(
      memory_store_name=memory_store.name,
      scope=scope,
      update_delay=1,  # Wait 1 second of inactivity before updating memories
      # In a real application, set this to a higher value like 300 (5 minutes, default)
  )
  ```
  <!-- END SNIPPET -->

  See the full [sample_agent_memory_search.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_memory_search.py) showing how to create an Agent with a memory store, and use it in multiple conversations.

  See also samples in the folder [samples\memories](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/memories) showing how to manage memory stores.

#### Connection-Based Tools

These tools require configuring connections in your AI Foundry project and use `project_connection_id`.

**Azure AI Search**

Integrate with Azure AI Search indexes for powerful knowledge retrieval and semantic search capabilities:

<!-- SNIPPET:sample_agent_ai_search.tool_declaration -->

```python
tool = AzureAISearchAgentTool(
    azure_ai_search=AzureAISearchToolResource(
        indexes=[
            AISearchIndexResource(
                project_connection_id=os.environ["AI_SEARCH_PROJECT_CONNECTION_ID"],
                index_name=os.environ["AI_SEARCH_INDEX_NAME"],
                query_type=AzureAISearchQueryType.SIMPLE,
            ),
        ]
    )
)
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_ai_search.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_ai_search.py).

**Bing Grounding**

Ground agent responses with real-time web search results from Bing to provide up-to-date information:

<!-- SNIPPET:sample_agent_bing_grounding.tool_declaration -->

```python
tool = BingGroundingAgentTool(
    bing_grounding=BingGroundingSearchToolParameters(
        search_configurations=[
            BingGroundingSearchConfiguration(project_connection_id=os.environ["BING_PROJECT_CONNECTION_ID"])
        ]
    )
)
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_bing_grounding.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_bing_grounding.py).

**Bing Custom Search**

Use custom-configured Bing search instances for domain-specific or filtered web search results:

<!-- SNIPPET:sample_agent_bing_custom_search.tool_declaration -->

```python
tool = BingCustomSearchAgentTool(
    bing_custom_search_preview=BingCustomSearchToolParameters(
        search_configurations=[
            BingCustomSearchConfiguration(
                project_connection_id=os.environ["BING_CUSTOM_SEARCH_PROJECT_CONNECTION_ID"],
                instance_name=os.environ["BING_CUSTOM_SEARCH_INSTANCE_NAME"],
            )
        ]
    )
)
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_bing_custom_search.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_bing_custom_search.py).

**Microsoft Fabric**

Connect to and query Microsoft Fabric:

<!-- SNIPPET:sample_agent_fabric.tool_declaration -->

```python
tool = MicrosoftFabricAgentTool(
    fabric_dataagent_preview=FabricDataAgentToolParameters(
        project_connections=[
            ToolProjectConnection(project_connection_id=os.environ["FABRIC_PROJECT_CONNECTION_ID"])
        ]
    )
)
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_fabric.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_fabric.py).

**SharePoint**

Access and search SharePoint documents, lists, and sites for enterprise knowledge integration:

<!-- SNIPPET:sample_agent_sharepoint.tool_declaration -->

```python
tool = SharepointAgentTool(
    sharepoint_grounding_preview=SharepointGroundingToolParameters(
        project_connections=[
            ToolProjectConnection(project_connection_id=os.environ["SHAREPOINT_PROJECT_CONNECTION_ID"])
        ]
    )
)
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_sharepoint.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_sharepoint.py).

**Browser Automation**

Automate browser interactions for web scraping, testing, and interaction with web applications:

<!-- SNIPPET:sample_agent_browser_automation.tool_declaration -->

```python
tool = BrowserAutomationAgentTool(
    browser_automation_preview=BrowserAutomationToolParameters(
        connection=BrowserAutomationToolConnectionParameters(
            project_connection_id=os.environ["BROWSER_AUTOMATION_PROJECT_CONNECTION_ID"],
        )
    )
)
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_browser_automation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_browser_automation.py).


**MCP with Project Connection**

MCP integration using project-specific connections for accessing connected MCP servers:

<!-- SNIPPET:sample_agent_mcp_with_project_connection.tool_declaration -->

```python
tool = MCPTool(
    server_label="api-specs",
    server_url="https://api.githubcopilot.com/mcp",
    require_approval="always",
    project_connection_id=os.environ["MCP_PROJECT_CONNECTION_ID"],
)
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_mcp_with_project_connection.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_mcp_with_project_connection.py).

**Agent-to-Agent (A2A)**

Enable multi-agent collaboration where agents can communicate and delegate tasks to other specialized agents:

<!-- SNIPPET:sample_agent_to_agent.tool_declaration -->

```python
tool = A2ATool(
    project_connection_id=os.environ["A2A_PROJECT_CONNECTION_ID"],
)
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_to_agent.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_to_agent.py).

**OpenAPI with Project Connection**

Call external APIs defined by OpenAPI specifications using project connection authentication:

<!-- SNIPPET:sample_agent_openapi_with_project_connection.tool_declaration-->

```python
with open(tripadvisor_asset_file_path, "r") as f:
    openapi_tripadvisor = jsonref.loads(f.read())

tool = OpenApiAgentTool(
    openapi=OpenApiFunctionDefinition(
        name="tripadvisor",
        spec=openapi_tripadvisor,
        description="Trip Advisor API to get travel information",
        auth=OpenApiProjectConnectionAuthDetails(
            security_scheme=OpenApiProjectConnectionSecurityScheme(
                project_connection_id=os.environ["OPENAPI_PROJECT_CONNECTION_ID"]
            )
        ),
    )
)
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_openapi_with_project_connection.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_openapi_with_project_connection.py).

For complete working examples of all tools, see the [sample tools directory](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools).

### Evaluation

Evaluation in Azure AI Project client library provides quantitative, AI-assisted quality and safety metrics to asses performance and Evaluate LLM Models, GenAI Application and Agents. Metrics are defined as evaluators. Built-in or custom evaluators can provide comprehensive evaluation insights.

The code below shows some evaluation operations. Full list of sample can be found under "evaluation" folder in the [package samples][samples]

<!-- SNIPPET:sample_agent_evaluation.agent_evaluation_basic -->

```python
with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):
    agent = project_client.agents.create_version(
        agent_name=os.environ["AZURE_AI_AGENT_NAME"],
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant that answers general questions",
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        include_sample_schema=True,
    )
    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "violence_detection",
            "evaluator_name": "builtin.violence",
            "data_mapping": {"query": "{{item.query}}", "response": "{{item.response}}"},
        }
    ]
    eval_object = openai_client.evals.create(
        name="Agent Evaluation",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,  # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    data_source = {
        "type": "azure_ai_target_completions",
        "source": {
            "type": "file_content",
            "content": [
                {"item": {"query": "What is the capital of France?"}},
                {"item": {"query": "How do I reverse a string in Python?"}},
            ],
        },
        "input_messages": {
            "type": "template",
            "template": [
                {"type": "message", "role": "user", "content": {"type": "input_text", "text": "{{item.query}}"}}
            ],
        },
        "target": {
            "type": "azure_ai_agent",
            "name": agent.name,
            "version": agent.version,  # Version is optional. Defaults to latest version if not specified
        },
    }

    agent_eval_run: Union[RunCreateResponse, RunRetrieveResponse] = openai_client.evals.runs.create(
        eval_id=eval_object.id, name=f"Evaluation Run for Agent {agent.name}", data_source=data_source  # type: ignore
    )
    print(f"Evaluation run created (id: {agent_eval_run.id})")
```

<!-- END SNIPPET -->

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
print(f"Create Index `{index_name}` with version `{index_version}`, referencing an existing AI Search resource:")
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

### Files operations

The code below shows some Files operations using the OpenAI client, which allow you to upload, retrieve, list, and delete files. These operations are useful for working with files that can be used for fine-tuning and other AI model operations. Full samples can be found under the "files" folder in the [package samples][samples].

<!-- SNIPPET:sample_files.files_sample-->

```python
print("Uploading file")
with open(file_path, "rb") as f:
    uploaded_file = openai_client.files.create(file=f, purpose="fine-tune")
print(uploaded_file)

print("Waits for the given file to be processed, default timeout is 30 mins")
processed_file = openai_client.files.wait_for_processing(uploaded_file.id)
print(processed_file)

print(f"Retrieving file metadata with ID: {processed_file.id}")
retrieved_file = openai_client.files.retrieve(processed_file.id)
print(retrieved_file)

print(f"Retrieving file content with ID: {processed_file.id}")
file_content = openai_client.files.content(processed_file.id)
print(file_content.content)

print("Listing all files:")
for file in openai_client.files.list():
    print(file)

print(f"Deleting file with ID: {processed_file.id}")
deleted_file = openai_client.files.delete(processed_file.id)
print(f"Successfully deleted file: {deleted_file.id}")
```

<!-- END SNIPPET -->

### Fine-tuning operations

The code below shows how to create fine-tuning jobs using the OpenAI client. These operations support various fine-tuning techniques like Supervised Fine-Tuning (SFT), Reinforcement Fine-Tuning (RFT), and Direct Performance Optimization (DPO). Full samples can be found under the "finetuning" folder in the [package samples][samples].

<!-- SNIPPET:sample_finetuning_oss_models_supervised_job.finetuning_oss_model_supervised_job_sample-->

```python
print("Uploading training file...")
with open(training_file_path, "rb") as f:
    train_file = openai_client.files.create(file=f, purpose="fine-tune")
print(f"Uploaded training file with ID: {train_file.id}")

print("Uploading validation file...")
with open(validation_file_path, "rb") as f:
    validation_file = openai_client.files.create(file=f, purpose="fine-tune")
print(f"Uploaded validation file with ID: {validation_file.id}")

print("Waits for the training and validation files to be processed...")
openai_client.files.wait_for_processing(train_file.id)
openai_client.files.wait_for_processing(validation_file.id)

print("Creating supervised fine-tuning job")
fine_tuning_job = openai_client.fine_tuning.jobs.create(
    training_file=train_file.id,
    validation_file=validation_file.id,
    model=model_name,
    method={
        "type": "supervised",
        "supervised": {"hyperparameters": {"n_epochs": 3, "batch_size": 1, "learning_rate_multiplier": 1.0}},
    },
    extra_body={
        "trainingType": "GlobalStandard"
    },  # Recommended approach to set trainingType. Omitting this field may lead to unsupported behavior.
    # Preferred trainingtype is GlobalStandard.  Note:  Global training offers cost savings , but copies data and weights outside the current resource region.
    # Learn more - https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/ and https://azure.microsoft.com/en-us/explore/global-infrastructure/data-residency/
)
print(fine_tuning_job)
```

<!-- END SNIPPET -->

## Tracing

**Note:** Tracing functionality is in preliminary preview and is subject to change. Spans, attributes, and events may be modified in future versions.

You can add an Application Insights Azure resource to your Microsoft Foundry project. See the Tracing tab in your AI Foundry project. If one was enabled, you can get the Application Insights connection string, configure your AI Projects client, and observe traces in Azure Monitor. Typically, you might want to start tracing before you create a client or Agent.

### Installation

Make sure to install OpenTelemetry and the Azure SDK tracing plugin via

```bash
pip install azure-ai-projects azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry azure-monitor-opentelemetry
```

You will also need an exporter to send telemetry to your observability backend. You can print traces to the console or use a local viewer such as [Aspire Dashboard](https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone?tabs=bash).

To connect to Aspire Dashboard or another OpenTelemetry compatible backend, install OTLP exporter:

```bash
pip install opentelemetry-exporter-otlp
```

### How to enable tracing

Here is a code sample that shows how to enable Azure Monitor tracing:

<!-- SNIPPET:sample_agent_basic_with_azure_monitor_tracing.setup_azure_monitor_tracing -->

```python
# Enable Azure Monitor tracing
application_insights_connection_string = project_client.telemetry.get_application_insights_connection_string()
configure_azure_monitor(connection_string=application_insights_connection_string)

```

<!-- END SNIPPET -->

You may also want to create a span for your scenario:

<!-- SNIPPET:sample_agent_basic_with_azure_monitor_tracing.create_span_for_scenario -->

```python
tracer = trace.get_tracer(__name__)
scenario = os.path.basename(__file__)

with tracer.start_as_current_span(scenario):
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_basic_with_azure_monitor_tracing.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/telemetry/sample_agent_basic_with_azure_monitor_tracing.py).

In addition, you might find it helpful to see the tracing logs in the console. You can achieve this with the following code:

<!-- SNIPPET:sample_agent_basic_with_console_tracing.setup_console_tracing -->

```python
# Setup tracing to console
# Requires opentelemetry-sdk
span_exporter = ConsoleSpanExporter()
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# Enable instrumentation with content tracing
AIProjectInstrumentor().instrument()
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_basic_with_console_tracing.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/telemetry/sample_agent_basic_with_console_tracing.py).

### Enabling content recording

Content recording controls whether message contents and tool call related details, such as parameters and return values, are captured with the traces. This data may include sensitive user information.

To enable content recording, set the `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` environment variable to `true`. If the environment variable is not set, content recording defaults to `false`.

**Important:** The environment variable only controls content recording for built-in traces. When you use custom tracing decorators on your own functions, all parameters and return values are always traced.

### Disabling automatic instrumentation

The AI Projects client library automatically instruments OpenAI responses and conversations operations through `AiProjectInstrumentation`. You can disable this instrumentation by setting the environment variable `AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API` to `false`. If the environment variable is not set, the responses and conversations APIs will be instrumented by default.

### Tracing Binary Data

Binary data are images and files sent to the service as input messages. When you enable content recording (`OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` set to `true`), by default you only trace file IDs and filenames. To enable full binary data tracing, set `AZURE_TRACING_GEN_AI_INCLUDE_BINARY_DATA` to `true`. In this case:

* **Images**: Image URLs (including data URIs with base64-encoded content) are included
* **Files**: File data is included if sent via the API

**Important:** Binary data can contain sensitive information and may significantly increase trace size. Some trace backends and tracing implementations may have limitations on the maximum size of trace data that can be sent to and/or supported by the backend. Ensure your observability backend and tracing implementation support the expected trace payload sizes when enabling binary data tracing.

### How to trace your own functions

The decorator `trace_function` is provided for tracing your own function calls using OpenTelemetry. By default the function name is used as the name for the span. Alternatively you can provide the name for the span as a parameter to the decorator.

**Note:** The `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` environment variable does not affect custom function tracing. When you use the `trace_function` decorator, all parameters and return values are always traced by default.

This decorator handles various data types for function parameters and return values, and records them as attributes in the trace span. The supported data types include:

* Basic data types: str, int, float, bool
* Collections: list, dict, tuple, set
  * Special handling for collections:
    * If a collection (list, dict, tuple, set) contains nested collections, the entire collection is converted to a string before being recorded as an attribute.
    * Sets and dictionaries are always converted to strings to ensure compatibility with span attributes.

Object types are omitted, and the corresponding parameter is not traced.

The parameters are recorded in attributes `code.function.parameter.<parameter_name>` and the return value is recorder in attribute `code.function.return.value`

#### Adding custom attributes to spans

You can add custom attributes to spans by creating a custom span processor. Here's how to define one:

<!-- SNIPPET:sample_agent_basic_with_console_tracing_custom_attributes.custom_attribute_span_processor -->

```python
class CustomAttributeSpanProcessor(SpanProcessor):
    def __init__(self):
        pass

    def on_start(self, span: Span, parent_context=None):
        # Add this attribute to all spans
        span.set_attribute("trace_sample.sessionid", "123")

        # Add another attribute only to create_thread spans
        if span.name == "create_thread":
            span.set_attribute("trace_sample.create_thread.context", "abc")

    def on_end(self, span: ReadableSpan):
        # Clean-up logic can be added here if necessary
        pass
```

<!-- END SNIPPET -->

Then add the custom span processor to the global tracer provider:

<!-- SNIPPET:sample_agent_basic_with_console_tracing_custom_attributes.add_custom_span_processor_to_tracer_provider -->

```python
provider = cast(TracerProvider, trace.get_tracer_provider())
provider.add_span_processor(CustomAttributeSpanProcessor())
```

<!-- END SNIPPET -->

See the full sample code in [sample_agent_basic_with_console_tracing_custom_attributes.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/telemetry/sample_agent_basic_with_console_tracing_custom_attributes.py).

### Additional resources

For more information see:

* [Trace AI applications using OpenAI SDK](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/trace-application)

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
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
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

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information, see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.

<!-- LINKS -->
[samples]: https://aka.ms/azsdk/azure-ai-projects-v2/python/samples/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[azure_sub]: https://azure.microsoft.com/free/

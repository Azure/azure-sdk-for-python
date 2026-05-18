# Azure AI Projects client library for Python

The AI Projects client library is part of the Microsoft Foundry SDK, and provides easy access to
resources in your Microsoft Foundry Project. Use it to:

* **Create and run Agents** using methods on the `.agents` client property.
* **Enhance Agents with specialized tools**:
  * Agent-to-Agent (A2A) (Preview)
  * Azure AI Search
  * Azure Functions
  * Bing Custom Search (Preview)
  * Bing Grounding
  * Browser Automation (Preview)
  * Code Interpreter
  * Computer Use (Preview)
  * Fabric IQ (Preview)
  * File Search
  * Function Tool
  * Image Generation
  * Memory Search (Preview)
  * Microsoft Fabric (Preview)
  * Microsoft SharePoint (Preview)
  * Model Context Protocol (MCP)
  * OpenAPI
  * Toolbox Search (Preview)
  * Web Search
  * Web Search (Preview)
  * Work IQ (Preview)
* **Get an OpenAI client** using `.get_openai_client()` method to run Responses, Conversations, Evaluations and Fine-Tuning operations with your Agent.
* **Manage memory stores (preview)** for Agent conversations, using `.beta.memory_stores` operations.
* **Explore additional evaluation tools (some in preview)** to assess the performance of your generative AI application, using `.evaluation_rules`,
`.beta.evaluation_taxonomies`, `.beta.evaluators`, `.beta.insights`, and `.beta.schedules` operations.
* **Run Red Team scans (preview)** to identify risks associated with your generative AI application, using `.beta.red_teams` operations.
* **Fine tune** AI Models on your data.
* **Enumerate AI Models** deployed to your Foundry Project using `.deployments` operations.
* **Enumerate connected Azure resources** in your Foundry project using `.connections` operations.
* **Upload documents and create Datasets** to reference them using `.datasets` operations.
* **Create and enumerate Search Indexes** using `.indexes` operations.

The client library uses version `v1` of the Microsoft Foundry [data plane REST APIs](https://aka.ms/azsdk/azure-ai-projects-v2/api-reference-v1).

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
* A [project in Microsoft Foundry](https://learn.microsoft.com/azure/foundry/how-to/create-projects).
* A Foundry project endpoint URL of the form `https://your-ai-services-account-name.services.ai.azure.com/api/projects/your-project-name`. It can be found in your Microsoft Foundry Project home page. Below we will assume the environment variable `FOUNDRY_PROJECT_ENDPOINT` was defined to hold this value.
* Client authentication is done using Entra ID. To authenticate, your application needs an object that implements the [TokenCredential](https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.tokencredential) interface. Code samples here use [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential). To get that working, you will need:
  * An appropriate role assignment. See [Role-based access control in Microsoft Foundry portal](https://learn.microsoft.com/azure/foundry/concepts/rbac-foundry). Role assignment can be done via the "Access Control (IAM)" tab of your Azure AI Project resource in the Azure portal.
  * [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed.
  * You are logged into your Azure account by running `az login`.

### Install the package

```bash
pip install azure-ai-projects
```

Verify that you have version 2.0.0 or above installed by running:

```bash
pip show azure-ai-projects
```

## Key concepts

### Create and authenticate the client with Entra ID

Entra ID is the only authentication method supported at the moment by the client.

To construct a synchronous client using a context manager:

```python
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"], credential=credential) as project_client,
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
    AIProjectClient(endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"], credential=credential) as project_client,
):
```

## Examples

For comprehensive examples covering Agents, tool usage, evaluation, fine-tuning, datasets, indexes, and more, see:

* **[Microsoft Foundry Agents overview](https://learn.microsoft.com/azure/foundry/agents/overview)** — concepts, setup, and quick-starts.
* **[Runtime components](https://learn.microsoft.com/azure/foundry/agents/concepts/runtime-components?tabs=python)** — deep-dive into agent architecture.
* **[Tool catalog](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog)** — all available tools and agent capabilities.
* **[SDK samples folder][samples]** — fully runnable Python code for synchronous and asynchronous clients covering all operations below.

The sections below cover SDK-specific behaviors (authentication variants, exception handling, logging, tracing) that are not documented in the above Learn pages.

### Performing Responses operations using OpenAI client

Use the `.get_openai_client()` method to obtain an authenticated [OpenAI](https://github.com/openai/openai-python) client and run Responses, Conversations, Evaluations, Files, and Fine-Tuning operations. See the **responses**, **agents**, **evaluations**, **files**, and **finetuning** folders in the [samples][samples] for complete working examples.

The code below assumes the environment variable `FOUNDRY_MODEL_NAME` is defined. It's the deployment name of an AI model in your Foundry Project. See "Build" menu, under "Models" (First column of the "Deployments" table).

<!-- SNIPPET:sample_responses_basic.responses -->

```python
with project_client.get_openai_client() as openai_client:
    response = openai_client.responses.create(
        model=os.environ["FOUNDRY_MODEL_NAME"],
        input="What is the size of France in square miles?",
    )
    print(f"Response output: {response.output_text}")

    response = openai_client.responses.create(
        model=os.environ["FOUNDRY_MODEL_NAME"],
        input="And what is the capital city?",
        previous_response_id=response.id,
    )
    print(f"Response output: {response.output_text}")
```

<!-- END SNIPPET -->

See the **responses** folder in the [samples][samples] for additional samples including streaming responses.

### Agents, Tools, Evaluation, Deployments, Connections, Datasets, Indexes, Files, and Fine-Tuning

Full descriptions and working code for all of the above are available in:

| Topic | Learn documentation | Samples folder |
|---|---|---|
| Agents (create, run, stream) | [Agents overview](https://learn.microsoft.com/azure/foundry/agents/overview) | `samples/agents/` |
| Hosted agents (preview) | [Hosted agents concepts](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents), [Deploy your first hosted agent](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent) | `samples/hosted_agents/` |
| Agents tools (Code Interpreter, File Search, MCP, OpenAPI, Bing, A2A, etc.) | [Tool catalog](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog) | `samples/agents/tools/` |
| Evaluation | [Evaluate agents](https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent) | `samples/evaluations/` |
| Deployments | [Deployment types](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/deployment-types) | `samples/deployments/` |
| Connections | [Connections operations](https://learn.microsoft.com/python/api/overview/azure/ai-projects-readme?view=azure-python#connections-operations) | `samples/connections/` |
| Datasets | [Dataset operations](https://learn.microsoft.com/python/api/overview/azure/ai-projects-readme?view=azure-python#dataset-operations) | `samples/datasets/` |
| Indexes | [Azure AI Search](https://learn.microsoft.com/azure/search/search-what-is-azure-search) | `samples/indexes/` |
| Files (upload, retrieve, list, delete) | [OpenAI Files API](https://platform.openai.com/docs/api-reference/files) | `samples/files/` |
| Fine-tuning | [Fine-Tuning in AI Foundry](https://github.com/microsoft-foundry/fine-tuning) | `samples/finetuning/` |

### Hosted agents (preview)

Hosted agents let you run your own containerized agent runtime while using Microsoft Foundry for managed hosting and scaling.

For product guidance, see:

* [Hosted agents concepts](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents)
* [Deploy your first hosted agent](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent)

For SDK usage examples in this package, see `samples/hosted_agents/`, including CRUD, file upload/download, and skills scenarios.

## Client-side tracing

See [Add client-side tracing to Foundry agents (preview)](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-client-side?tabs=python).

**Important:** GenAI tracing instrumentation is an experimental preview feature. Spans, attributes, and events may be modified in future versions. 

Samples can be found in the sub-folders `agents/telemetry` and `telemetry` in the [Samples][samples] folder.

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

The client uses the standard [Python logging library](https://docs.python.org/3/library/logging.html). The logs include HTTP request and response headers and body, which are often useful when troubleshooting or reporting an issue to Microsoft.

#### Default console logging

To turn on client console logging define the environment variable `AZURE_AI_PROJECTS_CONSOLE_LOGGING=true` before running your Python script. Authentication bearer tokens are automatically redacted from the log. Your log may contain other sensitive information, so be sure to remove it before sharing the log with others.

#### Customizing your log

Instead of using the above-mentioned environment variable, you can configure logging yourself and control the log level, format and destination. To log to `stdout`, add the following at the top of your Python script:

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
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    logging_enable=True
)
```

Note that the log level must be set to `logging.DEBUG` (see above code). Logs will be redacted with any other log level.

Be sure to protect non redacted logs to avoid compromising security.

For more information, see [Configure logging in the Azure libraries for Python](https://aka.ms/azsdk/python/logging)

### Reporting issues

To report an issue with the client library, or request additional features, please open a [GitHub issue here](https://github.com/Azure/azure-sdk-for-python/issues). Mention the package name "azure-ai-projects" in the title or content.

## Next steps

Have a look at the [Samples][samples] folder, containing fully runnable Python code for synchronous and asynchronous clients.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information, see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.

<!-- LINKS -->
[samples]: https://aka.ms/azsdk/azure-ai-projects-v2/python/samples/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[azure_sub]: https://azure.microsoft.com/free/

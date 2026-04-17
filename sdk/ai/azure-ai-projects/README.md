# Azure AI Projects client library for Python

The AI Projects client library (in preview) is part of the Microsoft Foundry SDK, and provides easy access to
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
  * File Search
  * Function Tool
  * Image Generation
  * Memory Search (Preview)
  * Microsoft Fabric (Preview)
  * Microsoft SharePoint (Preview)
  * Model Context Protocol (MCP)
  * OpenAPI
  * Web Search
  * Web Search (Preview)
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
* To authenticate using API key, you will need the "Project API key" as shown in your Microsoft Foundry Project home page.
* To authenticate using Entra ID, your application needs an object that implements the [TokenCredential](https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.tokencredential) interface. Code samples here use [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential). To get that working, you will need:
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

* **[Microsoft Foundry Agents overview](https://learn.microsoft.com/azure/foundry/agents/overview)** — concepts, setup, and quickstarts.
* **[Runtime components](https://learn.microsoft.com/azure/foundry/agents/concepts/runtime-components?tabs=python)** — deep-dive into agent architecture.
* **[Tool catalog](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog)** — all available tools and agent capabilities.
* **[SDK samples folder][samples]** — fully runnable Python code for synchronous and asynchronous clients covering all operations below.

The sections below cover SDK-specific behaviours (authentication variants, exception handling, logging, tracing) that are not documented in the above Learn pages.

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

## Tracing

### Experimental Feature Gate

**Important:** GenAI tracing instrumentation is an experimental preview feature. Spans, attributes, and events may be modified in future versions. To use it, you must explicitly opt in by setting the environment variable:

```bash
AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING=true
```

This environment variable must be set before calling `AIProjectInstrumentor().instrument()`. If the environment variable is not set or is set to any value other than `true` (case-insensitive), tracing instrumentation will not be enabled and a warning will be logged.

Only enable this feature after reviewing your requirements and understanding that the tracing behavior may change in future versions.

### Getting Started with Tracing

You can add an Application Insights Azure resource to your Microsoft Foundry project. See the Tracing tab in your Microsoft Foundry project. If one was enabled, you can get the Application Insights connection string, configure your AI Projects client, and observe traces in Azure Monitor. Typically, you might want to start tracing before you create a client or Agent.

For tracing concepts in Microsoft Foundry, see [Trace an agent](https://learn.microsoft.com/azure/foundry/observability/concepts/trace-agent-concept).

### Installation

Make sure to install OpenTelemetry and the Azure SDK tracing plugin via

```bash
pip install "azure-ai-projects>=2.0.0b4" opentelemetry-sdk azure-core-tracing-opentelemetry azure-monitor-opentelemetry
```

You will also need an exporter to send telemetry to your observability backend. You can print traces to the console or use a local viewer such as [Aspire Dashboard](https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone?tabs=bash).

To connect to Aspire Dashboard or another OpenTelemetry compatible backend, install OTLP exporter:

```bash
pip install opentelemetry-exporter-otlp
```

### How to enable tracing

**Remember:** Before enabling tracing, ensure you have set the `AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING=true` environment variable as described in the [Experimental Feature Gate](#experimental-feature-gate) section.

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

See the full sample in file `\agents\telemetry\sample_agent_basic_with_azure_monitor_tracing.py` in the [Samples][samples] folder.

**Note:** In order to view the traces in the Microsoft Foundry portal, the agent ID should be passed in as part of the response generation request.

In addition, you might find it helpful to see the tracing logs in the console. Remember to set `AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING=true` before running the following code:

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

See the full sample in file `\agents\telemetry\sample_agent_basic_with_console_tracing.py` in the [Samples][samples] folder.

### Enabling trace context propagation

Trace context propagation allows client-side spans generated by the Projects SDK to be correlated with server-side spans from Azure OpenAI and other Azure services. When enabled, the SDK automatically injects W3C Trace Context headers (`traceparent` and `tracestate`) into HTTP requests made by OpenAI clients obtained via `get_openai_client()`.

This feature ensures that all operations within a distributed trace share the same trace ID, providing end-to-end visibility across your application and Azure services in your observability backend (such as Azure Monitor).

Trace context propagation is **enabled by default** when tracing is enabled (for example through `configure_azure_monitor` or the `AIProjectInstrumentor().instrument()` call). To disable it, set the `AZURE_TRACING_GEN_AI_ENABLE_TRACE_CONTEXT_PROPAGATION` environment variable to `false`, or pass `enable_trace_context_propagation=False` to the `AIProjectInstrumentor().instrument()` call.

**When does the change take effect?**
- Changes to `enable_trace_context_propagation` (whether via `instrument()` or the environment variable) only affect OpenAI clients obtained via `get_openai_client()` **after** the change is applied. Previously acquired clients are unaffected.
- To apply the new setting to all clients, call `AIProjectInstrumentor().instrument(enable_trace_context_propagation=<value>)` before acquiring your OpenAI clients, or re-acquire the clients after making the change.

**Security and Privacy Considerations:**
- **Trace IDs are sent to external services**: The `traceparent` and `tracestate` headers from your client-side originating spans are injected into requests sent to service. This enables end-to-end distributed tracing, but note that the trace identifier may be shared beyond the initial API call.
- **Enabled by Default**: If you have privacy or compliance requirements that prohibit sharing trace identifiers with services, disable trace context propagation by setting `enable_trace_context_propagation=False` or the environment variable to `false`.

#### Controlling baggage propagation

When trace context propagation is enabled, you can separately control whether the baggage header is included. By default, only `traceparent` and `tracestate` headers are propagated. To also include the `baggage` header, set the `AZURE_TRACING_GEN_AI_TRACE_CONTEXT_PROPAGATION_INCLUDE_BAGGAGE` environment variable to `true`:

If no value is provided for the `enable_baggage_propagation` parameter with the `AIProjectInstrumentor.instrument()` call and the environment variable is not set, the value defaults to `false` and baggage is not included.

**Note:** The `enable_baggage_propagation` flag is evaluated dynamically on each request, so changes take effect **immediately** for all clients that have the trace context propagation hook registered. However, the hook is only registered on clients acquired via `get_openai_client()` **while trace context propagation was enabled**. Clients acquired when trace context propagation was disabled will never propagate baggage, regardless of the `enable_baggage_propagation` value.

**Why is baggage propagation separate?**

The baggage header can contain arbitrary key-value pairs added anywhere in your application's trace context. Unlike trace IDs (which are randomly generated identifiers), baggage may contain:

- User identifiers or session information
- Authentication tokens or credentials
- Business-specific data or metadata
- Personally identifiable information (PII)

Baggage is automatically propagated through your entire application's call chain, meaning data added in one part of your application will be included in requests to Azure OpenAI unless explicitly controlled.

**Important Security Considerations:**

- **Review Baggage Contents**: Before enabling baggage propagation, audit what data your application (and any third-party libraries) adds to OpenTelemetry baggage.
- **Sensitive Data Risk**: Baggage is sent to Azure OpenAI and may be logged or processed by Microsoft services. Never add sensitive information to baggage when baggage propagation is enabled.
- **Opt-in by Design**: Baggage propagation is disabled by default (even when trace context propagation is enabled) to prevent accidental exposure of sensitive data.
- **Minimal Propagation**: `traceparent` and `tracestate` headers are generally sufficient for distributed tracing. Only enable baggage propagation if your specific observability requirements demand it.

### Enabling content recording

Content recording controls whether message contents and tool call related details, such as parameters and return values, are captured with the traces. This data may include sensitive user information.

To enable content recording, set the `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` environment variable to `true`. If the environment variable is not set  and no value is provided with the `AIProjectInstrumentor().instrument()` call for the content recording parameter, content recording defaults to `false`.

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
    def __init__(self) -> None:
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

See the full sample in file `\agents\telemetry\sample_agent_basic_with_console_tracing_custom_attributes.py` in the [Samples][samples] folder.

### Additional resources

For more information see [Agent tracing overview (preview)](https://learn.microsoft.com/azure/foundry/observability/concepts/trace-agent-concept).

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

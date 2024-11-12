
# Azure AI Projects client library for Python
<!-- write necessary description of service -->

## Getting started

### Install the package

```bash
python -m pip install azure-ai-projects
```

#### Prequisites

- Python 3.8 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure Ai Projects instance.
#### Create with an Azure Active Directory Credential
To use an [Azure Active Directory (AAD) token credential][authenticate_with_token],
provide an instance of the desired credential type obtained from the
[azure-identity][azure_identity_credentials] library.

To authenticate with AAD, you must first [pip][pip] install [`azure-identity`][azure_identity_pip]

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.
As an example, [DefaultAzureCredential][default_azure_credential] can be used to authenticate the client:

Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`

Use the returned token credential to authenticate the client:

```python
>>> from azure.ai.projects import AIProjectClient
>>> from azure.identity import DefaultAzureCredential
>>> client = AIProjectClient(endpoint='<endpoint>', credential=DefaultAzureCredential())
```

## Key concepts

TODO

## Examples

### Agents (Private Preview)
Agents in the Azure AI Projects client library are designed to facilitate various interactions and operations within your AI projects. They serve as the core components that manage and execute tasks, leveraging different tools and resources to achieve specific goals. The following steps outline the typical sequence for interacting with agents:

Agents are actively being developed. A sign-up form for private preview is coming soon.

  - <a href='#create-project-client'>Create project client</a>
  - <a href='#create-agent'>Create agent</a> with:
    - <a href='#create-agent-with-file-search'>File Search</a>
    - <a href='#create-agent-with-code-interpreter'>Code interpreter</a>
    - <a href='#create-agent-with-bing-grounding'>Bing grounding</a>
    - <a href='#create-agent-with-azure-ai-search'>Azure AI Search</a>
    - <a href='#create-agent-with-function-call'>Function call</a>
  - <a href='#create-thread'>Create thread</a> with
     - <a href='#create-thread-with-tool-resource'>Tool resource</a>
  - <a href='#create-message'>Create message</a> with:
    - <a href='#create-message-with-file-search-attachment'>File search attachment</a>
    - <a href='#create-message-with-code-interpreter-attachment'>Code interpreter attachment</a>
  - <a href='#create-run-run_and_process-or-stream'>Execute Run, Run_and_Process, or Stream</a>
  - <a href='#retrieve-message'>Retrieve message</a>
  - <a href='#retrieve-file'>Retrieve file</a>
  - <a href='#teardown'>Tear down by deleting resource</a>
  - <a href='#tracing'>Tracing</a>


#### Create Project Client

When you create a project client, you need to make the decision to use synchronous or asynchronous client. Use either:

```python
from azure.ai.projects import AIProjectClient
# OR
from azure.ai.projects.aio import AIProjectClient
```

Here is an example of creating a project client:
<!-- SNIPPET:sample_agents_basics.create_project_client -->

```python
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)
```

<!-- END SNIPPET -->

Because the client is under resource and context manager, you are required to use `with` or `async with` to consume the client object:

```python
# For synchronous
with project_client:
    agent = project_client.agents.create_agent(
                model="gpt-4-1106-preview", 
                name="my-assistant", 
                instructions="You are helpful assistant"
 )

```

In the sections below, we will only provide code snippets in synchronous functions.

#### Create Agent

Now you should have your project client.  From the project client, you create an agent to serve the end users.  

Here is an example of create an agent:
<!-- SNIPPET:sample_agents_basics.create_agent -->

```python
agent = project_client.agents.create_agent(
    model="gpt-4-1106-preview", name="my-assistant", instructions="You are helpful assistant"
)
```

<!-- END SNIPPET -->

To allow agents to access your resources or custom functions, you need tools.   You can pass tools to `create_agent` by either `toolset` or combination of `tools` and `tool_resources`.

Here is an example of `toolset`:
<!-- SNIPPET:sample_agents_run_with_toolset.create_agent_toolset -->

```python
functions = FunctionTool(user_functions)
code_interpreter = CodeInterpreterTool()

toolset = ToolSet()
toolset.add(functions)
toolset.add(code_interpreter)

agent = project_client.agents.create_agent(
    model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant", toolset=toolset
)
```

<!-- END SNIPPET -->

Also notices that if you use asynchronous client, you use `AsyncToolSet` instead.  Additional information related to `AsyncFunctionTool` be discussed in the later sections.

Here is an example to use `tools` and `tool_resources`:
<!-- SNIPPET:sample_agents_vector_store_batch_file_search.create_agent_with_tools_and_tool_resources -->

```python
file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

# notices that FileSearchTool as tool and tool_resources must be added or the assistant unable to search the file
agent = project_client.agents.create_agent(
    model="gpt-4-1106-preview",
    name="my-assistant",
    instructions="You are helpful assistant",
    tools=file_search_tool.definitions,
    tool_resources=file_search_tool.resources,
)
```

<!-- END SNIPPET -->

In the following sections, we show you code snips in either `toolset` or combination of `tools` and `tool_resources`.   But you are welcome to use another approach.

#### Create Agent with File Search
To perform file search by an agent, we first need to upload a file, create a vector store, and associate the file to the vector store.
Here is an example:

<!-- SNIPPET:sample_agents_file_search.upload_file_create_vector_store_and_agent_with_file_search_tool -->

```python
file = project_client.agents.upload_file_and_poll(file_path="product_info_1.md", purpose="assistants")
print(f"Uploaded file, file ID: {file.id}")

vector_store = project_client.agents.create_vector_store_and_poll(file_ids=[file.id], name="my_vectorstore")
print(f"Created vector store, vector store ID: {vector_store.id}")

# Create file search tool with resources followed by creating agent
file_search = FileSearchTool(vector_store_ids=[vector_store.id])

agent = project_client.agents.create_agent(
    model="gpt-4-1106-preview",
    name="my-assistant",
    instructions="Hello, you are helpful assistant and can search information from uploaded files",
    tools=file_search.definitions,
    tool_resources=file_search.resources,
)
```

<!-- END SNIPPET -->


#### Create Agent with Code Interpreter

Here is an example to upload a file and use it for code interpreter by an agent:

<!-- SNIPPET:sample_agents_code_interpreter.upload_file_and_create_agent_with_code_interpreter -->

```python
file = project_client.agents.upload_file_and_poll(
    file_path="nifty_500_quarterly_results.csv", purpose=FilePurpose.AGENTS
)
print(f"Uploaded file, file ID: {file.id}")

code_interpreter = CodeInterpreterTool(file_ids=[file.id])

# create agent with code interpreter tool and tools_resources
agent = project_client.agents.create_agent(
    model="gpt-4-1106-preview",
    name="my-assistant",
    instructions="You are helpful assistant",
    tools=code_interpreter.definitions,
    tool_resources=code_interpreter.resources,
)
```

<!-- END SNIPPET -->


#### Create Agent with Bing Grounding
To enable your agent to perform search through Bing search API, you use `BingGroundingTool` along with a connection.

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
        model="gpt-4-1106-preview",
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
ai_search = AzureAISearchTool()
ai_search.add_index(conn_id, "sample_index")

# Create agent with AI search tool and process assistant run
with project_client:
    agent = project_client.agents.create_agent(
        model="gpt-4-1106-preview",
        name="my-assistant",
        instructions="You are a helpful assistant",
        tools=ai_search.definitions,
        headers={"x-ms-enable-preview": "true"},
    )
```

<!-- END SNIPPET -->

#### Create Agent with Function Call

You can enhance your agents by defining callback functions as function tools. These can be provided to `create_agent` via either the `toolset` parameter or the combination of `tools` and `tool_resources`. Here are the distinctions:

- `toolset`: When using the `toolset` parameter, you provide not only the function definitions and descriptions but also their implementations. The SDK will execute these functions within `create_and_run_process` or `streaming` . These functions will be invoked based on their definitions.
- `tools` and `tool_resources`: When using the `tools` and `tool_resources` parameters, only the function definitions and descriptions are provided to `create_agent`, without the implementations. The `Run` or `event handler of stream` will raise a `requires_action` status based on the function definitions. Your code must handle this status and call the appropriate functions.
 
For more details about calling functions by code, refer to [`sample_agents_stream_eventhandler_with_functions.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/sample_agents_stream_eventhandler_with_functions.py) and [`sample_agents_functions.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/sample_agents_functions.py).

Here is an example to use [user functions](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/user_functions.py) in `toolset`:
<!-- SNIPPET:sample_agents_stream_eventhandler_with_toolset.create_agent_with_function_tool -->

```python
functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)

agent = project_client.agents.create_agent(
    model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant", toolset=toolset
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
    model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant", toolset=toolset
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

In some scenarios, you might need to assign specific resources to individual threads. To achieve this, you provide the `tool_resources` argument to `create_thread`. In the following example, you create a vector store and upload a file, enable an agent for file search using the `tools` argument, and then associate the file with the thread using the `tool_resources` argument.


<!-- SNIPPET:sample_agents_with_resources_in_thread.create_agent_and_thread_for_file_search -->

```python
file = project_client.agents.upload_file_and_poll(file_path="product_info_1.md", purpose="assistants")
print(f"Uploaded file, file ID: {file.id}")

vector_store = project_client.agents.create_vector_store_and_poll(file_ids=[file.id], name="my_vectorstore")
print(f"Created vector store, vector store ID: {vector_store.id}")

# Create file search tool with resources followed by creating agent
file_search = FileSearchTool(vector_store_ids=[vector_store.id])

agent = project_client.agents.create_agent(
    model="gpt-4-1106-preview",
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
To attach a file to a message for data analysis, you use `MessageAttachment` and `CodeInterpreterTool`.  You must pass `CodeInterpreterTool` as `tools` or `toolset` in `create_agent` call or the file attachment cannot be opened for code interpreter.  

Here is an example to pass `CodeInterpreterTool` as tool:

<!-- SNIPPET:sample_agents_with_code_interpreter_file_attachment.create_agent_and_message_with_code_interpreter_file_attachment -->

```python
# notice that CodeInterpreter must be enabled in the agent creation,
# otherwise the agent will not be able to see the file attachment for code interpretation
agent = project_client.agents.create_agent(
    model="gpt-4-1106-preview",
    name="my-assistant",
    instructions="You are helpful assistant",
    tools=CodeInterpreterTool().definitions,
)
print(f"Created agent, agent ID: {agent.id}")

thread = project_client.agents.create_thread()
print(f"Created thread, thread ID: {thread.id}")

# create an attachment
attachment = MessageAttachment(file_id=file.id, tools=CodeInterpreterTool().definitions)

# create a message
message = project_client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="Could you please create bar chart in TRANSPORTATION sector for the operating profit from the uploaded csv file and provide file to me?",
    attachments=[attachment],
)
```

<!-- END SNIPPET -->

#### Create Run, Run_and_Process, or Stream

To process your message, you can use `create_run`, `create_and_process_run`, or `create_stream`.

`create_run` requests the agent to process the message without polling for the result. If you are using `function tools` regardless as `toolset` or not, your code is responsible for polling for the result and acknowledging the status of `Run`. When the status is `requires_action`, your code is responsible for calling the function tools. For a code sample, visit [`sample_agents_functions.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/sample_agents_functions.py).

Here is an example of `create_run` and poll until the run is completed:

<!-- SNIPPET:sample_agents_basics.create_run -->

```python
run = project_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)

# poll the run as long as run status is queued or in progress
while run.status in ["queued", "in_progress", "requires_action"]:
    # wait for a second
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

With streaming, polling also need not be considered.   If `function tools` are provided as `toolset` during the `create_agent` call, they will be invoked by the SDK.

Here is an example:

<!-- SNIPPET:sample_agents_stream_eventhandler.create_stream -->

```python
with project_client.agents.create_stream(
    thread_id=thread.id, assistant_id=agent.id, event_handler=MyEventHandler()
) as stream:
    stream.until_done()
```

<!-- END SNIPPET -->

The event handler is optional. Here is an example:

<!-- SNIPPET:sample_agents_stream_eventhandler.stream_event_handler -->

```python
class MyEventHandler(AgentEventHandler):
    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        for content_part in delta.delta.content:
            if isinstance(content_part, MessageDeltaTextContent):
                text_value = content_part.text.value if content_part.text else "No text"
                print(f"Text delta received: {text_value}")

    def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

    def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    def on_done(self) -> None:
        print("Stream completed.")

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")
```

<!-- END SNIPPET -->


#### Retrieve Message

To retrieve messages from agents, use the following example:

<!-- SNIPPET:sample_agents_basics.list_messages -->

```python
messages = project_client.agents.list_messages(thread_id=thread.id)
last_message_content = messages.data[-1].content[-1].text.value
print(f"Last message content: {last_message_content}")
```

<!-- END SNIPPET -->

Depending on the use case, if you expect the agents to return only text messages, `list_messages` should be sufficient.
If you are using tools, consider using the `get_messages` function instead. This function classifies the message content and returns properties such as `text_messages`, `image_contents`, `file_citation_annotations`, and `file_path_annotations`.

### Retrieve File

Files uploaded by agents cannot be retrieved back.  If your use case need to access the file content uploaded by the agents, you are adviced to keep an additional copy accessible by your application.   However, files generated by agents are retrievable by `save_file` or `get_file_content`.  

Here is an example retrieving file ids from messages and save to the local drive:

<!-- SNIPPET:sample_agents_code_interpreter.get_messages_and_save_files -->

```python
messages = project_client.agents.get_messages(thread_id=thread.id)
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

#### Tracing

As part of Azure AI project, you can use the its connection string and observe the full execution path through Azure Monitor.  Typically you might want to start tracing before you create an agent.   

##### Installation

Make sure to install OpenTelemetry and the Azure SDK tracing plugin via

```bash
pip install opentelemetry
pip install azure-core-tracing-opentelemetry
```

You will also need an exporter to send telemetry to your observability backend. You can print traces to the console or use a local viewer such as [Aspire Dashboard](https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone?tabs=bash).

To connect to Aspire Dashboard or another OpenTelemetry compatible backend, install OTLP exporter:

```bash
pip install opentelemetry-exporter-otlp
```

##### Examples
Here is a code snip to be included above `create_agent`:

<!-- SNIPPET:sample_agents_basics_with_azure_monitor_tracing.enable_tracing -->

```python
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor

# Enable Azure Monitor tracing
application_insights_connection_string = project_client.telemetry.get_connection_string()
if not application_insights_connection_string:
    print("Application Insights was not enabled for this project.")
    print("Enable it via the 'Tracing' tab in your AI Studio project page.")
    exit()
configure_azure_monitor(connection_string=application_insights_connection_string)

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span(scenario):
    with project_client:
```

<!-- END SNIPPET -->

In additional, you might find helpful to see the tracing logs in console.   You can achieve by the following code:

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
    result = client.connections.list()
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
client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=project_connection_string,
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
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/

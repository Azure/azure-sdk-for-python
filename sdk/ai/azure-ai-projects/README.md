
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

## Examples

### Agents
The following steps outline the typical sequence for interacting with agents:

  - <a href='#create-project-client'>Create a project client</a>
  - <a href='#create-agent'>Create an agent</a> with <a href='#create-agent-with-toolset-or-tools-and-tool-resources'>toolset, or tools and tool resources</a> including:
    - <a href='#create-agent-with-file-upload-in-vector-store-for-file-search'>File Search with file upload indexed by vector stores</a>
    - <a href='#create-agent-with-file-upload-for-code-interpreter'>Code Interpreter with file upload</a>
    - <a href='#create-agent-with-function-tool'>Function calls</a>
  - <a href='#create-thread'>Create a thread</a>
  - <a href='#create-message'>Create a message</a> with:
    - <a href='#create-message-with-file-search-attachment'>File search attachment</a>
    - <a href='#create-message-with-code-interpreter-file-attachment'>Code interpreter attachment</a>
  - <a href='#create-run-run_and_process-or-stream'>Execute Run, Run_and_Process, or Stream</a>
  - <a href='#retrieve-messages'>Retrieve messages</a>
  - <a href='#teardown'>Tear down by deleting resources</a>


#### Create Project Client

When you create an project client, you need to make the decision to use synchronized or asynchronized client.  Use either:

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

#### Create Agent

Here is an example of create an agent:
<!-- SNIPPET:sample_agents_basics.create_agent -->

```python
   
 agent = project_client.agents.create_agent(
     model="gpt-4-1106-preview", name="my-assistant", instructions="You are helpful assistant"
 )
```

<!-- END SNIPPET -->

#### Create Agent with Toolset, or Tools and Tool Resources
In order to use tools, you can provide toolset.  Here is an example:
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

Alternatively you can provide tool and tool resources.   Here is an example:
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

#### Create Agent with File Upload in Vector Store for File Search
To perform file search by an agent, we first need to upload a file, create a vector store, and associate the file to the vector store.
Here is an example:

<!-- SNIPPET:sample_agents_file_search.upload_file_create_vector_store_and_agent_with_file_search_tool -->

```python
file = project_client.agents.upload_file_and_poll(file_path="product_info_1.md", purpose="assistants")
print(f"Uploaded file, file ID: {file.id}")

vector_store = project_client.agents.create_vector_store_and_poll(
    file_ids=[file.id], name="my_vectorstore"
)
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

Again, you can define `toolset` instead of passing `tools` and `tool_resources`.

#### Create Agent with File Upload for Code Interpreter
Here is an example to upload a file and use it for code interpreter by an agent:

<!-- SNIPPET:sample_agents_code_interpreter.upload_file_and_creae_agent_with_code_interpreter -->

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

#### Create Agent with Function Tool
You can enhance your agents by defining callback functions as function tools. These can be provided to `create_agent` via either the `toolset` parameter or the combination of `tools` and `tool_resources`. Here are the distinctions:

- `toolset`: When using the `toolset` parameter, you provide not only the function definitions and descriptions but also their implementations. The SDK will execute these functions within `create_and_run_process` or `streaming` . These functions will be invoked based on their definitions.
- `tools` and `tool_resources`: When using the `tools` and `tool_resources` parameters, only the function definitions and descriptions are provided to `create_agent`, without the implementations. The `Run` or `event handler of stream` will raise a `requires_action` status based on the function definitions. Your code must handle this status and call the appropriate functions.
 
For more details about calling functions by code, refer to [`sample_agents_stream_eventhandler_with_functions.py`](samples/agents/sample_agents_stream_eventhandler_with_functions.py) and [`sample_agents_functions.py`](samples/agents/sample_agents_functions.py).

Here is an example to use [user functions](samples/agents/user_function.py) in `toolset`:
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

For asynchronized functions, you must import `AIProjectClient` from `azure.ai.projects.aio` and use `AsyncFunctionTool`.   Here is an example using [asynchronized user functions](samples/agents/async_samples/user_async_functions.py):   

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

#### Create Message with Code Interpreter File Attachment
To attach a file to a message for data analysis, you use `MessageAttachment` and `CodeInterpreterTool`.  You must pass `CodeInterpreterTool` as `tools` or `toolset` in `create_agent` call or the file attachment cannot be opened for code interpreter.  Here is an example:

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
    attachments=[attachment]
)
```

<!-- END SNIPPET -->

#### Create Run, Run_and_Process, or Stream

To process your message, you can use `create_run`, `create_and_process_run`, or `create_stream`.

`create_run` requests the agent to process the message without polling for the result. If you are using `function tools` regardless as `toolset` or not, your code is responsible for polling for the result and acknowledging the status of `Run`. When the status is `requires_action`, your code is responsible for calling the function tools. For a code sample, visit [`sample_agents_functions.py`](samples/agents/sample_agents_functions.py).

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

<!-- END SNIPPET -->

#### Retrieve Messages

To retrieve messages from agents, use the following example:

<!-- SNIPPET:sample_agents_basics.list_messages -->

```python
messages = project_client.agents.list_messages(thread_id=thread.id)
```

<!-- END SNIPPET -->

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

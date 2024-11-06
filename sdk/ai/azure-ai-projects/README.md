

# Azure Ai Projects client library for Python
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

1. Create a project client.
2. Upload files and associate them with a vector store for file search.
3. Create a thread.
4. Create a message.
5. Execute `Run`, `Run_and_Process`, or `Stream`.
6. Clean up by deleting resources.

Additionally, you can retrieve messages.

#### Create Project Client

To create a project client, use the following example:

<!-- SNIPPET:sample_agents_basics.create_project_client -->

```python
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)
```

<!-- END SNIPPET -->

#### Create Vector Store and Upload File

To enable agents to search your files, upload the files and associate them with a vector store:

<!-- SNIPPET:sample_agents_file_search.upload_file_and_create_vector_store -->

```python
file = project_client.agents.upload_file_and_poll(file_path="product_info_1.md", purpose="assistants")
vector_store = project_client.agents.create_vector_store_and_poll(
    file_ids=[file.id], name="my_vectorstore"
)
```

<!-- END SNIPPET -->

Note: If the file is for code interpretation and not for file search, a vector store is not needed.

### Create Agent

To create an agent with file search capabilities, use the following example:

<!-- SNIPPET:sample_agents_file_search.create_agent_with_file_search_tool -->

```python
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

Alternatively, you can create an agent using a toolset. Agents can utilize various tools such as `FunctionTool`. Here is an example with user function in [samples/agents/user_functions.py](../../samples/agents/user_functions.py):

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

#### Create Thread

To create a thread, use the following example:

<!-- SNIPPET:sample_agents_basics.create_thread -->

```python
   
 thread = project_client.agents.create_thread()
```

<!-- END SNIPPET -->

#### Create Message

To create a message and provide a file as an attachment, use the following example:

<!-- SNIPPET:sample_agents_with_file_search_attachment.create_message_with_attachment -->

```python
attachment = MessageAttachment(file_id=file.id, tools=FileSearchTool().definitions)
message = project_client.agents.create_message(
    thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?", attachments=[attachment]
)
```

<!-- END SNIPPET -->

#### Create Run, Run_and_Process, or Stream

To process your message, you can use `create_run`, `create_and_process_run`, or `create_stream`.

Here is an example using `create_run`:

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

Here is an example using `create_and_process_run`:

<!-- SNIPPET:sample_agents_run_with_toolset.create_and_process_run -->

```python
run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
```

<!-- END SNIPPET -->

Here is an example using `create_stream`:

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

#### Get Messages

To retrieve messages from agents, use the following example:

<!-- SNIPPET:sample_agents_basics.list_messages -->

```python
messages = project_client.agents.list_messages(thread_id=thread.id)
```

<!-- END SNIPPET -->

## Examples

```python
>>> from azure.ai.projects import AIProjectClient
>>> from azure.identity import DefaultAzureCredential
>>> from azure.core.exceptions import HttpResponseError

>>> client = AIProjectClient(endpoint='<endpoint>', credential=DefaultAzureCredential())
>>> try:
        <!-- write test code here -->
    except HttpResponseError as e:
        print('service responds error: {}'.format(e.response.json()))

```

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




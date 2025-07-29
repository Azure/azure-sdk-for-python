# Agents migration guide from Hub-based projects to Endpoint-based projects

This guide describes migration from hub-based to Endpoint-based projects. To create a Endpoint-based project, please use one of the deployment scripts on [foundry samples repository](https://github.com/azure-ai-foundry/foundry-samples/tree/main/samples/microsoft/infrastructure-setup) appropriate for your scenario, also you can use Azure AI Foundry UI. The support of hub-based projects was dropped in `azure-ai-projects` version `1.0.0b11`. In this document, we show the operation implementation of before `1.0.0b11` in **Hub-based** section, followed by code for `azure-ai-projects` version `1.0.0b11` or later in **Endpoint-based**.

## Import changes

| Hub-based | Endpoint-based |
|-|-|
| `azure.ai.projects` | `azure.ai.projects` |
| `azure.ai.projects.models` | `azure.ai.agents.models` |
| Agents were moved to a new package. | `azure.ai.agents` |

## Class structure changes

Agents Operations

| Hub-based | Endpoint-based |
|-|-|
| `project_client.agents.create_agent` | `project_client.agents.create_agent` |
| `project_client.agents.list_agents` | `project_client.agents.list_agents` |
| `project_client.agents.get_agent` | `project_client.agents.get_agent` |
| `project_client.agents.update_agent` | `project_client.agents.update_agent` |
| `project_client.agents.delete_agents` | `project_client.agents.delete_agent` |
| `project_client.agents.create_thread_and_run` | `project_client.agents.create_thread_and_run` |
| `project_client.agents.enable_auto_function_calls` | `project_client.agents.enable_auto_function_calls` |
| The new method was added in new SDK version. | `project_client.agents.create_thread_and_process_run` |

Threads Operations

| Hub-based | Endpoint-based |
|-|-|
| `project_client.agents.create_thread` | `project_client.agents.threads.create` |
| `project_client.agents.get_thread` | `project_client.agents.threads.get` |
| `project_client.agents.update_thread` | `project_client.agents.threads.update` |
| `project_client.agents.list_threads` | `project_client.agents.threads.list` |
| `project_client.agents.delete_thread` | `project_client.agents.threads.delete` |

Messages Operations

| Hub-based | Endpoint-based |
|-|-|
| `project_client.agents.create_message` | `project_client.agents.messages.create` |
| `project_client.agents.list_messages` | `project_client.agents.messages.list` |
| `project_client.agents.get_message` | `project_client.agents.messages.get` |
| `project_client.agents.update_message` | `project_client.agents.messages.update` |
| `OpenAIPageableListOfThreadMessage.get_last_message_by_role` | `project_client.agents.messages.get_last_message_by_role` |
| `OpenAIPageableListOfThreadMessage.get_last_text_message_by_role` | `project_client.agents.messages.get_last_message_text_by_role` |

Runs Operations

| Hub-based | Endpoint-based |
|-|-|
| `project_client.agents.create_run` | `project_client.agents.runs.create` |
| `project_client.agents.get_run` | `project_client.agents.runs.get` |
| `project_client.agents.list_run` | `project_client.agents.runs.list` |
| `project_client.agents.update_run` | `project_client.agents.runs.update` |
| `project_client.agents.create_and_process_run` | `project_client.agents.runs.create_and_process` |
| `project_client.agents.create_stream` | `project_client.agents.runs.stream` |
| `project_client.agents.submit_tool_outputs_to_run` | `project_client.agents.runs.submit_tool_outputs` |
| `project_client.agents.submit_tool_outputs_to_run` | `project_client.agents.runs.submit_tool_outputs_stream` |
| `project_client.agents.cancel_run` | `project_client.agents.runs.cancel` |

Run Steps Operations

| Hub-based | Endpoint-based |
|-|-|
| `project_client.agents.get_run_step` | `project_client.agents.run_steps.get` |
| `project_client.agents.list_run_steps` | `project_client.agents.run_steps.list` |

Vector Stores Operations

| Hub-based | Endpoint-based |
|-|-|
| `project_client.agents.create_vector_store_and_poll` | `project_client.agents.vector_stores.create_and_poll |
| `project_client.agents.create_vector_store` | `project_client.agents.vector_stores.create |
| `project_client.agents.list_vector_stores` | `project_client.agents.vector_stores.list |
| `project_client.agents.get_vector_store` | `project_client.agents.vector_stores.get |
| `project_client.agents.modify_vector_store` | `project_client.agents.vector_stores.modify |
| `project_client.agents.delete_vector_store` | `project_client.agents.vector_stores.delete |

Vector Store Files Operations

| Hub-based | Endpoint-based |
|-|-|
| `project_client.agents.create_vector_store_file_and_poll` | `project_client.agents.vector_store_files.create_and_poll` |
| `project_client.agents.list_vector_store_files` | `project_client.agents.vector_store_files.list` |
| `project_client.agents.create_vector_store_file` | `project_client.agents.vector_store_files.create` |
| `project_client.agents.get_vector_store_file` | `project_client.agents.vector_store_files.get` |
| `project_client.agents.delete_vector_store_file` | `project_client.agents.vector_store_files.delete` |

Vector Store File Batches Operations

| Hub-based | Endpoint-based |
|-|-|
| `project_client.agents.create_vector_store_file_and_poll` | `project_client.agents.vector_store_file_batches.create_and_poll`|
| `project_client.agents.create_vector_store_file_batch` | `project_client.agents.vector_store_file_batches.create`|
| `project_client.agents.get_vector_store_file_batch` | `project_client.agents.vector_store_file_batches.get`|
| `project_client.agents.list_vector_store_file_batch_files` | `project_client.agents.vector_store_file_batches.list_files`|
| `project_client.agents.cancel_vector_store_file_batch` | `project_client.agents.vector_store_file_batches.cancel`|

Files Operations

| Hub-based | Endpoint-based |
|-|-|
| `project_client.agents.upload_file_and_poll` | `project_client.agents.files.upload_and_poll` |
| `project_client.agents.upload_file` | `project_client.agents.files.upload` |
| `project_client.agents.save_file` | `project_client.agents.files.save` |
| `project_client.agents.get_file` | `project_client.agents.files.get` |
| `project_client.agents.list_files` | `project_client.agents.files.list` |
| `project_client.agents.delete_file` | `project_client.agents.files.delete` |

## API changes

1. Create project. The connection string is replaced by the endpoint. The project endpoint URL has the form https://\<your-ai-services-account-name\>.services.ai.azure.com/api/projects/\<your-project-name\>. It can be found in your Azure AI Foundry Project overview page.

    **Hub-based**

    ```python
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=connection_string,
    )
    ```

    **Endpoint-based**

    ```python
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    ```

2. Crate an agent. In the new versions of SDK, the agent can be created using project client or directly created by using `AgentsClient` constructor. In the code below, `project_client.agents`is an `AgentsClient` instance so `project_client.agents` and `agents_client` can be used interchangeably. For simplicity we will use ` project_client.agents `.

    **Hub-based**

    ```python
    agent = project_client.agents.create_agent(
        model= "gpt-4o",
        name="my-assistant",
        instructions="You are helpful assistant",
    )
    ```

    **Endpoint-based**

    Agent is instantiated using `AIProjectClient`

    ```python
    agent = project_client.agents.create_agent(
        model="gpt-4o",
        name="my-agent",
        instructions="You are helpful agent",
    )
    ```

    Agent is instantiated using `AgentsClient` constructor:

    ```python
    from azure.ai.agents import AgentsClient

    agents_client = AgentsClient(
        endpoint=connection_string,
        credential=DefaultAzureCredential(),
    )
    agent = agents_client.create_agent(
        model="gpt-4o",
        name="my-agent",
        instructions="You are helpful agent",
    )
    ```

3. List agents. New version of SDK allows more convenient ways of listing threads, messages and agents by returning `ItemPaged` and `AsyncItemPaged`. The list of returned items is split by pages, which may be consequently returned to user. Below we will demonstrate this mechanism for agents. The `limit` parameter defines the number of items on the page. This example is also applicable for listing threads, runs, run steps, vector stores, files in vector store, and messages.

    **Hub-based**

    ```python
    has_more = True
    last_id = None
    while has_more:
        agents_list = project_client.agents.list_agents(after=last_id)
        for agent in agents_list.data:
            print(agent.id)
        has_more = agents_list.has_more
        last_id = agents_list.last_id
    ```

    **Endpoint-based**

    ```python
    agents = project_client.agents.list_agents(limit=2)
     # Iterate items by page. Each page will be limited by two items.
     for i, page in enumerate(agents.by_page()):
             print(f"Items on page {i}")
             for one_agent in page:
                 print(one_agent.id)
       
    # Iterate over all agents. Note, the agent list object needs to be re instantiated, the same object cannot be reused after iteration.
    agents = project_client.agents.list_agents(limit=2)
    for one_agent in agents:
             print(one_agent.id)
    ```

4. Delete agent. In versions azure-ai-projects 1.0.0b11, all deletion operations used to return deletion status, for example, deletion of agent was returning `AgentDeletionStatus`. In 1.0.0b11 and later, these operations do not return a value.

    **Hub-based**

    ```python
    deletion_status = project_client.agents.delete_agent(agent.id)
    print(deletion_status.deleted)
    ```

    **Endpoint-based**

    ```python
    project_client.agents.delete_agent(agent.id)
    ```

5. Create a thread.

    **Hub-based**

    ```python
    thread = project_client.agents.create_thread()
    ```

    **Endpoint-based**

    ```python
    thread = project_client.agents.threads.create()
    ```

6. List threads.

    **Hub-based**

    ```python
    with project_client:
        last_id = None
        has_more = True
        page = 0
        while has_more:
            threads = project_client.agents.list_threads(limit=2, after=last_id)
            print(f"Items on page {page}")
            for thread in threads.data:
                print(thread.id)
            has_more = threads.has_more
            last_id = threads.last_id
            page += 1
    ```

    **Endpoint-based**

    ```python
    threads = project_client.agents.threads.list(limit=2)
    # Iterate items by page. Each page will be limited by two items.
    for i, page in enumerate(threads.by_page()):
          print(f"Items on page {i}")
          for thread in page:
              print(thread.id)

    # Iterate over all threads. Note, the thread list object needs to be re-instantiated, the same object cannot be reused after iteration.
    threads = project_client.agents.threads.list(limit=2)
    for thread in threads:
        print(thread.id)
    ```

7. Delete the thread. In previous SDK thread deletion used to return ` ThreadDeletionStatus` object, while in new version it does not return value.

    **Hub-based**

    ```python
    delete_status = project_client.agents.delete_thread(tread_id)
    print(delete_status.deleted)
    ```

    **Endpoint-based**

    ```python
    project_client.agents.threads.delete(tread_id)
    ```

8. Create the message on a thread.

    **Hub-based**

    ```python
    message = project_client.agents.create_message(thread_id=thread.id, role="user", content="The message text.")
    ```

    **Endpoint-based**

    ```python
    message = agents_client.messages.create(thread_id=thread.id, role="user", content=" The message text."")
    ```

9. Create and get the run.

    **Hub-based**

    ```python
    run = project_client.agents.runs.create(thread_id=thread.id, agent_id=agent.id)
    run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
    ```

    **Endpoint-based**

    ```python
    run = project_client.agents.runs.create(thread_id=thread.id, agent_id=agent.id)
    run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
    ```

10. List Runs.

    **Hub-based**

    ```python
    has_more = True
    last_id = None
    while has_more:
        runs_list = project_client.agents.list_runs(thread.id)
        for one_run in runs_list.data:
            print(one_run.id)
        has_more = runs_list.has_more
        last_id = runs_list.last_id
    ```

    **Endpoint-based**

    ```python
    runs = project_client.agents.runs.list(thread.id)
    for one_run in runs:
        print(one_run.id)
    ```

11. List Run steps.

    **Hub-based**

    ```python
    has_more = True
    last_id = None
    while has_more:
        runs_step_list = project_client.agents.list_run_steps(thread.id, run.id)
        for one_run_step in runs_step_list.data:
            print(one_run_step.id)
        has_more = runs_step_list.has_more
        last_id = runs_step_list.last_id
    ```

    **Endpoint-based**

    ```python
    run_steps = project_client.agents.run_steps.list(thread.id, run.id)
    for one_run_step in run_steps:
        print(one_run_step.id)
    ```

12. Using streams.

    **Hub-based**

    ```python
    with project_client.agents.create_stream(thread_id=thread.id, agent_id=agent.id) as stream:
        for event_type, event_data, func_return in stream:
                print(f"Received data.")
                print(f"Streaming receive Event Type: {event_type}")
                print(f"Event Data: {str(event_data)[:100]}...")
                print(f"Event Function return: {func_return}\n")
    ```

    **Endpoint-based**

    ```python
    with project_client.agents.runs.stream(thread_id=thread.id, agent_id=agent.id, event_handler=MyEventHandler()) as stream:
            for event_type, event_data, func_return in stream:
                print(f"Received data.")
                print(f"Streaming receive Event Type: {event_type}")
                print(f"Event Data: {str(event_data)[:100]}...")
                print(f"Event Function return: {func_return}\n")
    ```

13. List messages.

    **Hub-based**

    ```python
    messages = project_client.agents.list_messages(thread_id=thread.id)
        # In code below we assume that the number of messages fits one page for brevity.
        for data_point in reversed(messages.data):
            last_message_content = data_point.content[-1]
            if isinstance(last_message_content, MessageTextContent):
                print(f"{data_point.role}: {last_message_content.text.value}")
    ```

    **Endpoint-based**

    ```python
    messages = project_client.agents.messages.list(thread_id=thread.id)
        for msg in messages:
            if msg.text_messages:
                last_text = msg.text_messages[-1]
                print(f"{msg.role}: {last_text.text.value}")
    ```

14. Create, list and delete files are now handled by file operations, again, delete call in new SDK version does not return a value.

    **Hub-based**

    ```python
    # Create file
    file = project_client.agents.upload_file_and_poll(file_path="product_info_1.md", purpose=FilePurpose.AGENTS)
    # List and enumerate files
    files = project_client.agents.list_files()
        for one_file in files.data:
            print(one_file.id)
    # Delete file.
    delete_status = project_client.agents.delete_file(file.id)
    print(delete_status.deleted)
    ```

    **Endpoint-based**

    ```python
    # Create file
    file = project_client.agents.files.upload_and_poll(file_path=asset_file_path, purpose=FilePurpose.AGENTS)
    # List and enumerate files
    files = project_client.agents.files.list()
    for one_file in files.data:
        print(one_file.id)
    # Delete file.
    project_client.agents.files.delete(file_id=file.id)
    ```

15. Create, list vector store files list and delete vector stores.

    **Hub-based**

    ```python
    # Create a vector store with no file and wait for it to be processed
        vector_store = project_client.agents.create_vector_store_and_poll(file_ids=[file.id], name="sample_vector_store")
    # List vector stores
    has_more = True
    last_id = None
    while has_more:
        vector_store_list = project_client.agents.list_vector_stores(after=last_id)
        for one_vector_store in vector_store_list.data:
            print(one_vector_store.id)
        has_more = vector_store_list.has_more
        last_id = vector_store_list.last_id
    # List files in the vector store.
    has_more = True
    last_id = None
    while has_more:
        vector_store_file_list = project_client.agents.list_vector_store_files(vector_store.id, after=last_id)
        for one_file in vector_store_file_list.data:
            print(one_file.id)
        has_more = vector_store_file_list.has_more
        last_id = vector_store_file_list.last_id
    # Delete file from vector store
    project_client.agents.delete_vector_store_file(vector_store.id, file.id)
    # Delete vector store.
    deletion_status = project_client.agents.delete_vector_store(vector_store.id)
    print(deletion_status.deleted)
    ```

    **Endpoint-based**

    ```python
    # Create a vector store with no file and wait for it to be processed
    vector_store = project_client.agents.vector_stores.create_and_poll(file_ids=[file.id], name="my_vectorstore")
    # List vector stores
    vector_store_list = project_client.agents.vector_stores.list()
    for one_vector_store in vector_store_list:
        print(one_vector_store.id)
    # List files in the vector store.
    vector_store_file_list = project_client.agents.vector_store_files.list(vector_store.id)
    for one_file in vector_store_file_list:
         print(one_file.id)
    # Delete file from vector store
    project_client.agents.vector_store_files.delete(vector_store.id, file.id)
    # Delete vector store.
    project_client.agents.vector_stores.delete(vector_store.id)
    ```

16. Vector store batch file search.

    **Hub-based**

    ```python
    # Batch upload files
    vector_store_file_batch = project_client.agents.create_vector_store_file_batch_and_poll(
        vector_store_id=vector_store.id, file_ids=[file.id]
    )
    # List file in the batch
    has_more = True
    last_id = None
    while has_more:
        files = project_client.agents.list_vector_store_file_batch_files(vector_store.id, vector_store_file_batch.id, after=last_id)
        for one_file in files.data:
            print(one_file.id)
        has_more = files.has_more
        last_id = files.last_id
    # Try to cancel batch upload
    vector_store_file_batch = project_client.agents.cancel_vector_store_file_batch(vector_store.id, vector_store_file_batch.id)
    ```

    **Endpoint-based**

    ```python
    # Batch upload files
    vector_store_file_batch = project_client.agents.vector_store_file_batches.create_and_poll(
        vector_store_id=vector_store.id, file_ids=[file.id]
    )
    # List file in the batch
    files = project_client.agents.vector_store_file_batches.list_files(vector_store.id, vector_store_file_batch.id)
    for one_file in files:
        print(one_file.id)
    # Try to cancel batch upload
    project_client.agents.vector_store_file_batches.cancel(vector_store.id, vector_store_file_batch.id)
    ```

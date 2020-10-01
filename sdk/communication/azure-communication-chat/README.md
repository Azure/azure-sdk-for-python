[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=master)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=master)

# Azure Communication Chat Package client library for Python

This package contains a Python SDK for Azure Communication Services for Chat.
<!--Read more about Azure Communication Services [here](https://docs.microsoft.com/azure/project-spool/overview)-->

# Getting started

## Prerequisites

- Python 2.7, or 3.5 or later is required to use this package.
<!-- An Azure Communication Resource, learn how to create one from [Create an Azure Communication Resource](https://docs.microsoft.com/azure/project-spool/quickstarts/create-a-communication-resource)-->

## Install the package

Install the Azure Communication Service Chat SDK.

```bash
pip install --pre azure-communication-chat
```

## User Access Tokens

User access tokens enable you to build client applications that directly authenticate to Azure Communication Services. You can generate these tokens with azure.communication.administration module, and then use them to initialize the Communication Services SDKs. Example of using azure.communication.administration:

```bash
pip install --pre azure-communication-administration
```

```python
from azure.communication.administration import CommunicationIdentityClient
identity_client = CommunicationIdentityClient.from_connection_string("<connection string of your Communication service>")
user = identity_client.create_user()
tokenresponse = identity_client.issue_token(user, scopes=["chat"])
token = tokenresponse.token
```

The `user` created above will be used later, because that user should be added as a member of new chat thread when you creating
it with this token. It is because the initiator of the create request must be in the list of the members of the chat thread.

## Create the Chat Client

This will allow you to create, get, list or delete chat threads.

```python
from azure.communication.chat import ChatClient, CommunicationUserCredential
# Your unique Azure Communication service endpoint
endpoint = "https://<RESOURCE_NAME>.communcationservices.azure.com"
token = "<token>"
chat_client = ChatClient(endpoint, CommunicationUserCredential(token))
```

## Create Chat Thread Client

The ChatThreadClient will allow you to perform operations specific to a chat thread, like send message, get message, update
the chat thread topic, add members to chat thread, etc.

You can get it by creating a new chat thread using ChatClient:

```python
chat_thread_client = chat_client.create_chat_thread(topic, thread_members)
```

Alternatively, if you have created a chat thread before and you have its thread_id, you can create it by:

```python
chat_thread_client = chat_client.get_chat_thread_client(thread_id)
```

# Key concepts

A chat conversation is represented by a chat thread. Each user in the thread is called a thread member. Thread members can chat with one another privately in a 1:1 chat or huddle up in a 1:N group chat. Users also get near real-time updates for when others are typing and when they have read the messages.

Once you initialized a `ChatClient` class, you can do the following chat operations:

## Create, get, update, and delete threads

```Python
create_chat_thread(topic, thread_members, **kwargs)
get_chat_thread(thread_id, **kwargs)
list_chat_threads(**kwargs)
delete_chat_thread(thread_id, **kwargs)
```

Once you initialized a `ChatThreadClient` class, you can do the following chat operations:

## Update thread

```python
update_thread(topic, **kwargs)
```

## Send, get, update, and delete messages

```Python
send_message(content, **kwargs)
get_message(message_id, **kwargs)
list_messages(**kwargs)
update_message(message_id, content, **kwargs)
delete_message(message_id, **kwargs)
```

## Get, add, and remove members

```Python
list_members(**kwargs)
add_members(thread_members, **kwargs)
remove_member(member_id, **kwargs)
```

## Send typing notification

```python
send_typing_notification(**kwargs)
```

## Send and get read receipt

Notify the service that a message is read and get list of read messages.

```Python
send_read_receipt(message_id, **kwargs)
list_read_receipts(**kwargs)
```

# Examples

The following sections provide several code snippets covering some of the most common tasks, including:

<!-- - [Thread Operations](#thread-operations)
- [Message Operations](#message-operations)
- [Thread Member Operations](#thread-member-operations)
- [Events Operations](#events-operations) -->

## Thread Operations

### Create a thread

Use the `create_chat_thread` method to create a chat thread client object.

- Use `topic` to give a thread topic;
- Use `thread_members` to list the `ChatThreadMember` to be added to the thread;
- `user`, required, it is the `CommunicationUser` you created by CommunicationIdentityClient.create_user() from User Access Tokens
<!-- [User Access Tokens](#user-access-tokens) -->
- `display_name`, optional, is the display name for the thread member.
- `share_history_time`, optional, time from which the chat history is shared with the member.

`ChatThreadClient` is the result returned from creating a thread, you can use it to perform other chat operations to this chat thread

```Python
from azure.communication.chat import ChatThreadMember
topic = "test topic"
thread_members = [ChatThreadMember(
    user='<user>',
    display_name='name',
    share_history_time=datetime.utcnow()
)]

chat_thread_client = chat_client.create_chat_thread(topic, thread_members)
thread_id = chat_thread_client.thread_id
```

### Get a thread

The `get_chat_thread` method retrieves a thread from the service.
`thread_id` is the unique ID of the thread.

```Python
thread = chat_client.get_chat_thread(thread_id)
```

### List chat threads
The `list_chat_threads` method retrieves the list of created chat threads

- `results_per_page`, optional, The maximum number of messages to be returned per page.
- `start_time`, optional, The start time where the range query.

An iterator of `[ChatThreadInfo]` is the response returned from listing threads

```python
from datetime import datetime, timedelta
chat_client = ChatClient(self.endpoint, self.token)
start_time = datetime.utcnow() - timedelta(days=2)
start_time = start_time.replace(tzinfo=pytz.utc)
chat_thread_infos = chat_client.list_chat_threads(results_per_page=5, start_time=start_time)
```

### Update a thread

Use `update_chat_thread` method to update a thread's properties
`thread_id` is the unique ID of the thread.
`topic` is used to describe the change of the thread topic

- Use `topic` to give thread a new topic;

```python
topic="new topic"
chat_thread_client.update_chat_thread(topic=topic)
```

### Delete a thread

Use `delete_chat_thread` method to delete a thread
`thread_id` is the unique ID of the thread.

```Python
chat_client.delete_chat_thread(thread_id)
```

## Message Operations

### Send a message

Use `send_message` method to sends a message to a thread identified by threadId.

- Use `content` to provide the chat message content, it is required
- Use `priority` to specify the message priority level, such as 'Normal' or 'High', if not speficied, 'Normal' will be set
- Use `sender_display_name` to specify the display name of the sender, if not specified, empty name will be set

`SendChatMessageResult` is the response returned from sending a message, it contains an id, which is the unique ID of the message.

```Python
from azure.communication.chat import ChatMessagePriority

content='hello world'
priority=ChatMessagePriority.NORMAL
sender_display_name='sender name'

send_message_result = chat_thread_client.send_message(content, priority=priority, sender_display_name=sender_display_name)
```

### Get a message

The `get_message` method retrieves a message from the service.
`message_id` is the unique ID of the message.

`ChatMessage` is the response returned from getting a message, it contains an id, which is the unique ID of the message, and other fields please refer to azure.communication.chat.ChatMessage

```python
chat_message = chat_thread_client.get_message(message_id)
```

### Get messages

The `list_messages` method retrieves messages from the service.
- `results_per_page`, optional, The maximum number of messages to be returned per page.
- `start_time`, optional, The start time where the range query.

An iterator of `[ChatMessage]` is the response returned from listing messages

```Python
from datetime import datetime, timedelta
start_time = datetime.utcnow() - timedelta(days=1)
start_time = start_time.replace(tzinfo=pytz.utc)
chat_messages = chat_thread_client.list_messages(results_per_page=1, start_time=start_time)
for chat_message_page in chat_messages.by_page():
    l = list(chat_message_page)
    print("page size: ", len(l))
```

### Update a message

Use `update_message` to update a message identified by threadId and messageId.
`message_id` is the unique ID of the message.
`content` is the message content to be updated.

- Use `content` to provide a new chat message content;

```Python
content = "updated message content"
chat_thread_client.update_message(message_id, content=content)
```

### Delete a message

Use `delete_message` to delete a message.
`message_Id` is the unique ID of the message.

```python
chat_thread_client.delete_message(message_id)
```

## Thread Member Operations

### Get thread members

Use `list_members` to retrieve the members of the thread.

An iterator of `[ChatThreadMember]` is the response returned from listing members

```python
chat_thread_members = chat_thread_client.list_members()
for chat_thread_member in chat_thread_members:
    print(chat_thread_member)
```

### Add thread members

Use `add_members` method to add thread members to the thread.

- Use `thread_members` to list the `ChatThreadMember` to be added to the thread;
- `user`, required, it is the `CommunicationUser` you created by CommunicationIdentityClient.create_user() from User Access Tokens
<!-- [User Access Tokens](#user-access-tokens) -->
- `display_name`, optional, is the display name for the thread member.
- `share_history_time`, optional, time from which the chat history is shared with the member.

```Python
from azure.communication.chat import ChatThreadMember
from datetime import datetime
member = ChatThreadMember(
    user='<user>',
    display_name='name',
    share_history_time=datetime.utcnow())
thread_members = [member]
chat_thread_client.add_members(thread_members)
```

### Remove thread member

Use `remove_member` method to remove thread member from the thread identified by threadId.
`user` is the `CommunicationUser` you created by CommunicationIdentityClient.create_user() from User Access Tokens
<!-- [User Access Tokens](#user-access-tokens)  -->
and was added into this chat thread.

```python
chat_thread_client.remove_member(user)
```

## Events Operations

### Send typing notification

Use `send_typing_notification` method to post a typing notification event to a thread, on behalf of a user.

```Python
chat_thread_client.send_typing_notification()
```

### Send read receipt

Use `send_read_receipt` method to post a read receipt event to a thread, on behalf of a user.

```python
chat_thread_client.send_read_receipt(message_id)
```

### Get read receipts

`list_read_receipts` method retrieves read receipts for a thread.

An iterator of `[ReadReceipt]` is the response returned from listing read receipts

```python
read_receipts = chat_thread_client.list_read_receipts()
for read_receipt in read_receipts:
    print(read_receipt)
    print(read_receipt.sender)
    print(read_receipt.chat_message_id)
    print(read_receipt.read_on)
```

## Sample Code

These are code samples that show common scenario operations with the Azure Communication Chat client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations,
and require Python 3.5 or later.
Before run the sample code, refer to Prerequisites
<!-- [Prerequisites](#Prerequisites) -->
to create a resource, then set some Environment Variables

```bash
set AZURE_COMMUNICATION_SERVICE_ENDPOINT="https://<RESOURCE_NAME>.communcationservices.azure.com"
set AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING="<connection string of your Communication service>"

pip install azure-communication-administration

python samples\chat_client_sample.py
python samples\chat_client_sample_async.py
python samples\chat_thread_client_sample.py
python samples\chat_thread_client_sample_async.py
```

# Troubleshooting

Running into issues? This section should contain details as to what to do there.

# Next steps

More sample code should go here, along with links out to the appropriate example tests.

# Contributing

If you encounter any bugs or have suggestions, please file an issue in the [Issues](<https://github.com/Azure/azure-sdk-for-python/issues>) section of the project.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)

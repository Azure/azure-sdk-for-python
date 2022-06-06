# Azure Communication Chat Package client library for Python

This package contains a Python SDK for Azure Communication Services for Chat.
Read more about Azure Communication Services [here](https://docs.microsoft.com/azure/communication-services/overview)

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/communication/azure-communication-chat) | [Package (Pypi)](https://pypi.org/project/azure-communication-chat/) | [API reference documentation](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-communication-chat/1.0.0b5/index.html) | [Product documentation](https://docs.microsoft.com/azure/communication-services/)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

# Getting started

## Prerequisites

- Python 3.6 or later is required to use this package.
- A deployed Communication Services resource. You can use the [Azure Portal](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp) or the [Azure PowerShell](https://docs.microsoft.com/powershell/module/az.communication/new-azcommunicationservice) to set it up.

## Install the package

Install the Azure Communication Service Chat SDK.

```bash
pip install --pre azure-communication-chat
```

## User Access Tokens

User access tokens enable you to build client applications that directly authenticate to Azure Communication Services. You can generate these tokens with azure.communication.identity module, and then use them to initialize the Communication Services SDKs. Example of using azure.communication.identity:

```bash
pip install azure-communication-identity
```

```python
from azure.communication.identity import CommunicationIdentityClient
identity_client = CommunicationIdentityClient.from_connection_string("<connection string of your Communication service>")
user = identity_client.create_user()
tokenresponse = identity_client.get_token(user, scopes=["chat"])
token = tokenresponse.token
```

The `user` created above will be used later, because that user should be added as a participant of new chat thread when you creating
it with this token. It is because the initiator of the create request must be in the list of the participants of the chat thread.

## Create the Chat Client

This will allow you to create, get, list or delete chat threads.

```python
from azure.communication.chat import ChatClient, CommunicationTokenCredential

# Your unique Azure Communication service endpoint
endpoint = "https://<RESOURCE_NAME>.communcationservices.azure.com"
chat_client = ChatClient(endpoint, CommunicationTokenCredential(token))
```

## Create Chat Thread Client

The ChatThreadClient will allow you to perform operations specific to a chat thread, like send message, get message, update
the chat thread topic, add participants to chat thread, etc.

You can get it by creating a new chat thread using ChatClient:

```python
create_chat_thread_result = chat_client.create_chat_thread(topic)
chat_thread_client = chat_client.get_chat_thread_client(create_chat_thread_result.chat_thread.id)
```

Additionally, the client can also direct so that the request is repeatable; that is, if the client makes the
request multiple times with the same Idempotency-Token and it will get back an appropriate response without
the server executing the request multiple times. The value of the Idempotency-Token is an opaque string
representing a client-generated, globally unique for all time, identifier for the request.

```python
create_chat_thread_result = chat_client.create_chat_thread(
    topic,
    thread_participants=thread_participants,
    idempotency_token=idempotency_token
)
chat_thread_client = chat_client.get_chat_thread_client(create_chat_thread_result.chat_thread.id)
```

Alternatively, if you have created a chat thread before and you have its thread_id, you can create it by:

```python
chat_thread_client = chat_client.get_chat_thread_client(thread_id) # thread_id is the id of an existing chat thread
```

# Key concepts

A chat conversation is represented by a chat thread. Each user in the thread is called a thread participant.
Thread participants can chat with one another privately in a 1:1 chat or huddle up in a 1:N group chat.
Users also get near real-time updates for when others are typing and when they have read the messages.

Once you initialized a `ChatClient` class, you can do the following chat operations:

## Create, get, update, and delete threads

Perform CRD(Create-Read-Delete) operations on threads

```Python
create_chat_thread(topic, **kwargs)
list_chat_threads(**kwargs)
delete_chat_thread(thread_id, **kwargs)
```

Once you initialized a `ChatThreadClient` class, you can do the following chat operations:

## Update thread

Perform Update operation on thread topic

```python
update_topic(topic, **kwargs)
```

## Get Chat thread properties
```python
get_properties(**kwargs)
```

## Send, get, update, and delete messages

Perform CRUD(Create-Read-Update-Delete) operations on messages

```Python
send_message(content, **kwargs)
get_message(message_id, **kwargs)
list_messages(**kwargs)
update_message(message_id, content, **kwargs)
delete_message(message_id, **kwargs)
```

## Get, add, and remove participants

Perform CRD(Create-Read-Delete) operations on thread participants

```Python
list_participants(**kwargs)
add_participants(thread_participants, **kwargs)
remove_participant(participant_identifier, **kwargs)
```

## Send typing notification

Notify the service of typing notification

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

- [Thread Operations](#thread-operations)
- [Message Operations](#message-operations)
- [Thread Participant Operations](#thread-participant-operations)
- [Events Operations](#events-operations)

## Thread Operations

### Create a thread

Use the `create_chat_thread` method to create a chat thread.

- Use `topic`, required, to give a thread topic;
- Use `thread_participants`, optional, to provide a list the `ChatParticipant` to be added to the thread;
    - `user`, required, it is the `CommunicationUserIdentifier` you created by CommunicationIdentityClient.create_user()
      from User Access Tokens
    <!-- [User Access Tokens](#user-access-tokens) -->
    - `display_name`, optional, is the display name for the thread participant.
    - `share_history_time`, optional, time from which the chat history is shared with the participant.
- Use `idempotency_token`, optional, to specify the unique identifier for the request.


`CreateChatThreadResult` is the result returned from creating a thread, you can use it to fetch the `id` of
the chat thread that got created. This `id` can then be used to fetch a `ChatThreadClient` object using
the `get_chat_thread_client` method. `ChatThreadClient` can be used to perform other chat operations to this chat thread.

```Python
# Without idempotency_token and thread_participants
topic = "test topic"
create_chat_thread_result = chat_client.create_chat_thread(topic)
chat_thread_client = chat_client.get_chat_thread_client(create_chat_thread_result.chat_thread.id)
```

```Python
# With idempotency_token and thread_participants
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.chat import ChatParticipant, ChatClient, CommunicationTokenCredential
import uuid
from datetime import datetime

# create an user
identity_client = CommunicationIdentityClient.from_connection_string('<connection_string>')
user = identity_client.create_user()

# user access tokens
tokenresponse = identity_client.get_token(user, scopes=["chat"])
token = tokenresponse.token

## OR pass existing user
# from azure.communication.chat import CommunicationUserIdentifier
# user_id = 'some_user_id'
# user = CommunicationUserIdentifier(user_id)

# create the chat_client
endpoint = "https://<RESOURCE_NAME>.communcationservices.azure.com"
chat_client = ChatClient(endpoint, CommunicationTokenCredential(token))

# modify function to implement customer logic
def get_unique_identifier_for_request(**kwargs):
    res = uuid.uuid4()
    return res

topic = "test topic"
thread_participants = [ChatParticipant(
    identifier=user,
    display_name='name',
    share_history_time=datetime.utcnow()
)]

# obtains idempotency_token using some customer logic
idempotency_token = get_unique_identifier_for_request()

create_chat_thread_result = chat_client.create_chat_thread(
    topic,
    thread_participants=thread_participants,
    idempotency_token=idempotency_token)
thread_id = create_chat_thread_result.chat_thread.id

# fetch ChatThreadClient
chat_thread_client = chat_client.get_chat_thread_client(create_chat_thread_result.chat_thread.id)

# Additionally, you can also check if all participants were successfully added or not
# and subsequently retry adding the failed participants again
def decide_to_retry(error, **kwargs):
    """
    Insert some custom logic to decide if retry is applicable based on error
    """
    return True

retry = [thread_participant for thread_participant, error in create_chat_thread_result.errors if decide_to_retry(error)]
if retry:
    chat_thread_client.add_participants(retry)
```


### Get a thread

Use `get_properties` method retrieves a `ChatThreadProperties` from the service; `thread_id` is the unique ID of the thread.

```Python
chat_thread_properties = chat_thread_client.get_properties()
```

### List chat threads
Use `list_chat_threads` method retrieves the list of created chat threads

- Use `results_per_page`, optional, The maximum number of messages to be returned per page.
- Use `start_time`, optional, The start time where the range query.

An iterator of `[ChatThreadItem]` is the response returned from listing threads

```python
from azure.communication.chat import ChatClient, CommunicationTokenCredential
from datetime import datetime, timedelta

token = "<token>"
endpoint = "https://<RESOURCE_NAME>.communcationservices.azure.com"
chat_client = ChatClient(endpoint, CommunicationTokenCredential(token))
start_time = datetime.utcnow() - timedelta(days=2)

chat_threads = chat_client.list_chat_threads(results_per_page=5, start_time=start_time)
for chat_thread_item_page in chat_threads.by_page():
    for chat_thread_item in chat_thread_item_page:
        print("thread id:", chat_thread_item.id)
```

### Update a thread topic

Use `update_topic` method to update a thread's properties. `topic` is used to describe the change of the thread topic
- Use `topic` to give thread a new topic;

```python
topic = "new topic"
chat_thread_client.update_topic(topic=topic)

chat_thread = chat_thread_client.get_properties(thread_id)

assert chat_thread.topic == topic
```

### Delete a thread

Use `delete_chat_thread` method to delete a thread; `thread_id` is the unique ID of the thread.
- Use `thread_id`, required, to specify the unique ID of the thread.
```Python
chat_client.delete_chat_thread(thread_id=thread_id)
```

## Message Operations

### Send a message

Use `send_message` method to sends a message to a thread identified by `thread_id`.

- Use `content`, required, to provide the chat message content.
- Use `chat_message_type`, optional, to provide the chat message type. Possible values include: `ChatMessageType.TEXT`,
  `ChatMessageType.HTML`, `'text'`, `'html'`; if not specified, `ChatMessageType.TEXT` will be set
- Use `sender_display_name`,optional, to specify the display name of the sender, if not specified, empty name will be set

`SendChatMessageResult` is the response returned from sending a message, it contains an id, which is the unique ID of the message.

```Python
from azure.communication.chat import ChatMessageType

topic = "test topic"
create_chat_thread_result = chat_client.create_chat_thread(topic)
thread_id = create_chat_thread_result.chat_thread.id
chat_thread_client = chat_client.get_chat_thread_client(create_chat_thread_result.chat_thread.id)

content='hello world'
sender_display_name='sender name'
chat_message_type = ChatMessageType.TEXT

# without specifying sender_display_name and chat_message_type
send_message_result = chat_thread_client.send_message(content)
send_message_result_id = send_message_result.id
print("Message sent: id: ", send_message_result_id)

# specifying sender_display_name and chat_message_type
send_message_result_w_type = chat_thread_client.send_message(
            content,
            sender_display_name=sender_display_name,
            chat_message_type=chat_message_type # equivalent to chat_message_type = 'text'
)
send_message_result_w_type_id = send_message_result_w_type.id
print("Message sent: id: ", send_message_result_w_type_id)
```

### Get a message

Use `get_message` method retrieves a message from the service; `message_id` is the unique ID of the message.
- Use `message_id`,required, to specify message id of an existing message
`ChatMessage` is the response returned from getting a message, it contains an id, which is the unique ID of the message, and other fields please refer to azure.communication.chat.ChatMessage

```python
chat_message = chat_thread_client.get_message(message_id=send_message_result_id)
print("get_chat_message succeeded, message id:", chat_message.id, "content: ", chat_message.content)
```

### List messages

Use `list_messages` method retrieves messages from the service.
- Use `results_per_page`, optional, The maximum number of messages to be returned per page.
- Use `start_time`, optional, The start time where the range query.

An iterator of `[ChatMessage]` is the response returned from listing messages

```Python
from datetime import datetime, timedelta

start_time = datetime.utcnow() - timedelta(days=1)

chat_messages = chat_thread_client.list_messages(results_per_page=1, start_time=start_time)
for chat_message_page in chat_messages.by_page():
    for chat_message in chat_message_page:
        print("ChatMessage: Id=", chat_message.id, "; Content=", chat_message.content.message)
```

### Update a message

Use `update_message` to update a message identified by threadId and messageId.
- Use `message_id`,required, is the unique ID of the message.
- Use `content`, optional, is the message content to be updated; if not specified it is assigned to be empty

```Python
content = "updated message content"
chat_thread_client.update_message(send_message_result_id, content=content)

chat_message = chat_thread_client.get_message(message_id=send_message_result_id)

assert chat_message.content.message == content
```

### Delete a message

Use `delete_message` to delete a message.
- Use `message_id`, required, is the unique ID of the message.

```python
chat_thread_client.delete_message(message_id=send_message_result_id)
```

## Thread Participant Operations

### List thread participants

Use `list_participants` to retrieve the participants of the thread.
- Use `results_per_page`, optional, The maximum number of participants to be returned per page.
- Use `skip`, optional, to skips participants up to a specified position in response.

An iterator of `[ChatParticipant]` is the response returned from listing participants

```python
chat_participants = chat_thread_client.list_participants(results_per_page=5, skip=5)
for chat_participant_page in chat_participants.by_page():
    for chat_participant in chat_participant_page:
        print("ChatParticipant: ", chat_participant)
```

### Add thread participants

Use `add_participants` method to add thread participants to the thread.

- Use `thread_participants`, required, to list the `ChatParticipant` to be added to the thread;
  - `user`, required, it is the `CommunicationUserIdentifier` you created by CommunicationIdentityClient.create_user() from User Access Tokens
  <!-- [User Access Tokens](#user-access-tokens) -->
  - `display_name`, optional, is the display name for the thread participant.
  - `share_history_time`, optional, time from which the chat history is shared with the participant.

A `list(tuple(ChatParticipant, ChatError))` is returned. When participant is successfully added,
an empty list is expected. In case of an error encountered while adding participant, the list is populated
with the failed participants along with the error that was encountered.

```Python
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.chat import ChatParticipant
from datetime import datetime

# create 2 users
identity_client = CommunicationIdentityClient.from_connection_string('<connection_string>')
new_users = [identity_client.create_user() for i in range(2)]

# # conversely, you can also add an existing user to a chat thread; provided the user_id is known
# from azure.communication.chat import CommunicationUserIdentifier
#
# user_id = 'some user id'
# user_display_name = "Wilma Flinstone"
# new_user = CommunicationUserIdentifier(user_id)
# participant = ChatParticipant(
#     identifier=new_user,
#     display_name=user_display_name,
#     share_history_time=datetime.utcnow())

participants = []
for _user in new_users:
  chat_participant = ChatParticipant(
    identifier=_user,
    display_name='Fred Flinstone',
    share_history_time=datetime.utcnow()
  )
  participants.append(chat_participant)

response = chat_thread_client.add_participants(thread_participants=participants)

def decide_to_retry(error, **kwargs):
    """
    Insert some custom logic to decide if retry is applicable based on error
    """
    return True

# verify if all users has been successfully added or not
# in case of partial failures, you can retry to add all the failed participants
retry = [p for p, e in response if decide_to_retry(e)]
if retry:
    chat_thread_client.add_participants(retry)
```

### Remove thread participant

Use `remove_participant` method to remove thread participant from the thread identified by threadId.
`identifier` is the `CommunicationUserIdentifier` you created by CommunicationIdentityClient.create_user() from `azure-communication-identity`
<!-- [User Access Tokens](#user-access-tokens)  -->
and was added into this chat thread.
- Use `identifier` to specify the `CommunicationUserIdentifier` you created
```python
chat_thread_client.remove_participant(identifier=new_user)

# # conversely you can also do the following; provided the user_id is known
# from azure.communication.chat import CommunicationUserIdentifier
#
# user_id = 'some user id'
# chat_thread_client.remove_participant(identifier=CommunicationUserIdentifier(new_user))

```

## Events Operations

### Send typing notification

Use `send_typing_notification` method to post a typing notification event to a thread, on behalf of a user.

```Python
chat_thread_client.send_typing_notification()
```

### Send read receipt

Use `send_read_receipt` method to post a read receipt event to a thread, on behalf of a user.
- Use `message_id` to specify the id of the message whose read receipt is to be sent
```python
content='hello world'
send_message_result = chat_thread_client.send_message(content)
send_message_result_id = send_message_result.id
chat_thread_client.send_read_receipt(message_id=send_message_result_id)
```

### List read receipts

Use `list_read_receipts` method retrieves read receipts for a thread.
- Use `results_per_page`, optional, The maximum number of read receipts to be returned per page.
- Use `skip`,optional, to skips read receipts up to a specified position in response.

An iterator of `[ChatMessageReadReceipt]` is the response returned from listing read receipts

```python
read_receipts = chat_thread_client.list_read_receipts(results_per_page=5, skip=5)

for read_receipt_page in read_receipts.by_page():
    for read_receipt in read_receipt_page:
        print(read_receipt)
        print(read_receipt.sender)
        print(read_receipt.chat_message_id)
        print(read_receipt.read_on)
```

## Sample Code

These are code samples that show common scenario operations with the Azure Communication Chat client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations.
Before run the sample code, refer to Prerequisites
<!-- [Prerequisites](#Prerequisites) -->
to create a resource, then set some Environment Variables

```bash
set AZURE_COMMUNICATION_SERVICE_ENDPOINT="https://<RESOURCE_NAME>.communcationservices.azure.com"
set COMMUNICATION_SAMPLES_CONNECTION_STRING="<connection string of your Communication service>"

pip install azure-communication-identity

python samples\chat_client_sample.py
python samples\chat_client_sample_async.py
python samples\chat_thread_client_sample.py
python samples\chat_thread_client_sample_async.py
```

# Troubleshooting

Running into issues? This section should contain details as to what to do there.

# Next steps

More sample code should go [here](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/communication/azure-communication-chat/samples), along with links out to the appropriate example tests.

# Contributing

If you encounter any bugs or have suggestions, please file an issue in the [Issues](<https://github.com/Azure/azure-sdk-for-python/issues>) section of the project.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)

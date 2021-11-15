# Azure Communication CallingServer Package client library for Python

This package contains a Python SDK for Azure Communication Services of CallingServer.
Read more about Azure Communication Services [here](https://docs.microsoft.com/azure/communication-services/overview)


## Getting started

### Prerequisites

- Python 2.7, or 3.6 or later is required to use this package.
- A deployed Communication Services resource. You can use the [Azure Portal](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp) or the [Azure PowerShell](https://docs.microsoft.com/powershell/module/az.communication/new-azcommunicationservice) to set it up.
- You must have a phone number configured that is associated with an Azure subscription

### Install the package

Install the Azure Communication CallingServer client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-communication-callingserver
```

## Key concepts

`CallingServerClient` provides the functionality to create a call connection, join call connection or join a call with CallLocator.
Performing more functionality over the eastablised call.

## Examples

The following section provides several code snippets covering some of the most common Azure Communication Services tasks, including:

Call Connection Client APIs:
- [Client initialization](#client-initialization)
- [Create a call connection](#create-a-call-connection)
- [Add participant](#add-participant)
- [Remove participant](#remove-participant)
- [Play audio in the call connection](#play-audio-in-the-call-connection)
- [Cancel all media operations in the call connection](#cancel-all-media-operations-in-the-call-connection)
- [Hang up the call connection](#hang-up-the-call-connection)

Calling Server Client APIs:
- [Client initialization](#client-initialization)
- [Create a server Call](#create-a-call-connection)
- [Add participant with calllocator to the server call](#add-participant-with-calllocator-to-the-server-call)
- [Remove participant with calllocator from the server call](#remove-participant-with-calllocator-from-the-server-call)
- [Play audio with calllocator in the server call](#play-audio-with-calllocator-in-the-server-call)
- [Hang up the call connection](#hang-up-the-call-connection)

### Client initialization

To initialize the CallingServer Client, the connection string can be used to instantiate. Alternatively, you can also use Azure Active Directory-managed identities authentication using DefaultAzureCredential.

```Python
from azure.communication.callingserver.aio import CallingServerClient

connection_string = "endpoint=ENDPOINT;accessKey=KEY"
callingserver_client = CallingServerClient.from_connection_string(connection_string)
```

```Python
# To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have
# AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.
# see here: https://docs.microsoft.com/en-us/dotnet/api/azure.identity.environmentcredential?view=azure-dotnet
from azure.identity import DefaultAzureCredential

endpoint = "https://<RESOURCE_NAME>.communication.azure.com"
callingserver_client = CallingServerClient(endpoint, DefaultAzureCredential())
```

### Create a call connection
Once the client is initialized, the `createCallConnection` method can be invoked:

```Python
from azure.communication.callingserver import (
    CreateCallOptions,
    CommunicationUserIdentifier,
    PhoneNumberIdentifier
    )

call_connection_async = callingserver_client.create_call_connection(
    source=CommunicationUserIdentifier("<from-phone-number>"),
    targets=[PhoneNumberIdentifier("<to-phone-number>")],
    call_options=CreateCallOptions("<...>"))
```

- `source`: The source identity.
- `targets`: The target identities.
- `call_options`: The create call options.

### Add participant
Once the call is establised, the `add_participant` method can be invoked:

```Python
from azure.communication.callingserver import (
    CommunicationUserIdentifier
    )

add_participant_result = await call_connection_async.add_participant(
    participant=CommunicationUserIdentifier("<id>")
    )
```

- `participant`: The participant to be added to the call.

### Remove participant
Once the participant_id is provided, the `remove_participant` method can be invoked:

```Python
await call_connection_async.remove_participant(
    participant=CommunicationUserIdentifier("<id>")
    )
```

- `participant`: The identifier of participant to be removed from the call.

### Play audio in the call connection
Once the call is establised, the `play_audio` method can be invoked:

```Python
from azure.communication.callingserver import (
    PlayAudioOptions
    )

play_audio_result = await call_connection_async.play_audio(
    audio_url="<audio_url>",
    play_audio_options=PlayAudioOptions"<...>"))
    )
```

- `audio_url`: The uri of the audio file.
- `play_audio_options`: The playAudio options.

### Cancel all media operations in the call connection
Once the call is establised, the `cancel_all_media_operations` method can be invoked:

```Python
cancel_all_media_operations_result = await call_connection_async.cancel_all_media_operations()
```

### Hang up the call connection
Once the call is establised, the `hang_up` method can be invoked:

```Python
await call_connection_async.hang_up()
```

### Create a server Call
The call will be establised after the `join_call` method get invoked:

```Python
from azure.communication.callingserver import (
    CommunicationUserIdentifier,
    JoinCallOptions,
    ServerCallLocator
    )

call_locator = ServerCallLocator("<server-call-id>")
call_connection = await callingserver_client.join_call(
    call_locator=call_locator,
    source=CommunicationUserIdentifier("<id>"),
    join_call_options=JoinCallOptions"<...>"))
    )
```

- `call_locator`: The callLocator contains the call id.
- `source`: The source identity which join the call.
- `join_call_options`: The joinCall options.

### Add participant with calllocator to the server call
Once the call is establised, the `add_participant` method can be invoked:

```Python
from azure.communication.callingserver import (
    CommunicationUserIdentifier,
    ServerCallLocator
    )

call_locator = ServerCallLocator("<server-call-id>")
add_participant_result = await callingserver_client.add_participant(
    call_locator=call_locator,
    participant=CommunicationUserIdentifier("<id>")
    callback_uri="<callback-uri>"
    )
```

- `call_locator`: The callLocator contains the call id.
- `participant`: The participant to be added to the call.
- `callback_uri`: The callback uri.

### Remove participant with callLocator from the server call
Once the participant_id is provided, the `remove_participant` method can be invoked:

```Python
from azure.communication.callingserver import (
    CommunicationUserIdentifier,
    ServerCallLocator
    )

await callingserver_client.remove_participant(
    call_locator=call_locator,
    participant=CommunicationUserIdentifier("<id>")
    )
```

- `call_locator`: The callLocator contains the call id.
- `participant`: The participant to be removed from the call.

### Play audio with callLocator in the server call
Once the call is establised, the `play_audio` method can be invoked:

```Python
from azure.communication.callingserver import (
    PlayAudioOptions,
    ServerCallLocator
    )

call_locator = ServerCallLocator("<server-call-id>")
play_audio_result = await callingserver_client.play_audio(
    call_locator=call_locator,
    audio_url="<audio_url>",
    play_audio_options=PlayAudioOptions"<...>"))
    )
```

- `call_locator`: The callLocator contains the call id.
- `audio_url`: The uri of the audio file.
- `play_audio_options`: The playAudio options.

### Cancel media operations with calllocator in the server call
Once the call is establised, the `cancel_media_operation` method can be invoked:

```Python
from azure.communication.callingserver import (
    ServerCallLocator
    )

call_locator = ServerCallLocator("<server-call-id>")
cancel_all_media_operations_result = await call_connection_async.cancel_media_operation(
    call_locator=call_locator,
    media_operation_id=media_operation_id
)
```

- `call_locator`: The callLocator contains the call id.
- `media_operation_id`: The operationId of the media operation to cancel.


## Troubleshooting

Running into issues? This section should contain details as to what to do there.

## Next steps

More sample code should go under samples folder, along with links out to the appropriate example tests.

## Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the
PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

<!-- LINKS -->
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md

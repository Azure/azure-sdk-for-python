# Azure Communication Rooms client library for Python
This package contains a Python SDK for Azure Communication Services for Rooms.
Read more about Azure Communication Services [here](https://docs.microsoft.com/azure/communication-services/overview)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please
refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Key concepts

The Azure Communication Rooms package is used to do following:
- Create scheduled meetings
- Create meetings with managed permissions for its participants
## Getting started

### Installating the package

```bash
python -m pip install azure-communication-rooms
```

#### Prequisites

- Python 3.7 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- A deployed Communication Services resource. You can use the [Azure Portal](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp) or the [Azure PowerShell](https://docs.microsoft.com/powershell/module/az.communication/new-azcommunicationservice) to set it up.


### Client Initialization

To initialize the Rooms Client, the connection string can be used to instantiate.

```python
from azure.communication.rooms import RoomsClient

client = RoomsClient.from_connection_string(conn_str='<connection_str>' )
```
## Examples

### Key parameters

- `valid_from`: A datetime object from which room will start existing
- `valid_until`: A datetime object after which room meeting would end
- `room_join_policy`: The join policy of the room. Allows only participants or any communication
        service users to join
- `participants`: A list of RoomParticipant containing MRI's of invitees to the room
All the above attributes are optional. The service provides default values of valid_until and
valid_from if they are missing.

### Create Room
```python
from azure.communication.rooms import RoomsClient
from azure.core.exceptions import HttpResponseError
from datetime import datetime, timedelta

client = RoomsClient.from_connection_string(conn_str='<connection_str>')
try:
    response = client.create_room(
        valid_from=datetime.now(),
        valid_until=valid_from + timedelta(weeks=4)
        participants=["first-participant", "second-participant"]
    )
except HttpResponseError as e:
    print('service responds error: {}'.format(e))

```
### Update Room
```python
from azure.communication.rooms import RoomsClient
from azure.core.exceptions import HttpResponseError
from datetime import datetime, timedelta

client = RoomsClient.from_connection_string(conn_str='<connection_str>')
try:
    response = client.update_room(
        room_id="id of the room to be updated",
        valid_from=datetime.now(),
        valid_until=valid_from + timedelta(weeks=4)
    )
except HttpResponseError as e:
    print('service responds error: {}'.format(e))

```

### Delete a Room
```python
from azure.communication.rooms import RoomsClient
from azure.core.exceptions import HttpResponseError

client = RoomsClient.from_connection_string(conn_str='<connection_str>' )
try:
    client.delete_room(
        room_id="id of the room to be deleted")
except HttpResponseError as e:
    print('service responds error: {}'.format(e))

```

### Add participants to Room
```python
from azure.communication.rooms import RoomsClient
from azure.core.exceptions import HttpResponseError

client = RoomsClient.from_connection_string(conn_str='<connection_str>' )
try:
    response = client.add_participants(
        room_id="id of the room to be updated",
        participants=["new-participant-one", "new-participant-two"]
    )
except HttpResponseError as e:
    print('service responds error: {}'.format(e))

```

Please take a look at the [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/communication/azure-communication-rooms/samples) directory for detailed examples of how to use this library to create and manage rooms.

## Troubleshooting

Rooms operations will throw an exception if the request to the server fails. The Rooms client will raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md).


## Next steps
### More sample code

More examples are coming soon...

## Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project

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

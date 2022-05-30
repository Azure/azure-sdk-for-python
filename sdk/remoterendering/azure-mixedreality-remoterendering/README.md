[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=master)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=master)

# Azure Remote Rendering client library for Python

Azure Remote Rendering (ARR) is a service that enables you to render high-quality, interactive 3D content in the cloud and stream it in real time to devices, such as the HoloLens 2.

This SDK offers functionality to convert assets to the format expected by the runtime, and also to manage
the lifetime of remote rendering sessions.

This SDK supports version "2021-01-01" of the [Remote Rendering REST API](https://docs.microsoft.com/rest/api/mixedreality/2021-01-01/remote-rendering).

> NOTE: Once a session is running, a client application will connect to it using one of the "runtime SDKs".
> These SDKs are designed to best support the needs of an interactive application doing 3d rendering.
> They are available in ([.net](https://docs.microsoft.com/dotnet/api/microsoft.azure.remoterendering)
> or ([C++](https://docs.microsoft.com/cpp/api/remote-rendering/)).

[Product documentation](https://docs.microsoft.com/azure/remote-rendering/)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

# Getting started

## Prerequisites

You will need an [Azure subscription](https://azure.microsoft.com/free/dotnet/) and an [Azure Remote Rendering account](https://docs.microsoft.com/azure/remote-rendering/how-tos/create-an-account) to use this package.

In order to follow this tutorial it is highly recommended that you [link your storage account with your ARR account](https://docs.microsoft.com/azure/remote-rendering/how-tos/create-an-account#link-storage-accounts).

## Install the package

Install the Azure Remote Rendering client library for Python with [pip][pip]:

```bash
pip install --pre azure-mixedreality-remoterendering
```

## Create and authenticate the client

Constructing a remote rendering client requires an authenticated account, and a remote rendering endpoint.
For an account created in the eastus region, the account domain will have the form "eastus.mixedreality.azure.com".
There are several different forms of authentication:

- Account Key authentication
  - Account keys enable you to get started quickly with using Azure Remote Rendering. But before you deploy your application to production, we recommend that you update your app to use Azure AD authentication.
- Azure Active Directory (AD) token authentication
  - If you're building an enterprise application and your company is using Azure AD as its identity system, you can use user-based Azure AD authentication in your app. You then grant access to your Azure Remote Rendering accounts by using your existing Azure AD security groups. You can also grant access directly to users in your organization.
  - Otherwise, we recommend that you obtain Azure AD tokens from a web service that supports your app. We recommend this method for production applications because it allows you to avoid embedding the credentials for access in your client application.

See [here](https://docs.microsoft.com/azure/remote-rendering/how-tos/authentication) for detailed instructions and information.

In all the following examples, the client is constructed with a `endpoint` parameter.
The available endpoints correspond to regions, and the choice of endpoint determines the region in which the service performs its work.
An example is `https://remoterendering.eastus2.mixedreality.azure.com`.

A full list of endpoints in supported regions can be found in the [Azure Remote Rendering region list](https://docs.microsoft.com/azure/remote-rendering/reference/regions).

> NOTE: For converting assets, it is preferable to pick a region close to the storage containing the assets.

> NOTE: For rendering, it is strongly recommended that you pick the closest region to the devices using the service.
> The time taken to communicate with the server impacts the quality of the experience.

### Authenticating with account key authentication

Use the `AzureKeyCredential` object to use an account identifier and account key to authenticate:

```python
from azure.core.credentials import AzureKeyCredential
from azure.mixedreality.remoterendering import RemoteRenderingClient

account_id = "<ACCOUNTD ID>"
account_domain = "<ACCOUNT_DOMAIN>"
account_key = "<ACCOUNT_KEY>"
arr_endpoint = "<ARR_ENDPOINT>"

key_credential = AzureKeyCredential(account_key)
client = RemoteRenderingClient(
    endpoint=arr_endpoint,
    account_id=account_id,
    account_domain=account_domain,
    credential=key_credential
)
```

### Authenticating with a static access token

You can pass a Mixed Reality access token as an `AccessToken` previously retrieved from the
[Mixed Reality STS service](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/mixedreality/azure-mixedreality-authentication)
to be used with a Mixed Reality client library:

```python
from azure.mixedreality.authentication import MixedRealityStsClient
from azure.mixedreality.remoterendering import RemoteRenderingClient
account_id = "<ACCOUNTD ID>"
account_domain = "<ACCOUNT_DOMAIN>"
account_key = "<ACCOUNT_KEY>"

key_credential = AzureKeyCredential(account_key)

client = MixedRealityStsClient(account_id, account_domain, key_credential)

token = client.get_token()

client = RemoteRenderingClient(
    endpoint=arr_endpoint,
    account_id=account_id,
    account_domain=account_domain,
    credential=token,
)
```

### Authenticating with an Azure Active Directory Credential

Account key authentication is used in most of the examples, but you can also authenticate with Azure Active Directory
using the [Azure Identity library][azure_identity]. This is the recommended method for production applications. To use
the [DefaultAzureCredential][defaultazurecredential] provider shown below, or other credential providers provided with
the Azure SDK, please install the `@azure/identity` package:

You will also need to [register a new AAD application][register_aad_app] and grant access to your Mixed Reality resource
by assigning the appropriate role for your Mixed Reality service to your service principal.

```python
from azure.identity import DefaultAzureCredential
from azure.mixedreality.remoterendering import RemoteRenderingClient

account_id = "<ACCOUNTD ID>"
account_domain = "<ACCOUNT_DOMAIN>"
default_credential = DefaultAzureCredential()

client = RemoteRenderingClient(
    endpoint=arr_endpoint,
    account_id=account_id,
    account_domain=account_domain,
    credential=default_credential
)
```

## Key concepts

### RemoteRenderingClient

The `RemoteRenderingClient` is the client library used to access the RemoteRenderingService.
It provides methods to create and manage asset conversions and rendering sessions.

### Long-Running Operations
Long-running operations are operations which consist of an initial request sent to the service to start an operation,
followed by polling the service at intervals to determine whether the operation has completed or failed, and if it has
succeeded, to get the result.

Methods that convert assets, or spin up rendering sessions are modelled as long-running operations.
The client exposes a `begin_<method-name>` method that returns an LROPoller or AsyncLROPoller.
Callers should wait for the operation to complete by calling result() on the poller object returned from the
`begin_<method-name>` method. Sample code snippets are provided to illustrate using long-running operations
[below](#examples "Examples").

## Examples

- [Convert an asset](#convert-an-asset)
- [List conversions](#list-conversions)
- [Create a session](#create-a-session)
- [Extend the lease time of a session](#extend-the-lease-time-of-a-session)
- [List sessions](#list-sessions)
- [Stop a session](#stop-a-session)

### Convert an asset

We assume that a RemoteRenderingClient has been constructed as described in the [Authenticate the Client](#authenticate-the-client) section.
The following snippet describes how to request that "box.fbx", found at at a path of "/input/box/box.fbx" of the blob container at the given storage container URI, gets converted.

Converting an asset can take anywhere from seconds to hours.
This code uses an existing conversion poller and polls regularly until the conversion has finished or failed.
The default polling period is 5 seconds.
Note that a conversion poller can be retrieved using the client.get_asset_conversion_poller using the id of an existing conversion and a client.

Once the conversion process finishes the output is written to the specified output container under a path of "/output/<conversion_id>/box.arrAsset".
The path can be retrieved from the output.asset_uri of a successful conversion.

```python
    conversion_id = str(uuid.uuid4()) # A randomly generated uuid is a good choice for a conversion_id.

    input_settings = AssetConversionInputSettings(
        storage_container_uri="<STORAGE CONTAINER URI>",
        relative_input_asset_path="box.fbx",
        blob_prefix="input/box"
    )
    output_settings = AssetConversionOutputSettings(
        storage_container_uri="<STORAGE CONTAINER URI>",
        blob_prefix="output/"+conversion_id,
        output_asset_filename="convertedBox.arrAsset" #if no output_asset_filename <input asset filename>.arrAsset will be the name of the resulting converted asset
    )
    try:
        conversion_poller = client.begin_asset_conversion(
            conversion_id=conversion_id,
            input_settings=input_settings,
            output_settings=output_settings
        )

        print("Conversion with id:", conversion_id, "created. Waiting for completion.")
        conversion = conversion_poller.result()
        print("conversion output:", conversion.output.asset_uri)

    except Exception as e:
        print("Conversion failed", e)
```

### List conversions

You can get information about your conversions using the `list_asset_conversions` method.
This method may return conversions which have yet to start, conversions which are running and conversions which have finished.
In this example, we list all conversions and print id and creation ad as well as the output asset URIs of successful conversions.

```python
    print("conversions:")
    for c in client.list_asset_conversions():
        print(
            "\t conversion:  id:",
            c.id,
            "status:",
            c.status,
            "created on:",
            c.created_on.strftime("%m/%d/%Y, %H:%M:%S"),
        )
        if c.status == AssetConversionStatus.SUCCEEDED:
            print("\t\tconversion result URI:", c.output.asset_uri)
```

### Create a session

We assume that a RemoteRenderingClient has been constructed as described in the [Authenticate the Client](#authenticate-the-client) section.
The following snippet describes how to request that a new rendering session be started.

```python
    print("starting rendering session with id:", session_id)
    try:
        session_poller = client.begin_rendering_session(
            session_id=session_id, size=RenderingSessionSize.STANDARD, lease_time_minutes=20
        )
        print(
            "rendering session with id:",
            session_id,
            "created. Waiting for session to be ready.",
        )
        session = session_poller.result()
        print(
            "session with id:",
            session.id,
            "is ready. lease_time_minutes:",
            session.lease_time_minutes,
        )
    except Exception as e:
        print("Session startup failed", e)
```

### Extend the lease time of a session

If a session is approaching its maximum lease time, but you want to keep it alive, you will need to make a call to 
increase its maximum lease time.
This example shows how to query the current properties and then extend the lease if it will expire soon.

> NOTE: The runtime SDKs also offer this functionality, and in many typical scenarios, you would use them to
> extend the session lease.

```python
    session = client.get_rendering_session(session_id)
    if session.lease_time_minutes - session.elapsed_time_minutes < 2:
        session = client.update_rendering_session(
            session_id=session_id, lease_time_minutes=session.lease_time_minutes + 10
        )
```

### List sessions

You can get information about your sessions using the `list_rendering_sessions` method of the client.
This method may return sessions which have yet to start and sessions which are ready.

```python
    print("sessions:")
    rendering_sessions = client.list_rendering_sessions()
    for session in rendering_sessions:
        print(
            "\t session:  id:",
            session.id,
            "status:",
            session.status,
            "created on:",
            session.created_on.strftime("%m/%d/%Y, %H:%M:%S"),
        )
```

### Stop a Session

The following code will stop a running session with given id. Since running sessions incur ongoing costs it is
recommended to stop sessions which are not needed anymore.

```python
    client.stop_rendering_session(session_id)
    print("session with id:", session_id, "stopped")
```

## Troubleshooting

For general troubleshooting advice concerning Azure Remote Rendering, see [the Troubleshoot page](https://docs.microsoft.com/azure/remote-rendering/resources/troubleshoot) for remote rendering at docs.microsoft.com.

The client methods and waiting for poller results will throw exceptions if the request failed.

If the asset in a conversion is invalid, the conversion poller will throw an exception with an error containing details.
Once the conversion service is able to process the file, a &lt;assetName&gt;.result.json file will be written to the output container.
If the input asset is invalid, then that file will contain a more detailed description of the problem.

Similarly, sometimes when a session is requested, the session ends up in an error state.
The poller will throw an exception containing details of the error in this case. Session errors are usually transient
and requesting a new session should succeed.

### Logging

This library uses the standard
[logging][python_logging] library for logging.

Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted**
headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

See full SDK logging documentation with examples [here][sdk_logging_docs].

### Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][azure_core_ref_docs]
describes available configurations for retries, logging, transport protocols, and more.

### Exceptions

The Remote Rendering client library will raise exceptions defined in [Azure Core][azure_core_exceptions].

### Async APIs

This library also includes a complete async API supported on Python 3.5+. To use it, you must
first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/). Async clients
are found under the `azure.mixedreality.remoterendering.aio` namespace.



## Next steps

- Read the [Product documentation](https://docs.microsoft.com/azure/remote-rendering/)
- Learn about the runtime SDKs:
  - .NET: https://docs.microsoft.com/dotnet/api/microsoft.azure.remoterendering
  - C++: https://docs.microsoft.com/cpp/api/remote-rendering/

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

If you'd like to contribute to this library, please read the
[contributing guide](https://github.com/Azure/azure-sdk-for-python/blob/master/CONTRIBUTING.md) to learn more about how
to build and test the code.

<!-- LINKS -->
![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%remoterendering%2Fazure-mixedreality-remoterendering%2FREADME.png)

[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[azure_sub]: https://azure.microsoft.com/free/
[azure_portal]: https://portal.azure.com
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity

[pip]: https://pypi.org/project/pip/
[sdk_logging_docs]: https://docs.microsoft.com/azure/developer/python/azure-sdk-logging
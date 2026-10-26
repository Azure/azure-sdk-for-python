# Azure Communication Call Automation client library for Python

This package contains a Python SDK for Azure Communication Call Automation. Call Automation provides developers the ability to build server-based, intelligent call workflows, and call recording for voice and PSTN channels.

[Overview of Call Automation][overview] | [Product documentation][product_docs]

## _Disclaimer_
_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please
refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Security notice: version 1.6.0 deprecated

Version **1.6.0** of `azure-communication-callautomation` is deprecated as of
**2026-10-22** because of a recording URL validation security issue. This notice
applies to version 1.6.0, not to the library as a whole.

In applications that pass attacker-influenced recording URLs to the synchronous
`download_recording` or `delete_recording` methods using the default Requests
transport, an ambiguous URL can bypass hostname validation and send an
authenticated request to an unintended endpoint, potentially exposing a Bearer
token.

Upgrade to **1.6.1** or a later fixed release to receive the security fix.
Use only service-generated recording URLs received through trusted,
integrity-protected events; do not pass untrusted recording URLs to these methods.

Refer to the [release history](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-callautomation/CHANGELOG.md) and
[Azure SDK support policy](https://azure.github.io/azure-sdk/policies_support.html)
for more information.

## Getting started
### Prerequisites
- Python 3.8 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- A deployed Communication Services resource. You can use the [Azure Portal][azure_portal] or the [Azure PowerShell][azure_powershell] to set it up.

### Installing
Install the Azure Communication Service Call Automation SDK.

```bash
pip install azure-communication-callautomation
```

## Key concepts
| Name                 | Description                                                                                                                                                                                                                                                                                                                              |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CallAutomationClient | `CallAutomationClient` is the primary interface for developers using this client library. It can be used to initiate calls by `createCall` or `answerCall`. It can also be used to do recording actions such as `startRecording`                                                                                                         |                                                                      |
| CallConnectionClient | `CallConnectionClient` represents a ongoing call. Once the call is established with `createCall` or `answerCall`, further actions can be performed for the call, such as `transfer` or `play_media`.                                                                                                                                     |                                                                                                                                                               |
| Callback Events      | Callback events are events sent back during duration of the call. It gives information and state of the call, such as `CallConnected`. `CallbackUrl` must be provided during `createCall` and `answerCall`, and callback events will be sent to this url. |
| Incoming Call Event  | When incoming call happens (that can be answered with `answerCall`), incoming call eventgrid event will be sent. This is different from Callback events above, and should be setup on Azure portal. See [Incoming Call][incomingcall] for detail.                                                                                        |

### Recording URL security

`download_recording` and `delete_recording` accept only HTTPS URLs with ASCII DNS
hostnames under `*.asm.skype.com`, `*.asyncgw.teams.microsoft.com`, or
`*.ams.gov.teams.microsoft.us`. URLs containing user information, raw backslashes,
whitespace, control characters, or malformed authorities are rejected with
`ValueError` before authentication. Redirect destinations are subject to the same
validation. Valid signed query parameters are preserved.

Use service-generated recording URLs from trusted, integrity-protected events.

## Examples
### Initialize CallAutomationClient
```Python
from azure.identity import DefaultAzureCredential
from azure.communication.callautomation import (CallAutomationClient)

# Your unique Azure Communication service endpoint
endpoint_url = '<ENDPOINT>'
credential = DefaultAzureCredential()
client = CallAutomationClient(endpoint_url, credential)
```

### Create Call
```Python
from azure.communication.callautomation import (
    CallAutomationClient,
    CommunicationUserIdentifier
)

# target endpoint for ACS User
user = CommunicationUserIdentifier("8:acs:...")

# callback url to receive callback events
callback_url = "https://<MY-EVENT-HANDLER-URL>/events"

# send out the invitation, creating call
result = client.create_call(
    target_participant=user,
    callback_url=callback_url
)

# this id can be used to do further actions in the call
call_connection_id = result.call_connection_id
```

### Play Media
```Python
# using call connection id, get call connection
call_connection = client.get_call_connection(call_connection_id)

# from callconnection of result above, play media to all participants
my_file = FileSource(url="https://<FILE-SOURCE>/<SOME-FILE>.wav")
call_connection.play_to_all(my_file)
```

## Troubleshooting
## Next steps
- [Call Automation Overview][overview]
- [Incoming Call Concept][incomingcall]
- [Build a customer interaction workflow using Call Automation][build1]
- [Redirect inbound telephony calls with Call Automation][build2]
- [Quickstart: Play action][build3]
- [Quickstart: Recognize action][build4]
- [Read more about Call Recording in Azure Communication Services][recording1]
- [Record and download calls with Event Grid][recording2]

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
[overview]: https://learn.microsoft.com/azure/communication-services/concepts/voice-video-calling/call-automation
[product_docs]: https://learn.microsoft.com/azure/communication-services/overview
[azure_cli]: https://learn.microsoft.com/cli/azure
[azure_sub]: https://azure.microsoft.com/free/
[azure_portal]: https://portal.azure.com
[azure_powershell]: https://learn.microsoft.com/powershell/module/az.communication/new-azcommunicationservice
[build_doc]: https://aka.ms/AzureSDKBundling
[incomingcall]: https://learn.microsoft.com/azure/communication-services/concepts/voice-video-calling/incoming-call-notification
[build1]: https://learn.microsoft.com/azure/communication-services/quickstarts/voice-video-calling/callflows-for-customer-interactions?pivots=programming-language-csha
[build2]: https://learn.microsoft.com/azure/communication-services/how-tos/call-automation-sdk/redirect-inbound-telephony-calls?pivots=programming-language-csharp
[build3]: https://learn.microsoft.com/azure/communication-services/quickstarts/voice-video-calling/play-action?pivots=programming-language-csharp
[build4]: https://learn.microsoft.com/azure/communication-services/quickstarts/voice-video-calling/recognize-action?pivots=programming-language-csharp
[recording1]: https://learn.microsoft.com/azure/communication-services/concepts/voice-video-calling/call-recording
[recording2]: https://learn.microsoft.com/azure/communication-services/quickstarts/voice-video-calling/get-started-call-recording?pivots=programming-language-csharp

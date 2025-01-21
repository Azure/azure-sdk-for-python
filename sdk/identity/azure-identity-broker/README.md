# Azure Identity Broker plugin for Python

This package extends the [Azure Identity][azure_identity] library by providing supplemental credentials for authenticating via an authentication broker. An authentication broker is an application that runs on a user's machine that manages the authentication handshakes and token maintenance for connected accounts. The table below outlines supported brokers and the minimum package version required to use each of them.

| Broker                                    | Minimum package version |
|-------------------------------------------|-------------------------|
| [Company Portal][company_portal] on macOS | 1.3.0b1                 |
| Web Account Manager (WAM) on Windows 10+  | 1.0.0                   |

[Source code][source_code] | [Package (PyPI)][azure_identity_broker] | [API reference documentation][ref_docs] | [Microsoft Entra ID documentation][entra_id]

## Getting started

### Install the package

Install the Azure Identity Broker plugin for Python with [pip][pip]:

```bash
pip install azure-identity-broker
```

## Key concepts

This package enables broker support via `InteractiveBrowserBrokerCredential`, which is a subclass of the Azure Identity library's [InteractiveBrowserCredential][ibc].

### Parent window handle

When authenticating interactively via `InteractiveBrowserBrokerCredential`, a parent window handle is required to ensure that the authentication dialog is shown correctly over the requesting window. In the context of graphical user interfaces on devices, a window handle is a unique identifier that the operating system assigns to each window. For the Windows operating system, this handle is an integer value that serves as a reference to a specific window. On macOS, it is an integer-based identifier that represents and identifies a specific window instance.

## Microsoft account (MSA) passthrough

Microsoft accounts (MSA) are personal accounts created by users to access Microsoft services. MSA passthrough is a legacy configuration which enables users to get tokens to resources which normally don't accept MSA logins. This feature is only available to first-party applications. Users authenticating with an application that is configured to use MSA passthrough can set `enable_msa_passthrough` to `True` inside `InteractiveBrowserBrokerCredential` to allow these personal accounts to be listed by broker.

## Redirect URIs

Microsoft Entra applications rely on redirect URIs to determine where to send the authentication response after a user has logged in. To enable brokered authentication, [add a redirect URI](https://learn.microsoft.com/entra/identity-platform/quickstart-register-app#add-a-redirect-uri) to the application for the platform on which it's expected to run.

| Platform    | Redirect URI                                                                                                          |
|-------------|-----------------------------------------------------------------------------------------------------------------------|
| macOS       | `msauth.com.msauth.unsignedapp://auth` for unsigned applications<br>`msauth.BUNDLE_ID://auth` for signed applications |
| Windows 10+ | `ms-appx-web://Microsoft.AAD.BrokerPlugin/your_client_id`                                                             |

## Examples

### Authenticate with `InteractiveBrowserBrokerCredential`

This example demonstrates using `InteractiveBrowserBrokerCredential` as a broker-enabled credential for authenticating with the `BlobServiceClient` from the [azure-storage-blob][azure_storage_blob] library. Here, the `win32gui` module from the `pywin32` package is used to get the current window.

```python
# On Windows
import win32gui
from azure.identity.broker import InteractiveBrowserBrokerCredential
from azure.storage.blob import BlobServiceClient

# Get the handle of the current window
current_window_handle = win32gui.GetForegroundWindow()

credential = InteractiveBrowserBrokerCredential(parent_window_handle=current_window_handle)
client = BlobServiceClient(account_url, credential=credential)

# On macOS
import msal
from azure.identity.broker import InteractiveBrowserBrokerCredential
from azure.storage.blob import BlobServiceClient

credential = InteractiveBrowserBrokerCredential(
    parent_window_handle=msal.PublicClientApplication.CONSOLE_WINDOW_HANDLE
)
client = BlobServiceClient(account_url, credential=credential)
```

To bypass the account selection dialog and use the default broker account, set the `use_default_broker_account` argument to `True`. The credential will attempt to silently use the default broker account. If using the default account fails, the credential will fall back to interactive authentication.

```python
credential = InteractiveBrowserBrokerCredential(
    parent_window_handle=current_window_handle,
    use_default_broker_account=True
)
```

## Troubleshooting

See the Azure Identity [troubleshooting guide][troubleshooting_guide] for details on how to diagnose various failure scenarios.

## Next steps

### Client library support

Client and management libraries listed on the [Azure SDK release page](https://azure.github.io/azure-sdk/releases/latest/python.html) that support Microsoft Entra authentication accept credentials from this library. You can learn more about using these libraries in their documentation, which is linked from the release page.

### Known issues

This library doesn't support [Azure AD B2C][b2c].

For other open issues, refer to the library's [GitHub repository](https://github.com/Azure/azure-sdk-for-python/issues?q=is%3Aopen+is%3Aissue+label%3AAzure.Identity).

### Provide feedback

If you encounter bugs or have suggestions, [open an issue](https://github.com/Azure/azure-sdk-for-python/issues).

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

<!-- LINKS -->
[azure_identity]: https://pypi.org/project/azure-identity
[azure_identity_broker]: https://pypi.org/project/azure-identity-broker
[azure_storage_blob]: https://pypi.org/project/azure-storage-blob
[b2c]: https://learn.microsoft.com/azure/active-directory-b2c/overview
[company_portal]: https://learn.microsoft.com/mem/intune/apps/apps-company-portal-macos
[entra_id]: https://learn.microsoft.com/entra/identity/
[ibc]: https://learn.microsoft.com/python/api/azure-identity/azure.identity.interactivebrowsercredential?view=azure-python
[pip]: https://pypi.org/project/pip
[ref_docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-identity-broker/latest/index.html
[source_code]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity-broker
[troubleshooting_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/TROUBLESHOOTING.md

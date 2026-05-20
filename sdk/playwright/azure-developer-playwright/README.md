# Azure Developer Playwright client library for Python

Azure Developer Playwright is a service that enables you to run Playwright tests at scale in the cloud. This client library allows you to manage access tokens, test runs, browser sessions, and remote browsers for your Playwright Testing workspace.

## Getting started

### Install the package

```bash
python -m pip install azure-developer-playwright
```

### Prerequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure Developer Playwright workspace.

### Authenticate the client

To use this library, you need a [TokenCredential][azure_identity_credentials] implementation, such as [DefaultAzureCredential][default_azure_credential].

```bash
pip install azure-identity
```

```python
from azure.identity import DefaultAzureCredential
from azure.developer.playwright import PlaywrightClient

client = PlaywrightClient(
    endpoint="https://<region>.api.playwright.microsoft.com",
    credential=DefaultAzureCredential(),
)
```

## Key concepts

- **Workspace**: An Azure Playwright Testing workspace that hosts your testing resources.
- **Access Token**: A token used to authenticate Playwright browsers with the service.
- **Test Run**: Represents a collection of test results reported to the service.
- **Browser Session**: A remote browser session used during test execution.

## Examples

### List test runs

```python
from azure.identity import DefaultAzureCredential
from azure.developer.playwright import PlaywrightClient

client = PlaywrightClient(
    endpoint="https://<region>.api.playwright.microsoft.com",
    credential=DefaultAzureCredential(),
)

for run in client.test_runs.list(workspace_id="<workspace-id>"):
    print(run)
```

## Troubleshooting

For help troubleshooting common issues, see [Troubleshoot test run failures][troubleshoot_guide].

## Next steps

For more information about the Azure Developer Playwright service, see the [Azure Playwright Testing documentation][product_documentation].


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
[python_logging]: https://docs.python.org/3/library/logging.html
[product_documentation]: https://learn.microsoft.com/azure/playwright-testing/
[troubleshoot_guide]: https://learn.microsoft.com/azure/playwright-testing/troubleshoot-test-run-failures

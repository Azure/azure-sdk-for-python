# Azure Playwrightworkspaces client library for Python
<!-- write necessary description of service -->

## Getting started

### Install the package

```bash
python -m pip install azure-playwrightworkspaces
```

#### Prequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure Playwrightworkspaces instance.

### Authenticate the client

The `PlaywrightClient` uses [Azure Active Directory token authentication][azure_identity_credentials].
You can supply any credential from the [`azure-identity`][azure_identity_pip] package, such as
[`DefaultAzureCredential`][default_azure_credential].

```python
from azure.identity import DefaultAzureCredential
from azure.playwrightworkspaces import PlaywrightClient

client = PlaywrightClient(
    endpoint="https://<region>.api.playwright.microsoft.com",
    credential=DefaultAzureCredential(),
)
```

## Key concepts

- **PlaywrightClient** – the entry point for the service. Exposes operation groups for
  workspaces, access tokens, test runs, and browser sessions.
- **Workspaces** – represent a Playwright Workspaces resource and expose metadata such as
  the available cloud-hosted browsers.
- **Access tokens** – authentication tokens scoped to a workspace that allow Playwright
  test runners to authenticate against the service.
- **Test runs** – records of Playwright test executions reported to the workspace.
- **Browser sessions** – cloud-hosted browser sessions used during a test run.

An asynchronous client with the same surface is available under
`azure.playwrightworkspaces.aio`.

## Examples

### Create an access token

```python
import uuid
from datetime import datetime, timedelta, timezone

from azure.identity import DefaultAzureCredential
from azure.playwrightworkspaces import PlaywrightClient

client = PlaywrightClient(
    endpoint="https://<region>.api.playwright.microsoft.com",
    credential=DefaultAzureCredential(),
)

token = client.access_tokens.create_or_replace(
    workspace_id="<workspace-id>",
    access_token_id=str(uuid.uuid4()),
    resource={
        "name": "my-token",
        "expiryAt": (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    },
)
print(token["id"])
```

### List test runs (async)

```python
import asyncio

from azure.identity.aio import DefaultAzureCredential
from azure.playwrightworkspaces.aio import PlaywrightClient


async def list_runs():
    async with PlaywrightClient(
        endpoint="https://<region>.api.playwright.microsoft.com",
        credential=DefaultAzureCredential(),
    ) as client:
        async for run in client.test_runs.list(workspace_id="<workspace-id>"):
            print(run["runId"], run.get("displayName"))


asyncio.run(list_runs())
```

## Troubleshooting

- **Authentication errors (`401`/`403`)** – verify that the credential you pass has access
  to the target workspace and that the `endpoint` points at the correct region.
- **Wrong endpoint** – workspace, access-token, and test-run/browser-session APIs are
  served from related but distinct subdomains. Pass the base
  `https://<region>.api.playwright.microsoft.com` endpoint; the client routes
  test-run and browser-session calls to the reporting subdomain automatically.
- **Logging** – this library uses the standard Python [`logging`][python_logging] library.
  Set the root logger to `DEBUG` to capture detailed HTTP request/response logs.

## Next steps

- Browse the [Azure Playwright Workspaces documentation][playwright_workspaces_docs] for
  conceptual material and quickstarts.
- File issues or feature requests in the
  [Azure SDK for Python repository][azure_sdk_for_python_issues].

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
[playwright_workspaces_docs]: https://learn.microsoft.com/azure/playwright-testing/
[azure_sdk_for_python_issues]: https://github.com/Azure/azure-sdk-for-python/issues

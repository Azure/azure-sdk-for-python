
# Azure Management Core Library

Azure management core library defines extensions to Azure Core that are specific to ARM (Azure Resource Management) needed when you use client libraries.

As an end user, you don't need to manually install azure-mgmt-core because it will be installed automatically when you install other SDKs.

[Source code](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-mgmt-core/) | [Package (Pypi)][package] | [API reference documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-mgmt-core/)

## Experimental ARM external evaluation

This design-review prototype adds **opt-in** external-evaluation policies. Nothing
is enabled by default, and existing generated clients do not need regeneration.
The proposed API is not finalized; see
[Azure/azure-sdk#10081](https://github.com/Azure/azure-sdk/issues/10081).
Use both the `azure-core` and `azure-mgmt-core` sources from this prototype:
the accompanying core fix keeps per-operation logging overrides effective across
retries. A released minimum-core dependency must be selected before shipping.

When a subscription-level ARM write returns `403 RequestDisallowedByPolicy`
with a missing-policy-token hint, the policy invokes your provider and replays
the operation once with the returned token. The provider uses a separate Policy
client, without the external-evaluation policy, to avoid recursion.

Install `azure-mgmt-storage`, `azure-identity`, and a version
of `azure-mgmt-resource-policy` that exposes `policy_tokens.acquire`. The example
uses a Storage client for the guarded operation and a separate Policy client for
token acquisition. Other ARM clients supporting `per_call_policies` can be
configured the same way. Set `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, and
`AZURE_STORAGE_ACCOUNT_NAME` to identify an existing storage account.

### Synchronous SDK user

```python
import os

from azure.identity import DefaultAzureCredential
from azure.mgmt.core.policies import ExternalEvaluationPolicy, create_policy_token_provider
from azure.mgmt.resource.policy import PolicyClient
from azure.mgmt.storage import StorageManagementClient

subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
resource_group_name = os.environ["AZURE_RESOURCE_GROUP"]
storage_account_name = os.environ["AZURE_STORAGE_ACCOUNT_NAME"]

with DefaultAzureCredential() as credential:
    # The provider client uses the same credential and ARM cloud/endpoint as the
    # guarded client. Do not add ExternalEvaluationPolicy to this client.
    with PolicyClient(credential, subscription_id, api_version="2025-11-01") as token_client:
        provider = create_policy_token_provider(
            token_client.policy_tokens.acquire, subscription_id=subscription_id
        )

        with StorageManagementClient(
            credential,
            subscription_id,
            per_call_policies=[ExternalEvaluationPolicy(provider)],
        ) as storage_client:
            # Call ordinary SDK operations. If this scope has an external-
            # evaluation policy, acquisition and replay happen in the pipeline.
            account = storage_client.storage_accounts.get_properties(
                resource_group_name, storage_account_name
            )
            tags = {**(account.tags or {}), "external-evaluation-example": "enabled"}
            updated_account = storage_client.storage_accounts.update(
                resource_group_name, storage_account_name, {"tags": tags}
            )
            print(updated_account.name)
```

### Asynchronous SDK user

```python
import os

from azure.identity.aio import DefaultAzureCredential
from azure.mgmt.core.policies import AsyncExternalEvaluationPolicy, create_async_policy_token_provider
from azure.mgmt.resource.policy.aio import PolicyClient
from azure.mgmt.storage.aio import StorageManagementClient

async def update_storage_account_tags():
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    resource_group_name = os.environ["AZURE_RESOURCE_GROUP"]
    storage_account_name = os.environ["AZURE_STORAGE_ACCOUNT_NAME"]
    async with DefaultAzureCredential() as credential:
        async with PolicyClient(credential, subscription_id, api_version="2025-11-01") as token_client:
            provider = create_async_policy_token_provider(
                token_client.policy_tokens.acquire, subscription_id=subscription_id
            )

            async with StorageManagementClient(
                credential,
                subscription_id,
                per_call_policies=[AsyncExternalEvaluationPolicy(provider)],
            ) as storage_client:
                account = await storage_client.storage_accounts.get_properties(
                    resource_group_name, storage_account_name
                )
                tags = {**(account.tags or {}), "external-evaluation-example": "enabled"}
                updated_account = await storage_client.storage_accounts.update(
                    resource_group_name, storage_account_name, {"tags": tags}
                )
                print(updated_account.name)
```

The factories remove the need to write a callback, **not** the separate Policy
client. They accept its bound acquisition method, avoiding a dependency from
`azure-mgmt-core` to `azure-mgmt-resource-policy`. Pass the same subscription ID
used to construct that client. The caller continues to own client configuration
and cleanup. Custom callbacks remain supported.

The helper embeds the original serialized JSON directly in `operation.content`;
do not replace it with a parsed model or dictionary. Tokens are opaque and are
passed verbatim. A new policy instance should be used for each client pipeline.

### Prototype boundaries

- Only subscription-level `PUT`, `PATCH`, `POST`, and `DELETE` operations are
  supported. GETs, unrelated denials, acquisition requests, and requests with a
  caller-supplied token are left unchanged.
- Bodies must be in-memory UTF-8 JSON, with a JSON content type, or absent.
  Streams, multipart/form data, management-group scopes, and automatic
  ChangeSafety integration are not supported. An actionable challenge for an
  unsupported body or required change reference raises an explicit error.
- Acquisition must succeed, contain a nonempty token, and report only
  `Allow`/`Audit` evaluations. Acquisition/evaluation failure does not replay the
  operation. Azure SDK provider errors are chained to an `HttpResponseError`
  retaining the original 403 and ARM error details.
- Standard retry/authentication policies run again on replay, but token
  acquisition itself is never repeated by this policy. Configure timeouts and
  retries on both clients. A shared end-to-end deadline across the provider and
  replay is not implemented in this prototype.
- Token-bearing replay deliberately disables redirects and raw HTTP debug
  logging. The default provider factories also disable acquisition body logging
  and redirects; custom providers must do the same. Custom policies, telemetry,
  and test recordings must not expose
  tokens. Do not add this header to logging allowlists.
- For sovereign clouds or custom endpoints, configure both clients with the same
  trusted ARM endpoint, credential scopes, and cloud settings. Do not choose the
  acquisition endpoint from the challenge payload.
- Live service byte-binding, authorization, LRO integration, and cross-language
  API approval remain review/validation work before this can ship.


## Contributing
This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information, see the
[Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any
additional questions or comments.

<!-- LINKS -->
[package]: https://pypi.org/project/azure-mgmt-core/
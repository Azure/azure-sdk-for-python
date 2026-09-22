# Azure AI Fine-Tuning Sessions client library for Python

Preview client library for interactive supervised and reinforcement fine-tuning
in Microsoft Foundry. Create a session, submit training or sampling requests,
and save checkpoints with synchronous or asynchronous Python clients.

This preview preserves the tested Loom SDK's public API and behavior at commit
`485774df502642879fdf3a53777be4a0d95155dc`, with the agreed package/import rename.
The public SDK is reproducibly generated from TypeSpec plus maintained Python
customizations. See [GENERATION.md](GENERATION.md) for validation, local source
provenance, and deliberately deferred review fixes.

## Getting started

### Install the package

```bash
python -m pip install azure-ai-finetuningsessions
```

The distribution name is `azure-ai-finetuningsessions`. Python imports are now
`azure.ai.finetuningsessions`, including the asynchronous `aio` namespace.
Update earlier `azure.ai.finetuning_sessions` imports to the new spelling.

If an earlier preview was installed as `azure-ai-finetuning-sessions`, uninstall
that distribution **before** installing this one:

```bash
python -m pip uninstall azure-ai-finetuning-sessions
python -m pip install azure-ai-finetuningsessions
```

Update dependency files and lockfiles to use `azure-ai-finetuningsessions` as
well. A distribution-only preview used this same distribution name with the old
Python namespace and the same version number. If upgrading from that snapshot,
uninstall it before installing the new build so pip does not leave stale modules
or skip the reinstall. Do not rely on both preview distributions being installed.

#### Prerequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- A Foundry project with access to fine-tuning sessions and compatible model capacity.
- A gateway or Loom endpoint supporting `/fine_tuning/sessions`.

#### Authenticate with Microsoft Entra ID
To use a [token credential][authenticate_with_token],
provide an instance of the desired credential type obtained from the
[azure-identity][azure_identity_credentials] library.

To authenticate with AAD, you must first [pip][pip] install [`azure-identity`][azure_identity_pip]

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.
As an example, [DefaultAzureCredential][default_azure_credential] can be used to authenticate the client:

Use the returned token credential to authenticate the client:

```python
from azure.ai.finetuningsessions import FineTuningSessionClient
from azure.identity import DefaultAzureCredential

client = FineTuningSessionClient(
    endpoint="https://<account>.services.ai.azure.com/api/projects/<project>",
    credential=DefaultAzureCredential(),
)
```

`AzureKeyCredential` is also supported when API-key authentication is enabled for
the endpoint. Credential selection is preserved exactly as in Loom's configuration
and client customization. HTTPS is the default. The `allow_insecure_http` option
does not disable bearer-token HTTPS enforcement for remote endpoints; its HTTP
exception is restricted to loopback development servers.

## Create a session

```python
from azure.ai.finetuningsessions import FineTuningSession
from azure.ai.finetuningsessions.models import LoRAConfig

session = FineTuningSession.create(
        client,
        base_model="<supported-base-model>",
        lora_config=LoRAConfig(rank=16),
        user_metadata={"experiment": "example", "enabled": True},
        training_type="GlobalStandard",
)
try:
        # Submit forward_backward, optim_step, sample, and checkpoint requests here.
        pass
finally:
        session.close()
        client.close()
```

The asynchronous entry point is `azure.ai.finetuningsessions.aio.FineTuningSessionClient`.
Its `create_session` method returns a session ID after initialization; training,
sampling, checkpoint, and deletion methods accept that ID. Creation supports
`from_checkpoint`, JSON-valued `user_metadata`, and `training_type`. The service
requires a LoRA configuration with a rank; use values supported by the selected
model rather than assuming a client-side default.

## Generated operations versus convenience methods

Use `FineTuningSession` or the async client's convenience methods for training,
sampling, checkpoints, and session lifecycle operations, as in the tested Loom
SDK. They submit HTTP 200 requests, poll the returned request identifier, and
normalize results with the existing retries, chunking, heartbeat, and error handling.

The older raw `begin_*` surface is retained through supported operation hooks,
including its Azure LRO behavior; it is not a newly corrected request-ID poller. Likewise,
raw `operations.get` still declares `OperationResult`, and raw `sessions.create`
returns JSON rather than the public-only `CreateSessionResponse` model. These
are known legacy behaviors, not proof that every raw operation matches
the service's asynchronous protocol. HTTP 200 does not mean GPU work has finished.

All generated and convenience requests use `/fine_tuning/sessions`. No route
selection flag or gateway rewrite is needed. The public-only `use_legacy_routes`
option and compatibility adapters are not included in this Loom parity baseline.

## Compatibility with earlier previews

The renamed import is an intentional migration. The established convenience
methods, typed exceptions, retries, chunking, session-ID handling, checkpoint
helpers, and environment-variable names remain available. In particular,
omitting `lora_config` still omits it from the convenience request; a service
that requires an explicit rank can reject that request as before.

Public operation keywords and model declarations match the pinned Loom
API, including `body`, `operation_id`, and explicit per-call `api_version`.
This replaces the public-only regenerated surface; callers that adopted its
additional models, methods, or adapters must use the Loom surface instead.
`ApiError`, `ApiErrorResponse`, the top-level typed exceptions, and established
convenience APIs remain available as in Loom.

The awaited async heartbeat shutdown fix is intentionally deferred until after
baseline parity: matching Loom does not mean that review finding has been fixed.
See [GENERATION.md](GENERATION.md) for the exact source, limitations, and next stage.

## Inference error codes

Retryable inference failures use `request_timeout`, `request_orphaned`,
`inference_request_rate_limited`, and `inference_unavailable`. The SDK exposes
the server's code on `RequestRetryableError.error_code` and resubmits based on
`should_retry`, honoring `retry_after_sec`; it does not match code names.
Older services returning legacy inference codes remain supported by the same
mechanism. `invalid_request` and `internal_error` remain terminal.

## Local development

From the Azure SDK for Python repository root, install this package in editable
mode (after removing any older-named preview as described above):

```bash
python -m pip install --editable ./sdk/ai/azure-ai-finetuningsessions
```

Run the package's tests with `pytest`; the package configuration enables asyncio
tests. [verify_loom_snapshot.py](verify_loom_snapshot.py) verifies every runtime
and upstream test file against the pinned Loom source. With `--loom-repo`, the
check verifies the original Git blobs as well as the manifest hashes.

[verify_generation.py](verify_generation.py) separately emits TypeSpec twice into
temporary directories. Generation drift is currently a real reconciliation gap,
not an allowed snapshot difference. Do not generate over the preview runtime
until this independent check passes. See [GENERATION.md](GENERATION.md).

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

# Azure AI Fine-Tuning Sessions client library for Python

Preview client library for interactive supervised and reinforcement fine-tuning
in Microsoft Foundry. Create a session, submit training or sampling requests,
and save checkpoints with synchronous or asynchronous Python clients.

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
the endpoint. Credential selection is preserved in handwritten client hooks so
it survives regeneration. HTTPS is the default. The `allow_insecure_http` option
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

- Generated `sessions.create`, `training.forward`, `training.forward_backward`,
    `training.optimizer_step`, checkpoint, and sampling methods expose the REST
    submission response. HTTP 200 does **not** mean the GPU work has finished.
- Poll `operations.get` with the returned `request_id`. The raw status is
    `pending`, `completed`, or `failed`. Completed envelopes contain `result`;
    failed envelopes can include retry and diagnostic hints.
- Convenience methods handle this protocol and return normalized
    `OperationResult` objects. They preserve the established `optim_step` name,
    retries, chunking, heartbeat, session-ID handling, and typed errors.
- Session list results retain `data` and the explicit `cursor`; advance `offset`
    and `limit` yourself. Checkpoint lists return their complete envelope.
- All generated and convenience requests use `/fine_tuning/sessions`, including
    request polling. No route-selection flag or gateway rewrite is required to
    select the existing route family.

## Compatibility with earlier previews

The renamed import is an intentional migration. The established convenience
methods, typed exceptions, retries, chunking, session-ID handling, checkpoint
helpers, and environment-variable names remain available. In particular,
omitting `lora_config` still omits it from the convenience request; a service
that requires an explicit rank can reject that request as before.

The synchronous and asynchronous clients use `/fine_tuning/sessions` directly.
The earlier `use_legacy_routes` constructor option remains accepted as a
compatibility no-op: omitting it, setting `False`, and setting `True` all send
the same routes. It does not install a rewrite policy or alter custom pipelines.
The client never probes a second route or resubmits a POST merely because a
route failed.

Earlier operation keywords `body`, `operation_id`, and per-call `api_version`
are accepted by handwritten adapters. Per-call API versions do not mutate the
shared client or leak into transport options. `ApiError` and `ApiErrorResponse`
remain importable from `models`.

The legacy `sessions.begin_create`, `sessions.begin_unload`,
`training.begin_forward_backward`, `training.begin_optim_step`,
`checkpoints.begin_save`, `checkpoints.begin_save_sampler_weights`, and
`sampling.begin_sample` names return Azure Core pollers over the real HTTP 200
request-ID protocol. They submit once and poll the request; they do not invent
an HTTP 202 or `Operation-Location` response. Sampling still needs a real
`checkpoint_id`. `polling=False` returns the submitted handle without polling.
Continuation tokens, custom polling strategies, and streamed responses are not
supported by these adapters and are rejected before submission. Retryable
terminal failures are surfaced, not automatically resubmitted by these pollers;
the convenience methods retain their bounded resubmission behavior.

This is **not** a claim that the older generated surface is identical:
`operations.get` returns the real `pending/completed/failed` envelope, not the
older normalized `OperationResult` projection. Use its `result` on completion,
or use the convenience methods/pollers for normalized results. The generated
create result is a typed, mapping-compatible `CreateSessionResponse` rather
than a plain dictionary. See [GENERATION.md](GENERATION.md) for the exact
side-by-side validation scope and remaining review boundaries.

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
tests. [verify_generation.py](verify_generation.py) emits the TypeSpec twice into
temporary directories and compares generated files against this package without
rewriting either source tree. See [GENERATION.md](GENERATION.md) for the pinned
toolchain, review differences, and the pinned public TypeSpec source.

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

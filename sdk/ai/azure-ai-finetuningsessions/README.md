# Azure AI Fine-Tuning Sessions client library for Python

Preview client library for interactive supervised and reinforcement fine-tuning
in Microsoft Foundry. Create a session, submit training or sampling requests,
and save checkpoints with synchronous or asynchronous Python clients.

This preview starts from the tested Loom SDK at commit
`485774df502642879fdf3a53777be4a0d95155dc`, with the agreed package/import rename,
then applies separately tested fixes for lifecycle, bounded waits, validation,
logging, and client integration.
The public SDK is reproducibly generated from TypeSpec plus maintained Python
customizations. See the [generation and validation guide][generation-guide]
for the reproducible baseline and explicitly documented review changes.

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

## Key concepts

- A **session** holds model and adapter state for training and sampling.
- A **request** is submitted once and then polled until its result is available;
        a successful HTTP submission does not mean GPU work has completed.
- A **checkpoint** persists training state or sampler weights. Sampling requires
        a completed sampler checkpoint identifier.
- Heartbeats keep sessions active. Close/delete sessions explicitly and close
        clients or use their context managers to release HTTP resources.

## Examples

### Create a session

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
        sampler = session.save_weights_for_sampler(seq_id=0, sampling_session_seq_id=0)
        print(sampler.checkpoint_id)
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

### Forward-only passes and session deletion

Both capabilities are available through maintained convenience methods. In the
table below, `session` is a `FineTuningSession` and `async_client` is an
`azure.ai.finetuningsessions.aio.FineTuningSessionClient`.

| Operation | Synchronous API | Asynchronous API |
|---|---|---|
| Forward-only pass | `session.forward(batch)` | `await async_client.forward(session_id, batch)` |
| Delete a session | `session.delete()` | `await async_client.delete_session(session_id)` |

Forward-only passes do not accumulate gradients. These forward methods split
large batches into chunks, submit requests, and poll request IDs until the
completed result is available. Alternatively,
`await async_client.forward_async(session_id, batch)` returns an awaitable for
the result; await that returned object to obtain the completed result.

The delete methods stop the session heartbeat, send HTTP DELETE, and return
`None`. They treat HTTP 404 as success, so deleting an already absent session is
safe to repeat. The service handles cascading deletion of the session's models,
checkpoints, and sampling sessions; the SDK does not wait for background storage
cleanup. Deletion is distinct from `session.close()` or
`await async_client.close_session(session_id)`, which unload the session.

## Generated operations versus convenience methods

Use `FineTuningSession` or the async client's convenience methods for training,
sampling, checkpoints, and session lifecycle operations, as in the tested Loom
SDK. For request-ID-based operations, they submit HTTP 200 requests, poll the
returned request identifier, and normalize results with the existing retries,
chunking, heartbeat, and error handling. Deletion sends HTTP DELETE directly;
it does not poll a request ID.

The raw operation-group methods `client.sessions.delete()` and
`client.training.forward()` are intentionally not generated in this preview.
The convenience entry points above preserve the established preview API used
by Loom and provide the lifecycle, chunking, and polling behavior described
above. Their supported Python customization hooks are included during SDK
regeneration; the REST specification still defines both operations. Adding raw
operation-group entry points would be a separate additive API change.

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

Async lifecycle methods now await heartbeat shutdown before sending close/delete,
and closing the async client drains its heartbeat tasks. Empty batches and sampler
requests missing both a path and sampling-session ordinal are rejected locally
rather than producing an invalid request or a false successful no-op.

## Troubleshooting

### Inference error codes

Retryable inference failures use `request_timeout`, `request_orphaned`,
`inference_request_rate_limited`, and `inference_unavailable`. The SDK exposes
the server's code on `RequestRetryableError.error_code` and resubmits based on
`should_retry`, honoring `retry_after_sec`; it does not match code names.
Older services returning legacy inference codes remain supported by the same
mechanism. `invalid_request` and `internal_error` remain terminal.

### Retry and transport limitations

Use HTTPS endpoints for both token and API-key credentials. The historical
API-key/plain-HTTP behavior is retained pending security review; do not use it
with real credentials. Automatic resubmission after ambiguous transport failures
is also under service review: without a server deduplication contract, blindly
retrying non-idempotent training submissions can duplicate work.

Normal INFO progress logs include status and identifiers, not full create or
completion payloads. `FINETUNING_VERBOSE_HTTP=1` explicitly enables body logging;
do not enable it for sensitive customer data.

When supplying a custom `policies` list or prebuilt pipeline, the caller owns
header/auth policy configuration. Default pipelines propagate configured direct
route context to raw session operations while preserving per-request overrides.

## Next steps

Use the returned sampler checkpoint ID with `FineTuningSession.sample`, and save
training checkpoints before unloading a session. Review the
[generation and validation guide][generation-guide] before changing maintained
customizations or regenerating the package.

### Local development

From the Azure SDK for Python repository root, install this package in editable
mode (after removing any older-named preview as described above):

```bash
python -m pip install --editable ./sdk/ai/azure-ai-finetuningsessions
```

Run the package's tests with `pytest`; the package configuration enables asyncio
tests. The [reference verifier][snapshot-check] verifies the immutable upstream
Git blobs and manifest. Intentional review deltas are recorded separately from
the reproducible baseline; current runtime is not claimed to be byte-identical.

The [generation verifier][generation-check] emits TypeSpec twice with maintained
customizations pre-seeded and compares the complete runtime. A changed or extra
generated file is a failure, not an allowed review delta.

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
[generation-guide]: https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/GENERATION.md
[snapshot-check]: https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/verify_loom_snapshot.py
[generation-check]: https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/verify_generation.py
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/

# Azure AI Fine-Tuning Sessions client library for Python

Preview client library for interactive supervised and reinforcement fine-tuning
in Microsoft Foundry. Create a session, submit training or sampling requests,
and save checkpoints with synchronous or asynchronous Python clients.

For general background, see the [Microsoft Foundry (classic) fine-tuning
overview][fine-tuning-overview]. That article covers general fine-tuning
workflows; it is not documentation for this fine-tuning sessions preview SDK.

The client combines TypeSpec-generated operations and models with maintained
Python customizations for polling, lifecycle, and error handling. See the
[generation and validation guide][generation-guide] for source provenance,
generation instructions, and recorded validation results.

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

- Python 3.10 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- A Foundry project with access to fine-tuning sessions and compatible model capacity.
- A service endpoint supporting `/fine_tuning/sessions`.

#### Authenticate with Microsoft Entra ID

Install [azure-identity][azure_identity_pip] with [pip][pip], then supply a
[token credential][authenticate_with_token] from the
[Azure Identity library][azure_identity_credentials]. For example, use
[DefaultAzureCredential][default_azure_credential]:

```python
from azure.ai.finetuningsessions import FineTuningSessionClient
from azure.identity import DefaultAzureCredential

client = FineTuningSessionClient(
    endpoint="https://<account>.services.ai.azure.com/api/projects/<project>",
    credential=DefaultAzureCredential(),
)
```

`AzureKeyCredential` is also supported when API-key authentication is enabled for
the endpoint. Default API-key authentication requires HTTPS and sends the key
only to the configured origin (scheme, host, and effective port). For local
development only, `allow_insecure_http=True` permits the configured HTTP
loopback origin: `localhost`, `127.0.0.1`, or `[::1]`. It does not permit remote
plaintext authentication. Use HTTPS and non-production credentials for testing.

## Key concepts

- A **session** holds model and adapter state for training and sampling.
- A **request** is submitted and then polled until its result is available;
  a successful HTTP submission does not mean GPU work has completed.
- A **checkpoint** persists training state or sampler weights. Sampling requires
  a completed sampler checkpoint identifier.
- Heartbeats keep sessions active. Close/delete sessions explicitly and close
  clients or use their context managers to release HTTP resources.

## Examples

### Create a session

```python
from azure.ai.finetuningsessions import FineTuningSession
from azure.ai.finetuningsessions.models import LoRAConfig, TrainingType

session = FineTuningSession.create(
    client,
    base_model="<supported-base-model>",
    lora_config=LoRAConfig(rank=16),
    user_metadata={"experiment": "example", "enabled": True},
    training_type=TrainingType.GLOBAL_STANDARD,
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
`from_checkpoint`, JSON-valued `user_metadata`, and `training_type`. Session
creation and checkpoint-resume methods require an explicit `lora_config` with
a `rank`, including `FineTuningSession.create`, `FineTuningSession.create_from_checkpoint`,
`async_client.create_session`, and `async_client.create_session_from_checkpoint`.
Use values supported by the selected model; no client-side rank default is supplied.

Choose the creation API according to the lifecycle behavior needed:

| API | Completion and heartbeat behavior |
|---|---|
| `client.sessions.create(...)` / `await async_client.sessions.create(...)` | Returns the HTTP 200 submission JSON, not an initialized session. Does not poll or start a heartbeat. |
| `client.sessions.begin_create(...)` / `await async_client.sessions.begin_create(...)` | Returns a sync/async poller. Use `poller.result()` / `await poller.result()` for request completion. Does not start a heartbeat. |
| `FineTuningSession.create(...)` / `await async_client.create_session(...)` | Waits for initialization, then starts the existing background heartbeat. Returns a session object / session ID. |

Automatic heartbeat startup in convenience creation is unchanged; an opt-in-only
heartbeat lifecycle has not been implemented.

`training_type` accepts `TrainingType` members or strings. The known wire values
remain `GlobalStandard`, `DatazoneStandard`, and `DeveloperTier`; future strings
are passed through without client-side validation. Set the property explicitly
to select a tier. If omitted, the SDK leaves selection to the service.

### Sampling options and results

`SamplingParams.response_format` has type `Optional[Dict[str, Any]]` and requests
a response format from compatible sampling providers. It is omitted when not
supplied; supported formats depend on the selected model and provider.

`SamplingOperationResult` is a friendly alias for `SampleOperationResult`.
Both names identify the same result model; the existing name remains available.

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
sampling, checkpoints, and session lifecycle operations. For request-ID-based
operations, they submit work, receive HTTP 200 acceptance, poll the returned
request identifier, and normalize results with convenience-level recovery,
chunking, heartbeats, and error handling. Deletion sends HTTP DELETE directly;
it does not poll a request ID.

The raw operation-group methods `client.sessions.delete()` and
`client.training.forward()` are intentionally not generated in this preview.
The convenience entry points above preserve the established preview API and
provide the lifecycle, chunking, and polling behavior described above.
Their supported Python customization hooks are included during SDK
regeneration; the REST specification still defines both operations. Adding raw
operation-group entry points would be a separate additive API change.

The raw operation groups provide lower-level access. Their accepted inputs and
return types can differ from the convenience methods. Prefer convenience APIs
for end-to-end session workflows.

Default raw `begin_*` pollers now accept the real HTTP 200 response in both
sync and async clients, then GET the returned request ID within its session
until completion. They do not invent HTTP 202 or an `Operation-Location` header,
replay the POST, or start a heartbeat. Results retain `OperationResult`
deserialization and the `cls` callback. The default strategy disables transport
retries and redirects for both submission and polling; errors are surfaced.
Its continuation token resumes the existing request with GET only.

Explicit custom polling strategies and `polling=False` (`NoPolling` or
`AsyncNoPolling`) retain their own completion, callback, and continuation
semantics. Disabling polling does not establish that GPU work completed.

All generated and convenience requests use `/fine_tuning/sessions`. No route
selection flag or gateway rewrite is needed. The earlier `use_legacy_routes`
option is not included in this preview.

## Compatibility with earlier previews

The renamed import is an intentional migration. The established convenience
methods, typed exceptions, convenience-level recovery, chunking, session-ID
handling, checkpoint helpers, and environment-variable names remain available.

Requiring `lora_config` and `LoRAConfig.rank` is an intentional breaking change
from earlier previews that allowed omission. Update creation and checkpoint-resume
calls to pass `LoRAConfig(rank=...)`; an empty configuration is not a supported
default. `CreateSessionRequest` also requires `lora_config` with a rank.

The raw operation groups retain the established `body`, `operation_id`, and
explicit per-call `api_version` arguments. Check the current operation signatures
when migrating from an earlier regenerated-only preview. `ApiError`,
`ApiErrorResponse`, and the top-level typed exceptions remain available.

Async lifecycle methods now await heartbeat shutdown before sending close/delete,
and closing the async client drains its heartbeat tasks. Empty batches and sampler
requests missing both a path and sampling-session ordinal are rejected locally
rather than producing an invalid request or a false successful no-op.

## Troubleshooting

### Inference error codes

Retryable inference failures use `request_timeout`, `request_orphaned`,
`inference_request_rate_limited`, and `inference_unavailable`. The SDK exposes
the server's code on `RequestRetryableError.error_code`. Convenience polling
uses `should_retry` to decide whether to resubmit, honoring `retry_after_sec`;
it does not match code names. Default raw pollers surface the error instead.
Older inference codes remain supported by the same mechanism. `invalid_request`
and `internal_error` remain terminal.

### Retry and transport safety

The default sync and async transport retry policies never retry POST requests,
including heartbeats, even if retry counts or method lists are supplied.
Ordinary GET retry behavior is retained. Supplying an explicit `retry_policy`
opts ordinary requests into that policy's behavior; the caller owns mutation
replay safety. The default raw `begin_*` strategy additionally disables retries
and redirects for its own requests, as described above.

This does not change convenience-level recovery decisions, ordinary redirect
handling, or the service's `should_retry` contract. No server deduplication or
exactly-once guarantee is implied; resubmitting an ambiguous mutation can still
duplicate work.

Default pipelines remove SDK API-key authentication on cross-origin redirects.
Direct-route context headers are scoped to the configured origin and session
path, including prepopulated values equal to SDK defaults; those values are
removed outside that scope. Distinct caller header overrides are preserved.
An explicitly supplied value identical to an SDK default is scoped as a default.

Normal INFO progress logs include status and identifiers, not full create or
completion payloads. `FINETUNING_VERBOSE_HTTP=1` explicitly enables body logging;
do not enable it for sensitive customer data.

When supplying a custom `policies` list or prebuilt pipeline, the caller owns
header, authentication, redirect, and retry configuration; the SDK does not
replace that pipeline or promise that its defaults protect caller-owned policies.

Malformed or non-object error bodies retain typed error handling rather than
causing an attribute error. Retry hints must be finite and non-negative.
Mapping-form image inputs undergo the same image validation as keyword inputs.

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
customizations pre-seeded and compares the complete runtime. It uses the SDK
repository's shared emitter manifest and lock, not a package-local override.
A changed or extra generated file is a failure, not an allowed review delta.

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
[fine-tuning-overview]: https://learn.microsoft.com/en-us/azure/foundry-classic/concepts/fine-tuning-overview
[generation-guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/GENERATION.md
[snapshot-check]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/scripts/verify_reference_snapshot.py
[generation-check]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/scripts/verify_generation.py
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[authenticate_with_token]: https://learn.microsoft.com/en-us/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/

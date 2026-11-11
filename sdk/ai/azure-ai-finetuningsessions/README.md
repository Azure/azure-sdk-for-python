# Azure AI Fine-Tuning Sessions client library for Python

Preview client library for interactive supervised and reinforcement fine-tuning
in Microsoft Foundry. Create sessions, submit training and sampling requests,
and save checkpoints with synchronous or asynchronous Python clients.

For general background, see the [Microsoft Foundry fine-tuning overview][overview].
Availability of fine-tuning sessions and individual features depends on your
account, region, model, and service configuration.

## Getting started

### Install the package

```bash
python -m pip install --pre azure-ai-finetuningsessions
python -m pip install azure-identity
```

### Prerequisites

- Python 3.10 or later.
- An [Azure subscription][subscription].
- A Foundry project with access to fine-tuning sessions and compatible capacity.
- The project endpoint supplied for the service, for example
  `https://<account>.services.ai.azure.com/api/projects/<project>`.

### Authenticate and create a session

Use an Azure Identity credential such as `DefaultAzureCredential`.
Session creation requires an explicit LoRA configuration and adapter rank.
Use a base model and configuration supported by your account.

```python
from azure.ai.finetuningsessions import FineTuningSession, FineTuningSessionClient
from azure.ai.finetuningsessions.models import LoRAConfig
from azure.identity import DefaultAzureCredential

endpoint = "https://<account>.services.ai.azure.com/api/projects/<project>"

with DefaultAzureCredential() as credential:
    with FineTuningSessionClient(endpoint=endpoint, credential=credential) as client:
        session = FineTuningSession.create(
            client,
            base_model="<supported-base-model>",
            lora_config=LoRAConfig(rank=16),
            user_metadata={"experiment": "example"},
        )
        try:
            checkpoint = session.save_weights_for_sampler(
                sampling_session_seq_id=0,
                seq_id=0,
            )
            print(checkpoint.checkpoint_id)
        finally:
            session.close()
```

`AzureKeyCredential` is also supported when API-key authentication is enabled
for the endpoint. Use HTTPS. Default API-key authentication sends credentials
only to the configured origin. For local testing, `allow_insecure_http=True`
allows HTTP only for the configured loopback endpoint; it does not permit
remote plaintext authentication.

## Key concepts

- A **session** holds model and adapter state between requests.
- A **request** is submitted and polled until its result is available.
  Successful submission does not mean the requested work has completed.
- A **checkpoint** saves training state or sampler weights. Sampling requires
  a completed sampler checkpoint identifier.
- A **heartbeat** refreshes an active session during gaps between requests.
  Convenience creation starts background heartbeats automatically.

`training_type` accepts `TrainingType` members or strings. Known values are
`GlobalStandard`, `DatazoneStandard`, and `DeveloperTier`. If omitted, the SDK
sends no tier and the service selects the default. Explicit choices remain
subject to service eligibility and capacity; the SDK does not select a
different tier when the requested one is unavailable.

### Client and session lifetime

`FineTuningSession.create(...)` waits for initialization and returns a session
wrapper. Its background heartbeat uses a thread. Calling `session.close()`
stops that heartbeat and requests session unload. Closing the HTTP client
alone does not unload the session or stop a synchronous wrapper's heartbeat.

The asynchronous client returns a session ID from `await client.create_session(...)`.
Its methods accept that ID:

```python
from azure.ai.finetuningsessions.aio import FineTuningSessionClient
from azure.ai.finetuningsessions.models import LoRAConfig
from azure.identity.aio import DefaultAzureCredential

async def run():
    async with DefaultAzureCredential() as credential:
        async with FineTuningSessionClient(
            endpoint="https://<account>.services.ai.azure.com/api/projects/<project>",
            credential=credential,
        ) as client:
            session_id = await client.create_session(
                base_model="<supported-base-model>",
                lora_config=LoRAConfig(rank=16),
            )
            try:
                checkpoint_task = await client.save_weights_for_sampler_async(
                    session_id,
                    name="example-sampler",
                )
                checkpoint = await checkpoint_task
                print(checkpoint.checkpoint_id)
            finally:
                await client.close_session(session_id)
```

Closing the async client drains its heartbeat tasks and closes the transport,
but does not unload or delete remote sessions. Use `close_session` explicitly.
Keep the event loop responsive so background heartbeats can run.

The async `save_weights_for_sampler_async` method returns a task after
submission. Await both the method and its returned task before using the
checkpoint, as shown above.

`session.delete()` and `await async_client.delete_session(session_id)` stop the
associated heartbeat and request deletion of the session and its resources.
They treat an already absent session as successfully deleted. Deletion differs
from unloading and does not wait for background storage cleanup.

### Attach an existing session

For synchronous use, `FineTuningSession(client, session_id)` wraps an existing
session and starts its heartbeat. Repeated wrappers own separate heartbeat
threads, so manage their lifetimes explicitly.

For asynchronous use, call `await async_client.attach_session(session_id)`.
It registers one best-effort heartbeat per client/session and returns `None`.
The first heartbeat is sent after 30 seconds; registration itself makes no
HTTP request and does not verify existence, readiness, or access. Client close
stops these tasks without unloading the remote session.

### Training and sampling

Use the convenience methods for complete workflows:

| Operation | Synchronous API | Asynchronous API |
|---|---|---|
| Forward/backward | `session.forward_backward(batch)` | `await client.forward_backward(session_id, batch)` |
| Forward only | `session.forward(batch)` | `await client.forward(session_id, batch)` |
| Optimizer step | `session.optim_step(adam_params)` | `await client.optim_step(session_id, adam_params)` |
| Save training state | `session.save_weights(path)` | `await client.save_weights(session_id, path)` |
| Sample | `session.sample(...)` | `await client.sample(session_id, ...)` |

Forward-only passes do not accumulate gradients. Training and sampling helpers
submit work, poll request IDs, normalize results, and apply their documented
batching and error-handling behavior.

`ModelInput` accepts ordered text and image chunks. `ModelInputChunk(tokens=...)`
represents token IDs; `ImageChunk` accepts validated JPEG, PNG, or WebP data.
Image validation checks the 10,000,000-byte limit, matching content and format,
positive `expected_tokens`, and at most 64 images per example. Legacy token-only
mappings remain accepted; unknown explicit chunk tags are not reclassified.
Support for any particular chunk variant still depends on the service.

Set `AZURE_AI_FINETUNING_MAX_CHUNK_BYTES` before importing the SDK to override
the approximate per-request chunk-size budget. Unset or invalid values retain
the 5,000,000-byte default; invalid values log a warning. This does not change
the service's request limits.

`SamplingParams.response_format` requests a response format from compatible
models and providers. `SamplingOperationResult` is an alias for
`SampleOperationResult`. Its read-only `prompt_tokens` reports the service's
prompt count once per prompt, not once per sampled sequence. Missing or
invalid counts remain `None`; the SDK does not estimate them from other data.

### Opt-in text-only operations

Sampling and training convenience methods accept `text_only_input` instead
of token-native inputs. Sampling accepts public `system`, `user`, `assistant`,
and `tool` messages and optional function definitions. Only function tools are
supported. Training accepts opaque `sample_ref` values and finite scalar
advantages without exposing underlying token evidence.

Text-only sampling results contain valid assistant choices or safely classified
invalid choices. Invalid choices have no public message but can still have
trainable references; they are not automatically operation failures. Keep
references opaque and use the exact returned value for subsequent training.
Reference training exposes scalar metrics rather than private per-token output.

For compatible models, `reasoning_effort` accepts `"low"`, `"medium"`, `"high"`,
or `None`. Omission or `None` preserves the model default. Unsupported values
are rejected before submission. Text-only sampling does not support prompt
log-probabilities, caller-selected stopping criteria, or `response_format`.
Installing the SDK does not enable these capabilities or grant model access.

### Checkpoint preparation only

`client.checkpoints.download_weights(session_id, checkpoint_id, output_path)`
and its async counterpart currently **prepare a checkpoint on the service;
they do not download files**. They validate the destination, poll preparation,
validate the returned inventory, and return `None` after successful preparation.
They do not create directories, write files, or transfer weights.

These methods require service support and authorized checkpoint access.
Preparation failure, unknown states, invalid inventories, and HTTP/transport
errors are surfaced; unknown states are never treated as success.

The checked destination is `output_path/<session_id>/<checkpoint_id>`.
That checkpoint directory must be empty or absent. Identifiers must be portable
directory names, and resolved paths must remain inside the output root,
including through symlinks. Validation happens before the preparation request
and does not reserve the destination. Do not interpret a successful return as
confirmation of a local download.

### Raw operations and convenience methods

The raw operation groups provide lower-level access with explicit request
models and per-call API versions. Generated requests use canonical
`/fine_tuning_sessions` routes. Some maintained convenience paths retain
compatibility routes using `/fine_tuning/sessions`; use a service endpoint
that supports the operations you call rather than manually rewriting URLs.

Raw `create` methods return submission results without waiting for initialization.
Default raw `begin_*` methods return pollers that accept HTTP 200 submissions
and poll the returned request ID. They do not start a heartbeat. Use
`poller.result()` or `await poller.result()` to obtain completion.
Explicit custom polling or `polling=False` retains the chosen strategy's
semantics; disabling polling does not confirm that work completed.

Raw `client.training.forward` and `client.sessions.delete` methods are not
provided in this preview. Use their session/convenience equivalents.

## Troubleshooting

### Training engine interruptions

`TrainingEngineError` (also available as `EngineDeadError`) with code
`engine_dead` or `worker_crashed` indicates a terminal interruption. Resume in
a **new session** from the latest completed training checkpoint using
`FineTuningSession.create_from_checkpoint(...)` or
`await async_client.create_session_from_checkpoint(...)`.

Keep the source base model and LoRA configuration. Restore the dataset cursor
and client-side learning-rate schedule separately; the SDK does not restore
them. Progress after the checkpoint is not recovered. Without a completed
training checkpoint, restart from the base model.

Do not resubmit training on the interrupted session. Terminal interruption
errors remain terminal even if a response includes a retry hint.
`engine_oom` and `engine_timeout` do not by themselves mean the trainer is
terminally interrupted; follow the error's guidance, such as reducing batch
size or sequence length for an out-of-memory error.

### Transport, retries, and logging

Default transport policies do not retry POST requests, including heartbeats.
Convenience operations have separate bounded recovery for supported service
responses. An explicit `retry_policy` remains caller-owned; the SDK does not
guarantee deduplication or exactly-once execution. Default raw pollers disable
transport retries and redirects for their own submission and polling requests.

Default API-key authentication is removed on cross-origin redirects.
Callers supplying custom policies or pipelines are responsible for their
authentication, retry, and redirect configuration.

Normal INFO logs contain progress and identifiers rather than complete request
or response bodies. `FINETUNING_VERBOSE_HTTP=1` enables body logging; **do not
enable it for sensitive data**. Avoid logging credentials, training inputs,
generated messages, or checkpoint contents.

## Compatibility and migration

The distribution is `azure-ai-finetuningsessions` and imports use
`azure.ai.finetuningsessions`, including its `aio` namespace. If an older
`azure-ai-finetuning-sessions` distribution is installed, uninstall it before
installing this package and update dependency/import declarations.

Creation and checkpoint-resume calls require `lora_config=LoRAConfig(rank=...)`.
No implicit rank or empty LoRA configuration is supplied.

The obsolete `FoundryFeaturesOptInKeys.AGENT_INSIGHTS_V1_PREVIEW` constant is
removed in b2 because Agent Insights no longer requires that preview opt-in.
Explicit references must be removed. Fine-tuning continues using the unchanged
`Foundry-Features: FineTuningSessions=V1Preview` value.

## Contributing

See the [Azure SDK for Python contribution guide][contributing] and
[Microsoft Open Source Code of Conduct][code-of-conduct].

<!-- LINKS -->
[overview]: https://learn.microsoft.com/azure/foundry-classic/concepts/fine-tuning-overview
[subscription]: https://azure.microsoft.com/free/
[contributing]: https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md
[code-of-conduct]: https://opensource.microsoft.com/codeofconduct/

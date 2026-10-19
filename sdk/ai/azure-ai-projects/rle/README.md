# RLE development SDK beta registry

This is the development counterpart of the `rle-releases` registry. Public
distribution uses the `Azure/azure-sdk-for-python` branch `rle-dev-releases`.
Publishing is a separate, human-owned step; pushing this SDK PR does not publish
an artifact to the public repository.

Publish these files under `sdk/ai/azure-ai-projects/rle`, matching public PR #49488:

- `install_rle_sdk.py`
- `registry.json`
- `wheels/2.7.0b5/azure_ai_projects-2.7.0b5-py3-none-any.whl`

The registry pins the wheel checksum. This build uses `2.7.0b5`; published
`2.7.0b2`, `2.7.0b3` and `2.7.0b4` wheels remain unchanged. Subsequent development builds
should increment the beta number and update the registry checksum. The installer
also explicitly reinstalls the verified wheel if the installed version matches.

For a development installation:

```bash
curl --fail --location \
  https://raw.githubusercontent.com/Azure/azure-sdk-for-python/rle-dev-releases/sdk/ai/azure-ai-projects/rle/install_rle_sdk.py \
  --output install_rle_sdk.py
python install_rle_sdk.py --version 2.7.0b5
```

Use `--requirements runtime-requirements.txt` to install command-job dependencies
alongside the SDK. The installer does not add environment-authoring extras.

Command-job images select the beta directly in their Dockerfile installer
command. Run the installer before installing recipe dependencies, which declare
`azure-ai-projects` without a conflicting version or direct wheel URL. Changing
the SDK requires rebuilding the image; existing images do not update at runtime.

Beta `2.7.0b5` adds graceful deployment handoff to the shared async rollout client.
On `server-draining`, old rollouts retain their original receiver while new
submissions open a replacement with fresh credentials. One admission limit covers
all connections. Only the explicit pre-execution `ServerDraining` rejection is
resubmitted with the same ID and request, at most three submissions within the
original deadline. Ambiguous sends or disconnects are never replayed; old
rollouts still depend on the backend delivering results before its drain ends.

The beta retains the typed `HarnessConfiguration` model integrated in `2.7.0b4`.
The shared WebSocket client and sync/async HTTP operations use this single typed
contract, preserving rollout/job correlation. Callers using dictionaries must
construct `HarnessConfiguration` instead. The recipe adapter does this at the SDK
boundary without changing its metadata or wire schema.

The client uses `get_rollout_client()` returning `AsyncRolloutClient`,
matching the OpenEnv client naming, without the old session-name alias.
It retains the opt-in `server_managed_token_renewal=True` for async rollout clients,
keeping a healthy socket open past its age and token expiry.
This requires RLE caller-token renewal, Capture Proxy model-call token renewal,
and service support for long-lived sockets and the requested rollout duration.
It does not remove server limits or implement durable disconnect recovery.
Deployment handoff works with either renewal setting. The SDK default continues
to replace sockets based on age/token expiry.

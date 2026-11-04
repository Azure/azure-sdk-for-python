# RLE preview SDK installation

This directory publishes the approved `azure-ai-projects[rle]` wheel manifest
and a standalone installer. No GitHub credentials or sample checkout are required.
Run the installer in the Python environment where you want to use the SDK.

## PowerShell

```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/Azure/azure-sdk-for-python/rle-releases/sdk/ai/azure-ai-projects/rle/install_rle_sdk.py -OutFile install_rle_sdk.py
python install_rle_sdk.py
```

## macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/Azure/azure-sdk-for-python/rle-releases/sdk/ai/azure-ai-projects/rle/install_rle_sdk.py -o install_rle_sdk.py
python3 install_rle_sdk.py
```

The installer reads the public [manifest](registry.json), downloads only the
selected wheel, verifies SHA-256, and installs it with the `rle` extra.
It uses an explicit public manifest URL, so it can run from any directory.

Version selection follows `--version`, then `AZURE_AI_PROJECTS_VERSION`, then
the manifest's `latest`. Pin an exact version listed in the manifest with:

```powershell
python install_rle_sdk.py --version 2.7.2b1
```

Unavailable versions and checksum mismatches fail installation; there is no
fallback. `--requirements` optionally installs a caller-supplied requirements
file; no requirements file is needed for standalone SDK installation.

## Version 2.7.2b1

This preview adds an optional renewable `finetune_credential` to
`get_rollout_client()` and `AsyncRolloutClient`. The project credential remains
the primary user identity. The optional fine-tuning identity is sent separately
in `x-ms-finetune-identity` on every WebSocket handshake and recovery lookup;
direct SDK customers can omit it. Socket renewal respects the earlier token
expiry, and credential failures never silently remove this identity. A separate
fine-tuning credential cannot be combined with `server_managed_token_renewal=True`.
Existing admission, graceful drain, and no-replay recovery behavior is preserved.

The wheel is built from SDK source commit
`77052fe2e3d73eb8c26ce565db16b38dc64f451e` in
`sujit-kamireddy/azure-sdk-for-python`, with only the staged package version
changed from `2.7.0b7` to `2.7.2b1`. Existing wheel versions and checksums are
preserved. Live dual-token gateway/training qualification remains incomplete;
this artifact is a preview, not a PyPI release.

## Standalone queued V3 development artifact

`2.7.0b7.dev20261104+queuedv3.1` provides explicitly selected durable queued V3
rollout transport. It is a **development-only artifact**, not an approved registry
release or a PyPI publication. The approved registry, `latest` (`2.7.2b1`), existing
installer and all previously published wheels/checksums are unchanged. The SDK
source implementation is reviewed separately; this distribution-only addition
does not modify the source tree on `rle-releases`.

To select the development artifact explicitly, use its immutable public commit
URL with a SHA-256 pin:

```powershell
python -m pip install "azure-ai-projects[rle] @ https://raw.githubusercontent.com/swatisinghvi99/azure-sdk-for-python/4c69a064e7d6c9c013a5be090262e9f2058c2bf9/sdk/ai/azure-ai-projects/rle/wheels/2.7.0b7.dev20261104+queuedv3.1/azure_ai_projects-2.7.0b7.dev20261104+queuedv3.1-py3-none-any.whl#sha256=1cca2b75a5f2fbfa864584bf7f0f830098bf4fe13519cc4e1a39b3bd60a9ea8e"
```

The wheel is anonymously readable from the public fork and contains no GitHub
credentials. Pip verifies the pinned hash before installation. It is deliberately
not selected by the registry installer or its `--version` option. See the
[artifact documentation](wheels/2.7.0b7.dev20261104+queuedv3.1/README.md) and
[provenance](wheels/2.7.0b7.dev20261104+queuedv3.1/provenance.json) for the public API,
source identity and offline validation evidence.

Consumers opt into queued delivery with
`get_rollout_client(..., protocol_version="v3")`; omission retains legacy defaults.
The same optional `finetune_credential` identity behavior is preserved. Training
consumers still need to rebuild and select an image containing this pin.
Publication does not enable service feature gates, qualify worker recovery, run
models, deploy resources or grant permissions.

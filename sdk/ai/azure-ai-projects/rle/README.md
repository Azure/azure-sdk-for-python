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

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
python install_rle_sdk.py --version 2.7.6b1
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

## Version 2.7.3b1

This preview adds optional queued V3 rollout transport:
`get_rollout_client(..., protocol_version="v3")`. Explicit V3 negotiates only
`rle.execute-rollout.v3`, with no legacy fallback. Omitting `protocol_version`
preserves legacy v2/v1 defaults; synchronous/asynchronous HTTP operations are
unchanged. The project credential remains primary and the optional renewable
`finetune_credential` remains separate, with the earlier token expiry bounding
connection lifetime.

The SDK owns durable acceptance/state/progress/terminal delivery, bounded
admission, original-ID attachment recovery, received sequence cursors and
authenticated result retrieval. Connection expiry is checked before each
submission; recovery preserves deadlines and never replays ambiguous execute
commands. Safe opaque `ftjob-` IDs, including managed 32-hex IDs, are preserved
unchanged within the service's 991-character limit.

The wheel is built from merged SDK source
`4f82d3c33e5e55614aeb167bce2ff1980ceba64e` in
`sujit-kamireddy/azure-sdk-for-python`, with only the staged package version
overridden from `2.7.0b7.dev20261104+queuedv3.3` to `2.7.3b1`.
The wheel is 600811 bytes with SHA-256
`a3823cc9e9e9386746523137db58a6ff00833f41aa60cec281bee374085a66d8`.
Existing wheel versions and checksums are preserved; this is distribution,
not an upstream source merge or a PyPI publication.

Version `2.7.3b1` remains available; to pin explicitly:

```powershell
python install_rle_sdk.py --version 2.7.3b1
```

Installing this preview does not enable V3 automatically: callers must opt in.
Image rebuild/selection and service qualification are separate work; this
publication does not run cloud jobs, deploy resources or change permissions.

## Version 2.7.4b1

This preview fixes queued V3 result retrieval for Foundry workspace names such
as `account-name@project-name@AML`. The service encodes `@` as `%40` in result
references; the SDK now accepts that encoding instead of raising
`InvalidRolloutResultReference` after execution completes. Other encoded
characters remain rejected. Original-project authentication, rollout-ID checks,
disabled redirects and no execution replay are preserved. No V4 backend or
protocol selection is required.

The wheel also includes the already-merged grading-context additions from
source PR #9.

The wheel is built from merged SDK source
`1e8d9b3e338b936b1b6ac14248cd7b086ced9433` in
`sujit-kamireddy/azure-sdk-for-python`, including source PR #14, with only the
staged package version overridden from `2.7.0b7.dev20261104+queuedv3.4` to
`2.7.4b1`. The wheel is 602347 bytes with SHA-256
`fb99412bfd393ee04cc6575515c5fc2ea3400a9ba85ecc14dd2fa545b99636e1`.
All 102 queued V3 offline tests passed against an isolated installation of
this wheel. Live gateway or training qualification was not performed.

Version `2.7.4b1` remains available for explicit installation. Existing
environments and training images must install a fixed version or be rebuilt
to consume the fix. This is not a PyPI publication.

## Version 2.7.5b1

This preview adds opt-in V4 completion-to-HTTP result delivery:
`get_rollout_client(..., protocol_version="v4")`. The socket carries a small
completion notification; the SDK fetches the complete stored result using an
authenticated HTTP GET at the original project endpoint. Downloads do not
block the socket receiver, preserve the original deadline, and never replay
rollout execution.

V4 result downloads default to **32 MiB (33,554,432 bytes)**. Callers can
increase or decrease the per-call budget with
`execute_rollout(..., max_response_bytes=64 * 1024 * 1024)`. A
`RolloutResultTooLarge` error reports the configured limit, bytes observed,
rollout ID, and an example override. The rollout has completed; only result
retrieval failed. Full responses are buffered and parsed in memory, so choose
a limit appropriate for the calling process.

Omitting `protocol_version` preserves legacy defaults. V3 and legacy result
budgets remain 8 MiB, and the WebSocket payload limit remains 8 MiB. V4 requires
a backend that supports `rle.execute-rollout.v4`; installing this wheel does not
deploy or enable backend support. The typed result exposes the current
`rollout_graph` field and retains legacy `rollout` support.

The wheel is built from merged SDK source
`4dfc1b984da6fae96b68969c302f7e7286501976` in
`sujit-kamireddy/azure-sdk-for-python`, including source PR #13 and the earlier
V3 Foundry reference fix from PR #14. Only the staged package version is
overridden to `2.7.5b1`. The wheel is 603721 bytes with SHA-256
`5f31c171ba3459210d676cade5f77772795559f179d0d23b60deae1a2e3a46bf`.
All 402 offline rollout and model tests passed against an isolated installation
of this wheel. Packaged Python files match the pinned merged source except for
the release version.

Version `2.7.5b1` remains available for explicit installation. This is an RLE
preview distribution, not a PyPI publication.
No live gateway/training qualification, backend deployment, or image rebuild
is included.

## Version 2.7.6b1

This preview makes **V4 the default** for asynchronous `get_rollout_client()`
and direct `AsyncRolloutClient` construction. Completion notifications trigger
authenticated HTTP retrieval of the full typed result. The configurable result
download budget remains 32 MiB; use
`execute_rollout(..., max_response_bytes=64 * 1024 * 1024)` to increase it.

**A V4-capable backend is required.** Failed negotiation is an explicit error,
with no silent fallback or execution replay. Explicit `protocol_version="v3"`
retains V3. Explicit `protocol_version=None` retains legacy v2/v1, and is
required when using legacy-only `server_managed_token_renewal=True`.
Synchronous and asynchronous one-shot `rle.execute_rollout()` still default
to HTTP. Earlier V3 result-reference fixes are included.

The wheel is built from merged SDK source
`401b1615119282243d460387c5b26f6a8f174fac` in
`sujit-kamireddy/azure-sdk-for-python`, including source PR #16. Only the staged
package version is overridden to `2.7.6b1`. The wheel is 604062 bytes with SHA-256
`16c237b9e7b6f923c975a13b61c17c34006589239ade7d72a516a673f1e137db`.
All 404 offline rollout and model tests passed against an isolated installation
of this wheel. Packaged Python files match the pinned merged source except for
the release version.

The registry selects `2.7.6b1` as `latest`, preserving all earlier versions and
checksums. This is an RLE preview distribution, not a PyPI publication.
Backend deployment, live gateway/training qualification and consumer image
rebuilds are separate work.

## Version 2.7.7b1

This explicitly pinned preview preserves caller-safe grader causes from queued
V3/V4 failed events, including attachment recovery and synthesized terminal
delivery. `RLERolloutError` exposes `cause`, `service_message`, `attempt_id` and
`sequence`. Unknown cause codes remain available as bounded metadata; arbitrary
fields are discarded. Older failures without structured causes stay generic.
No raw grader traceback or diagnostic is introduced by this change.

The wheel is built from SDK source PR #15 commit
`c2221797bf30457520ead8ba027bb80ad35e67c6` in
`sujit-kamireddy/azure-sdk-for-python`, with only the staged package version
overridden to `2.7.7b1`. That source includes the merged `2.7.6b1` source
revision. V4 remains the default; consumers requiring V3 must continue to set
`protocol_version="v3"` explicitly. Source PR #15 is not merged by this artifact
publication.

The wheel is 610379 bytes with SHA-256
`d73422c1c21f0e9be3983c146dcc3373f1e0e69908c7c3ef900764dbf1e1f2ed`.
All 291 offline rollout tests and 27 Loom WebSocket/breaker/report integration
tests passed against an isolated installation of the wheel, without an SDK
source-path override.

`latest` deliberately remains `2.7.6b1`; this publication adds an opt-in version
and preserves every existing wheel and checksum. The registry entry becomes
usable through the upstream installer only after this artifact PR is merged
into `rle-releases`. Immutable, hash-pinned public-fork artifact URLs can be
consumed before that merge. This is not a PyPI release, upstream source merge,
backend deployment, image publication or live training qualification.

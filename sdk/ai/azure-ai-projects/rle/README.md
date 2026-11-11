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
python install_rle_sdk.py --version 2.7.9b1
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

Version `2.7.6b1` remains available for explicit installation.
This is an RLE preview distribution, not a PyPI publication.
Backend deployment, live gateway/training qualification and consumer image
rebuilds are separate work.

## Version 2.7.7b1

This preview adds optional per-rollout model sampling defaults to
`SamplingOptions`: `max_completion_tokens`, `temperature`, `top_p`, `top_k`,
and `seed`. Pass `sampling=SamplingOptions(...)` to HTTP or shared-session
`execute_rollout()` calls. Explicit model-request values override these
defaults; service/provider ceilings and remaining model context still apply.
Training capture requires neutral `top_p=1` and `top_k=-1` or `0`. Provider
support varies, and a seed does not guarantee reproducibility.

V4 remains the default for asynchronous rollout sessions, with authenticated
full-result retrieval and the configurable 32 MiB download budget. Explicit
V3/legacy selections and one-shot HTTP defaults are unchanged.

The wheel is built from merged SDK source
`ead8557db7474a94c38d3fce3564e249642c3da6` in
`sujit-kamireddy/azure-sdk-for-python`, including source PR #11. Only the staged
package version is overridden to `2.7.7b1`. The wheel is 604885 bytes with SHA-256
`09319d1f7a5a2889677c03ac9ca952fd89913d93a80f441e9fbf52611b30f470`.
All 406 offline rollout and model tests passed against an isolated installation
of this wheel, including sampling serialization over HTTP and WebSocket.
Packaged Python files match the pinned merged source except for the release
version.

The registry selects `2.7.7b1` as `latest`, preserving all seven earlier
versions and checksums. This is an RLE preview distribution, not a PyPI
publication. Backend deployment, live gateway/training qualification and
consumer image rebuilds are separate work.

## Version 2.7.8b1

This preview adds optional top-level `phase="train"` or `phase="eval"` to
rollout requests, synchronous/asynchronous HTTP operations, and shared async
rollout clients. Omitted values remain absent; invalid values fail before
submission. A backend that accepts the phase field is required.

Legacy terminal failures preserve an explicit boolean retry hint on
`RLERolloutError.retryable`. Missing/nonboolean hints and unknown outcomes
remain nonretryable. Queued V3/V4 dependency `cause.retryable=true` does not
authorize fresh execution and never sets this terminal retry property.
The SDK does not automatically replay executions.

The wheel also includes merged model/renderer catalog preflight and bounded
structured queued failure causes. V4 defaults, protected full-result retrieval,
dual credentials, admission at 32, and original-ID attachment remain unchanged.

The wheel is built from merged SDK source
`6cdd9afe512e826355a861338c2b0179d0cf7fb1` in
`sujit-kamireddy/azure-sdk-for-python`, including source PR #18. Only the staged
package version is overridden to `2.7.8b1`. The wheel is 612970 bytes with SHA-256
`eba805b4d5a7e8d665328903fe23bb865738bd43985462ab09a4aa278d9476b6`.
All 595 offline rollout/model tests passed against an isolated installation
of this wheel. All 63 packaged Python files match the merged source except
for the release version, and all nine registry wheels pass integrity and
checksum validation.

At publication, the registry selected `2.7.8b1` as `latest`, preserving all eight earlier
versions and checksums. This is an RLE preview distribution, not a PyPI
publication. Backend deployment, live gateway/training qualification and
consumer image rebuilds are separate work.

## Version 2.7.9b1

This preview isolates invalid queued V3/V4 event payloads when the SDK can
trust their rollout correlation. Only the affected call fails; unfinished
sibling calls and subsequent work remain usable. Malformed optional structured
failure causes are omitted with a safe diagnostic instead of replacing the
original terminal error or failing sibling rollouts.

Diagnostics contain fixed validation categories and validated rollout IDs,
not full frames, credentials, trajectories or terminal error text. Admission
at 32, deadlines, authentication, existing transport defaults and no execution
replay remain unchanged. Nullable/optional cause-schema alignment and recovery
changes for untrustworthy framing/correlation are not included.

The candidate wheel is built from SDK source commit
[`c31afd0fd325f73fd4ab781a6b0c8833e92a7c28`](https://github.com/sujit-kamireddy/azure-sdk-for-python/commit/c31afd0fd325f73fd4ab781a6b0c8833e92a7c28)
in [source PR #19](https://github.com/sujit-kamireddy/azure-sdk-for-python/pull/19),
with only the staged package version overridden to `2.7.9b1`.
Source PR #19 must receive human review and merge before this candidate is
published.

The wheel is 613555 bytes with SHA-256
`a586a2c1e42746f192dde209056e717d3a7a3e842dfc16359095d4c34eac7486`.
An isolated installation passed 804 offline RLE/rollout/model tests, with two
tests skipped. All 63 packaged Python files match the pinned source except
for the release version, dependency requirements are unchanged, and all ten
registry wheels pass integrity and checksum validation.

The prepared registry selects `2.7.9b1` as `latest`, preserving all nine
earlier versions and entries. This is an RLE preview distribution, not a
PyPI publication. Backend deployment, live gateway/training qualification
and consumer image rebuilds are separate work.

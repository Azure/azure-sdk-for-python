# Generation and local review

## Reference and scope

The runtime SDK and its regression tests were ported from Loom master commit
`af8006382149c72c646d488b2bcee004767380f2`. The public TypeSpec was reconciled
with that SDK and the actual service schemas, rather than reverse-mapping only
files that happened to be different between two manually edited SDK copies.

The follow-up inference-error documentation and retry tests from
`8710e209831248a986393c2df0ee47e333d51dfa` are included as well; that follow-up
does not change the SDK runtime or raw response schema.

The namespace migration uses Loom master
`f6033f7a4137339c40da63525df12c4cfcb599cb` as its behavioral baseline. There
were no additional SDK changes between the follow-up above and that revision.
Loom's local `haarunkumar/finetuningsessions-namespace` branch renames its SDK
and in-repository consumers while preserving its legacy service routes. Those
Loom changes remain uncommitted and are not part of the public SDK/spec commits.

The feature branches incorporate their September 17 target revisions through
ordinary merge commits, without rebasing or rewriting existing history. PR
reopening and review remain separate from pushing the feature branches.

## Package identity

The distribution and SDK package directory are named
`azure-ai-finetuningsessions`. Wheels and source archives use the normalized
distribution stem `azure_ai_finetuningsessions`. The Python namespace is now
`azure.ai.finetuningsessions`; model/client names and REST routes are unchanged.
See [installation and migration guidance](README.md#install-the-package) before
switching an environment that contains the earlier preview distribution.

The TypeSpec client project is
`specification/ai-foundry/data-plane/Foundry/src/sdk-python-azure-ai-finetuningsessions`.
Its emitter configuration sets both `package-name` and `emitter-output-dir` to
the renamed package. Both the emitter namespace and all relevant Python
`clientNamespace` mappings select `azure.ai.finetuningsessions`.
Regeneration also sets the sync/async SDK user-agent moniker to
`ai-finetuningsessions`; wire-contract tests assert that name on real outbound
requests through the offline transports.

The local migration also updates the Loom SDK copy, in-repository cookbook and
job/benchmark imports, dependency names, lockfile references, build paths, and
notebooks. The separate public cookbook repository is not updated by these
changes and still needs its own coordinated source/wheel migration.

## Sources

- Public spec repository: `Azure/azure-rest-api-specs`, branch
  `haarunkumar/finetuning-sessions-spec`, targeting `feature/foundry-release`.
- SDK branch: `feature/finetuning-sessions-sdk`, targeting `main`.
- The generation source is described by [tsp-location.yaml](tsp-location.yaml).
  It pins the immutable TypeSpec commit
  `5507786d95dd56c5346cabb3d8b8fcf6282eaacc`, including the route restoration
  and suppression cleanup while retaining the namespace migration and preview
  error-model exports.
  Generation was verified against
  that commit's exact source content; the fingerprint below identifies it.
- The TypeSpec target incorporated is
  `6d8e681878ddcfad7749a69e48dea167755dde6b`; the SDK main target incorporated is
  `031b28b8b36efd78bc326de802ef03c1c53af7d4`.

For future updates, commit and push TypeSpec first, replace the source pin with
the new full SHA, and recheck generation before committing the SDK. The TypeSpec
commit must be remotely available before remote SDK regeneration can use it.

## Pinned generation environment

| Package | Version |
|---|---|
| `@typespec/compiler`, `@typespec/http`, `@typespec/openapi3` | `1.16.0` |
| `@azure-tools/typespec-azure-core`, `@azure-tools/typespec-client-generator-core` | `0.72.0` |
| `@azure-tools/typespec-python` | `0.63.7` |
| `@typespec/http-client-python` | `0.37.2` |
| `@azure-tools/openai-typespec` | `1.28.0` |

The SDK emitter version matches the SDK repository's emitter manifest. The
public specs repository pins the compiler and service libraries. Full Foundry
validation used its frozen pnpm lockfile with Node 24.14.1 and pnpm 11.8.0.
Python generation used an isolated installation of the package-specific emitter
manifest, without modifying shared dependency manifests or lock files.

[emitter-package.json](emitter-package.json) pins this package's generation
toolchain explicitly and is referenced by [tsp-location.yaml](tsp-location.yaml),
including the `client.tsp` entry point. This avoids changing the shared emitter
manifest or accidentally mixing service-library versions during regeneration.

The emitter's automatic `uv` bootstrap encountered package-download TLS errors.
Its isolated Python environment was instead installed through its supported
`package_manager.install_packages(..., package_manager="python -m pip")` path,
using the configured package feed. `PYYAML_FORCE_LIBYAML=0` built the pinned
PyYAML dependency in pure Python on Python 3.13. TLS verification was not disabled.

## Verification

[verify_generation.py](verify_generation.py) takes `--spec-repo` followed by the
local public specs repository root and optionally `--toolchain` followed by an
isolated directory containing the pinned generation dependencies. It:

1. Verifies the installed TypeSpec/compiler/emitter versions.
2. Snapshots the SDK-specific TypeSpec inputs into temporary directories under
  that toolchain and generates Python twice into isolated package directories.
3. Compares all generated Python modules, typing marker, and generated metadata
   with each other and with this SDK package, ignoring only CRLF/LF differences.
4. Detects extra/orphaned generated modules in the SDK.
5. Confirms neither the TypeSpec sources nor the package's handwritten files were
   changed by the check.

It does not install dependencies, update this package, stage files, or commit.
The input fingerprint identifies the exact TypeSpec working-tree content. Input
snapshots prevent an older npm emitter from resolving newer pnpm libraries (or
the reverse) merely because both installations exist on the same machine.

To update the generated layer, compile the SDK-specific TypeSpec client entry
point with its adjacent configuration and set the Python emitter output directory
to this package. Do not modify emitted code to force parity. The emitter preserves
patch files, but its formatter may normalize handwritten Python formatting.

## Intentional differences from the source snapshot

- Generated operations, convenience calls, heartbeats, and polling use the
  existing `/fine_tuning/sessions` paths directly, matching Loom. The earlier
  `use_legacy_routes` option is accepted as a no-op for either value. No rewrite
  policy, automatic fallback, or gateway deployment is needed for route selection.
- Raw generated responses now match HTTP 200 submissions, string `session_id`,
  `request_id`, and `pending/completed/failed` request envelopes. Generated
  operations use ordinary submission methods; no invented `Operation-Location`
  response is required. The seven older `begin_*` names are preserved by
  [handwritten request pollers](azure/ai/finetuningsessions/_legacy_polling.py),
  with the limits described in [README.md](README.md#compatibility-with-earlier-previews).
- The generated optimizer operation is `training.optimizer_step`; the
  convenience `optim_step` API remains unchanged.
- The raw service requires LoRA configuration and rank. Optional convenience
  arguments and omission behavior are retained for compatibility; examples
  supply a valid rank. No empty LoRA object is injected when the caller omits it.
- `user_metadata` retains arbitrary JSON values. Omitted `training_type` remains
  omitted so the service's legacy metadata selector is not overridden by an
  injected client default.
- The raw contract includes forward requests, checkpoint resume/deletion,
  checkpoint metadata, multimodal chunks, vision/projector settings, and the
  required sample `checkpoint_id` query parameter.
- `ejectable` is not a declared service creation field in the reference schema;
  it is no longer advertised as a generated raw input. SDK-only output
  normalization stays outside the raw REST response definitions.
- SDK-only normalized result types are declared in the Python customization
  entry point, not presented as the service's raw polling schema.
- Authentication/HTTPS policy selection, exception exports, and logging wiring
  are preserved in [the handwritten options module](azure/ai/finetuningsessions/_client_options.py)
  and patch modules instead of manual edits to generated configuration/initializer
  files. Guard tests exercise the supported public clients.
- Earlier `body`, `operation_id`, and per-call `api_version` keywords are handled
  by [handwritten adapters](azure/ai/finetuningsessions/_compat.py). Per-call
  configuration is copied instead of mutating shared client state. The
  convenience heartbeat retains Loom's `v1` default. Earlier `ApiError` and
  `ApiErrorResponse` exports are forced through TypeSpec usage metadata.
- Session lists return explicit page/cursor responses. The REST specification
  uses offset pagination decorators; Python disables incomplete automatic paging
  rather than silently returning only one page or inventing a `nextLink`.

## Loom comparison, not a whole-source identity claim

[verify_loom_compatibility.py](verify_loom_compatibility.py) takes `--loom-repo`
and imports each SDK in a separate subprocess. Network access and filesystem
writes are blocked in each worker. Twenty paired cases compare actual outgoing
URLs, headers, JSON bodies, model attributes, exceptions, exported symbols,
selected signatures, and session/resource-ID mappings. Both SDKs use their
default routes with no selection flag; the verifier does not normalize route
paths after requests are sent. Background heartbeats are disabled in this workload.

Only header casing, validated random request UUIDs, the exact runtime suffix
of the user agent, and JSON object ordering are normalized. Added generated
models/shared preview flags and explicit constructor keyword additions are
listed separately. The workload is not proof of source equality or every
service behavior: raw `operations.get` still returns the correct
`pending/completed/failed` envelope rather than the earlier normalized model
projection. Generated create responses are mapping-compatible typed models,
not plain dictionaries. The old generated LRO methods are tested separately
against the real HTTP-200 protocol, not treated as a correct baseline.

The legacy poller adapters submit once, preserve ordinary result callbacks and
polling intervals, and surface typed terminal failures. They do not support
continuation tokens, arbitrary polling strategies, streaming, or automatic
resubmission. These are explicit compatibility boundaries, not passing parity
claims. The existing convenience APIs retain their own bounded resubmissions.

## Validation boundaries

Offline regression and raw-contract tests cover sync/async clients, all 15
generated routes, credentials, metadata, poll envelopes, session IDs, checkpoint
results, image serialization, log-probabilities, retry budgets, and convenience
behavior. No live service or GPU training test was run.

The full Foundry specification and Python SDK project compile and emit. Remaining
TypeSpec linter warnings include the existing/custom operation-template rule,
shared Foundry documentation, legacy paging compatibility, and non-enum unions.
Compilation success does not mean the PR's entire CI is green.

The SDK automation helper's full pylint/mypy checks could not install its
dependencies because of feed authentication/TLS errors. These full repository
checks require a working authenticated package-feed environment and remain
distinct from the offline tests and successful emission comparisons.

### Local results after restoring the existing routes

- **706 public SDK tests passed** against both source and the installed wheel.
  This includes default, false,
  and true route-option cases, custom-pipeline preservation, and all existing
  compatibility regressions.
- **428 Loom SDK tests passed** before/after the mechanical rename and against
  its installed renamed wheel. Both wheels contain only the new Python namespace.
- **20/20 paired cases passed**, with **134 requests and 2,246 checks per SDK**,
  using both SDKs' default routes without a route-selection flag.
- **22 generated files** matched two independent pinned emissions; handwritten
  files and TypeSpec source were unchanged during verification.
- The renamed TypeSpec input fingerprint is
  `0bfa77b361e2bb531a006c46766d9d2d93c816e8b283a0f58e03d637ba480b8d`.
- The unused `no-unknown` linter disable was removed without changing generated
  output. The closed-literal-union exception remains justified by existing
  input/shared unions and still requires API reviewer approval.
- The API contains **13 paths / 15 methods**, now under `/fine_tuning/sessions`,
  matching HTTP 200 submissions and raw request-status envelopes. Package and
  Python namespace names remain `azure-ai-finetuningsessions` and
  `azure.ai.finetuningsessions`; the route restoration does not change models.
- Full Foundry compilation and Python emission were rerun successfully. Full-service
  compilation retained 29 warnings; Python emission retained 66 warnings.
- Both wheels and source archives build with the new distribution name. Public
  wheel: **29 Python modules**; Loom wheel: **26 Python modules**. Wheel modules
  match their respective sources, include `py.typed`, and contain no stale
  old-namespace modules, build trees, or tests.
- Reviewed public wheel SHA-256:
  `0b539a05b737e79394041b079d9aa7ebfd9add9ca732addf0a989bffd7b2edd6`.
  Reviewed Loom wheel SHA-256:
  `30bfd7bdbd941c33215fea80886d21439e9a094918482882083c80c2327aafb3`.
- Six changed PowerShell build scripts parse successfully; the renamed Loom
  SDK lockfile passes `uv lock --check --offline`. Full consumer lock resolution
  is blocked by uncached dependencies (including the private ECS package).
  Heavy cookbook/service test environments and live GPU tests were not run.
  Loom's pre-existing missing changelog packaging warning remains unchanged.

The original unrelated shared client-tool lockfile difference was removed during
merge resolution, and the old wheel was removed from Git tracking (its local
copy was preserved). A wheel belongs in a distribution/cookbook workflow, not in
this SDK source PR. Package registration in shared SDK CI remains a review item;
public SDK pipeline definitions were not changed. Loom pipeline changes are
limited to the renamed package paths and labels.
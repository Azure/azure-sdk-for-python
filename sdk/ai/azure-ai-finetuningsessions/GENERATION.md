# Generation and local review

## Reference and scope

The runtime SDK and its regression tests were ported from Loom master commit
`af8006382149c72c646d488b2bcee004767380f2`. The public TypeSpec was reconciled
with that SDK and the actual service schemas, rather than reverse-mapping only
files that happened to be different between two manually edited SDK copies.

The follow-up inference-error documentation and retry tests from
`8710e209831248a986393c2df0ee47e333d51dfa` are included as well; that follow-up
does not change the SDK runtime or raw response schema.

The feature branches incorporate their September 17 target revisions through
ordinary merge commits, without rebasing or rewriting existing history. PR
reopening and review remain separate from pushing the feature branches.

## Package identity

The distribution and SDK package directory are named
`azure-ai-finetuningsessions`. Wheels and source archives use the normalized
distribution stem `azure_ai_finetuningsessions`. The Python namespace stays
`azure.ai.finetuning_sessions`; model/client names and REST routes are unchanged.
See [installation and migration guidance](README.md#install-the-package) before
switching an environment that contains the earlier preview distribution.

The TypeSpec client project is
`specification/ai-foundry/data-plane/Foundry/src/sdk-python-azure-ai-finetuningsessions`.
Its emitter configuration sets both `package-name` and `emitter-output-dir` to
the renamed package, while explicitly retaining the existing Python namespace.
Regeneration also sets the sync/async SDK user-agent moniker to
`ai-finetuningsessions`; wire-contract tests assert that name on real outbound
requests through the offline transports.

This rename is limited to the public TypeSpec and Python SDK feature branches.
The separate Loom SDK copy, cookbook dependencies, and bundled-wheel workflows
must be migrated together in a later change; they are not changed by this PR.

## Sources

- Public spec repository: `Azure/azure-rest-api-specs`, branch
  `haarunkumar/finetuning-sessions-spec`, targeting `feature/foundry-release`.
- SDK branch: `feature/finetuning-sessions-sdk`, targeting `main`.
- The generation source is described by [tsp-location.yaml](tsp-location.yaml).
  It pins the immutable public TypeSpec commit
  `4ea1ecd5b4dfec03bfc5a5cd67d164869db95014`, including the distribution rename.
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

- Canonical public `/fine_tuning_sessions` paths replace the legacy route family.
  Gateway/RP compatibility must be deployed before exercising these clients
  against an environment that previously accepted only the legacy path.
- Raw generated responses now match HTTP 200 submissions, string `session_id`,
  `request_id`, and `pending/completed/failed` request envelopes. Generated
  `begin_*` Azure-LRO methods are replaced by the corresponding ordinary
  submission methods; no invented `Operation-Location` response is required.
- The generated optimizer operation is `training.optimizer_step`; the
  convenience `optim_step` API remains unchanged.
- The raw service requires LoRA configuration and rank. Optional convenience
  arguments are retained for compatibility; examples supply a valid rank.
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
  are preserved in [the handwritten options module](azure/ai/finetuning_sessions/_client_options.py)
  and patch modules instead of manual edits to generated configuration/initializer
  files. Guard tests exercise the supported public clients.
- Session lists return explicit page/cursor responses. The REST specification
  uses offset pagination decorators; Python disables incomplete automatic paging
  rather than silently returning only one page or inventing a `nextLink`.

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

### Local results after the distribution rename

- **485 tests passed** against both source and the wheel installed by the new
  distribution name into an isolated target directory. The installed sync/async
  clients and models retain the `azure.ai.finetuning_sessions` imports.
- **22 generated files** matched two independent pinned emissions; handwritten
  files and TypeSpec source were unchanged during verification.
- The renamed TypeSpec input fingerprint is
  `132f0aa7cc4ff9e91f772ca1af26591eda9ca687c58aef68e5ae181c710f0a77`.
- The preceding public OpenAPI validation contained **13 canonical paths / 15
  methods**, matching HTTP 200 submissions and raw request-status envelopes.
  The distribution rename does not change those contracts.
- Full Foundry compilation and Python emission were rerun successfully. Full-service
  compilation retained 29 warnings; Python emission retained 66 warnings.
- The renamed wheel and source archive contain the new distribution name in
  their filenames and metadata. The wheel contains **27 Python modules** matching
  source, includes `py.typed`, and excludes build directories and tests.
- A wheel rebuilt from the source archive has exactly the same file contents
  and metadata as the directly built wheel. The reviewed direct wheel SHA-256 is
  `21e11da1e8d2aa800c0ee45f550c3badbd88838aaebfa6303973de8db85bef47`.
- The repository's `ParsedSetup.from_path` recognizes the new distribution,
  unchanged import namespace, and `1.0.0b1` version without extra build settings.

The original unrelated shared client-tool lockfile difference was removed during
merge resolution, and the old wheel was removed from Git tracking (its local
copy was preserved). A wheel belongs in a distribution/cookbook workflow, not in
this SDK source PR. Package registration in shared SDK CI remains a review item;
no pipeline definitions were changed as part of this synchronization.
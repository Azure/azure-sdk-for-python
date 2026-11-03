# Proof only: generated Python LRO result selection

**DO NOT MERGE OR RELEASE.** Radiology Insights is retired. This is an offline
Python sync/async example for [Azure/typespec-azure#5837](https://github.com/Azure/typespec-azure/pull/5837),
not a production SDK update or evidence for any other language. Package version
1.1.0, historical release notes, samples, and the original `tsp-location.yaml`
are intentionally retained; nothing is published.

## What this proves

The public generated clients now own `begin_infer_radiology_insights`. For normal
completion, both return a typed `RadiologyInsightsInferenceResult`, including
typed `RadiologyInsightsPatientResult` children, rather than a job envelope.
The package-root and `aio` customization files retain their normal extension
hooks but no longer contain client wrappers.

At the matched TCGC baseline, the unpatched Python generator extracts `result`
but deserializes it as `RadiologyInsightsJob`. With the TCGC PR's default behavior,
it returns the complete job instead. Adding the **Python-scoped**
`@@clientLroResult(..., AzureHealthInsights.RadiologyInsightsJob.result, "python")`
selects the inference payload and its correct type without handwritten mapping.
The adjacent patch is the LRO-only overlay for the original service `client.tsp`;
its linter suppression explains the intentional preservation of this Python
return contract. It does not replace the original aliases or other decorators.

Tests use the public package imports, fake credentials, and mocked HTTP
transports. They check `PUT resource -> GET Operation-Location (running) ->
GET Operation-Location (succeeded) -> GET original resource`, callback return
values and headers, custom polling, error propagation, continuation without
another PUT, and present/missing/null results with `polling=False`.

## Inputs and exact toolchain

| Input | Revision/version |
| --- | --- |
| Service repository | `Azure/azure-rest-api-specs` |
| Service directory | `specification/ai/HealthInsights/HealthInsights.RadiologyInsights` |
| Additional directories | `HealthInsights.Common`, `HealthInsights.OpenAPI` under the same parent |
| Recorded spec commit | `69eadf978055e646bc6b0ef1fa92fdac394eaab2` |
| API version | `2024-10-01` (the checked-in SDK's actual default) |
| TCGC baseline | `770234e25dc1769494c8d7da1d4161a2f46e90ac` |
| TCGC PR head | `4bac6e7d93bb600e1ec08a26826343d2eb7575ec` |
| TypeSpec core submodule | `780c2c6a944d2f6be276b60f890854f7a18b2955` |
| SDK `tsp-client` | `@azure-tools/typespec-client-generator-cli` 0.33.1 |
| Installed Azure Python wrapper | `@azure-tools/typespec-python` 0.63.10 |
| Invoked Python frontend | `@typespec/http-client-python` 0.39.0 |
| Unchanged packaged backend | `pygen` 0.1.0 |
| Backend wheel SHA-256 | `06c7267545e58722535dc43d38c9ecedca71424efde73652e66cd2abbcdab651` |
| Generation Python | 3.12.13 |
| Generation dependencies | black 26.3.1, PyYAML 6.0.1, Jinja2 3.1.6, tomli 2.0.1, setuptools 83.0.0, docutils 0.23 |

The final reproduction uses **real SDK `tsp-client update`**, including normal
sync, `npm ci`, the Azure wrapper, native Python backend, and generated-code
formatting. `eng/emitter-package.json` was temporarily pinned to ordinary local
tarballs of **both TCGC and Azure Core**, built from the corresponding source
revision above. Recursive npm overrides make the direct service imports and
the Python frontend use the same packages. A matching emitter lock was generated
before each update; the original engineering manifest and lock were then restored
byte-for-byte. No repository-wide dependency pins or lockfiles are included here.

The **source-built TypeSpec compiler is also required** in every comparison.
Its package version is 1.17.0, but the released 1.17.0 compiler lacks
`resolveEncodedEnumMemberValue`, which this TCGC source imports. The shared
compiler tarball is built from the exact core submodule revision above. The
remaining emitter dependencies resolve normally from the SDK manifest. Matching
Azure Core packages preserve the complete branch-versus-baseline comparison;
`getLroProtocolMetadata` already exists on both source revisions.

The native backend installed by the normal frontend postinstall matches all
99 payload files in its bundled wheel. All 14 original service input files
were hash-verified before applying overlays. Module-resolution checks compare
the TypeSpec import entrypoints with the Azure wrapper's nested Python frontend
resolution, and installed custom packages are checked byte-for-byte against
their tarballs. No frontend imports or installed package sources are rewritten.

Earlier exploratory runs used a private frontend invocation, not `tsp-client`.
Those preliminary runs are not the final orchestration evidence. The real
workflow output is compared with that earlier output as an additional check;
the original `2024-04-01` cohort is not current-package compatibility evidence.

### Source-built package fingerprints

These are local packed artifacts, **not new published package versions**.

| Package / source | Version | SHA-256 |
| --- | --- | --- |
| TCGC baseline | 0.73.0 | `0dfe57a0758d0ebcc8eaba9a341afa076225441a47d458778e667ea02fb7ba3c` |
| Azure Core baseline | 0.73.0 | `da24f47db41d7a539d04e413ba23e4b986c615e2368249e0cc50d0338a04af86` |
| TCGC PR | 0.73.0 | `ba6481d8b6cfb688dc7cef696198b12385ed14755059e2c7aa621a450e4d3a55` |
| Azure Core PR | 0.73.0 | `79a02cd0d77b195fc4f1c609f532ad59cdce600df7e354d81c3ed51afe6f7262` |
| Shared TypeSpec compiler | 1.17.0 | `76739322c052d58b47908c21ed7945c6d7d4cd17ffef51c50de7c3a73ca4a223` |

## Shared compatibility overlays, separate from the selector

The following changes were applied identically to **all three** comparisons,
in isolated local service copies, without modifying upstream sources:

- Remove exactly three obsolete
  `@useDependency(Azure.Core.Versions.v1_0_Preview_2)` lines from
  `HealthInsights.OpenAPI/service.tsp`; modern Azure.Core is unversioned.
- Normalize the old nested-quoted `package-pprint-name` option to
  `Azure Health Insights - Radiology Insights` so packaging emits valid TOML.
- Append the following Python-only usage overrides to `client.tsp` to retain
  three otherwise omitted, already-public enum exports:

```typespec
@@usage(Fhir.R4.ContactPointSystem, Usage.output, "python");
@@usage(Fhir.R4.ContactPointUse, Usage.output, "python");
@@usage(Fhir.R4.ResearchStudyStatusCodeType, Usage.output, "python");
```

The initial exploratory `2024-04-01` generation was **not integrated**: it would
have downgraded the actual SDK's default and removed newer public models.
The integrated `2024-10-01` generation retains all 81 existing model/enum export
names. This check is not a complete public-API compatibility assessment.

Generation options: namespace `azure.healthinsights.radiologyinsights`,
flavor `azure`, package mode `dataplane`, package version `1.1.0`,
API version `2024-10-01`, packaging enabled, sample/test scaffolding disabled,
`clear-output-folder: false`, and private output folders. The final workflow
does **not** use `emit-yaml-only` or `--skip-install`. Native generation runs
pygen `PreProcessPlugin` and `CodeGenerator`, followed by the frontend's normal
Black fast-mode/line-length-120 formatting and generated pylint-header pass.
The preliminary direct-backend comparison also ran the unchanged bundled
`BlackScriptPlugin` consistently on all variants, with Linux newlines to avoid
double CR translation on Windows. That separate invocation is not presented
as the final `tsp-client` execution path. No generated return annotations,
callbacks, or lint headers were edited by hand.

The first implementation commit modernizes the baseline generator output while
retaining both existing wrappers. It introduces generated TypedDicts and model
utilities, adopts generated `pyproject.toml` packaging, and intentionally raises
minimums from Python 3.9 to **Python >=3.10**, and from azure-core 1.30.0 to
**azure-core >=1.37.0**. Original conda settings are preserved. The next commit
contains only selected generation and wrapper removal (including generated FHIR
constructor/TypedDict additions and APIView mapping changes). A separate cleanup
commit completes the bundled formatter stage and removes the obsolete generated
root `_model_base.py`: its only remaining importers were the removed wrappers,
and new generated models use `_utils/model_base.py`. Inspect the selector commit
to separate selector effects from generator modernization and cleanup.

## Reproducing the real SDK workflow

Build and pack the TCGC and Azure Core workspace packages from each pinned
`Azure/typespec-azure` revision using that repository's pinned tools and normal
build/`pnpm pack` procedures. Build and pack the compiler once from the pinned
core submodule. Do not use a monorepo-root GitHub branch URL as an npm subpackage
dependency, publish the packages, or substitute released packages with matching
version labels.

Use separate, disposable service copies from the recorded
`Azure/azure-rest-api-specs` revision. Retain the three original directories and
their relative layout inside a local Git repository, because `--local-spec-repo`
finds additional directories from that repository root. Apply the shared
overlays above to each copy. Only the selected copy additionally receives
`client-lro-result.patch`; do not apply that selector to baseline/default.
Use `git -C <isolated-spec-copy> apply --ignore-space-change <patch-path>` to
allow LF/CRLF context differences between the two checkouts.

Install the SDK repository's `eng\common\tsp-client` dependencies. With
PowerShell 7, run the adjacent helper once per cohort:

```powershell
.\sdk\healthinsights\azure-healthinsights-radiologyinsights\tests\unit\lro_result_proof\regenerate.ps1 `
  -LocalSpecDirectory <isolated-spec-copy\specification\ai\HealthInsights\HealthInsights.RadiologyInsights> `
  -TcgcArchive <matching-local-tcgc.tgz> `
  -AzureCoreArchive <matching-local-azure-core.tgz> `
  -CompilerArchive <shared-source-built-compiler.tgz> `
  -OutputDirectory <sdk-checkout\.artifacts\lro-proof\cohort>
```

Baseline uses both baseline Azure packages. Default and selected use both PR
packages. All three use the same source-built compiler, released Python
frontend/backend, shared overlays, and options. The helper temporarily updates
the actual SDK engineering manifest, regenerates its matching lock using
`tsp-client generate-lock-file`, and runs:

```powershell
node eng\common\tsp-client\node_modules\@azure-tools\typespec-client-generator-cli\dist\index.js update --output-dir <private-output> --local-spec-repo <isolated-service-directory> --emitter-options "api-version=2024-10-01;generate-test=false;generate-sample=false;clear-output-folder=false;generate-packaging-files=true" --save-inputs --no-prompt
```

Do not run parallel helpers against the same checkout: they temporarily edit
the same engineering files. Original files are restored in `finally`; keep the
saved `TempTypeSpecFiles` only as private provenance, not committed artifacts.
The helper generates into `.artifacts` rather than overwriting package docs.

This proof used the anonymous public registry
`https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-js/npm/registry/`
through task-local npm configuration inherited by subprocesses. Global/user
authentication settings and TLS verification were not changed. Set
`AUTOREST_PYTHON_EXE` to the intended Python executable. On this machine uv's
TLS bootstrap failed; removing uv's directory only from the child process PATH
selected the installer's normal pip fallback. `PYTHONUTF8=1` avoided the system
GBK subprocess-decoding issue. These are environment workarounds, not emitter
source changes or skipped installation.

## Important limitations

- **Not fully drop-in compatible:** with `polling=False` and no `result` property,
  the released wrapper's `.get("result")` returns `None`, whereas the current
  Python backend's `.get("result", {})` returns an empty
  `RadiologyInsightsInferenceResult`. Explicit `null` still returns `None`.
  Tests assert this difference instead of hiding it. This pre-existing backend
  default comes from
  `core/packages/http-client-python/generator/pygen/codegen/models/response.py`
  (lines 130-134 at the pinned core revision), not from TCGC selection.
  Strict compatibility requires a separate Python-side decision/fix.
- The released async wrapper passes a wrapper instead of the pipeline client
  when resuming. It raises `AttributeError('_pipeline')` on azure-core 1.41.0.
  Generated continuation succeeds. This incidental existing bug is not a TCGC
  regression or a skipped test.
- Generator modernization changes additional public constructor/type surfaces
  and supported minimums; this is not an assertion of complete API equivalence.
- The decorator is **unreleased**, and the service overlay has no upstream spec
  PR/commit. Ordinary released-toolchain `tsp-client` cannot reproduce this yet.
  `tsp-location.yaml` still truthfully identifies the original service input,
  not the TypeSpec implementation repository. Reproduction requires the pinned
  local TCGC/Azure Core/compiler tarballs and the disclosed service overlays.
- No retired-service calls, live credentials, releases, or deployment were used.

## Focused local validation

Use an isolated Python environment and the repository's
[testing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md).
The new tests do not require a test proxy. From the repository root, with the
package installed:

```powershell
python -m pytest -q sdk\healthinsights\azure-healthinsights-radiologyinsights\tests\unit\test_lro_result.py -o asyncio_default_fixture_loop_scope=function
python -m black --check --config eng\black-pyproject.toml sdk\healthinsights\azure-healthinsights-radiologyinsights\azure sdk\healthinsights\azure-healthinsights-radiologyinsights\tests\unit
python -m mypy --python-version 3.10 --show-error-codes --ignore-missing-imports sdk\healthinsights\azure-healthinsights-radiologyinsights\azure
python -m mypy --python-version 3.10 --show-error-codes --ignore-missing-imports --check-untyped-defs --follow-imports=silent sdk\healthinsights\azure-healthinsights-radiologyinsights\samples
python -m pylint --rcfile=pylintrc --output-format=parseable sdk\healthinsights\azure-healthinsights-radiologyinsights\azure
python -m build --no-isolation --outdir <private-output-directory> sdk\healthinsights\azure-healthinsights-radiologyinsights
```

These are the underlying commands used by the repo's `azpysdk` checks, with its
Black 24.4.0, mypy 1.19.1, pylint 4.0.4 with guidelines checker 0.5.7,
pytest 8.3.5 and pytest-asyncio 0.24.0 pins.
Direct focused commands avoid installing the adjacent azure-core source omitted
from this deliberately sparse checkout. They do not execute the retired-service
sample/test suite. See the draft PR for the actual command results and any
remaining check limitations.

The same 15 tests also run at all declared runtime dependency minimums:
azure-core 1.37.0, isodate 0.6.1, and typing-extensions 4.6.0. Their pickleable
response fixtures support the older core continuation-token implementation;
no continuation test is skipped. APIView tokens are generated with the pinned
apiview-stub-generator 0.3.31. Runtime verification used Python 3.12.13, not a
Python 3.10 interpreter; the Python 3.10 syntax/type checks are not a substitute
for a complete supported-Python CI matrix.

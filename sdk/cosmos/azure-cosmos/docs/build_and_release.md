# Building and releasing the Rust-backed Azure Cosmos DB Python SDK

## Local PR #48867 integration — September 15, 2026

This section describes the local integration, not an executed pipeline or an
approved release. A **prototype** is a configuration being tried before release;
**CI** means continuous integration, the automated build-and-test process.
The user approved the needed CI-file changes. The required SDK and Central
parts of PR #48867 are now integrated locally, preserving the existing SDK,
generic pipeline approval logic, and local work rather than copying all newer
Central infrastructure. These changes have **not been committed, pushed, or
used to queue a pipeline run**.

The reference is PR commit `9eb4e5f49c15903af89bc9df58c43d45bfb63beb`,
compared with base `b67336fba5f8d41b82dc9b810ecf7713aea02d05`; the local
integration started at Python commit `a7b5972`. The changes below describe
the completed local integration and its bounded validation evidence. A local
Windows build is not evidence that the shared pipeline or all five targets
work.

### What changes, and why

Paths in the SDK rows are relative to `sdk/cosmos/azure-cosmos/`.
The Cosmos SDK team owns `sdk/cosmos/`; Central owns shared `eng/` infrastructure.

| Owner and files | What changes | Why it is needed |
|---|---|---|
| SDK: `pyproject.toml`, `setup.py` | Add Python `[project]` metadata for `azure-cosmos` version `4.17.1`, matching `_version.py`; preserve dependencies and optional extras; align both Python minimums to 3.10 | Maturin must package the Python SDK identity, not the internal Rust crate's name/version. This prototype deliberately no longer supports Python 3.9 |
| SDK: `pyproject.toml` | Keep the custom backend and Maturin module settings; pin `maturin==1.15.0`, enforce `locked = true`, and exclude stale locally built extensions and Python bytecode | Keep the existing packaging behavior while preventing an old local binary from contaminating another target's wheel; fail instead of silently changing Rust dependencies |
| SDK: `pyproject.toml`, `tests/common/test_build_configuration_unit.py` | Explicitly include `rust-toolchain.toml` and `scripts/*.sh` in source distributions, retain the existing backend inclusion, and add a configuration test for those rules | Reconciliation beyond the earlier prototype: inspecting the first source archive found the new, not-yet-Git-tracked setup files missing even though archive creation succeeded |
| SDK: `pyproject.toml`, `azure_cosmos_rust/Cargo.toml` | Select `cp310-*` builds and PyO3 `abi3-py310` | Use CPython's stable application binary interface (ABI), the rules for calling compiled code, starting at Python 3.10; one wheel per operating system/processor can serve later compatible CPython versions, subject to testing |
| SDK: both `Cargo.toml` files | Declare one shared Git driver revision in the root workspace and reuse it for normal and development dependencies; retain normal `fault_injection`, development `__internal_in_memory_emulator`, and native query planning | A clean build must not need a neighboring Rust checkout, and tests must not select a different driver or lose existing capabilities |
| SDK: root `Cargo.toml`, `Cargo.lock` | Remove the unused `azure_identity` neighboring path; regenerate the lock with Cargo while retaining existing versions where possible | Avoid importing an unused Git dependency and make source selection reproducible; review the actual lock changes rather than silently updating during a locked build |
| SDK: `rust-toolchain.toml`, `scripts/install-msrustup.sh`, `scripts/configure-cargo-feed.sh` | Select internal `ms-prod-1.97` with `profile = "minimal"` and add prototype toolchain/feed setup scripts | Build machines need the selected compiler and authenticated dependency source. These are prototype scripts, not customer installation requirements |
| SDK: `tests/common/test_build_configuration_unit.py` | Check version/metadata agreement with `setup.py`, exactly five configured targets, shared normal/development driver source and features, and the matching lock entry | Catch configuration drift before a costly native build; these checks complement rather than replace wheel and runtime tests |
| SDK: `azure_cosmos_rust/README.md` | Explain the current Git pin, Python 3.10 minimum, and toolchain setup while preserving existing local documentation changes | Keep binding development instructions consistent with the integrated configuration |
| Central: `eng/pipelines/templates/stages/cosmos-sdk-client.yml`, reached from SDK `sdk/cosmos/ci.yml` | Enable platform wheel generation and request Rust installation through the shared pipeline | The package configuration alone cannot start the required platform jobs; the existing SDK entry point already extends the Cosmos template |
| Central: `eng/tools/azure-sdk-tools/ci_tools/parsing/parse_functions.py` and `sdk_build` | Detect `[tool.cibuildwheel]` independently of setuptools `ext_modules`, and route those packages through `cibuildwheel`, the tool coordinating platform wheel builds | A Maturin extension is not declared as a setuptools extension; the old detection otherwise chooses the wrong build path |
| Central: shared stage, job, and build-step templates | Pass `installRust` settings through every layer; use `install-msrust-toolchain.yml` and the feed/authentication task chain | A request in the Cosmos YAML must reach the step that installs the compiler and grants build-time feed access |
| Central: platform build setup | Supply Windows ARM64 Rust target/Python library-directory settings and forward required build environment settings into Linux containers | Cross-compilation and container builds do not automatically inherit the host's full setup |
| Central: build timeouts | Allow 240 minutes per build job and 210 minutes for the package-generation step | Rust compilation must fit inside both the step and enclosing job limits |
| Central: parser/build regression tests | Exercise the real Cosmos package through `ParsedSetup`, the shared package-configuration reader, as well as the build routing | Verify that Central reads the Python package name, version matching `_version.py`, Python 3.10 minimum, project metadata, and `cibuildwheel` selection rather than treating it as a legacy pure-Python package |

The Central integration changes 10 files: six pipeline files, including the
new Microsoft Rust installation template, the parser and build implementation,
and two test files. It includes the required prototype build changes without
replacing the checkout's existing generic approval logic.

The shared infrastructure already has Windows, Linux, and macOS jobs,
`cibuildwheel==2.23.3`, Linux QEMU emulation (software running ARM64 code on
an x64 machine), Windows CPython caching, macOS ARM64 agents, and artifact
folders `packages_linux`, `packages_mac`, and `packages_windows`. Those are
existing facilities being reused, not newly implemented by this integration.

### Scope and deliberate differences from the earlier prototype

The local target set is **CPython 3.10+**, with five wheels: Windows x64 and
ARM64, Linux x64 and ARM64, and macOS ARM64. Both Linux architectures use
`manylinux_2_28`, meaning a glibc 2.28 compatibility baseline. Intel macOS,
musllinux, PyPy, and Python 3.9 are outside this experiment. Central's earlier
build log names a `macosx_11_0_arm64` wheel. The new branch's actual macOS
artifact and the final supported minimum still need validation.

The older prototype pinned driver revision `658f396` (driver `0.7.0`).
The local integration instead pins
`075917d6cb987055dfa93e31296b261574456b66` (driver `0.8.0`), the clean
neighboring Rust checkout's HEAD found on `origin/main`, to avoid downgrading
the user's runtime. The local root manifest and lock now record that exact
revision and driver version, and Cargo successfully fetched that exact source
from GitHub. The lock retains driver `0.8.0` and existing registry versions,
adds the Git source and `python3-dll-a` version `0.2.15`, and preserves the
existing `percent-encoding` development feature. Configuration tests pass;
native compilation and complete wheel validation are separate checks below.
This is a development Git pin, not approval of a published GA driver.
The workspace's declared compiler minimum `1.75`, the selected
`ms-prod-1.97` toolchain, and dependency compiler minimums are different
settings: a successful build with the newer toolchain would not prove 1.75
compatibility.

### Prototype choices to track before release

This table tracks intentional experiment choices and omissions so they are
not mistaken for the approved final support policy. **Configured** means the
local source selects that behavior; it does not mean a pipeline has produced
and tested the corresponding wheel.

| Prototype choice | Old baseline or difference | Why this choice was made | Status and remaining release decision |
|---|---|---|---|
| Python 3.10 minimum; `cp310-*` and `abi3-py310` | The historical Python baseline allowed 3.9; earlier examples used `cp39-abi3` | Build the requested stable-ABI experiment from CPython 3.10 without generating a separate wheel for every later compatible Python version | Configured; Python 3.9 is excluded from this experiment. Approve the final Python floor and test every version claimed as supported |
| Five platform wheels only: Windows x64/ARM64, Linux x64/ARM64, macOS ARM64 | The historical pure-Python wheel was `py3-none-any`; the earlier four-target proposal omitted Windows ARM64 | Limit the prototype to the requested operating-system/processor combinations while reusing existing build infrastructure | Configured; no Intel macOS, musllinux, or PyPy wheels. Validate all five artifacts and execution-test coverage, then approve the final platform list; do not interpret omitted targets as an approved permanent policy |
| `manylinux_2_28` for both Linux architectures | Earlier illustrative filenames used `manylinux_2_17` | Use the selected prototype build images consistently for x64 and ARM64 | Central's build logs name both `manylinux_2_28` wheels and a `macosx_11_0_arm64` wheel. Validate our branch's artifacts and approve final platform compatibility floors separately |
| Static Python project version `4.17.1` | Historical examples use `4.16.2`; absent Python metadata could expose Rust crate version `0.1.0` | Match the existing Python `_version.py` without inventing a v5 release number | Configuration tests and local Windows wheel metadata checks passed. This is not an approved v5 version; select the final release version separately |
| Git-pinned driver `075917d6cb987055dfa93e31296b261574456b66` (`0.8.0`) | The old prototype pinned `658f396` (`0.7.0`); local development previously required a neighboring checkout | Preserve the confirmed clean sibling Rust revision on `origin/main` rather than downgrade the user's runtime; let clean builds fetch the same source | Exact-source fetching and the local Windows public-compiler build passed; all-target pipeline validation remains. This is not a published GA driver selection. Normal and development dependencies share the root pin, existing features remain enabled, and the unused root `azure_identity` path is removed |
| Microsoft `ms-prod-1.97`, minimal profile, installed using `msrustup` | The pre-integration package had no toolchain file; workspace `rust-version = "1.75"` is only a declared minimum | Reuse the prototype's selected compiler and authenticated build setup | Configured; validate feed/toolchain access and approve the release compiler policy. A newer compiler build does not prove the 1.75 minimum or a public customer source-build path |
| Unsigned build outputs only | A completed public release requires approved signing, final-wheel tests, and publication | Separate wheel generation from release processing while the build path is being validated | Authenticated inspection confirms run `6780552` generated packages successfully on all three operating systems, although the overall run failed in other jobs. Artifact names and build-log wheel filenames are verified; archive contents and signatures have not been independently checked. No run of our new branch, signing, or publishing has been performed |
| QueryPlanInterop not provisioned; source-directory variable not forwarded into Linux | The planned complete wheel includes a matching QueryPlanInterop library alongside `_rust` | Proceed now with the built-in Rust planner and Gateway fallback; keep DLL packaging as a later deliverable | Deferred by agreement on September 15, 2026, not a blocker for prototype wheel generation. The inspected Windows wheel has no QueryPlanInterop files. Later obtain approved target-matching libraries, stage them into wheels, and prove the QueryPlanInterop provider actually works |
| Explicit source-archive inclusion of toolchain/setup files | The first archive omitted new untracked files even though creation succeeded | Make required build inputs independent of Git tracking and catch missing files before release | Corrected archive was regenerated and passed all 10 required-input checks. A wheel build from the extracted archive has **not** been performed; the public source-distribution policy remains undecided |
| Publishing an sdist with Rust-backed wheels | Legacy source installation primarily packages Python files; Rust source installation compiles native code on the customer's machine | Decide deliberately whether to offer and support this customer-side build path | Open release decision, not a blocker for prototype wheel generation. Confirm wheels-only versus wheels plus sdist, define a customer-accessible toolchain/dependency setup, and validate a clean source installation. See [the sdist tracking note](#sdist-tracking-note-customer-source-installation) |

### QueryPlanInterop is explicitly deferred

**Decision on September 15, 2026: include QueryPlanInterop in the wheel later,
but do not wait for it to continue the current prototype builds.** For now,
the wheel carries the built-in Rust planner and can use Gateway planning
when needed. This postpones DLL packaging; it does not remove the driver's
DLL integration or abandon the plan to ship the library.

**The local integration does not download or provision QueryPlanInterop
binaries. It also does not forward
`AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR` into Linux containers.**
The existing custom backend is unchanged: when that setting is absent, it
skips staging the separate query-planning library. Consequently a compiled
prototype wheel may contain `_rust` but lack QueryPlanInterop; the local Windows
wheel inspection below confirms exactly that omission. This is acceptable
for the agreed prototype scope, not evidence that the later DLL-packaging
work is complete. Compilation or an import check alone still does not prove
which query planner works at runtime.

Before that gap can be closed, the producing team must supply approved
libraries for each operating system and processor, matched to the driver.
Each library must be available **before** its wheel build, visible inside the
Linux container where applicable, and passed to the backend with the source
directory setting. Later validation must inspect every wheel's files and
prove QueryPlanInterop-backed planning from a clean installation. None of this deferred
work is replaced by a green build.

### Correction: local Rust planning is not QueryPlanInterop

Rust PR #5181, "Integrate local query planning", merged on September 8, 2026
as `d8dc2a4ce3adc8fcab8815f1032fda978dd15adb`. It connects a pure-Rust planner
to the production driver for eligible cross-partition queries. This planner
is compiled into the Rust driver and therefore into the Python `_rust`
extension; it does not need a separate QueryPlanInterop DLL.

Git ancestry confirms that our driver pin
`075917d6cb987055dfa93e31296b261574456b66` includes that PR. The older Central
prototype pin `658f396d722aacd8928a9018882f935d815f8bb6` does not. The Windows
wheel built during this session uses the newer pin, so its lack of the
QueryPlanInterop DLL does not mean it lacks the pure-Rust planner.

There are three ways the current driver can obtain a query plan:

| Planner | Where it runs | Needs the separate QueryPlanInterop library? |
|---|---|---|
| QueryPlanInterop | Native library loaded by the Rust driver | Yes |
| Pure-Rust planner | Code already compiled into `_rust` | No |
| Gateway planner | Cosmos DB service | No |

In the default `LocalPreferred` mode, normal plan resolution tries the enabled
QueryPlanInterop provider first, then the pure-Rust planner, then the Gateway.
The Rust planner accepts only query shapes it can handle correctly. It is not
a complete replacement for the other planners. `GatewayOnly` bypasses both
local providers. Contradictory filters can also be recognized as an empty
result before topology lookup.

This corrects the earlier explanation that "no QueryPlanInterop means every
query plan comes from the Gateway." It also changes how we must validate the
wheel: a successful local query is not proof that QueryPlanInterop was used.
The driver has separate diagnostic provider labels, `native_ffi`, `local_rust`,
and `gateway`; tests must distinguish the selected provider, not just whether
the query succeeded.

We still intend to include QueryPlanInterop in later wheels. Final platform,
binary-version, redistribution, and release approvals remain separate.
PR #5181 does not supply that binary or remove its integration.

Reference: `https://github.com/Azure/azure-sdk-for-rust/pull/5181`

### What the Rust driver does with the DLL

The driver contains code that knows how to call QueryPlanInterop, even when
the wheel does not contain the library itself. When this provider is enabled
and local planning is allowed, that code:

1. Tries to load the platform library on first use, from the configured
   directory or the operating system's normal search locations.
2. Finds its callable functions and creates a query-planning provider.
3. Passes the query and partition-key information to the library, including
   a call to `GetPartitionKeyRangesFromQuery4`.
4. Reads the returned JSON plan into the driver's own plan representation.
   The driver then executes the query; the DLL supplies the plan, not the
   results from Cosmos DB.

If this provider cannot supply a plan, normal `LocalPreferred` resolution
continues with the built-in Rust planner and then the Gateway if necessary.
The driver does not download or compile QueryPlanInterop automatically.

### Later work: include QueryPlanInterop in the wheel

Keep the existing custom backend and DLL integration for this follow-up:

| Work to do later | Why it is needed | Owner |
|---|---|---|
| Identify the binary source and approved versions | The Rust repository contains the calling code, not the compiled QueryPlanInterop library | Cosmos SDK team and QueryPlanInterop-producing team |
| Obtain the library and required companions for each selected operating system and processor | A Windows x64 DLL cannot serve a Windows ARM64, Linux, or macOS wheel | QueryPlanInterop-producing team |
| Supply the matching directory before each wheel build | The backend uses `AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR` to stage files into `azure/cosmos/.libs` | Cosmos SDK team for local builds; Central team for pipeline delivery |
| Make Linux inputs visible inside the build containers and forward the setting | A host-only path or omitted environment variable cannot supply the container build | Central team |
| Inspect and install the completed wheels, then exercise the QueryPlanInterop provider | A file in the archive, an import, or a successful pure-Rust plan does not prove the DLL loads and generates plans | Cosmos SDK team |

Until this work is complete, describe our artifacts as prototype wheels
without QueryPlanInterop, not wheels with the DLL already integrated.

### Local QueryPlanInterop discovery on September 15, 2026

No compiled QueryPlanInterop library was found in either local Cosmos
repository, including hidden and build-output files, or in the inspected
Windows search-path locations. The Rust native-test example names
`Q:\QueryPlanInterop`, but that directory was absent. No current, user-level,
or machine-level QueryPlanInterop directory setting was found.

We also inspected the loaded modules of 46 matching running Python processes.
None had QueryPlanInterop or `_rust` loaded. This is only a process snapshot:
it does not identify an active Rust-backed query workload or establish which
planner an earlier run used. No recent query-provider logs were found in the
inspected local test and Rust build-output locations.

A direct Windows `LoadLibraryA("Cosmos.QueryPlanInterop.dll")` probe, matching
the driver's default loader call, failed with error 126 from both repository
working directories using the existing Python SDK virtual environment.
That means this environment could not load the library or its dependencies;
it is not proof that no copy exists elsewhere on the machine.

The separate request to build a wheel containing QueryPlanInterop was
subsequently deferred by agreement. Locating the Windows x64 DLL and any
required companions remains a prerequisite for that future build, not a
blocker for the current prototype work. No wheel containing it has been
generated. The existing wheel without it is unchanged.

### What still needs evidence or approval

- Build and validate the remaining four targets and exercise SDK behavior on
  all five, including confirmation of the exact macOS build tag. Local Windows
  x64 packaging, clean-install imports, and configuration checks have passed
  as recorded below; they do not replace pipeline or functional validation.
- Commit and push the reviewed changes, then follow the
  [playground run steps and access requirements](V5/build-pipeline-legacy.md#7-what-running-the-pipeline-against-our-branch-means).
  No push, automatic trigger, or reproduced run is claimed here.
- Inspect the source commit, logs, five actual wheel files, tags, metadata,
  extension architectures, and clean-install tests. The Central team's
  playground run `6780552` now has authenticated setup, timeline, selected
  build-log, and artifact-list evidence. Its actual wheel archive contents
  remain uninspected; our branch still needs its own run.
- Keep final release version, platform policy, source-distribution policy,
  QueryPlanInterop completion, signing, and publication as separate release
  gates. Signing and publishing have not been done.

### Local validation recorded on September 15, 2026

- **Passed:** the final **13 SDK tests** across the existing QueryPlanInterop staging tests and
  new `tests/common/test_build_configuration_unit.py` checks. The new tests
  check version/metadata agreement with `setup.py`, exactly five configured
  targets, shared normal/development driver source, features, and lock, and
  the added source-archive inclusion rules. This supersedes the earlier
  12-test result.
- **Passed:** Central regression tests: **19 passed, 1 skipped**. The real
  Cosmos `ParsedSetup` check verifies the name, version matching `_version.py`,
  Python `>=3.10`, `is_pyproject`, and `uses_cibuildwheel` settings.
  All **six pipeline YAML files passed parsing**, and the Central diff
  passed whitespace checks. Parsing verifies file syntax, not authenticated
  pipeline execution.
- **Passed:** Cargo fetched the exact `075917d6cb987055dfa93e31296b261574456b66`
  Git source. The regenerated lock keeps the existing driver and registry
  versions apart from the added Windows import-library helper described above.
- **Passed:** `cargo +1.95 check --lib` using the Git-pinned `0.8.0` driver,
  in 5 minutes 21 seconds. This uses the installed **public Rust 1.95**
  compiler; it does not validate internal `ms-prod-1.97`, its installation,
  or its feed authentication.
- **Passed:** the final `cargo +1.95 check --lib --locked --offline` check.
  It reuses the already fetched sources and locked dependencies without
  network access or permission to rewrite the lock. It still uses public
  Rust 1.95, not the internal Microsoft toolchain.
- **Passed:** isolated `cibuildwheel==2.23.3 --print-build-identifiers`
  selected exactly the five identifiers below. These identify requested build
  environments, not generated wheel files; in particular, the macOS identifier
  does not establish a minimum-version wheel tag.

  ```text
  cp310-win_amd64
  cp310-win_arm64
  cp310-manylinux_x86_64
  cp310-manylinux_aarch64
  cp310-macosx_arm64
  ```

- **Passed:** the local Windows x64 command
  `python -m build --wheel --no-isolation`, using Maturin `1.15.0` from the
  activated validation environment and explicit `RUSTUP_TOOLCHAIN=1.95`.
  It produced `azure_cosmos-4.17.1-cp310-abi3-win_amd64.whl`, retained under
  the session's `files\prototype-wheel-check` directory. The public-compiler
  override is for local validation only, not the internal-toolchain pipeline.
- **Passed:** wheel archive checks and isolated installation/import checks,
  detailed in the table below.
- **Passed after correction:** the first companion `4.17.1`
  source distribution was created with Maturin `1.15.0`, but inspection found
  the new untracked `rust-toolchain.toml` and setup scripts missing. Explicit
  source-archive inclusion rules were added. The archive was regenerated
  and passed all **10 required-input checks**, including the backend, root
  Cargo configuration and lock, toolchain file, binding manifest, `build.rs`,
  `query_plan_binary.rs`, and both setup scripts. This proves file inclusion
  only: building a wheel from the extracted archive has **not** been performed.
- **Not performed:** a commit, push, or queued pipeline reproduction.

| Local Windows x64 check | Observed result and what it proves |
|---|---|
| Archive structure | 217 files, unique archive entries, and no Python bytecode; no duplicate packaged extension |
| Python SDK contents | Python SDK files, `py.typed`, and `query_advice_rules.json` are present |
| Compiled extension | Exactly one `azure/cosmos/_rust.pyd`, 15,114,752 bytes; its Windows binary header has machine value `0x8664`, identifying x64 |
| Installation metadata | Version `4.17.1`, `Requires-Python: >=3.10`, required dependencies, and the `aio` optional dependencies are correct; `WHEEL` records the native compatibility tag |
| QueryPlanInterop | **Zero files present**; this is an observed packaging gap, not proof of a complete release wheel |
| Clean installation | The wheel installed into an isolated environment. `python -I` imported `CosmosClient` and `_rust`, and `create_database` was callable; the extension path was inside that installed environment, not the source checkout |

The import check did not call `create_database` or run SDK functional tests.
This evidence covers **local Windows x64 with public Rust 1.95 only**. It does
not validate Microsoft Rust 1.97, the other four targets, a pipeline run,
local query planning, signing, or publication.

Activate the validation environment and verify that `maturin --version` reports
`1.15.0` before using `--no-isolation`: that option uses installed build tools
instead of creating a fresh build environment. Correct tool selection is a
reproduction prerequisite, not an outstanding repository blocker.

The source-archive correction goes beyond copying the earlier prototype:
successful archive creation was not enough. The new rules explicitly include
`rust-toolchain.toml` and `scripts/*.sh` with `format = "sdist"`, so packaging
these required setup files does not depend on their already being tracked by
Git. The custom backend's existing source-archive inclusion remains in place.

This is a dated progress checkpoint, not a claim that the experiment or release
is complete. QueryPlanInterop staging tests exercise supplied test inputs;
they do not provision approved production binaries.

The rest of this document explains the local mechanics and the still-proposed release
requirements. All `4.16.2` pure-Python examples are **historical baselines**,
not claims about the current package version or latest published release.

The legacy `azure-cosmos` baseline used here contains only Python code. Azure Cosmos DB
Python SDK v5 adds Rust code, so the release process must compile that code and
place the result in platform wheels. A platform wheel is a `.whl` file built
for one operating-system and processor combination, called a **build target**
in this document.

The `4.16.2` baseline uses these release filenames; this document does not
claim it is the latest published version:

```text
azure_cosmos-4.16.2-py3-none-any.whl
azure_cosmos-4.16.2.tar.gz
```

The wheel can be used across operating systems and processors because it
contains no compiled target-specific code.

The proposed v5 release instead contains a compiled Python extension:

```text
Windows:       azure/cosmos/_rust.pyd
Linux/macOS:   azure/cosmos/_rust.abi3.so
```

This extension contains compiled code from two Rust crates. Cargo is the Rust
build tool that downloads dependencies and starts the Rust compiler. A
**crate** is a Rust source project that Cargo can compile:

- `azure_cosmos_rust`, the Python-facing binding stored in
  `azure-sdk-for-python`;
- `azure_data_cosmos_driver`, the Cosmos driver published from
  `azure-sdk-for-rust`.

Because the extension contains machine code, one wheel cannot serve every
operating system and processor. The integrated prototype target list is:

```text
Windows x64
Windows ARM64
Linux x64
Linux ARM64
macOS ARM64
```

Linux ARM64 is configured for the existing emulation path. Actual builds and
tests on all five targets still need validation before release approval.

Before executing a cross-partition query, the SDK needs a query plan: the list
of partitions to contact and the work to perform on the combined results.
QueryPlanInterop is a separate compiled library that can create that plan on
the customer's machine. The pinned driver also includes a pure-Rust planner
for eligible queries. When local providers cannot supply a plan, or
`GatewayOnly` is selected, the driver asks the Cosmos DB Gateway for it.

Every official v5 platform wheel must include the QueryPlanInterop library
built for the same target and must support local query planning.

This is a proposed release requirement, not a claim that the current backend
rejects every wheel missing that library. The backend permits omission when
its source-directory setting is unset.

Read [the existing pipeline overview](V5/build-pipeline-legacy.md) first for
the separate validation, live-test, and release paths. This document then
explains the transition to Rust-backed packages. Repository observations
describe the working checkout reviewed during these lessons, not every branch
or the final release configuration.

### Is the Rust setup still missing?

**No: the Rust setup is already enabled in our working-copy Cosmos template.**
Enabling it means running the compiler-installation steps before building
the Python extension.

The starting YAML, `sdk/cosmos/ci.yml`, extends the Central-owned
`eng/pipelines/templates/stages/cosmos-sdk-client.yml`, where we set:

```yaml
InstallMsRustToolchain: true
```

The verified playground entry point uses this chain. We do not need a
different YAML connection for Rust; the edited template must be committed
and pushed so the pipeline can use it.

Pipeline registration, manual queuing, feeds, permissions, and the verified
playground settings are explained in the
[legacy pipeline foundations](V5/build-pipeline-legacy.md#concept-1-from-github-code-to-an-azure-devops-pipeline-run).

### Prototype evidence and remaining validation

Run `6780552` was manually started on September 2, 2026, from
`refs/heads/djurek/rust-driver-engsys-prototype`, using commit
`9eb4e5f49c15903af89bc9df58c43d45bfb63beb`. It used definition revision `2`,
the same revision returned by the authenticated setup check documented in
the legacy pipeline guide.

Its **overall result was failed**, not wholly successful. However,
`Build_Linux`, `Build_MacOS`, and `Build_Windows` all succeeded. Each completed
the Rust installation, Cargo feed authentication, and `Generate Packages`
steps. The three package artifacts were published successfully. Other jobs,
including Build Extended, Build Docs, and tests, failed.

This independently supports Central's claim that wheel generation worked;
it does not establish that the complete pipeline or functional tests passed.
The new branch still needs its own run. Feed access and queue permissions
are covered in the [pipeline foundations](V5/build-pipeline-legacy.md#8-feeds-and-permissions-what-the-build-can-download).

| Published artifact | Cosmos wheel filenames named in its generation job's log |
|---|---|
| `packages_windows` | `azure_cosmos-4.16.2-cp310-abi3-win_amd64.whl`, `azure_cosmos-4.16.2-cp310-abi3-win_arm64.whl` |
| `packages_linux` | `azure_cosmos-4.16.2-cp310-abi3-manylinux_2_28_x86_64.whl`, `azure_cosmos-4.16.2-cp310-abi3-manylinux_2_28_aarch64.whl` |
| `packages_mac` | `azure_cosmos-4.16.2-cp310-abi3-macosx_11_0_arm64.whl` |

The Linux log also contains intermediate `linux_x86_64` and `linux_aarch64`
wheel names. The table records the manylinux names, not seven final targets.
The artifact list and log filenames were read; the remote wheel archives
were not downloaded or opened. Their contents remain a separate check.
Version `4.16.2` belongs to Central's earlier run, not our current `4.17.1`
package configuration.

The immediate goal is unsigned generation and packaging with the integrated
changes, followed by a reviewed push and a playground run against that branch.
Confirm the source commit, five-target wheel set, filenames and metadata,
Python files, and matching Rust extension. QueryPlanInterop provisioning and
its Linux environment forwarding are explicitly deferred, so complete
release-wheel contents cannot yet be claimed. A green job or an artifact-folder
name alone does not establish these properties.

Use the [manual run instructions](V5/build-pipeline-legacy.md#7-what-running-the-pipeline-against-our-branch-means)
for branch selection and queue access. The distinction between the normal
public pipeline and the playground belongs in that foundational guide.

The second goal is clean installation and functional tests, including
evidence of actual local query planning rather than only importing `_rust`.
Signing and publication are later goals. These unsigned prototype artifacts
are not approved for public release. Central `eng/` changes may contain
required build fixes even though the PR author's SDK review request focused
on `sdk/cosmos/`; do not blindly omit them or overwrite local work.

References:

- `https://github.com/Azure/azure-sdk-for-python/pull/48867`
- `https://dev.azure.com/azure-sdk/playground/_build/results?buildId=6780552&view=results`

## Terminology used throughout

| Term | Meaning |
|---|---|
| **PyPI project** | `azure-cosmos` across all versions published under that name on the Python Package Index (PyPI) |
| **Release** | One version of the PyPI project, such as `azure-cosmos <version>`, including all files published for that version |
| **Build output** | A wheel or sdist created by a build but not necessarily published |
| **Release file** | A platform wheel or sdist after it is published as part of a release |
| **Platform wheel** | A `.whl` file containing compiled code for one build target |
| **Source distribution (sdist)** | A `.tar.gz` file containing source and build instructions |
| **`azure.cosmos` Python package** | The importable Python files installed under `azure/cosmos/` |
| **Package source directory** | The repository directory `sdk/cosmos/azure-cosmos/` |
| **Rust binding crate** | `azure_cosmos_rust`, which exposes Rust operations to Python |
| **Rust driver crate** | `azure_data_cosmos_driver`, which implements the Cosmos operations used by the binding |
| **Compiled Python extension** | `_rust.pyd` on Windows or `_rust.abi3.so` on Linux and macOS |
| **QueryPlanInterop library** | The separate `.dll`, `.so`, or `.dylib` used for local query planning |
| **Build target** | One operating-system and processor combination, such as Windows x64 |
| **CPython** | The standard Python implementation used for the proposed wheels |
| **`pip`** | The Python installation tool that selects and installs a compatible wheel or sdist |
| **CI artifact** | A build output saved internally by continuous integration (CI) but not published to customers |

The following ownership terms are also used consistently:

| Role | Responsibility |
|---|---|
| **Cosmos SDK team** | Owns the package source directory, build configuration, and SDK-owned tests |
| **Rust driver team** | Publishes the approved Rust driver crate |
| **QueryPlanInterop-producing team** | Builds and supplies the QueryPlanInterop libraries; the identity of this team is not yet confirmed |
| **Shared Azure SDK pipeline team** | Owns the shared build and release infrastructure |
| **Repository maintainers** | Own repository-wide GitHub settings, including dependency-update automation |
| **Release approver** | The authorized person or group that approves targets, versions, sdist policy, and publication; the exact owner must be confirmed |

## Proposed release plan

This is the release destination, not an outstanding-work list for the local
prototype: metadata, development Git dependency, toolchain, and build routing
are in the integration scope above. Before the v5 release can be produced:

1. Remove Cargo dependencies on the neighboring `azure-sdk-for-rust`
   checkout.

   Change the Rust binding crate's driver dependency in
   `sdk/cosmos/azure-cosmos/azure_cosmos_rust/Cargo.toml` to an approved Rust
   driver crate version published on crates.io, the public registry from which
   Cargo downloads Rust source crates. Also remove the unused
   `azure_identity` neighboring path from
   `sdk/cosmos/azure-cosmos/Cargo.toml`.

   A generally available (GA) Python wheel and Rust binding crate must use a
   GA Rust driver crate version, not a beta or preview driver version.

   This allows clean continuous-integration (CI) machines to download the
   driver source without requiring both repositories to exist beside each
   other.

2. Complete the Python project metadata in
   `sdk/cosmos/azure-cosmos/pyproject.toml`.

   It must identify the PyPI project as `azure-cosmos`, provide the approved
   version and Python requirements, configure Maturin, and declare the
   supported build targets. Maturin is the build tool that combines the Python
   files with the compiled Python extension and creates the wheel.

3. Select the approved Rust toolchain policy for default local and CI builds.

   Record the approved toolchain channel or version in
   `sdk/cosmos/azure-cosmos/rust-toolchain.toml`. The Central Engineering
   System prototype in PR #48867 uses the internal Microsoft
   `ms-prod-1.97` channel through `msrustup`. The Central team reports a
   successful unsigned build with the prototype; the channel declaration
   alone does not prove build success or approve that
   channel for the public release. The selected compiler must not be older
   than the minimum version required by either Rust crate.

4. Supply the correct QueryPlanInterop files to each build target.

   Each job must receive files matching both its operating system and
   processor. These files are built separately; the wheel build does not
   convert one target's library into another.

5. Extend the shared Azure SDK pipeline so it recognizes `azure-cosmos` as a
   PyPI project whose source builds a compiled Python extension.

   The pipeline must start the Windows, Linux, and macOS build jobs, provide
   the selected Rust toolchain and QueryPlanInterop files, and run the wheel
   build for every supported target.

6. Apply the shared Azure SDK pipeline's approved release processing. For
   Windows and macOS wheels, the shared Azure SDK pipeline team must unpack
   the wheel, sign the `_rust` extension and any other compiled files covered
   by the approved signing policy, and repack the wheel.

   Install and test every final wheel before publication, including the
   repacked Windows and macOS wheels.

   Testing must use the final wheel—the same file customers will receive—not
   only the source checkout or an intermediate build output.

7. Publish the complete approved set of platform wheels and, if selected, the
   sdist under one `azure-cosmos` version.

   When a customer runs `pip install azure-cosmos`, `pip` selects the wheel
   matching that customer's CPython version and build target.

## Decisions still required before release

The following decisions are intentionally unresolved:

| Decision | Owner |
|---|---|
| Identify the person or group acting as release approver | Cosmos SDK team |
| Approved v5 release version | Release approver |
| Published Rust driver crate version | Rust driver team, Cosmos SDK team, and release approver |
| Minimum Rust version and approved default toolchain channel or version | Cosmos SDK team and shared Azure SDK pipeline team, based on the selected driver crate and build environment |
| QueryPlanInterop-producing team and storage location | Cosmos SDK team and release approver identify the owner; the selected QueryPlanInterop-producing team confirms the storage location |
| Matching QueryPlanInterop and Rust driver versions | QueryPlanInterop-producing team, Rust driver team, and release approver |
| Minimum supported Windows version, Linux compatibility level, and macOS version | Release approver |
| Whether v5 publishes an sdist and which tool creates it | Release approver |
| Whether a source-built wheel must include local query planning | Release approver |
| Confirm that the shared pipeline can use `cibuildwheel` Linux ARM64 emulation to build the proposed wheel and run its tests | Shared Azure SDK pipeline team and release approver |
| Dependency-update system for the Cargo files | Repository maintainers and Cosmos SDK team |
| Validate the integrated `cibuildwheel` route with the Maturin/custom backend on all five targets | Shared Azure SDK pipeline team |
| Confirm that release tooling can sign the approved platform wheels and publish them together with any selected sdist under one version | Shared Azure SDK pipeline team |
| Validate platform-generation and Rust-installation settings in the shared Cosmos template reached from `sdk/cosmos/ci.yml` | Cosmos SDK team and shared Azure SDK pipeline team |

The historical pure-Python baseline publishes an sdist. If v5 publishes one, it
must contain everything needed to build the compiled Python extension from an
unpacked archive. If v5 is wheel-only, every supported target must have a
published platform wheel.

The following sections explain the files involved, the local development build,
the CI wheel build, the files placed in each wheel, and the remaining Cosmos
SDK and shared Azure SDK pipeline work.

---

## Table of contents

- [Why both setup.py and pyproject.toml exist](#why-both-setuppy-and-pyprojecttoml-exist)
- [Local PR #48867 integration](#local-pr-48867-integration--september-15-2026)
- [Current release files and what changes in v5](#current-release-files-and-what-changes-in-v5)
- [Where the Python and Rust code lives](#where-the-python-and-rust-code-lives)
- [Files that control the Rust build](#files-that-control-the-rust-build)
- [How Cargo builds the Rust extension](#how-cargo-builds-the-rust-extension)
- [Local development build](#local-development-build)
- [Building and checking a wheel locally](#building-and-checking-a-wheel-locally)
- [What a completed wheel contains](#what-a-completed-wheel-contains)
- [How QueryPlanInterop is packaged and loaded](#how-queryplaninterop-is-packaged-and-loaded)
- [Why one release needs several wheels](#why-one-release-needs-several-wheels)
- [Decide whether v5 publishes a source distribution](#decide-whether-v5-publishes-a-source-distribution)
- [Changes owned by the Cosmos SDK team](#changes-owned-by-the-cosmos-sdk-team)
- [How the Cosmos pipeline produces the release files](#how-the-cosmos-pipeline-produces-the-release-files)
- [Service test resources do not change](#service-test-resources-do-not-change)
- [What customers install](#what-customers-install)
- [Reference terms](#reference-terms)

---


## Why both setup.py and pyproject.toml exist

`setup.py` is executable Python packaging configuration using setuptools,
the packaging library it imports. It supplies the package name, reads the
version from `azure/cosmos/_version.py`, declares Python requirements and
dependencies, and selects Python packages and data files. `MANIFEST.in`
provides additional source-distribution inclusion rules.

`pyproject.toml` was not introduced solely for Rust. TOML is a configuration
file format, not a compiler or executable script. The legacy Cosmos file
configured Azure SDK code-quality checks and Conda bundle participation:

```toml
[tool.azure-sdk-build]
mypy = true
pyright = false
pylint = true

[tool.azure-sdk-conda]
in_bundle = false
```

The local Git history inspected in the lessons records that tool-only file
on April 27, 2026 (`625741c40e`), Maturin build settings added on May 14,
2026 (`192fb91cde`), and the QueryPlanInterop backend added on July 28,
2026 (`40ed219c5c`). The tool-only file could coexist with `setup.py`
because it did not replace the package metadata.

Before this integration, the transitional checkout had no `[project]` table.
The integration adds it with version `4.17.1` and Python `>=3.10`.
The repository's
`ParsedSetup` logic in
`eng/tools/azure-sdk-tools/ci_tools/parsing/parse_functions.py` selects TOML
package metadata only when that table is populated; otherwise it selects
`setup.py`. The legacy non-extension branch of `sdk_build` invokes
`setup.py bdist_wheel` and `setup.py sdist`.

Do not confuse that repository-specific selection with Python's general
backend protocol. `python -m build --wheel` reads `[build-system]` and calls
the declared backend even without a `[project]` table. Thus two commands
could take different paths before integration:

```text
Legacy sdk_build -> setup.py -> setuptools packaging
python -m build --wheel -> custom backend -> Maturin -> Cargo
```

The local integration makes `[project]` authoritative for Maturin while
retaining the required tool settings. Central now detects `[tool.cibuildwheel]`
independently of `ext_modules` and routes the package through `cibuildwheel`,
then the custom backend and Maturin. `setup.py` remains for legacy callers,
with its minimum aligned to 3.10; it has not thereby become the native-wheel
builder. Adding Maturin settings alone would not accomplish that migration.

## Current release files and what changes in v5

The two legacy release files, the meaning of "binary distribution", Python
version checks, and customer installation from a wheel or source archive are
explained in
[Legacy release files and customer installation](V5/build-pipeline-legacy.md#legacy-release-files-and-customer-installation).
That guide uses `azure-cosmos 4.16.2` as a historical pure-Python example.

For the Rust migration, the integrated prototype uses this `[project]` setting in
`pyproject.toml`, with the retained `setup.py` aligned:

```toml
requires-python = ">=3.10"
```

This deliberately raises the experiment's minimum from the historical
Python 3.9 baseline to Python 3.10.

A Rust-backed sdist would need the Rust binding source, Cargo files, and
enough build configuration to compile the extension on the customer's
machine. Whether we publish it, and how customers obtain a compatible
toolchain, remain open items in
[the sdist tracking note](#sdist-tracking-note-customer-source-installation).

### Why the v5 wheel is different

The v5 wheel will contain `_rust.pyd` on Windows or `_rust.abi3.so` on Linux
and macOS. These files contain machine code compiled for a particular operating
system and processor.

That changes the release files as follows:

| Release area | Historical pure-Python baseline | Proposed v5 release |
|---|---|---|
| Python source | Included | Included |
| Compiled Rust extension | None | `_rust.pyd` or `_rust.abi3.so` |
| QueryPlanInterop | None | Required target-matching library under `azure/cosmos/.libs` |
| Wheel coverage | One `py3-none-any` wheel | One wheel for each supported build target |
| Source distribution | Published | Decision still required |
| Customer compilation when using a wheel | None | None |

The platform wheels are different release files after publication, but they
all belong to the same `azure-cosmos` release. `pip` chooses the wheel matching
the customer's CPython version and build target.

The next section identifies where the Python source, Rust binding, Rust driver,
and build configuration are stored.

---

## Where the Python and Rust code lives

The Python SDK and the Rust driver are maintained in separate repositories. In
the current development setup, those repositories are checked out beside each
other:

```text
source/repos/
├── azure-sdk-for-python/
│   └── sdk/cosmos/azure-cosmos/
│       ├── azure/cosmos/                  Python package
│       ├── azure_cosmos_rust/             Rust binding crate
│       │   ├── Cargo.toml
│       │   └── src/                       binding Rust source
│       ├── Cargo.toml
│       ├── Cargo.lock
│       ├── pyproject.toml
│       └── azure_cosmos_build_backend.py
│
└── azure-sdk-for-rust/
    └── sdk/cosmos/azure_data_cosmos_driver/
        ├── Cargo.toml
        └── src/                           driver Rust source
```

The `azure_cosmos_rust/` name in the diagram is a folder. That folder, its
`Cargo.toml`, and its Rust source files make up the Rust binding crate.

The Rust binding crate makes the Rust driver callable from Python. The Rust
driver crate implements the Cosmos operations used by the binding. The driver
crate stays in `azure-sdk-for-rust`; it is not copied into the Python
repository.

Before integration, the binding referred to the neighboring driver folder.
This is a historical example, not the integrated dependency:

```toml
azure_data_cosmos_driver = {
    path = "../../../../../azure-sdk-for-rust/sdk/cosmos/azure_data_cosmos_driver",
    features = ["__internal_native_query_plan"],
}
```

A Cargo **feature** is a named switch that enables optional crate code. Here,
`__internal_native_query_plan` enables the Rust driver's local-query-planning
support.

That path works only when both repositories are checked out beside each
other. The integration replaces it with a single root-workspace Git revision
inherited by both normal and development driver dependencies, preserving
`fault_injection` and `__internal_in_memory_emulator` respectively. The `0.8.0`
revision and its validation status are recorded at the top of this
document. Shared development can use either:

- a released driver version from crates.io; or
- a Git dependency pointing to a specific branch, tag, or commit in
  `azure-sdk-for-rust` when testing driver changes that have not been
  published.

For example, a development dependency pinned to a commit can use:

```toml
azure_data_cosmos_driver = {
    git = "https://github.com/Azure/azure-sdk-for-rust",
    rev = "<commit SHA>",
    features = ["__internal_native_query_plan"],
}
```

A developer may temporarily use the neighboring path as a local override, but
that checkout-specific path must not become the shared release configuration.

The release configuration must use an approved driver version published on
crates.io:

```toml
azure_data_cosmos_driver = {
    version = "<approved crates.io version>",
    features = ["__internal_native_query_plan"],
}
```

If the Python wheel and Rust binding crate are generally available (GA), this
driver version must also be GA. A GA release must not depend on a beta or
preview driver version.

crates.io provides a public crate archive containing the Rust driver crate's
`Cargo.toml` and Rust source files. It does not provide a precompiled driver
library for this build. During a release build, Cargo downloads that public
source and compiles it for the build target.

The Python repository contains the binding source and the declaration that it
depends on the driver. It does not contain a copy of the driver source or
commit generated files such as:

```text
target/
azure/cosmos/_rust.pyd
azure/cosmos/_rust.abi3.so
```

The integration also removes the root Cargo file's unused `azure_identity`
neighboring path rather than replacing it with an unused Git dependency.
The Rust binding crate does not use that workspace dependency.
No release Cargo configuration may require a path outside the package source
directory.

The next section explains the files that control which Rust source and compiler
versions are used.

---

## Files that control the Rust build

Five settings determine which Rust crates and compiler version the
build uses. `rustc` is the installed Rust compiler program.

| File or setting | Purpose |
|---|---|
| `sdk/cosmos/azure-cosmos/Cargo.toml` | Lists the Rust binding crate as the workspace member and provides settings and dependency versions that the binding can reuse |
| `sdk/cosmos/azure-cosmos/azure_cosmos_rust/Cargo.toml` | Defines the Rust binding crate, the library Cargo must create, and the Rust crates it depends on |
| `sdk/cosmos/azure-cosmos/Cargo.lock` | Records the exact direct and indirect Rust crate versions selected by Cargo |
| `rust-version` in the root `Cargo.toml` | States the oldest Rust compiler version the project promises to support |
| `sdk/cosmos/azure-cosmos/rust-toolchain.toml` | Selects `ms-prod-1.97` for the local prototype; final release policy remains separate |

Cargo calls a `Cargo.toml` file a **manifest**. In this document, it is called a
Cargo configuration file because that states its purpose more directly.

### The two Python-repository `Cargo.toml` files

The root `Cargo.toml` defines the local Rust workspace:

```toml
[workspace]
members = ["azure_cosmos_rust"]
resolver = "2"
```

This workspace currently has only one member crate. Cargo does not require a
workspace merely because a project contains one crate; the binding could
instead keep all of its settings in its own `Cargo.toml`. The current design
uses the root workspace as the package-level location for settings inherited
by the binding crate and for the shared `Cargo.lock`.

`resolver = "2"` selects Cargo's second-generation rules for combining
dependency features.

The root file provides values that the binding crate reuses:

```toml
[workspace.package]
rust-version = "1.75"

[workspace.dependencies]
azure_core = "1.1.0"
tokio = "1"
```

The Rust binding crate's `Cargo.toml` defines the binding itself and declares
its dependencies. An entry such as:

```toml
tokio = { workspace = true, features = ["rt-multi-thread", "macros"] }
```

means that the binding uses the `tokio` version declared in the root
`Cargo.toml`. Other inherited values include the Rust edition, minimum Rust
version, authors, license, and repository. The two files are therefore not
duplicates: the root file holds package-level shared settings, while the
nested file defines the actual binding crate and the library it builds.

If more Rust crates are added to this Python package later, they can be added
as additional workspace members and reuse the same package-level settings and
lock file. That future possibility is a benefit of the structure, not the
reason Cargo needs a workspace today.

### `Cargo.lock` is already checked in

The package source directory already contains:

```text
sdk/cosmos/azure-cosmos/Cargo.lock
```

The `Cargo.toml` files describe acceptable crate versions. `Cargo.lock`
records the exact versions Cargo selected, including crates required
indirectly by other dependencies. Cargo generates and updates this file; it
should not be edited manually.

Keeping the lock file in the repository gives default local and CI builds the
same starting dependency set. A dependency change that updates `Cargo.lock`
must include the changed lock file for review.

Automatic maintenance happens when Cargo runs, not as a background service:

| Situation | Normal Cargo behavior |
|---|---|
| `Cargo.lock` is missing | `cargo build` resolves dependencies and creates it |
| The existing lock satisfies the manifest | A normal build reuses locked versions |
| A manifest change requires new resolution | A normal build can update the lock file |
| New compatible releases exist upstream | A normal build does not refresh everything just because they exist; `cargo update` requests an update |
| `cargo build --locked` needs to change or create the lock | The command fails instead of rewriting it |

Cargo does not commit its changes to Git. The SDK team reviews and commits
any generated lock-file change. Also, a local path dependency is not an
immutable source snapshot: changing the neighboring driver's source can
change the build without changing its recorded version in `Cargo.lock`.

### Rust crates and the Rust compiler are different

A Rust crate contains source code and build information:

```text
Cargo.toml
src/*.rs
```

The Rust compiler is an installed program named `rustc`. It converts the `.rs`
source files into machine code. Cargo selects and downloads the required
crates, determines their build order, and starts `rustc`.

### Minimum compiler versus selected build compiler

The root `Cargo.toml` currently contains:

```toml
rust-version = "1.75"
```

This is the minimum supported Rust version: the oldest compiler the Rust
binding crate claims can build the source. It must be updated if the approved
published driver requires a newer compiler.

`rust-version` does not install or select a compiler, and declaring it does
not prove compatibility. It applies to the crate whether built locally, in
CI, or from customer source; the selected compiler and all dependencies must
satisfy the build requirements.

The local integration adds the Central PR #48867 prototype's
`rust-toolchain.toml`:

```toml
[toolchain]
channel = "ms-prod-1.97"
profile = "minimal"
```

`ms-prod-1.97` is an internal Microsoft Rust toolchain channel. It identifies
the Microsoft production 1.97 toolchain line: a coordinated bundle containing
`rustc`, Cargo, and the Rust standard library. The minor-only channel can pick
up approved point releases when the toolchain is updated, so it is not the
same as pinning one immutable compiler patch version.

`msrustup` is Microsoft's internal toolchain manager. It installs and selects
internal `ms-*` toolchain channels. Standard public `rustup` cannot resolve
`ms-prod-1.97`. The prototype therefore requires `msrustup`; its internal
installation guidance is available through `https://aka.ms/msrustup` to
authenticated Microsoft users.

`profile = "minimal"` tells the toolchain manager to install the basic
components needed for compilation: Cargo, `rustc`, and the Rust standard
library. It does not choose between a debug build and a release build.

The final release still requires an approved toolchain policy. If it retains
the internal Microsoft channel, the shared pipeline and documented developer
environment must install `msrustup`. If it changes to a public Rust toolchain,
the file and instructions must instead identify a channel or exact version
that public `rustup` can resolve.

`Cargo.lock` and `rust-toolchain.toml` therefore control different inputs:

```text
Cargo.lock
    exact Rust crate versions

rust-toolchain.toml
    selected Cargo and rustc toolchain channel or version
```

The next section explains how Cargo uses these files to compile the binding and
driver.

---

## How Cargo builds the Rust extension

Cargo begins with the Rust binding crate because that is the library being
built. Its `Cargo.toml` declares `azure_data_cosmos_driver` as a dependency, so
Cargo also includes the driver and everything the driver requires.

The **linker** is the operating-system program that combines compiled crate
output and required system libraries into one loadable file.

The build follows this order:

```text
Cargo reads the Rust binding crate's Cargo.toml and Cargo.lock
                  ↓
Cargo finds the driver and all other required Rust crates
                  ↓
Cargo starts rustc for each required crate
                  ↓
rustc compiles the Rust source into machine code
                  ↓
the linker combines the required machine code
                  ↓
one dynamic library containing the binding and driver
```

Cargo calculates the dependency order before compiling. A crate needed by
the driver is compiled before the driver, and the driver is compiled before
the binding that calls it.

The Rust binding crate's `Cargo.toml` requests this final library type:

```toml
[lib]
name = "azure_cosmos_rust"
crate-type = ["cdylib"]
```

`cdylib` tells Cargo to create a dynamic library that software outside Rust can
load. PyO3 is the Rust library that connects Rust functions and Python.
It supplies the Python initialization entry point inside that library.

The result contains the binding and driver code in one file. Customers do not
install a separate compiled Rust driver library:

```text
binding machine code
        +
driver machine code
        ↓
one compiled dynamic library
```

The same source must be compiled separately for each target. A Windows x64
build produces Windows x64 machine code; Windows ARM64, Linux x64, Linux ARM64,
and macOS ARM64 each require their own build.

Cargo writes the compiled output under `target/`. At that point it has
completed the Rust build. It has not yet given the library its Python extension
filename, installed it into a Python environment, or created a wheel.

---

## Local development build

A developer uses this build when changing and testing the Python or Rust code
locally. It installs the `azure.cosmos` Python package into a Python
environment but does not create a wheel.

### Prepare the checkout and Rust toolchain

Before running the command:

- the pinned driver source must be downloadable; the integrated Git dependency
  does not require the neighboring repository;
- when using the PR #48867 prototype configuration, `msrustup` must be
  installed so it can resolve and select the internal `ms-prod-1.97`
  toolchain declared by `rust-toolchain.toml`.

`msrustup` prepares the Rust tools; it does not compile the SDK or create the
wheel. Cargo and `rustc` from the selected toolchain perform the Rust build,
and Maturin later packages the compiled extension with the Python files.

### Activate a Python virtual environment and install Maturin

First, activate the Python virtual environment in which the SDK will be
tested.

A virtual environment provides an isolated Python installation for this
project. It tells Maturin:

- which Python interpreter the extension must work with;
- where to install the compiled extension;
- where this project's Python dependencies belong.

Without an active virtual environment, Maturin could target the machine's
system Python, encounter installation permission errors, or replace packages
used by unrelated projects.

Install Maturin in that active virtual environment:

```powershell
python -m pip install "maturin==1.15.0"
```

Confirm `maturin --version` reports `1.15.0` and `Get-Command maturin`
points into that activated environment. Installing a pinned tool in an
environment does not ensure an unactivated shell selects it.

From `sdk/cosmos/azure-cosmos`, run:

```powershell
maturin develop --release
```

Here, `--release` tells Cargo to produce an optimized Rust build. It does not
mean that an official `azure-cosmos` release is being published.

### What the command runs

```text
developer runs maturin develop --release
                  ↓
Maturin reads [tool.maturin] in pyproject.toml
                  ↓
Maturin starts the Cargo build described earlier
                  ↓
Maturin gives it its Python extension filename
                  ↓
Maturin installs the `azure.cosmos` Python package into the active environment
```

The integrated Maturin settings are in:

```text
sdk/cosmos/azure-cosmos/pyproject.toml
```

They tell Maturin:

```toml
[tool.maturin]
manifest-path = "azure_cosmos_rust/Cargo.toml"
python-source = "."
module-name = "azure.cosmos._rust"
features = ["pyo3/extension-module"]
locked = true
```

- `manifest-path` identifies the Rust binding crate that Cargo must build.
- `python-source` identifies the directory containing the `azure/cosmos`
  Python package.
- `module-name` tells Maturin that the compiled library must be importable as
  `azure.cosmos._rust`.
- `features` enables the PyO3 setting required when building a Python
  extension.
- `locked` makes the build fail if `Cargo.lock` is missing or out of date.

Maturin changes Cargo's compiled library into the filename Python expects:

| Operating system | Compiled Python extension |
|---|---|
| Windows | `_rust.pyd` |
| Linux | `_rust.abi3.so` |
| macOS | `_rust.abi3.so` |

Python code can then load it with:

```python
from azure.cosmos import _rust
```

### Why this is called an editable installation

The Python `.py` files continue to come from the developer's checkout rather
than from a separately copied release wheel.

Therefore:

- Python source changes are visible without rebuilding the Rust extension.
- Rust source changes require running `maturin develop --release` again.

### What this command does not do

This local command does not:

- create the final release wheel;
- call `azure_cosmos_build_backend.py`;
- add QueryPlanInterop files to a wheel;
- collect build outputs or publish release files.

The custom backend is not involved because the developer calls Maturin
directly. Its additional purpose is to place supplied QueryPlanInterop files
into wheel builds, which is part of the release-wheel process explained next.

---

## Building and checking a wheel locally

A developer uses this process to confirm that the package source directory can
produce an installable wheel for the developer's current build target. The
resulting wheel build output is for local inspection and testing. It is not a
release file and is not published.

Install the Python `build` command-line package in the active virtual
environment if it is not already available:

```powershell
python -m pip install build
```

The command is:

```powershell
python -m build --wheel
```

Unlike `maturin develop --release`, this command creates a wheel under `dist/`.
It does not install the SDK into the developer's active Python environment.

Building and installing are separate operations:

```text
Build:   source and build configuration -> dist/<wheel-name>.whl
Install: that .whl -> package files in a selected Python environment
```

After building, a developer explicitly installs the exact output with
`python -m pip install "dist\<actual-wheel-name>.whl"`. Installing build
dependencies in a temporary build environment is not the same as installing
the SDK for use. Neither operation publishes a release.

### What each build tool is

| Component | Kind and responsibility |
|---|---|
| `build` | Third-party PyPA Python command-line tool, invoked as `python -m build`; calls the configured build backend |
| `azure_cosmos_build_backend.py` | SDK-owned Python wrapper; prepares supplied QueryPlanInterop files and delegates packaging |
| Maturin | Third-party Rust/Python packaging tool and backend; invokes Cargo and assembles Python distribution files |
| Cargo and `rustc` | Tools from the selected Rust toolchain; manage dependencies and compile Rust |
| PyO3 | Rust dependency providing the Python/Rust interface, not a wheel-building command |
| `cibuildwheel` | Third-party PyPA tool used by CI to coordinate configured wheel builds and tests |

The pipeline runs installed tools; `cibuildwheel` and Maturin are not custom
Cosmos scripts. The public packaging protocol calls the initiating tool a
build frontend and the component performing the package build a build backend.

### The temporary build environment

`python -m build` creates a temporary Python environment containing the tools
needed to build the wheel. This is separate from the developer's virtual
environment:

```text
Developer's virtual environment
    runs and tests an installed SDK

Temporary build environment
    contains the tools that create the wheel
```

The `[build-system]` table in `pyproject.toml` controls that temporary
environment:

```toml
[build-system]
requires = ["maturin==1.15.0"]
build-backend = "azure_cosmos_build_backend"
backend-path = ["."]
```

- `requires` installs the declared Maturin version into the temporary build
  environment.
- `build-backend` tells the Python build tool to call
  `azure_cosmos_build_backend.py`.
- `backend-path = ["."]` tells it that the backend file is in the package
  source directory.

The build therefore does not depend on an unspecified Maturin version already
installed on the developer's machine.

This is the default isolated-build behavior. Isolation supplies Python build
dependencies; it does not by itself provision a compatible Rust toolchain or
QueryPlanInterop. Maturin 1.15.0 can attempt a temporary Rust installation when
Cargo is missing, but that is separate backend behavior. Our custom wrapper
does not currently forward Maturin's `get_requires_for_build_*` callbacks,
which request the extra Python dependency for that bootstrap. We therefore
do not promise automatic Rust installation through this prototype, especially
for its internal `ms-prod-1.97` channel.

For the current build, arrange a compatible toolchain explicitly.
`[tool.maturin]` configures Maturin's behavior; `[build-system]` selects which
backend the Python build frontend calls.

### What the local wheel command runs

```text
developer runs python -m build --wheel
                  ↓
Python build creates a temporary build environment
                  ↓
the environment installs the declared Maturin version
                  ↓
Python build calls azure_cosmos_build_backend.py
                  ↓
the backend calls Maturin
                  ↓
Maturin runs the Cargo build described earlier
                  ↓
Maturin gives the library its Python extension filename
                  ↓
Maturin combines it with the Python package
                  ↓
the completed wheel is written under dist/
```

Maturin uses the same `[tool.maturin]` settings explained in
[Local development build](#local-development-build).

On Windows, the wheel contains `azure/cosmos/_rust.pyd`. On Linux and macOS,
it contains `azure/cosmos/_rust.abi3.so`.

### Adding QueryPlanInterop to a local wheel

The custom backend exists to add supplied QueryPlanInterop files to wheel
builds. To test that packaging locally, set:

```powershell
$env:AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR = "C:\path\to\queryplaninterop"
python -m build --wheel
```

An environment variable is a named setting passed to a process. This one
points to already-built library files; neither the wrapper nor Maturin builds
QueryPlanInterop from its source.

For a wheel build, `azure_cosmos_build_backend.py`:

1. checks the supplied directory;
2. temporarily copies its compiled QueryPlanInterop files into
   `azure/cosmos/.libs`;
3. asks Maturin to create the wheel; and
4. removes the temporary copies from the source checkout.

The cleanup does not remove the files already stored in the completed wheel.

If the environment variable is not set, the current backend still creates a
wheel, but it does not add QueryPlanInterop. This can be useful for testing
Gateway query planning when QueryPlanInterop is unavailable, but it cannot be
published as an official v5 release file because official wheels require
QueryPlanInterop.

Because `pyproject.toml` can name only one backend, the custom backend also
forwards sdist, editable-build, and metadata requests to Maturin. Its
additional behavior is limited to adding QueryPlanInterop files to wheel
builds.

Running `maturin build` directly would bypass this custom backend. Use
`python -m build --wheel` when checking the complete wheel-building path.

### Why use a custom backend?

A project-specific wrapper around another backend is supported by Python's
build protocol. Here it makes preparation and cleanup part of the configured
wheel-building path, instead of requiring a separate manual copy step.
Maturin still performs Rust/Python packaging.

Without that additional preparation, `[build-system]` could name
`build-backend = "maturin"` directly and omit `backend-path`. QueryPlanInterop
does not inherently require a wrapper: a different design could prepare its
files before invoking Maturin. The wrapper is this project's chosen approach,
not a general requirement for including native libraries.

That design choice is separate from release readiness. Required-file
enforcement, target compatibility, failure cleanup, and functional tests of
the final wheel still need to pass.

### Checking the locally built wheel

First, identify the wheel created under `dist/`:

```powershell
$wheel = Get-ChildItem .\dist\*.whl | Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
```

List its contents:

```powershell
python -m zipfile --list $wheel.FullName
```

The list should include:

```text
azure/cosmos/*.py
azure/cosmos/_rust.pyd              Windows
azure/cosmos/_rust.abi3.so          Linux or macOS
azure/cosmos/.libs/*                when QueryPlanInterop was supplied
azure_cosmos-<version>.dist-info/*
```

Opening the archive proves that the files were packaged. It does not prove
that the compiled libraries can load.

For that check, create a clean virtual environment, install the wheel and its
declared Python dependencies, and import the extension:

```powershell
python -m venv .wheel-test
.\.wheel-test\Scripts\python -m pip install $wheel.FullName
.\.wheel-test\Scripts\python -I -c "from azure.cosmos import _rust; print(_rust.__file__)"
```

`-I` prevents this import check from using the current source directory or
`PYTHONPATH` instead of the installed wheel. Confirm that the printed location
belongs to the clean environment. Functional tests must likewise be arranged
to avoid importing the source checkout; an editable installation is not a
substitute for this check.

The local test proves only that the compiled extension imports on the current
machine. It does not exercise all SDK behavior, validate another build target,
collect the complete release, or publish anything. Those tasks belong to the
shared Azure SDK pipeline described later.

The next section explains what each completed wheel must contain.

---

## What a completed wheel contains

A wheel is the installable file that `pip` downloads for a customer. It is a
ZIP archive with a `.whl` filename.

A proposed Windows x64 v5 wheel would be named:

```text
azure_cosmos-<version>-cp310-abi3-win_amd64.whl
```

The final release version and platform policy still require approval.
The integrated `[project]` metadata identifies `azure-cosmos` version `4.17.1`,
matching the existing Python runtime version, rather than falling back to
Rust crate `azure_cosmos_rust` version `0.1.0`. This local version is not an
approved v5 release number. The following contents describe a complete release
wheel; prototype wheels may omit the explicitly deferred QueryPlanInterop.

Opening the proposed Windows wheel should show files like these:

```text
azure/
└── cosmos/
    ├── __init__.py
    ├── cosmos_client.py
    ├── container.py
    ├── py.typed
    ├── _query_advisor/
    │   └── query_advice_rules.json
    ├── _rust.pyd
    └── .libs/
        ├── Cosmos.QueryPlanInterop.dll
        └── any additional compiled libraries required by that DLL

azure_cosmos-<version>.dist-info/
├── METADATA
├── WHEEL
└── RECORD
```

These files have different purposes:

| Wheel content | Purpose |
|---|---|
| `azure/cosmos/*.py` | Normal Python SDK source |
| Package data such as `py.typed` and query-advisor rules | Files used by typing tools or SDK features |
| `_rust.pyd` or `_rust.abi3.so` | Compiled Python extension containing the binding and Rust driver |
| `.libs/QueryPlanInterop` files | Required separate target-matching libraries used for local query planning |
| `.dist-info/` | PyPI project name, version, Python requirement, dependencies, wheel compatibility, and installed-file records |

The Python source remains as `.py` files. It is not converted into machine
code. The same wheel also contains the compiled `_rust.pyd` or
`_rust.abi3.so` extension and the required QueryPlanInterop library.

### The compiled Python extension

Each wheel contains one `_rust` extension built for that wheel's build target:

```text
Windows:       azure/cosmos/_rust.pyd
Linux/macOS:   azure/cosmos/_rust.abi3.so
```

That one file contains compiled code from both Rust crates:

```text
azure_cosmos_rust binding code
              +
azure_data_cosmos_driver code
              ↓
one Python extension
```

The customer does not install a separate Rust driver crate or compiled Rust
driver library.

### QueryPlanInterop remains a separate library

QueryPlanInterop is not linked into `_rust`. It remains a separate compiled
library under:

```text
azure/cosmos/.libs/
```

A Windows wheel contains the Windows DLL. Linux and macOS wheels contain their
matching libraries. Any additional compiled libraries required by
QueryPlanInterop must also be included or provided by the supported operating
system.

The next section explains how these files are supplied, packaged, loaded, and
checked.

### Installed project metadata

The `.dist-info` directory tells `pip` what it is installing. Its metadata
must identify:

- the PyPI project as `azure-cosmos`;
- the approved release version;
- the supported CPython versions;
- required Python dependencies such as `azure-core`;
- the wheel's Python, operating-system, and processor compatibility.

For the integrated prototype, the minimum Python requirement is:

```text
Requires-Python: >=3.10
```

It must agree with `[project]` and the retained `setup.py`; the historical
3.9 requirement does not apply to this experiment.

### What the filename tells `pip`

For this example:

```text
azure_cosmos-<version>-cp310-abi3-win_amd64.whl
```

- `azure_cosmos` identifies the `azure-cosmos` PyPI project.
- `<version>` is the approved release version.
- `cp310-abi3` identifies the Python compatibility.
- `win_amd64` means Windows x64.

`pip` compares these tags with the customer's Python installation and
machine. It will not install this Windows wheel on Linux, macOS, or a
different processor architecture.

The detailed Python-version and platform compatibility rules are covered
later. This section establishes only what must be present inside one completed
wheel.

---

## How QueryPlanInterop is packaged and loaded

**Release requirement, deferred integration work:** the existing staging and
loading code described below is retained, but this integration supplies no
QueryPlanInterop artifacts and does not forward its source-directory variable
into Linux containers. When that variable is unset, staging is skipped.
The following complete-wheel requirements are not current build guarantees.

The compiled Python extension contains the Rust binding and Rust driver. It
does not contain QueryPlanInterop, which remains a separate library:

| Operating system | Compiled Python extension | QueryPlanInterop library |
|---|---|---|
| Windows | `_rust.pyd` | `Cosmos.QueryPlanInterop.dll` |
| Linux | `_rust.abi3.so` | `libqueryplaninterop.so` |
| macOS | `_rust.abi3.so` | `libqueryplaninterop.dylib` |

Each platform wheel must contain both files for the same build target.
QueryPlanInterop may depend on additional compiled libraries; the completed
wheel must also contain any such libraries that are not supplied by the
supported operating system.

### The QueryPlanInterop source must be confirmed

The QueryPlanInterop library is not included in the
Rust driver crate downloaded from crates.io. That crate contains Rust source
and the driver code that loads QueryPlanInterop; it does not contain a
precompiled QueryPlanInterop `.dll`, `.so`, or `.dylib`.

QueryPlanInterop must be built separately for each supported build target. The
QueryPlanInterop-producing team, storage location, and version that matches the
selected Rust driver have not yet been confirmed.

Before release, the Cosmos SDK team and release approver must identify or
confirm:

- the QueryPlanInterop-producing team and build pipeline;
- the approved storage location;
- the matching QueryPlanInterop and Rust driver versions;
- the redistribution and licensing requirements, including whether each
  library must carry a digital signature identifying its approved publisher;
- how local developers obtain the files; and
- how each CI job securely downloads the correct target's build output.

Until those decisions are complete, paths shown below are examples of how an
already obtained build output is supplied to the wheel build. They do not
identify an existing approved source.

### How a release build adds the files

For an official release, each CI wheel job must receive QueryPlanInterop files
already built for that job's target. The job sets:

```
AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR=<directory containing QueryPlanInterop files>
```

No wheel build converts one target's library into another. The
QueryPlanInterop-producing team must supply every target in the approved wheel
set. For the five configured prototype targets, eventual provisioning means:

```text
Windows x64 build  -> Cosmos.QueryPlanInterop.dll
Windows ARM64 build -> Cosmos.QueryPlanInterop.dll
Linux x64 build    -> libqueryplaninterop.so
Linux ARM64 build  -> libqueryplaninterop.so
macOS ARM64 build  -> libqueryplaninterop.dylib
```

The custom build backend then:

```text
reads AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR
        ↓
requires exactly one primary QueryPlanInterop library
        ↓
temporarily copies that library and its supplied dependencies
into azure/cosmos/.libs/
        ↓
starts the Maturin wheel build
        ↓
removes only the temporary copies from the source checkout
```

The cleanup does not remove files already stored in the completed wheel.
The local command for exercising this same path is documented in
[Adding QueryPlanInterop to a local wheel](#adding-queryplaninterop-to-a-local-wheel).

Calling `maturin build` directly skips the custom backend. Official wheel
builds must therefore use the configured Python build path.

An editable local build does not package QueryPlanInterop. To use that
specific planner, the developer points the running SDK at an external library
directory:

```
AZURE_COSMOS_QUERYPLANINTEROP_DIR=<directory containing QueryPlanInterop files>
```

Without a loadable QueryPlanInterop library, eligible queries can still use
the built-in Rust planner. Queries it cannot plan fall back to the Gateway;
`GatewayOnly` requests a Gateway plan directly.

### How the build rejects the wrong compiled file

The check lives in:

```text
sdk/cosmos/azure-cosmos/azure_cosmos_rust/build.rs
sdk/cosmos/azure-cosmos/azure_cosmos_rust/query_plan_binary.rs
```

Cargo runs `build.rs` before compiling the Rust binding crate. When
QueryPlanInterop staging is active, the check:

1. requires the primary filename for the target operating system;
2. reads the operating system's compiled-file header;
3. compares the processor recorded in that header with Cargo's build target;
4. also checks the 32-bit or 64-bit class for Linux; and
5. stops the wheel build with an error when the file is invalid or does not
   match the target.

This check proves the operating system and processor recorded in the supplied
files. It does not prove that every dependent library is present or that
QueryPlanInterop can load and create a plan. Those behaviors must be tested
from the installed wheel.

### How the installed wheel finds QueryPlanInterop

The installed Python wrapper calculates the `.libs` directory beside `_rust`
and supplies that absolute directory to the Rust driver:

```
Path(_rust.__file__).resolve().parent / ".libs"
```

If the caller already supplied
`AZURE_COSMOS_QUERYPLANINTEROP_DIR`, the wrapper preserves that explicit
value. In `LocalPreferred` mode, normal plan resolution tries QueryPlanInterop,
then the built-in Rust planner, then the Gateway. An unavailable library does
not by itself force Gateway planning for every query.

### Remaining QueryPlanInterop decisions

| Decision or work | Owner |
|---|---|
| Identify the producing team, pipeline, and approved storage location | Cosmos SDK team and release approver |
| Approve matching QueryPlanInterop and Rust driver versions | Rust driver team, QueryPlanInterop-producing team, and release approver |
| Confirm redistribution, library-signing, and licensing requirements | QueryPlanInterop-producing team and release approver |
| Supply the correct files to each CI wheel job | Shared Azure SDK pipeline team |
| Provide a test-visible result that distinguishes QueryPlanInterop, pure-Rust, and Gateway planning | Rust driver team and Cosmos SDK team |
| Open, install, and exercise each completed wheel | Cosmos SDK team supplies the tests; shared Azure SDK pipeline runs them for every build target |

---

## Why one release needs several wheels

The historical pure-Python baseline uses one wheel:

```text
azure_cosmos-4.16.2-py3-none-any.whl
```

It works across supported operating systems and processors because it
contains no compiled Cosmos code.

The v5 wheel contains machine code:

```text
azure/cosmos/_rust.pyd
```

or:

```text
azure/cosmos/_rust.abi3.so
```

Machine code built for Windows x64 cannot run on Linux x64, Linux ARM64, or
macOS ARM64. Each supported build target therefore needs its own wheel.

### Configured prototype wheel set and release approval

The user-approved local experiment configures five targets:

| Operating system | Processor |
|---|---|
| Windows | x64 |
| Windows | ARM64 |
| Linux | x64 |
| Linux | ARM64 |
| macOS | ARM64 |

Linux ARM64 uses the existing
[`cibuildwheel` emulation path](#current-ci-build-machine-limit). This is a
configured build target, not evidence that its wheel or tests passed.
Windows ARM64 is also configured; a successful cross-build on x64 does not
establish execution-test coverage on ARM64.

The expected filename shapes are below, not inspected artifacts:

```text
azure_cosmos-<version>-cp310-abi3-win_amd64.whl
azure_cosmos-<version>-cp310-abi3-win_arm64.whl
azure_cosmos-<version>-cp310-abi3-manylinux_2_28_x86_64.whl
azure_cosmos-<version>-cp310-abi3-manylinux_2_28_aarch64.whl
azure_cosmos-<version>-cp310-abi3-macosx_<minimum-version-tag>_arm64.whl
```

`<minimum-version-tag>` is deliberately a placeholder, not a valid literal
wheel tag. Inspect the actual macOS build and artifact to establish it.
The local metadata version is `4.17.1`. The release approver must still approve:

- the release version;
- the minimum Linux compatibility level;
- the minimum macOS version;
- the final operating-system support statement.

Intel macOS, musllinux, and PyPy—an alternative Python implementation—are
not part of this experiment.

### Why there is not one wheel for every Python version

Without additional configuration, a compiled Python extension may require a
separate wheel for each Python version:

```text
Windows x64 + Python 3.10
Windows x64 + Python 3.11
Windows x64 + Python 3.12
Windows x64 + Python 3.13
```

Repeating that list for every build target would create many
wheels.

The binding avoids this by enabling:

```toml
pyo3 = {
    version = "0.22",
    features = ["extension-module", "abi3-py310"],
}
```

ABI means **application binary interface**: the low-level rules used when
compiled code calls CPython. `abi3` is CPython's stable ABI for extension
modules.

PyO3 generates the low-level code that lets `_rust`:

- load as a CPython module;
- receive Python values such as strings;
- return Python objects; and
- raise Python exceptions.

Without `abi3`, that generated code may be tied to one CPython version:

```text
_rust built for CPython 3.10
    → CPython 3.10 only

_rust built for CPython 3.11
    → CPython 3.11 only
```

`abi3-py310` tells PyO3 to use only the stable low-level CPython functions
available starting with Python 3.10. Those functions keep the same binary rules
in later compatible CPython versions.

On the same build target, one compiled file can therefore be tested with
several CPython versions:

```text
one cp310-abi3 _rust.pyd
    → CPython 3.10
    → CPython 3.11
    → CPython 3.12
    → CPython 3.13
```

This produces the wheel filename portion:

```text
cp310-abi3
```

One Windows x64 wheel can therefore be tested across compatible CPython
versions instead of building a separate Windows x64 wheel for each version.

### `abi3` does not declare supported Python versions

`abi3-py310` allows the same compiled `_rust` file to load on CPython 3.10 and
later compatible CPython versions. It does not decide which versions the
Azure Cosmos DB SDK officially supports.

The project metadata separately declares the minimum Python version:

```toml
[project]
requires-python = ">=3.10"
```

This becomes:

```text
Requires-Python: >=3.10
```

inside the wheel metadata.

The local experiment targets CPython 3.10 and later compatible versions.
It does not approve a final release support matrix. A later CPython version
is not automatically supported merely because `_rust` may load on it: the SDK
must test it and include it in the support policy. `requires-python = ">=3.10"`
has no upper bound, so installability does not itself mean official support.

These settings answer different questions:

| Setting | What it controls |
|---|---|
| `abi3-py310` | Allows the same compiled `_rust` file to load on CPython 3.10 and later compatible CPython versions |
| `requires-python = ">=3.10"` | Tells `pip` not to install the prototype on Python versions older than 3.10 |
| SDK support policy and tests | States which Python versions the team officially supports |

### What the Windows tag means

This filename ending:

```text
win_amd64
```

means that the wheel contains 64-bit x86 Windows machine code.

`pip` will not install it on Linux, macOS, Windows ARM64, or 32-bit Windows.
The tag does not state the minimum supported Windows version. That must be
declared separately in the SDK support policy.

The other configured Windows target uses `win_arm64`, for 64-bit ARM Windows.
It requires its own extension and matching QueryPlanInterop library.

### What the Linux tags mean

Linux operating-system releases may use different versions of system
libraries. A wheel built on a new Linux machine can accidentally depend on
system-library versions unavailable on older supported machines.

A tag such as:

```text
manylinux_2_28_x86_64
```

means:

- Linux;
- x64 processor;
- compatible with the `manylinux_2_28` rules.

Similarly:

```text
manylinux_2_28_aarch64
```

means Linux ARM64 under the same compatibility rules.

The `2_28` value refers to the minimum glibc compatibility level represented
by the wheel tag. glibc is the common C runtime library used by many Linux
operating systems. A compatible customer machine must provide glibc 2.28 or
later.

The prototype configures `manylinux_2_28` images for both Linux architectures,
not the earlier document's `manylinux_2_17` proposal. Final release policy
must still approve the oldest supported Linux environment and validate the
actual binaries. The **Linux build image** is the prepared Linux environment
used to compile the wheel and establish that compatibility level.

### What the macOS tag means

For explanation only, this hypothetical filename ending:

```text
macosx_11_0_arm64
```

means:

- macOS;
- Apple Silicon ARM64;
- macOS 11.0 as the minimum version represented by the wheel tag.

The experiment supports Apple Silicon only. Intel macOS is not included.
The `11_0` example is not the observed prototype tag or a confirmed minimum.
The **deployment target** is the minimum macOS version recorded when compiling
the wheel. Confirm the actual build setting and artifact before recording an
exact minimum here.

### QueryPlanInterop must match the same target

Each platform wheel contains two compiled components:

```text
_rust extension
QueryPlanInterop library
```

They must both match the wheel tag.

For example, a Linux ARM64 wheel needs:

```text
Linux ARM64 _rust extension
Linux ARM64 QueryPlanInterop library
```

A wheel must not combine a Windows DLL with a Linux extension or combine x64
and ARM64 files.

### How these settings are recorded

`cibuildwheel` is the tool that repeats a wheel build in the declared CPython
and build-target environments.

| Decision | Configuration location |
|---|---|
| Reuse one compiled `_rust` file across compatible CPython versions starting with 3.10 | `abi3-py310` in `azure_cosmos_rust/Cargo.toml` |
| Minimum installable Python version | `[project] requires-python` in `pyproject.toml` |
| Prototype build targets | `[tool.cibuildwheel]` settings in `pyproject.toml`; release approval remains separate |
| Minimum Windows version | SDK support policy and test matrix |
| Minimum Linux compatibility | Linux wheel build image and final manylinux tag |
| Minimum macOS version | macOS build environment and deployment target |
| Officially supported Python and operating-system versions | SDK release policy and test matrix |

The **test matrix** is the list of CPython versions and build targets on which
the shared Azure SDK pipeline runs the SDK-owned tests.

The target configuration states which wheels must be produced. It does not
create the required build machines or publish the wheels. Those
responsibilities belong to
[How the Cosmos pipeline produces the release files](#how-the-cosmos-pipeline-produces-the-release-files).

---

## Decide whether v5 publishes a source distribution

The historical pure-Python baseline includes the sdist described in
[Current release files and what changes in v5](#current-release-files-and-what-changes-in-v5).
It contains source files and build instructions rather than an already
compiled `_rust` extension.

The v5 release must decide whether it will:

1. publish the platform wheels and an sdist; or
2. publish platform wheels only.

This decision affects what happens when `pip` cannot find a wheel matching a
customer's build target.

### Sdist tracking note: customer source installation

**Status: open release decision; not an immediate wheel-generation blocker.**

Publishing a Rust-backed sdist is not just making source code available.
It exposes an installation path in which the customer's machine must build
the Rust extension before pip can install the SDK. This can happen during
an ordinary `pip install azure-cosmos` when no compatible wheel is available.

Pip normally installs the declared Maturin version into a temporary Python
build environment. A compatible Cargo/Rust compiler toolchain and the
required platform build tools must also be available. Customers do not need
our multi-platform `cibuildwheel` setup for an ordinary source installation.

Our prototype currently selects the internal `ms-prod-1.97` toolchain.
External customers cannot be assumed to have access to that toolchain or
our internal feeds. Creating an sdist successfully does not prove that
customers can install it.

To close this item:

1. The Cosmos SDK team and release approver must decide whether the release
   offers wheels only or wheels plus a supported sdist installation path.
2. If an sdist is offered, the Cosmos SDK team and Central team must define
   and document a customer-accessible toolchain and dependency setup.
3. Validate installation from the actual source archive in a clean
   environment using that setup, including successful compilation and import
   of the resulting Rust extension.

The existing archive-generation and file-inclusion checks are useful progress,
but they do not close this item. No publication policy or build configuration
is changed by recording this note.

### If an sdist is published

Suppose a customer runs:

```powershell
pip install azure-cosmos
```

on a build target for which no matching wheel exists.

If an sdist is available, `pip` may download it and try to build a wheel on
that customer's machine:

```text
pip finds no compatible wheel
              ↓
pip downloads azure_cosmos-<version>.tar.gz
              ↓
pip creates a build environment
              ↓
pip installs the declared Maturin dependency
              ↓
the custom backend calls Maturin
              ↓
Cargo and rustc compile the Rust source
              ↓
a platform wheel is built locally
              ↓
pip installs that wheel
```

This is a substantially different installation path from downloading a
precompiled wheel.

**The customer needs a Rust build environment, but not every tool used by
our multi-platform pipeline, and not every tool must be installed manually.**

| Tool or input | Customer source-install requirement |
|---|---|
| Python and pip | Required to start the installation |
| Maturin | Required during the build; pip normally installs the declared version into its temporary build environment |
| Cargo and `rustc` | A compatible Rust toolchain must be available during compilation; do not assume the current prototype can install it automatically |
| Operating-system build tools and libraries | Required as appropriate for the target and native dependencies |
| `cibuildwheel` | Not required for an ordinary pip source install; our pipeline uses it to coordinate multiple targets |
| The Python `build` package | Not required just to run `pip install`; pip can invoke the backend itself |

If build isolation is disabled, the person running the build is responsible
for arranging the Python build dependencies too. Installing Maturin with pip
is not the same as provisioning the complete platform toolchain.

The customer would need:

- a supported CPython version and `pip`;
- a Rust toolchain containing Cargo and `rustc`;
- the operating system's required linker and compiled-code build tools;
- access to crates.io or an approved internal copy of its crate sources;
- access to the driver source, including GitHub while this prototype uses a
  Git-pinned driver rather than a published registry version;
- the system libraries required by the Rust dependencies;
- matching QueryPlanInterop files if the locally built wheel must provide
  that specific planner; the pure-Rust planner does not need those files.

The exact source from which developers and customers would obtain
QueryPlanInterop is not yet confirmed.

A public source-build path cannot assume access to the internal `msrustup`
service. If an sdist includes `rust-toolchain.toml` naming `ms-prod-1.97`,
the release must document and validate an approved public-toolchain selection
or override path for customers, or choose a distribution policy that does
not promise customer source builds. This does not affect installation of an
already-built compatible wheel.

Any supported source-build path is CPython-only under the current proposal.
PyPy remains unsupported even though `requires-python` cannot distinguish
between Python implementations.

### What the v5 sdist must contain

The sdist must contain everything from the package source directory
that is needed to start a clean build:

```text
azure/__init__.py                       allows azure.cosmos to share the top-level azure namespace with other Azure SDKs
azure/cosmos/**                         Python package and package data
azure_cosmos_rust/Cargo.toml           Rust binding crate configuration
azure_cosmos_rust/build.rs             QueryPlanInterop build-time validation
azure_cosmos_rust/query_plan_binary.rs compiled-file header validation
azure_cosmos_rust/src/**               Rust binding crate source
Cargo.toml                             Rust workspace configuration
Cargo.lock                             exact Rust crate versions
rust-toolchain.toml                    selected Cargo and rustc toolchain
scripts/*.sh                          prototype toolchain/feed setup used by configured builds
pyproject.toml                         Python build and project metadata
azure_cosmos_build_backend.py          custom wheel backend
README.md                              project description; add customer source-build instructions if an sdist is published
CHANGELOG.md                           release history included in current long description
LICENSE                                Microsoft license terms referenced by project metadata
```

If the selected sdist path uses `setup.py` and `MANIFEST.in`, both files must
also be included. If the Maturin path is selected, its explicit sdist
inclusion settings must include every non-Cargo file required above.

It does not need to contain the `azure_data_cosmos_driver` source. After the
binding dependency is changed to an approved crates.io version, Cargo
downloads that public driver source during the build.

It also should not contain one target's QueryPlanInterop library as if that
file worked everywhere. A customer building a wheel with local query planning
must supply the QueryPlanInterop files matching that customer's build target.

### The legacy sdist path is not sufficient evidence for v5

The legacy sdist command is:

```powershell
python setup.py sdist
```

`setup.py` supplies the project metadata, while `MANIFEST.in` helps choose
which repository files are copied into the archive.

The legacy `MANIFEST.in` path cannot be assumed to include all binding Rust
source and Cargo files. The integrated custom backend delegates source
distribution requests to Maturin, but a complete clean-archive rebuild still
needs validation; metadata and wheel-build success alone do not establish it.

### The release sdist creation tool must be chosen

The local prototype created a source distribution with Maturin `1.15.0`,
but inspection found new untracked toolchain/setup files missing. The
integration therefore adds explicit Maturin source-archive inclusion rules
for `rust-toolchain.toml` and `scripts/*.sh`, alongside the retained custom
backend inclusion. The regenerated archive passed all 10 required-input
checks. A wheel build from the unpacked archive has not been performed, so
successful inclusion does not establish a working source-build path or
approval to publish the archive. There are two possible release paths:

| Build path | How source files are selected |
|---|---|
| Legacy `setup.py sdist` path | `setup.py`, which must read authoritative metadata from `pyproject.toml`, and `MANIFEST.in` |
| Maturin sdist path | Cargo, Maturin, and explicit Maturin inclusion settings |

These paths do not use the same file-selection rules. The release must choose
one path and configure that path completely.

The release cannot update `MANIFEST.in` and assume a Maturin sdist uses it. It
also cannot configure Maturin and assume the current `setup.py sdist` command
includes the same files.

### How to prove an sdist is complete

The completed sdist must be tested outside both repository checkouts:

```text
create the sdist
        ↓
copy it to a clean directory
        ↓
unpack it
        ↓
confirm no neighboring azure-sdk-for-rust checkout exists
        ↓
build a wheel from the unpacked archive
        ↓
open the wheel and check its contents
        ↓
install it into a clean Python environment
        ↓
import _rust and run the required tests
```

This proves that:

- the archive contains the binding source and configuration;
- the build uses the published driver rather than a neighboring checkout;
- no active Cargo dependency requires a path outside the unpacked archive;
- `Cargo.lock` and other required files are included;
- the unpacked archive can produce an installable wheel.

If local query planning is part of the source-build promise, the test must
also supply approved QueryPlanInterop files and prove that they are included
and load successfully.

### If the release is wheel-only

A wheel-only release does not publish:

```text
azure_cosmos-<version>.tar.gz
```

Customers on supported build targets receive precompiled wheels and do not need
Rust, Cargo, a linker, or QueryPlanInterop build inputs.

If no wheel matches the customer's machine, installation fails instead of
attempting an unplanned source build.

A wheel-only policy therefore requires:

- a complete wheel for every supported build target;
- clear documentation of unsupported build targets;
- release checks that fail if any required wheel is missing;
- publication tooling that does not accidentally include an incomplete
  sdist.

### Decision required before release configuration is finalized

The remaining source-distribution decisions and responsibilities are:

| Decision or work | Required answer | Owner |
|---|---|---|
| Will v5 publish an sdist? | Yes or no | Release approver |
| If yes, which tool creates it? | Legacy `setup.py` path or Maturin | Release approver |
| Does a source-built wheel promise local query planning? | If yes, define how QueryPlanInterop is obtained | Release approver |
| Which source-build targets are supported? | Explicit supported-target list | Release approver |
| Where are customer source-build requirements documented? | `README.md` | Cosmos SDK team |
| How is a clean sdist build validated? | SDK-owned test and shared Azure SDK pipeline environment | Cosmos SDK team defines the test; shared Azure SDK pipeline team runs it |

Until these decisions are made and tested, the document should describe the
v5 sdist as unresolved rather than as a guaranteed release file.

The next section lists the source files and settings that the Cosmos SDK team
must change after these release decisions are approved.

---

## Changes owned by the Cosmos SDK team

This section covers source and configuration under:

```text
sdk/cosmos/azure-cosmos/
```

These changes define the PyPI project name and metadata, its Rust and Python
dependencies, the platform wheels the release must produce, and the tests
that each installed wheel must pass.

They do not create CI build machines, collect the complete build-output set,
or publish release files. Those responsibilities belong to the shared Azure
SDK pipeline.

### Configure the driver dependency for development and release

The old checkout found the Rust driver through a neighboring repository
(historical configuration, replaced by the integration):

```toml
# sdk/cosmos/azure-cosmos/azure_cosmos_rust/Cargo.toml

azure_data_cosmos_driver = {
    path = "../../../../../azure-sdk-for-rust/sdk/cosmos/azure_data_cosmos_driver",
    features = ["__internal_native_query_plan"],
}
```

The integration declares one root `[workspace.dependencies]` Git pin and
uses `workspace = true` for the binding's normal and development driver
dependencies. Normal `fault_injection`, development
`__internal_in_memory_emulator`, and native-query-plan features are retained.
The revision recorded in the local manifest and lock is
`075917d6cb987055dfa93e31296b261574456b66` (`0.8.0`), not the old
prototype's `658f396` (`0.7.0`). Exact-source fetching and configuration tests
and local Windows wheel generation have passed. Complete-wheel functional
validation and builds on the remaining targets are still required.
The neighboring path is now only a possible developer-local override.

Before release, the shared root declaration must use an approved version
published on crates.io, while the binding continues inheriting it. For example:

```toml
# sdk/cosmos/azure-cosmos/Cargo.toml
[workspace.dependencies]
azure_data_cosmos_driver = {
    version = "<approved crates.io version>",
    features = ["__internal_native_query_plan"],
}
```

The selected version must contain the required feature, provide the behavior
needed by the Python SDK, and declare a Rust compiler requirement the Rust
binding crate can support. A GA Python wheel and Rust binding crate must use a
GA driver version rather than a beta or preview version. Git dependencies and
neighboring-repository overrides must not be included in a release.

The root Cargo configuration previously contained this unused entry:

```toml
# sdk/cosmos/azure-cosmos/Cargo.toml

[workspace.dependencies]
azure_identity = {
    path = "../../../../azure-sdk-for-rust/sdk/identity/azure_identity",
}
```

The Rust binding crate does not use this `azure_identity` entry. The integration
removes it instead of importing an unused Git dependency. The clean-build
test must still prove no active Cargo dependency needs a neighboring repository.

### Update the minimum compiler and selected toolchain settings

The minimum compiler version belongs in:

```toml
# sdk/cosmos/azure-cosmos/Cargo.toml

[workspace.package]
rust-version = "<minimum supported Rust version>"
```

This is the oldest Rust compiler the binding and selected driver promise they
can use.

The toolchain channel or version used for default local and CI builds belongs
in:

```toml
# sdk/cosmos/azure-cosmos/rust-toolchain.toml

[toolchain]
channel = "<approved toolchain channel or version>"
profile = "minimal"
```

These values do not have to be identical. The rule is:

```text
selected build toolchain >= minimum supported Rust version
```

The current working checkout declares this minimum:

```toml
# sdk/cosmos/azure-cosmos/Cargo.toml

[workspace.package]
rust-version = "1.75"
```

Separately, the toolchain file brought into this integration from the Central
prototype declares:

```toml
# sdk/cosmos/azure-cosmos/rust-toolchain.toml

[toolchain]
channel = "ms-prod-1.97"
profile = "minimal"
```

These observations are not approved release values. The minimum must be
confirmed after selecting the published driver. The compiler supplied by the
selected toolchain must be the same version as the minimum or newer.

If customer source builds are supported, CI should also test the declared
minimum compiler separately. Building default wheels with a newer toolchain
does not prove that the minimum compiler still works.

### Keep `Cargo.lock` synchronized

The lock file is already checked in at:

```text
sdk/cosmos/azure-cosmos/Cargo.lock
```

When a Rust dependency changes:

```text
change Cargo.toml
        ↓
Cargo resolves the dependency set
        ↓
Cargo.lock changes
        ↓
review and commit both files
```

The release build must use the checked-in lock file. An unexpected lock-file
change should be reviewed rather than silently accepted during publication.

Enforce that requirement in:

```toml
# sdk/cosmos/azure-cosmos/pyproject.toml

[tool.maturin]
locked = true
```

This makes Maturin pass Cargo's locked-build requirement. The build fails
instead of changing `Cargo.lock` when the lock file is missing or no longer
matches the `Cargo.toml` files. A direct Cargo command used for validation must
use the equivalent `--locked` option.

### Keep Cargo dependencies under automated review

`.github/dependabot.yml` is a repository setting that tells GitHub to monitor
dependency files and open update pull requests automatically. It is not part
of the SDK build and is not shipped to customers.

For example, if `Cargo.lock` pins `tokio` to `1.40.0` and `1.41.0` contains a
security fix, Dependabot can open a pull request updating `Cargo.lock`. CI
builds and tests the wheels before the update is approved and merged. Without
this automation, the locked versions remain unchanged until someone checks
them manually.

`locked = true` prevents builds from changing `Cargo.lock`; Dependabot instead
proposes dependency updates before a build.

The repository maintainers must confirm the dependency-update system. If
Dependabot is used, configure it to monitor:

- `sdk/cosmos/azure-cosmos/Cargo.toml`;
- `sdk/cosmos/azure-cosmos/azure_cosmos_rust/Cargo.toml`;
- `sdk/cosmos/azure-cosmos/Cargo.lock`.

The Cosmos SDK team reviews and tests these pull requests. Updates to
`azure_data_cosmos_driver` may also require Rust driver team review.

### Move authoritative Python metadata to `pyproject.toml`

The integrated Python project metadata is defined in:

```toml
# sdk/cosmos/azure-cosmos/pyproject.toml

[project]
name = "azure-cosmos"
version = "4.17.1"
requires-python = ">=3.10"
```

The experiment aligns with the existing `_version.py` value rather than
inventing a v5 release version. It raises the minimum to 3.10 and leaves no
upper Python-version bound. Installation on a later compatible CPython version
does not establish support without tests. Final release version and support
policy remain separate decisions.

The same `[project]` table preserves the existing Python project
information, including:

- dependencies such as `azure-core` and `typing-extensions`;
- optional dependencies;
- description;
- license;
- README;
- classifiers, which are standard PyPI labels such as the supported Python
  versions;
- project URLs;
- authors or maintainers.

The retained `setup.py` has the same Python 3.10 minimum. The local integration
does not claim that all remaining legacy callers or final release metadata
checks have been validated.

The Rust binding crate's internal Cargo metadata:

```toml
# sdk/cosmos/azure-cosmos/azure_cosmos_rust/Cargo.toml

[package]
name = "azure_cosmos_rust"
version = "0.1.0"
```

must not become the PyPI project name or release version.

After the metadata move:

- `[project]` in `pyproject.toml` is the authority for the PyPI project name,
  release version, Python requirement, and Python dependencies;
- `azure/cosmos/_version.py` remains the runtime version exposed by the SDK
  and must contain the same version as `[project].version`;
- an SDK-owned test must fail when those two version values differ;
- if the legacy `setup.py sdist` path is retained, `setup.py` must become a
  thin file that reads the authoritative values instead of maintaining an
  independent copy; otherwise it must not be used by the release build; and
- the version in `azure_cosmos_rust/Cargo.toml` remains internal to the Rust
  binding crate and must not supply the wheel metadata.

### Preserve the Maturin module configuration

The Maturin settings shown in
[Local development build](#local-development-build) belong in:

```text
sdk/cosmos/azure-cosmos/pyproject.toml
```

They must continue to identify the Rust binding crate, the Python source
directory, and the `azure.cosmos._rust` import path. They must also retain
`locked = true` so wheel builds reject an out-of-date `Cargo.lock`.

The configuration must preserve this name match:

```text
module-name = "azure.cosmos._rust"
                              ↓
#[pymodule]
fn _rust(...)
```

The import test must fail if these names no longer agree.

### Declare the build targets in `pyproject.toml`

The integrated target list is summarized below. This is a configuration
excerpt, not the full toolchain/environment setup or proof of passed tests:

```toml
# sdk/cosmos/azure-cosmos/pyproject.toml

[tool.cibuildwheel]
build = ["cp310-*"]
skip = ["*-musllinux*"]
test-command = "python -c \"from azure.cosmos import CosmosClient, _rust; assert _rust.create_database\""

[tool.cibuildwheel.windows]
archs = ["AMD64", "ARM64"]

[tool.cibuildwheel.linux]
archs = ["x86_64", "aarch64"]
manylinux-x86_64-image = "manylinux_2_28"
manylinux-aarch64-image = "manylinux_2_28"

[tool.cibuildwheel.macos]
archs = ["arm64"]
```

The `test-command` shown here checks imports and the presence of a Rust
entry point; it does not call that operation or prove local query planning.
The complete SDK-owned wheel tests are defined later in this section.

Both Linux build images are explicitly `manylinux_2_28` in this experiment.
Central's earlier log names a `macosx_11_0_arm64` wheel. Confirm the deployment
target and actual artifact from our branch's run rather than treating the
older filename as approval of the final release policy.
The existing Linux ARM64 emulator and Windows ARM64 cross-build setup are
reused; successful builds and tests still need evidence. QueryPlanInterop
inputs and their Linux source-variable forwarding are intentionally not
provided by this integration.

### Apply the sdist decision

If the release publishes an sdist, configure the selected creation path and
prove that the unpacked archive contains the required Python and binding Rust
source, `azure_cosmos_rust/build.rs`,
`azure_cosmos_rust/query_plan_binary.rs`, both Python-repository Cargo
configuration files, `Cargo.lock`, `rust-toolchain.toml`, `pyproject.toml`,
the build backend, and metadata files such as the README and license.

If the release is wheel-only, ensure the wheel build does not create an
incomplete sdist for publication.

The detailed choices and clean-build test are described in
[Decide whether v5 publishes a source distribution](#decide-whether-v5-publishes-a-source-distribution).

### Add SDK-owned wheel tests

Preserve the QueryPlanInterop staging, target validation, `.libs` packaging,
and cleanup behavior described in
[How QueryPlanInterop is packaged and loaded](#how-queryplaninterop-is-packaged-and-loaded).

For every supported wheel, the Cosmos SDK tests must verify:

1. The archive contains the Python source and package data.
2. The archive contains the correct `_rust` extension.
3. The archive contains the expected QueryPlanInterop files.
4. The wheel installs into a clean Python environment.
5. `from azure.cosmos import _rust` succeeds.
6. Required Rust-backed SDK operations succeed.
7. QueryPlanInterop-backed planning works when its matching library is present.
8. Pure-Rust planning works for eligible queries without QueryPlanInterop, and
   Gateway planning works for ineligible queries and in `GatewayOnly` mode.
9. Installed metadata identifies `azure-cosmos`, the correct version, and
    the correct Python requirement.

For the missing-QueryPlanInterop test, start a new process with
`AZURE_COSMOS_QUERYPLANINTEROP_DIR` pointing to an empty directory before
importing the SDK, and ensure the test environment does not expose another
QueryPlanInterop copy. This prevents the installed `.libs` directory from
being selected for that test. It does not disable the pure-Rust planner.
Use the driver's `GatewayOnly` mode for an explicit Gateway-only test, and
separately test fallback from a query the local planners cannot handle.

The Cosmos SDK team must provide a reliable test signal showing whether a
query used QueryPlanInterop, the pure-Rust planner, or the Gateway. File
presence alone does not prove which path executed.

The shared Azure SDK pipeline must:

1. run the SDK-owned tests for every build target;
2. run the same `abi3` wheel against every officially supported CPython
   version;
3. confirm that the complete approved wheel set exists;
4. confirm the approved Windows, Linux, and macOS minimum versions or
   compatibility levels;
   and
5. stop publication when any required build output or test result is missing.

### Cosmos SDK-owned change list

| Change | File or area |
|---|---|
| Configure the driver dependency for development and release, and remove neighboring-repository Cargo paths from release configuration | `sdk/cosmos/azure-cosmos/Cargo.toml` and `sdk/cosmos/azure-cosmos/azure_cosmos_rust/Cargo.toml` |
| Declare the minimum Rust compiler | `sdk/cosmos/azure-cosmos/Cargo.toml` |
| Select the approved default build toolchain channel or version | `sdk/cosmos/azure-cosmos/rust-toolchain.toml` |
| Record and enforce exact Rust crate versions | `sdk/cosmos/azure-cosmos/Cargo.lock` and `locked = true` in `sdk/cosmos/azure-cosmos/pyproject.toml` |
| Define `azure-cosmos` project metadata | `sdk/cosmos/azure-cosmos/pyproject.toml` |
| Preserve the `_rust` module configuration | `sdk/cosmos/azure-cosmos/pyproject.toml` and `sdk/cosmos/azure-cosmos/azure_cosmos_rust/src/lib.rs` |
| Declare the build-target list and import check | `[tool.cibuildwheel]` in `sdk/cosmos/azure-cosmos/pyproject.toml` |
| Test QueryPlanInterop packaging and behavior | `sdk/cosmos/azure-cosmos/azure_cosmos_build_backend.py`, `sdk/cosmos/azure-cosmos/azure_cosmos_rust/build.rs`, `sdk/cosmos/azure-cosmos/azure_cosmos_rust/query_plan_binary.rs`, and SDK-owned tests under `sdk/cosmos/azure-cosmos/tests/` |
| Apply the approved sdist or wheel-only policy | `sdk/cosmos/azure-cosmos/pyproject.toml`; `sdk/cosmos/azure-cosmos/MANIFEST.in` only for the legacy `setup.py` path; SDK-owned tests for the selected policy |

The next section explains the separate work required in the shared Azure SDK
pipeline.

---

## How the Cosmos pipeline produces the release files

This section uses two pipeline terms:

| Term | Meaning |
|---|---|
| **Cosmos pipeline** | The SDK-owned `sdk/cosmos/ci.yml` file |
| **Shared Azure SDK pipeline** | The repository-wide build and release system invoked by `sdk/cosmos/ci.yml` |

The Cosmos pipeline does not contain all build and release steps itself. It
selects the Cosmos SDK work and passes it to the shared Azure SDK pipeline.

### Current Cosmos pipeline file

The SDK-owned pipeline file is:

```text
sdk/cosmos/ci.yml
```

Its existing path filters already cover changes under:

```text
sdk/cosmos/
```

This includes changes to the `azure.cosmos` Python package, Rust source, Cargo
files, `pyproject.toml`, and `rust-toolchain.toml` in the package source
directory.

No change to those path filters is required.

The existing SDK YAML already extends
`eng/pipelines/templates/stages/cosmos-sdk-client.yml`; the platform-generation
and Rust-installation integration belongs in that shared template and its
downstream templates, rather than requiring a new SDK entry point.
The matching Central parser and
`sdk_build` changes recognize `[tool.cibuildwheel]` without depending on
setuptools `ext_modules`. Shared stage, job, and build-step templates forward
the Rust-installation request to the actual setup step. These local source
changes do not establish playground registration or guarantee an automatic
run on push; those settings must be verified separately.

### Reuse the existing `cibuildwheel` precedent

`cibuildwheel` is a third-party, open-source Python command-line tool maintained
as a Python Packaging Authority (PyPA) project. It is not a Cosmos-specific
script or an Azure DevOps service. The build environment installs it as a
Python package and can invoke it with `python -m cibuildwheel`. Its upstream
source and setup documentation are at `https://github.com/pypa/cibuildwheel`.

The shared pipeline supplies the build machines and invokes the tool.
`cibuildwheel` reads the selected build configuration, prepares the Python
build environments, invokes the package build, optionally runs configured
wheel tests, and collects the wheels. The SDK-owned custom backend and Maturin
still perform the package-specific build work; they are not replaced by
`cibuildwheel`.

The shared Azure SDK pipeline already uses `cibuildwheel` to ship the native
C-based Python Storage Extension. That implementation is the preferred
precedent for selecting build environments, collecting completed wheels, and
passing them to the existing validation and publication stages.

The local integration reuses that route and adds the needed Maturin detection,
toolchain/feed setup, environment forwarding, and timeout changes. It does
not replace the shared process or bulk-sync newer `eng/` files.
`cibuildwheel==2.23.3` was already present. A run against the integrated commit
must still validate the custom backend and all five outputs. QueryPlanInterop
provisioning remains a separate, deferred addition.

### Current CI build-machine limit

The current CI system provides these machines:

| Operating system | Processor |
|---|---|
| Windows | x64 |
| Linux | x64 |
| macOS | ARM64 |

`cibuildwheel` can use each machine differently:

- The macOS ARM64 machine builds and tests the macOS ARM64 wheel directly.
- For Linux ARM64, `cibuildwheel` can use a container and an emulator on the
  Linux x64 machine. An emulator is software that lets the x64 machine run ARM64
  code, so the ARM64 wheel can be built and its tests can execute.
- `cibuildwheel` cross-compiles the configured Windows ARM64 target on a
  Windows x64 machine. The integration supplies the Rust ARM64 target and
  Python library-directory settings. An ARM64 test environment is still
  required to establish runtime behavior; cross-compilation alone is not a test.

The existing infrastructure already supplies QEMU for Linux ARM64 emulation
and Windows CPython caching. The shared Azure SDK pipeline team must confirm
that the integrated build runs SDK-owned tests on the intended targets and,
after provisioning is added, with matching QueryPlanInterop libraries.
Producing an ARM64 wheel without running those tests does not satisfy the
release requirement.

If the emulator path is not available for the release, the release approver
must remove Linux ARM64 from the approved wheel set rather than publish an
untested wheel.

### How the declared wheel set reaches the pipeline

The preceding Cosmos SDK-owned changes section defines the integrated
`[tool.cibuildwheel]` target list in:

```text
sdk/cosmos/azure-cosmos/pyproject.toml
```

The package source directory declares the target list. The shared Azure SDK
pipeline must invoke `cibuildwheel` in the environments needed to produce the
approved platform wheels and run the SDK-owned tests.

### Pull-request and CI validation flow

```text
a file under sdk/cosmos changes and the registered trigger applies
              ↓
the registered pipeline runs sdk/cosmos/ci.yml (or is queued manually)
              ↓
the Cosmos pipeline invokes the shared Azure SDK pipeline
              ↓
the shared Azure SDK pipeline recognizes that azure-cosmos builds
a compiled Python extension
              ↓
cibuildwheel reads the target list from
sdk/cosmos/azure-cosmos/pyproject.toml
              ↓
the configured prototype wheel set is built
              ↓
the completed wheels are saved as CI artifacts
```

A pull-request or CI validation run ends with CI artifacts. It does not
publish a release. This diagram describes the intended execution, not a run
performed during the local integration. A successful native build can still
omit QueryPlanInterop while its source setting is unset.

### Release flow

An approved release run produces the complete wheel set declared in
`pyproject.toml`.

If the release policy includes an sdist, it also includes:

```text
azure_cosmos-<version>.tar.gz
```

The shared Azure SDK pipeline team must confirm that the release tooling can
process several platform wheels and any selected sdist as one release. It must
not publish only part of the approved wheel set or publish the sdist as a
separate version.

Before publication, the shared Azure SDK pipeline team performs the required
post-build signing for Windows and macOS wheels:

```text
unpack the completed wheel
        ↓
sign the _rust extension and any other compiled files required by policy
        ↓
repack the wheel
        ↓
run the SDK-owned tests against the repacked wheel
```

Signing infrastructure and credentials remain owned by the shared Azure SDK
pipeline team; they are not stored in the Cosmos package source directory.

The shared Azure SDK pipeline collects the complete set and publishes it as
one `azure-cosmos` release.

Publication must not continue if a required build output or required test
result is missing. After publication, those wheels and any selected sdist are
the release files.

### SDK-owned boundary

The Cosmos SDK team owns the package source directory:

```text
sdk/cosmos/azure-cosmos/
```

and any confirmed parameter required in:

```text
sdk/cosmos/ci.yml
```

The required Python and Rust source, project metadata, Rust settings, target
declarations, and tests were covered in the preceding sections.

The shared Azure SDK pipeline owns the repository-wide process that turns
those declarations into the complete build-output set and then publishes the
approved release files.

The shared Cosmos template and downstream flag plumbing are part of the
integration; `sdk/cosmos/ci.yml` remains the entry point. Remaining questions
concern actual pipeline registration and
execution, authenticated toolchain/feed access, complete artifacts and tests,
and the explicitly deferred QueryPlanInterop provisioning—not whether the
needed CI edits have been approved.

---

## Service test resources do not change

The test accounts are created by:

```text
sdk/cosmos/test-resources.bicep
```

The Rust-backed SDK uses the same Cosmos DB accounts, endpoints, and
authentication as the current Python SDK. Therefore, this release does not
require a change to that file.

It would need to change only if the test plan introduces a service capability
that the existing test accounts do not provide.

---

## What customers install

This section describes the proposed completed public release, not the unsigned
local prototype or the historical `4.16.2` wheel.

On a supported build target, this command:

```text
pip install azure-cosmos
```

downloads the matching platform wheel. The wheel contains the Python files,
the compiled `_rust` extension, and the Cosmos Rust driver linked into that
extension. It also contains the matching QueryPlanInterop library.

Customers installing a wheel do not need Rust, Cargo, Maturin, or a separate
Cosmos driver installation.

They also do not need `rustup`, `msrustup`, or `cibuildwheel`. They do need:

- a CPython version approved for the release;
- an operating system and processor covered by a compatible published wheel;
- an installer such as `pip` that understands the wheel's compatibility tags;
- any required operating-system runtime libraries not bundled in the wheel.

`pip` normally installs declared Python dependencies automatically.
QueryPlanInterop should be included in the proposed complete wheel, not
downloaded separately by each customer. Exact platform, Python, installer,
and system-library requirements must be established by release testing; this
document does not assert that Python 3.10 or later alone is sufficient.

If no matching wheel exists, the result depends on the approved sdist policy:

- if an sdist is published, `pip` may attempt to build the SDK locally using
  the documented build requirements;
- if the release is wheel-only, installation fails on unsupported build
  targets.

---

## Sources for packaging behavior

The repository files named above establish this checkout's configuration.
These upstream references explain the general tool behavior:

- Cargo lock-file maintenance: `https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html`
- Python build frontends, backends, and in-tree wrappers: `https://peps.python.org/pep-0517/`
- Wheel building and build isolation: `https://build.pypa.io/en/stable/how-to/basic-usage.html`
- Maturin development installs: `https://www.maturin.rs/local_development.html`
- `cibuildwheel` project and usage: `https://github.com/pypa/cibuildwheel`

## Reference terms

| Term | Plain-language meaning |
|---|---|
| **ABI** | Application binary interface: the low-level rules used when compiled code calls CPython |
| **Build image** | A prepared operating-system environment used by CI to compile a wheel |
| **`cibuildwheel`** | The tool that repeats a wheel build for declared CPython and build-target environments |
| **Deployment target** | The oldest macOS version recorded as compatible with a compiled wheel |
| **Digital signing** | Attaching verifiable publisher and integrity information to a file when required by the release policy |
| **Linker** | The operating-system program that combines compiled code into one loadable file |
| **Maturin** | The build tool that combines a Rust extension with Python files and creates Python wheels or sdists |
| **PyO3** | The Rust library that exposes Rust functions and types to CPython |
| **msrustup** | Microsoft's internal Rust toolchain manager; it installs and selects internal `ms-*` toolchain channels such as the prototype's `ms-prod-1.97` |
| **Rustup** | The public Rust toolchain manager; it installs and selects public Rust channels and versions but cannot resolve the prototype's internal `ms-prod-1.97` channel |
| **Test matrix** | The declared CPython versions and build targets on which tests must run |
| **Wheel repair** | Operating-system-specific processing that checks a compiled wheel, copies permitted dependent libraries when needed, and updates the wheel's compatibility information; whether the shared Azure SDK pipeline requires it must be confirmed there |

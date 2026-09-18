# Building and releasing the Rust-backed Azure Cosmos DB Python SDK

## Table of contents

1. [Scope and current configuration](#1-scope-and-current-configuration)
2. [Where the Python and Rust code lives](#2-where-the-python-and-rust-code-lives)
3. [Files and ownership](#3-files-and-ownership)
4. [Why both setup.py and pyproject.toml exist](#4-why-both-setuppy-and-pyprojecttoml-exist)
5. [Files that control the Rust build](#5-files-that-control-the-rust-build)
6. [How Cargo builds the Rust extension](#6-how-cargo-builds-the-rust-extension)
7. [Local development build](#7-local-development-build)
8. [Building and checking a wheel locally](#8-building-and-checking-a-wheel-locally)
9. [What a completed wheel contains](#9-what-a-completed-wheel-contains)
10. [Why one release needs several wheels](#10-why-one-release-needs-several-wheels)
11. [How QueryPlanInterop is packaged and loaded](#11-how-queryplaninterop-is-packaged-and-loaded)
12. [Decide whether v5 publishes a source distribution](#12-decide-whether-v5-publishes-a-source-distribution)
13. [How the Cosmos pipeline produces the release files](#13-how-the-cosmos-pipeline-produces-the-release-files)
14. [What customers install](#14-what-customers-install)
15. [Release readiness and remaining decisions](#15-release-readiness-and-remaining-decisions)

## 1. Scope and current configuration

This guide explains the Rust build, wheel contents, customer installation,
and remaining release work. It describes the current prototype configuration,
not an approved public release. A **prototype** is a configuration being tried
before release.

Pipeline foundations, stages and jobs, registration, branch selection,
permissions, and the legacy wheel/sdist installation flow are outside the
scope of this guide.

A **wheel** is a `.whl` archive prepared for installation. A **platform wheel**
contains compiled code for a particular operating system and processor,
called a **build target**. One `azure-cosmos` release can contain several
platform wheels, all sharing the same version.

The Rust migration changes the build from packaging Python files alone to:

```text
Python SDK files + Rust binding source + Rust driver source
    -> compile the Rust extension for one build target
    -> combine the extension with the Python files in a wheel
    -> inspect, install, and test that wheel
    -> repeat for the other targets
    -> release processing and publication after approval
```

| Setting | Current prototype configuration |
|---|---|
| Python project | `azure-cosmos`, version `4.17.1`; this is not an approved v5 release number |
| Python implementation and minimum | CPython, the standard Python implementation, starting at 3.10 |
| Build targets | Windows x64/ARM64, Linux x64/ARM64, macOS ARM64 |
| Linux compatibility | `manylinux_2_28` on both architectures |
| Python/Rust packaging tool | Maturin `1.15.0`, called through the SDK-owned custom backend |
| Rust driver | Git-pinned `azure_data_cosmos_driver` version `0.8.0`; exact revision in the root `Cargo.toml` and `Cargo.lock` |
| Selected compiler toolchain | Internal Microsoft `ms-prod-1.97`, minimal profile |
| Rust dependency control | Checked-in `Cargo.lock`; Maturin `locked = true` |
| QueryPlanInterop | Inclusion planned for later; not provisioned by the current pipeline configuration |
| Source distribution | Publication and customer source-build policy unresolved |

**QueryPlanInterop packaging is deferred, not abandoned, and is not an
immediate prototype-wheel blocker.** The current driver also has a built-in
Rust query planner and Gateway fallback; the distinction is explained in
[the QueryPlanInterop section](#11-how-queryplaninterop-is-packaged-and-loaded).

Configured targets and a successful local build do not establish release
readiness. All-target pipeline execution, functional tests, signing, and
publication still need the evidence and approvals listed in
[release readiness](#15-release-readiness-and-remaining-decisions).

## 2. Where the Python and Rust code lives

A **Rust crate** is a Rust source project that Cargo, Rust's build tool, can
compile. This SDK uses two crates with different responsibilities:

| Component | Source location | Responsibility |
|---|---|---|
| Python SDK | Python repository: `sdk\cosmos\azure-cosmos\azure\cosmos` | Python-facing SDK code |
| Rust binding crate, `azure_cosmos_rust` | Python repository: `sdk\cosmos\azure-cosmos\azure_cosmos_rust` | Makes the Rust driver's operations callable from Python |
| Rust driver crate, `azure_data_cosmos_driver` | Rust repository: `sdk\cosmos\azure_data_cosmos_driver` | Implements the Cosmos operations used by the binding |

The Python package source directory has this structure:

```text
sdk\cosmos\azure-cosmos\
    azure\cosmos\                    Python SDK and package data
    azure_cosmos_rust\
        Cargo.toml                  binding crate configuration
        build.rs                    build-time native-library checks
        query_plan_binary.rs        compiled-file header validation
        src\                        binding Rust source
    Cargo.toml                      shared Rust workspace configuration
    Cargo.lock                      exact Rust dependency selections
    rust-toolchain.toml             selected Rust tools
    pyproject.toml                  Python metadata and build settings
    azure_cosmos_build_backend.py    custom Python build backend
    scripts\                        toolchain/feed setup
```

The driver source remains in the Rust repository. The shared configuration
uses a Git revision rather than requiring a neighboring checkout. Cargo
fetches that source when it builds the binding.

A developer can use a temporary local driver override while changing both
repositories, but a shared build must not require that developer's directory
layout. The release plan calls for an approved driver version published on
crates.io, the public registry for Rust source crates. A generally available
(GA) release must use a GA driver rather than a preview driver.

The driver source is compiled into the Python extension; customers installing
a wheel do not install the driver crate separately. Generated files such as
`target\` and locally compiled `_rust` extensions are build outputs, not source
to commit.

## 3. Files and ownership

The **Cosmos SDK team** owns `sdk\cosmos`. The **Central team** owns the shared
`eng` build and release infrastructure. Shared engineering maintains
`eng\common`. Selecting a source branch selects its same-repository files,
including Central-owned templates; ownership does not make those files come
from a different branch.

Paths in the first table are relative to `sdk\cosmos\azure-cosmos`.

| SDK-owned file or area | What it controls |
|---|---|
| `pyproject.toml` | Python metadata, build backend, Maturin settings, target selection, and package-file inclusion |
| `setup.py`, `MANIFEST.in` | Retained legacy packaging configuration; not the native-wheel build path |
| `azure\cosmos\_version.py` | Runtime SDK version, which must match Python project metadata |
| `Cargo.toml` | Shared Rust settings and driver dependency source |
| `azure_cosmos_rust\Cargo.toml` | Binding library type, Rust dependencies, and Python compatibility |
| `Cargo.lock` | Exact direct and indirect Rust dependency selections |
| `rust-toolchain.toml`, `scripts\*.sh` | Selected Rust toolchain and prototype toolchain/feed setup |
| `azure_cosmos_build_backend.py` | Stages supplied QueryPlanInterop files for wheel builds and delegates packaging to Maturin |
| `azure_cosmos_rust\build.rs`, `query_plan_binary.rs` | Check staged native-library operating system and processor |
| `azure_cosmos_rust\src\lib.rs` | Python module initialization; its `_rust` name must match Maturin's module setting |
| `tests\common\test_build_configuration_unit.py` | Configuration, metadata, driver-source, target, and source-archive inclusion contracts |
| `tests\common\test_query_plan_packaging_unit.py` and other SDK tests | Packaging behavior and SDK functionality |

The SDK also owns `sdk\cosmos\ci.yml`, the pipeline entry point, and
`sdk\cosmos\test-resources.bicep`, which defines service test resources.
The Rust packaging change alone does not require different Cosmos accounts;
change test resources only if a test introduces a capability they do not
already provide.

These Central-owned paths are relative to the Python repository root:

| Central-owned file | What it controls |
|---|---|
| `eng\pipelines\templates\stages\cosmos-sdk-client.yml` | Cosmos-specific shared settings, including enabling Rust toolchain installation |
| `eng\pipelines\templates\stages\archetype-sdk-client.yml` | Shared stage composition and forwarding of build settings |
| `eng\pipelines\templates\jobs\ci.yml` | Platform build jobs and their job-level limits |
| `eng\pipelines\templates\steps\resolve-build-platforms.yml` | Platform setup, including Windows Python locations |
| `eng\pipelines\templates\steps\build-package-artifacts.yml` | Build-tool preparation, authentication, and package generation |
| `eng\pipelines\templates\steps\install-msrust-toolchain.yml` | Microsoft Rust toolchain installation |
| `eng\tools\azure-sdk-tools\ci_tools\parsing\parse_functions.py` | Reads package metadata and detects the `cibuildwheel` configuration |
| `eng\tools\azure-sdk-tools\ci_tools\build.py` | Routes compiled packages to `cibuildwheel` |
| `eng\tools\azure-sdk-tools\tests\test_build_interactions.py`, `test_parse_functionality.py` | Regression coverage for the shared parser and build route |

The SDK declares what to build and how to test it. Central supplies the build
environments, runs the shared process, collects outputs, and manages approved
signing and publication. Toolchain and feed credentials belong to that
infrastructure, not package source.

## 4. Why both setup.py and pyproject.toml exist

`setup.py` is executable Python packaging configuration using setuptools,
the packaging library it imports. `pyproject.toml` is a configuration file;
TOML is its file format, not a compiler.

The two files can coexist because tools read different sections for different
purposes:

| Configuration | Purpose in this package |
|---|---|
| `[project]` in `pyproject.toml` | Authoritative Python name, version, Python requirement, and dependencies for Maturin |
| `[build-system]` | Selects the backend called by Python build tools and its Python dependencies |
| `[tool.maturin]` | Tells Maturin where the Rust and Python code lives and how to package it |
| `[tool.cibuildwheel]` | Declares the platform builds coordinated by CI |
| `[tool.azure-sdk-build]`, `[tool.azure-sdk-conda]` | Repository-specific checks and bundle settings |
| `setup.py` and `MANIFEST.in` | Retained for legacy callers and their file-selection rules |

The current Python metadata includes:

```toml
[project]
name = "azure-cosmos"
version = "4.17.1"
requires-python = ">=3.10"
```

It preserves Python dependencies and optional extras. The version must agree
with `azure\cosmos\_version.py`; the retained `setup.py` must not drift from
shared metadata. The binding crate's internal name `azure_cosmos_rust` and
version `0.1.0` must not become the Python distribution's identity.

Central's `ParsedSetup`, the shared package-configuration reader, selects
Python project metadata from a populated `[project]` table. The shared build
code also detects `[tool.cibuildwheel]` independently of setuptools'
`ext_modules` declaration. This matters because Maturin does not declare its
Rust extension as a setuptools extension.

That repository routing is separate from the Python backend protocol:
`python -m build --wheel` reads `[build-system]` to select the backend.
Adding Maturin settings alone does not make every legacy build command follow
the native-wheel route. Official builds must use the configured backend
path, not assume `python setup.py bdist_wheel` produces the Rust wheel.

If a release retains a `setup.py` packaging path, it must read the authoritative
metadata rather than maintain an independent copy, and its output must be
validated separately.

## 5. Files that control the Rust build

### The two Cargo configuration files

Cargo calls a `Cargo.toml` file a **manifest**. The package-level file defines
a **workspace**: a group of crates sharing settings and a lock file.
This workspace currently contains one member:

```toml
[workspace]
members = ["azure_cosmos_rust"]
resolver = "2"
```

`resolver = "2"` selects Cargo's second-generation dependency-feature rules.
A **feature** is a named switch enabling optional crate code.

The root file provides reusable settings under `[workspace.package]` and
dependencies under `[workspace.dependencies]`. The nested
`azure_cosmos_rust\Cargo.toml` defines the binding itself and opts into those
settings. For example:

```toml
tokio = { workspace = true, features = ["rt-multi-thread", "macros"] }
```

This means the binding inherits the root's Tokio dependency and enables the
listed features. A workspace is not required merely because there is one
crate; here it centralizes settings rather than duplicating them.

Normal and development driver dependencies share the root's Git source.
The normal dependency enables native query planning and `fault_injection`;
the development dependency adds `__internal_in_memory_emulator`. Keep their
source consistent when changing the driver, and preserve required features.
The binding's `azure_core` dependency must also resolve compatibly with the
driver's so that their shared Rust types are the same crate's types.

### Exact dependencies: Cargo.lock

The manifests describe acceptable dependencies. `Cargo.lock` records the exact
versions and sources Cargo selected, including indirect dependencies.
Cargo generates this file; do not edit it manually.

| Situation | Behavior |
|---|---|
| Existing lock satisfies the manifests | A normal build reuses the locked selections |
| Lock is missing or manifests require different resolution | A normal Cargo build can create or change the lock |
| New compatible versions appear upstream | They are not all adopted automatically; `cargo update` requests updates |
| A locked build would need to change the lock | It fails instead of rewriting the file |

The package checks in `Cargo.lock` and sets Maturin's `locked = true`.
Direct Cargo validation should use `--locked` for the same guarantee.
Dependency changes require reviewing and committing the manifest and
Cargo-generated lock changes together. A path dependency is not an immutable
source snapshot: a neighboring checkout can change without a version change.

Locking prevents silent changes during builds; it does not maintain
dependencies automatically. Repository maintainers and the SDK team must
confirm update coverage for both manifests and the lock, through Dependabot
or the approved dependency-update system.

### Minimum compiler versus selected toolchain

A **toolchain** is the bundle of Rust build programs and libraries. It includes
Cargo, the compiler `rustc`, and the Rust standard library. These are different
from the source crates recorded in `Cargo.lock`.

| Setting | Current value | Meaning |
|---|---|---|
| `[workspace.package] rust-version` in `Cargo.toml` | `1.75` | Declared minimum compiler; it does not install or select one |
| `channel` in `rust-toolchain.toml` | `ms-prod-1.97` | Selects the default toolchain |
| `profile` in `rust-toolchain.toml` | `minimal` | Requests basic compilation components, not an optimized-build mode |

`msrustup` is Microsoft's internal Rust toolchain manager. Public `rustup`
cannot resolve the internal `ms-prod-1.97` channel. Internal developers and
build machines need the appropriate toolchain setup and access; see the
internal setup guidance at `https://aka.ms/msrustup`.

The channel is not an immutable compiler patch-version pin. Approve the final
release compiler policy separately and record the toolchain actually used
by release builds.

The selected compiler must satisfy the binding and all dependencies. Building
with a newer compiler does not prove the declared `1.75` minimum works.
Validate or update that minimum when selecting the release driver. If customer
source builds are supported, also test the promised minimum and provide a
customer-accessible toolchain path.

## 6. How Cargo builds the Rust extension

The binding's `Cargo.toml` requests this library:

```toml
[lib]
name = "azure_cosmos_rust"
crate-type = ["cdylib"]
```

`cdylib` tells Cargo to produce a dynamic library that software outside Rust
can load. **PyO3** is the Rust library providing the Python/Rust interface,
including the Python module initialization entry point.

Cargo resolves the dependency order and starts `rustc`. A **linker** combines
the required compiled code into the loadable library:

```text
Cargo reads the binding manifest, workspace settings, and Cargo.lock
    -> obtains the binding's dependencies, including the driver
    -> runs rustc for the required crates in dependency order
    -> links binding and driver machine code into one dynamic library
    -> writes Rust build outputs under target\
```

Cargo's output is not yet a Python distribution. **Maturin** is the packaging
tool that gives the compiled library its Python extension filename and
combines it with the Python SDK files.

The relevant `pyproject.toml` settings are:

```toml
[tool.maturin]
manifest-path = "azure_cosmos_rust/Cargo.toml"
python-source = "."
module-name = "azure.cosmos._rust"
features = ["pyo3/extension-module"]
locked = true
```

`manifest-path` selects the binding crate; `python-source` locates the Python
source; `module-name` defines the import path. Its final `_rust` component must
match the binding's `#[pymodule]` function name. The extension-module feature
configures PyO3 for a Python extension.

The resulting extension is `_rust.pyd` on Windows or `_rust.abi3.so` on Linux
and macOS. Each contains compiled binding and driver code for its target.
The Python `.py` files remain readable Python source.

## 7. Local development build

Use an editable installation when changing and testing SDK source.
**Editable** means the Python files continue to come from the checkout;
Rust changes still require recompilation.

Before building, arrange the selected Rust toolchain, platform compiler/linker
requirements, and access to the pinned driver and dependency sources. A
neighboring Rust checkout is not required by the shared configuration.

Activate a Python **virtual environment**, an isolated environment for this
project's Python packages. From `sdk\cosmos\azure-cosmos`:

```powershell
python -m pip install "maturin==1.15.0"
maturin --version
Get-Command maturin
maturin develop --release
```

Check that Maturin resolves inside the activated environment and reports the
declared version. `--release` requests optimized Rust code; it does not publish
an SDK release.

Maturin reads the configuration, runs Cargo, prepares the extension, and makes
the SDK available in the active environment. Python edits are visible without
rebuilding the extension; rerun the development build after Rust edits.

This is not the distributable-wheel workflow. Calling Maturin directly bypasses
`azure_cosmos_build_backend.py`, so it does not perform that backend's
QueryPlanInterop staging. An editable installation also does not prove that a
release wheel contains all required files.

## 8. Building and checking a wheel locally

### Build tools and the backend

A **build frontend** starts the Python packaging process. A **build backend**
implements the package build. Their responsibilities here are:

| Component | Role |
|---|---|
| Python `build` package | Frontend invoked as `python -m build` |
| `azure_cosmos_build_backend.py` | SDK-owned backend wrapper; stages supplied QueryPlanInterop libraries for wheels |
| Maturin | Backend and command-line tool; invokes Cargo and assembles Python distributions |
| Cargo and `rustc` | Resolve dependencies and compile Rust |
| PyO3 | Rust dependency implementing the Python/Rust interface, not a packaging command |
| `cibuildwheel` | CI tool coordinating repeated builds across configured targets |

In an active development environment with the Rust prerequisites arranged:

```powershell
python -m pip install build
python -m build --wheel
```

Run these from `sdk\cosmos\azure-cosmos`. The wheel is written under `dist`;
the command does not install the SDK or publish it.

The build uses this configuration:

```toml
[build-system]
requires = ["maturin==1.15.0"]
build-backend = "azure_cosmos_build_backend"
backend-path = ["."]
```

The frontend creates a temporary Python build environment and installs the
declared Maturin version. `backend-path` lets it find the SDK-owned backend
in the package source directory. The flow is:

```text
python -m build --wheel
    -> temporary Python build environment
    -> azure_cosmos_build_backend.py
    -> Maturin
    -> Cargo and rustc
    -> compiled extension + Python files + metadata
    -> dist\<wheel-name>.whl
```

Build isolation supplies Python build dependencies, not a complete platform
toolchain or QueryPlanInterop. Do not rely on automatic Rust installation
through this prototype, especially for its internal toolchain. If isolation
is disabled with `--no-isolation`, the caller must also install and select the
correct Python build tools.

The wrapper forwards source-distribution, editable-build, and metadata
requests to Maturin. Its additional wheel behavior is explained once in
[QueryPlanInterop packaging](#11-how-queryplaninterop-is-packaged-and-loaded).
Calling `maturin build` directly bypasses that wrapper.

### Inspect and install the exact wheel

Building and installing are separate operations:

```text
Build:   source + configuration -> a .whl file
Install: that .whl file -> files in a chosen Python environment
```

Select the exact output being tested rather than an older wheel left in
`dist`. Replace the filename placeholder below with that output:

```powershell
$wheel = (Resolve-Path ".\dist\<actual-wheel-name>.whl").Path
python -m zipfile --list $wheel
python -m venv .wheel-test
.\.wheel-test\Scripts\python -m pip install $wheel
.\.wheel-test\Scripts\python -I -c "from azure.cosmos import _rust; print(_rust.__file__)"
```

Archive inspection proves inclusion, not loadability. The clean-environment
import checks that the extension can load on this machine. `-I` prevents
the check from selecting the source directory or `PYTHONPATH` instead of the
installed wheel; the printed path must belong to `.wheel-test`.

Neither check proves SDK operations work. Functional tests must also run
against the installed wheel without falling back to the checkout.

## 9. What a completed wheel contains

A wheel is a ZIP archive. The following is the intended Windows wheel layout;
`.libs` is the planned QueryPlanInterop addition, not a guarantee of current
prototype contents:

```text
azure\
    cosmos\
        __init__.py
        cosmos_client.py
        container.py
        py.typed
        _query_advisor\
            query_advice_rules.json
        _rust.pyi
        _rust.pyd
        .libs\
            Cosmos.QueryPlanInterop.dll
            <required companion libraries>
azure_cosmos-<version>.dist-info\
    METADATA
    WHEEL
    RECORD
```

| Content | Purpose |
|---|---|
| Python `.py` files | Python SDK implementation |
| `py.typed`, `_rust.pyi`, query-advisor rules | Typing information and package data |
| Exactly one target-matching `_rust` extension | Compiled binding and Rust driver |
| `.libs` libraries, when provisioned | Separate QueryPlanInterop library and required companions |
| `METADATA` | Python project name, version, Python requirement, and dependencies |
| `WHEEL` | Wheel-format and compatibility information |
| `RECORD` | Packaged-file records |

Linux and macOS wheels contain `_rust.abi3.so` instead of `_rust.pyd`.
QueryPlanInterop is not linked into that extension.

Check the Python name and version, dependencies and extras, and
`Requires-Python` against the package configuration. Also reject stale
extensions, duplicate entries, and Python bytecode left by local builds.
An importable wheel with incorrect metadata or missing package data is not a
complete deliverable.

## 10. Why one release needs several wheels

Windows x64 machine code cannot serve Linux or ARM64. The prototype therefore
configures five target builds. Expected filename shapes are:

```text
azure_cosmos-<version>-cp310-abi3-win_amd64.whl
azure_cosmos-<version>-cp310-abi3-win_arm64.whl
azure_cosmos-<version>-cp310-abi3-manylinux_2_28_x86_64.whl
azure_cosmos-<version>-cp310-abi3-manylinux_2_28_aarch64.whl
azure_cosmos-<version>-cp310-abi3-macosx_<minimum-version-tag>_arm64.whl
```

These are shapes, not literal filenames or evidence of generated artifacts.
Inspect the macOS build and wheel to establish its minimum-version tag.
Intel macOS, musllinux, PyPy, and Python 3.9 are outside this experiment,
not automatically rejected forever by an approved release policy.

### Python compatibility and the stable ABI

**ABI** means application binary interface: the low-level rules compiled code
uses to call Python. `abi3` is CPython's stable ABI for extensions.
PyO3's `abi3-py310` feature lets the binding use that stable interface starting
at Python 3.10.

For one target, the same `cp310-abi3` wheel can serve later compatible CPython
versions instead of requiring a separate wheel for each Python version.
It still needs tests on every version the SDK claims to support.

| Setting | What it establishes |
|---|---|
| PyO3 `abi3-py310` | Stable binary interface starting at CPython 3.10 |
| `[project] requires-python = ">=3.10"` | Installer rejects Python versions below 3.10 |
| SDK support policy and tests | Versions the team actually supports |

An unbounded `Requires-Python` value and a loadable extension are not automatic
support approval for every future Python version.

### Operating-system and processor compatibility

| Tag or setting | Meaning |
|---|---|
| `win_amd64` | Windows x64; does not encode a minimum Windows version |
| `win_arm64` | Windows ARM64 |
| `manylinux_2_28_x86_64` | Linux x64 under the glibc 2.28 compatibility baseline |
| `manylinux_2_28_aarch64` | Linux ARM64 under the same baseline |
| Example `macosx_11_0_arm64` | Apple Silicon, with macOS 11.0 represented as the minimum; illustrative until the actual artifact is checked |

**glibc** is the C runtime library used by many Linux systems. A
`manylinux_2_28` wheel requires that compatibility baseline; it is not a
universal Linux wheel. A **build image** is the prepared environment used to
compile it. On macOS, the **deployment target** records the intended minimum
OS version. Validate the actual binaries as well as their filename tags.

The target-selection excerpt in `pyproject.toml` is:

```toml
[tool.cibuildwheel]
build = ["cp310-*"]
skip = ["*-musllinux*"]

[tool.cibuildwheel.windows]
archs = ["AMD64", "ARM64"]

[tool.cibuildwheel.linux]
archs = ["x86_64", "aarch64"]
manylinux-x86_64-image = "manylinux_2_28"
manylinux-aarch64-image = "manylinux_2_28"

[tool.cibuildwheel.macos]
archs = ["arm64"]
```

This excerpt omits toolchain setup and environment forwarding; it is not a
replacement for the complete file. Declaring targets does not create build
machines or prove runtime support. The pipeline must build them and execute
the required tests.

## 11. How QueryPlanInterop is packaged and loaded

### Three query-planning providers

A **query plan** identifies the partitions to contact and how to process the
combined results. The current driver has three providers:

| Provider | Where planning happens | Separate library required? |
|---|---|---|
| QueryPlanInterop | Native library loaded by the driver | Yes |
| Pure-Rust planner | Driver code compiled into `_rust` | No |
| Gateway planner | Cosmos DB service | No |

In default `LocalPreferred` mode, normal plan resolution tries the enabled
QueryPlanInterop provider, then the pure-Rust planner, then the Gateway.
The Rust planner handles eligible query shapes, not every query.
`GatewayOnly` bypasses both local providers. Some contradictory filters can
also produce an empty result before topology lookup.

**A wheel without QueryPlanInterop can still plan eligible queries locally.**
A successful query, or even evidence of local planning, is therefore not proof
that QueryPlanInterop ran. The driver distinguishes providers with
`native_ffi`, `local_rust`, and `gateway` diagnostic labels.

When enabled and used, the QueryPlanInterop provider loads the library, finds
its functions, creates a provider, and passes query and partition-key
information to it, including through `GetPartitionKeyRangesFromQuery4`.
The returned JSON describes the plan; the driver executes the query.
The driver does not download or compile this library automatically.

### Supplying and packaging the library

The Rust driver crate contains calling code, not precompiled QueryPlanInterop
files. They must be supplied separately for each target:

| Operating system | Primary library |
|---|---|
| Windows | `Cosmos.QueryPlanInterop.dll` |
| Linux | `libqueryplaninterop.so` |
| macOS | `libqueryplaninterop.dylib` |

Both the primary library and its required companions must match the wheel's
operating system and processor. An x64 file does not become ARM64 because it
is copied into an ARM64 wheel.

Two environment variables, named settings passed to processes, have different
purposes:

| Variable | When used | Meaning |
|---|---|---|
| `AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR` | Wheel build | Directory of already-built files to package |
| `AZURE_COSMOS_QUERYPLANINTEROP_DIR` | SDK execution | Directory from which the driver should load the library |

For a local wheel build with already-obtained matching files:

```powershell
$env:AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR = "C:\path\to\queryplaninterop"
python -m build --wheel
```

The example path is not an approved binary source. The custom backend:

1. Requires a valid source directory with exactly one primary library.
2. Temporarily copies the primary and supplied native companions into
   `azure\cosmos\.libs`.
3. Calls Maturin to build the wheel.
4. Removes its staged copies from the checkout; the completed archive retains
   its packaged files.

When the source setting is absent, staging is skipped. It is not currently
an error to build a wheel without QueryPlanInterop. The pipeline does not yet
provision these files or forward their source-directory variable into Linux
containers. Provisioning must make both the files and the path visible inside
the container, not just on the host.

`build.rs` and `query_plan_binary.rs` validate the staged library's target
filename and compiled-file headers, including processor and Linux word size.
These checks reject wrong-target files; they do not prove all dependencies
are available or that the library loads and creates plans.

### Loading from an installed wheel

The Python wrapper locates `.libs` beside the imported `_rust` extension and
supplies that directory to the driver. It preserves an explicitly supplied
`AZURE_COSMOS_QUERYPLANINTEROP_DIR`. The driver uses the configured directory
or operating-system lookup as applicable.

For editable development, use the runtime setting to point at an external
matching library directory; `maturin develop` does not stage it into a wheel.
Missing QueryPlanInterop does not disable the pure-Rust planner.

### Deferred work and completion criteria

The plan is to include QueryPlanInterop in later release wheels. Before
claiming that requirement is complete:

| Work | Owner |
|---|---|
| Identify the producing team, approved binary source, and matching driver/library versions | Cosmos SDK team, Rust driver team, and QueryPlanInterop-producing team |
| Confirm redistribution, licensing, signing, and companion-library requirements | Producing team and release approver |
| Supply a matching binary set before each platform build, including inside Linux containers | Central team, with SDK-owned staging configuration |
| Inspect final wheels and prove this specific provider loads and generates plans | Cosmos SDK team supplies tests; Central runs them on the required targets |

The producing team and approved distribution location still need confirmation.
A compiled wheel, archive inclusion check, or import alone does not close this
work.

## 12. Decide whether v5 publishes a source distribution

A **source distribution**, or **sdist**, is a `.tar.gz` archive containing source
and build instructions rather than an already-compiled extension. The release
must choose between wheels only and wheels plus a supported sdist.

### Sdist tracking note: customer source installation

**Status: open release decision, not an immediate wheel-generation blocker.**

Publishing a Rust-backed sdist exposes an installation path in which the
customer's machine compiles Rust. This can happen during an ordinary pip
installation when no compatible wheel is available for the selected version:

```text
pip selects the sdist
    -> creates a Python build environment
    -> installs declared Python build dependencies
    -> calls the custom backend and Maturin
    -> Cargo/rustc compile the extension
    -> pip installs the resulting wheel
```

The source archive is not installed merely by downloading or unpacking it.
The tool requirements differ from installing a prebuilt wheel:

| Tool or input | Customer source-install requirement |
|---|---|
| Python and pip | Start the installation |
| Maturin | Needed during the build; pip normally installs the declared version in build isolation |
| Cargo and `rustc` | Compatible Rust toolchain must be available |
| Platform compiler/linker and libraries | Required as appropriate for the target and dependencies |
| Rust dependency sources | Accessible registry sources and, while Git-pinned, the driver Git source |
| QueryPlanInterop inputs | Required if the source-build promise includes that specific provider, not merely pure-Rust local planning |
| `cibuildwheel` | Not required for an ordinary pip source install |
| Python `build` package | Not required just to run `pip install` |

If isolation is disabled, the caller must arrange Python build dependencies
too. Installing Maturin does not provision the entire native-build environment.

**External customers cannot be assumed to have access to `ms-prod-1.97`,
`msrustup`, or internal feeds.** A public source-install path needs a documented
and tested customer-accessible toolchain selection and dependency setup.
Successfully generating an archive does not establish that path.

To close this item, the SDK team and release approver must select the policy,
the SDK and Central teams must define the supported public build environment,
and installation from the actual archive must pass in that environment.

### Required archive contents and build path

The configured backend delegates source-distribution creation to Maturin.
Its inclusion rules are not the same as the legacy `setup.py` and
`MANIFEST.in` rules. Updating one path does not establish the other's contents.
Release automation must use and validate the selected path.

The archive must carry all package-owned build inputs:

| Input | Purpose |
|---|---|
| `azure\__init__.py`, `azure\cosmos\**` | Python package, namespace support, typing files, and data |
| `azure_cosmos_rust\Cargo.toml`, `src\**` | Rust binding configuration and source |
| `azure_cosmos_rust\build.rs`, `query_plan_binary.rs` | Native-library validation |
| Root `Cargo.toml`, `Cargo.lock` | Workspace and locked dependencies |
| `rust-toolchain.toml`, required `scripts\*.sh` | Toolchain and configured setup inputs |
| `pyproject.toml`, `azure_cosmos_build_backend.py` | Python metadata and build backend |
| README, license, and any other files referenced by packaging metadata | Distribution metadata and documentation |

Explicit Maturin sdist includes cover the backend, toolchain file, and setup
scripts. Do not rely on archive creation succeeding as proof of inclusion.
If a legacy source-build path is retained, its `setup.py` and `MANIFEST.in`
must also be complete and consistent.

The archive need not vendor the driver when Cargo can download its approved
source. No active dependency may require a neighboring checkout. Do not
include one target's QueryPlanInterop library as though it worked everywhere;
define target-specific provisioning if that provider is promised.

### Proving a supported source installation

Create the sdist, move it outside both repositories, and build/install from
that archive in a clean environment with the documented customer-accessible
tools. Verify that:

1. No neighboring checkout or undeclared local files supply missing inputs.
2. The locked dependencies and selected toolchain can be obtained.
3. The resulting wheel has correct contents and metadata.
4. Its extension imports and required SDK operations pass.
5. QueryPlanInterop is supplied and exercised if that provider is promised.

Archive-generation and inclusion checks do not replace this end-to-end test.
Document supported source-build targets and requirements in the package README.

If the release is wheel-only, ensure publication excludes sdists and includes
every required wheel. For that release version, a customer without a compatible
wheel has no source-install fallback; do not imply unsupported targets can
install it.

## 13. How the Cosmos pipeline produces the release files

The SDK entry point delegates to shared Central templates:

```text
sdk\cosmos\ci.yml
    -> eng\pipelines\templates\stages\cosmos-sdk-client.yml
    -> eng\pipelines\templates\stages\archetype-sdk-client.yml
    -> shared build jobs and conditional release processing
```

The Cosmos template already sets `InstallMsRustToolchain: true` and supplies
the package working directory and Windows ARM64 Rust target. The downstream
templates carry those settings to the installation step before package
generation. Rust does not need a different pipeline entry point.

The shared package reader recognizes `[tool.cibuildwheel]`, and `sdk_build`
invokes `cibuildwheel`. That tool coordinates the target builds; the custom
backend, Maturin, and Cargo still perform each package build.
The system reuses the shared native-wheel infrastructure rather than replacing
it with a Cosmos-specific publishing system.

### Build environments and execution coverage

| Build machine | Configured use |
|---|---|
| Windows x64 | Build x64 directly; cross-compile Windows ARM64 |
| Linux x64 | Build x64 in a container; use QEMU emulation for Linux ARM64 |
| macOS ARM64 | Build macOS ARM64 directly |

**Cross-compilation** builds code for a different processor from the build
machine. **Emulation** lets one processor run software intended for another.
An ARM64 wheel produced on x64 is not proof that ARM64 runtime tests ran.
Central must provide suitable execution coverage for each supported target.

Windows ARM64 uses `CARGO_BUILD_TARGET = "aarch64-pc-windows-msvc"` and
`PYO3_CROSS_LIB_DIR` from the pipeline's ARM64 Python-library location.
The PyO3 `generate-import-lib` feature supports this build arrangement.

Linux builds run inside prepared containers. Toolchain setup, dependency
access, and required environment settings must reach those containers;
installing tools only on the host is insufficient.

A **job timeout** limits the whole build job; a **step timeout** limits one
operation inside it. The Rust-enabled jobs allow 240 minutes, with 210 minutes
for package generation. Both limits must accommodate compilation and setup.

### Validation outputs versus release files

When the applicable trigger or manual request starts a run:

```text
selected source commit
    -> platform jobs prepare tools and dependency access
    -> cibuildwheel invokes the configured package build per target
    -> configured wheel checks run where supported
    -> wheels are collected as CI artifacts
```

**CI artifacts** are internally saved outputs, not published customer releases.
The package's current `test-command` checks imports and the presence of
`_rust.create_database`; it does not call that operation or prove query planning.
Full installed-wheel tests remain necessary.

Path coverage under `sdk\cosmos` includes the Rust source and configuration,
but it does not guarantee that every branch push triggers a run. Registration,
manual queuing, identities, and permissions are outside the scope of this
guide.

### Approved release processing

Central must confirm that the release route handles all approved wheels and
any selected sdist as one `azure-cosmos` version. A successful build is not
approval to publish a partial set.

The release plan requires approved signing for Windows and macOS native files.
**Digital signing** attaches verifiable publisher and integrity information.
Where signing modifies a wheel's contents, the process must unpack, sign,
repack with correct file records, and test the final wheel again.
Signing credentials stay in Central-owned infrastructure.

Publish only the complete approved output set after final-wheel checks and
release approval. Neither an editable install nor tests of a pre-signing
intermediate wheel establish that the published files work.

## 14. What customers install

For an approved Rust-backed release, a Contoso Bank developer normally runs:

```powershell
python -m pip install azure-cosmos
```

For the selected version, pip normally chooses a compatible wheel when one
is available. For example, Contoso's Windows x64 application receives a Windows
x64 wheel, not the Linux or Windows ARM64 file.

The wheel already contains the Python SDK and compiled binding/driver.
Customers installing it do not need Rust, Cargo, Maturin, `rustup`,
`msrustup`, `cibuildwheel`, or a separate driver installation. The planned
QueryPlanInterop addition belongs inside the matching wheel, not in a manual
download step for every customer.

Customers still need compatible CPython and OS/processor versions, an installer
that understands the tags, and any required system runtimes not bundled with
the wheel. Pip normally installs declared Python dependencies.

If no compatible wheel exists, behavior depends on the
[sdist policy](#sdist-tracking-note-customer-source-installation). Building on
the customer's machine is a different installation path, not a requirement
for customers who install compatible wheels.

## 15. Release readiness and remaining decisions

These are release requirements and unresolved decisions, not claims that the
prototype has completed them. The **release approver** is the authorized person
or group approving the final version, support policy, and publication; that
owner must be identified.

| Work or decision | Required outcome | Owner |
|---|---|---|
| Release identity | Approved Python release version; metadata and runtime version agree | Cosmos SDK team and release approver |
| Driver dependency | Approved published GA driver for a GA release; shared normal/development source and synchronized lock | Cosmos SDK team and Rust driver team |
| Rust compiler policy | Approved build toolchain and validated minimum; do not infer minimum compatibility from a newer compiler | Cosmos SDK team and Central team |
| Python and OS support | Approved Python versions, platform list, Linux baseline, and Windows/macOS minimums | Release approver, with SDK and Central evidence |
| Multi-target pipeline | Run the intended commit; inspect all required output files and confirm execution-test coverage, including ARM64 | Central team and Cosmos SDK team |
| QueryPlanInterop | Complete the [deferred provisioning and provider tests](#deferred-work-and-completion-criteria) | Producing team, Cosmos SDK team, and Central team |
| Source distributions | Resolve and validate the [customer source-install policy](#sdist-tracking-note-customer-source-installation) | Release approver, Cosmos SDK team, and Central team |
| Dependency maintenance | Confirm automated update coverage for Cargo manifests and lock | Repository maintainers and Cosmos SDK team |
| Signing and publication | Approved signing, tests of final repacked wheels, and complete-set publication under one version | Central team and release approver |

### Required installed-wheel checks

The SDK supplies the tests; Central runs them across the approved **test
matrix**, the list of Python versions and targets requiring coverage.
Use the same stable-ABI wheel across the Python versions it claims to support.

| Check | What must be established |
|---|---|
| Archive and metadata | Correct Python files, data, one matching extension, expected native companions, project identity, dependencies, and compatibility tags |
| Clean installation | SDK and `_rust` import from the installed wheel, not the source checkout |
| SDK functionality | Required Rust-backed operations actually execute successfully |
| QueryPlanInterop | The `native_ffi` provider loads and generates plans when provisioned |
| Pure-Rust and Gateway planning | Eligible queries use `local_rust` without QueryPlanInterop; unsupported local shapes can fall back; `GatewayOnly` explicitly exercises Gateway planning |
| Final outputs | Required wheel set and any approved sdist are present; final signed/repacked wheels retain correct contents and behavior |

For missing-QueryPlanInterop coverage, start a new process with the runtime
directory setting pointing to an empty directory before SDK import, and ensure
the environment exposes no other copy. That does not disable the pure-Rust
planner or force every query to the Gateway. Observe provider-specific
diagnostics rather than treating query success as proof of a particular path.

Existing configuration and staging unit tests support these checks but cannot
replace execution on the supported targets. Publication must stop if a
required output or test result is missing.


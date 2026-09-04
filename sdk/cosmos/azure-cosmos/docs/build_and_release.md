# Building and releasing the Rust-backed Azure Cosmos DB Python SDK

The current `azure-cosmos` release contains only Python code. Azure Cosmos DB
Python SDK v5 adds Rust code, so the release process must compile that code and
place the result in platform wheels. A platform wheel is a `.whl` file built
for one operating-system and processor combination, called a **build target**
in this document.

Today, release `4.16.2` produces:

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
operating system and processor. The complete proposed target list is:

```text
Windows x64
Linux x64
Linux ARM64
macOS ARM64
```

Linux ARM64 remains conditional on obtaining a supported CI build-and-test
environment.

Before executing a cross-partition query, the SDK needs a query plan: the list
of partitions to contact and the work to perform on the combined results.
QueryPlanInterop is a separate compiled library that can create that plan on
the customer's machine. Without it, the SDK asks the Cosmos DB Gateway—the
service endpoint that can create the plan—for the same information.

Every official v5 platform wheel must include the QueryPlanInterop library
built for the same target and must support local query planning.

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

Before the v5 release can be produced:

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
   `ms-prod-1.97` channel through `msrustup`. This proves that the prototype
   pipeline can compile the extension; it does not by itself approve that
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
| Whether the existing Python Storage Extension `cibuildwheel` integration can invoke the configured Maturin and custom-backend build | Shared Azure SDK pipeline team |
| Confirm that release tooling can sign the approved platform wheels and publish them together with any selected sdist under one version | Shared Azure SDK pipeline team |
| Whether `sdk/cosmos/ci.yml` needs a confirmed shared Azure SDK pipeline parameter | Shared Azure SDK pipeline team |

The current release publishes an sdist. If v5 continues to publish one, it
must contain everything needed to build the compiled Python extension from an
unpacked archive. If v5 is wheel-only, every supported target must have a
published platform wheel.

The following sections explain the files involved, the local development build,
the CI wheel build, the files placed in each wheel, and the remaining Cosmos
SDK and shared Azure SDK pipeline work.

---

## Table of contents

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


## Current release files and what changes in v5

The Rust migration uses `azure-cosmos 4.16.2` as the current pure-Python
release baseline. Its release process publishes two release files:

```text
azure_cosmos-4.16.2-py3-none-any.whl
azure_cosmos-4.16.2.tar.gz
```

These release files contain the same SDK release in two different forms.

### The current wheel

The `.whl` release file is what `pip` normally installs. It contains the
`azure.cosmos` Python package, package data, and installation metadata. It does
not contain `_rust.pyd`, `_rust.abi3.so`, or any other compiled Cosmos code.

The filename describes what the wheel can support:

```text
azure_cosmos-4.16.2-py3-none-any.whl
                    │   │    │
                    │   │    └─ not limited to one operating system or processor
                    │   └────── not tied to one CPython-version-specific extension
                    └────────── Python 3
```

`py3` does not mean every Python 3 version is supported. The current release
declares:

```python
python_requires=">=3.9"
```

in `sdk/cosmos/azure-cosmos/setup.py`. During packaging, this becomes:

```text
Requires-Python: >=3.9
```

inside the installed project metadata. `pip` reads that value and rejects the
release on Python versions older than 3.9.

The proposed Maturin build will move this setting to the `[project]` table in
`pyproject.toml`:

```toml
requires-python = ">=3.9"
```

This preserves the existing minimum Python version after `pyproject.toml`
becomes the source of the release metadata.

### The current source distribution

The `.tar.gz` file is the source distribution:

```text
azure_cosmos-4.16.2.tar.gz
```

It contains source files and build instructions rather than already compiled
and installable files. The current sdist is created through `setup.py`,
with `MANIFEST.in` helping determine which repository files are included.

The current CI pipeline validates the completed sdist rather than only checking
the source checkout. The Linux build job runs `twine check` against the
generated `.tar.gz`. The later Analyze job downloads the build artifacts and
runs the `verifysdist` check, which installs the generated sdist and verifies
its included directories, package metadata, compatibility with the prior
release metadata, and `py.typed` packaging configuration.

The Cosmos emulator test matrix also requests the `sdist` functional check.
That check installs the generated source distribution into an isolated Python
environment and runs the selected pytest tests against the installed package.
This is separate from `verifysdist`: the emulator job tests package behavior,
while the Analyze job inspects source-distribution contents and metadata.

The current sdist does not need Rust source. A v5 sdist would also
need the Rust binding source, Cargo files, and enough build configuration to
produce the compiled extension from an unpacked archive.
Whether v5 will publish that sdist remains a release decision and is
covered in the source-distribution section.

### Why the v5 wheel is different

The v5 wheel will contain `_rust.pyd` on Windows or `_rust.abi3.so` on Linux
and macOS. These files contain machine code compiled for a particular operating
system and processor.

That changes the release files as follows:

| Release area | Current pure-Python release | Proposed v5 release |
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

The binding currently refers to the neighboring driver folder through this
entry in `azure_cosmos_rust/Cargo.toml`:

```toml
azure_data_cosmos_driver = {
    path = "../../../../../azure-sdk-for-rust/sdk/cosmos/azure_data_cosmos_driver",
    features = ["__internal_native_query_plan"],
}
```

A Cargo **feature** is a named switch that enables optional crate code. Here,
`__internal_native_query_plan` enables the Rust driver's local-query-planning
support.

The current path works only when both repositories are checked out beside each
other. The shared development configuration should instead use either:

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

The root `sdk/cosmos/azure-cosmos/Cargo.toml` also currently declares an
`azure_identity` path under `[workspace.dependencies]`. The Rust binding crate
does not use that dependency, so it must be removed before a release build.
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
| Proposed `sdk/cosmos/azure-cosmos/rust-toolchain.toml` | Selects the Rust toolchain channel or version used for default local and CI builds |

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

The current working branch does not contain `rust-toolchain.toml`. The Central
Engineering System prototype in PR #48867 adds:

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
build produces Windows x64 machine code; Linux x64, Linux ARM64, and macOS
ARM64 each require their own build.

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

- both repositories must remain checked out beside each other while the Rust
  binding crate still uses the neighboring driver path;
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
python -m pip install "maturin>=1.4,<2.0"
```

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

The final proposed settings belong in:

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
requires = ["maturin>=1.4,<2.0"]
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
.\.wheel-test\Scripts\python -c "from azure.cosmos import _rust; print(_rust.__file__)"
```

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
azure_cosmos-<version>-cp39-abi3-win_amd64.whl
```

The version and platform tags still require release approval. The
current repository metadata is not ready to produce this name: Maturin
currently reads `azure_cosmos_rust` and version `0.1.0` from the Rust binding
crate's `Cargo.toml`. The release configuration must instead identify the PyPI
project as `azure-cosmos` and use the approved release version.

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

For example, the current minimum Python requirement:

```text
Requires-Python: >=3.9
```

must remain present after project metadata moves from `setup.py` to
`pyproject.toml`.

### What the filename tells `pip`

For this example:

```text
azure_cosmos-<version>-cp39-abi3-win_amd64.whl
```

- `azure_cosmos` identifies the `azure-cosmos` PyPI project.
- `<version>` is the approved release version.
- `cp39-abi3` identifies the Python compatibility.
- `win_amd64` means Windows x64.

`pip` compares these tags with the customer's Python installation and
machine. It will not install this Windows wheel on Linux, macOS, or a
different processor architecture.

The detailed Python-version and platform compatibility rules are covered
later. This section establishes only what must be present inside one completed
wheel.

---

## How QueryPlanInterop is packaged and loaded

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
set. Under the complete four-target proposal, that means:

```text
Windows x64 build  -> Cosmos.QueryPlanInterop.dll
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

An editable local build does not package QueryPlanInterop. To use local query
planning, the developer points the running SDK at an external library
directory:

```
AZURE_COSMOS_QUERYPLANINTEROP_DIR=<directory containing QueryPlanInterop files>
```

Without a configured QueryPlanInterop library, Rust queries still work, but
the driver asks the Cosmos DB Gateway for their query plans.

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
value. The driver attempts local query planning when the library is available
and uses Gateway query planning when it is unavailable.

### Remaining QueryPlanInterop decisions

| Decision or work | Owner |
|---|---|
| Identify the producing team, pipeline, and approved storage location | Cosmos SDK team and release approver |
| Approve matching QueryPlanInterop and Rust driver versions | Rust driver team, QueryPlanInterop-producing team, and release approver |
| Confirm redistribution, library-signing, and licensing requirements | QueryPlanInterop-producing team and release approver |
| Supply the correct files to each CI wheel job | Shared Azure SDK pipeline team |
| Provide a test-visible result that reliably distinguishes local query planning from Gateway query planning | Rust driver team and Cosmos SDK team |
| Open, install, and exercise each completed wheel | Cosmos SDK team supplies the tests; shared Azure SDK pipeline runs them for every build target |

---

## Why one release needs several wheels

The current pure-Python release uses one wheel:

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

### Proposed wheel set

The proposed v5 support list is:

| Operating system | Processor |
|---|---|
| Windows | x64 |
| Linux | x64 |
| Linux | ARM64 |
| macOS | ARM64 |

Linux ARM64 remains a proposed target. The current CI machines do not include
a Linux ARM64 machine, so the shared pipeline must confirm the
[`cibuildwheel` emulation path](#current-ci-build-machine-limit) before this
target is approved.

The complete proposal produces four wheels:

```text
azure_cosmos-<version>-cp39-abi3-win_amd64.whl
azure_cosmos-<version>-cp39-abi3-manylinux_2_17_x86_64.whl
azure_cosmos-<version>-cp39-abi3-manylinux_2_17_aarch64.whl
azure_cosmos-<version>-cp39-abi3-macosx_11_0_arm64.whl
```

These names are proposed examples. The release approver must still approve:

- the release version;
- the minimum Linux compatibility level;
- the minimum macOS version;
- the final operating-system support statement.

Intel macOS, Windows ARM64, and PyPy—an alternative Python
implementation—are not part of the current proposed release set.

### Why there is not one wheel for every Python version

Without additional configuration, a compiled Python extension may require a
separate wheel for each Python version:

```text
Windows x64 + Python 3.9
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
    features = ["extension-module", "abi3-py39"],
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
_rust built for CPython 3.9
    → CPython 3.9 only

_rust built for CPython 3.10
    → CPython 3.10 only
```

`abi3-py39` tells PyO3 to use only the stable low-level CPython functions
available starting with Python 3.9. Those functions keep the same binary rules
in later compatible CPython versions.

On the same build target, one compiled file can therefore be tested with
several CPython versions:

```text
one cp39-abi3 _rust.pyd
    → CPython 3.9
    → CPython 3.10
    → CPython 3.11
    → CPython 3.12
    → CPython 3.13
```

This produces the wheel filename portion:

```text
cp39-abi3
```

One Windows x64 wheel can therefore serve the proposed supported CPython
versions instead of building five Windows wheels.

### `abi3` does not declare supported Python versions

`abi3-py39` allows the same compiled `_rust` file to load on CPython 3.9 and
later compatible CPython versions. It does not decide which versions the
Azure Cosmos DB SDK officially supports.

The project metadata separately declares the minimum Python version:

```toml
[project]
requires-python = ">=3.9"
```

This becomes:

```text
Requires-Python: >=3.9
```

inside the wheel metadata.

The proposed release support statement is CPython 3.9 through 3.13. A later
CPython version is not automatically supported merely because `_rust` may
load on it. The SDK must test and explicitly add that version to its support
policy. With the proposed `requires-python = ">=3.9"` value, `pip` may still
install the wheel on that later version; installability does not mean official
support.

These settings answer different questions:

| Setting | What it controls |
|---|---|
| `abi3-py39` | Allows the same compiled `_rust` file to load on CPython 3.9 and later compatible CPython versions |
| `requires-python = ">=3.9"` | Tells `pip` not to install the release on Python versions older than 3.9 |
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

### What the Linux tags mean

Linux operating-system releases may use different versions of system
libraries. A wheel built on a new Linux machine can accidentally depend on
system-library versions unavailable on older supported machines.

A tag such as:

```text
manylinux_2_17_x86_64
```

means:

- Linux;
- x64 processor;
- compatible with the `manylinux_2_17` rules.

Similarly:

```text
manylinux_2_17_aarch64
```

means Linux ARM64 under the same compatibility rules.

The `2_17` value refers to the minimum glibc compatibility level represented
by the wheel tag. glibc is the common C runtime library used by many Linux
operating systems. A compatible customer machine must provide glibc 2.17 or
later.

The exact manylinux level is not configured or approved yet. The final value
must be selected according to the oldest Linux environment the SDK promises
to support. The **Linux build image** is the prepared Linux environment used
to compile the wheel and establish that compatibility level.

### What the macOS tag means

This filename ending:

```text
macosx_11_0_arm64
```

means:

- macOS;
- Apple Silicon ARM64;
- macOS 11.0 as the minimum version represented by the wheel tag.

The current proposal supports Apple Silicon only. Intel macOS is not included.
The `11_0` value remains a proposed example until the minimum supported macOS
version is approved. The **deployment target** is the minimum macOS version
recorded when compiling the wheel.

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
| Reuse one compiled `_rust` file across compatible CPython versions starting with 3.9 | `abi3-py39` in `azure_cosmos_rust/Cargo.toml` |
| Minimum installable Python version | `[project] requires-python` in `pyproject.toml` |
| Supported build targets | Proposed `[tool.cibuildwheel]` settings in `pyproject.toml` |
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

The current release includes the sdist described in
[Current release files and what changes in v5](#current-release-files-and-what-changes-in-v5).
It contains source files and build instructions rather than an already
compiled `_rust` extension.

The v5 release must decide whether it will:

1. publish the platform wheels and an sdist; or
2. publish platform wheels only.

This decision affects what happens when `pip` cannot find a wheel matching a
customer's build target.

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
Cargo and rustc compile the Rust source
              ↓
a platform wheel is built locally
              ↓
pip installs that wheel
```

This is a substantially different installation path from downloading a
precompiled wheel.

The customer would need:

- a supported CPython version and `pip`;
- a Rust toolchain containing Cargo and `rustc`;
- the operating system's required linker and compiled-code build tools;
- access to crates.io or an approved internal copy of its crate sources;
- the system libraries required by the Rust dependencies;
- matching QueryPlanInterop files if the locally built wheel must support
  local query planning.

The exact source from which developers and customers would obtain
QueryPlanInterop is not yet confirmed.

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

### The current sdist is not sufficient for v5

The current sdist is produced through:

```powershell
python setup.py sdist
```

`setup.py` supplies the project metadata, while `MANIFEST.in` helps choose
which repository files are copied into the archive.

The current `MANIFEST.in` does not include all Rust binding source and Cargo
files required to build the v5 compiled extension. The current sdist process
therefore cannot be assumed to produce a complete v5 sdist.

### The sdist creation tool must be chosen

There are two possible build paths:

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

The Rust binding crate currently finds the Rust driver through a neighboring
repository:

```toml
# sdk/cosmos/azure-cosmos/azure_cosmos_rust/Cargo.toml

azure_data_cosmos_driver = {
    path = "../../../../../azure-sdk-for-rust/sdk/cosmos/azure_data_cosmos_driver",
    features = ["__internal_native_query_plan"],
}
```

For shared development, the binding dependency must use either a released
crates.io version or a Git dependency pointing to a specific
`azure-sdk-for-rust` branch, tag, or commit. The neighboring path may be used
only as a developer's temporary local override.

Before release, the same file must use an approved version published on
crates.io:

```toml
# sdk/cosmos/azure-cosmos/azure_cosmos_rust/Cargo.toml

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

The root Cargo configuration also currently contains:

```toml
# sdk/cosmos/azure-cosmos/Cargo.toml

[workspace.dependencies]
azure_identity = {
    path = "../../../../azure-sdk-for-rust/sdk/identity/azure_identity",
}
```

The Rust binding crate does not use `azure_identity`. Remove this entry from
the release configuration. The clean-build test must prove that no active
Cargo dependency requires a neighboring repository.

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

The verified Central Engineering System prototype uses:

```toml
# sdk/cosmos/azure-cosmos/Cargo.toml

[workspace.package]
rust-version = "1.75"
```

```toml
# sdk/cosmos/azure-cosmos/rust-toolchain.toml

[toolchain]
channel = "ms-prod-1.97"
profile = "minimal"
```

These are prototype values, not approved release values. The minimum must be
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

The Python project metadata must be defined in:

```toml
# sdk/cosmos/azure-cosmos/pyproject.toml

[project]
name = "azure-cosmos"
version = "<version>"
requires-python = ">=3.9"
```

This plan preserves the current metadata without an upper Python-version
limit. Therefore, `pip` may install the release on CPython 3.14 or later even
before that version is officially supported. Official support remains CPython
3.9 through 3.13 until the Cosmos SDK team adds and passes the required tests
for a later version. If the release approver instead requires installation to
stop at 3.13, `requires-python` must use an approved upper bound.

The same `[project]` table must preserve the current Python project
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

After the build-target decisions are approved, the `cibuildwheel` target list
belongs in:

```toml
# sdk/cosmos/azure-cosmos/pyproject.toml

[tool.cibuildwheel]
build = "cp39-*"
test-command = "python -c \"from azure.cosmos import _rust; print(_rust.__file__)\""

[tool.cibuildwheel.windows]
archs = ["AMD64"]

[tool.cibuildwheel.linux]
archs = ["x86_64", "aarch64"]

[tool.cibuildwheel.macos]
archs = ["arm64"]
```

The `test-command` shown here is only the immediate import check performed by
`cibuildwheel`. The complete SDK-owned wheel tests are defined later in this
section.

For example, if macOS 11 is approved, the macOS build environment would set:

```text
MACOSX_DEPLOYMENT_TARGET=11.0
```

That value and the manylinux build image are not approved yet. The release
approver must first choose the oldest supported macOS and Linux environments.
The shared Azure SDK pipeline team then supplies those environments, the Rust
toolchain, and QueryPlanInterop build outputs. The proposed Linux ARM64 entry
must not become a release requirement until the pipeline team provides the
build-and-test method described later.

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
7. Local query planning works when QueryPlanInterop is present.
8. Gateway query planning works when QueryPlanInterop is unavailable.
9. Installed metadata identifies `azure-cosmos`, the correct version, and
    the correct Python requirement.

For the Gateway query-planning test, start a new process with
`AZURE_COSMOS_QUERYPLANINTEROP_DIR` pointing to an empty directory before
importing the SDK, and ensure the test environment does not expose another
QueryPlanInterop copy. This prevents the installed `.libs` directory from
being selected for that test.

The Cosmos SDK team must provide a reliable test signal showing whether a
query used local query planning or Gateway query planning. File presence alone
does not prove which path executed.

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

There is currently no confirmed SDK-owned YAML change. The shared Azure SDK
pipeline still needs a supported way to recognize that the package source
directory produces a compiled Python extension.

If the shared Azure SDK pipeline team defines a parameter that must be passed
from `sdk/cosmos/ci.yml`, that exact parameter should be added after it is
confirmed. This document should not invent a YAML setting.

### Reuse the existing `cibuildwheel` precedent

The shared Azure SDK pipeline already uses `cibuildwheel` to ship the native
C-based Python Storage Extension. That implementation is the preferred
precedent for selecting build environments, collecting completed wheels, and
passing them to the existing validation and publication stages.

The shared Azure SDK pipeline team must first confirm that this existing
integration can invoke the `azure-cosmos` Python build backend, which then
calls Maturin. If it can, the Cosmos release should reuse that pattern rather
than introduce a separate native-wheel process. Any required change should be
limited to supporting the Maturin and QueryPlanInterop inputs described in
this document.

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
- `cibuildwheel` can cross-compile Windows ARM64 code on a Windows x64 machine,
  but Windows ARM64 is not part of the proposed Cosmos wheel set.

The shared Azure SDK pipeline team must confirm that its existing
`cibuildwheel` integration enables the Linux ARM64 emulator and can run the
SDK-owned tests with the matching Linux ARM64 QueryPlanInterop library.
Producing an ARM64 wheel without running those tests does not satisfy the
release requirement.

If the emulator path is not available for the release, the release approver
must remove Linux ARM64 from the approved wheel set rather than publish an
untested wheel.

### How the declared wheel set reaches the pipeline

The preceding Cosmos SDK-owned changes section defines the proposed
`[tool.cibuildwheel]` target list in:

```text
sdk/cosmos/azure-cosmos/pyproject.toml
```

The package source directory declares the target list. The shared Azure SDK
pipeline must invoke `cibuildwheel` in the environments needed to produce the
approved platform wheels and run the SDK-owned tests.

### Pull-request and CI validation flow

```text
a file under sdk/cosmos changes
              ↓
sdk/cosmos/ci.yml starts the Cosmos pipeline
              ↓
the Cosmos pipeline invokes the shared Azure SDK pipeline
              ↓
the shared Azure SDK pipeline recognizes that azure-cosmos builds
a compiled Python extension
              ↓
cibuildwheel reads the target list from
sdk/cosmos/azure-cosmos/pyproject.toml
              ↓
the approved platform wheel set is built
              ↓
the completed wheels are saved as CI artifacts
```

A pull-request or CI validation run ends with CI artifacts. It does not
publish a release.

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

The only unresolved SDK pipeline-file question is whether the shared Azure SDK
pipeline team will require a new confirmed parameter in
`sdk/cosmos/ci.yml`.

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

On a supported build target, this command:

```text
pip install azure-cosmos
```

downloads the matching platform wheel. The wheel contains the Python files,
the compiled `_rust` extension, and the Cosmos Rust driver linked into that
extension. It also contains the matching QueryPlanInterop library.

Customers installing a wheel do not need Rust, Cargo, Maturin, or a separate
Cosmos driver installation.

If no matching wheel exists, the result depends on the approved sdist policy:

- if an sdist is published, `pip` may attempt to build the SDK locally using
  the documented build requirements;
- if the release is wheel-only, installation fails on unsupported build
  targets.

---

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

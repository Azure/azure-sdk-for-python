# Building and releasing the Rust-backed Azure Cosmos DB Python SDK

## Table of contents

1. [Start with the complete build-to-install flow](#1-start-with-the-complete-build-to-install-flow)
2. [Where the Python and Rust code lives](#2-where-the-python-and-rust-code-lives)
3. [Which work belongs to the SDK team and which belongs to Central](#3-which-work-belongs-to-the-sdk-team-and-which-belongs-to-central)
4. [Why both setup.py and pyproject.toml exist](#4-why-both-setuppy-and-pyprojecttoml-exist)
5. [Files that control the Rust build](#5-files-that-control-the-rust-build)
6. [How Cargo builds the Rust extension](#6-how-cargo-builds-the-rust-extension)
7. [Building for local development](#7-building-for-local-development)
8. [Building and checking a wheel locally](#8-building-and-checking-a-wheel-locally)
9. [What goes inside the wheel](#9-what-goes-inside-the-wheel)
10. [Why one release needs several wheels](#10-why-one-release-needs-several-wheels)
11. [How QueryPlanInterop reaches the wheel and the running SDK](#11-how-queryplaninterop-reaches-the-wheel-and-the-running-sdk)
12. [How the pipeline builds and releases the complete wheel set](#12-how-the-pipeline-builds-and-releases-the-complete-wheel-set)
13. [What Contoso Bank installs](#13-what-contoso-bank-installs)
14. [What changes if we also publish a source distribution](#14-what-changes-if-we-also-publish-a-source-distribution)
15. [What still needs to be decided or proved before release](#15-what-still-needs-to-be-decided-or-proved-before-release)

## 1. Start with the complete build-to-install flow

The SDK team and the customer have different jobs. We will use Contoso Bank
as the customer throughout this guide. Its **customer app** is the bank's
application code; the **SDK** is the complete Azure Cosmos DB package that
application installs and uses.

**The SDK team prepares and tests the package. Contoso Bank installs that
package and uses it in its customer app.** We want the normal customer
installation to remain straightforward even though the SDK now contains Rust.

The SDK team first **builds a wheel**: it turns source code and packaging
instructions into a `.whl` archive prepared for installation. An **archive**
groups several files into one file for storage or delivery.

The team then installs that wheel into a test **Python environment**: the
Python interpreter and the packages available to it. If the required checks
and approvals pass, the release
process **publishes** the wheel, making it available through a package service.

Contoso Bank can then use **pip**, Python's installation tool, to select and
install the package. Pip normally obtains public packages from **PyPI**, the
Python Package Index, unless another source is configured.


### What changes when we add Rust?

The existing pure-Python SDK wheel packages Python files and supporting data.
The Rust-backed wheel also needs a **compiled extension**: a file containing
machine code that Python can load. **Compilation** turns source code into
machine code, the instructions a processor executes. This guide uses
**native code** to mean compiled code built for a particular operating system
and processor.

The Python files remain Python files. We are adding a compiled component, not
converting the whole Python SDK into Rust machine code.

The overall process becomes:

```text
SDK team maintains Python and Rust source
    -> compile the Rust component
    -> package it with the Python SDK files
    -> install and test the resulting wheel
    -> repeat for the required operating systems and processors
    -> complete release checks and publish the approved files

Contoso Bank
    -> installs a compatible wheel
    -> runs its application using the installed SDK
```

A **build target** is an operating-system and processor combination, such as
Windows x64. A **platform wheel** contains compiled code for such a target.
The processor labels x64 and ARM64 identify different machine-code families.
One compiled file cannot serve both simply because the Python source is the
same.



## 2. Where the Python and Rust code lives

Before asking how to compile the SDK, we need to identify what we are compiling.
A **binding** is code that makes one language's functionality callable from
another language. Here, the binding connects Python to Rust.

The Rust-backed path has three source components:

```text
customer app
    -> Python wrapper prepares the operation
    -> Python/Rust binding calls the Rust driver
    -> Rust driver sends requests to the service backend
```

A **Rust crate** is a Rust project containing source and build information.
**Cargo** is Rust's build tool; it understands those projects and builds them.
A **dependency** is another library our code needs. The Rust driver is a
dependency of our binding, even though its source lives in a different
repository.

| Component | Where its source is maintained | Its job |
|---|---|---|
| Python wrapper | Python repository: `sdk\cosmos\azure-cosmos\azure\cosmos` | Our Python code: accepts customer arguments, prepares calls, and returns Python results or exceptions |
| Python/Rust binding, `azure_cosmos_rust` | Python repository: `sdk\cosmos\azure-cosmos\azure_cosmos_rust` | Our compiled extension: converts Python inputs into Rust driver calls and converts their results back |
| Rust driver, `azure_data_cosmos_driver` | Rust repository: `sdk\cosmos\azure_data_cosmos_driver` | A separately owned dependency: manages connections, routes requests, and applies its retry rules |

The **service backend** is the remote Cosmos DB service, not another component
inside the Python package.
The SDK's **public API** is the set of classes, methods, and options exposed
to the customer app.
In code explanations, use the layer names above so ownership stays clear.
For example, `_backend\binding_adapter.py` and its `BindingAdapter` class are Python
wrapper code; the compiled Python/Rust binding is exposed as `azure.cosmos._rust`.

The release will use the Rust driver for operations. Private switches that
still select the legacy Python implementation in this checkout are migration
test controls to remove before release, not customer options.

The **package source directory** in this guide means:

```text
azure-sdk-for-python\sdk\cosmos\azure-cosmos
```

The build also needs **package metadata**: information describing the package,
such as its name, version, and dependencies, rather than the implementation
of its operations.

Inside the package source directory, the important layout is:

```text
azure\cosmos\                    Python wrapper files
azure_cosmos_rust\
    Cargo.toml                  binding configuration
    src\                        binding Rust source
    build.rs                    checks performed during the Rust build
    query_plan_binary.rs        supporting compiled-file checks
Cargo.toml                      shared Rust configuration
Cargo.lock                      selected Rust dependency versions
rust-toolchain.toml             selected Rust build tools
pyproject.toml                  Python package and build settings
setup.py                        metadata compatibility for repository tools
azure_cosmos_build_backend.py    SDK-specific packaging helper
scripts\                        build-tool setup scripts
```

We will explain the configuration files individually rather than treating
this list as instructions to memorize.

### How the build obtains the Rust driver

The driver stays in the Rust repository. It is not copied into the Python
repository as another maintained source directory.

The current configuration tells Cargo to fetch a specific Git revision of the
driver. A **Git revision** identifies a particular source snapshot. The
package-level `Cargo.toml` selects the revision, and `Cargo.lock` records the
resolved dependency.

**Checkout reviewed on October 22, 2026:** the driver is `1.1.0-beta.1`, a
preview rather than a stable release, at revision
`84e2bb66c9911fa730dc9756c8fc3f9612456344`. Both the driver and its
`azure_data_cosmos_macros` dependency resolve to this revision.

The revision selection is often called a **pin**: builds request that
specific source snapshot. Updating a neighboring Rust checkout alone does
not update the Python extension:
the SDK team must change the pin, update the lockfile, rebuild the binding,
and install the resulting extension before Python can use the new code.

For the final release, our plan calls for an approved driver version published
on **crates.io**, the public registry from which Cargo downloads Rust source
packages. A stable SDK release must use an approved stable driver, not a
preview dependency.

Cargo downloads driver source and compiles it with the binding. A customer
installing our wheel does not separately install a Rust driver package.

## 3. Which work belongs to the SDK team and which belongs to Central

**A pipeline** is an automated sequence of work, such as building and testing
a package. The SDK owns the Cosmos entry file, `sdk\cosmos\ci.yml`, but that
file delegates most work to Central's shared pipeline files.

The **continuous integration**, or **CI**, pipeline checks code changes by
building and testing them. Azure DevOps is the service that schedules and
runs this pipeline.

Before looking at ownership, distinguish its three levels:

| Level | What it groups | Example |
|---|---|---|
| **Stage** | A broad part of a pipeline run | Build the packages and run required checks |
| **Job** | A unit of work assigned to a build environment | Build the Windows wheels |
| **Step** | One operation inside a job | Install build tools, then run the package-build command |

Steps in a job run in order. Jobs can run in parallel when their declared
dependencies allow it and suitable build capacity is available. A job that
tests a wheel must wait for the job producing that wheel.

The `.yml` files use **YAML**, a text format for structured settings.
A **shared template** is a reusable file of pipeline instructions. The Cosmos
entry file selects shared templates and supplies their inputs, rather than
maintaining a separate copy of every job and step.

### The SDK-owned files

The following paths are relative to the package source directory:

| File or area | What the SDK team controls there |
|---|---|
| `azure\cosmos`, `azure_cosmos_rust\src` | Python and binding implementation |
| `setup.py`, `MANIFEST.in` | Metadata compatibility and legacy source-file rules; the Rust-backed build uses Maturin, introduced in section 4 |
| `pyproject.toml` | Package information, selected build tools, and requested platform builds |
| Both `Cargo.toml` files and `Cargo.lock` | Rust dependencies and the selections used by builds |
| `rust-toolchain.toml`, `scripts\*.sh` | Selected Rust tools and the prototype's setup scripts |
| `azure_cosmos_build_backend.py` | SDK-specific preparation around the wheel build |
| `azure_cosmos_build_metadata.py` | Version checks shared by the Rust-backed and setuptools build routes |
| `azure_cosmos_rust\build.rs`, `query_plan_binary.rs` | Checks on supplied compiled libraries |
| `tests` | Packaging checks and tests of installed SDK behavior |


### The Central-owned files

Central maintains the shared files under `eng\pipelines\templates` and the
build tools under `eng\tools\azure-sdk-tools`. Shared engineering also maintains
`eng\common` and the shared Sphinx configuration under `doc\sphinx`.

For example, the SDK can declare:

> "We need a Windows ARM64 wheel."

Central must arrange the environment that can build it and the environment
that can execute its required tests. A setting in a package file does not
create either environment.


Ownership also does not override source-branch selection. A run using a
particular branch uses that branch's same-repository SDK files and shared
templates. Required Central-owned changes must therefore be available in the
source used by the run, not merely present in someone else's branch.

**Integration status after the October 22, 2026 rollback:** this branch keeps
the SDK-owned implementation and configuration, but its additional changes
under `eng` and `doc\sphinx` have been removed for Central to implement.
Existing shared Rust build support remains. The
[pending Central work](#central-changes-still-required) must not be mistaken
for functionality enabled by an SDK setting alone.

## 4. Why both setup.py and pyproject.toml exist

**Both files existed before the Rust integration, but they had different jobs.
With Rust, we are expanding what `pyproject.toml` controls, not introducing it
for the first time.**

Existing pure-Python production branches retain their packaging path. In this
Rust-backed source tree, however, every distributable wheel must contain the
Rust extension. Keeping `setup.py` for metadata must not create a second build
route that silently omits it.

### Before Rust: setup.py controlled packaging

The SDK team needed to collect the Python SDK files and prepare the wheel and
source archive that customers could install. These are different outputs:
a wheel supplies installation-ready files; a **source distribution**, or
**sdist**, supplies source files and instructions for building a wheel.
Section 14 covers the extra requirements for building from Rust-backed source.

The legacy Cosmos build used **setuptools**, an open-source Python packaging
tool. Setuptools is not Cosmos-specific, and it is still maintained. "Legacy"
here describes our existing Cosmos packaging process, not the tool itself.

Our `setup.py` supplied instructions to setuptools, such as:

> "Call this package `azure-cosmos`. Read its version from `_version.py`.
> Include these Python packages and data files. Declare these dependencies
> and Python requirements."

The legacy build commands followed this path:

```text
Build command
    -> setup.py supplies the package instructions
    -> setuptools performs the packaging
    -> a pure-Python wheel or source archive is produced
```

`setup.py` is Python code used during packaging. It is not code that
Contoso Bank calls when its customer app uses the installed SDK.

### Before Rust: pyproject.toml held other tool settings

The pre-Rust `pyproject.toml` was **already used**, but it did not direct the
Cosmos package build. TOML is the format used to write these settings; it is
not a tool that runs the build.

The file contained settings such as:

```toml
[tool.azure-sdk-build]
mypy = true
pyright = false
pylint = true

[tool.azure-sdk-conda]
in_bundle = false
```

The first section selected which repository code checks were enabled.
`mypy` and `pyright` check whether values are used consistently with their
declared **types**, the kinds of values the code expects. `pylint` checks code
for likely mistakes and rule violations.
These tools inspect code; they do not compile Rust or assemble a wheel.

The second section was for **Conda**, a separate package and environment
manager. This setting concerns the Conda distribution process, not how we
compile Rust or build a wheel for pip.

That file did not yet contain `[project]` package information or
`[build-system]` build instructions.

So the responsibilities were:

```text
setup.py
    -> describes the package to setuptools

pyproject.toml
    -> configures repository checks and other tooling
```

The important distinction is **"not used to direct packaging," rather than
"not used."**

### With Rust: pyproject.toml also controls the new build path

A Rust-backed wheel requires more than collecting Python files. The build must
compile the Rust code and include the resulting Python-loadable extension.

For this path, we use **Maturin**, an open-source tool for building Python
packages containing Rust code. Maturin invokes Cargo and packages the compiled
extension together with the Python files.

A **build backend** is the component a Python build tool calls to create the
package. Our backend is an SDK-owned helper that prepares the inputs and
calls Maturin. Its exact configuration is explained below.

Our `pyproject.toml` retains the existing repository settings and adds these
responsibilities:

| Section | What it tells the build tools |
|---|---|
| `[project]` | "The customer-facing package is `azure-cosmos`. Here are its version, Python requirements, and dependencies." |
| `[build-system]` | "Call this component to carry out the package build." |
| `[tool.maturin]` | "Here is the Rust binding to compile, the Python source to include, and the extension's Python import name." |
| `[tool.cibuildwheel]` | "Here are the platform wheel builds that our automated build process should coordinate." |

The Python package information matters because the internal Rust binding has
its own name and version. Customers are installing `azure-cosmos`, not a
separately named Rust package.

### How package metadata and the running SDK keep the same version

Suppose Contoso Bank installs the approved v5 wheel. Here, **v5** means major
version 5, the first number in the release version. This is the intended
upgrade that can change previously supported behavior.

The version recorded in the wheel must agree with the version reported by the
installed SDK. Otherwise the installer can report one release while the
customer app is running code labelled as another.

The current source still declares `4.17.2`. That is development metadata, not
the release identity for this breaking upgrade. The
[v5 release requirement](#treat-the-rust-backed-release-as-a-v5-upgrade)
must be satisfied before publication.

**`azure\cosmos\_version.py` is the version authority.** The other release
files carry copies or descriptions of that version:

| File | What its version means |
|---|---|
| `azure\cosmos\_version.py` | The Python SDK version, currently `4.17.2` |
| `pyproject.toml`, `[project].version` | The package version Maturin puts in distribution metadata |
| `api.metadata.yml`, `packageVersion` | The package version associated with the API metadata |
| The first release heading in `CHANGELOG.md` | The release described by the newest notes |

`setup.py` obtains the version from the SDK-owned version-check helper, which
reads `_version.py` without loading the SDK itself. Maturin still reads the
static copy in `pyproject.toml`. The Rust binding crate's version is separate and
does not determine the Python package release.

### Updating a release without leaving stale copies

The SDK records that it needs synchronized version updates:

```toml
[tool.azure-sdk-build]
synchronize-version-metadata = true
```

**Pending Central work:** the restored shared versioning tools do not
implement this setting. Setting it to `true` does not currently make a
version command update all four files.

Central needs to extend the shared commands so one approved version update
also synchronizes the static package version, API metadata, and newest
changelog heading. The stability **classifier**, a metadata label identifying
a stable or beta release, must also agree in `setup.py` and `pyproject.toml`.

After that support is integrated, the intended workflow is to approve the
exact v5 version and release date, then run the following command from the
package directory. Replace the placeholders with the approved values, using
`YYYY-MM-DD` for the date:

```powershell
sdk_update_version --package-path . --version "<approved-v5-version>" --release-date "<approved-release-date>"
```

This is the intended synchronized-update workflow, not a claim that the
current command implements it. It does not publish a package.

The same synchronization is needed in `sdk_set_version`,
`sdk_increment_version`, and `sdk_set_dev_version`, including development
changelog updates. Central's implementation must restore the original files
and fail if an update or validation step fails, rather than leave a partially
updated version.

Until that integration is available, the release owner must keep all four
version files and the stability classifiers aligned explicitly. The SDK's
existing build validation still rejects disagreements; it does not update
the files. Complete the version update before starting builds.

### What happens if someone changes only one file?

Before calling Maturin, our build backend checks all four versions. The
setuptools route performs the same check before calling `setup()`. A mismatch
stops the build with the disagreeing filenames and versions; it does not
silently select one copy or repair the checkout during packaging.

The check also runs when preparing source archives, installing a checkout
for development, or answering package-information requests. Source archives
include the helper and its metadata inputs so a later build from the archive
can perform the same check. Packaging tests verify that a mismatch is rejected
before either builder is called.


### What the SDK-owned build helper does

Our `[build-system]` section selects:

```toml
build-backend = "azure_cosmos_build_backend"
```

This selects our SDK-owned Python file as the build backend:

```text
azure_cosmos_build_backend.py
```

The setting means:

> "When asked to build this package, call our helper file. That helper will
> perform our package-specific preparation and then ask Maturin to build
> the wheel."

The helper exists because we have an additional preparation step for
**QueryPlanInterop**, a separate compiled library that can create database
query plans: instructions for coordinating a query, not the query's returned
data. Its detailed purpose and delivery are covered in
[section 11](#11-how-queryplaninterop-reaches-the-wheel-and-the-running-sdk).

For a wheel build, the helper's added work is:

```text
Check that the SDK version and release metadata agree

If matching QueryPlanInterop files were supplied:
    temporarily copy them into the Python package directory

Call Maturin to build the wheel

Remove the temporary copies from the source checkout
```

The completed wheel retains the packaged files. The cleanup affects the
temporary source-checkout copies.

**The helper does not replace Maturin or compile Rust itself.** If no
QueryPlanInterop files are supplied, the current helper skips that preparation
and still calls Maturin.

### What cibuildwheel does

**`cibuildwheel` is an open-source tool that coordinates building and testing
Python wheels across different platform and Python environments.** It is not
a Cosmos script or an Azure DevOps service.

It addresses a different problem from Maturin:

> "We can build one Rust-backed wheel. How do we repeat the appropriate build
> for all our configured platforms?"

For example:

```toml
[tool.cibuildwheel.windows]
archs = ["AMD64", "ARM64"]
```

This tells `cibuildwheel` to target Windows x64 and Windows ARM64.

`[tool.cibuildwheel]` is simply the section containing its settings. The section
does not run anything by itself. Central arranges the build jobs and invokes
the tool in suitable environments.

The new responsibilities fit together as follows:

```text
Azure DevOps pipeline
    -> supplies and starts the build jobs

cibuildwheel
    -> coordinates the configured wheel builds within those jobs

SDK-owned build helper
    -> prepares supplied QueryPlanInterop files for each wheel

Maturin
    -> invokes Cargo and packages the Python files with the Rust extension

Cargo and the Rust compiler
    -> build the Rust code
```

### Why setup.py must remain

Repository tools still inspect setuptools metadata, such as the package name,
version, and dependencies. **In this Rust-backed tree, `setup.py` is a
metadata-only compatibility entry point, not an alternative package builder.**

Without that boundary, `python setup.py bdist_wheel` can package the Python
files and `_rust.pyi` without compiling Rust. The resulting same-version
`py3-none-any` wheel looks installable but lacks the compiled extension.
`any` identifies a wheel that claims no operating-system or processor
restriction, which is wrong for this compiled SDK. The `.pyi`
file describes the interface for developer tools; Python cannot execute it
as the Rust extension.

| Command | Behavior in this Rust-backed tree |
|---|---|
| `python setup.py --name` or `--version` | Returns package information. |
| `python setup.py egg_info` or `dist_info` | Produces metadata for compatible tooling. |
| `python setup.py bdist_wheel`, `sdist`, or other build/install commands | Fails before executing commands and directs the caller to the supported build path. |
| `python -m build --wheel` or `--sdist` | Uses the configured backend, which delegates native packaging to Maturin. |
| `python -m pip install -e .` | Uses the configured backend to install the checkout for development, explained in section 7. |

A mixed command such as `python setup.py egg_info bdist_wheel` also fails
before either command runs. Keeping the metadata commands available does
not permit an incomplete setuptools source archive or Rust-less wheel.

This restriction applies to the Rust-backed source tree, not the historical
pure-Python production branch. Package metadata in `setup.py` and
`pyproject.toml` must still agree.

## 5. Files that control the Rust build

Before the SDK team can build a Rust-backed wheel, the build needs answers to
three questions:

1. Which Rust code should we build, and which libraries does it need?
2. Which exact versions of those libraries should we use?
3. Which Rust compiler should build them?

These are separate decisions. Choosing a driver version does not choose a
compiler, and choosing a compiler does not fix the versions of every library.

The files below record those decisions so developers and pipeline builds do
not have to make them from scratch each time.

### Start with the files and their responsibilities

Cargo manages the Rust build and its dependencies. It obtains their source
and invokes **`rustc`**, the
Rust compiler, to compile the code.

The relevant files are inside the package source directory:

| File | Question it answers |
|---|---|
| `Cargo.toml` | "How is the Rust work organized, and which settings and dependency declarations are shared?" |
| `azure_cosmos_rust\Cargo.toml` | "What is our Python-facing Rust binding, and what does it need to build?" |
| `Cargo.lock` | "Which exact dependency versions and sources have been selected?" |
| `rust-toolchain.toml` | "Which Rust build tools should this checkout use by default?" |

There are two files named `Cargo.toml`, but they do not have the same job.

### The package-level Cargo.toml: shared settings

The file at:

```text
sdk\cosmos\azure-cosmos\Cargo.toml
```

defines a **workspace**. In Cargo, a workspace is a collection of Rust projects
managed together, with shared settings and a shared lock file. It can contain
just one project.

Our workspace currently declares:

```toml
[workspace]
members = ["azure_cosmos_rust"]
resolver = "2"
```

The `members` line says:

> "The Rust project in the `azure_cosmos_rust` directory belongs to this
> workspace."

That project is our binding. The driver is an external dependency, not a
second member of this Python repository's workspace.

`resolver = "2"` selects Cargo's rules for combining dependencies and their
optional capabilities. It is
not a Rust compiler version. We do not need the detailed rules here to
understand the file's purpose.

The package-level file provides settings that the binding can reuse:

- The driver's source location and selected Git revision.
- Dependency version requirements.
- The declared minimum Rust compiler version.
- Information such as the license and authors.

For example, it contains:

```toml
[workspace.dependencies]
tokio = "1"
```

**Tokio** is a Rust library used by the binding to run asynchronous work:
work that can wait for a network response without preventing other scheduled
work from progressing.

This declaration permits compatible Tokio versions in the `1.x` series. It
does not mean "download the newest Tokio version on every build." The exact
selection is recorded separately in `Cargo.lock`.

### The binding's Cargo.toml: what this Rust project needs

The second file is:

```text
sdk\cosmos\azure-cosmos\azure_cosmos_rust\Cargo.toml
```

It describes the actual binding project: its name, the library it builds, and
the dependencies it uses. Cargo documentation calls a `Cargo.toml` file a
**manifest**: the file describing a Rust project or workspace.

The binding can reuse a declaration from the package-level file:

```toml
tokio = { workspace = true, features = ["rt-multi-thread", "macros"] }
```

Read this as:

> "This binding needs Tokio. Use the dependency declaration from the
> workspace, and enable these additional Tokio capabilities."

A **feature** is a named switch enabling optional functionality in a Rust
library. The `features` list selects capabilities, not a different library
version.

`workspace = true` explicitly requests the shared declaration. Putting a
dependency in the workspace file does not automatically make every member
use it.

This explains why the two files are not duplicates:

```text
Package-level Cargo.toml
    -> provides shared settings and dependency declarations

Binding's Cargo.toml
    -> declares what the binding uses
    -> reuses selected settings from the package-level file
```

Normal and test-related driver dependencies use the same shared source.
The normal dependency enables these driver features:

```toml
features = ["__internal_native_query_plan", "fault_injection", "unstable_patch"]
```

The first two enable native query-planning integration and **fault injection**,
deliberately introducing failure conditions to test how the SDK responds.
A **patch** changes selected fields of an item rather than replacing the
whole item. `unstable_patch` enables patch-strategy configuration: the binding
uses it to select service-side evaluation when a patch includes a condition.
Core patch support remains available in the driver without that feature.

**Unfinished test migration:** the current test dependency still enables
`__internal_in_memory_emulator`, a Rust test substitute that keeps simulated
service state in memory. The agreed direction is to replace those tests with
Windows Cosmos DB Emulator coverage against a separately running local
service, not retain this substitute. The feature
must be removed after the dependent tests are migrated; its presence is not
evidence that Windows-emulator coverage has run.

The pinned driver declares `unstable_patch`, not `preview_patch`. The build
configuration test checks the exact feature set, so a stale expected name
rejects the configuration even when Cargo uses the intended feature.
When changing the driver revision, check its declared features and keep the
binding manifest and test expectation aligned; do not weaken the assertion
to accept arbitrary feature names.

The binding and driver also exchange values defined by the `azure_core` Rust
library. If the binding creates a value using one copy of that library but
the driver expects the type
from a different copy, the compiler can reject the call even when the types
have the same name. Their dependency selections must therefore allow them to
use the same crate's types.

### Cargo.lock: the exact dependency selections

Knowing that we allow Tokio `1.x` is not enough to identify which version a
particular build should use. That is the job of `Cargo.lock`.

In the checked-out files:

```text
Cargo.toml
    -> allows Tokio "1"

Cargo.lock
    -> records Tokio 1.52.3
```

The version shown is the checkout's selection, not a claim about the newest
available release.

The lock also records dependencies needed by our dependencies. For example,
the binding needs the driver, and the driver needs other libraries. Those
additional libraries are **indirect dependencies**.

**Cargo generates and maintains `Cargo.lock`; we should not manually edit its
dependency entries.** Checking it into Git lets builds reuse the reviewed
selections rather than independently choose versions.

A lock file does not promise byte-for-byte identical builds. Compiler versions,
target platforms, and other inputs still matter. Nor does it freeze files in
a developer's local path override: those source files can still change.

### How we prevent a build from silently changing dependencies

Our Maturin configuration in `pyproject.toml` includes:

```toml
[tool.maturin]
locked = true
```

For our wheel build, this means:

> "Use the existing lock file. If the build cannot proceed without changing
> it, stop with an error instead of quietly choosing another dependency set."

A direct Cargo command expresses the same requirement with `--locked`.
The build fails if the lock is missing or dependency resolution requires
changing it.

**Locked does not mean offline.** Cargo can still download the already-selected
dependency sources if the machine does not have them. The lock controls which
dependencies are used, not whether the build needs network access.

This separates two activities:

| Activity | Expected behavior |
|---|---|
| Building a wheel from reviewed source | Reuse the checked-in dependency selections |
| Deliberately updating dependencies | Let Cargo update the lock, review the changes, and commit them |

For example, when changing the driver:

```text
Change the dependency declaration
    -> use Cargo to resolve the updated dependencies
    -> review the resulting Cargo.lock changes
    -> test the SDK
    -> commit the configuration and lock changes together
```

A normal build does not update everything merely because newer versions exist.
Cargo provides `cargo update` for requesting dependency updates.

The team must also confirm automated update coverage. **Dependabot**, GitHub's
dependency-update service, is one possible mechanism for proposing changes
through pull requests. A locked build prevents unreviewed changes during
packaging; it does not replace dependency maintenance.

### rust-toolchain.toml: selecting the build tools

So far, the files have described source code and library versions. We still
need the programs that compile that source.

A **Rust toolchain** includes Cargo, `rustc`, and the Rust **standard library**,
the basic support code supplied with Rust rather than obtained as a separate
project dependency.
Our `rust-toolchain.toml` currently contains:

```toml
[toolchain]
channel = "ms-prod-1.97"
profile = "minimal"
```

The `channel` selects the default toolchain for this prototype.
`ms-prod-1.97` is an internal Microsoft toolchain channel. It requires
**msrustup**, Microsoft's internal toolchain manager. The public toolchain
manager, **rustup**, cannot resolve this internal channel.

The file records the choice; developer environments and pipeline machines
still need the installation setup and access. The channel is not an immutable
compiler patch-version pin, so release builds must also record the actual
toolchain used.

`profile = "minimal"` requests basic compilation components rather than
additional tools and documentation. **It does not mean "produce a smaller
wheel" or "compile without optimization."** Installation profiles and
compilation optimization settings are different things.

### Why rust-version and rust-toolchain.toml are different

The package-level `Cargo.toml` also contains:

```toml
[workspace.package]
rust-version = "1.75"
```

The binding inherits that value. It answers a different question:

| Setting | Meaning |
|---|---|
| `rust-version = "1.75"` | "This project declares Rust 1.75 as its minimum supported compiler." |
| `channel = "ms-prod-1.97"` | "Use this selected toolchain by default for our current builds." |

**Declaring a minimum does not install or select that compiler.**

If a wheel builds successfully with the selected 1.97 toolchain, that does not
demonstrate that Rust 1.75 can build the same source. The driver or another
dependency may require a newer compiler. Validate the minimum against the
complete dependency set, or update the declaration.

The distinction to retain is:

```text
Cargo.toml
    -> what our Rust code needs

Cargo.lock
    -> the exact dependencies selected

rust-toolchain.toml
    -> the build tools selected

rust-version
    -> the minimum compiler compatibility we declare
```

These are SDK build concerns. Contoso Bank does not need the tools when
installing a compatible prebuilt wheel. Customer source installation, if
supported, needs its own accessible toolchain path; it cannot assume access
to our internal Microsoft toolchain.

## 6. How Cargo builds the Rust extension

The configuration now identifies the source, dependencies, and compiler.
The next question is:

> "How do the binding and driver become a file that Python can import?"

An **import** makes a Python **module**, a unit of code, available to the
running Python program. A module can come from a Python source file or a
compiled extension. Here, the module we need to produce is `azure.cosmos._rust`.

Cargo handles the Rust build, but it does not by itself assemble our Python
wheel. This section follows the boundary between compilation and packaging.

### First, create a library Python can load

The binding's `Cargo.toml` contains:

```toml
[lib]
name = "azure_cosmos_rust"
crate-type = ["cdylib"]
```

A **dynamic library** is compiled code another program can load while running.
`cdylib` tells Cargo to create a library suitable for use by software outside
Rust, rather than a standalone command-line application.

That library also needs to understand Python's calling conventions.
**PyO3** is the open-source Rust library that supplies the Python/Rust
interface. It helps expose Rust functions and types to Python, receive Python
arguments, return Python objects, and report Python exceptions.

PyO3 is code compiled into the binding. It is not another command we run to
create the wheel.

### Cargo builds dependencies before the code that needs them

The compiler turns Rust source into machine code. A **linker** combines the
required compiled pieces and library references into the final loadable file.

The build follows the dependency relationships:

```text
Cargo reads the binding configuration and shared workspace settings
    -> uses Cargo.lock to resolve the selected dependency sources
    -> obtains any sources not already available
    -> invokes rustc for the required crates
    -> links the binding and driver code into a dynamic library
    -> writes Rust build outputs under target\
```

A dependency needed by the driver must be available before the driver can
finish building. The binding, in turn, depends on the driver.
Cargo manages this ordering; we do not manually compile the libraries one
by one.

The important result for the Python package is:

```text
compiled binding code + compiled driver code
    -> one Python extension
```

We do not ask Contoso Bank to install a separate compiled driver alongside it.
QueryPlanInterop is different: it remains a separate library and is covered
later.

### Maturin gives the result its place in the Python package

Cargo knows how to build Rust projects. Maturin knows how the compiled result
belongs in this Python package.

Our `pyproject.toml` provides:

```toml
[tool.maturin]
manifest-path = "azure_cosmos_rust/Cargo.toml"
python-source = "."
module-name = "azure.cosmos._rust"
features = ["pyo3/extension-module"]
locked = true
```

Read the settings in terms of the work Maturin needs to do:

| Setting | Instruction |
|---|---|
| `manifest-path` | "Build this Rust binding project." |
| `python-source` | "Find the Python source starting in this directory." |
| `module-name` | "Make the compiled result importable as `azure.cosmos._rust`." |
| `features` | "Enable PyO3's Python-extension build behavior." |
| `locked` | "Do not silently change Rust dependency selections." |

The final `_rust` part must match the Python module name declared in
`azure_cosmos_rust\src\lib.rs`. Its `#[pymodule]` declaration is how the binding
identifies the module to PyO3.

Maturin places the extension under the Python package using the appropriate
filename:

| Target operating system | Extension location |
|---|---|
| Windows | `azure\cosmos\_rust.pyd` |
| Linux and macOS | `azure\cosmos\_rust.abi3.so` |

Python can then import it with:

```python
from azure.cosmos import _rust
```

The `abi3` name relates to Python-version compatibility; section 10 explains
it. For now, the distinction is that Cargo produces the compiled code and
Maturin prepares it for Python.

There are then two useful workflows: install the development checkout for
editing, or create a distributable wheel. They use the same source but answer
different questions.

## 7. Building for local development

Suppose an SDK developer changes the Rust binding and wants to try that change
immediately. Repeatedly building, locating, and installing a release-style
wheel would be inconvenient.

Maturin provides a development workflow:

```powershell
maturin develop --release
```

This makes the SDK available in the developer's active Python environment.
It is not the process for collecting release wheels.

### Prepare the environment before running the command

A **Python virtual environment** gives the project its own Python package
installation area. Using one keeps the SDK and its Python dependencies
separate from unrelated projects.

For the current configuration, the developer needs:

- A suitable Python environment for the prototype's Python 3.10 minimum.
- The selected Rust toolchain, with the required internal setup and access.
- The operating system's required compiler/linker tools.
- Access to the selected driver and other Rust dependency sources.

The package configuration does not require a neighboring Rust repository.

Activate the intended virtual environment, then run these commands from the
package source directory:

```powershell
python -m pip install "maturin==1.15.0"
maturin --version
Get-Command maturin
maturin develop --release
```

The current build configuration selects Maturin `1.15.0`. Confirm that the
command resolves to that version in the intended environment. Installing a
tool into one environment does not ensure a different shell finds it.

`--release` requests optimized Rust code. It does not mean the SDK is being
published or approved for production.

### What changes after the command succeeds?

The installation is **editable**: the Python source continues to come from
the checkout rather than a separately installed release copy.

| Developer change | What is needed before trying it |
|---|---|
| Change Python source | No Rust rebuild is needed just for that Python edit; run with the updated source |
| Change Rust source or relevant Rust build settings | Rebuild the extension |

This is useful for development, but it introduces an important limitation:

> "A working checkout does not prove that our wheel contains everything
> another machine needs."

The development environment may contain source files, dependencies, or local
libraries that are missing from the wheel.

### The custom wheel helper is not involved

This command calls Maturin directly. It does not invoke
`azure_cosmos_build_backend.py` to stage QueryPlanInterop files.

If a developer needs that particular query-planning library, the running SDK
must be pointed at an appropriate external library directory, as described in
[section 11](#11-how-queryplaninterop-reaches-the-wheel-and-the-running-sdk).
Do not use the setting that selects files for a wheel as a substitute for
the setting that tells the running SDK where to find the library.

For packaging validation, move to the next workflow: build a wheel, then test
what was installed from that wheel.

## 8. Building and checking a wheel locally

Now the SDK developer asks a different question:

> "If I hand this wheel to another machine, does it contain an installable SDK?"

That requires testing the archive, not merely using the development checkout.

### The command that starts the build

The **Python `build` package** is an open-source tool invoked as
`python -m build`. It starts a package build by calling the backend selected
in `pyproject.toml`.

This initiating role is called a **build frontend**. The frontend starts the
work; the backend implements the package build. In our case, the backend is
the SDK helper that delegates to Maturin.

With the Rust and platform prerequisites from section 7 arranged, run from
the package source directory:

```powershell
python -m pip install build
python -m build --wheel
```

The result is a `.whl` file under `dist`. It is a local build output, not a
published release.

**The command builds the wheel; it does not install the SDK into the
developer's environment.**

### Why the build creates another Python environment

The developer's environment might contain a different Maturin version from
the one the package requires. By default, the frontend avoids depending on
that accidental setup.

It creates a temporary Python build environment and installs the dependencies
declared here:

```toml
[build-system]
requires = ["maturin==1.15.0"]
build-backend = "azure_cosmos_build_backend"
backend-path = ["."]
```

| Setting | Meaning |
|---|---|
| `requires` | "Install this Python build dependency for the build." |
| `build-backend` | "Call our SDK-owned helper." |
| `backend-path` | "Find that helper in the package source directory." |

Keeping those build dependencies separate is called **build isolation**.
The temporary environment creates the wheel; it is not Contoso Bank's
application environment.

```text
Developer's environment
    -> runs python -m build

Temporary build environment
    -> contains the declared Maturin version
    -> runs the configured helper and packaging work

dist\
    -> receives the completed wheel
```

Build isolation manages Python build dependencies. It is not a promise to
install the complete Rust toolchain, operating-system build tools, or
QueryPlanInterop. Arrange those inputs explicitly for this prototype.

If `--no-isolation` is used, the caller becomes responsible for installing
and selecting the correct Python build tools too.

### Follow one wheel through the build

For a Windows x64 example:

```text
python -m build --wheel
    -> reads [build-system]
    -> prepares the Python build environment
    -> calls azure_cosmos_build_backend.py
    -> the helper stages QueryPlanInterop if supplied
    -> Maturin invokes Cargo for the Windows x64 extension
    -> Maturin packages the extension, Python files, and package information
    -> writes the Windows x64 wheel under dist\
```

Calling `maturin build` directly bypasses our helper. Use the configured Python
build path when checking the wheel workflow, including its version checks and
optional staging. Direct `maturin develop` remains a local-development shortcut;
it does not run these release-metadata checks.

The helper also delegates source-archive, editable-build, and package-information
requests to Maturin. Its extra QueryPlanInterop staging is specific to the
wheel-building path.

### Inspect the archive, then install that exact file

Before returning a built wheel, the backend checks the actual archive for
exactly one nonempty `_rust` extension under `azure/cosmos`, with a `.pyd` or
`.so` suffix, and rejects an `any`-platform wheel. A wheel containing only
the `_rust.pyi` interface description, called a **type stub**, fails
even if importing the Python wrapper would succeed. The check accepts
target-platform extension names rather than relying on the build machine's
Python suffix, so wheels built for another processor can be checked too.

This archive check does not prove that the binary has the right architecture
or can load. Installation and native-import checks remain necessary.

Choose the exact wheel produced by the build. Do not accidentally inspect an
older wheel left in `dist`.

The following PowerShell example uses a filename placeholder; replace it
with the actual output:

```powershell
$wheel = (Resolve-Path ".\dist\<actual-wheel-name>.whl").Path
python -m zipfile --list $wheel
```

This lists the archive's files. Section 9 explains what each group is for.
File presence is useful evidence, but it does not prove compiled files can
load on the machine.

For that check, use a separate clean Python environment. The example assumes
`.wheel-test` does not already exist. If it does, choose a new directory name
and use that name in all three commands; creating a virtual environment over
an existing one does not establish a clean installation.

```powershell
python -m venv .wheel-test
.\.wheel-test\Scripts\python -m pip install $wheel
.\.wheel-test\Scripts\python -I -c "from azure.cosmos import _rust; print(_rust.__file__)"
```

The printed path must point inside `.wheel-test`.

Why use `-I`? It puts Python in an isolated mode that avoids using the current
source directory or extra search directories configured through `PYTHONPATH`
for this check. Otherwise, a test might import
the developer's checkout and accidentally report success without testing
the installed wheel.

The sequence establishes increasingly useful evidence:

```text
Archive contains the files
    -> pip can install it
    -> Python can load the installed extension
    -> SDK operations must still be tested
```

An import check does not create a database, run a query, or prove which query
planner ran. Functional tests must exercise those operations against the
installed wheel.

## 9. What goes inside the wheel

The wheel must carry the files the installed SDK needs, not just the compiled
Rust result.

A wheel is a ZIP archive. Here is the intended Windows layout. The `.libs`
part is the planned QueryPlanInterop addition, not a claim that the current
prototype already includes it:

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

The `<version>` text is a placeholder for the package version.

### The Python files are still part of the product

Files such as `cosmos_client.py` remain readable Python source. Compiling the
binding does not replace those files.

The wheel also carries **package data**: supporting files used by the SDK or
development tools. For example:

- `query_advice_rules.json` contains data used by the query-advisor feature.
- `py.typed` tells Python type-checking tools that the package provides typing
  information.
- `_rust.pyi` describes the extension's Python-facing types and functions for
  those tools; it is not the compiled extension itself.

Forgetting a data file can break a feature even when importing the SDK works.

### The extension is one compiled file for this target

On Windows, `_rust.pyd` contains the compiled binding and driver.
Linux and macOS use `_rust.abi3.so`.

Each wheel should contain exactly the extension intended for that wheel.
A stale extension left by an earlier local build must not be copied in as an
extra file or mistaken for the newly built result.

QueryPlanInterop is not folded into `_rust`. When included, it remains under
`.libs` with any required companion libraries.

### The installer also needs information about the package

The `.dist-info` directory carries the package metadata introduced in
section 2. The installer reads it to understand the package it is installing.
It also records file contents using **hashes**, values calculated from those
contents so tooling can detect changes.

| File | What it tells installation tooling |
|---|---|
| `METADATA` | Package name, version, Python requirement, and Python dependencies |
| `WHEEL` | Wheel-format details and compatibility information |
| `RECORD` | Records of packaged files, including hashes and sizes where applicable |

For example, the installer needs to know that it is installing `azure-cosmos`,
which version it is, and whether the current Python version is allowed.

Those values must agree with the SDK configuration. Correct Rust code packaged
under the wrong name or with incorrect requirements is still an incorrect
release file.

Archive checks should therefore inspect both implementation and metadata:
Python source, supporting data, the extension's architecture, planned native
companions, package information, and unwanted duplicate files or caches left
by earlier Python runs.

The next question is why we need several such archives for the same release.

## 10. Why one release needs several wheels

Suppose Contoso Bank develops on Windows x64 but runs its customer app on
Linux ARM64.

The Python source may be the same, but the two environments cannot load the
same compiled Rust file. Each environment needs machine code built for it.

This is why the Rust-backed release needs platform wheels rather than the
single platform-independent wheel used by the pure-Python package.

### The prototype's five targets

The current configuration selects:

| Operating system | Processor |
|---|---|
| Windows | x64 |
| Windows | ARM64 |
| Linux | x64 |
| Linux | ARM64 |
| macOS | ARM64 |

This is the experiment's target list, not an approved permanent support policy.
Final operating-system minimums and test coverage still require approval.

### Reading one filename

Consider this filename shape:

```text
azure_cosmos-<version>-cp310-abi3-win_amd64.whl
```

The last parts are **compatibility tags**: labels the installer compares with
the customer's Python and platform.

**CPython** is the standard Python implementation targeted by these wheels.
Other Python implementations exist, so a Python version number alone does
not describe every compatibility condition.

Compiled code also needs agreed rules for communicating with Python.
An **application binary interface**, or **ABI**, defines those low-level
calling rules. CPython's stable ABI allows a suitably built extension to
work across compatible Python versions rather than requiring a new binary
for each one.

| Part | Meaning |
|---|---|
| `azure_cosmos` | The distribution name corresponding to `azure-cosmos` |
| `<version>` | The release version |
| `cp310` | A CPython 3.10 compatibility baseline for this stable-ABI wheel |
| `abi3` | The extension uses CPython's stable binary interface |
| `win_amd64` | Windows x64 |

### Why we do not necessarily build a wheel for every Python version

An extension tied to a particular Python version can require separate builds
for different Python versions. CPython also offers the stable interface
called `abi3`.

Our PyO3 dependency enables:

```text
abi3-py310
```

This asks PyO3 to use that stable interface starting at Python 3.10.
For the same operating system and processor, the resulting extension can
serve later compatible CPython versions:

```text
One Windows x64 cp310-abi3 wheel
    -> test with CPython 3.10
    -> test the same wheel with later supported CPython versions
```

It does not turn a Windows wheel into a Linux wheel, nor does it automatically
approve support for every future Python version.

Three decisions remain separate:

| Setting or process | Question it answers |
|---|---|
| PyO3 `abi3-py310` | "Which stable binary interface does the extension use?" |
| `[project] requires-python = ">=3.10"` | "Which Python versions does the package metadata allow?" |
| SDK support policy and tests | "Which Python versions do we actually support?" |

An extension that imports successfully is not enough to establish full SDK
support on that Python version.

A **test matrix** lists the combinations that must be checked, such as
Windows x64 with Python 3.10 and Windows x64 with Python 3.13. Reusing one
wheel across those combinations reduces the number of files to build, not
the number of environments whose behavior must be verified.

### The operating-system part has compatibility limits too

The expected filename shapes for the prototype are:

```text
azure_cosmos-<version>-cp310-abi3-win_amd64.whl
azure_cosmos-<version>-cp310-abi3-win_arm64.whl
azure_cosmos-<version>-cp310-abi3-manylinux_2_28_x86_64.whl
azure_cosmos-<version>-cp310-abi3-manylinux_2_28_aarch64.whl
azure_cosmos-<version>-cp310-abi3-macosx_<minimum-version-tag>_arm64.whl
```

These are examples of the required shapes, not evidence that all five files
were produced and tested. The placeholders are not literal valid tags.

On Windows, `win_amd64` and `win_arm64` distinguish processors. They do not
state the minimum Windows release supported by the SDK.

On Linux, **glibc** is a common system library used by compiled programs.
The `manylinux_2_28`
tag identifies a compatibility baseline requiring glibc 2.28 or later on the
matching architecture. It is not a promise to support every Linux environment.

The prototype chooses prepared Linux build environments, called **build
images**, using that baseline. The binaries must satisfy the compatibility
rules; putting the tag in a filename is not proof.

On macOS, a **deployment target** records the minimum intended macOS version.
For example, `macosx_11_0_arm64` represents macOS 11.0 and Apple Silicon.
That is an explanatory example here. Inspect our actual build setting and
wheel before recording a confirmed minimum.

The experiment does not include Intel macOS, Python 3.9, PyPy (another Python
implementation), or musllinux wheels (a different Linux runtime family).

### Where the target list is declared

The relevant excerpt from `pyproject.toml` is:

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

This excerpt explains selection; it omits setup commands and environment
settings from the complete file. Central must supply the environments that
execute these builds and tests.

Every separate library added to a wheel must match the same target. That
requirement becomes important for QueryPlanInterop.

## 11. How QueryPlanInterop reaches the wheel and the running SDK

Suppose Contoso Bank stores orders in a Cosmos DB **container**, the service
resource holding those items. To handle data at scale, the service backend
distributes it across **partitions**, portions of the container's data.
A query may need results from several partitions rather than just one.

Before requesting those results, the SDK needs a **query plan** describing
which data ranges are relevant and how to process the combined results.

Creating that plan is different from executing the query and returning its
results. The driver can obtain a plan from more than one place.
The **gateway** is the service backend's front end; it can return a plan to
the SDK. That describes where the SDK obtains the plan, not which internal
service component generates it.

### There are three query-planning providers

A **provider** here means one implementation capable of supplying a query plan.

| Provider | Where it runs | What the installed package needs |
|---|---|---|
| QueryPlanInterop | Separate compiled library loaded on the application's machine | A matching library and its dependencies |
| Pure-Rust planner | Code compiled into the Rust driver inside `_rust` | No separate QueryPlanInterop library |
| Gateway plan retrieval | Service backend's gateway | A request to the gateway for a plan |

Here, **local** means on the customer app's machine, not in the remote
service backend. The **planning mode** selects which providers the driver may try.
The default `LocalPreferred` mode means the driver normally tries an enabled
QueryPlanInterop provider, then the pure-Rust planner, then the gateway.
The pure-Rust planner handles eligible query shapes, not every query.

Trying the next provider when the previous one cannot supply a plan is
**fallback**. `GatewayOnly` explicitly bypasses both local providers.
These are provider-selection rules, not a requirement that every query
contact every provider; the driver can recognize some queries as having
no possible results.

**No QueryPlanInterop library does not mean every query must use gateway
planning.** Eligible queries can still use the Rust planner already compiled
into the extension.

### Why QueryPlanInterop is a separate packaging task

The driver contains code that knows how to call QueryPlanInterop. That does
not mean it contains the compiled QueryPlanInterop library itself.

The library must be obtained from its producing team for each target:

| Target operating system | Primary library name |
|---|---|
| Windows | `Cosmos.QueryPlanInterop.dll` |
| Linux | `libqueryplaninterop.so` |
| macOS | `libqueryplaninterop.dylib` |

Some libraries also require **companion libraries**, other compiled files
they load. Those must be packaged or available through the supported operating
system.

Two files can have the same filename but target different processors.
A Windows x64 DLL cannot serve a Windows ARM64 wheel simply because both files
are named `Cosmos.QueryPlanInterop.dll`.

The current plan is to include QueryPlanInterop in later wheels. **Obtaining
and supplying these libraries is deferred and is not an immediate
prototype-wheel blocker.**
The producing team, approved source, matching versions, and distribution
permissions still need confirmation.

### Build time: tell the helper which files to include

An **environment variable** is a named setting made available to a running
process. Our helper reads:

```text
AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR
```

This means:

> "These are the already-built QueryPlanInterop files to include in the wheel
> we are creating."

After obtaining the approved files for the selected target, a local Windows
example would be:

```powershell
$env:AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR = "C:\path\to\queryplaninterop"
python -m build --wheel
```

The path is an example, not a known download location.

`azure_cosmos_build_backend.py` checks that the directory contains exactly one
primary library. It temporarily stages that library and the supplied native
companions under `azure\cosmos\.libs`, lets Maturin package them, and cleans up
its staged copies afterward.

An invalid supplied directory or invalid primary-library set is an error.
An absent source setting is different: the current backend skips staging and
can build a wheel without QueryPlanInterop.

The current pipeline does not yet deliver these binaries or forward this
source setting into Linux build containers. A **build container** is an
isolated environment used to run build tools with its own filesystem view.
It is unrelated to the Cosmos DB container holding Contoso Bank's orders.
The future setup must make both the files and the setting available inside it.
A path visible only on the host machine is insufficient.

### Build time: reject the wrong processor's file

Cargo runs `azure_cosmos_rust\build.rs` as part of building the binding.
When staging is active, it uses `query_plan_binary.rs` to inspect the supplied
compiled files.

A compiled file has a **header**, a part of the file that identifies properties
such as its format and processor. The checks compare those properties with
the build target and reject incompatible files.

They also require the target's primary filename and check Linux's 32-bit or
64-bit file class. Supplied native companions are checked as well.

This proves more than checking the filename, but less than executing a query.
Correct file headers do not establish that every dependency is present or
that the library can create a valid plan.

### Runtime: find the library beside the installed extension

**Runtime** means when Contoso Bank's customer app is using the installed SDK,
rather than when the SDK team is building it.

The runtime setting is different:

```text
AZURE_COSMOS_QUERYPLANINTEROP_DIR
```

It means:

> "Look in this directory when the driver needs to load QueryPlanInterop."

The Python helper in `azure\cosmos\_backend\_binding_adapter_shared.py` finds `.libs` beside
the imported `_rust` extension. If that directory exists, it supplies the path
to the driver unless the caller already provided an explicit runtime setting.

The desired customer experience is that a wheel containing the library finds
its own packaged copy. The customer should not have to locate it manually.

For editable development, where wheel staging was not performed, a developer
can point the runtime setting at an external matching library directory.
Do not confuse the two variables:

| Variable | Used by | Purpose |
|---|---|---|
| `AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR` | Wheel build | Select files to package |
| `AZURE_COSMOS_QUERYPLANINTEROP_DIR` | Running SDK | Select where to load the library |

When the provider is used, the driver loads the library, finds the required
functions, and submits query and partition-key information, including through
`GetPartitionKeyRangesFromQuery4`. The returned JSON describes a plan.
The SDK uses that plan to coordinate query requests and combine responses.
The **partition replicas**, service-backend components holding copies of the
partition data, execute the data operations. The QueryPlanInterop library
does not read the database's items or return their query results.

The driver does not download or compile QueryPlanInterop automatically.

### Prove which planner ran

A successful query is not enough evidence for the QueryPlanInterop feature.
The Rust planner or gateway may have supplied the plan instead.

The driver's diagnostic labels distinguish them:

| Label | Provider |
|---|---|
| `native_ffi` | QueryPlanInterop |
| `local_rust` | Pure-Rust planner |
| `gateway` | Plan returned by the gateway |

Installed-wheel tests need an observable signal for the actual provider,
not merely an import check or a file-presence check. The label alone is not
proof of success: `native_ffi` also appears in logs reporting an unavailable
library or failed planning attempt. Check the message and outcome, such as
`using native FFI query plan`, rather than treating a fallback message as
successful QueryPlanInterop use.

For missing-library tests, start a fresh process with the runtime setting
pointing to an empty directory before importing the SDK, and ensure no other
copy is discoverable. This does not turn off the pure-Rust planner.
Use `GatewayOnly` for a test that explicitly requests its plan from the gateway.

### Deferred work and completion criteria

| Work | Owner |
|---|---|
| Identify the producing team, approved binary source, and matching driver/library versions | Cosmos SDK team, Rust driver team, and producing team |
| Confirm permission to redistribute the libraries, licensing, signing, and required companions | Producing team and release approver |
| Supply each target's files before its wheel build, including inside Linux containers | Central team, using SDK-owned staging configuration |
| Inspect final wheels and demonstrate QueryPlanInterop planning on supported targets | SDK team supplies tests; Central runs them |

This work is complete only when the intended files reach the final wheel and
the installed SDK proves this particular provider works.

## 12. How the pipeline builds and releases the complete wheel set

The local workflow answers:

> "Can this machine build and install one wheel?"

The pipeline must answer a larger question:

> "Can we build the whole required set from the intended source, test it, and
> publish only the approved results?"

### The SDK entry point calls shared Central instructions

The Cosmos entry file uses the shared templates introduced in section 3.
It selects the common build instructions and passes the Cosmos-specific
settings through them.

The current chain is:

```text
sdk\cosmos\ci.yml
    -> eng\pipelines\templates\stages\cosmos-sdk-client.yml
    -> eng\pipelines\templates\stages\archetype-sdk-client.yml
    -> shared build jobs and conditional release processing
```

**Having shared instructions for installing Rust is different from asking
the Cosmos pipeline to use them.** The general template supports Microsoft
Rust installation, but leaves it disabled unless a caller requests it.

The SDK-owned `sdk\cosmos\ci.yml` must send that request through the
Central-owned `cosmos-sdk-client.yml`. The Cosmos template must accept the
inputs and forward them to `archetype-sdk-client.yml`; it does not need another
implementation of the installer.

**Checkout reviewed on October 22, 2026:** the SDK entry requests Rust
installation, and `cosmos-sdk-client.yml` declares and forwards the installer
inputs to `archetype-sdk-client.yml`. That existing toolchain support remains
after the rollback.

The test-job integration is different. The restored Cosmos template does not
declare `RunRustTests`. Supplying that input caused Cosmos CI build 6990313
to fail during YAML validation, before any jobs could run. The SDK entry now
omits the unsupported input. **Removing it addresses that validation failure;
it does not connect the additional Rust test jobs or prove that tests pass.**
The test template and runner remain SDK-owned files. The SDK team must restore
the opt-in only after Central integrates support for those jobs.

These template inputs are named settings passed from one file to the next.
A **feed** is a service from which tools download packages or other build
inputs. Here, one input tells the installer which feed supplies the compiler.

| Input | What it tells the build |
|---|---|
| `InstallMsRustToolchain` | Enable Microsoft Rust installation |
| `MsRustWorkingDirectory` | Find `rust-toolchain.toml` in this package directory and use its selected compiler version |
| `MsRustToolchainFeed` | Download the toolchain from this package source, explained below |
| `MsRustAdditionalTargets` | Also install support for compiling Windows ARM64 on the Windows x64 build machine |

The first three are required to enable the current installer successfully.
The fourth is needed for our requested Windows ARM64 wheel; it is not a
universal requirement for every Rust package.

The pipeline names the outputs it will save as **artifacts**. Our
`azure-cosmos` artifact entry already sets `signBinaries: true`. That
separate flag opts into the supported **digital-signing** path: attaching
verifiable publisher and integrity information to compiled files.
The shared build also uses the flag to select extension builds.
**It does not request Microsoft Rust installation.**

### How matrix files describe the test environments

The test matrix introduced in section 10 needs a concrete representation.
The SDK-owned `sdk\cosmos\cosmos-emulator-public-matrix.json` and
`sdk\cosmos\cosmos-emulator-internal-matrix.json` describe combinations of
build-machine settings, Python versions, emulator settings, and checks.

The shared Cosmos template selects the public matrix for pull-request runs
and the internal matrix for other runs. Its job-generation instructions
turn the selected combinations into test jobs. For example, the public
matrix has separate standard-test configurations for Python 3.10 and 3.13.
Each needs its own execution result even if both install the same wheel.

A matrix file describes requested work; it does not run tests itself.
Nor is the matrix the list of wheel targets: one wheel can serve several
Python-version test configurations.

### Test the Rust integration, not just the ability to compile it

Contoso Bank needs the installed SDK to behave correctly when its customer app
creates, reads, or updates an order. A successful wheel build establishes that
the package could be assembled. It does not establish that the Rust tests ran
or that the Python and Rust paths produce compatible outcomes.

The tests answer different questions:

| Test kind | What it checks |
|---|---|
| **Offline unit test** | A focused behavior using controlled inputs, without connecting to a database service |
| **Native test** | Rust code executed by Cargo's test runner, rather than only through Python calls |
| **Service-parity test** | The same operation and inputs through the legacy Python and Rust-backed paths, comparing the observed results |

Service-parity tests need somewhere to create containers and items. The
**Windows Cosmos DB Emulator** runs a local service for those requests,
following the existing Python test approach. It is not the Rust in-memory
test substitute identified as unfinished migration work in section 5.

The service tests cover both Python calling styles. A **synchronous** call
waits before returning its result. An **asynchronous** call lets the customer
app await the result while other scheduled work can proceed.

**pytest** is the Python test runner. It first **collects** tests, finding
the test cases selected by the command, and then executes them. Finding a
test is not evidence that its checks ran.

The inherited Cosmos test job selects the `cosmosEmulator` **marker**, a label
on a Python test. Some service-parity modules have conditional skip checks but
do not carry that label. A skip check decides whether a selected test can run;
it does not add the label needed to select that test.

The SDK-owned `sdk\cosmos\templates\rust-tests.yml` therefore defines two
additional jobs intended to become required checks in the Build stage.
A **required check**, sometimes called a gate, must succeed before that
part of the pipeline can succeed. Neither job uses `continueOnError` or the
inherited emulator-marker filter.

**The following describes the SDK's job definitions, not jobs currently
connected to the shared pipeline.** Central must accept the opt-in and
include these jobs before they can enforce this requirement.

| Job | What it executes |
|---|---|
| `Cosmos_Rust_Offline` | `cargo test --workspace --locked -- --test-threads=1`, followed by every `test_*_unit.py` module under the package's tests |
| `Cosmos_Rust_ServiceParity` | Both synchronous and asynchronous service-parity tests, plus the copied tests under operation-specific `legacy` folders, against the job's Windows emulator |

Both jobs install the Windows x64 wheel from `Build_Windows` and require its
native extension to import before Python test collection. They therefore
depend on `Build_Windows`; after it succeeds, they can run independently
when build capacity is available. They use Python
3.13. This is an additional required coverage baseline, not a replacement for
the existing Python-version matrix or proof of every supported platform.
The native job uses the package's selected Microsoft Rust toolchain.
`core-python` names the legacy Python implementation in these migration
tests. Offline Python tests retain that default; native-specific tests
select Rust explicitly. The service job selects Rust for calls that do not
already specify which implementation to use.
Cargo's test build includes code marked `#[cfg(test)]`, meaning it belongs
to test builds rather than ordinary wheel builds. Deliberately ignored Rust
benchmarks, which measure performance, remain outside the normal test run.

The service job selects `test_*parity*.py` modules and copied `legacy` tests
directly, excluding offline unit modules and the `auth` and `common` helper
directories. Token-authentication parity needs its own account/credential
configuration; the job using the emulator's key does not claim to cover it.
Tests involving several service regions or a network proxy that introduces
failures also retain their separate environment requirements.

The runner checks the test names declared in source against the cases pytest
actually collects. It rejects missing tests, selected tests removed from the
run, unexpected skips, and unfinished tests. It also rejects `xfail` results:
tests marked as expected to fail cannot count as required passing evidence.
Each required test file must have passing test bodies. Existing unconditional
skip markers with reasons are reported, not counted as passes. For offline
parameter combinations that do not apply to a particular SDK implementation
or client type, the runner records exact
file-scoped skip reasons. Missing dependencies, a missing native extension,
or an unavailable emulator are not permitted skip reasons.

Each job publishes the pytest results and a `coverage.json` report. Here,
**coverage** means accounting for which required tests were selected and
completed; it is not a measurement of which source-code lines executed.
The native job also retains its Cargo transcript and rejects an empty or filtered native
run. `--collect-only` is available for local selection checks and is explicitly
identified in the report; the pipeline does not use it as an execution gate.

| File | Owner and responsibility |
|---|---|
| `sdk\cosmos\ci.yml` | SDK team restores `RunRustTests: true` only after Central integrates support; the unsupported input is currently omitted |
| `sdk\cosmos\templates\rust-tests.yml` | SDK team defines dependencies, emulator setup, commands, and result publication |
| `sdk\cosmos\azure-cosmos\scripts\run_rust_ci.py` | SDK team owns suite discovery and collection/execution assertions |
| `eng\pipelines\templates\stages\cosmos-sdk-client.yml` | Pending Central change: accept the Cosmos opt-in and select the SDK job template |
| `eng\pipelines\templates\stages\archetype-sdk-client.yml` | Pending Central change: accept additional jobs in the existing Build stage without changing other callers |

Central must implement and integrate these shared-template changes. The
opt-in must default to disabled so other callers keep their existing behavior.
When enabled, it must include both SDK-owned jobs in the Build stage alongside
the existing emulator matrix. Accepting the parameter without adding the jobs
does not deliver the required test coverage.

Local
validation of the SDK runner and YAML does not replace an Azure Pipelines run
using the authenticated toolchain feed and the built wheel. Newly selected
test failures must be investigated rather than excluded to make the gate
green.

### Which shared files do the work?

These files implement the shared stages, jobs, and steps introduced in
section 3. Paths are relative to the Python repository root:

| Central-owned file | Its part of the process |
|---|---|
| `eng\pipelines\templates\stages\cosmos-sdk-client.yml` | Applies Cosmos-specific settings |
| `eng\pipelines\templates\stages\archetype-sdk-client.yml` | Connects the shared stages and passes build settings onward |
| `eng\pipelines\templates\jobs\ci.yml` | Defines platform build jobs and their limits |
| `eng\pipelines\templates\steps\resolve-build-platforms.yml` | Resolves platform setup, including Windows Python locations |
| `eng\pipelines\templates\steps\build-package-artifacts.yml` | Prepares tools and dependency access, then generates packages |
| `eng\pipelines\templates\steps\install-msrust-toolchain.yml` | Installs the Microsoft Rust toolchain |
| `eng\tools\azure-sdk-tools\ci_tools\parsing\parse_functions.py` | Reads package information and recognizes the `cibuildwheel` configuration |
| `eng\tools\azure-sdk-tools\ci_tools\build.py` | Selects and invokes the package-build route |
| `eng\tools\azure-sdk-tools\azpysdk\sphinx.py` | Prepares documentation sources and installs the package used to generate API documentation |

The parser's `ParsedSetup` object is the shared code's representation of the
package configuration. It selects the Python package information from a
populated `[project]` section and recognizes `[tool.cibuildwheel]`.

That extra recognition matters because a Maturin extension is not declared
as a setuptools `ext_modules` extension. The shared build must not overlook
the need for platform-wheel coordination just because that setuptools setting
is absent.

`sdk_build`, the shared build command, then invokes `cibuildwheel`.
This does not replace the helper or Maturin; it arranges their repeated
execution in the selected environments.

### What Sphinx does and why the pipeline runs it

A developer using the SDK needs to know how to call its methods. For example,
before the customer app calls `database.replace_container`, the developer
needs to know which values to pass and what the call returns.

The SDK team maintains that information alongside the Python code:

- A **method signature** describes how a method can be called. It names the
  inputs, called **parameters**, and declares the types they accept.
- A **docstring** is explanatory text inside a Python class or function.
  It describes behavior, parameters, return values, and examples.

**Sphinx** is the tool that turns these descriptions and supporting documents,
such as the README, into documentation pages that a developer can read in a
web browser.

In this pipeline, Sphinx imports the SDK into the documentation process
so it can inspect the classes and methods.
It uses their signatures and docstrings to generate the reference pages.
It also turns references to other documented classes into links.

This gives the pipeline another check before release: can the documentation
be generated without errors or warnings? For example, a class reference that
could point to two different classes needs to be corrected, not silently
linked to whichever one happens to be found first.

Generating these pages does not build the customer package or prove that
requests succeed against the service backend. The wheel supplies the code
that the customer app runs; the documentation explains how to use that code.

### Why documentation generation installs the built wheel

Because Sphinx imports the SDK, the documentation environment needs an
installed, usable package. The earlier package build has already compiled
the Rust extension. The documentation step should use that result rather
than compile the extension again.

The documentation check therefore needs two different inputs:

| Input | What the documentation check uses it for |
|---|---|
| Source distribution (`sdist`) | An archive supplying the README and source files used to prepare documentation pages |
| Compatible wheel | The installed SDK, including its compiled extension, that Sphinx imports |

**Pending Central work:** the restored shared check in
`eng\tools\azure-sdk-tools\azpysdk\sphinx.py` still installs the sdist.
That asks the build backend to create a new wheel. For our package it invokes
Maturin and Cargo, which require the selected Microsoft Rust toolchain.
Installing Maturin alone does not supply that toolchain.

Central needs to use the existing `ext_modules` or `cibuildwheel` package
information to recognize compiled packages. For those packages, the check
must stage the sdist without installing it, then install a compatible built
wheel. In CI, `PREBUILT_WHEEL_DIR` identifies the existing artifacts.
A missing compatible wheel must fail the check, not silently trigger a new
source build.

Ordinary Python packages should retain their existing sdist-installation
path. Building a compiled package locally without prebuilt artifacts still
requires its build tools. Using a wheel for documentation does not establish
that customer installation from source is supported.

### How documentation resolves types on traced methods

Once Sphinx can import the SDK, it must describe each supported way to call
a method correctly. Returning to `replace_container`, the customer app can
request different results:

| Setting | What the method returns |
|---|---|
| `return_properties=False`, the default | A `ContainerProxy` object representing the container |
| `return_properties=True` | Both the `ContainerProxy` object and the container properties, returned together |

A **tuple** groups values into one result. The SDK declares separate call
signatures for these two cases, called **overloads**, so tools can describe
which result corresponds to each setting.

For the generated documentation to link `ContainerProxy` to the right class,
Sphinx needs more than its short name. The SDK has separate synchronous and
asynchronous classes with that name. A **qualified name** includes the path
to the class, such as `azure.cosmos.ContainerProxy` or
`azure.cosmos.aio.ContainerProxy`, to distinguish them.

There is one more step between Sphinx and the original method. **Tracing**
records information about SDK operations. The SDK adds a **wrapper function**
around a method so it can record that information while calling the original
method.

Sphinx 8.2 looks up the overload's type names using the wrapper's module
rather than the module defining the original method.
The wrapper's module does not contain the
`ContainerProxy` and `PartitionKey` names imported by the original method's
module. The resulting short-name references can match several documented
classes. That is why the documentation check can fail even when the
docstring already contains qualified names.

The correction belongs to the documentation tools, not the customer app.
**Pending Central work:** the proposed `_autodoc.py` helper and its
registration in `doc\sphinx\conf.py` have been removed from this branch.
Central needs a correction that resolves overloaded signatures using the
original method's types, rather than the tracing wrapper's imports.

The SDK must keep its tracing wrapper and runtime behavior, and documentation
warnings must remain errors. Central's regression tests should generate
pages containing competing class names and check that both overloads link
to the intended class. Those tests must be tracked and included in a test
run, not left under an ignored generated-documentation directory.

### Why package inspection must handle several wheels

Another shared step records the package's Python **namespace**, the import
name such as `azure.cosmos`. It obtains that information by inspecting
Python files inside a wheel.

The pure-Python package supplied one wheel, but this release supplies several
platform wheels. The current `eng\scripts\Save-Package-Namespaces-Property.ps1`
can pass several matching files to a helper that accepts one archive path.
That causes the namespace step to fail before it records the package data.

**Pending Central work:** select one wheel for the exact package version and
pass its full path to the existing inspection helper. This step reads archive
contents; it does not load the Rust extension, so it does not need a wheel
that can execute on the inspection machine. A missing matching wheel must
remain an explicit error.

### How three build-machine types serve five targets

Five wheel targets do not necessarily need five kinds of build machine.
**Cross-compilation** means producing code for a different processor from
the one running the compiler. Windows ARM64 uses this arrangement on an
x64 build machine.

**Emulation** lets a machine run software intended for another processor.
QEMU is the emulation software used by the Linux ARM64 path.

The configured machine roles are:

| Build machine | Wheel work |
|---|---|
| Windows x64 | Build Windows x64; cross-compile Windows ARM64 |
| Linux x64 | Build Linux x64; use QEMU emulation for Linux ARM64 |
| macOS ARM64 | Build macOS ARM64 directly |

The configuration supplies `CARGO_BUILD_TARGET` for the ARM64 Rust target and
`PYO3_CROSS_LIB_DIR` for the pipeline's ARM64 Python-library location.
These are environment variables, not new commands to run. PyO3's
`generate-import-lib` feature helps create the Python-linking files needed
by this Windows build arrangement.

Neither setup excuses missing tests. Producing an ARM64 file on x64 does not
prove the ARM64 file executes correctly. Central must establish execution-test
coverage for each supported target.

Linux wheel builds run inside the prepared containers introduced in section
11. The compiler setup, required credentials, and input files must be available
where the build actually runs, not just on the host.

### Where does the build download its Rust tools and dependencies?

The build machine needs more than our Python and Rust source. It needs the
compiler that turns Rust into machine code, and the dependency source packages
that Cargo builds with our binding.

Our shared setup uses two different feeds because installing a compiler
and downloading a library's source are different operations. The dependency
feed acts as a **mirror**, serving packages from another registry through
a different address:

| Feed | What the build obtains | How the shared setup selects it |
|---|---|---|
| Microsoft Rust toolchain feed | The Microsoft Rust build tools selected by `rust-toolchain.toml` | Explicit `MsRustToolchainFeed` input, passed to the installer's `ToolchainFeed` parameter |
| Cargo dependency feed | Rust dependency packages, through the configured crates.io mirror | The installer's `CratesIoFeed` parameter, whose current default selects `azure-sdk-for-rust-public` |

For our package, `rust-toolchain.toml` selects `ms-prod-1.97`. That answers
**which toolchain version to use**. The toolchain feed answers **where to
download it**. Neither setting replaces the other.

The Cargo feed does not select the compiler version. It also does not replace
the driver Git revision configured in `Cargo.toml`; that driver source still
requires access to its Git repository.

### Can we reuse the test toolchain feed?

The checked-out SDK entry selects this feed for prototype testing:

```text
https://pkgs.dev.azure.com/azure-sdk/_packaging/azure-sdk-for-rust-org-test/nuget/v3/index.json
```

The address ends in `nuget/v3/index.json` because the toolchain is distributed
using **NuGet**, another package-distribution system. We are downloading
build tools here, not changing how customers install the Python SDK.

The shared installer requires the caller to supply the toolchain feed
explicitly. The SDK entry chooses the address; Central's template receives
and uses it.

The SDK entry now supplies the following inputs alongside `ServiceDirectory`
under `extends.parameters` in `sdk\cosmos\ci.yml`, retaining the existing
`Artifacts` list:

```yaml
InstallMsRustToolchain: true
MsRustWorkingDirectory: $(Build.SourcesDirectory)/sdk/cosmos/azure-cosmos
MsRustToolchainFeed: https://pkgs.dev.azure.com/azure-sdk/_packaging/azure-sdk-for-rust-org-test/nuget/v3/index.json
MsRustAdditionalTargets: aarch64-pc-windows-msvc
```

The final value identifies the Windows ARM64 compilation target, not the
processor running the build job. These configured inputs do not establish
that a run has succeeded. The test feed is not yet an approved
production-release feed decision.

### Knowing the feed address does not grant access

The address tells the installer where to ask for the toolchain. The pipeline's
**build identity**, the account used by the automation, must also be allowed
to download it. A developer's ability to open the feed in a browser does not
establish that the pipeline can use it.

Authentication for internal feeds belongs in pipeline infrastructure.
The feed address is configuration; access tokens are credentials and must not
be committed into the SDK's package files.

The next run must confirm that its identity can obtain `ms-prod-1.97` and the
required targets from this feed. Feed contents and current build access have
not been verified by this documentation update. Successful toolchain
installation also does not prove that Cargo dependency downloads will succeed;
those use their own feed configuration and authentication.

These are build-time downloads. A customer installing a compatible wheel does
not need these internal feeds or Microsoft Rust tools.

**Source:** `eng\pipelines\templates\stages\archetype-sdk-client.yml`,
`eng\pipelines\templates\steps\build-package-artifacts.yml`,
`eng\pipelines\templates\steps\install-msrust-toolchain.yml`, and the package's
`rust-toolchain.toml`. The forwarding and feed selection described here were
checked in `cosmos-sdk-client.yml` and `sdk\cosmos\ci.yml`; feed access and
successful execution still need their own evidence.

### Build time limits are separate from feed access

The Rust-enabled jobs currently allow 240 minutes for a whole job and
210 minutes for the package-generation step inside it.

The two limits answer different questions:

```text
Job limit
    -> how long may this complete unit of work run?

Package-generation step limit
    -> how long may this particular operation run?
```

Increasing one does not remove the other. The limits must allow time for setup,
compilation, and the remaining job work.

### A saved pipeline output is not a published release

When a matching trigger or manual request starts a run:

```text
Pipeline checks out the selected source
    -> platform jobs prepare their build environments
    -> cibuildwheel coordinates the requested wheels
    -> the configured checks run where execution is supported
    -> completed outputs are saved for inspection and later processing
```

Saving artifacts lets the team inspect what the automated build produced
and pass those files to later jobs. It does not automatically make them
customer-visible releases.

The current package `test-command` checks that `CosmosClient` and `_rust`
import and that `_rust.create_database` is present. It does not call that
operation, validate the complete SDK, or demonstrate query planning.

The source paths covered by `sdk\cosmos\ci.yml` include the Rust source and
configuration. Branch conditions still matter: the presence of a matching
file path does not mean every branch push automatically runs the pipeline.

### The release route processes and publishes approved outputs

Before publication, Central must confirm that the tooling handles every
approved platform wheel, plus any selected source archive, under one
`azure-cosmos` version.

The release plan also calls for approved signing of Windows and macOS native
files. The `signBinaries` setting requests signing work; the release still
needs the approved policy and evidence that the final files were processed.

If signing changes files inside a wheel, the release process must:

```text
unpack the wheel
    -> sign the files required by the approved policy
    -> repack it with correct packaged-file records
    -> install and test that final wheel
```

Signing can change file contents, so the hashes and sizes recorded in the
wheel's `RECORD` file must describe the signed files, not the earlier copies.
Testing an earlier unsigned wheel does not prove the repacked wheel works.
Signing infrastructure and credentials remain Central-owned.

Only after the required outputs, final-wheel tests, and approvals are complete
should publication proceed. These are requirements for the finished release
route, not a claim that the prototype has completed them.

## 13. What Contoso Bank installs

The purpose of all that SDK-team work is to avoid making every customer repeat
the compilation process.

For a published Rust-backed release, a Contoso Bank developer normally uses:

```powershell
python -m pip install azure-cosmos
```

For the selected version, pip normally prefers a compatible wheel when one is
available from the configured package source.

### The customer's platform determines the wheel

Suppose the developer's application runs on supported Windows x64 using
64-bit x64 CPython at a compatible version.

Pip selects the matching Windows x64 wheel. It does not select the Linux
wheel, and it does not compile the Windows ARM64 wheel into x64 code.

The match is against the Python environment running pip, not just the
machine's physical processor. For example, 32-bit Python on a 64-bit Windows
machine cannot use our `win_amd64` wheel.

If Contoso Bank later deploys the customer app to supported Linux ARM64, that
environment needs the Linux ARM64 wheel for the same SDK version.
These are different files belonging to one release.

### Installing a wheel does not compile our Rust source

The SDK team has already done the compilation:

```text
SDK team
    -> builds the extension
    -> places it in the platform wheel
    -> publishes the approved wheel

Contoso Bank
    -> downloads and installs that wheel
    -> runs the installed SDK
```

For this installation path, the customer does not need Cargo, `rustc`,
Maturin, `rustup`, `msrustup`, `cibuildwheel`, or a separate Rust driver
installation.

The intended completed wheel also supplies its matching QueryPlanInterop
library. Customers should not need an extra manual download to use a feature
their wheel promises to include.

The customer still needs compatible Python and platform versions, an installer
that understands the tags, and any required operating-system runtime libraries
not packaged in the wheel. Pip normally installs declared Python dependencies.

### What happens if there is no compatible wheel?

The Rust-backed release policy requires wheels-only publication. Once that
policy is enforced, if none of that version's wheels is compatible, the
customer cannot install that version using our published packages.

The SDK records this policy, but enforcement in the restored shared
publishers is still pending with Central. The current publishing path must
not be used for this Rust-backed release before that work is integrated.

Could we publish the source files so the customer can build a compatible wheel?
That would offer a different installation path, with additional requirements.
The next section explains why we do not yet support it.

## 14. What changes if we also publish a source distribution

If no compatible wheel is available, a source archive could let Contoso Bank
build one on its own machine. That moves compilation from the SDK team to
the customer. For this package, the sdist filename has the shape:

```text
azure_cosmos-<version>.tar.gz
```

Unlike a platform wheel, it does not provide the already-built Rust extension
for the customer's machine.

### Sdist tracking note: customer source installation

**Current policy: publish prebuilt wheels only. Customer source installation
remains unvalidated. Enforcement in the shared publishers is pending.**

For the existing pure-Python package, source installation primarily packages
Python files. For the Rust-backed package, it must also compile the extension.
That changes the tools and access the customer's machine needs.

If source publication is enabled in the future, pip could select the sdist:

```text
pip downloads the source archive
    -> prepares a Python build environment
    -> installs the declared Python build dependencies
    -> calls our helper and Maturin
    -> Cargo and rustc build the extension for Contoso Bank's machine
    -> a local wheel is created
    -> pip installs that wheel
```

Pip can arrange these steps; the customer does not necessarily invoke each
one manually. Downloading or unpacking the source archive alone is not
installation.

### Which tools would the customer need?

**The customer needs a working native-build environment, not the entire
multi-platform Azure SDK pipeline.**

| Tool or input | Requirement for an ordinary pip source installation |
|---|---|
| Python and pip | Start the installation |
| Maturin | Needed during the build; pip normally installs the declared version into build isolation |
| Cargo and `rustc` | A compatible Rust toolchain must be available |
| Platform compiler/linker and required libraries | Needed as appropriate for the target and native dependencies |
| Rust dependency sources | Must be accessible; the prototype's Git-pinned driver also requires access to its Git source |
| QueryPlanInterop files | Needed if this source-build path promises that particular provider |
| `cibuildwheel` | Not needed to build just the customer's local wheel |
| Python `build` package | Not required merely to run `pip install`; pip can call the backend |

If build isolation is disabled, the caller must arrange the Python build
dependencies as well. Installing Maturin is not the same as installing the
complete Rust and operating-system toolchain.

### The internal compiler choice is a release decision, not a customer prerequisite

Our current `rust-toolchain.toml` selects `ms-prod-1.97`.
External customers cannot be assumed to have access to that internal channel,
`msrustup`, or internal feeds.

Before supporting source installation, the SDK and Central teams must define
and test a customer-accessible toolchain selection and dependency setup.
That could require a documented public-toolchain selection or override;
the current prototype does not establish a supported customer procedure.

This concern does not apply to installing an already-built compatible wheel.
The compiler used to create that wheel is not a program the customer must
install just to use it.

Tool access is only part of the requirement: the source archive must also
supply the package's own build inputs.

### The archive must stand on its own

A source archive is incomplete if it builds only because the developer's
machine supplies missing source files or a neighboring Rust checkout.

It must include all package-owned inputs required to start a clean build:

| Input | Why it is needed |
|---|---|
| `azure\__init__.py`, `azure\cosmos\**` | Python package structure, implementation, typing files, and data |
| `azure_cosmos_rust\Cargo.toml`, `src\**` | Binding configuration and Rust source |
| `azure_cosmos_rust\build.rs`, `query_plan_binary.rs` | Build-time native-library checks |
| Root `Cargo.toml`, `Cargo.lock` | Workspace and dependency selections |
| `rust-toolchain.toml`, required `scripts\*.sh` | Selected toolchain and configured setup inputs |
| `pyproject.toml`, `azure_cosmos_build_backend.py` | Package information and build entry point |
| `azure_cosmos_build_metadata.py`, `api.metadata.yml`, `CHANGELOG.md` | Version-check helper and its additional inputs; `_version.py` is included with the Python source |
| README, license, and other files referenced by packaging | Required package descriptions and supporting information |

The driver source need not be copied into the archive if Cargo can obtain the
approved source through the declared dependency. No active dependency may
require an unrelated local directory outside the archive.

Likewise, one target's QueryPlanInterop binary must not be included as if it
worked on every target. If the source-installation promise includes that
provider, define how the customer obtains matching files.

### Use and validate the actual source-archive creation path

The configured custom backend delegates internal sdist creation to Maturin.
`pyproject.toml` explicitly includes the backend, toolchain file, and setup
scripts in that archive.

The shared `create_package` function in
`eng\tools\azure-sdk-tools\ci_tools\build.py` can already request this archive
when `enable_sdist` is true. **Generating an sdist as a build output does not
decide whether we publish it or promise customers that source installation
works.**

Internal documentation builds use the archive's README and source files, so
we retain archive generation. Publication must be blocked separately.

The `azure-cosmos` artifact in `sdk\cosmos\ci.yml` requests that separation
with `skipPublishSdist: true`. **The restored publishing templates do not
read this setting.** They still select `.tar.gz` files for publication, so
the SDK flag alone does not protect customers.

Central must update `eng\pipelines\templates\stages\release-artifact.yml`
to exclude source archives from PyPI staging and source uploads to other
release and development feeds. It must also reject source archives already
present in a wheels-only staging directory. The separate
`eng\pipelines\templates\steps\publish-alpha-package.yml` must honor the same
setting for daily alpha packages. Packages that do not opt in should retain
their existing behavior.

Do not publish this Rust-backed package through those paths until the
restriction is implemented and demonstrated.

For customers, `pip --no-binary` requests installation from source rather than
a prebuilt wheel. Under the required wheels-only policy, that option will not
provide an installation path for this release.

The legacy setuptools path uses different file-selection rules, including
`MANIFEST.in`, a file containing source-inclusion instructions.
Changing that file does not automatically change a Maturin archive, and
changing Maturin settings does not prove the legacy archive is complete.

The release tooling must use and validate the selected path. Preserving the
production packaging path does not mean we can assume its source archive is
sufficient for the Rust build.

### How to prove source installation works

Creating a `.tar.gz` file successfully proves only that an archive was created.
The meaningful check is:

```text
Create the actual source archive
    -> move it outside both repository checkouts
    -> use a clean environment with documented customer-accessible tools
    -> build and install from the archive
    -> inspect the resulting wheel and its metadata
    -> import the installed extension
    -> run the required SDK operations
```

The test must not borrow missing files from a checkout. If QueryPlanInterop is
promised, it must also supply and exercise that provider.

Before removing `skipPublishSdist`, the release approver must approve source
installation, the SDK team must document supported source-build targets and
prerequisites in the README, and Central must run the clean-archive validation
above. Until then, every supported target needs a compatible prebuilt wheel.

## 15. What still needs to be decided or proved before release

The preceding sections explain how the build is configured and what a complete
release should do. They do not establish that every target, test, or approval
is complete.

A **release approver** is the authorized person or group deciding whether the
version, support policy, and final outputs are ready to publish. That owner
must be identified.

### Central changes still required

The SDK owns the requested behavior and its package-side configuration.
Central owns the shared code that must act on those requests. After the
October 22, 2026 rollback, the following work is pending rather than part of
this branch's shared implementation:

| Work | Central-owned files | What must be delivered |
|---|---|---|
| Synchronized version updates | `eng\tools\azure-sdk-tools\ci_tools\versioning\*`, `packaging_tools\sdk_update_version.py` under the same tool directory | Honor the SDK setting, update all version copies and stability labels, and restore files if the update fails |
| Required Rust test jobs | `eng\pipelines\templates\stages\cosmos-sdk-client.yml`, `archetype-sdk-client.yml` | Add `RunRustTests` with a disabled default and connect both SDK-owned jobs to the Build stage without replacing the existing emulator matrix |
| Documentation installation | `eng\tools\azure-sdk-tools\azpysdk\sphinx.py` | Keep sdist sources for page generation but install a compatible built wheel for compiled packages |
| Overloaded method documentation | Shared configuration under `doc\sphinx` | Resolve types from the original method without changing SDK tracing or suppressing warnings |
| Multi-wheel namespace inspection | `eng\scripts\Save-Package-Namespaces-Property.ps1` | Inspect one exact-version wheel instead of passing several files to a single-archive helper |
| Wheels-only publication | `eng\pipelines\templates\stages\release-artifact.yml`, `eng\pipelines\templates\steps\publish-alpha-package.yml` | Honor `skipPublishSdist` across all publication routes while preserving other packages' behavior |

Each change needs Central-owned, tracked regression coverage and integration
into the source used by the pipeline. A saved patch or an SDK opt-in is not
evidence that the shared implementation exists. The unsupported `RunRustTests`
input has been removed from the SDK entry, but the additional Rust jobs remain
disconnected until Central integrates them. The current publishers still do
not enforce the source-archive restriction.

### Treat the Rust-backed release as a v5 upgrade

Contoso Bank needs to distinguish an update that preserves the existing API from
an upgrade that intentionally removes supported behavior. **This Rust-backed
release targets SDK major version 5, not another compatible 4.x release.**
The exact v5 version, preview or stable status, and release date still require
approval.

For example, a customer app using Cosmos resource tokens, one of the previous
ways to supply access credentials, cannot move unchanged to this release.
The release notes and migration guidance must explain that removal.
They must explain the supported authentication choices and the access-model
changes needed for migration, not present an account key or Microsoft Entra
credential as a drop-in replacement. Other intentional removals need the same
customer-facing treatment; their detailed contracts remain in the API review
rather than being duplicated here.

Before publication, the Cosmos SDK team and release approver must establish:

| Requirement | Evidence needed |
|---|---|
| Approved v5 identity | The exact version and preview or stable status are approved; the breaking release is not labelled as 4.x. |
| Synchronized source metadata | `_version.py`, `[project].version`, `api.metadata.yml`, and the newest changelog release heading carry that approved version; stability classifiers match the release status. |
| Customer migration guidance | Release notes identify the intentional breaking changes and link to reviewed migration guidance. A major-version label alone does not explain how to migrate. |
| Final artifact identity | Every final wheel and any approved source archive carries the approved v5 version; an installed wheel reports that same SDK version. |

**These are release requirements, not an automated major-version gate.**
The existing metadata check rejects disagreement between version files, but
it would accept matching `4.17.2` values. Passing that check does not authorize
publishing this breaking release under a 4.x version.

### Keep the remaining decisions in one place

| Area | What must be decided or proved | Owner |
|---|---|---|
| Existing production builds | Preserve the historical pure-Python production branch's build path; in the Rust-backed tree, keep setuptools metadata-only and build artifacts through Maturin | Cosmos SDK team and Central team |
| Shared engineering integration | Complete the [pending Central changes](#central-changes-still-required), including pipeline-input support and publication enforcement | Central team, with SDK requirements and scenarios |
| Release identity and migration | Complete the [v5 release requirements](#treat-the-rust-backed-release-as-a-v5-upgrade), including approved metadata, final artifact identity, and customer migration guidance | Cosmos SDK team and release approver |
| Rust driver | Select the approved published driver for release, preserve required features, and review the synchronized lock | Cosmos SDK team and Rust driver team |
| Compiler policy | Approve the release toolchain and validate or correct the declared compiler minimum | Cosmos SDK team and Central team |
| Support policy | Approve Python versions, platform coverage, Linux baseline, and Windows/macOS minimums | Release approver, using SDK and Central evidence |
| Multi-target builds | Build the intended source and inspect every required wheel; establish execution-test coverage including ARM64 | Central team and Cosmos SDK team |
| QueryPlanInterop | Complete the [deferred library delivery and provider checks](#deferred-work-and-completion-criteria) | Producing team, Cosmos SDK team, and Central team |
| Source installation | Keep sdists unpublished until [customer source installation](#sdist-tracking-note-customer-source-installation) is approved and validated | Release approver, Cosmos SDK team, and Central team |
| Dependency maintenance | Confirm update automation covers both Cargo manifests and the lock | Repository maintainers and Cosmos SDK team |
| Signing and publication | Apply approved signing, test final repacked wheels, and publish the complete set under one version | Central team and release approver |

### Define what each test actually proves

The test matrix from section 10 identifies the environments whose behavior
must be demonstrated. Building one stable-ABI wheel reduces the number of
files; it does not eliminate tests across supported Python versions.

For every supported wheel, the SDK's tests and Central's execution environments
must establish:

| Check | Required evidence |
|---|---|
| Archive contents | Python source and data, exactly the intended extension, and any required QueryPlanInterop companions |
| Identity and compatibility | Correct package name, version, dependencies, Python requirement, filename tags, and native-file architecture |
| Clean installation | The SDK and extension import from the installed wheel, not the source checkout |
| SDK functionality | Required Rust-backed operations actually execute successfully |
| QueryPlanInterop behavior | The installed `native_ffi` provider loads and creates plans when promised |
| Other planning paths | Eligible queries use `local_rust` without QueryPlanInterop; gateway fallback and `GatewayOnly` behave as required |
| Final release processing | The final signed/repacked files retain correct contents, installation behavior, and SDK functionality |
| Complete output set | All approved wheels and any approved sdist belong to the approved v5 release version |

A missing required output or test result must stop publication. A successful
build job, import, or query cannot stand in for the complete evidence.

### Configuration tests catch different mistakes from runtime tests

The SDK has focused tests under:

```text
tests\common\test_build_configuration_unit.py
tests\common\test_query_plan_packaging_unit.py
```

They check matters such as metadata agreement, target selection, driver-source
consistency, source-archive inclusion settings, and QueryPlanInterop staging.

Central's corresponding shared-tool tests include:

```text
eng\tools\azure-sdk-tools\tests\test_build_interactions.py
eng\tools\azure-sdk-tools\tests\test_parse_functionality.py
```

Those checks help catch a misread package or an incorrect build route before
expensive native builds start. They do not prove that a compiled extension
works on Windows ARM64 or that an installed query-planning library executes.

The release needs both kinds of evidence: correct configuration and working
final packages in the environments we promise to support.

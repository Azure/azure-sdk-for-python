# Building and releasing the Rust-backed Azure Cosmos DB Python SDK

## Table of contents

1. [Start with the complete build-to-install flow](#1-start-with-the-complete-build-to-install-flow)
2. [Which parts become the installed SDK](#2-which-parts-become-the-installed-sdk)
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
13. [What Alpha Bank installs](#13-what-alpha-bank-installs)
14. [What changes if we also publish a source distribution](#14-what-changes-if-we-also-publish-a-source-distribution)
15. [What still needs to be decided or proved before release](#15-what-still-needs-to-be-decided-or-proved-before-release)

## 1. Start with the complete build-to-install flow

The SDK team and the customer have different jobs. We will use Alpha Bank
as the customer throughout this guide. Its **customer app** is the bank's
application code; the **SDK** is the complete Azure Cosmos DB package that
application installs and uses.

**The SDK team prepares and tests the package. Alpha Bank installs that
package and uses it in its customer app.** We want the normal customer
installation to remain straightforward even though the SDK now contains Rust.

The SDK team first **builds a wheel**: it turns source code and packaging
instructions into a `.whl` archive prepared for installation. An **archive**
groups several files into one file for storage or delivery.

The team then installs that wheel into a test **Python environment**: the
Python interpreter and the packages available to it. If the required checks
and approvals pass, the release process **publishes** the wheel, making it
available from a package service for customers to download.

Alpha Bank can then use **pip**, Python's installation tool, to select and
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

Alpha Bank
    -> installs a compatible wheel
    -> runs its application using the installed SDK
```

A **build target** is an operating-system and processor combination, such as
Windows x64. A **platform wheel** contains compiled code for such a target.
The processor labels x64 and ARM64 identify different machine-code families.
One compiled file cannot serve both simply because the Python source is the
same.

## 2. Which parts become the installed SDK

Before building the wheel, the SDK team needs to identify which parts it must
include. Follow a customer call that creates an order:

```text
customer app
    -> Python wrapper checks the supplied order and prepares the operation
    -> Python/Rust binding converts those inputs and calls the Rust driver
    -> Rust driver sends requests to the service backend
    -> binding and wrapper return the result or raise a Python exception
```

A **binding** makes code written in one language callable from another.
Here, it lets the Python wrapper call the Rust driver.

| Component | Owner | What the wheel includes |
|---|---|---|
| Python wrapper | Cosmos SDK team | Python files that accept customer arguments and return Python results or exceptions |
| Python/Rust binding | Cosmos SDK team | Compiled code that converts inputs, calls the driver, and converts its results |
| Rust driver | Rust driver team | Driver code compiled together with the binding into the Python extension |

The **service backend** is the remote Cosmos DB service. It is not included
in the wheel. The customer app is also separate: it imports and calls the SDK
after installation.

A **Rust crate** is a Rust project containing source and build information.
**Cargo** is Rust's build tool; it understands those projects and builds them.
A **dependency** is another library our code needs. The Rust driver is a
dependency of our binding, even though its source lives in a different
repository.

For the commands later in this guide, the **package source directory** means
the directory containing the package's `pyproject.toml`:

```text
azure-sdk-for-python\sdk\cosmos\azure-cosmos
```

### How the build obtains the Rust driver

The SDK team does not maintain a second copy of the driver in the Python
repository. The prototype tells Cargo to fetch a specific **Git revision**,
which identifies a particular saved state of the driver's source.
Selecting that revision is called **pinning** the dependency.

Cargo downloads the selected source and compiles it with the binding. Editing
a neighboring Rust checkout does not change the extension already installed
in Python. To use a different driver revision, the SDK team must change the
dependency selection, rebuild, and install the new extension. Section 5
explains how the build records that selection.

For the final release, our plan calls for an approved driver version published
on **crates.io**, the public registry from which Cargo downloads Rust source
packages. A stable SDK release must use an approved stable driver, not a
preview dependency.

A customer installing our wheel does not separately install a Rust driver
package. Next, we need to distinguish who prepares that wheel from who runs
the shared build and release process.

## 3. Which work belongs to the SDK team and which belongs to Central

The **Cosmos SDK team** maintains the Python wrapper, binding, package settings,
and tests. **Central** is the shared engineering team that maintains build and
release tools used by multiple SDK packages.

For example, the SDK team can request a Windows ARM64 wheel. Central must
provide a machine that can build it and an environment that can run its tests.
Declaring the target does not create those environments.

| Work | SDK team | Central team |
|---|---|---|
| Package contents | Specify the Python files, extension, data, and dependencies | Run the shared tools that build and collect the package |
| Platform coverage | Request the supported wheel targets and supply tests | Provide build machines and execute the required tests |
| Version changes | Approve the package version and identify every copy that must agree | Make shared version commands update those copies together |
| Publication | Identify the approved files and release requirements | Apply signing and publication rules through shared release tools |

A **pipeline** is an automated sequence of work, such as building a package
and testing it. Some requested shared behavior is still
[pending with Central](#central-changes-still-required). An SDK setting is a
request for that behavior, not proof that the shared tools implement it.

We will return to the full pipeline after following one local build. First,
we need to understand how the package tells its build tools what to do.

## 4. Why both setup.py and pyproject.toml exist

The build needs more than code. It also needs **package metadata**: the package
name, version, Python requirements, and dependencies that pip will read.

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
tool. Setuptools is not Cosmos-specific. "Legacy"
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
Alpha Bank calls when its customer app uses the installed SDK.

### Before Rust: pyproject.toml held other tool settings

The pre-Rust `pyproject.toml` was **already used**, but it did not direct the
Cosmos package build. TOML is the format used to write these settings; it is
not a tool that runs the build.

It selected repository checks, such as checks for likely Python mistakes,
and held settings for other packaging tools. Those settings did not tell
setuptools which files to put in the Cosmos wheel.

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
package. We call ours the **SDK package builder**:
`azure_cosmos_package_builder.py`. It prepares the inputs and calls Maturin.
Its exact configuration is explained below.

Our `pyproject.toml` retains the existing repository settings and adds these
responsibilities:

| Section | What it tells the build tools |
|---|---|
| `[project]` | "The customer-facing package is `azure-cosmos`. Here are its version, Python requirements, and dependencies." |
| `[build-system]` | "Call this component to carry out the package build." |
| `[tool.maturin]` | "Here is the Rust binding to compile, the Python source to include, and the extension's Python import name." |

The Python package information matters because the internal Rust binding has
its own name and version. Customers are installing `azure-cosmos`, not a
separately named Rust package.

### How package metadata and the running SDK keep the same version

Suppose pip reports that Alpha Bank installed version `5.0.0`, but the SDK
reports `4.17.2` when the app asks for its version. The developer cannot tell
which release is running. These numbers illustrate a mismatch; they are not
approved release versions.

The wheel and installed SDK must report the same version.
**`_version.py` is the version authority.** The other release
files carry copies or descriptions of that version:

| File | What its version means |
|---|---|
| `_version.py` | The Python SDK version |
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

**Pending Central work:** the shared versioning tools do not
implement this setting. Setting it to `true` does not currently make a
version command update all four files.

Central needs to extend the shared commands so one approved version update
also synchronizes the static package version, API metadata, and newest
changelog heading. The stability **classifier**, a metadata label identifying
a stable or beta release, must also agree in `setup.py` and `pyproject.toml`.

After that support is integrated, the intended workflow is to approve the
exact release version and release date, then run the following command from the
package directory. Replace the placeholders with the approved values, using
`YYYY-MM-DD` for the date:

```powershell
sdk_update_version --package-path . --version "<approved-version>" --release-date "<approved-release-date>"
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

Before calling Maturin, our SDK package builder checks all four versions. The
setuptools metadata commands perform the same check. A mismatch
stops the build with the disagreeing filenames and versions; it does not
silently select one copy or repair the checkout during packaging.

The check also runs when preparing source archives, installing a checkout
for development, or answering package-information requests. Source archives
include the helper and its metadata inputs so a later build from the archive
can perform the same check. Packaging tests verify that a mismatch is rejected
before either builder is called.


<a id="what-the-sdk-owned-build-helper-does"></a>

### What the SDK package builder does

Our `[build-system]` section selects:

```toml
build-backend = "azure_cosmos_package_builder"
```

`build-backend` is the standard Python packaging key; its value names our
Python module without the `.py` extension. This selects the SDK package
builder rather than calling Maturin directly.
The package builder checks the version information and, when supplied, temporarily
places additional compiled libraries among the files Maturin will package.
Section 11 follows the separate query-planning library that needs this step.

For a wheel build, the package builder's added work is:

```text
Check that the SDK version and release metadata agree

If matching additional compiled libraries were supplied:
    temporarily copy them into the Python package directory

Call Maturin to build the wheel

Remove the temporary copies from the source checkout
```

The completed wheel retains the packaged files. The cleanup affects the
temporary source-checkout copies. This temporary copying before packaging is
called **staging**.

**The package builder does not replace Maturin or compile Rust itself.** If no
additional compiled libraries are supplied, it skips that preparation
and still calls Maturin.

For one wheel, the tools now have distinct jobs:

```text
SDK package builder
    -> checks version information and prepares supplied library files

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
| `python -m build --wheel` or `--sdist` | Uses the SDK package builder, which delegates native packaging to Maturin. |
| `python -m pip install -e .` | Uses the SDK package builder to install the checkout for development, explained in section 7. |

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

The package-level file defines a **workspace**: a collection of Rust projects
managed together, with shared settings and a shared lock file. It can contain
just one project.

The workspace's member selection is:

```toml
[workspace]
members = ["azure_cosmos_rust"]
```

The `members` line says:

> "The Rust project in the `azure_cosmos_rust` directory belongs to this
> workspace."

That project is our binding. The driver is an external dependency, not a
second member of this Python repository's workspace.

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

The file inside the binding directory describes its name, the library it builds, and
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

Normal builds and tests must use the same selected driver source. When the
SDK team updates it, they must also check that the new driver still provides
every feature requested by the binding. A renamed or removed feature should
fail configuration checks rather than be silently omitted.

The binding and driver also exchange values defined by the `azure_core` Rust
library. If the binding creates a value using one copy of that library but
the driver expects the type
from a different copy, the compiler can reject the call even when the types
have the same name. Their dependency selections must therefore allow them to
use the same crate's types.

### Cargo.lock: the exact dependency selections

Knowing that we allow Tokio `1.x` is not enough to identify which version a
particular build should use. That is the job of `Cargo.lock`.

For an illustrative selection:

```text
Cargo.toml
    -> allows Tokio "1"

Cargo.lock
    -> records Tokio 1.52.3
```

The important difference is the allowed series, `1.x`, versus one exact
selected version, `1.52.3`. A normal build reuses the selection.

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

These are SDK build concerns. Alpha Bank does not need the tools when
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

We do not ask Alpha Bank to install a separate compiled driver alongside it.
Additional libraries supplied to the packaging helper remain separate files;
section 9 shows their place in the wheel.

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

The final `_rust` part must match the module name the compiled binding exposes.
Otherwise, Python asks to load one module name while the extension provides
another, and the import can fail.

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

### Install the Microsoft Rust toolchain on a developer machine

Before `maturin develop` can compile anything, the SDK developer's machine
needs the Rust build tools that `rust-toolchain.toml` selects.
[Section 5](#5-files-that-control-the-rust-build) explains that this file
selects `ms-prod-1.97`, a Microsoft toolchain that only **msrustup** can
install.

Suppose the SDK developer already has public Rust installed through `rustup`.
They run `cargo -V` in `sdk\cosmos\azure-cosmos`, and the command stops:

```text
error: custom toolchain 'ms-prod-1.97' specified in override file
'...\sdk\cosmos\azure-cosmos\rust-toolchain.toml' is not installed
```

Public Rust is present, but the selected Microsoft toolchain is not.

### Why the developer cannot use the pipeline's installer

The pipeline installs the toolchain with an Azure DevOps step named
`RustInstaller@1`, described in
[section 12](#12-how-the-pipeline-builds-and-releases-the-complete-wheel-set).
That step runs only inside a pipeline. A developer machine needs a different
route, and the header of `scripts\install-msrustup.sh` names it:

> "This script is expected to be copied into any build system that needs to
> install the internal Rust toolchain, if that system cannot use an ADO
> pipeline and the Rust installer pipeline task."

**Installation therefore has two parts: the script downloads `msrustup`, then
`msrustup` downloads the toolchain that `rust-toolchain.toml` selects.**

### What the script needs

Microsoft publishes `msrustup` and its toolchains in an internal **feed**: a
private download location in Azure DevOps. The feed only answers requests
that prove who is asking. That proof is an **access token**: a temporary
credential issued after the developer signs in.

A token also records which **tenant** issued it. A tenant is the
organization directory that a sign-in belongs to. One person can have
accounts in several tenants. **The feed accepts tokens from the Microsoft
corporate tenant only.** A token from another tenant is still a valid token,
but the feed refuses it with `403 Forbidden`.

The script also needs a few command-line tools:

| Tool | What the script uses it for |
|---|---|
| Git Bash | Runs the script, which is written for a Unix-style shell. |
| `curl` | Downloads from the feed. Windows includes it. |
| `unzip` | Extracts `msrustup` from the download. Git Bash includes it. |
| `jq` | Reads the feed's reply to find the latest `msrustup` version. Install it separately, for example with `winget install --id jqlang.jq -e`. |

**Use Git Bash, at `C:\Program Files\Git\bin\bash.exe`, not the `bash`
command that Windows itself provides.** The Windows `bash` command starts a
Linux environment. The script asks which operating system it is running on,
so from that environment it would download the Linux `msrustup`, which
cannot install a Windows toolchain. Git Bash reports Windows, so the script
downloads the Windows `msrustup`.

### Run the installation

First, obtain a corporate-tenant token and place it where the script looks
for it, the `MSRUSTUP_ACCESS_TOKEN` environment variable. With the Azure CLI,
name the corporate tenant and the Azure DevOps service explicitly:

```powershell
$env:MSRUSTUP_ACCESS_TOKEN = az account get-access-token `
    --tenant 72f988bf-86f1-41af-91ab-2d7cd011db47 `
    --resource 499b84ac-1321-427f-aa17-267ca6975798 `
    --query accessToken -o tsv
```

The `--tenant` value identifies the Microsoft corporate tenant. The
`--resource` value identifies Azure DevOps, the service that hosts the feed.
The script can also use `MSRUSTUP_PAT`, a personal access token created in
Azure DevOps, or the `azureauth` sign-in tool if either is available instead.

Then, from the same PowerShell window and the package directory, download
`msrustup` and install the selected toolchain:

```powershell
$bootstrap = "$env:USERPROFILE\.msrustup\bootstrap"
New-Item -ItemType Directory -Force $bootstrap | Out-Null
Copy-Item scripts\install-msrustup.sh $bootstrap
& "C:\Program Files\Git\bin\bash.exe" -lc `
    'cd "$(cygpath "$USERPROFILE")/.msrustup/bootstrap" && sh ./install-msrustup.sh'
& "$bootstrap\msrustup.exe" toolchain install
```

The first two commands create a working folder. The third copies the script
into it. The fourth runs the script in Git Bash, which places `msrustup.exe`
in that folder. The last command reads `rust-toolchain.toml` from the current
directory and installs `ms-prod-1.97`.

If the script reports that it requires `jq` immediately after `jq` was
installed, Git Bash has not found the new program yet. Add the folder that
contains `jq.exe` to the search path inside the Git Bash command.

### What changes on the developer machine

Windows finds a command such as `cargo` by checking the folders listed in
the **`PATH`** setting, in order, and running the first match. Public Rust
already placed its own `cargo` in `%USERPROFILE%\.cargo\bin`.

`msrustup toolchain install` makes three changes:

| Change | What it means for the developer |
|---|---|
| Installs `ms-prod-1.97` | The selected Microsoft toolchain is now on the machine. |
| Places `%USERPROFILE%\.msrustup\multiplexers\bin` first in the user `PATH` | Typing `cargo` or `rustc` now runs `msrustup`'s copy. That copy reads `rust-toolchain.toml` and starts the selected toolchain. |
| Adds a `global-credential-providers` line to `%USERPROFILE%\.cargo\config.toml` | When a Rust package source requires sign-in, Cargo can ask `msrustup` for the credential. |

**The `PATH` change applies only to terminals opened afterward.** A terminal
that was already open keeps its old `PATH`, so `cargo` still runs public
Rust's copy there. `msrustup` warns about this by saying that `cargo` and
`rustc` are "shadowed".

Open a new terminal in the package directory and confirm which `cargo` runs:

```powershell
Get-Command cargo
cargo -V
```

`Get-Command` should show `%USERPROFILE%\.msrustup\multiplexers\bin\cargo.exe`.
`cargo -V` should show version `1.97.1` with an `-ms-` label, which marks a
Microsoft build.

### The first build after switching takes longer

Compiled Rust output from the previous toolchain cannot be reused, so the
first `maturin develop --release` recompiles the binding and every Rust
dependency. On one Windows developer machine, that build took about
12 minutes. Later builds recompile only what changed.

To confirm which compiler produced a build, open `target\.rustc_info.json`.
It records the `rustc` version that Cargo used, including the Microsoft
build label.

### Prepare the environment before running the command

A **Python virtual environment** gives the project its own Python package
installation area. Using one keeps the SDK and its Python dependencies
separate from unrelated projects.

For the current configuration, the developer needs:

- A suitable Python environment for the prototype's Python 3.10 minimum.
- The selected Rust toolchain, installed as described in the previous
  subsection.
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

This command calls Maturin directly. It does not run the SDK package builder's version
checks or copy additional compiled libraries into the package.

If a developer needs the separate query-planning library, the running SDK
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
`python -m build`. It starts a package build by calling the SDK package builder selected
in `pyproject.toml`.

This initiating role is called a **build frontend**. The frontend starts the
work; our SDK package builder prepares the inputs and delegates to Maturin.

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
build-backend = "azure_cosmos_package_builder"
backend-path = ["."]
```

| Setting | Meaning |
|---|---|
| `requires` | "Install this Python build dependency for the build." |
| `build-backend` | "Call our SDK package builder." |
| `backend-path` | "Find that module in the package source directory." |

Keeping those build dependencies separate is called **build isolation**.
The temporary environment creates the wheel; it is not Alpha Bank's
application environment.

```text
Developer's environment
    -> runs python -m build

Temporary build environment
    -> contains the declared Maturin version
    -> runs the SDK package builder and packaging work

dist\
    -> receives the completed wheel
```

Build isolation manages Python build dependencies. It is not a promise to
install the Rust toolchain, operating-system build tools, or additional
compiled libraries. The developer must supply those before starting the build.

If `--no-isolation` is used, the caller becomes responsible for installing
and selecting the correct Python build tools too.

### Follow one wheel through the build

For a Windows x64 example:

```text
python -m build --wheel
    -> reads [build-system]
    -> prepares the Python build environment
    -> calls the SDK package builder
    -> the package builder checks versions and temporarily copies supplied libraries
    -> Maturin invokes Cargo for the Windows x64 extension
    -> Maturin packages the extension, Python files, and package information
    -> writes the Windows x64 wheel under dist\
```

Calling `maturin build` directly bypasses our SDK package builder. Use the configured Python
build path when checking the wheel workflow, including its version checks and
optional staging. Direct `maturin develop` remains a local-development shortcut;
it does not run these release-metadata checks.

The package builder also delegates source-archive, editable-build, and package-information
requests to Maturin. Its extra library copying is specific to the
wheel-building path.

### Inspect the archive, then install that exact file

Before returning a built wheel, the SDK package builder checks the actual archive for
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

A wheel is a ZIP archive. The intended Windows layout below includes the
Python wrapper, extension, and package information.

It also shows a planned addition: **QueryPlanInterop**, a separate compiled
library that creates a query plan, instructions the driver uses to request
and combine query results. It is not yet supplied by the prototype wheel.
Section 11 explains why it needs separate packaging and testing.

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
section 4. The installer reads it to understand the package it is installing.
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

Suppose Alpha Bank develops on Windows x64 but runs its customer app on
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

Building each target by hand would mean repeating the same preparation,
build, installation, and test commands in several environments.
**cibuildwheel** is an open-source tool that runs those wheel-building and
testing workflows for the requested platforms and Python environments.
It invokes the SDK package builder; it does not replace Maturin or Cargo.

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

For example, `archs = ["AMD64", "ARM64"]` requests both Windows processor
targets. Writing that list does not start either build. Central must supply
the build environments and invoke cibuildwheel there.

Every separate library added to a wheel must match the same target. That
requirement becomes important for QueryPlanInterop.

## 11. How QueryPlanInterop reaches the wheel and the running SDK

Alpha Bank stores orders in a Cosmos DB **container** named `orders`.
A container holds items, and the service backend distributes those items
across **physical partitions**, service-managed portions of its data.
Consider this illustrative set:

| Physical partition | Order ID | Total |
|---|---|---|
| A | `order-17` | `125.50` |
| B | `order-18` | `200.00` |
| B | `order-19` | `70.00` |

The customer app asks for orders over 100, sorted by total:

```sql
SELECT c.id, c.total FROM c WHERE c.total > 100 ORDER BY c.total
```

The expected result is `order-17`, then `order-18`. Reading only partition A
would miss a matching order; combining unsorted replies could put them in the
wrong order.

A **query plan** tells the driver how to obtain and combine the results.
For this example, the required work is:

```text
Request matching orders from both partitions, sorted by total
    -> combine the replies while preserving that order
    -> return order-17, then order-18
```

Those lines explain the work, not the literal format of a driver's plan.

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

The SDK package builder checks that the directory contains exactly one
primary library. It temporarily stages that library and the supplied native
companions under `azure\cosmos\.libs`, lets Maturin package them, and cleans up
its staged copies afterward.

An invalid supplied directory or invalid primary-library set is an error.
An absent source setting is different: the SDK package builder skips staging and
can build a wheel without QueryPlanInterop.

The current pipeline does not yet deliver these binaries or forward this
source setting into Linux build containers. A **build container** is an
isolated environment used to run build tools with its own filesystem view.
It is unrelated to the Cosmos DB container holding Alpha Bank's orders.
The future setup must make both the files and the setting available inside it.
A path visible only on the host machine is insufficient.

### Build time: reject the wrong processor's file

When library files have been staged, the binding's build checks inspect them
before accepting them for the selected target.

A compiled file has a **header**, a part of the file that identifies properties
such as its format and processor. The checks compare those properties with
the build target and reject incompatible files.

They also require the target's primary filename and check Linux's 32-bit or
64-bit file class. Supplied native companions are checked as well.

This proves more than checking the filename, but less than executing a query.
Correct file headers do not establish that every dependency is present or
that the library can create a valid plan.

### Runtime: find the library beside the installed extension

**Runtime** means when Alpha Bank's customer app is using the installed SDK,
rather than when the SDK team is building it.

The runtime setting is different:

```text
AZURE_COSMOS_QUERYPLANINTEROP_DIR
```

It means:

> "Look in this directory when the driver needs to load QueryPlanInterop."

The Python wrapper looks for `.libs` beside
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

When this provider is used, the driver loads the library and supplies the query
and the container's partition-key definition: the fields used to group related
items for storage. The library returns a
plan. The driver then sends the required data requests to the service backend
and combines its replies. QueryPlanInterop creates the plan; it does not read
`order-17` or `order-18` from the database.

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

Installed-wheel tests must inspect the driver's reported planning result,
not merely check that a library file exists or that the SDK imports. A label
alone is not
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

> "Can we build the whole required set from the intended source and
> publish only the approved results?"

This section covers build preparation, packaging, documentation generation,
and release processing. Test coverage and execution belong in the
testing guide.

### The SDK entry point calls shared Central instructions

**Azure DevOps** schedules and runs the automated pipeline. Its **continuous
integration**, or **CI**, runs check proposed code changes by building and
testing the package.

The Cosmos configuration supplies package-specific settings to Central's
**shared templates**, reusable pipeline instructions used by several SDKs.
The configuration is written in **YAML**, a text format for structured settings.

The pipeline groups work at three levels:

| Level | Meaning | Example |
|---|---|---|
| Stage | A named group of jobs | Build the package files |
| Job | Work assigned to one build environment | Build the Windows wheels |
| Step | One operation in that job | Install the compiler, or run a wheel-build command |

Steps in a job run in order. Independent jobs can run in parallel when build
machines are available. A job that installs a wheel must wait for the job
that produces it.

### What Microsoft Rust installation means

Before Maturin can ask Cargo to compile our Rust code, the build environment
needs a **Rust toolchain**: Cargo, the `rustc` compiler, and Rust's standard
library. Microsoft Rust installation means downloading and preparing the
Microsoft-distributed toolchain selected for this SDK build. It does **not**
install the Cosmos SDK into Alpha Bank's application, build a wheel, or
publish anything.

**msrustup** is Microsoft's toolchain manager: the program used to obtain
and select these internal Rust build tools. It is different from the public
`rustup` toolchain manager. Installing Maturin as a Python package does not
install this Microsoft toolchain.

### Who creates rust-toolchain.toml, and where is it used?

`rust-toolchain.toml` is an **SDK-owned configuration file** in
`sdk\cosmos\azure-cosmos`, alongside `pyproject.toml`. The SDK team creates
and maintains it with the package source. It is not generated by the
pipeline or by the tool installer.

The file records our selected build tools:

```toml
[toolchain]
channel = "ms-prod-1.97"
profile = "minimal"
```

`channel` names the Microsoft toolchain to select. `profile = "minimal"`
requests its basic compilation components, not a smaller wheel. The file
contains settings; it does not contain the compiler or install it by itself.

**The same file applies to local development and pipeline builds.**

| Environment | How the file is used |
|---|---|
| Developer's machine | Rust build commands in this checkout use the selected toolchain. The developer must first install `msrustup` and the toolchain, with authorized access to its downloads, as described in [section 7](#7-building-for-local-development). |
| Pipeline build machine | The installation step reads the file from the configured package directory and prepares that toolchain before the wheel build. |
| Linux wheel-build container | The compiler must also be installed inside the container. Our `before-all` preparation in `pyproject.toml` obtains `msrustup` with `scripts\install-msrustup.sh`, then runs `msrustup toolchain install` from the mounted source directory. |
| Alpha Bank installing a compatible wheel | No Rust compilation is needed, so the customer does not need these tools or this toolchain-selection file to install the wheel. |

For example, a developer may already have public Rust installed and still
receive "`ms-prod-1.97` is not installed." The missing prerequisite is the
selected Microsoft toolchain, not the SDK source or a Cosmos API.

### What the pipeline installer is

Here, **installer** means the Azure DevOps step named `RustInstaller@1`.
It installs the selected Microsoft Rust build tools into the build
environment. It is not pip, the tool that installs Python packages.

Central's shared
`eng\pipelines\templates\steps\install-msrust-toolchain.yml` invokes that
installation step. The template first checks that the package directory
contains `rust-toolchain.toml` and that a download source was supplied.
After installation, it configures Cargo's package source and authentication.
It reads the SDK's selection; it does not create that selection file.

### How the SDK requests that installation

Follow a request for a Windows ARM64 wheel:

```text
SDK configuration requests the wheel and its Rust build tools
    -> shared templates pass those settings to a Windows build job
    -> the job installs the requested tools
    -> cibuildwheel invokes the package build for the requested target
```

**Having shared instructions for installing Rust is different from asking
the Cosmos pipeline to use them.** The general template supports Microsoft
Rust installation, but leaves it disabled unless a caller requests it.

The shared templates already support forwarding the Rust installation request.
Every template between the SDK configuration and installer must accept and
forward the required settings. An unsupported setting can fail configuration
validation before any job starts; adding a new name to the SDK configuration
does not add the corresponding shared behavior.

These template inputs are named settings passed from one file to the next.
A **feed** is a service from which tools download packages or other build
inputs. Here, one input tells the installer which feed supplies the compiler.

| Input | What it tells the build |
|---|---|
| `InstallMsRustToolchain` | Ask the shared build to run the Microsoft Rust installation steps |
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

### How shared tools select the Rust-backed build

The shared build reads the package information in `[project]` and recognizes
the `[tool.cibuildwheel]` settings. That recognition matters: this package
does not declare its extension through setuptools, so checking only the old
setuptools extension setting would miss the Rust-backed build.

The shared build command invokes cibuildwheel, which runs the SDK package
builder for each requested target. The same package builder, Maturin, and Cargo
steps from the local wheel build still perform the work.

After the wheels are built, the pipeline also needs to produce the API
documentation that explains how to use the installed SDK.

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

These are customer-facing SDK API reference pages: the kind of documentation
Alpha Bank's developers consult on Microsoft Learn to understand classes,
methods, parameters, and return values. They are different from this
`build_and_release.md` guide, which explains how contributors build and release
the SDK.

In this pipeline, Sphinx imports the SDK into the documentation process
so it can inspect the classes and methods.
It uses their signatures and docstrings to generate the reference pages.
It also turns references to other documented classes into links.

This gives the pipeline another check before release: can the documentation
be generated without errors or warnings? For example, a class reference that
could point to two different classes needs to be corrected, not silently
linked to whichever one happens to be found first.

**Generating documentation is not the same as publishing it publicly.** The
pull-request check verifies that the pages can be generated; it does not by
itself update the public reference pages. Documentation publication is handled
separately through release processing.

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

**Pending Central work:** the shared documentation check still installs the sdist.
That asks the SDK package builder to create a new wheel. For our package it invokes
Maturin and Cargo, which require the selected Microsoft Rust toolchain.
Installing Maturin alone does not supply that toolchain.

Central needs to recognize packages that declare compiled extensions or
cibuildwheel builds. For those packages, the check
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

The documentation check can look up an overload's type names where the
tracing wrapper is defined, rather than where the original method is defined.
Those locations do not necessarily make the same classes available.
Consequently, a short name such as `ContainerProxy` can resolve to the wrong
class or remain ambiguous, even when the docstring uses a qualified name.

The correction belongs to the documentation tools, not the customer app.
**Pending Central work:** resolve overloaded signatures using the
original method's types, rather than the tracing wrapper's imports.

The SDK must keep its tracing wrapper and runtime behavior, and documentation
warnings must remain errors.

### Why package inspection must handle several wheels

Another shared step records the package's Python **namespace**, the import
name such as `azure.cosmos`. It obtains that information by inspecting
Python files inside a wheel.

The pure-Python package supplied one wheel, but this release supplies several
platform wheels. The shared namespace-inspection step can pass several
matching files to a helper that accepts one archive path.
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

### Choosing a toolchain feed

The prototype uses a test feed. A release needs an approved feed containing
the selected toolchain and additional compilation targets.

The shared installer requires the caller to supply the toolchain feed
explicitly. The SDK entry chooses the address; Central's template receives
and uses it.

The required settings have this shape. Replace the placeholders with the
package directory on the build machine and the chosen feed address:

```yaml
InstallMsRustToolchain: true
MsRustWorkingDirectory: <package-source-directory>
MsRustToolchainFeed: <toolchain-feed-address>
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

The pipeline must demonstrate that its identity can obtain the selected
toolchain and required targets from the chosen feed. Knowing the address
does not establish that the files are present or accessible. Successful toolchain
installation also does not prove that Cargo dependency downloads will succeed;
those use their own feed configuration and authentication.

These are build-time downloads. A customer installing a compatible wheel does
not need these internal feeds or Microsoft Rust tools.

### Build time limits are separate from feed access

For example, a job can allow 240 minutes overall while its package-generation
step allows only 210 minutes.

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

The pipeline's trigger rules must cover changes to the Rust source and build
configuration. Those rules also select branches: changing a covered file
does not mean every branch push starts a run. Required SDK and shared-tool
changes must be available in the branch that the pipeline actually builds.

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
    -> verify the final archive before publication
```

Signing can change file contents, so the hashes and sizes recorded in the
wheel's `RECORD` file must describe the signed files, not the earlier copies.
Signing infrastructure and credentials remain Central-owned.

Only after the required outputs, release checks, and approvals are complete
should publication proceed. These are requirements for the finished release
route, not a claim that the prototype has completed them.

<a id="13-what-customer-installs"></a>

## 13. What Alpha Bank installs

The purpose of all that SDK-team work is to avoid making every customer repeat
the compilation process.

For a published Rust-backed release, an Alpha Bank developer normally uses:

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

If Alpha Bank later deploys the customer app to supported Linux ARM64, that
environment needs the Linux ARM64 wheel for the same SDK version.
These are different files belonging to one release.

### Installing a wheel does not compile our Rust source

The SDK team has already done the compilation:

```text
SDK team
    -> builds the extension
    -> places it in the platform wheel
    -> publishes the approved wheel

Alpha Bank
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

The SDK records this policy, but enforcement in the shared
publishers is still pending with Central. The current publishing path must
not be used for this Rust-backed release before that work is integrated.

Could we publish the source files so the customer can build a compatible wheel?
That would offer a different installation path, with additional requirements.
The next section explains why we do not yet support it.

## 14. What changes if we also publish a source distribution

If no compatible wheel is available, a source archive could let Alpha Bank
build one on its own machine. That moves compilation from the SDK team to
the customer. For this package, the sdist filename has the shape:

```text
azure_cosmos-<version>.tar.gz
```

Unlike a platform wheel, it does not provide the already-built Rust extension
for the customer's machine.

### Why customer source installation is not supported yet

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
    -> Cargo and rustc build the extension for Alpha Bank's machine
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
| Python `build` package | Not required merely to run `pip install`; pip can call the SDK package builder |

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
| Python package files | Wrapper implementation, import structure, typing information, and package data |
| Binding source and build checks | Rust code to compile and checks for supplied native libraries |
| Both `Cargo.toml` files and `Cargo.lock` | Workspace, binding configuration, and selected dependencies |
| `rust-toolchain.toml` and required setup scripts | Toolchain selection and preparation commands |
| `pyproject.toml` and `azure_cosmos_package_builder.py` | Package information and the SDK package builder that prepares inputs and calls Maturin |
| Version-check code and its inputs | The check must find `_version.py`, project metadata, API metadata, and the changelog inside the archive |
| README, license, and referenced supporting files | Package description and distribution information |

The driver source need not be copied into the archive if Cargo can obtain the
approved source through the declared dependency. No active dependency may
require an unrelated local directory outside the archive.

Likewise, one target's QueryPlanInterop binary must not be included as if it
worked on every target. If the source-installation promise includes that
provider, define how the customer obtains matching files.

### Use and validate the actual source-archive creation path

The SDK package builder delegates internal sdist creation to Maturin.
`pyproject.toml` explicitly includes `azure_cosmos_package_builder.py`, the toolchain file, and setup
scripts in that archive.

The shared build can request this archive with `enable_sdist: true`.
**Generating an sdist as a build output does not
decide whether we publish it or promise customers that source installation
works.**

Internal documentation builds use the archive's README and source files, so
we retain archive generation. Publication must be blocked separately.

The SDK's package-output settings request that separation
with `skipPublishSdist: true`. **The shared publishing templates do not
read this setting.** They still select `.tar.gz` files for publication, so
the SDK flag alone does not protect customers.

Central must update the release publishers to exclude source archives from
PyPI staging and source uploads to other
release and development feeds. It must also reject source archives already
present in a wheels-only staging directory. The daily alpha-package publisher
must honor the same setting. Packages that do not opt in should retain
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
Central owns the shared code that must act on those requests. These changes
remain pending:

| Work | What Central must deliver |
|---|---|
| Synchronized version updates | Honor the SDK setting, update every version copy and stability label, and restore files if the update fails |
| Documentation installation | Keep sdist sources for page generation but install a compatible built wheel for compiled packages |
| Overloaded method documentation | Resolve types from the original method without changing SDK tracing or suppressing warnings |
| Multi-wheel namespace inspection | Inspect one exact-version wheel instead of passing several files to a single-archive helper |
| Wheels-only publication | Honor `skipPublishSdist` across all publication routes while preserving other packages' behavior |

Each change needs regression tests and must be included in the source used
by the pipeline. A saved patch or an SDK opt-in is not
evidence that the shared implementation exists. The SDK team must complete
the retained-test migration and provide the package-side runners. Central
must integrate the required checks into the normal pipeline; the temporary
job layout is not a requirement. The specific pipeline files are recorded in
the [Central pipeline handoff](#pipeline-changes-for-central-to-implement).
The current publishers still do not enforce the source-archive restriction.

### Treat the Rust-backed release as a v5 upgrade

Alpha Bank needs to distinguish an update that preserves the existing API from
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
it would accept matching 4.x versions. Passing that check does not authorize
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
| Source installation | Keep sdists unpublished until [customer source installation](#why-customer-source-installation-is-not-supported-yet) is approved and validated | Release approver, Cosmos SDK team, and Central team |
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

Configuration tests can reject a mismatched package version, a missing target,
or a build route that omits the Rust extension before compilation starts.
They can also check which library files the helper copies into the package.

Those checks do not execute the resulting extension. A Windows ARM64 wheel
still needs installation and operation tests in a compatible environment.
A wheel promising QueryPlanInterop still needs a query test that demonstrates
successful planning by that provider, not merely a library filename in the ZIP.

The release needs both kinds of evidence: correct configuration and working
final packages in the environments we promise to support.

### Pipeline changes for Central to implement

**The SDK team changes files inside `sdk/cosmos/azure-cosmos/`. Central changes
the pipeline files outside that package.** We should not change root settings
such as `.vscode/cspell.json` as part of this SDK work.

Why do we need pipeline changes at all? The old package contained Python code.
The new package also contains compiled Rust code. The pipeline must have the
tools to build that code, put it in the wheel, and test the wheel that customers
will install. Adding a test file to the package does not, by itself, tell the
pipeline to run it.

The four files below already have draft changes in this branch. Leave them
unchanged for now. Central should review and implement the work they describe.
These paths start at the repository root.

| File | Why the change is needed | What Central needs to do |
|---|---|---|
| `sdk/cosmos/ci.yml` | The pipeline needs instructions for building and checking the new Rust-backed package. | Install the selected Rust compiler, build and sign the required wheels, connect the required tests, and prevent publication of a source archive until source installation is supported. |
| `sdk/cosmos/templates/rust-tests.yml` | A wheel can build successfully and still contain broken or missing code. | Run the Rust tests and the Python tests against the installed wheel. Start the emulator for tests that need a service, and report failures. |
| `sdk/cosmos/templates/telemetry-tests.yml` | Operations can succeed while the SDK's tracing or diagnostic reporting is broken. | Run the telemetry checks against the built wheel and save their results. Missing required results must not count as success. |
| `sdk/cosmos/templates/toxiproxy-tests.yml` | Tests on a healthy connection do not show what happens when the network slows down or disconnects. | Install the network-fault test tool, run the package's failure scenarios against the built wheel and emulator, and save the results. |

For example, Alpha Bank needs a wheel that installs, reads an order, reports
useful diagnostics, and handles a broken connection as intended. These checks
cover different parts of that promise.

Central does not have to keep these exact four files or create separate jobs
for every check. It can use the existing pipeline structure. What matters is
that the required checks actually run against the right wheel and that their
failures are visible. This note records the work for Central; it does not ask
the SDK team to make more root or pipeline changes.

The package keeps its technical
terms in `sdk/cosmos/azure-cosmos/cspell.json`, without changing the root
dictionary. The draft `rust-tests.yml` and `toxiproxy-tests.yml` files now
contain file-local spelling annotations for their tool names and command-line
flags. These comments do not change pipeline behavior. The package dictionary
does not cover files outside the package.

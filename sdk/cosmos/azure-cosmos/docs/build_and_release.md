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
13. [How the pipeline chooses dependent-service regression tests](#13-how-the-pipeline-chooses-dependent-service-regression-tests)
14. [How Sphinx generates the SDK documentation](#14-how-sphinx-generates-the-sdk-documentation)
15. [What Alpha Bank installs](#15-what-alpha-bank-installs)
16. [What changes if we also publish a source distribution](#16-what-changes-if-we-also-publish-a-source-distribution)
17. [What still needs to be decided or proved before release](#17-what-still-needs-to-be-decided-or-proved-before-release)

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
repository. The workspace `Cargo.toml` uses a **Git dependency** pinned to
one commit of `azure-sdk-for-rust`:

```toml
azure_data_cosmos_driver = { git = "https://github.com/Azure/azure-sdk-for-rust", rev = "36c6f191ffe45ef44e5ef4efa26c59f0d71c3300" }
```

Cargo downloads that exact commit from GitHub. `Cargo.lock` records the same
commit, so every machine, including CI, compiles the same driver source. No
`azure-sdk-for-rust` checkout is needed. CI pipelines do not check one out.

A pinned commit is not a published release. It is a temporary choice for
the preview, because the driver changes we need are not yet on crates.io.

To move to a newer driver commit, first disable any local driver patch in
`.cargo\config.toml`; otherwise Cargo resolves the local checkout instead
of the pinned revision. Change `rev`, run
`cargo update -p azure_data_cosmos_driver`, and review the `Cargo.lock`
changes. `tests\common\test_build_configuration_unit.py` checks the pinned
commit in both files, so update it at the same time.

To try unreleased driver changes from a local checkout, see
[Build against a local driver checkout](#build-against-a-local-driver-checkout).

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
Section 16 covers the extra requirements for building from Rust-backed source.

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
does not determine the Python package release. The built extension does not
expose the crate version. Use `azure.cosmos.__version__` for the package
version.

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

The build check compares only versions. The rest of the package information
written in both `setup.py` and `pyproject.toml` is compared by a unit test,
`test_python_metadata_stays_aligned_rust` in
`tests\common\test_build_configuration_unit.py`, which the pipeline's
offline Python tests run (section 17). This covers the name, required Python version,
dependencies, the `aio` extra, classifiers, description, license, authors,
maintainers, keywords, project links and readme. A difference fails the test,
not the build.

### What the PyPI page shows

The package description on PyPI is the file named by `readme` in
`pyproject.toml`: `README.md`. When the wheel is built, the file's text is
copied into the wheel's `METADATA` file, and PyPI shows it on the package
page.

PyPI is not the only place customers read this file. Central's release
tooling treats each package's `README.md` as its customer documentation and
publishes it to learn.microsoft.com (`eng\common\scripts\Package-Properties.ps1`
and `Update-DocsMsMetadata.ps1`).

So `README.md` contains customer information only. Building and testing the
SDK is described in `docs\local_development.md`. `README.md` does not link to
it yet. The link pointed to the guide on `main`, where it does not exist
until this branch merges, so the pipeline's link check reported it as broken.

We considered two other layouts:

| Layout | Why we did not use it |
|---|---|
| Keep the build and test steps in `README.md` | Customers install a prebuilt wheel. They would still read steps they never need, such as installing the Microsoft Rust toolchain |
| Keep `README.md` for developers and point `readme` at a separate customer file | Fixes PyPI only. learn.microsoft.com would still publish the developer steps from `README.md` |

For example, an Alpha Bank developer who looks up `azure-cosmos` on PyPI or
learn.microsoft.com sees how to install and use the SDK, not how to compile
it.

Most packages in this repository also add `CHANGELOG.md` to the description,
using a setuptools-only setting that accepts a list of files. Maturin accepts
one file, so we link to the changelog instead: the `Changelog` entry in
`[project.urls]`, which PyPI shows beside the description. `setup.py` uses
the same README-only description and the same links, so both files describe
the same page.


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

- The driver's source location (currently a pinned GitHub commit).
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

### Release build settings: Cargo's defaults, on purpose

A **release profile** is a set of optional Cargo settings for optimized
builds. Three of them are often suggested to make the compiled file smaller:

- **LTO** (link-time optimization): optimize all the Rust code together
  instead of one library at a time.
- **`codegen-units = 1`**: compile each library as one piece, so the compiler
  sees more code at once.
- **Strip**: remove the names of internal functions from the compiled file.

Cargo reads these settings only from the package-level `Cargo.toml`, the file
at the top of the build. Neither of our `Cargo.toml` files sets them, so every
wheel uses Cargo's defaults.

We measured before deciding. On Windows x64, the release extension was
11.35 MB with the defaults and 11.71 MB with all three settings turned on.
Stripping saves little on Windows because the debug information is already
in a separate `.pdb` file, and LTO made the file larger.

Linux and macOS were not measured. Stripping might shrink those files, but it
also removes the Rust function names that a crash report on a customer's
machine would otherwise show. We keep the defaults until a Linux wheel built
by the pipeline shows a saving worth that cost.

The Rust SDK repository sets no release profile either, but that is not a
precedent. It publishes source code, and Cargo ignores profile settings that
come from dependencies, so the customer's own project chooses them. We ship
an already-compiled file, so our package-level `Cargo.toml` is the one that
decides.

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

In this package, the binding takes every dependency version from the
workspace file. Keep that file limited to dependencies the binding uses.
Cargo does not warn about an entry that no member uses, so remove the entry
when the binding stops using that dependency.

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
target platforms, and other inputs still matter. Nor does it freeze driver
files when a developer overrides the pin with a local checkout: those source
files can still change.

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
components = ["clippy"]
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

`components = ["clippy"]` adds clippy, which the minimal profile leaves out.
The section "Clippy: catching risky Rust code before it ships" explains it.

### Why rust-version and rust-toolchain.toml are different

The package-level `Cargo.toml` also contains:

```toml
[workspace.package]
rust-version = "1.97"
```

The binding inherits that value. It answers a different question:

| Setting | Meaning |
|---|---|
| `rust-version = "1.97"` | "This project declares Rust 1.97 as its minimum supported compiler." |
| `channel = "ms-prod-1.97"` | "Use this selected toolchain by default for our current builds." |

**Declaring a minimum does not install or select that compiler.**

A declared minimum is only true if something builds with it. CI builds only
with the selected toolchain, so `rust-version` names that same version. An
older minimum would be an untested promise; the pinned driver already needs
Rust 1.88. A unit test fails if the two versions drift apart, so update both
together.

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

### Clippy: catching risky Rust code before it ships

The compiler rejects code that is invalid. It accepts code that is valid but
risky. Tests catch only the risks that a test happens to exercise.

**Clippy** is Rust's standard code checker. It reads our Rust code without
running it and reports patterns that are known to cause bugs, waste memory, or
confuse readers. Each kind of check is called a **lint**.

For example, calling an `async` function in Rust does not run it immediately.
It returns a **future**: a package holding the remaining work plus every local
value that work needs while it waits for the network. A container-delete
future in our binding is about 28 KB. Waiting on it directly with `.await`
places all 28 KB on the thread's **stack**, the small fixed-size memory each
thread receives. Enough of these nested together can overflow the stack and
crash the customer app. Clippy's `large_futures` lint reports this, and
`Box::pin(...)` fixes it by moving the future to general (heap) memory.

**Our lint rules live in the package-level `Cargo.toml`:**

```toml
[workspace.lints.rust]
unsafe_code = "forbid"

[workspace.lints.clippy]
large_futures = "deny"
style = { level = "allow", priority = -1 }
uninlined_format_args = "allow"
```

The binding uses these rules only because its own `Cargo.toml` contains
`[lints] workspace = true`. Without that line, the rules are ignored.

| Rule | Meaning |
|---|---|
| `unsafe_code = "forbid"` | The compiler rejects any `unsafe` block. `unsafe` turns off Rust's memory-safety checks; the binding has none and must not gain any. |
| `large_futures = "deny"` | A large future awaited on the stack is an error. |
| `style` and `uninlined_format_args` allowed | Formatting-preference lints are not reported. |

The clippy rules match the driver repo (`azure-sdk-for-rust\Cargo.toml`), so
both crates follow one policy.

**Errors block CI; warnings do not.** The native CI step runs clippy before
`cargo test`:

```text
cargo clippy
    -> any error (for example, large_futures)  -> the step fails
    -> warnings only                           -> printed; the step continues
cargo test
```

Clippy also reports warnings, such as a conversion that does nothing or a
function with too many arguments. They are shown in `cargo-clippy.log` for
cleanup but do not fail the build.

Run the same check locally from the package folder:

```text
cargo clippy --workspace --all-targets --all-features --locked
```

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

In a development checkout, this compiled file is a build output, not source.
The package `.gitignore` lists the extension names (`_rust*.pyd`,
`_rust*.so`, `_rust*.dylib`) so git does not offer to commit them. The
`_rust.pyi` file beside the extension is different: it is hand-written source
and is committed (section 9 explains what it is for).

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
- Network access to GitHub, so Cargo can download the pinned driver commit,
  and access to the other Rust dependency sources.

Activate the intended virtual environment, then run these commands from the
package source directory:

```powershell
python -m pip install "maturin==1.15.0"
maturin --version
Get-Command maturin
$env:PATH = "$env:USERPROFILE\.msrustup\multiplexers\bin;$env:PATH"
$env:RUSTUP_TOOLCHAIN = $null
Get-Command cargo, rustc
cargo -V
rustc -V
$env:AZURE_COSMOS_BUILD_PYTHON_COMMIT = git rev-parse HEAD
maturin develop --release --locked
```

An existing terminal can have an older process `PATH` than the user `PATH`
configured by the installer. The commands above put the installed Microsoft
multiplexers first for this process and clear any public-toolchain override.
Confirm that both tools report the Microsoft build selected by
`rust-toolchain.toml` before rebuilding. Do not substitute public Rust merely
because the current terminal cannot find `msrustup`.

The current build configuration selects Maturin `1.15.0`. Confirm that the
command resolves to that version in the intended environment. Installing a
tool into one environment does not ensure a different shell finds it.

### Which commits the built extension records

When a customer reports a problem, support needs to know which driver code
is inside their wheel. The package version alone does not say, because the
driver is pinned by commit, not by version. So every build records two
labels in the extension, which anyone can read from
`_rust.__python_commit__` and `_rust.__rust_driver_commit__`.

`azure_cosmos_rust\build.rs` chooses them, using `build_commit.rs`:

| Label | First choice | Otherwise |
|---|---|---|
| Driver commit | `AZURE_COSMOS_BUILD_RUST_DRIVER_COMMIT`, if set | The driver's pinned commit in `Cargo.lock`. `local` if `Cargo.lock` lists the driver with no source, as for a local path build. `unknown` if neither is found |
| Python commit | `AZURE_COSMOS_BUILD_PYTHON_COMMIT`, if set | `BUILD_SOURCEVERSION`, which Azure Pipelines sets to the commit being built. `unknown` if neither is set |

So the driver label needs no setting in any build, including a source
distribution, which ships `Cargo.lock`. A local `maturin develop` has no
`BUILD_SOURCEVERSION`, so the commands above set the Python label. A label
names a commit; it does not capture uncommitted changes.

On a pull request build, Azure Pipelines builds a temporary commit that
merges the pull request into its target branch. `BUILD_SOURCEVERSION` names
that merge commit, not the pull request's last commit.

For the pipeline-specific limitation on the Python commit label, see
[Which settings reach the Linux build container](#which-settings-reach-the-linux-build-container).

`--release` requests optimized Rust code. It does not mean the SDK is being
published or approved for production.

### Build against a local driver checkout

Sometimes we need driver changes that are not in the pinned commit yet. For
example, a driver fix may still be under review in `azure-sdk-for-rust`.
Cargo's **patch** setting builds from a local checkout instead of the pinned
commit, without editing `Cargo.toml`.

This example assumes the Rust checkout sits next to the Python checkout:

```text
repos\
  azure-sdk-for-python\
    sdk\cosmos\azure-cosmos\
  azure-sdk-for-rust\
    sdk\cosmos\azure_data_cosmos_driver\
```

From the package source directory, create `.cargo\config.toml`:

```toml
[patch."https://github.com/Azure/azure-sdk-for-rust"]
azure_data_cosmos_driver = { path = "../../../../azure-sdk-for-rust/sdk/cosmos/azure_data_cosmos_driver" }
```

The relative path starts from the package source directory. Git ignores
`.cargo\` in this package, so the override cannot be committed by mistake.

Our Maturin settings always build with `--locked`, so update the lock first,
then build:

```powershell
cargo update -p azure_data_cosmos_driver
maturin develop --release --locked
```

`cargo update` switches the two driver entries in `Cargo.lock` from the
GitHub commit to the local folder. Each rebuild now compiles the checkout's
current source, including uncommitted changes. The driver commit label is
`local`, because the lock no longer names a commit.

Passing the patch to Maturin with `--config` does not work: Maturin first
runs `cargo metadata`, which does not receive `--config` and then fails on
the lock.

When finished, remove the override and restore the pinned lock:

```powershell
Remove-Item .cargo -Recurse
git checkout -- Cargo.lock
```

Do not commit a `Cargo.lock` that points at a local folder. CI does not have
the Rust checkout, and `test_build_configuration_unit.py` fails on it.

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

### Building for tests that inspect the Rust execution path

When a customer app cancels an order read, the SDK team needs evidence that
the native operation future stops, not just that the Python waiter is cancelled.
The cancellation test observes that future through a private, single-use probe.
It does not prove that sockets close or that the service backend undoes work.

The `test-probes` Cargo feature includes this instrumentation only when requested.
It also enables the six `_debug_*` exports: operation, attempt, and retry counters;
fault-rule hit counts and toggling; and cached-account-region inspection.
Their counters are compiled out of customer builds; normal request diagnostics remain.
Normal builds omit `_AsyncOperationProbe`, the `_debug_lifecycle` keyword on
`read_item_async`, and the operation's probe wrapper. Do not enable this feature
for customer wheels.

In the activated development environment, from the package source directory:

```powershell
python -m maturin develop --locked --features test-probes
$env:PYTHONPATH = "$PWD;$PWD\tests"
python -m pytest --import-mode=importlib --confcutdir=tests\fault_injection tests\fault_injection\aio\test_async_cancellation_fault.py -q
```

Set `ACCOUNT_HOST` and `ACCOUNT_KEY` to an isolated test account before running
the test. Its fixtures create and clean up uniquely named resources. It checks
native-future destruction after cancellation, a no-injection control, and
recovery using the same client. A normal build fails with rebuild instructions
instead of silently skipping this evidence. Its `cosmosRustProbes` marker
keeps the regular emulator selection from including it. CI runs it in its own
step using the same isolated probe wheel (section 17).

After testing, restore the normal build and restart Python processes that loaded
the instrumented extension:

```powershell
python -m maturin develop --locked
python -c "from azure.cosmos import _rust; assert not hasattr(_rust, '_AsyncOperationProbe')"
```

### Fault injection requires a test build and a test switch

SDK tests pass `_fault_injection_rules` to `CosmosClient` to make a request
fail on purpose, for example an order read that returns 503. A customer wheel
must not be able to inject that failure.

In `azure_cosmos_rust\Cargo.toml`, `test-probes` enables the driver's
`fault_injection` feature. Normal wheel builds omit it. Native Rust unit tests
enable it through a development dependency, which does not enable it in wheels.
Normal request diagnostics and attempt telemetry remain available in both builds.

To inspect an injected failure, tests can pass `include_fault_diagnostics=True`
to the native `create_item` or `read_item` binding, including their async twins.
Only probe wheels accept this keyword; customer wheels omit both the parameter
and its fault-payload conversion code. `include_attempts` remains available.

Both Python clients reject any non-`None` `_fault_injection_rules` argument in
a customer wheel, even when `COSMOS_ENABLE_FAULT_INJECTION=1`. The binding also
rejects nonempty rules supplied directly in a prepared configuration, before
initializing a runtime or acquiring a driver.

A probe wheel still requires `COSMOS_ENABLE_FAULT_INJECTION` to be exactly `1`
when supplying rules through either Python client. The check is in
`_prepare_fault_injection_rules` (`azure\cosmos\_backend\client_config.py`).
`tests\conftest.py` and
`tests\fault_injection\conftest.py` set the switch; the second is needed
because the native cancellation test step runs with `--confcutdir=tests\fault_injection`,
which skips the first.

In a `test-probes` build, the binding's `_debug_fault_injection_rule_hit_count` and
`_debug_set_fault_injection_rule_enabled` act only on configured rules;
unknown rule IDs fail with `unknown fault injection rule id`.
`_debug_cached_account_regions` only reads the regions the client already
cached.

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

The package builder rejects wheels without exactly one nonempty compiled
`_rust` extension, but file presence does not prove that the extension loads
or that SDK operations work.

Validate wheels locally and in the pipeline:

- Local validation follows
  one exact wheel through archive inspection, clean installation, import
  checks, the customer wheel tests, and optional sync/async emulator operations.
- Pipeline validation
  identifies the final release files, checks each platform/Python combination,
  and separates implemented checks from missing release evidence.

A successful local check does not establish that the other platform wheels work.

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

### The shared azure folder has no `__init__.py`

The layout above has no `azure\__init__.py`, on purpose. Every `azure-*`
package installs into the same `azure` folder, so no single package should
own a file in it. If our wheel shipped `azure\__init__.py`, pip would record
it as ours. Uninstalling azure-cosmos would then delete it while, for
example, azure-storage-blob still uses the folder.

Without that file, Python treats `azure` as a **namespace package**: one
import name whose contents can come from several folders. `azure.cosmos`
comes from our wheel and `azure.core` from azure-core's.

The source tree keeps the file for development, so `[tool.maturin] exclude`
in `pyproject.toml` leaves it out of the wheel only. `main`'s `setup.py` did
the same by excluding the `azure` package. The source archive still includes
it, as `main`'s did.

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

### `_rust.pyi` is written by hand

Nothing generates `_rust.pyi` from the Rust code. When a binding function is
renamed or gains a parameter, someone must update the stub too. Type checkers
and editors trust the stub, so a stale one hides the mistake until the call
runs.

The stub declares every export of a normal build: each operation and its
`_async` twin, runtime and driver-handle functions, the feed cursor, the
three error classes, and the test diagnostics. It has no `__getattr__`
catch-all, so a type checker reports any name the stub does not declare.

The unit test `test_type_stub_matches_the_installed_rust_module_rust`
(`tests\common\test_naming_contracts_unit.py`) reads the stub that sits next
to the installed extension and compares it with the real module. It fails if
the extension has an export the stub does not declare, if the stub declares a
name the extension lacks, or if a declaration differs:

| Declared in the stub | Must match in the extension |
|---|---|
| Function | Name, and each parameter's name, kind (positional or keyword-only), and default |
| Class | Name, properties, and constructor parameters |

The six `_debug_*` functions, `_AsyncOperationProbe`, the `include_fault_diagnostics`
keyword on create/read item bindings, and the `_debug_lifecycle` keyword of `read_item_async`
exist only in `test-probes` builds (section 7), so the test accepts them only
in those builds.

**The stub does not check every call the SDK makes.** The SDK finds most
operations by name at run time, for example
`getattr(_rust_module, "read_item")` in `azure\cosmos\_backend\binding_adapter.py`,
so a type checker cannot see which function is called or check its
arguments. Tests that run the operation catch those mistakes instead.

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

The platform tag is the only operating-system information the installer
uses. Package metadata also has optional **operating-system classifiers**,
labels shown on the package index page. The installer ignores them.

We do not declare one. The pure-Python package said
`Operating System :: OS Independent`, which is false for platform wheels.
Listing each operating system would be one more copy of the target list to
keep in step. `azure-storage-extensions`, another compiled package in this
repository, also declares none.

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

One more setting must agree with `abi3-py310`. The Windows ARM64 wheel is
cross-compiled with a generated PyO3 config file, and
`pyo3-abi3-minimum = "3.10"` in `pyproject.toml` keeps that file on the same
stable-ABI baseline. Section 12 explains why.

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

Alpha Bank's customer app stores orders in the `sales/orders` container.
A **container** holds items, and the service backend distributes those items
across **physical partitions**, separate portions of its storage.
The bank wants to know: "How many orders does each customer have?"
Consider this illustrative set:

| Physical partition | Order ID | Customer |
|---|---|---|
| A | `order-42` | `customer-17` |
| A | `order-43` | `customer-17` |
| B | `order-44` | `customer-88` |

The customer app asks:

```sql
SELECT c.customerId, COUNT(1) AS orderCount
FROM c
GROUP BY c.customerId
```

`GROUP BY` gathers orders for the same customer. `COUNT` counts them;
this calculation is called an **aggregate**. The required answer is two
orders for `customer-17` and one for `customer-88`. Reading only partition A
would omit `customer-88`.

These are illustrative expected results, not an executed test or a claim
that the pinned SDK supports this query from start to finish.

### Planning and execution are different jobs

A **query plan** tells the driver how to obtain and combine the results.
For this example, the required work is:

```text
Prepare instructions for obtaining each customer's order count
    -> request the required data from the service backend
    -> combine the replies into the correct counts
    -> return customer-17: 2 and customer-88: 1
```

Those lines explain the work, not the literal format of a driver's plan.

**Planning** prepares the instructions. **Execution** carries them out.
Adding execution support does not automatically teach every planner to
produce the instructions it needs.

Preparing a plan on the customer app's machine does not move the database
there. The service backend still supplies the data.
The driver can obtain a plan from more than one place.
The **gateway** is the service backend's front end; it can return a plan to
the SDK. That describes where the SDK obtains the plan, not which internal
service component generates it.

<a id="there-are-three-query-planning-providers"></a>

### There are three ways to obtain a query plan

The code calls each source of plans a **provider**. This is simply a name
for one of the three implementations below, not another SDK layer.

| Source of the plan | Where it runs | What the installed package needs |
|---|---|---|
| QueryPlanInterop | Separate compiled library loaded on the customer app's machine | A matching library and its dependencies |
| Pure-Rust planner | Code compiled into the Rust driver inside `_rust` | No separate QueryPlanInterop library |
| Gateway plan retrieval | Service backend's gateway | A request to the gateway for a plan |

Here, **local** means on the customer app's machine, not in the remote
service backend. Both QueryPlanInterop and the pure-Rust planner are local.
The **planning mode** selects which sources the driver may try.
The default `LocalPreferred` mode means the driver normally tries an enabled
QueryPlanInterop library, then the pure-Rust planner, then the gateway.
The pure-Rust planner handles eligible query shapes, not every query.

Trying the next source when the previous one cannot supply a plan is
**fallback**. `GatewayOnly` explicitly bypasses both local planners.
These are selection rules, not a requirement that every query
contact every source; the driver can recognize some queries as having
no possible results.

**No QueryPlanInterop library does not mean every query must use gateway
planning.** Eligible queries can still use the Rust planner already compiled
into the extension.

### What the query discussion identifies as missing

Return to Alpha Bank's order-count query. In the pinned driver revision
`36c6f191ffe45ef44e5ef4efa26c59f0d71c3300`, the production pure-Rust
planning path explicitly declines aggregates and `GROUP BY`. It also
declines vector and hybrid-search functions, which are separate query
families. The checks are in `query/local_plan_adapter.rs`.

The pinned driver includes aggregate execution support, and the Python
binding advertises that support when requesting a query plan. Execution
support does not by itself add pure-Rust local planning for these queries.

For the bank, a declined local plan does not by itself mean the query fails:
another source may supply a usable plan. Execution must also support that
plan. Without QueryPlanInterop, this example cannot rely on the current
pure-Rust planning path; the driver tries the gateway instead.

**Extending the pure-Rust planner and shipping QueryPlanInterop are separate
tasks.** Adding the library does not fill in the pure-Rust planner's missing
code, and extending that planner does not require packaging the library.

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

If Alpha Bank develops on Windows and deploys to Linux, each installed SDK
needs the matching library if we promise QueryPlanInterop planning there.
The bank should not have to find or compile those files itself.

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
64-bit file class.

The SDK package builder decides which files count as native libraries and
copies only those. It passes their names to the binding's build in
`AZURE_COSMOS_QUERYPLANINTEROP_STAGED_FILES`, and the checks inspect exactly
those files. So every copied file is checked, and the rule for picking files
exists only in the builder.

A macOS **universal** file holds builds for several processors, such as Intel
and Apple Silicon. The check accepts it if one of those builds matches the
target, and ignores builds for processors it doesn't recognize.

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

When QueryPlanInterop is used, the driver loads the library and supplies the query
and the container's partition-key definition: the fields used to group related
items for storage. The library returns a
plan. The driver then sends the required data requests to the service backend
and combines its replies. QueryPlanInterop creates the plan; it does not read
`order-42`, `order-43`, or `order-44` from the database.

The driver does not download or compile QueryPlanInterop automatically.

### Why writing the runtime setting is a temporary approach

At the pinned driver commit, the environment variable is the only way to
give the driver this directory. The driver reads it with `std::env::var`
when it loads the library (`query_plan_native/native.rs`). It has no option
for passing the directory instead. So the Python wrapper writes it into the
process environment, once per process, just before the SDK first starts the
driver (`_binding_adapter_shared.py`).

That write affects the whole customer app, not just the SDK:

| Effect | Example |
|---|---|
| Another thread may read the environment at the same moment. On Linux this can crash the process. The SDK's lock stops two SDK calls from writing at once, but it cannot stop other code from reading. | Alpha Bank's app has a thread doing a DNS lookup while the first Cosmos request starts |
| Child processes inherit the setting, and an existing setting wins. | Alpha Bank's app, running in virtual environment A, starts a helper program in virtual environment B, which has a different SDK version. B loads A's library, which may not match B's driver |

The time window for the first effect is small, because there is only one
write per process.

**The preview is not affected.** No pipeline sets
`AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR`, so preview wheels contain no
`.libs` directory. Without it, the wrapper writes nothing. The write starts
only when we ship QueryPlanInterop, so the driver fix below is needed
before then.

The fix belongs to the driver: accept the directory as an option when the
driver starts. The driver team's design record ADR-0009 already lists
`AZURE_COSMOS_QUERYPLANINTEROP_DIR` as a temporary setting to replace with
such an option. Once that option exists, the wrapper passes the path to the
driver and stops writing the environment.

### Prove which planner ran

A successful query is not enough evidence for the QueryPlanInterop feature.
The Rust planner or gateway may have supplied the plan instead.

The driver writes a `provider` label in its diagnostic logs to identify
the source of a plan or the source it attempted to use:

| Log label | Meaning |
|---|---|
| `native_ffi` | QueryPlanInterop |
| `local_rust` | Pure-Rust planner |
| `gateway` | Plan returned by the gateway |

These exact labels are more useful than the word "native" on its own.
`native_ffi` identifies QueryPlanInterop in this code. In a conversation,
"native" might instead mean the Rust driver's execution support. Do not
assume which meaning the speakers intended without the referenced PRs.

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

For Alpha Bank's example, require both the correct counts and evidence of
which source supplied the plan. Then check the missing-library and
unsupported-local-plan paths. A correct answer obtained through the gateway
proves neither QueryPlanInterop use nor newly added pure-Rust planning support.

### Deferred work and completion criteria

| Work | Owner |
|---|---|
| Identify the producing team, approved binary source, and matching driver/library versions | Cosmos SDK team, Rust driver team, and producing team |
| Confirm permission to redistribute the libraries, licensing, signing, and required companions | Producing team and release approver |
| Supply each target's files before its wheel build, including inside Linux containers | Central team, using SDK-owned staging configuration |
| Inspect final wheels and demonstrate QueryPlanInterop planning on supported targets | SDK team supplies tests; Central runs them |
| Accept the library directory as a driver option, so the wrapper stops writing `AZURE_COSMOS_QUERYPLANINTEROP_DIR` into the process environment. Needed before the first wheel that ships QueryPlanInterop | Rust driver team, then Cosmos SDK team |
| Extend production pure-Rust planning for the query families discussed, separately from query execution; verify the changes reach the driver revision Python uses | Rust driver team implements; Cosmos SDK team verifies integration |
| Demonstrate Alpha Bank's expected counts, the successful planning source, and fallback behavior using the installed SDK | Cosmos SDK team |

Keep the completion evidence separate: correct results establish execution
for the tested query; successful planning logs identify the planner; final
package checks establish which libraries actually ship. Packaging work is
complete only when the installed SDK proves QueryPlanInterop works on the
promised targets. Pure-Rust planning work needs its own successful evidence.

## 12. How the pipeline builds and releases the complete wheel set

The local workflow answers:

> "Can this machine build and install one wheel?"

The pipeline must answer a larger question:

> "Can we build the whole required set from the intended source and
> publish only the approved results?"

This section covers build preparation, packaging, SDK tests, and release processing.
[Section 13](#13-how-the-pipeline-chooses-dependent-service-regression-tests)
explains dependent-service test selection;
[section 14](#14-how-sphinx-generates-the-sdk-documentation) follows the
separate documentation-generation step.

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

The pipeline must install the Microsoft Rust tools selected in
[section 5](#rust-toolchaintoml-selecting-the-build-tools) before building
wheels. This prepares the compiler; it does not install or publish the SDK.
Developer-machine installation follows the separate procedure in
[section 7](#install-the-microsoft-rust-toolchain-on-a-developer-machine).

### Who creates rust-toolchain.toml, and where is it used?

`rust-toolchain.toml` is an **SDK-owned configuration file** in
`sdk\cosmos\azure-cosmos`, alongside `pyproject.toml`. The SDK team creates
and maintains it with the package source. It is not generated by the
pipeline or by the tool installer.

**The pipeline reads the same selection used for local development.**
It must prepare the tools wherever compilation actually runs:

| Environment | How the file is used |
|---|---|
| Pipeline build machine | The installation step reads the file from the configured package directory and prepares that toolchain before the wheel build. |
| Linux wheel-build container | The compiler must also be installed inside the container. Our `before-all` preparation in `pyproject.toml` obtains `msrustup` with `scripts\install-msrustup.sh`, then runs `msrustup toolchain install` from the mounted source directory. Last, `scripts\configure-cargo-feed.sh` points Cargo at the dependency feed if the pipeline forwarded its address; without an address, Cargo keeps using crates.io. |

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

When the pipeline supplies its own ARM64 Python libraries, the shared build
tool (`eng\tools\azure-sdk-tools\ci_tools\windows_wheels.py`) also writes a
**PyO3 config file**: a small text file that tells PyO3 which Python it is
building for, instead of letting PyO3 inspect the x64 Python running the build.
That file must also say the extension uses the stable binary interface, or it
would describe a version-specific build. The SDK supplies this in
`pyproject.toml`:

```toml
[tool.azure-sdk-build]
pyo3-abi3-minimum = "3.10"
```

The value must match PyO3's `abi3-py310` feature and `requires-python`. The
tool rejects it for free-threaded Python builds, which this configuration does
not select.

Linux wheel builds run inside the prepared containers introduced in section
11. The compiler setup, required credentials, and input files must be available
where the build actually runs, not just on the host.

### Which settings reach the Linux build container

The container does not see the build machine's environment variables. It
sees only the variables named in a **pass list**. Two places define that
list, and only one is used for a given build:

| Pass list | Used when | Variables it forwards |
|---|---|---|
| `environment-pass` in our `pyproject.toml` | Someone runs cibuildwheel without the pipeline, for example on a developer machine | `PIP_INDEX_URL`, `MSRUSTUP_ACCESS_TOKEN`, `MSRUSTUP_PAT`, `MSRUSTUP_FEED_URL`, and the three `CARGO_REGISTRIES_AZURE_SDK_FOR_RUST_PUBLIC_*` variables |
| `CIBW_ENVIRONMENT_PASS_LINUX`, set by Central's `build-package-artifacts.yml` | Pipeline builds | `PIP_INDEX_URL`; because `ci.yml` sets `InstallMsRustToolchain: true`, also the same Rust variables except `MSRUSTUP_PAT` |

**In the pipeline, Central's list replaces ours; the two are not combined.**
Today this causes no failure. `install-msrustup.sh` accepts either
`MSRUSTUP_ACCESS_TOKEN` or `MSRUSTUP_PAT`, and the pipeline forwards the
access token.

The risk is a future change. If our Linux `before-all` step starts to need a
new variable, adding it to `pyproject.toml` is not enough for pipeline
builds. Central must add it to their list. `BUILD_SOURCEVERSION` is one
such variable today: without it, Linux wheels record the Python commit as
`unknown` unless an explicit `AZURE_COSMOS_BUILD_PYTHON_COMMIT` override is
supplied. This is the source-confirmed fallback, not a result from an
inspected release wheel. Windows and macOS builds run on the build machine,
so they see `BUILD_SOURCEVERSION`. The driver label is unaffected because
it comes from `Cargo.lock`, which is inside the container.
See [section 7](#which-commits-the-built-extension-records) for the label
selection rules and [Central's follow-up](#central-changes-still-required)
for the required change and final-wheel checks.

### The pipeline's login stays visible for the whole build

`MSRUSTUP_ACCESS_TOKEN` is not a token made only for the Rust installer. In
the pipeline, `build-package-artifacts.yml` sets it to `System.AccessToken`,
which is the pipeline's own login. It can do whatever the pipeline's account
is allowed to do, such as reading internal feeds.

We need it for one thing: `install-msrustup.sh` uses it in `before-all` to
download the Microsoft Rust installer. But the variable is set for the whole
"Generate Packages" step, and on Linux the pass list forwards it into the
container. So every program the build runs can read it, not just our
script. That includes pip's build tools, Cargo, and each third-party
crate's build script (`build.rs`). On Windows and macOS the same step sets
it directly on the build machine.

For example, if a compromised crate's `build.rs` read
`MSRUSTUP_ACCESS_TOKEN`, it would get the pipeline's login, not just
installer access. Our scripts only send the token in a `curl` header and
never print it.

This is the same on `main`, and Central owns the fix (section 17, "Central
changes still required").

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

The Cargo feed does not select the compiler version. It also does not supply
the driver: Cargo fetches the pinned driver commit from GitHub directly, not
through the feed.

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

### How the pipeline organizes and runs the SDK tests

Alpha Bank might run its customer app on Python 3.10 today and Python 3.14
after an upgrade. Building a wheel successfully does not show that the SDK
behaves correctly on both versions.

The pipeline therefore has separate Windows test jobs for Python **3.10,
3.11, 3.12, 3.13 and 3.14**. Each job uses its own Python environment and
starts its own **emulator**, a local program that acts as the database for
tests. The jobs do not share one emulator.

The job name also says which installation arrangement it checks. For example:

| Job name | What it checks |
|---|---|
| **Emulator Tests Python 3.13 Standard** | Install the ready-made wheel and test it. Separately install from source and test that installation too. |
| **Emulator Tests Python 3.13 Special** | Check SDK imports. Separately install the wheel and remove `aiohttp`, an optional Python networking library, before running selected tests. |
| **Emulator Tests Python 3.13 Dependency Checks** | Install the latest versions of the libraries the SDK depends on, then run selected tests to check that they still work together. |

These are different ways to check the same SDK, not different SDK packages.
The same three arrangements exist for every Python version above.

For a **pull request**, a proposal to change the source code, the pipeline
uses the five Standard jobs. Runs that are not for a pull request use the
internal configuration: five Standard, five Special and five Dependency
Checks jobs, making **15 test jobs**. These counts describe the Cosmos
emulator tests; the package-build jobs described earlier are separate.

#### Follow one Standard job

Take **Emulator Tests Python 3.13 Standard**. The job first builds a separate
SDK package with test-only controls for creating failures and observing Rust
operations. The pipeline calls these controls **test probes**, and the step
is named **Build and verify an isolated test-probes wheel**. This package
stays separate from the files prepared for customers.

After starting the emulator, the job runs the following steps in order.
The other four Standard jobs use the same steps with their own Python
versions.

| Step name shown in the pipeline | What it does |
|---|---|
| **Run Tests** | Check that the customer package loads, performs basic operations, and does not expose the test-only controls. Central owns this step's name. |
| **Emulator Functional Tests and Dependency Checks** | Check normal SDK operations against the emulator: creating, reading, querying, updating and deleting resources. The copied functional tests selected for emulator testing run here. |
| **SDK Fault-Injection Tests** | Use SDK test controls to deliberately create failures, then check retries, timeouts, errors and recovery. Copied tests that inject failures belong here rather than in the normal functional group. |
| **Prepare Supplemental Test Environment** | Check that the separate test package has the controls needed by the remaining tests. This step does not rebuild the package. |
| **Rust Unit Tests - Default Features and Clippy** | Run Clippy, the Rust code checker, then test individual pieces of Rust code without the test-only controls enabled. |
| **Rust Unit Tests - Test Probes** | Run the Rust tests with the test-only controls enabled. |
| **Python Unit Tests** | Test individual pieces of Python behaviour without needing a database. |
| **Native Cancellation Tests** | Cancel an operation and check that its Rust work stops and the client remains usable afterward. |
| **Telemetry Unit Tests** | Check records of what operations did, along with counts and timings, without sending them to a live monitoring account. |
| **Network Fault Tests - Toxiproxy** | Use Toxiproxy, a program placed between the SDK and emulator, to disrupt actual network connections and check how the SDK responds. |

The normal functional group does not also run the SDK fault-injection,
cancellation or Toxiproxy groups. They have their own selections.

#### What runs twice, and what runs once?

In a Standard job, **Run Tests**, **Emulator Functional Tests and Dependency
Checks**, and **SDK Fault-Injection Tests** each check both installation
methods:

```text
Install the wheel -> run that test group
Install from source -> run that test group again
```

The remaining test groups run **once per Standard job**, not once per
installation method. The Python groups reuse the separate test package;
the Rust steps compile and run their selected Rust tests.

So there are two reasons for repetition: checking five Python versions,
and checking two installation methods. Testing source installation here
does not mean source archives are published for customers; section 16
explains that separate release decision.

The Special and Dependency Checks jobs keep the customer-package,
functional and SDK fault-injection checks, using their own installation
arrangements. They skip the steps from **Prepare Supplemental Test
Environment** onward in the table. The Special job's import check is not
repeated in the SDK fault-injection step.

Steps named **Publish ... Results** upload results already produced by
the tests. They do not run the tests again. Rust test output is saved in
separate logs.

**This describes what the pipeline is configured to run, not proof that
every test has passed.** Existing skips still apply. The expanded
five-version test coverage still needs confirmation from a complete
pipeline run.

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

## 13. How the pipeline chooses dependent-service regression tests

The Cosmos SDK team's tests check that Cosmos operations still work after a
change. But another package might use Cosmos and rely on behavior that changed.
The pipeline therefore also needs to identify those packages for
**regression testing**: checking that previously working behavior still works.

### Start with one package that uses another

Imagine a package called `azure-order-reporting` that reads orders through
`azure-cosmos` and prepares reports for Alpha Bank. This is an illustrative
package, not a dependent we have found in the repository.

```text
Alpha Bank's customer app
    -> uses azure-order-reporting to prepare an order report
    -> azure-order-reporting uses azure-cosmos to read the orders
```

In this example, `azure-cosmos` is a **dependency** of the reporting package:
the reporting package needs it to work. A Cosmos change could therefore
affect the bank's reports even if the Cosmos tests pass.

Our repository contains many separately installable packages, grouped under
folders such as `sdk\cosmos`, `sdk\storage`, and `sdk\monitor`. Sharing the
repository does not mean they all depend on Cosmos.

### What Ensure service coverage actually does

`Ensure service coverage` is a pipeline step that prepares the list of
dependent services to test. Here, coverage means selecting relevant services,
not measuring the percentage of Cosmos source code exercised by tests.

The shared tool reads **package metadata**: information such as the package
name, version, and declared dependencies. Files such as `pyproject.toml`
and `setup.py` provide that information.

For a Cosmos run, the process is:

```text
Identify the packages targeted under sdk\cosmos
    -> scan package metadata across the repository
    -> find packages that declare those Cosmos packages as dependencies
    -> select their service folders for the regression-test plan
```

The scan must look beyond `sdk\cosmos` because a dependent package can live
in another service folder. In our example, it would find the reporting
package's declared dependency on `azure-cosmos` and select its service.

`scripts\devops_tasks\update_regression_services.py` coordinates this selection.
Its dependency lookup is in `scripts\devops_tasks\test_regression.py`.
This is discovery of declared dependencies inside the repository, not a
search of every external package or customer app that uses Cosmos.

### Why a Storage package can stop a Cosmos pipeline

During the broad scan, the tool can encounter a package whose metadata it
cannot read. If that error stops discovery, the pipeline cannot finish
selecting the Cosmos-related services.

That is where the reported `azure-storage-extensionstransfer` version error
occurred. This is an Azure Storage SDK package under `sdk\storage`, not the
storage used internally by the Cosmos DB service backend.

**Encountering that package does not prove it depends on Cosmos.**
The failure occurs while reading metadata, before the dependency selection
finishes. It is not a failed Cosmos operation or regression test.

Ownership depends on the cause: incomplete package metadata belongs to the
package's team; valid metadata that the shared reader cannot understand
requires Central's tooling work.

### Does moving Cosmos to v5 avoid this scan?

Return to the reporting package. Its dependency declaration decides which
Cosmos versions an installer may select:

| Illustrative declaration | Allows a final Cosmos v5 release? |
|---|---|
| `azure-cosmos==4.17.2` | No; it requests exactly that version |
| `azure-cosmos>=4.0,<5.0` | No; it allows v4 but excludes v5 |
| `azure-cosmos>=4.0` | Yes; it has no upper version limit |

A major-version bump signals the breaking release, but does not automatically
protect every dependent package from selecting it. A package that cannot use
v5 needs a dependency constraint that excludes it.

The regression discovery tool answers a different question: which package
names are declared as dependencies? Its dependency map uses names, not the
allowed version ranges. Even a reporting package restricted to v4 would
still be identified as depending on `azure-cosmos`.

Therefore, bumping Cosmos to v5 does not bypass the repository-wide metadata
scan or resolve the Storage metadata failure.

### Which packages currently depend on Cosmos?

**No dependent package has been confirmed by this investigation.** The
reported discovery run failed before producing the dependent-service list.
The reporting package above remains only an example, and the Storage error
does not establish a dependency.

The current conclusion is "dependents not yet established," not "there are
no dependents." A completed discovery result is needed before naming the
packages and services that require regression testing.

<a id="13-how-sphinx-generates-the-sdk-documentation"></a>

## 14. How Sphinx generates the SDK documentation

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

These are customer-facing SDK API reference pages that help Alpha Bank's
developers understand classes, methods, parameters, and return values.

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

### Which jobs publish the documentation

`Generate Docs` saves the Sphinx pages in a pipeline artifact named
`documentation`. Saving that artifact does not publish the pages for customers.

The release template, `eng\pipelines\templates\stages\release-artifact.yml`,
defines two separate documentation jobs:

| Job | Display name | What it does |
|---|---|---|
| `PublishGitHubIODocs` | Publish Docs to GitHubIO Blob Storage | Downloads the `documentation` artifact and uploads the generated Sphinx pages to documentation hosting |
| `PublishDocs` | Docs.MS Release | Updates documentation metadata in `MicrosoftDocs/azure-docs-sdk-python` for the Microsoft Learn publishing process |

Both jobs depend on `PublishPackage` and run after it succeeds, subject to
the release conditions and documentation-publishing skip settings.

**These are different publishing routes.** `PublishDocs` does not upload the
Sphinx pages to Microsoft Learn; it updates the documentation repository.
The Learn build and publication process is separate from the Sphinx upload.

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

**Pending Central work:** the shared documentation check still installs the
source archive, triggering another Rust build that can fail when the selected
toolchain is unavailable. Central owns updating this check to use a compatible,
already-built SDK wheel instead.

### How documentation resolves types on traced methods

**Status: a possible issue to investigate, not a confirmed SDK documentation
failure or an agreed fix.**

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

One possibility to investigate is whether the documentation tools look up
an overload's type names in the tracing wrapper's file instead of the
original method's file. If so, they might not identify the intended
`ContainerProxy` class. The presence of wrappers and overloads alone does
not prove that this happens.

Before proposing a fix, reproduce a type-resolution warning and check
whether using the original method's type definitions removes it. Only then
can we identify the cause and required change. Any change to shared
documentation tooling under `eng/` belongs to Central.

This is separate from documentation setup failing to build a source archive
because the selected Rust toolchain is missing.

The SDK must keep its tracing wrapper and runtime behavior, and documentation
warnings must remain errors.

<a id="13-what-customer-installs"></a>
<a id="13-what-alpha-bank-installs"></a>
<a id="14-what-alpha-bank-installs"></a>

## 15. What Alpha Bank installs

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

### Which customers have no compatible wheel

[Section 10](#the-prototypes-five-targets) lists the five configured targets.
Customers on other platforms have no wheel for this version, even though
the default `core-python` backend does not need the Rust extension:

| Platform | Why no wheel matches |
|---|---|
| Intel Mac | We build macOS for ARM64 only |
| Alpine and other musl-based Linux | `skip = ["*-musllinux*"]` |
| Linux with glibc older than 2.28, such as Amazon Linux 2 and RHEL 7 | Our Linux wheels require glibc 2.28 |
| Other processors, such as 32-bit Windows | No wheel targets them |

The pure-Python package (for example 4.16.1) installed on all of them,
because its single `py3-none-any` wheel matches any platform. So for these
customers this is a regression.

What pip does on these platforms depends on whether the customer pins a
version:

| Customer's request | What pip does |
|---|---|
| `pip install azure-cosmos` | Quietly installs the newest earlier version that has a matching file, which is the last pure-Python release |
| `pip install azure-cosmos==<this version>` | Fails with "No matching distribution found" |

We checked both with pip 24.0, using a local folder with a `py3-none-any`
version 1.0 and a Linux-only version 2.0.

The quiet case is the harder one to support: Alpha Bank's Intel Mac
developer gets an older SDK than its Linux servers, with no warning.

We accept this for the preview. Section 17 records the decision needed
before general availability.

Could we publish the source files so the customer can build a compatible wheel?
That would offer a different installation path, with additional requirements.
The next section explains why we do not yet support it.

<a id="14-what-changes-if-we-also-publish-a-source-distribution"></a>
<a id="15-what-changes-if-we-also-publish-a-source-distribution"></a>

## 16. What changes if we also publish a source distribution

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
| Rust dependency sources | Must be accessible. Cargo downloads the pinned driver commit from GitHub and other dependencies from crates.io. A pinned commit is a preview choice; supporting standalone source installation needs the approved published driver described in [section 2](#how-the-build-obtains-the-rust-driver) |
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
machine supplies missing source files or a local Rust checkout.

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

### Today's archive is missing files that main's archive carried

Before Rust, setuptools built the source archive. It read `MANIFEST.in`,
which on `main` lists the extra files to copy in:

```text
include *.md
include LICENSE
recursive-include samples *.py *.md
recursive-include tests *.py
recursive-include doc *.rst
```

**Maturin builds the archive now, and Maturin does not read `MANIFEST.in`.**
Our `MANIFEST.in` says so in its first line. It stays only because the
repository's sdist check (`verify_sdist.py`) requires its `py.typed` line
when the file exists. `setup.py` also refuses to build archives
([section 4](#why-setuppy-must-remain)).
To change archive contents, edit `include` and `exclude` under
`[tool.maturin]` in `pyproject.toml`. Maturin adds the
binding and the Python package on its own, and `README.md` because
`pyproject.toml` names it as `readme`. Every other file
must be listed under `[tool.maturin] include` in `pyproject.toml` with
`format = "sdist"`. That list does not name the files above, so they
silently dropped out.

A Maturin source archive built from this branch has 263 files:

| Content | In main's archive | In today's archive |
|---|---|---|
| `azure\cosmos\` Python package | Yes | Yes (210 files) |
| `azure_cosmos_rust\` binding source | Not applicable | Yes (40 files) |
| `README.md`, `CHANGELOG.md` | Yes | Yes |
| `LICENSE` | Yes | **No** |
| `samples\` | Yes | **No** |
| Python `tests\` | Yes | **No** |
| `doc\*.rst`, `api.md`, `Contributing.md` | Yes | **No** |
| Rust driver source | Not applicable | No; Cargo downloads the pinned commit during the build |

Only `LICENSE` is required by the table in the previous subsection. The
package is MIT licensed, and the license text should travel with its source.
The file exists in the package directory; it is simply not listed. Samples,
tests, and docs do not affect whether the archive builds. `main` shipped
them, so leaving them out is a visible change for anyone who used them.

Whether the archive builds on a clean machine has not been tested.

The preview release publishes wheels only, so this does not block it. Before
any release that publishes a source archive, add `LICENSE` to
`[tool.maturin] include` with `format = "sdist"`. Decide whether to add
samples, tests, and docs to match `main`, then rebuild the archive and list
its contents to confirm.

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

Our Cosmos configuration in `sdk\cosmos\ci.yml` already requests that
separation with `skipPublishSdist: true`. **The shared publishing templates do not
read this setting.** They still select `.tar.gz` files for publication, so
the SDK flag alone does not protect customers.

**The fix belongs in Central's shared pipeline files, not our Python wrapper
or Rust binding.** These files are in the same `azure-sdk-for-python`
repository, but fall under the `/eng/` ownership rule in `.github\CODEOWNERS`.

| Owner | File | Required change |
|---|---|---|
| Our Cosmos team | `sdk\cosmos\ci.yml` | Keep `skipPublishSdist: true`; the setting is already present. |
| Central team | `eng\pipelines\templates\stages\release-artifact.yml` | Read the setting and exclude source archives from PyPI staging and uploads to release and development feeds. |
| Central team | `eng\pipelines\templates\steps\publish-alpha-package.yml` | Read the same setting and skip source-archive uploads for daily development packages. |

Central must also reject source archives already present in a wheels-only
staging directory. Packages that do not opt in should retain their existing
publication behavior.

Our Cosmos team must verify the result: start with a release folder containing
both `azure_cosmos-<version>-cp310-abi3-win_amd64.whl` and
`azure_cosmos-<version>.tar.gz`, then check that the publishing steps select
only the wheel. Repeat the check for the release and daily development paths.
This describes the required check, not a completed pipeline run or evidence
that an unwanted source archive has already been published.

Do not publish this Rust-backed package through those paths until the
restriction is implemented and demonstrated.

For customers, `pip --no-binary` requests installation from source rather than
a prebuilt wheel. Under the required wheels-only policy, that option will not
provide an installation path for this release.

The release tooling must use and validate this path. Preserving the
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

<a id="15-what-still-needs-to-be-decided-or-proved-before-release"></a>
<a id="16-what-still-needs-to-be-decided-or-proved-before-release"></a>

## 17. What still needs to be decided or proved before release

### SDK pipeline wiring and Central ownership

These paths start at the repository root. Cosmos owns the files under
`sdk/cosmos/templates/`; `sdk/cosmos/ci.yml` has Central reviewers. A folder
named `templates` is not automatically Central-owned.

The [test-job explanation](#how-the-pipeline-organizes-and-runs-the-sdk-tests)
describes which jobs run these checks and how often.

| File | Current responsibility | Owner or reviewer |
|---|---|---|
| `sdk/cosmos/ci.yml` | Select the customer-package checks and add the SDK-owned test steps to the shared pipeline. | Cosmos-specific configuration with Central review |
| `sdk/cosmos/tests.yml` | Reuse `prepare-test-probes.yml` to build a separate probe wheel for live-account tests, then pass that wheel to the shared test runner. | Cosmos SDK team |
| `sdk/cosmos/templates/prepare-test-probes.yml` | Build and verify the probe wheel under the agent temporary directory, outside publish artifacts; retain packaged native sidecars from the downloaded customer wheel. | Cosmos SDK team |
| `sdk/cosmos/templates/emulator-probe-tests.yml` | Keep customer-package results and run separate functional and SDK fault-injection groups for each configured installation check. | Cosmos SDK team |
| `sdk/cosmos/templates/rust-tests.yml` | Run Rust unit tests, Python unit tests and cancellation tests once in each Standard job; save their results. | Cosmos SDK team |
| `sdk/cosmos/templates/telemetry-tests.yml` | Run diagnostic checks against the separate test package once in each Standard job; require their results. | Cosmos SDK team |
| `sdk/cosmos/templates/toxiproxy-tests.yml` | Install the network-fault tool, run its tests once in each Standard job, and require their results. | Cosmos SDK team |

<a id="only-microsoft-employees-can-build-the-package-today"></a>

### A supported build procedure for external contributors

Suppose an Alpha Bank developer wants to fix the SDK and test the changed
Rust-backed code. Installing a ready-made wheel does not build their changes:
they need to compile the Rust extension from the checkout.

The current setup selects Microsoft's Rust toolchain, the compiler and
associated build tools:

| File in the package directory | What the code establishes |
|---|---|
| `rust-toolchain.toml` | Selects `ms-prod-1.97` |
| `scripts\install-msrustup.sh` | Requires authentication and defaults to an internal DevDiv package feed |
| `Cargo.toml` | Declares Rust `1.97` as the minimum compiler version |

These settings establish an internal-toolchain default. They do **not** prove
that building with a public Rust compiler is impossible. A public-toolchain
build has not been demonstrated by this review.

**There is an existing pattern we can follow, but applying it needs work.**
The inspected `azure-sdk-for-rust` checkout selects public Rust `1.95` in
its root `rust-toolchain.toml`. Its internal native-artifact build instead
uses `eng\templates\ms-rust-toolchain.toml`, selecting `ms-prod-1.95`.
The pipeline step `eng\pipelines\templates\steps\use-ms-rust.yml` replaces
the checkout's toolchain configuration for that build.

That separates the compiler contributors use from the compiler used for
internal release builds. We can adopt the same separation for the Python
package; contributors need not use the release compiler merely because our
pipeline uses it. However, copying the Rust SDK's `1.95` selection is not
enough: this Python package currently declares a minimum Rust version of
`1.97`. Its binding and dependencies still need a compatible, tested public
compiler.

**Decision needed:** the SDK team and Central must decide whether to provide
a supported build procedure using publicly available Rust tools. If so, they
must choose the compiler version and explain how contributors select it
without changing the pipeline's compiler.

**Proof needed:** build the extension and run the relevant tests on a clean
machine without internal feed access. Record the working commands in
`docs\local_development.md` and decide how CI will check that the procedure
continues to work.

This concerns contributing to the SDK, not installing a compatible prebuilt
wheel. Supporting installation from a published source archive is a separate
question in
[section 16](#the-internal-compiler-choice-is-a-release-decision-not-a-customer-prerequisite).

### Platforms without a wheel

The configured targets and compatibility limits are defined in
[section 10](#10-why-one-release-needs-several-wheels).
[Section 15](#which-customers-have-no-compatible-wheel) explains the
customer impact when no wheel matches.

`_validate_native_wheel` in `azure_cosmos_package_builder.py` requires every
wheel to contain the compiled Rust extension and rejects an `any` platform
wheel. The current path therefore does not produce a Python-only fallback.

Before general availability, the SDK team and Central must decide how to
handle platforms outside the configured targets:

| Option | What it means | Cost |
|---|---|---|
| Publish a pure-Python fallback wheel | Also publish a `py3-none-any` wheel of the same version. pip prefers a platform wheel where one matches, and uses the fallback elsewhere. The default `core-python` backend works there, while the Rust backend is unavailable | Reverses the "every wheel contains Rust" rule (section 4) and `_validate_native_wheel` in the package builder. Central must build and publish the extra wheel |
| Build more targets | Add Intel Mac, musllinux, and an older glibc baseline such as `manylinux2014` | Each needs the Microsoft Rust installer in that build environment, plus Central build machines and time |
| Explicitly exclude a platform | State that this release does not support installation on that platform | Review the customer impact and publish the support boundary |

Until that decision and the required validation are complete, these five
targets remain the configured prototype scope, not a proven release matrix.

### The pinned pyo3 version has a security advisory

Alpha Bank needs to assess the dependencies included in our SDK, not just
our own code. **PyO3** is the library our binding uses to exchange values
between Rust and Python. It becomes part of the compiled extension.
The package's `Cargo.lock` selects PyO3 **0.22.6**.

A **security advisory** is a published report of a known security defect.
[RUSTSEC-2025-0020](https://rustsec.org/advisories/RUSTSEC-2025-0020.html)
identifies a defect in PyO3's `PyString::from_object` and
`PyString::from_object_bound` string-conversion functions. They pass text
to Python without ensuring that it has the end marker Python expects.
Python can then read beyond that text and potentially include unrelated
memory contents in an exception message. PyO3 **0.24.1** fixes this defect.

**What we know about our use:** a search of our binding source found no
direct calls to either affected function. That is not a complete check of
calls through dependencies, and it does not prove that the defect is
unreachable. We have confirmed an affected dependency version, not
demonstrated an exploit through a customer operation.

For example, Alpha Bank's security team may flag the affected version during
its dependency review. We should not dismiss that concern merely because
the SDK builds or its ordinary operation tests pass.

**Planned work, deferred to a separate change:** upgrade to **PyO3 0.30.1**
with **`pyo3-async-runtimes` 0.30.0**. The second library connects Rust
asynchronous work to Python's asynchronous waits. Its declared PyO3
dependency accepts the 0.30 series; the two libraries do not need identical
patch-version numbers.

These targets were checked on November 19, 2026 against the
[PyO3 release](https://github.com/PyO3/pyo3/releases/tag/v0.30.1) and
[async-runtime dependency declaration](https://docs.rs/crate/pyo3-async-runtimes/0.30.0).
They are the planned upgrade versions, not versions already installed by
this documentation change. Recheck advisories and compatibility when doing
the upgrade.

This is not just changing two version numbers. PyO3 has changed APIs since
0.22; our binding must be adapted using its
[migration guide](https://pyo3.rs/v0.30.1/migration).
The SDK team owns this work before general availability. Completion requires:

- Update the dependency declarations and lockfile, adapt the binding, and
  confirm the affected PyO3 version is no longer selected.
- Rebuild the extension and run the native and Python tests, including
  synchronous/asynchronous operations, credential callbacks, cancellation,
  and preservation of Python exceptions.
- Build and validate the five configured wheel targets, including their
  Python compatibility and Windows ARM64 build configuration.

The upgrade remains open until those checks pass. Selecting a fixed version
addresses this advisory; it is not proof that every dependency is free of
security defects.

<a id="the-wheel-has-no-third-party-license-notices"></a>

### Confirm that required third-party license notices ship with the wheel

Alpha Bank receives our compiled extension, which includes code from other
projects. Those dependencies have their own licenses. Alpha Bank's compliance
team may ask where to find the copyright notices and license terms for that
code, not just the SDK's own MIT license.

Two different kinds of information matter here:

| Material | What it tells Alpha Bank |
|---|---|
| Software bill of materials, or SBOM | Which software components and versions are included |
| License notices | The applicable copyright notices and license terms |

A dependency list or license name alone does not establish that the required
notices accompany the package.

**Current evidence:** the Python package configuration declares our MIT
license. The inspected package builder and configuration have no explicit
third-party-notice handling. The local wheel available during this review
was an empty archive, not usable release evidence. We therefore still need
to inspect a freshly built release wheel; this review does not establish
its final license-file contents.

**What we can learn from the Rust SDK:** its inspected packaging code has
related tooling, but we have not confirmed a complete license-notice solution:

- `eng\scripts\Pack-Crates.ps1` produces Rust source packages, a different
  output from our compiled Python wheels.
- Its internal packaging pipeline invokes
  `eng\scripts\Generate-CargoSbom.ps1` to generate dependency information.
- The native driver's `pipeline\Invoke-LocalSupplyChain.ps1`, under
  `sdk\cosmos\azure_data_cosmos_driver_native`, generates and validates an
  SBOM for compiled artifacts.

These steps establish dependency-inventory tooling, not proof that full
required notices reach customers. No explicit consolidated notice-generation
step was found in the inspected paths. Confirm the Rust team's release
process and actual artifacts before deciding which tooling we can reuse.

**Follow-up, deferred for now:** the SDK team should work with the Rust
release owners and Microsoft's legal/compliance team to identify the notices
needed for the dependencies actually shipped. Then arrange their inclusion
in the Python wheels and check the final artifacts for every configured
target. Keep this release-readiness item open until that review and the
packaging checks are complete.

### Central changes still required

Central owns the shared implementation under `eng/`, including compiler
installation, wheel provisioning, signing, and publication. Reusing an
existing hook does not require changing those shared templates.
The wheels-only publication fix belongs in Central's shared publishers;
our Cosmos configuration already requests it. See
[the file ownership and required publication check](#use-and-validate-the-actual-source-archive-creation-path)
in section 16. Central also needs to agree on the
contributor toolchain question in
[A supported build procedure for external contributors](#a-supported-build-procedure-for-external-contributors).

**Central must pass the source commit into the Linux build container.**
For the forwarding behavior and its effect on commit labels, see
[section 12](#which-settings-reach-the-linux-build-container).
Central must add `BUILD_SOURCEVERSION` to the forwarding list in
`eng\pipelines\templates\steps\build-package-artifacts.yml`.
No Python wrapper or Rust driver change is needed.

Our Cosmos team must then install each final Linux wheel and compare
`_rust.__python_commit__` with the source commit recorded by the build that
produced it. An absent value, `unknown`, or a different commit must fail the
release check. Keep this item open until the final-wheel results exist.

**Open follow-up with Central: limit access to the Rust installer token.**
The current exposure is explained in
[section 12](#the-pipelines-login-stays-visible-for-the-whole-build).

Central owns the shared pipeline change. The goal is to supply the credential
only to the installation work that needs it, not to subsequent compilation.
Central should also check whether its permissions can be restricted to reading
the required feed. Reducing permissions limits what the token can do;
limiting its availability reduces which programs can use it. These are
separate protections, not interchangeable fixes.

To close this item, Central must demonstrate that installation still succeeds
and subsequent compilation and dependency build scripts cannot read
`MSRUSTUP_ACCESS_TOKEN`. Check for its presence without printing its value.
Record the approved permissions separately. The inspected files establish
where the credential is supplied, not its actual permissions or evidence of
theft. No customer app, Python wrapper, or Rust driver change is needed.

**Release-wheel validation remains open until the required results exist.**
The release record must identify the final wheel files and show results for
each required platform/Python combination. Source-level tests and pipeline
configuration alone do not establish that those wheels install and run.

The package keeps technical terms in `sdk/cosmos/azure-cosmos/cspell.json`,
without changing the root dictionary. The SDK templates use file-local
spelling annotations where needed, since the package dictionary does not
cover files outside the package.

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
13. [What Customer Bank installs](#13-what-contoso-bank-installs)
14. [What changes if we also publish a source distribution](#14-what-changes-if-we-also-publish-a-source-distribution)
15. [What still needs to be decided or proved before release](#15-what-still-needs-to-be-decided-or-proved-before-release)

## 1. Start with the complete build-to-install flow

The SDK team and the customer have different jobs.

**The SDK team prepares and tests the package. Customer installs that
package and uses it in its application.** We want the normal customer
installation to remain straightforward even though the SDK now contains Rust.

The SDK team first **builds a wheel**: it turns source code and packaging
instructions into a `.whl` archive prepared for installation.

The team then installs that wheel into a test Python environment so its files
can be used there. If the required checks and approvals pass, the release
process **publishes** the wheel, making it available through a package service.

Customer can then use **pip**, Python's installation tool, to select and
install the package. Pip normally obtains public packages from **PyPI**, the
Python Package Index, unless another source is configured.


### What changes when we add Rust?

The existing pure-Python SDK wheel packages Python files and supporting data.
The Rust-backed wheel also needs a **compiled extension**: a file containing
machine code that Python can load.

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

Customer
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
Python SDK
    -> calls the Python-facing Rust binding
    -> the binding calls the Cosmos Rust driver
```

A **Rust crate** is a Rust project containing source and build information.
**Cargo** is Rust's build tool; it understands those projects and builds them.

| Component | Where its source is maintained | Its job |
|---|---|---|
| Python SDK | Python repository: `sdk\cosmos\azure-cosmos\azure\cosmos` | Provides the Python SDK code |
| Binding crate, `azure_cosmos_rust` | Python repository: `sdk\cosmos\azure-cosmos\azure_cosmos_rust` | Makes Rust operations callable from Python |
| Driver crate, `azure_data_cosmos_driver` | Rust repository: `sdk\cosmos\azure_data_cosmos_driver` | Implements the Cosmos operations used by the binding |

The **package source directory** in this guide means:

```text
azure-sdk-for-python\sdk\cosmos\azure-cosmos
```

Inside it, the important layout is:

```text
azure\cosmos\                    Python SDK files
azure_cosmos_rust\
    Cargo.toml                  binding configuration
    src\                        binding Rust source
    build.rs                    checks performed during the Rust build
    query_plan_binary.rs        supporting compiled-file checks
Cargo.toml                      shared Rust configuration
Cargo.lock                      selected Rust dependency versions
rust-toolchain.toml             selected Rust build tools
pyproject.toml                  Python package and build settings
setup.py                        existing Python packaging instructions
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
selected driver is version `0.8.0`; the exact revision is recorded in the
package-level `Cargo.toml` and `Cargo.lock`.


For the final release, our plan calls for an approved driver version published
on **crates.io**, the public registry from which Cargo downloads Rust source
packages. For a generally available release, the selected driver must also be
generally available rather than a preview.

Cargo downloads driver source and compiles it with the binding. A customer
installing our wheel does not separately install a Rust driver package.

## 3. Which work belongs to the SDK team and which belongs to Central

**A pipeline** is an automated sequence of work, such as building and testing
a package. The SDK owns the Cosmos entry file, `sdk\cosmos\ci.yml`, but that
file delegates most work to Central's shared pipeline files.

### The SDK-owned files

The following paths are relative to the package source directory:

| File or area | What the SDK team controls there |
|---|---|
| `azure\cosmos`, `azure_cosmos_rust\src` | Python and binding implementation |
| `setup.py`, `MANIFEST.in` | Existing packaging instructions and source-file inclusion rules |
| `pyproject.toml` | Package information, selected build tools, and requested platform builds |
| Both `Cargo.toml` files and `Cargo.lock` | Rust dependencies and the selections used by builds |
| `rust-toolchain.toml`, `scripts\*.sh` | Selected Rust tools and the prototype's setup scripts |
| `azure_cosmos_build_backend.py` | SDK-specific preparation around the wheel build |
| `azure_cosmos_rust\build.rs`, `query_plan_binary.rs` | Checks on supplied compiled libraries |
| `tests` | Packaging checks and tests of installed SDK behavior |


### The Central-owned files

Central maintains the shared files under `eng\pipelines\templates` and the
build tools under `eng\tools\azure-sdk-tools`. Shared engineering also maintains
`eng\common`.

For example, the SDK can declare:

> "We need a Windows ARM64 wheel."

Central must arrange the environment that can build it and the environment
that can execute its required tests. A setting in a package file does not
create either environment.


Ownership also does not override source-branch selection. A run using a
particular branch uses that branch's same-repository SDK files and shared
templates. Required Central-owned changes must therefore be available in the
source used by the run, not merely present in someone else's branch.

## 4. Why both setup.py and pyproject.toml exist

**Both files existed before the Rust integration, but they had different jobs.
With Rust, we are expanding what `pyproject.toml` controls, not introducing it
for the first time.**

We also need to continue supporting the existing pure-Python production builds.
The new Rust build path must therefore coexist with the existing packaging
path without breaking it.

### Before Rust: setup.py controlled packaging

The SDK team needed to collect the Python SDK files and prepare the wheel and
source archive that customers could install.

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

`setup.py` is Python code used during packaging. It is not code that Customer
 calls when its application uses the installed SDK.

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

The second section was for **Conda**. This setting concerns the separate Conda distribution process, not how we
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


### What the SDK-owned build helper does

Our `[build-system]` section selects:

```toml
build-backend = "azure_cosmos_build_backend"
```

A **build backend** is the component a Python build tool calls to create the
package. Here, that component is our SDK-owned Python file:

```text
azure_cosmos_build_backend.py
```

The setting means:

> "When asked to build this package, call our helper file. That helper will
> perform our package-specific preparation and then ask Maturin to build
> the wheel."

The helper exists because we have an additional preparation step for
**QueryPlanInterop**, a separate compiled library that can create database
query plans. Its detailed purpose and delivery are covered in
[section 11](#11-how-queryplaninterop-reaches-the-wheel-and-the-running-sdk).

For a wheel build, the helper's added work is:

```text
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
does not run anything by itself. Central arranges **build jobs**, units of
automated work scheduled on build machines, and invokes the tool in suitable
environments.

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

We still need the existing pure-Python production builds, so **we must preserve
their `setup.py`-based packaging path**. It is not merely an unused file waiting
to be deleted.

At the same time, the new Rust wheel path does not run `setup.py` as a
prerequisite.

| File | Existing pure-Python production path | New Rust-backed path |
|---|---|---|
| `setup.py` | Supplies the existing setuptools packaging instructions | Not part of the Maturin wheel-build chain |
| `pyproject.toml` | Holds repository-tool settings in the pre-Rust configuration | Also supplies package information and selects/configures the Rust build tools |

Keeping both files is not enough by itself. The build commands and pipeline
routing must select the intended path, and overlapping package information
must not contradict itself. 

**The goal is to add the Rust-backed build process while preserving the
production build process we still support, not to assume that adding Rust
means deleting `setup.py`.**

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

Cargo manages the Rust build and its **dependencies**, the other libraries
our code needs. It obtains those dependencies and invokes **`rustc`**, the
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

`resolver = "2"` selects Cargo's dependency-feature resolution rules. It is
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

**Tokio** is a Rust library used by the binding to run asynchronous work,
including work that waits for network responses.

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
The normal dependency enables native query planning and fault-injection
capabilities; tests add the in-memory emulator capability. Changing the driver
must preserve the features the SDK and tests need.

The binding and driver also exchange values defined by the `azure_core` Rust
library. Their dependency selections must allow them to use the same crate's
types, rather than incompatible copies. A matching name alone does not make
types from different crate instances interchangeable.

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

A **Rust toolchain** includes Cargo, `rustc`, and the Rust standard library.
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

These are SDK build concerns. Customer does not need the tools when
installing a compatible prebuilt wheel. Customer source installation, if
supported, needs its own accessible toolchain path; it cannot assume access
to our internal Microsoft toolchain.

## 6. How Cargo builds the Rust extension

The configuration now identifies the source, dependencies, and compiler.
The next question is:

> "How do the binding and driver become a file that Python can import?"

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

We do not ask Customer to install a separate compiled driver alongside it.
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
Do not use the wheel-staging source setting as a substitute for the runtime
setting.

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
The temporary environment creates the wheel; it is not Customer's
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
build path when checking the wheel workflow, including its optional staging.

The helper also delegates source-archive, editable-build, and package-information
requests to Maturin. Its extra QueryPlanInterop staging is specific to the
wheel-building path.

### Inspect the archive, then install that exact file

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
source directory or `PYTHONPATH` for this check. Otherwise, a test might import
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

**Metadata** means information describing the package, rather than its
implementation. The `.dist-info` directory provides that information:

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
companions, package information, and unwanted duplicate or bytecode files.

The next question is why we need several such archives for the same release.

## 10. Why one release needs several wheels

Suppose Customer develops on Windows x64 but runs its application on
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

| Part | Meaning |
|---|---|
| `azure_cosmos` | The distribution name corresponding to `azure-cosmos` |
| `<version>` | The release version |
| `cp310` | A CPython 3.10 compatibility baseline for this stable-ABI wheel |
| `abi3` | The extension uses CPython's stable binary interface |
| `win_amd64` | Windows x64 |

### Why we do not necessarily build a wheel for every Python version

Compiled code needs an agreed interface for communicating with Python.
An **application binary interface**, or **ABI**, defines those low-level
calling rules.

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

On Linux, **glibc** is a common system runtime library. The `manylinux_2_28`
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

Suppose Customer runs a query across data stored in multiple Cosmos
partitions. A **query plan** describes which partitions to contact and how
to process the combined results.

Creating that plan is different from executing the query and returning its
results. The driver can obtain a plan from more than one place.

### There are three query-planning providers

A **provider** here means one implementation capable of supplying a query plan.

| Provider | Where it runs | What the installed package needs |
|---|---|---|
| QueryPlanInterop | Separate compiled library loaded on the application's machine | A matching library and its dependencies |
| Pure-Rust planner | Code compiled into the Rust driver inside `_rust` | No separate QueryPlanInterop library |
| Gateway planner | Cosmos DB service | A request to the service for a plan |

The default `LocalPreferred` mode means the driver normally tries an enabled
QueryPlanInterop provider, then the pure-Rust planner, then the Gateway.
The pure-Rust planner handles eligible query shapes, not every query.

`GatewayOnly` explicitly bypasses both local providers. Some contradictory
filters can also be recognized as producing no results without first looking
up the container's partition layout; not every query needs to pass through
all providers.

**No QueryPlanInterop library does not mean every query must use Gateway
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

The current plan is to include QueryPlanInterop in later wheels. **Provisioning
these libraries is deferred and is not an immediate prototype-wheel blocker.**
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
source setting into Linux build containers. A container is an isolated
environment used to run the build with its own tools and filesystem view.
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

**Runtime** means when Customer's application is using the installed SDK,
rather than when the SDK team is building it.

The runtime setting is different:

```text
AZURE_COSMOS_QUERYPLANINTEROP_DIR
```

It means:

> "Look in this directory when the driver needs to load QueryPlanInterop."

The Python helper in `azure\cosmos\_backend\_shared.py` finds `.libs` beside
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
The driver then executes the query; the DLL does not return the database's
query results.

The driver does not download or compile QueryPlanInterop automatically.

### Prove which planner ran

A successful query is not enough evidence for the QueryPlanInterop feature.
The Rust planner or Gateway may have supplied the plan instead.

The driver's diagnostic labels distinguish them:

| Label | Provider |
|---|---|
| `native_ffi` | QueryPlanInterop |
| `local_rust` | Pure-Rust planner |
| `gateway` | Gateway planner |

Installed-wheel tests need an observable signal for the actual provider,
not merely an import check or a file-presence check. The label alone is not
proof of success: `native_ffi` also appears in logs reporting an unavailable
library or failed planning attempt. Check the message and outcome, such as
`using native FFI query plan`, rather than treating a fallback message as
successful QueryPlanInterop use.

For missing-library tests, start a fresh process with the runtime setting
pointing to an empty directory before importing the SDK, and ensure no other
copy is discoverable. This does not turn off the pure-Rust planner.
Use `GatewayOnly` for an explicitly Gateway-only test.

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

A **pipeline template** is a reusable file of pipeline instructions.
The Cosmos entry file uses shared templates instead of copying the entire
build process into its own file.

The current chain is:

```text
sdk\cosmos\ci.yml
    -> eng\pipelines\templates\stages\cosmos-sdk-client.yml
    -> eng\pipelines\templates\stages\archetype-sdk-client.yml
    -> shared build jobs and conditional release processing
```

The Cosmos template already sets:

```yaml
InstallMsRustToolchain: true
```

That is a request for the downstream setup steps to install the selected Rust
toolchain. The template also supplies the package working directory and the
additional Rust target needed for Windows ARM64.

The flags must reach the step that performs installation. Merely declaring a
setting at the top of a pipeline would not help if downstream templates
ignored it.

### Which shared files do the work?

A **stage** groups a broad part of the pipeline, such as its build jobs.
A **step** is an operation inside a job, such as installing the compiler or
generating packages.

Paths in this table are relative to the Python repository root:

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

### How three build-machine types serve five targets

The configured machine roles are:

| Build machine | Wheel work |
|---|---|
| Windows x64 | Build Windows x64; cross-compile Windows ARM64 |
| Linux x64 | Build Linux x64; use QEMU emulation for Linux ARM64 |
| macOS ARM64 | Build macOS ARM64 directly |

**Cross-compilation** means producing code for a different processor from the
one running the compiler. Windows ARM64 uses this arrangement on an x64 build
machine.

The configuration supplies `CARGO_BUILD_TARGET` for the ARM64 Rust target and
`PYO3_CROSS_LIB_DIR` for the pipeline's ARM64 Python-library location.
PyO3's `generate-import-lib` feature supports this build arrangement.

**Emulation** lets a machine run software intended for another processor.
QEMU is the emulation software used by the Linux ARM64 path.

Neither setup excuses missing tests. Producing an ARM64 file on x64 does not
prove the ARM64 file executes correctly. Central must establish execution-test
coverage for each supported target.

Linux wheel builds run inside the prepared containers introduced in section
11. The compiler setup, required credentials, and input files must be available
where the build actually runs, not just on the host.

### Build access and time limits are part of the environment

The build needs access to compiler and dependency sources. A **feed** is a
service from which tools download packages or other build inputs.
Authentication for internal feeds belongs in pipeline infrastructure.
Credentials must not be committed into the SDK's package files.

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

Those saved outputs are **artifacts**. In continuous integration, or **CI**,
they let the team inspect what the automated build produced.
They are not automatically customer-visible releases.

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
files. **Digital signing** attaches verifiable publisher and integrity
information to a file.

If signing changes files inside a wheel, the release process must:

```text
unpack the wheel
    -> sign the files required by the approved policy
    -> repack it with correct packaged-file records
    -> install and test that final wheel
```

Testing an earlier unsigned wheel does not prove the repacked wheel works.
Signing infrastructure and credentials remain Central-owned.

Only after the required outputs, final-wheel tests, and approvals are complete
should publication proceed. These are requirements for the finished release
route, not a claim that the prototype has completed them.

## 13. What Customer installs

The purpose of all that SDK-team work is to avoid making every customer repeat
the compilation process.

For a published Rust-backed release, a Customer developer normally uses:

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

If Customer later deploys the application to supported Linux ARM64, that
environment needs the Linux ARM64 wheel for the same SDK version.
These are different files belonging to one release.

### Installing a wheel does not compile our Rust source

The SDK team has already done the compilation:

```text
SDK team
    -> builds the extension
    -> places it in the platform wheel
    -> publishes the approved wheel

Customer
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

That depends on whether we publish a source distribution for the selected
release version.

If a source archive is available, pip may attempt to build a wheel on the
customer's machine. If that version has only wheels and none is compatible,
there is no source-build fallback for it.

That is why the source-distribution choice is not merely a question of whether
we upload one extra file. It determines whether we offer a different customer
installation path.

## 14. What changes if we also publish a source distribution

A **source distribution**, usually shortened to **sdist**, is an archive
containing source files and build instructions. For this package, its filename
has the shape:

```text
azure_cosmos-<version>.tar.gz
```

Unlike a platform wheel, it does not provide the already-built Rust extension
for the customer's machine.

### Sdist tracking note: customer source installation

**Status: open release decision, not an immediate wheel-generation blocker.**

The team must decide whether the Rust-backed release offers:

1. Prebuilt wheels only.
2. Prebuilt wheels plus a supported source-installation path.

For the existing pure-Python package, source installation primarily packages
Python files. For the Rust-backed package, it must also compile the extension.
That changes the tools and access the customer's machine needs.

Suppose Customer requests a version for which pip selects the sdist:

```text
pip downloads the source archive
    -> prepares a Python build environment
    -> installs the declared Python build dependencies
    -> calls our helper and Maturin
    -> Cargo and rustc build the extension for Customer's machine
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
| README, license, and other files referenced by packaging | Required package descriptions and supporting information |

The driver source need not be copied into the archive if Cargo can obtain the
approved source through the declared dependency. No active dependency may
require an unrelated local directory outside the archive.

Likewise, one target's QueryPlanInterop binary must not be included as if it
worked on every target. If the source-installation promise includes that
provider, define how the customer obtains matching files.

### Use and validate the actual source-archive creation path

The configured custom backend delegates sdist creation to Maturin.
`pyproject.toml` explicitly includes the backend, toolchain file, and setup
scripts in that archive.

The shared `create_package` function in
`eng\tools\azure-sdk-tools\ci_tools\build.py` can already request this archive
when `enable_sdist` is true. **Generating an sdist as a build output does not
decide whether we publish it or promise customers that source installation
works.** Release configuration must enforce that separate decision.

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

To close the tracking item, the release approver must choose the policy, the
SDK team must document supported source-build targets and prerequisites in
the README, and Central must run the appropriate clean-archive validation.

If the decision is wheels only, publication must exclude sdists and include
a compatible wheel for every supported target. An accidentally uploaded,
untested sdist would expose a customer build path we did not intend to support.

## 15. What still needs to be decided or proved before release

The preceding sections explain how the build is configured and what a complete
release should do. They do not establish that every target, test, or approval
is complete.

A **release approver** is the authorized person or group deciding whether the
version, support policy, and final outputs are ready to publish. That owner
must be identified.

### Keep the remaining decisions in one place

| Area | What must be decided or proved | Owner |
|---|---|---|
| Existing production builds | Preserve the required setuptools packaging route while introducing the Rust route; test the intended routing rather than relying on file presence | Cosmos SDK team and Central team |
| Release identity | Select the release version and keep Python metadata and `_version.py` consistent; the prototype's `4.17.1` is not a v5 release approval | Cosmos SDK team and release approver |
| Rust driver | Select the approved published driver for release, preserve required features, and review the synchronized lock | Cosmos SDK team and Rust driver team |
| Compiler policy | Approve the release toolchain and validate or correct the declared compiler minimum | Cosmos SDK team and Central team |
| Support policy | Approve Python versions, platform coverage, Linux baseline, and Windows/macOS minimums | Release approver, using SDK and Central evidence |
| Multi-target builds | Build the intended source and inspect every required wheel; establish execution-test coverage including ARM64 | Central team and Cosmos SDK team |
| QueryPlanInterop | Complete the [deferred library delivery and provider checks](#deferred-work-and-completion-criteria) | Producing team, Cosmos SDK team, and Central team |
| Source installation | Resolve and validate the [sdist policy](#sdist-tracking-note-customer-source-installation) | Release approver, Cosmos SDK team, and Central team |
| Dependency maintenance | Confirm update automation covers both Cargo manifests and the lock | Repository maintainers and Cosmos SDK team |
| Signing and publication | Apply approved signing, test final repacked wheels, and publish the complete set under one version | Central team and release approver |

### Define what each test actually proves

The **test matrix** is the set of Python versions and target environments
that must be tested. Building one stable-ABI wheel reduces the number of
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
| Other planning paths | Eligible queries use `local_rust` without QueryPlanInterop; Gateway fallback and `GatewayOnly` behave as required |
| Final release processing | The final signed/repacked files retain correct contents, installation behavior, and SDK functionality |
| Complete output set | All approved wheels and any approved sdist belong to the same release version |

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

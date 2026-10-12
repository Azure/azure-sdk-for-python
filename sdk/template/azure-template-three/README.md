# Azure Rust Template Package client library for Python

**This package is an engineering-system test fixture, not a service SDK.**

`azure-template-three` complements the pure-Python `azure-template` and the
setuptools/C-extension `azure-template-two`. It builds one PyO3 function with
Maturin, without setuptools `ext_modules`, to exercise the Rust native-wheel
path.

```python
from azure.template.three import _rust

assert _rust.is_true() is True
```

## Run template CI

Queue the template CI pipeline for the desired branch. Every run builds all
three fixtures and installs the Microsoft Rust toolchain for
`azure-template-three`. The Rust fixture follows the normal signing and release
workflow. `ReleaseToDevOpsOnly` can direct the release to the existing staging
feed instead of PyPI.

Template CI validates this fixture. Generic PR validation excludes it because
that pipeline does not enable its Rust toolchain setup. Shared PR
discovery and dependency validation otherwise remain unchanged.
The separate template live-test pipeline continues to target the Python and C
fixtures because its source-installing jobs do not provision Microsoft Rust.

The feed and tool versions use:

- Toolchain: `ms-prod-1.97`, selected by `rust-toolchain.toml`.
- Toolchain feed: `https://pkgs.dev.azure.com/azure-sdk/_packaging/azure-sdk-for-rust-org-test/nuget/v3/index.json`.
- Build backend: Maturin `1.15.0`.
- Binding: PyO3 `0.22`, with the Python 3.10 stable ABI.

The wheel matrix covers Linux x86_64/aarch64, macOS arm64, and Windows
AMD64/ARM64. Linux containers bootstrap their own Microsoft Rust toolchain
and configure the authenticated Cargo mirror. Windows ARM64 cross-compilation
uses the ARM64 Python import libraries provisioned by the shared build job.
Installed-wheel tests call the Rust function and verify that the module is
native. Windows ARM64 import testing still requires an ARM64 runner; producing
a cross-compiled wheel on an x64 agent does not prove that it loads.

Toolchain/feed credentials are supplied by the pipeline, never checked in.
Use a trusted Azure DevOps run with access to the prototype feed. Local checks
cannot establish that the internal toolchain or authenticated downloads work.
PR runs do not sign binaries. Internal manual runs can exercise the existing
signing and release stages.

## Build locally

With Microsoft Rust installed and authenticated:

```bash
python -m build sdk/template/azure-template-three
python -m pip install sdk/template/azure-template-three/dist/*.whl
python -m pytest sdk/template/azure-template-three/tests
```

For a local compile/import check using public Rust instead of Microsoft Rust:

```bash
RUSTUP_TOOLCHAIN=stable python -m build sdk/template/azure-template-three
```

This does not exercise the CI toolchain feed, manylinux bootstrap, or credentials.

## Validation boundaries

Ordinary source-installing analysis, documentation, and test jobs remain
disabled, as in the C fixture.

Windows ARM64 wheels are cross-built and signed, but their runtime import still
needs a Windows ARM64 runner. Linux aarch64 build tests use the existing QEMU
setup.

# Contributing

If you encounter any bugs or have suggestions, please file an issue in the [Issues](<https://github.com/Azure/azure-sdk-for-python/issues>) section of the project.

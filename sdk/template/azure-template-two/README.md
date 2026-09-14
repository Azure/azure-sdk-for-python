# Binary template package for the Azure SDK for Python

**This package is a test fixture for the Azure SDK engineering system and is not intended for direct use.**

`azure-template-two` is the binary counterpart to `azure-template`. It ships a minimal C extension so that the build and release pipelines have a package that produces both platform specific wheels and an sdist. Use it to exercise `cibuildwheel`, binary signing, and publishing without depending on a real service library.

The extension exposes a single function that takes no arguments and always returns `True`:

```python
from azure.template.two import istrue

istrue.is_true()  # True
```

## Installation

```bash
pip install azure-template-two
```

### Prerequisites
* Python 3.10 or later is required to use this package. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/python_version_support_policy.md).

## Building locally

Wheels are produced with [cibuildwheel](https://cibuildwheel.pypa.io/), configured in `pyproject.toml` to build CPython 3.10 for x86_64 Linux, x86_64 Windows, and arm64 macOS. Because the extension compiles against the CPython limited API, each wheel is tagged `abi3` and remains importable on later interpreters.

To build and test for the current platform only:

```bash
pip install cibuildwheel
cibuildwheel --only cp310-macosx_arm64 sdk/template/azure-template-two
```

A plain in-place build is also enough for local development:

```bash
pip install -e sdk/template/azure-template-two
pytest sdk/template/azure-template-two/tests
```

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

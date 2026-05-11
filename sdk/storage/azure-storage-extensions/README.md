# Extension package for Azure Storage Python libraries

**This package provides optional native extensions for Azure Storage Python SDK libraries and is not intended for direct use.**

This package contains native extension modules that provide performance-critical functionality for Azure Storage Python SDK libraries. It is designed exclusively for use with Azure Storage SDKs and must be explicitly installed to enable enhanced performance features.

## Important Notes

⚠️ **Not for standalone use**: This package is designed exclusively as an optional dependency for Azure Storage Python SDK libraries. The API surface is subject to change without following semantic versioning conventions—breaking changes may occur between minor versions.

⚠️ **Implementation may change**: While this package currently uses C extensions, future versions may migrate to Rust extensions or other native implementations, which would require different build toolchains.

## Installation

**Recommended**: Install this package via extras when installing Azure Storage libraries:

```bash
pip install azure-storage-blob[extensions]
```

This ensures you get compatible versions of both the SDK and the extensions package.

You can also install it directly if needed:

```bash
pip install azure-storage-extensions
```

### Prerequisites
* Python 3.9 or later is required to use this package. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/python_version_support_policy.md).

### Troubleshooting Installation Issues

This package contains native extension modules and requires platform-specific compiled binaries. We distribute pre-built wheels for common platforms (Windows, macOS, Linux) on PyPI, which `pip` will automatically install when available.

If a pre-built wheel is not available for your platform, `pip` will attempt to build the extensions from source. This requires:
- A C compiler (e.g., gcc, clang, MSVC)
- Python development headers

**Common installation errors:**

- **"error: Microsoft Visual C++ 14.0 or greater is required"** (Windows): Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- **"error: command 'gcc' failed"** (Linux): Install build essentials: `sudo apt-get install build-essential python3-dev` (Debian/Ubuntu) or equivalent for your distribution
- **"error: command 'clang' failed"** (macOS): Install Xcode Command Line Tools: `xcode-select --install`

If you encounter installation issues, please open an issue in the [Azure SDK for Python repository](https://github.com/Azure/azure-sdk-for-python/issues).

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

# Extension package for Azure Storage Python libraries
This package contains a set of C-Extension modules intended to be used with the other Azure Storage Python SDK libraries.

## Getting started

### Prerequisites
* Python 3.8 or later is required to use this package. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy).

### Install the package
This package is not meant to be used standalone and is meant to accompany other Azure Storage Python SDK libraries. However it can be installed and used standalone as well.

Install the Azure Storage Extensions library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-storage-extensions
```

Please note that this package contains [C-Extension modules](https://docs.python.org/3/extending/extending.html) and therefore you must install the correct wheel for your
particular platform. We distribute many pre-built wheels for a wide variety of platforms on PyPi and `pip` will attempt to install the wheel meant for your platform. If
however, a wheel is not available for your platform, we also distribute the source code on PyPi so `pip` will attempt to build the module at install time, assuming you have
a compiler available. If you encounter any issues installing this package, please feel to open an Issue.

## Extensions
This section contains the list of available extensions and how to use them.

### Storage CRC64
The `crc64` extension provides an implementation of the CRC64 algorithm, including the custom polynomial, that is used by the Azure Storage service. It can be used to compute
the crc64 hash of `bytes` data, including given an initial hash.

```py
from azure.storage.extensions import crc64

data = b'Hello World!'
result = crc64.compute_crc64(data, 0)

# Chain together calculations
data2 = b'Goodbye World!`
result2 = crc64.compute_crc64(data2, result)
```

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

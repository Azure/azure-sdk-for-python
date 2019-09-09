# Microsoft Azure SDK for Python

This is the Microsoft Azure Key Vault namespace package. It isn't intended to
be installed directly. Key Vault client libraries are located elsewhere:
- [`azure-keyvault-certificates`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates)
- [`azure-keyvault-keys`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys)
- [`azure-keyvault-secrets`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets)

This is a Python 2 package only. Python 3.x libraries will use
[`PEP420`](https://www.python.org/dev/peps/pep-0420/) as namespace package
strategy. To avoid issues with package servers that don't support
`python_requires`, a Python 3 package is installed but is empty.

This package provides the necessary files for other packages to extend the
`azure` namespace.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fkeyvault%2Fazure-keyvault-nspkg%2FFREADME.png)

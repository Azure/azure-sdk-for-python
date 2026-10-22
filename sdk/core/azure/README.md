# Microsoft Azure SDK for Python

This package was the Microsoft Azure bundle.

Starting with v5.0.0, this package is deprecated. Please install the service specific packages prefixed by `azure` needed for your application.

The complete list of available packages can be found at:
https://aka.ms/azsdk/python/all

Here's a non-exhaustive list of common packages:

-  [azure-mgmt-compute](https://pypi.python.org/pypi/azure-mgmt-compute) : Management of Virtual Machines, etc.
-  [azure-mgmt-storage](https://pypi.python.org/pypi/azure-mgmt-storage) : Management of storage accounts.
-  [azure-mgmt-resource](https://pypi.python.org/pypi/azure-mgmt-resource) : Generic package about Azure Resource Management (ARM)
-  [azure-keyvault-secrets](https://pypi.python.org/pypi/azure-keyvault-secrets) : Access to secrets in Key Vault
-  [azure-storage-blob](https://pypi.python.org/pypi/azure-storage-blob) : Access to blobs in storage accounts

A more comprehensive discussion of the rationale for this decision can be found in the following issue:
https://github.com/Azure/azure-sdk-for-python/issues/10646



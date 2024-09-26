# Microsoft Azure SDK for Python

This is the Microsoft Azure Postgresqlflexibleservers Management Client Library.
This package has been tested with Python 3.8+.
For a more complete view of Azure libraries, see the [azure sdk python release](https://aka.ms/azsdk/python/all).

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started
This library is used to provision an Azure Database for PostgreSQL flexible server instance, multiple servers, or multiple databases on a server.


### Prerequisites

- Python 3.8+ is required to use this package.
- [Azure subscription](https://azure.microsoft.com/free/)

### Install the package
      
```bash
pip install azure-mgmt-postgresqlflexibleservers
pip install azure-identity
```

### Authentication

By default, [Azure Active Directory](https://aka.ms/awps/aad) token authentication depends on correct configure of following environment variables.

- `AZURE_CLIENT_ID` for Azure client ID.
- `AZURE_TENANT_ID` for Azure tenant ID.
- `AZURE_CLIENT_SECRET` for Azure client secret.

In addition, Azure subscription ID can be configured via environment variable `AZURE_SUBSCRIPTION_ID`.

## Examples
```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.postgresqlflexibleservers import PostgreSQLManagementClient
import os

sub_id = os.getenv("AZURE_SUBSCRIPTION_ID")
client = PostgreSQLManagementClient(credential=DefaultAzureCredential(), subscription_id=sub_id)
```
Code samples for this package can be found at:
- [Detailed documentation](https://learn.microsoft.com/azure/postgresql/flexible-server/quickstart-create-server-python-sdk?tabs=PythonSDK)

## Release Notes

### Important Update

**Note:** This library was previously a module under azure-mgmt-rdbms library but has now been separated and is maintained as an independent library. Please update your import statements accordingly.

#### Previous Import Statement
When the library was part of rdbms, you might have imported it like this:
```python
from azure.mgmt.rdbms.postgresql_flexibleservers import PostgreSQLManagementClient
```

#### Current Import Statement
Now with this new version you can import this library like this:
```python
from azure.mgmt.postgresqlflexibleservers import PostgreSQLManagementClient

```

## Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the
[Issues](https://github.com/Azure/azure-sdk-for-python/issues)
section of the project. 

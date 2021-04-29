# Setup Python Development Environment - Advanced
In this document we will provide additional information about the test environments:

- [Test Mixin Classes](#test-mixin-classes)
- [Resource Preparers](#preparers)
- [Examples with Preparers](#examples-with-preparers)
- [mgmt_settings_real.py](#mgmt_settings_real-file)

## Test Mixin Classes
Many of our test suites use a mixin class to reduce re-writing code in multiple test files. For example, in the Tables test suite there is a `_shared` directory containing two of these mixin classes, a [sync one](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/tables/azure-data-tables/tests/_shared/testcase.py) and an [async version](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/tables/azure-data-tables/tests/_shared/asynctestcase.py). These classes will often have ways to create connection strings from an account name and key, formulate the account url, configure logging, or validate service responses. In order for these mixin classes to be used by both the functional and unit tests they should inherit from `object`. For example:

```python

class TablesTestMixin(object):
    def connection_string(self, account, key):
        return "DefaultEndpointsProtocol=https;AccountName=" + account + ";AccountKey=" + str(key) + ";EndpointSuffix=core.windows.net"

    def account_url(self, account, endpoint_type):
        """Return an url of storage account.
        :param str storage_account: Storage account name
        :param str storage_type: The Storage type part of the URL. Should be "table", or "cosmos", etc.
        """
        try:
            if endpoint_type == "table":
                return account.primary_endpoints.table.rstrip("/")
            if endpoint_type == "cosmos":
                return "https://{}.table.cosmos.azure.com".format(account.name)
            else:
                raise ValueError("Unknown storage type {}".format(storage_type))
        except AttributeError: # Didn't find "primary_endpoints"
            if endpoint_type == "table":
                return 'https://{}.{}.core.windows.net'.format(account, endpoint_type)
            if endpoint_type == "cosmos":
                return "https://{}.table.cosmos.azure.com".format(account)

    def enable_logging(self):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        self.logger.handlers = [handler]
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = True
        self.logger.disabled = False
```

In action this class can be used in functional tests:

```python
class TestTablesFunctional(AzureTestCase, TablesTestMixin):
    ...
    def test_with_mixin(self, account, key):
        conn_str = self.connection_string(account, key)
        client = TableClient.from_connection_string(conn_str)
        client.create_table('first')
        client.create_table('second')
        tables = 0
        for table in client.list_tables():
            tables += 1

        assert tables == 2
```

Or can be used in a unit test:
```python
class TestTablesUnit(TablesTestMixin):
    ...
    def test_valid_url(self):
        account = "fake_tables_account"
        credential = "fake_tables_account_key_0123456789"

        url = self.account_url(account, "tables")
        client = TableClient(account_url=url, credential=credential)

        assert client is not None
        assert client.account_url == "https://{}.tables.core.windows.net/".format(account)
```


## Preparers
The Azure SDK team has created some in house tools to help with easier testing. These additional tools are located in the `devtools_testutils` package that was installed with your `dev_requirements.txt`. In this package are the preparers that will be commonly used throughout the repository to test various resources. A preparer is a way to programmatically create fresh resources to run our tests against and then deleting them after running a test suite. These help guarantee standardized behavior by starting each test group from a fresh resource and account.

If this situation is a requirement for your tests, you can opt to create a new preparer for your service from the management plane library for a service. There are already a few preparers built in the [devtools_testutils](https://github.com/Azure/azure-sdk-for-python/tree/master/tools/azure-sdk-tools/devtools_testutils). Most prepares will start with the [`ResourceGroupPreparer`](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/resource_testcase.py#L29-L99) to first create a resource group for your service.

To build your own preparer you will need to use the management plane library to create a service and pass the credentials you need into your tests. The two important methods for a preparer are the `create_resource` and `remove_resource` methods. In the `create_resource` method you will use the management client to create the resource and return a dictionary of key-value pairs. The keys will be matched with the test method parameters and passed in as positional arguments to the test. The `remove_resource` method will clean up and remove the resource to prevent a backlog of unused resources in your subscription. For examples of each of these methods, check out these examples:

| Preparer | `create_resource` | `remove_resource` |
|-|-|-|
| Resource Group | [link](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/resource_testcase.py#L57-L85) | [link](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/resource_testcase.py#L87-L99) |
| Storage Account | [link](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/storage_testcase.py#L53-L102) | [link](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/storage_testcase.py#L104-L107) |
| KeyVault | [link](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/keyvault_preparer.py#L84-L131) | [link](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/keyvault_preparer.py#L133-L138) |


## Examples with Preparers

### Example 2: Basic Preparer Usage with Storage

```python
import os
import pytest

from azure.data.tables import TableServiceClient
from devtools_testutils import (
    AzureTestCase,
    ResourceGroupPreparer,
    StorageAccountPreparer
)

class ExampleStorageTestCase(AzureTestCase):

    @ResourceGroupPreparer()
    @StorageAcountPreparer()
    def test_create_table(self, resource_group, location, storage_account, storage_account_key):
        account_url = self.account_url(storage_account, "table")
        client = self.create_client_from_credential(TableServiceClient, storage_account_key, account_url=account_url)

        valid_table_name = "validtablename"
        table = client.create_table(valid_table_name)

        assert valid_table_name == table.table_name
```

This test uses preparers to create resources, then creates a table, and finally verifies the name is correct.

Notes:
1. This test is aiming to create a new Table, which requires a storage account, which in hand requires a resource group. The first decorator (`@ResourceGroupPreparer()`) creates a new resource group, and passes the parameters of this resource group into the `@StorageAccountPreparer()` which creates the storage account. The parameters from the storage account creation is passed into the signature of `test_create_table` .
2. The `create_client_from_credential` is used again but this time with `storage_account_key` instead of getting a credential from the `self.get_credential` method showed in the previous section. The storage account preparer returns the key for the account which is a valid credential.


### Example 3: Cached Preparer Usage
```python
import os
import pytest

from azure.core.exceptions import ResourceExistsError
from azure.data.tables import TableServiceClient
from devtools_testutils import (
    AzureTestCase,
    CachedResourceGroupPreparer,
    CachedStorageAccountPreparer
)

class ExampleStorageTestCase(AzureTestCase):

    @CachedResourceGroupPreparer(name_prefix="storagetest")
    @CachedStorageAcountPreparer(name_prefix="storagetest")
    def test_create_table(self, resource_group, location, storage_account, storage_account_key):
        account_url = self.account_url(storage_account, "table")
        client = self.create_client_from_credential(TableServiceClient, storage_account_key, account_url=account_url)

        valid_table_name = "validtablename"
        table = client.create_table(valid_table_name)

        assert valid_table_name == table.table_name

    @CachedResourceGroupPreparer(name_prefix="storagetest")
    @CachedStorageAcountPreparer(name_prefix="storagetest")
    def test_create_table_if_exists (self, resource_group, location, storage_account, storage_account_key):
        account_url = self.account_url(storage_account, "table")
        client = self.create_client_from_credential(TableServiceClient, storage_account_key, account_url=account_url)

        valid_table_name = "validtablename"
        with pytest.raises(ResourceExistsError):
            table = client.create_table(valid_table_name)
```

The first test is the same as above, the second test tries to create a table that already exists and asserts that the correct type of error is raised in response. These tests use cached preparers unlike the previous example.

Notes:
1. The cached preparers here will first look to see if an existing resource group or storage account exists with the given parameters, in this case the `name_prefix`. For more information on what parameters differentiate a new resource group or storage account look for the `self.set_cache()` method in the preparer source code [here](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/storage_testcase.py#L49). The advantage to using a cached preparer is the time saver to re-using the same resource instead of creating a new resource for each test. However, this can increase the possibility that you have to be more exact about cleaning up the entities created in between test runs.

## mgmt_settings_real file

A `mgmt_settings_real.py` can be used in place of a `.env` file by copying `sdk/tools/azure-sdk-tools/devtools_testutils/mgmt_settings_fake.py` to `sdk/tools/azure-sdk-tools/devtools_testutils/mgmt_settings_real.py` and providing real credentials to it. The following changes need to be made to the `mgmt_settings_real.py` file:

1. Change the value of the `SUBSCRIPTION_ID` variable to your organizations subscription ID, which can be found in the "Overview" section of the "Subscriptions" blade in the [Azure portal](https://portal.azure.com/).
2. Define `TENANT_ID`, `CLIENT_ID`, and `CLIENT_SECRET`, which are available after creating a Service Principal or can be retrieved from the Azure Portal after creating a Service Principal. Check out the [Azure docs](https://docs.microsoft.com/cli/azure/ad/sp?view=azure-cli-latest#az_ad_sp_create_for_rbac) to create  a Service Principal with a simple one line command to create one. The recommended practice is to include your alias or name in the Service Principal name.
3. Change the [`get_azure_core_credentials(**kwargs):`](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/mgmt_settings_fake.py#L39-L53) function in the `mgmt_settings_real.py` file to construct and return a `ClientSecretCredential` object. Pass in the `CLIENT_ID`, `CLIENT_SECRET`, and `TENANT_ID` values to the `ClientSecretCredential` object. This method should look like this:
```python
def get_azure_core_credentials(**kwargs):
    from azure.identity import ClientSecretCredential
    import os
    return ClientSecretCredential(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        tenant_id = TENANT_ID
    )
```
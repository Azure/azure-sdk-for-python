# Python SDK advanced testing guide
This guide covers advanced testing scenarios for Azure SDK for Python libraries.

## Table of contents

- [Test mixin classes](#test-mixin-classes)

## Test mixin classes
Many of our test suites use a base/mixin class to consolidate shared test logic. Mixin classes can define instance attributes to handle environment variables, make complex assertions, and more. By inheriting from these mixins, test classes can then share this logic throughout multiple files.

For example, in the Tables test suite there is a `_shared` directory containing two of these mixin classes: a [sync version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/tables/azure-data-tables/tests/_shared/testcase.py) and an [async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/tables/azure-data-tables/tests/_shared/asynctestcase.py).

```python
class TableTestCase(object):

    def account_url(self, account, endpoint_type):
        """Return an url of storage account.

        :param str storage_account: Storage account name
        :param str storage_type: The Storage type part of the URL. Should be "table", or "cosmos", etc.
        """
        try:
            if endpoint_type == "table":
                return account.primary_endpoints.table.rstrip("/")
            if endpoint_type == "cosmos":
                cosmos_suffix = os.getenv("TABLES_COSMOS_ENDPOINT_SUFFIX", DEFAULT_COSMOS_ENDPOINT_SUFFIX)
                return f"https://{account.name}.table.{cosmos_suffix}"
        except AttributeError:  # Didn't find "account.primary_endpoints"
            if endpoint_type == "table":
                storage_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX", DEFAULT_STORAGE_ENDPOINT_SUFFIX)
                return f"https://{account}.table.{storage_suffix}"
            if endpoint_type == "cosmos":
                cosmos_suffix = os.getenv("TABLES_COSMOS_ENDPOINT_SUFFIX", DEFAULT_COSMOS_ENDPOINT_SUFFIX)
                return f"https://{account}.table.{cosmos_suffix}"

    ...

    def _assert_delete_retention_policy_equal(self, policy1, policy2):
        """Assert that two deletion retention policies are equal."""
        if policy1 is None or policy2 is None:
            assert policy1 == policy2
            return

        assert policy1.enabled == policy2.enabled
        assert policy1.days == policy2.days

    ...
```

In action this class can be used in functional tests:

```python
class TestTable(AzureRecordedTestCase, TableTestCase):
    @tables_decorator
    @recorded_by_proxy
    def test_create_properties(self, tables_storage_account_name, tables_primary_storage_account_key):
        # # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        table_name = self._get_table_reference()
        # Act
        created = ts.create_table(table_name)
        ...
```

Or can be used in a unit test:
```python
class TestTablesUnit(TableTestCase):
    ...
    def test_valid_url(self):
        account = "fake_tables_account"
        credential = "fake_tables_account_key_0123456789"

        url = self.account_url(account, "tables")
        client = TableClient(account_url=url, credential=credential)

        assert client is not None
        assert client.account_url == f"https://{account}.tables.core.windows.net/"
```

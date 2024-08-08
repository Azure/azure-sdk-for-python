# Python SDK advanced testing guide
This guide covers advanced testing scenarios for Azure SDK for Python libraries.

## Table of contents

- [Mixin classes](#test-mixin-classes)
- [Pre-test setup](#pre-test-setup)
  - [xunit-style setup](#xunit-style-setup)
  - [Fixture setup](#fixture-setup)

## Mixin classes
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

## Pre-test setup
Tests will often use shared resources that make sense to set up before tests execute. There are two recommended
approaches for this kind of setup, with each having benefits and drawbacks.

### xunit-style setup
Pytest has documentation describing this setup style: https://docs.pytest.org/en/latest/how-to/xunit_setup.html. For
example:

```python
from devtools_testutils.azure_recorded_testcase import get_credential

class TestService(AzureRecordedTestCase):
    def setup_method(self, method):
        """This method is called before each test in the class executes."""
        credential = self.get_credential(ServiceClient)  # utility from parent class
        self.client = ServiceClient("...", credential)

    @classmethod
    def setup_class(cls):
        """This method is called only once, before any tests execute."""
        credential = get_credential()  # only module-level and classmethod utilities are available
        cls.client = ServiceClient("...", credential)
```

The primary benefit of using `setup_method` is retaining access to the utilities provided your test class. You could
use `self.get_credential`, for example, to pick up our core utility for selecting a client credential based on your
environment. A drawback is that `setup_method` runs before each test method in the class, so your setup needs to be
idempotent to avoid issues caused by repeated invocations.

Alternatively, the class-level `setup_class` method runs once before all tests, but doesn't give you access to all
instance attributes on the class. You can still set attributes on the test class to reference from tests, and
module-level utilities can be used in place of instance attributes, as shown in the example above.

### Fixture setup
Pytest has documentation explaining how to implement and use fixtures:
https://docs.pytest.org/en/latest/how-to/fixtures.html. For example, in a library's `conftest.py`:

```python
from devtools_testutils.azure_recorded_testcase import get_credential

@pytest.fixture(scope="session")
def setup_teardown_fixture():
    # Note that we can't reference AzureRecordedTestCase.get_credential but can use the module-level function
    client = ServiceClient("...", get_credential())
    client.set_up_resource()
    yield  # <-- Tests run here, and execution resumes after they finish
    client.tear_down_resources()
```

We can then request the fixture from a test class:

```python
@pytest.mark.usefixtures("setup_teardown_fixture")
class TestService(AzureRecordedTestCase):
    ...
```

By requesting a fixture from the test class, the fixture will execute before any tests in the class do. Fixtures are the
preferred solution from pytest's perspective and offer a great deal of modular functionality.

As shown in the example above, the
[`yield`](https://docs.pytest.org/latest/how-to/fixtures.html#yield-fixtures-recommended) command will defer to test
execution -- after tests finish running, the fixture code after `yield` will execute. This enables the use of a fixture
for both setup and teardown.

However, fixtures in this context have similar drawbacks to the `setup_class` method described in
[xunit-style setup](#xunit-style-setup). Since their scope is outside of the test class, test class instance utilities
can't be accessed and class state can't be modified.

By convention, fixtures should be defined in a library's `tests/conftest.py` file. This will provide access to the
fixture across test files, and the fixture can be requested without having to manually import it.

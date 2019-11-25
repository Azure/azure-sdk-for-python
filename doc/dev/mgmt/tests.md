# Table of contents

-   [Overview](#overview)
-   [Getting the tests to run](#running-the-tests)
    -   [Setting up a test environment](#setting-up-a-test-environment)
    -   [Running the tests](#running-the-tests)
    -   [Getting Azure credentials](#getting-azure-credentials)
        -   [Get a token with Azure Active Directory user/password](#get-a-token-with-azure-active-directory-userpassword)
        -   [Get a token with Active Directory application and service principal](#get-a-token-with-active-directory-application-and-service-principal)
    -   [Providing credentials to the tests](#providing-credentials-to-the-tests)
    -   [Running tests in live mode](#running-tests-in-live-mode)
- [Using the Azure Python SDK test framework](#using-the-azure-python-sdk-test-framework)

IMPORTANT NOTE: All the commands in this page assumes you have loaded the [dev_setup](../dev_setup.md) in your currently loaded virtual environment.

# Overview

This page is to help you write tests for Azure Python SDK when these tests require Azure HTTP requests.
The Azure SDK test framework uses the [`azure-devtools`](https://pypi.python.org/pypi/azure-devtools) package,
which in turn rests upon on a HTTP recording system ([vcrpy](https://pypi.python.org/pypi/vcrpy))
that enables tests depending on network interaction
to be run offline.

In this document, we will describe:
-   How to run the tests offline, using previously recorded HTTP interactions,
    or online, by authenticating with Azure to record new HTTP interactions
-   How to write new tests using our utility classes

# Getting the tests to run

This section describes how to run the SDK tests,
by installing dependencies into a virtual environment
and using a helper script and the [pytest](https://docs.pytest.org/en/latest/) test runner
to choose which tests to run.

## Running the tests

Azure SDK tests use [pytest](https://docs.pytest.org/en/latest/) test runner.
To run all the tests, you can use the following command:

```Shell
pytest
```

You can provide directories or individual files as positional arguments
to specify particular tests to run
rather than running the entire test suite. For example:
```Shell
pytest -s sdk/storage/azure-mgmt-storage/
pytest sdk/storage/azure-mgmt-storage/tests/test_mgmt_storage.py
```

By default, tests run in playback mode,
using recordings of HTTP interactions to simulate
requests made against Azure and allow the tests to run offline.
To run the tests in live (or "recording") mode,
you'll need to set up token-based Azure authentication.

## Getting Azure credentials

There are several ways to authenticate to Azure,
but to be able to record test HTTP interactions,
you must use an OAuth authentication method which gives you a token:
- Azure Active Directory user/password
- Active Directory application and service principal

Certificate authentication does not allow you to record HTTP queries for testing.

### Get a token with Azure Active Directory user/password. This is considered deprecated and should not be used anymore (https://docs.microsoft.com/en-us/python/azure/python-sdk-azure-authenticate?view=azure-python#mgmt-auth-legacy).

1.  Connect to the [Azure Classic Portal](https://manage.windowsazure.com/) with your admin account.
2.  Create a user in your default AAD https://azure.microsoft.com/en-us/documentation/articles/active-directory-create-users/
   **You must NOT activate Multi-Factor Authentication!**
3.  Go to Settings - Administrators.
4.  Click on *Add* and enter the email of the new user.
    Check the checkbox of the subscription you want to test with this user.
5.  Login to Azure Portal with this new user to change the temporary password to a new one.
    You will not be able to use the temporary password for OAuth login.

You are now able to log in Python using OAuth. You can test with this code:
```python
from azure.common.credentials import UserPassCredentials
credentials = UserPassCredentials(
    'user@domain.com',     # Your new user
    'my_smart_password',   # Your password
)
```

### Get a token with Active Directory application and service principal

Follow this detailed tutorial to set up an Active Directory application and service principal:
https://azure.microsoft.com/en-us/documentation/articles/resource-group-create-service-principal-portal/

To use the credentials from Python,
you need the application ID (a.k.a. client ID),
authentication key (a.k.a. client secret),
tenant ID and subscription ID from the Azure portal for use in the next step.
[This section of the above tutorial](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal#get-application-id-and-authentication-key)
describes where to find them
(besides the subscription ID,
which is in the "Overview" section of the "Subscriptions" blade.)

You are now able to log in from Python using OAuth.
You can test with this code:
```python
from azure.common.credentials import ServicePrincipalCredentials

credentials = ServicePrincipalCredentials(
    client_id =  'ABCDEFGH-1234-ABCD-1234-ABCDEFGHIJKL',
    secret = 'XXXXXXXXXXXXXXXXXXXXXXXX',
    tenant = 'ABCDEFGH-1234-ABCD-1234-ABCDEFGHIJKL'
)
```

## Providing credentials to the tests

When you run tests in playback mode,
they use a fake credentials file,
located at `tools/azure-sdk-tools/devtools_testutils/mgmt_settings_fake.py`,
to simulate authenticating with Azure.

In live mode, you need to use actual credentials
like those you obtained in the previous section.
To enable the tests to use them,
make a copy of the `mgmt_settings_fake.py` file in the same location,
and rename it `mgmt_settings_real.py`.
Then make the following changes:

*   Change the value of the `SUBSCRIPTION_ID` constant to your subscription ID.
    (If you don't have it,
    you can find it in the "Overview" section of the "Subscriptions" blade
    in the [Azure portal](https://portal.azure.com/).)
*   Change the `get_credentials()` function to construct and return
    a `UserPassCredentials` or `ServicePrincipalCredentials` object
    such as you constructed in the samples in the previous section.
    (Don't forget to make sure the necessary imports are present as well!)

**Important: `mgmt_settings_real.py` should not be committed since it contains your actual credentials! To prevent this, it is included in `.gitignore`.**

## Running tests in live mode

To configure the tests to run in live mode, you have two options:

*   Set the environment variable `AZURE_TEST_RUN_LIVE` to "true" or "yes".
    If you want to go back to playback mode you can either unset it entirely
    or set it to "false" or "no".
*   Create a `testsettings_local.cfg` file in the same directory as
    `mgmt_settings_real.py`. It should look like the following:
    ```
    live-mode: true
    ```
    To go back to playback mode using the config file,
    change the "true" to "false" or delete the file.
    (`testsettings_local.cfg` is listed in `.gitignore`
    and not present in the repo; if it's missing,
    the tests default to playback mode.)

Now you can run tests using the same method described in
[Running the tests](#running-the-tests).
You would be well-advised to specify a limited number of tests to run.
Running every existing test in live mode will take a very long time
and produce a great deal of changes to recording files in your Git repository.

# Writing new tests

SDK tests are based on the `scenario_tests` subpackage of the
[`azure-devtools`](https://pypi.python.org/pypi/azure-devtools) package.
`scenario_tests` is a general, mostly abstract framework
providing several features useful for the SDK tests, for example:

*   HTTP interaction recording and playback using [vcrpy](https://pypi.python.org/pypi/vcrpy)
*   Creation and cleanup of helper resources, such as resource groups,
    for tests that need them in order to test other services
*   Processors for modifying requests and responses when writing or reading recordings
    (for example, to avoid recording credential information)
*   Patches for overriding functions and methods that don't work well with tests
    (such as long-running operations)

Code in the [`azure-sdk-tools/devtools_testutils`](tools/azure-sdk-tools/devtools_testutils) directory
provides concrete implementations of the features provided in `scenario_tests`
that are oriented around use in SDK testing
and that you can use directly in your unit tests.

## Test structure

New tests should be located alongside the packages containing the code they test.
For example, the tests for `azure-mgmt-media` are in `azure-mgmt-media/tests`.
Each test folder also has a `recordings` subfolder containing one .yaml recording file
for each test that has HTTP interactions to record.

There are also legacy tests in the following three locations:

*   azure-servicebus/tests
*   azure-servicemanagement-legacy/tests

For more information about legacy tests, see [Legacy tests](https://github.com/Azure/azure-sdk-for-python/wiki/Legacy-tests).

## Using the Azure Python SDK test framework

This section will demonstrate writing tests using `devtools_testutils`
with a few increasingly sophisticated examples
to show how to use some of the features of the underlying test frameworks.

### Example 1: Basic Azure service interaction and recording

```python
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtTestCase

class ExampleResourceGroupTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(ExampleResourceGroupTestCase, self).setUp()
        self.client = self.create_mgmt_client(ResourceManagementClient)

    def test_create_resource_group(self):
        test_group_name = self.get_resource_name('testgroup')
        group = self.client.resource_groups.create_or_update(
            test_group_name,
            {'location': 'westus'}
        )
        self.assertEqual(group.name, test_group_name)
        self.client.resource_groups.delete(group.name).wait()
```

This simple test creates a resource group and checks that its name
is assigned correctly.

Notes:

1.  This test inherits all necessary behavior for HTTP recording and playback
    described previously in this document
    from its `AzureMgmtTestCase` superclass.
    You don't need to do anything special to implement it.
2.  The `get_resource_name()` helper method of `AzureMgmtTestCase`
    creates a pseudorandom name based on the parameter
    and the names of the test file and method.
    This ensures that the name generated is the same for each run
    of the same test, thereby ensuring reproducability,
    but prevents name collisions if the tests are run live
    and the same parameter is used from several different tests.
3.  The `create_mgmt_client()` helper method of `AzureMgmtTestCase`
    creates a client object using the credentials
    from `mgmt_settings_fake.py` or `mgmt_settings_real.py` as appropriate,
    with some checks to make sure it's created successfully
    and cause the unit test to fail if not.
    You should use it for any clients you create.
4.  Note that this test cleans up the resource group it creates!
    If you create resources yourself as part of the test,
    make sure to delete them afterwards.
    But if you need something like a resource group
    as a prerequisite for what you're actually trying to test,
    you should use a "preparer" as demonstrated in the following two examples.
    Preparers will create and clean up helper resources for you.


### Example 2: Basic preparer usage

```python
from azure.mgmt.sql import SqlManagementClient
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class ExampleSqlServerTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(ExampleSqlServerTestCase, self).setUp()
        self.client = self.create_mgmt_client(SqlManagementClient)

    @ResourceGroupPreparer()
    def test_create_sql_server(self, resource_group, location):
        test_server_name = self.get_resource_name('testsqlserver')
        server_creation = self.client.servers.create_or_update(
            resource_group.name,
            test_server_name,
            {
                'location': location,
                'version': '12.0',
                'administrator_login': 'mysecretname',
                'administrator_login_password': 'HusH_Sec4et'
            }
        )
        server = server_creation.result()
        self.assertEqual(server.name, test_server_name)
```

This test creates a SQL server and confirms that its name is set correctly.
Because a SQL server must be created in a resource group,
the test uses a `ResourceGroupPreparer` to create a group for use in the test.

Preparers are [decorators](https://www.python.org/dev/peps/pep-0318/)
that "wrap" a test method,
transparently replacing it with another function that has some additional functionality
before and after it's run.
For example, the `@ResourceGroupPreparer` decorator adds the following to the wrapped method:
*   creates a resource group
*   inspects the argument signature of the wrapped method
    and passes in information about the created resource group
    if appropriately-named parameters
    (here, `resource_group` and `location`) are present
*   deletes the resource group after the test is run

Notes:

1.  HTTP interactions undertaken by preparers
    to create and delete the prepared resource
    are not recorded or played back,
    as they're not part of what the test is testing.
2.  If the test is run in playback mode,
    the `resource_group` parameter will be a simple `FakeResource` object
    with a pseudorandom `name` attribute and a blank `id` attribute.
    If you need a more sophisticated fake object, see the next example.
3.  Why not use a preparer in Example 1, above?

    Preparers are only for *auxiliary* resources
    that aren't part of the main focus of the test.
    In example 1, we want to test the actual creation and naming
    of the resource group, so those operations are part of the test.
    By contrast, in example 2, the subject of the test
    is the SQL server management operations;
    the resource group is just a prerequisite for those operations.
    We only want this test to fail if something is wrong with the SQL server creation.
    If there's something wrong with the resource group creation,
    there should be a dedicated test for that.

### Example 3: More complicated preparer usage

```python
from azure.mgmt.media import MediaServicesManagementClient
from devtools_testutils import (
    AzureMgmtTestCase, ResourceGroupPreparer, StorageAccountPreparer, FakeResource
)

FAKE_STORAGE_ID = 'STORAGE-FAKE-ID'
FAKE_STORAGE = FakeResource(name='teststorage', id=FAKE_STORAGE_ID)

class ExampleMediaServiceTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(ExampleMediaServiceTestCase, self).setUp()
        self.client = self.create_mgmt_client(MediaServicesManagementClient)

    @ResourceGroupPreparer(parameter_name='group')
    @StorageAccountPreparer(playback_fake_resource=FAKE_STORAGE,
                            name_prefix='testmedia',
                            resource_group_parameter_name='group')
    def test_create_media_service(self, group, location, storage_account):
        test_media_name = self.get_resource_name('pymediatest')
        media_obj = self.client.media_service.create(
            group.name,
            test_media_name,
            {
                'location': location,
                'storage_accounts': [{
                    'id': storage_account.id,
                    'is_primary': True,
                }]
            }
        )

        self.assertEqual(media_obj.name, test_media_name)
```

This test creates a media service and confirms that its name is set correctly.

Notes:

1.  Here, we want to test creation of a media service,
    which requires a storage account.
    We want to use a preparer for this,
    but creation of a storage account itself needs a resource group.
    So we need both a `ResourceGroupPreparer` and a `StorageAccountPreparer`,
    in that order.
2.  Both preparers are customized.
    We pass a `parameter_name` keyword argument of `group` to `ResourceGroupPreparer`,
    and as a result the resource group is passed into the test method
    through the `group` parameter (rather than the default `resource_group`).
    Then, because `StorageAccountPreparer` needs a resource group,
    we need to let it know about the modified parameter name.
    We do so with the `resource_group_parameter_name` argument.
    Finally, we pass a `name_prefix` to `StorageAccountPreparer`.
    The names it generates by default include the fully qualified test name,
    and so tend to be longer than is allowed for storage accounts.
    You'll probably always need to use `name_prefix` with `StorageAccountPreparer`.
3.  We want to ensure that the group retrieved by `get_properties`
    has a `kind` of `BlobStorage`.
    We create a `FakeStorageAccount` object with that attribute
    and pass it to `StorageAccountPreparer`,
    and also pass the `kind` keyword argument to `StorageAccountPreparer`
    so that it will be passed through when a storage account is prepared for real.
4.  Similarly to how a resource group parameter is added by `ResourceGroupPreparer`,
    `StorageAccountPreparer` passes the model object for the created storage account
    as the `storage_account` parameter, and that parameter's name can be customized.
    `StorageAccountPreparer` also creates an account access key
    and passes it into the test method through a parameter whose name is formed
    by appending `_key` to the name of the parameter for the account itself.

### Example 4: Different endpoint than public Azure (China, Dogfood, etc.)

```python
from azure.mgmt.sql import SqlManagementClient
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

_CUSTOM_ENDPOINT = "https://api-dogfood.resources.windows-int.net/"

class ExampleSqlServerTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(ExampleSqlServerTestCase, self).setUp()
        self.client = self.create_mgmt_client(
            SqlManagementClient,
            base_url=_CUSTOM_ENDPOINT
        )

    @ResourceGroupPreparer(client_kwargs={'base_url':_CUSTOM_ENDPOINT})
    def test_create_sql_server(self, resource_group, location):
        test_server_name = self.get_resource_name('testsqlserver')
        server_creation = self.client.servers.create_or_update(
            resource_group.name,
            test_server_name,
            {
                'location': location,
                'version': '12.0',
                'administrator_login': 'mysecretname',
                'administrator_login_password': 'HusH_Sec4et'
            }
        )
        server = server_creation.result()
        self.assertEqual(server.name, test_server_name)
```


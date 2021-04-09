# Table of contents

-   [Overview](#overview)
-   [Getting the tests to run](#running-the-tests)
    -   [Setting up a test environment](#setting-up-a-test-environment)
    -   [Running the tests](#running-the-tests)
    -   [Getting Azure credentials](#getting-azure-credentials)
        -   [Get a token with Active Directory application and service principal](#get-a-token-with-active-directory-application-and-service-principal)
    -   [Providing credentials to the tests](#providing-credentials-to-the-tests)
    -   [Running tests in live mode](#running-tests-in-live-mode)
- [Using the Azure Python SDK test framework](#writing-new-tests)

IMPORTANT NOTE: All the commands in this page assumes you have loaded the [dev_setup][dev_setup] in your currently loaded virtual environment.

# Overview

This page is to help you write tests for Azure Python SDK when these tests require Azure HTTP requests. The Azure SDK test framework uses the [`azure-devtools`][azure_devtools] package, which in turn rests upon on a HTTP recording system ([vcrpy][vcrpy]) that enables tests dependent on network interaction to be run offline.

In this document, we will describe:
-   [How to run the tests online (by authenticating with Azure to record new HTTP interactions)](#running-tests-in-live-mode)
-   [How to run the tests offline (using previously recorded HTTP interactions)](#running-tests-in-playback-mode)
-   [How to write new tests using our utility classes](#writing-new-tests)

# Getting the tests to run

This section describes how to run the SDK tests, by installing dependencies into a virtual environment and using a helper script and the [pytest][pytest] test runner to choose which tests to run.

## Running the tests

In this section, we will be running the tests in `azure-mgmt-storage`. Azure SDK tests use [pytest][pytest] test runner. To run all the tests, you can use the following command:

```Shell
sdk/storage/azure-mgmt-storage> pytest
```

You can provide directories or individual files as positional arguments to specify particular tests to run rather than running the entire test suite. For example:
```Shell
sdk/storage/azure-mgmt-storage> pytest
sdk/storage/azure-mgmt-storage> pytest tests/test_mgmt_storage.py
```

If you have print statements in your tests for debugging you can add the `-s` flag to send those print statements to standard output:
```Shell
sdk/storage/azure-mgmt-storage> pytest -s
```

## Getting Azure credentials

There are several ways to authenticate to Azure, but to be able to record test HTTP interactions, you must use an OAuth authentication method which gives you a token:
- Active Directory application and service principal

### Get a token with Active Directory application and service principal

Follow this detailed tutorial to set up an Active Directory application and service principal:
https://azure.microsoft.com/documentation/articles/resource-group-create-service-principal-portal/

To use the credentials from Python, you need:
* Application ID (a.k.a. client ID)
* Authentication key (a.k.a. client secret)
* Tenant ID
* Subscription ID from the Azure portal
[This section of the above tutorial](https://docs.microsoft.com/azure/azure-resource-manager/resource-group-create-service-principal-portal#get-application-id-and-authentication-key) describes where to find them (besides the subscription ID, which is in the "Overview" section of the "Subscriptions" blade.)

The recommended practice is to store these three values in environment variables called `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET`. To set an environment variable use the following commands:
```Shell
$env:AZURE_TENANT_ID='<value>'        # PowerShell only
set AZURE_TENANT_ID=<value>         # Windows CMD (alternatively, use export AZURE_TENANT_ID=<value> to export to the global env)
export AZURE_TENANT_ID=<value>      # Linux shell only
```
*** Note: when setting these variables, do not wrap the value in quotation marks ***

You are now able to log in from Python using OAuth.
You can test with this code:
```python
import os
from azure.common.credentials import ServicePrincipalCredentials

credentials = ServicePrincipalCredentials(
    client_id = os.environ['AZURE_CLIENT_ID'],
    secret = os.environ['AZURE_CLIENT_SECRET'],
    tenant = os.environ['AZURE_TENANT_ID']
)
```

## Providing credentials to the tests

When you run tests in playback mode, they use a fake credentials file, located at [`tools/azure-sdk-tools/devtools_testutils/mgmt_settings_fake.py`][mgmt_settings_fake], to simulate authenticating with Azure. In most scenarios you will not have to adjust this file, you will have to make edits to this file if your service uses values that are not already included in the `mgmt_settings_fake.py` file.

In live mode, you need to use real credentials like those you obtained in the previous section. To enable the tests to use them, make a copy of the `mgmt_settings_fake.py` file in the same location, and rename it `mgmt_settings_real.py`.
Then make the following changes:

* Change the value of the `SUBSCRIPTION_ID` constant to your subscription ID. (If you don't have it, you can find it in the "Overview" section of the "Subscriptions" blade in the [Azure portal][azure_portal].)
* Change the `get_credentials()` function to construct and return a `UserPassCredentials` (Don't forget to make sure the necessary imports are present as well!).
```python
def get_credentials(**kwargs):
    import os
    from azure.common.credentials import ServicePrincipalCredentials

    return ServicePrincipalCredentials(
        client_id = os.environ['AZURE_CLIENT_ID'],
        secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant = os.environ['AZURE_TENANT_ID']
    )
```
* Change the `get_azure_core_credentials()` function to construct and return a `ClientSecretCredential`:
```python
def get_azure_core_credentials(**kwargs):
    from azure.identity import ClientSecretCredential
    import os
    return ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )
```
These two methods are used by the authentication methods within `AzureTestCase` to provide the correct credential for your client class, you do not need to call these methods directly. Authenticating clients will be discussed further in the [examples](#writing-management-plane-test) section.

**Important: `mgmt_settings_real.py` should not be committed since it contains your actual credentials! To prevent this, it is included in `.gitignore`.**

## Running tests in live mode

To configure the tests to run in live mode, you have two options:
* Set the environment variable `AZURE_TEST_RUN_LIVE` to "true" or "yes".
* Create the `tools/azure-sdk-tools/devtools_testutils/testsettings_local.cfg` file and copy and paste the following line:
    ```
    live-mode: true
    ```
(`testsettings_local.cfg` is listed in `.gitignore` and not present in the repo; if it's missing, the tests default to playback mode.)

Now you can run tests using the same method described in [Running the tests](#running-the-tests). You would be well-advised to specify a limited number of tests to run. Running every existing test in live mode will take a very long time and produce a great deal of changes to recording files in your Git repository. However, for changes in the client code, the recordings will need to be committed to the Git repository.

## Running tests in playback mode
Now that the tests have been run against live resources and generated the HTTP recordings, you can run your tests in playback mode. There are two options for changing from live mode to playback mode:
* Set the environment variable `AZURE_TEST_RUN_LIVE` to "false" or "no".
* Change the `tools/azure-sdk-tools/devtools_testutils/testsettings_local.cfg` file to:
    ```
    live-mode: false
    ```

# Writing new tests

Code in the [`azure-sdk-tools/devtools_testutils`][devtools_testutils] directory provides concrete implementations of the features provided in `scenario_tests` that are oriented around use in SDK testing and that you can use directly in your unit tests.

## Test structure

New tests should be located alongside the packages containing the code they test. For example, the tests for `azure-mgmt-media` are in `azure-mgmt-media/tests`.

There are also legacy tests in the following three locations:

*   azure-servicebus/tests
*   azure-servicemanagement-legacy/tests

For more information about legacy tests, see [Legacy tests](https://github.com/Azure/azure-sdk-for-python/wiki/Legacy-tests).

## Writing management plane test

Management plane SDKs are those that are formatted `azure-mgmt-xxxx`, otherwise the SDK is data plane. Management plane SDKs work against the [Azure Resource Manager APIs][arm_apis], while the data plane SDKs will work against service APIs. This section will demonstrate writing tests using `devtools_testutils` with a few increasingly sophisticated examples to show how to use some of the features of the underlying test frameworks.

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

This simple test creates a resource group and checks that its name is assigned correctly.

Notes:
1. This test inherits all necessary behavior for HTTP recording and playback described previously in this document from its `AzureMgmtTestCase` superclass. You don't need to do anything special to implement it.
2. The `get_resource_name()` helper method of `AzureMgmtTestCase` creates a pseudorandom name based on the parameter and the names of the test file and method. This ensures that the name generated is the same for each run of the same test, ensuring reproducability and preventing name collisions if the tests are run live and the same parameter is used from several different tests.
3. The `create_mgmt_client()` helper method of `AzureMgmtTestCase` creates a client object using the credentials from `mgmt_settings_fake.py` or `mgmt_settings_real.py` as appropriate, with some checks to make sure it's created successfully and cause the unit test to fail if not. You should use it for any clients you create.
4. While the test cleans up the resource group it creates, you will need to manually delete any resources you've created independent of the test framework. But if you need something like a resource group as a prerequisite for what you're actually trying to test, you should use a "preparer" as demonstrated in the following two examples. Preparers will create and clean up helper resources for you.


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

This test creates a SQL server and confirms that its name is set correctly. Because a SQL server must be created in a resource group, the test uses a `ResourceGroupPreparer` to create a group for use in the test.

Preparers are [decorators][decorators] that "wrap" a test method, transparently replacing it with another function that has some additional functionality before and after it's run. For example, the `@ResourceGroupPreparer` decorator adds the following to the wrapped method:
* creates a resource group
* inspects the argument signature of the wrapped method and passes in information about the created resource group if appropriately-named parameters (here, `resource_group` and `location`) are present
* deletes the resource group after the test is run

Notes:
1. HTTP interactions undertaken by preparers to create and delete the prepared resource are not recorded or played back, as they're not part of what the test is testing.
2. If the test is run in playback mode, the `resource_group` parameter will be a simple `FakeResource` object with a pseudorandom `name` attribute and a blank `id` attribute. If you need a more sophisticated fake object, see the next example.
3. Why not use a preparer in Example 1, above?

    Preparers are only for *auxiliary* resources that aren't part of the main focus of the test. In example 1, we want to test the actual creation and naming of the resource group, so those operations are part of the test.
    By contrast, in example 2, the subject of the test is the SQL server management operations; the resource group is just a prerequisite for those operations.  We only want this test to fail if something is wrong with the SQL server creation.
    If there's something wrong with the resource group creation, there should be a dedicated test for that.

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

1. Here, we want to test creation of a media service, which requires a storage account. We want to use a preparer for this, but creation of a storage account itself needs a resource group. So we need both a `ResourceGroupPreparer` and a `StorageAccountPreparer`, in that order.
2. Both preparers are customized. We pass a `parameter_name` keyword argument of `group` to `ResourceGroupPreparer`, and as a result the resource group is passed into the test method through the `group` parameter (rather than the default `resource_group`). Then, because `StorageAccountPreparer` needs a resource group, we need to let it know about the modified parameter name. We do so with the `resource_group_parameter_name` argument. Finally, we pass a `name_prefix` to `StorageAccountPreparer`. The names it generates by default include the fully qualified test name, and so tend to be longer than is allowed for storage accounts. You'll probably always need to use `name_prefix` with `StorageAccountPreparer`.
3. We want to ensure that the group retrieved by `get_properties` has a `kind` of `BlobStorage`. We create a `FakeStorageAccount` object with that attribute and pass it to `StorageAccountPreparer`, and also pass the `kind` keyword argument to `StorageAccountPreparer` so that it will be passed through when a storage account is prepared for real.
4. Similarly to how a resource group parameter is added by `ResourceGroupPreparer`, `StorageAccountPreparer` passes the model object for the created storage account as the `storage_account` parameter, and that parameter's name can be customized. `StorageAccountPreparer` also creates an account access key and passes it into the test method through a parameter whose name is formed by appending `_key` to the name of the parameter for the account itself.

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

<!-- LINKS -->
[arm_apis]: https://docs.microsoft.com/rest/api/resources/
[azure_devtools]: https://pypi.org/project/azure-devtools/
[azure_portal]: https://portal.azure.com/
[decorators]: https://www.python.org/dev/peps/pep-0318/
[dev_setup]: https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/dev_setup.md
[devtools_testutils]: https://github.com/Azure/azure-sdk-for-python/tree/master/tools/azure-sdk-tools/devtools_testutils
[mgmt_settings_fake]: https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/mgmt_settings_fake.py
[pytest]: https://docs.pytest.org/en/latest/
[vcrpy]: https://pypi.python.org/pypi/vcrpy
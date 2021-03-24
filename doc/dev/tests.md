# Setup Python Development Environment
In this document we will provide the introduction to the testing framework by:

- [Setting up your development environment](#setup-the-development-environment)
- [Integrating with pytest](#integrate-with-the-pytest-test-framework)
- [Using Tox](#tox)
- [The `devtools_testutils` package](#devtools_testutils-package)
- [Writing New Tests](#writing-new-tests)
- [Define our credentials and settings](#define-credentials)
- [Create live test resources](#create-live-test-resources)
- [Write our test](#writing-your-test)
- [An example test](#an-example-test)
- [Run and record our tests](#run-and-record-the-test)
    -[Purging secrets from recording files](#purging-secrets)

## Setup your development environment

The Azure SDK Python team creates libraries that are compatible with Python 2.7 and 3.5 and up. We will set up working Python virtual environments for Python 2.7, 3.5, and 3.9. It is recommended to do your development work in Python3, however it is helpful to have virtual environments for other versions to make debugging PRs easier locally.

* Python 3.9: Use the [python website](https://www.python.org/downloads/) or the one-click experience from the [Windows store](https://www.microsoft.com/p/python-39/9p7qfqmjrfp7) (Windows only).
* Python 3.5: Use the [python website](https://www.python.org/downloads/release/python-3510/)
* Python 2.7: Use the [python website](https://www.python.org/downloads/release/python-2718/)
```cmd
C:\Users> python -m venv env
C:\Users> env\scripts\activate       # PowerShell only
C:\Users> source env\bin\activate    # Linux shell (Bash, ZSH, etc.) only
C:\Users> env\scripts\activate.bat   # Windows CMD only
(env)C:\Users>
```
To create virtual environment for different versions of Python use the `-p` flag to pass the specific Python executable you want to use
```cmd
C:\Users> python -m venv -p <path/to/Python/Python35/python.exe> py35_venv
C:\Users> python -m venv -p <path/to/Python/Python27/python.exe> py27_venv
```

### SDK root directory

In the root directory of our SDK, a number of mandatory files have been added. When creating your own SDK, these files can be copied from the [`sdk/template`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/template) project, and modified to your needs.

- README.md. This is the description and guidance for customers or your SDK. Please see the guide on writing a README to make sure you have the complete [content requirements and formatting](https://review.docs.microsoft.com/help/contribute-ref/contribute-ref-how-to-document-sdk?branch=master#readme).
- CHANGELOG.md. This is where you will add the summary of changes for each new release. Please see [the guidance](https://azure.github.io/azure-sdk/policies_releases.html#changelog-guidance) for correct formatting.
- setup.py. This is the 'installer' for your Python SDK. Please see [the guide on Python packaging][packaging] for details on customizing this for a specific package.
- setup.cfg. This is an artifact used in building the Python package. Please see [the guide on Python packaging][packaging] for details.
- MANIFEST.in. This is an artifact used in building the Python package. Please see [the guide on Python packaging][packaging] for details.
- dev_requirements.txt. This is for developers, and lists the packages required for running the tests and samples. See the dependency installation section below.
- sdk_packaging.toml. This configuration is used by the packaging pipeline and no further modifications should be required.


### Dependency installation

Our SDK will have dependencies on other packages in the Azure Python SDK ecosystem. In order to run our tests and samples, we will need to setup our virtual environment to be able to find these external dependencies within the repo. We use the `dev_requirements.txt` to list these dependencies as relative paths (along with any other external packages that should be installed from PyPI).
The libraries currently listed in this file include `azure-core` and `azure-identity` as well as some internal tooling packages and our testing framework libraries.
These dependencies can be installed with the following command:

```cmd
(env)azure-sdk-for-python\sdk\my-directory\my-library> pip install -r dev_requirements.txt
```
Next we will install our Python SDK to the virtual environment as an 'editable install' - this means that as we work on the implementation, we will be able to run the package as it develops, as opposed to having to periodically rebuild and reinstall.
```cmd
(env)azure-sdk-for-python\sdk\my-directory\my-library> pip install -e .
```

We should now be able to open an interactive Python terminal, and execute code from our new SDK
```cmd
(env)azure-sdk-for-python\sdk\my-directory\my-library> python

>>> import azure.my_library
>>> print(azure.my_library.__version__)
0.0.1
```

### Open code in IDE

Open the directory for your library in your preferred editor, for example VSCode.
```cmd
(env)azure-sdk-for-python\sdk\my-directory\my-library> code .
```

## Integrate with the pytest Test Framework
As a quick background, the Azure SDK uses the [pytest](https://docs.pytest.org/en/latest/) test runner to support creating unit and functional tests for Track 2 Azure libraries. To intall `pytest` run `pip install pytest` from your virtual environment, you can confirm the installation was successful by running `pytest -V`. The commands will run all files of the form `test_*.py` or `*_test.py` in the provided directory and its subdirectories, for more information check out the [docs](https://docs.pytest.org/en/stable/getting-started.html#run-multiple-tests).

With the pytest test suite you can provide directories or specific tests to run rather than running the entire test suite:
```cmd
azure-sdk-for-python\sdk\my-directory\my-library> pytest
azure-sdk-for-python\sdk\my-directory\my-library> pytest <test_file.py>
```

If your tests are broken up into multiple folders for organization, you can run specific folders:
```cmd
azure-sdk-for-python\sdk\my-directory\my-library> pytest .\tests\async_tests\
azure-sdk-for-python\sdk\my-directory\my-library> pytest .\tests\async_tests\<test_file.py>
```

In addition you can provide keywords to run specific tests within the suite or within a specific file
```cmd
azure-sdk-for-python\sdk\my-directory\my-library> pytest -k <keyword>
azure-sdk-for-python\sdk\my-directory\my-library> pytest <test_file.py> -k <keyword>
```

If you have print statements in your tests for debugging you can add the `-s` flag to send those print statements to standard output:
```cmd
azure-sdk-for-python\sdk\my-directory\my-library> pytest sdk/storage/azure-mgmt-storage/ -s
```

## Tox
The Python SDK uses the [tox project](https://tox.readthedocs.io/en/latest/) to automate releases, run tests, run linters, and build our documentation. The `tox.ini` file is located at `azure-sdk-for-python/eng/tox/tox.ini` for reference. You do not need to make any changes to the tox file for tox to work with your project. Tox will create a directory (`.tox`) in the head of your branch. The first time you run tox commands it may take several moments, but subsequent runs will be quicker. To install tox run the following command from within your virtual environment.
`(env) > pip install tox tox-monorepo`.

To run a tox command from your directory use the following commands:
```cmd
azure-sdk-for-python\sdk\my-directory\my-library> tox -c ../../../eng/tox/tox.ini -e sphinx
azure-sdk-for-python\sdk\my-directory\my-library> tox -c ../../../eng/tox/tox.ini -e lint
azure-sdk-for-python\sdk\my-directory\my-library> tox -c ../../../eng/tox/tox.ini -e mypy
azure-sdk-for-python\sdk\my-directory\my-library> tox -c ../../../eng/tox/tox.ini -e whl
azure-sdk-for-python\sdk\my-directory\my-library> tox -c ../../../eng/tox/tox.ini -e sdist
azure-sdk-for-python\sdk\my_directory\my_library> tox -c ../../../eng/tox/tox.ini -e samples
azure-sdk-for-python\sdk\my_directory\my_library> tox -c ../../../eng/tox/tox.ini -e apistub
```
A quick description of the five commands above:
* sphinx: documentation generation using the inline comments written in our code
* lint: runs pylint to make sure our code adheres to the style guidance
* mypy: runs the mypy static type checker for Python to make sure that our types are valid. In order to opt-in to mypy checks, add your package name to [this](https://github.com/Azure/azure-sdk-for-python/blob/master/eng/tox/mypy_hard_failure_packages.py) list of packages.
* whl: creates a whl package for installing our package
* sdist: creates a zipped distribution of our files that the end user could install with pip
* samples: runs all of the samples in the `samples` directory and verifies they are working correctly
* apistub: runs the [apistubgenerator](https://github.com/Azure/azure-sdk-tools/tree/master/packages/python-packages/api-stub-generator) tool on your code

## `devtools_testutils` Package
The Azure SDK team has created some in house tools to help with easier testing. These additional tools are located in the `devtools_testutils` package that was installed with your `dev_requirements.txt`. In this package is the [`AzureTestCase`](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/azure_testcase.py#L99-L350) object which every test case object should inherit from. This management object takes care of creating and scrubbing recordings to make sure secrets are not added to the recordings files (and subsequently to the git history) and authenticating clients for test methods.

## Writing New Tests
SDK tests are based on the `scenario_tests` subpackage located in [`azure-sdk-for-python/tools/azure-devtools/src/azure_devtools`](https://pypi.org/project/azure-devtools/). `scenario_tests` is a general, mostly abstracted framework which provides several useful features for writing SDK tests, ie:
* HTTP interaction recording and playback using [vcrpy](https://pypi.python.org/pypi/vcrpy)
* Creation and cleanup of helper resources, such as resource groups, storage accounts, etc. which can be used in order to test services
* Processors for modifying requests and responses when writing or reading recordings (for example, to to avoid recording credential information)
* Patches for overriding functions and methods that don't work well with testing frameworks (such as long-running operations)

Code in the [`azure-sdk-tools/devtools_testutils`](https://github.com/Azure/azure-sdk-for-python/tree/master/tools/azure-sdk-tools/devtools_testutils) directory provides concrete implementations of the features provided in `scenario_tests` that are oriented around use in SDK testing and that you can use directly in your unit tests.

## Define credentials
When you run tests in playback mode, they use a fake credentials file, located at [`tools/azure-sdk-tools/devtools_testutils/mgmt_settings_fake.py`][mgmt_settings_fake] to simulate authenticating with Azure.

In live mode, the credentials need to be real so that the tests are able to connect to the service. Create a `.env` file at the root of the repository (in the same directory as the `sdk`, `tools`, `eng` folders). In this file you can define any environment variables you need for a test and that will be loaded by the `AzureTestCase` file.
1. Add the `SUBSCRIPTION_ID` variable with your organizations subscription ID. If you don't have it, you can find it in the "Overview" section of the "Subscriptions" blade in the [Azure portal](https://portal.azure.com/).
2. Define the `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` which are available after creating a Service Principal or can be retrieved from the Azure Portal if you have already created a Service Principal. If you do not have a Service Principal, check out the [Azure docs](https://docs.microsoft.com/cli/azure/ad/sp?view=azure-cli-latest#az_ad_sp_create_for_rbac) on a simple one line command to create one. The recommended practice is to include your alias or name in the Service Principal name.
    Your `.env` file stores secrets in plain text so it is important that the contents of this file are not committed to the git repository.
3. Create the `tools/azure-sdk-tools/devtools_testutils/testsettings_local.cfg` file and copy and paste the following line:
```
live-mode: true
```

## Create Live Test Resources
The Azure Python SDK library has two ways of providing live resources to our tests:
* Using an ArmTemplate and the PowerShellPreparer (we will demonstrate this one)
    * [PowerShell preparer implementation](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/powershell_preparer.py)
    * [In line use](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/schemaregistry/azure-schemaregistry/tests/test_schema_registry.py#L30-L39) for the schemaregistry library
* Using an individualized preparer such as the storage preparer
    * [Storage preparer implementation](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/storage_testcase.py)
    * [In line use](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/storage/azure-storage-blob/tests/test_blob_client.py#L49-L61) for the blob client

If your library has a management plane library, you can build a preparer specific to your service using the storage preparer as an example. It is recommended that you use a PowerShellPreparer for new libraries and those without management plane libraries. The `PowerShellPreparer` uses the `New-TestResources.ps1` script to deploy resources using an ARM Template. This script and information about running it can be found in the [`eng/common/TestResources`](https://github.com/Azure/azure-sdk-for-python/tree/master/eng/common/TestResources#live-test-resource-management) directory. For more information about the engineering systems in Azure SDK, check out their [wiki][engsys_wiki]

1. Create an Azure Resource Management Template for your specific service and the configuration you need. This can be done in the portal by creating the resources and at the very last step (Review + Create) clicking "Download a template for automation". Save this template to a `test-resources.json` file under the directory that contains your library (`sdk/<my-library>/test-resources.json`).
2. Use the [`New-TestResources.ps1`](https://github.com/Azure/azure-sdk-for-python/tree/master/eng/common/TestResources#on-the-desktop) script to deploy those resources.
3. Set the environment variables returned from step 2 in your current shell or add them to your `.env` file at the root of the repo to save these secrets. If you choose the latter method, you will have to make sure all the key-value pairs are in the format `<key_name>=<value>`, rather than the  `${env:<key_name>} = '<value>'` formatting used in PowerShell. The names of the environment variables should be in all capital letters, snake case, and be prefixed with the library name. Ie. `TABLES_PRIMARY_KEY`, `FORMRECOGNIZER_ACCOUNT_URL`, `EVENTHUBS_SECRET_KEY`.
4. Create a partial implementation of the PowerShellPreparer to pass in your specific environment variables. An example implementation is shown below for schemaregistry

```python
import functools
from devtools_testutils import PowerShellPreparer

MyServicePreparer = functools.partial(
    PowerShellPreparer, "<my_service_directory>",
    schemaregistry_endpoint="fake_resource.servicebus.windows.net",
    schemaregistry_group="fakegroup"
)
```

The parameters for the `functools.partial` method are:
* The `PowerShellPreparer` class
* The library folder that holds your code (ie. `sdk/schemaregistry`). This value is used to search your environment variables for the appropriate values.
* The remaining arguments are key-value kwargs, with the keys being the environment variables needed for the tests, and the value being a fake value for replacing the actual value in the recordings. The fake value in this implementation will replace the real value in the recording to make sure the secret keys are not committed to the recordings. These values should closely resemble the values because they are used in playback mode and will need to pass any client side validation. The fake value should also be a unique value to the other key-value pairs.

## Write your tests

In the `tests` directory create a file with the naming pattern `test_<what_you_are_testing>.py`. The base of each testing file will be roughly the same:

```python
import functools
import pytest

from devtools_testutils import AzureTestCase, PowerShellPreparer

from azure.schemaregistry import SchemaRegistryClient

SchemaRegistryPreparer = functools.partial(
    PowerShellPreparer, 'schemaregistry',
    schemaregistry_endpoint="fake_resouce.servicebus.windows.net",
    schemaregistry_group="fakegroup"
)

class TestSchemaRegistry(AzureTestCase):

# Start with any helper functions you might need, for example a client creation method:
    def create_schemareg_client(self, endpoint):
        credential = self.get_credential(SchemaRegistryClient)
        client = self.create_client_from_credential(SchemaRegistryClient, credential=credential, endpoint=endpoint)
        return client

    ...

# Write your tests
    @SchemaRegistryPreparer()
    def test_client_creation(self, schemaregistry_endpoint):
        client = self.create_schemareg_client(schemaregistry_endpoint)
        assert client is not None

```

There's a lot going on in the example so we'll take this piece by piece:

* Import everything you will need in your tests as normal, add to your imports the line `from devtools_testutils import AzureTestCase, PowerShellPreparer`. These two objects give our tests a lot of the desired powers.
* `AzureTestCase`: the test class should inherit from this object (`class TestSchemaRegistry(AzureTestCase)`), doing so sets up the recording infrastructure and the client creation methods.
* `PowerShellPreparer`: this preparer serves two purposes.
    * First, it will provide the live keys we need to test our library against live resources.
    * Second, it will keep those same live keys out of our recordings to make sure that we are not leaking our secrets into the recordings.
* At the top of your test class you should include any helper methods you will need. Most libraries will have a client creation method to eliminate repetitive code.
* Following your helper methods will be your actual tests. All test methods must start with "test". The preparer built at the top of the file should decorate your test in the fashion: `@MyPreparer()`.
    * The signature of your test will always contain `self`, and following self will be all the keys that you need from your preparer. A test does not need to have every key passed into it, the test framework will take care of passing in only the parameters specifically requested in the test signature.

If you need logging functionality for your testing, pytest also offers [logging](https://docs.pytest.org/en/stable/logging.html) capabilities either inline through the `caplog` fixture or with command line flags.

## An example test
An example test for schemaregistry looks like:
```python
class SchemaRegistryTestCase(AzureTestCase):

    ...
    @SchemaRegistryPreparer()
    def test_schema_basic(self, schemaregistry_endpoint, schemaregistry_group):
        client = self.create_client(schemaregistry_endpoint)
        schema_name = self.get_resource_name('test-schema-basic')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        serialization_type = "Avro"
        schema_properties = client.register_schema(schemaregistry_group, schema_name, serialization_type, schema_str)

        assert schema_properties.schema_id is not None
        assert schema_properties.location is not None
        assert schema_properties.location_by_id is not None
        assert schema_properties.version is 1
        assert schema_properties.serialization_type == "Avro"

        with pytest.raises(HttpResponseError):
            client.get_schema('a' * 32)
```
The `AzureTestCase` class has the ability to define a client by passing in the client object and the account URL, without having to worry about identity. Test files should not import `azure.identity`, the `self.create_basic_client` will take care of loading environment variables and creating the default credentials.

The test infrastructure heavily leverages the `assert` keyword, which tests if the condition following it is true, and if it is not the program will raise an `AssertionError`. When writing tests, any uncaught exception results in a failure, from an assert or from the code itself (ie. `TypeError`, `ValueError`, `HttpResponseError`, etc.). The assert statements are testing that all the exected properties of the returned object are not `None`, and the last two assert statements verify that the tested properties are a given value. The last two lines of the test use a [context manager](https://docs.python.org/3/library/contextlib.html) used from the `pytest` library that tests whether the following block of code will raise a certain exception. The `client.get_schema('a' * 32)` is expected to fail because it does not exist, and we expect this test to raise an error that is an instance of `HttpResponseError`.

## Run and record the test

From your terminal run the `pytest` command to run all the tests that you have written so far.

```cmd
(env)azure-sdk-for-python\sdk\my-directory\my-library> pytest
```

Your update should run smooth and have green dots representing passing tests. Now if you look at the contents of your `tests` directory there should be a new directory called `recording` with four `.yaml` files. Each `yaml` file is a recording for a single test. To run a test in playback mode change the `testsettings_local.cfg` to `live-mode: false` and rerun the tests with the same command. The test infrastructure will use the automatically created `.yaml` recordings to mock the HTTP traffic and run the tests.

### Purging Secrets

The `yaml` files created from running tests in live mode store the request and response interactions between the library and the service and this can include authorization, account names, shared access signatures, and other secrets. The recordings are included in our public GitHub repository, making it important for us to remove any secrets from these recordings before committing them to the repository. There are two easy ways to remove secrets. The first is the `PowerShellPreparer` implementation, discussed above. This method will automatically purge the keys with the provided fake values. The second way is to use the `self.scrubber.register_name_pair(key, fake_key)` method (This method is a function of the base `AzureTestCase` class), which is used when a secret is dynamically created during a test. For example, [Tables](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/tables/azure-data-tables/tests/_shared/cosmos_testcase.py#L86-L89) uses this method to replace storage account names with standard names.

#### Special Case: Shared Access Signature

Tests that use the Shared Access Signature (SAS) to authenticate a client should use the [`AzureTestCase.generate_sas`](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/azure_testcase.py#L357-L370) method to generate the SAS and purge the value from the recordings. An example of using this method can be found [here](https://github.com/Azure/azure-sdk-for-python/blob/78650ba08523c14227ce8139cba5f4d1e6ed7956/sdk/tables/azure-data-tables/tests/test_table_entity.py#L1628-L1636). The method takes any number of positional arguments, with the first being the method that creates the SAS, and any number of keyword arguments (**kwargs). The method will be purged appropriately and allow for these tests to be run in playback mode.

## Functional vs. Unit Tests

The test written above is a functional test, it generates HTTP traffic and sends data to the service. Most of our clients have some client-side validation for account names, formatting, or properties that do not generate HTTP traffic. For unit tests, the best practice is to have a separate test class from the `AzureTestCase` class which tests client side validation methods. For example, the `azure-data-tables` library has client-side validation for the table name and properties of the entity, below is an example of how these could be tested:

```python
import pytest
from azure.data.tables import TableServiceClient, EntityProperty, EdmType

class TestTablesUnitTest(object):

    def test_invalid_table_name(self):
        account_name = 'fake_account_name'
        account_key = 'fake_account_key1234567890'
        tsc = TableServiceClient(
            account_url='https://{}.table.core.windows.net/'.format(account_name),
            credential=account_key
        )

        invalid_table_name = "bad_table_name" # table name cannot have an '_' character

        with pytest.raises(ValueError):
            tsc.create_table(invalid_table_name)

    def test_entity_properties(self):
        ep = EntityProperty('abc', EdmType.STRING)
        ep = EntityProperty(b'abc', EdmType.BINARY)
        ep = EntityProperty(1.2345, EdmType.DOUBLE)

        with pytest.raises(ValueError):
            ep = EntityProperty(2 ** 75, EdmType.Int64) # Tables can only handle integers up to 2 ^ 63
```

Async tests need to be marked with a `@pytest.mark.asyncio` to be properly handled. For example:
```python
import pytest
from azure.data.tables.aio import TableServiceClient

class TestTablesUnitTest(object):

    @pytest.mark.asyncio
    async def test_invalid_table_name(self):
        account_name = 'fake_account_name'
        account_key = 'fake_account_key1234567890'
        tsc = TableServiceClient(
            account_url='https://{}.table.core.windows.net/'.format(account_name),
            credential=account_key
        )

        invalid_table_name = "bad_table_name" # table name cannot have an '_' character

        with pytest.raises(ValueError):
            await tsc.create_table(invalid_table_name)
```


## More Test Examples

This section will demonstrate how to write tests with the `devtools_testutils` package with a few samples to showcase the features of the test framework.

For more information, refer to the [advanced tests notes][advanced_tests_notes] on more advanced scenarios and additional information.


<!-- Links -->
[advanced_tests_notes]: https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/tests-advanced.md
[azure_devtools]: https://pypi.org/project/azure-devtools/
[engsys_wiki]: https://dev.azure.com/azure-sdk/internal/_wiki/wikis/internal.wiki/48/Create-a-new-Live-Test-pipeline?anchor=test-resources.json
[mgmt_settings_fake]: https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/mgmt_settings_fake.py
[packaging]: https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/packaging.md

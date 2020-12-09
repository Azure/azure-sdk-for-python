# Setup for Testing Tutorial, Python
In this section, we will provide the introduction to the testing framework by:

- [Setting up your development environment](#setup-the-development-environment)
- [Integrating with pytest](#integrate-with-the-pytest-test-framework)
- [Using Tox](#tox)
- [The `devtools_testutils` package](#devtools_testutils-package)
- [Writing New Tests](#Writing-new-tests)
- [Define our credentials and settings](#define-credentials)
- [Create live test resources](#create-live-test-resources)
- [Write our test](#writing-your-test)
- [An example test](#an-example-test)
- [Run and record our tests](#run-and-record-the-test)

## Setup the development environment

Now that you have the code locally, let's set up a development environment. If you previously completed the [API Implementation tutorial](https://github.com/Azure/azure-sdk-pr/blob/master/training/azure-sdk-implement/tutorials/implementation-intro/setup/setup-python.md) the development environment will have already been set up, you can skip this section.
The directory we will be working from for this tutorial can be found at:
[`azure-sdk-for-python\sdk\api-learn\azure-learnappconfig`](https://github.com/Azure/azure-sdk-for-python/tree/feature/tutorial/implementation/starter/sdk/api-learn/azure-learnappconfig)
We will set this as the current working directory, then create and activate a Python virtual environment. This tutorial requires Python version 3.7 and above, you can test your current python version with `python --version`. If the output indicates your python version is below 3.7 you can download the latest version from the [python website](https://www.python.org/downloads/) or with a one-click experience from the [Windows store](https://www.microsoft.com/en-us/p/python-38/9mssztt1n39l) (Windows only).
```cmd
azure-sdk-for-python> cd sdk\api-learn\azure-learnappconfig
azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> python -m venv env
azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> env\scripts\activate       # PowerShell only
azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> source env\bin\activate    # Linux shell (Bash, ZSH, etc.) only
azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> env\scripts\activate.bat   # Windows CMD only
(env)azure-sdk-for-python\sdk\api-learn\azure-learnappconfig>
```

The project, while bare-bones, already has all the necessary components to make a functioning Python package. These components were present in the API Design Intro Tutorial, however we will now take a closer look.

### SDK root directory

In the root directory of our SDK, a number of mandatory files have been added. You will not need to edit these files for this tutorial, but you should be aware about the various components and where to find more details on them. When creating your own SDK, these files can be copied from the [`sdk/template`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/template) project, and modified to your needs.

- README.md. This is the description and guidance for customers or your SDK. Please see the guide on writing a README to make sure you have the complete [content requirements and formatting](https://review.docs.microsoft.com/en-us/help/contribute-ref/contribute-ref-how-to-document-sdk?branch=master#readme).
- CHANGELOG.md. This is where you will add the summary of changes for each new release. Please see [the guidance](https://azure.github.io/azure-sdk/policies_releases.html#changelog-guidance) for correct formatting.
- setup.py. This is the 'installer' for your Python SDK. Please see [the guide on Python packaging](https://github.com/Azure/azure-sdk-pr/issues/225) for details on customizing this for a specific package.
- setup.cfg. This is an artifact used in building the Python package. Please see [the guide on Python packaging](https://github.com/Azure/azure-sdk-pr/issues/225) for details.
- MANIFEST.in. This is an artifact used in building the Python package. Please see [the guide on Python packaging](https://github.com/Azure/azure-sdk-pr/issues/225) for details.
- dev_requirements.txt. This is for developers, and lists the packages required for running the tests and samples. See the dependency installation section below.
- sdk_packaging.toml. This configuration is used by the packaging pipeline and no further modifications should be required.


### Dependency installation

Our SDK will have dependencies on other packages in the Azure Python SDK ecosystem. In order to run our tests and samples, we will need to setup our virtual environment to be able to find these external dependencies within the repo. We use the `dev_requirements.txt` to list these dependencies as relative paths (along with any other external packages that should be installed from PyPI).
The libraries currently listed in this file include `azure-core` and `azure-identity` as well as some internal tooling packages and our testing framework libraries.
These dependencies can be installed with the following command:

```cmd
(env)azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> pip install -r dev_requirements.txt
```
Next we will install our Python SDK to the virtual environment as an 'editable install' - this means that as we work on the implementation, we will be able to run the package as it develops, as opposed to having to periodically rebuild and reinstall.
```cmd
(env)azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> pip install -e .
```

We should now be able to open an interactive Python terminal, and execute code from our new SDK (even though it is currently empty).
```cmd
(env)azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> python

>>> import azure.learnappconfig
>>> print(azure.learnappconfig.__version__)
0.0.1
```

### Open code in IDE

Open the `azure-learnappconfig` directory in your preferred editor, for example VSCode.
```cmd
(env)azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> code .
```


## Integrate with the pytest Test Framework
As a quick background, the Azure SDK uses the [pytest](https://docs.pytest.org/en/latest/) test runner support creating unit and functional tests for Track 2 Azure libraries. To intall `pytest` run `pip install pytest` from your virtual environment. The commands will run all files for the form `test_*.py` or `*_test.py` in the provided directory and its subdirectories, for more information check out the [docs](https://docs.pytest.org/en/stable/getting-started.html#run-multiple-tests). `pytest` will have been install during setup for the [implementation tutorial](https://github.com/Azure/azure-sdk-pr/tree/master/training/azure-sdk-implement), you can confirm by running `pytest -V`. If it was not installed, run the command `pip install pytest` to install.

With the pytest test suite you can provide directories or specific tests to run rather than running the entire test suite:
```bash
azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> pytest
azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> pytest <test_file.py>
```

In addition you can provide keywords to run specific tests within the suite or within a specific file
```bash
azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> pytest -k <keyword>
azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> pytest <test_file.py> -k <keyword>
```

The implementation tutorial is already configured according to the [Template SDK Directory](https://github.com/Azure/azure-sdk-for-python/tree/training/sdk/api-learn/implementation-tutorial) and therefore already has a test directory ready for us to work with.

## Tox
The Python SDK uses the [tox project](https://tox.readthedocs.io/en/latest/) to automate releases, run tests, run linters, and build our documentation. The `tox.ini` file is located at `azure-sdk-for-python/eng/tox/tox.ini` for reference. You do not need to make any changes to the tox file for tox to work with the `app-config` project. Tox will create a directory (`.tox`) in the head of your branch. The first time you run tox commands it may take several moments, but subsequent runs will be quicker. To install tox run the following command from within your virtual environment.
`(env) > pip install tox tox-monorepo`.

To run a tox command from your directory use the following commands:
```bash
azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> tox -c ../../../eng/tox/tox.ini -e sphinx
azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> tox -c ../../../eng/tox/tox.ini -e lint
azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> tox -c ../../../eng/tox/tox.ini -e mypy
azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> tox -c ../../../eng/tox/tox.ini -e whl
azure-sdk-for-python\sdk\api-learn\azure-learnappconfig> tox -c ../../../eng/tox/tox.ini -e sdist
```
A quick description of the five commands above:
* sphinx: documentation generation using the inline comments written in our code
* lint: runs pylint to make sure our code adheres to the style guidance
* mypy: runs the mypy static type checker for Python to make sure that our types are valid
* whl: creates a whl package for installing our package
* sdist: creates a zipped distribution of our files that the end user could install with pip

## `devtools_testutils` Package
The Azure SDK team has created some in house tools to help with easier testing. These additional tools are located in the `devtools_testutils` package that was installed with your `dev_requirements.txt`. In this package are the preparers that will be commonly used throughout the repository to test various resources. A preparer is a way to programmatically create fresh resources to run our tests against and then deleting them after running a test suite. These are helpful to help guarantee standardized behavior by starting each test group from a fresh resource and account. For more information on writing and building preparers following this tutorial on how to create the [app-configuration account preparer](https://github.com/Azure/azure-sdk-pr/issues/458).

Also in this package is the `AzureTestCase` object which every test case object should inherit from. This management object takes care of creating and scrubbing recordings to make sure secrets are not added to the recordings files (and subsequently to the git history) and authenticating clients for test methods.

## Writing New Tests
SDK tests are based on the `scenario_tests` subpackage located in [`azure-sdk-for-python/tools/azure-devtools/src/azure_devtools`](https://pypi.org/project/azure-devtools/). `scenario_tests` is a general, mostly abstracted framework which provides several useful features for writing SDK tests, ie:
* HTTP interaction recording and playback using [vcrpy](https://pypi.python.org/pypi/vcrpy)
* Creation and cleanup of helper resources, such as resource groups, storage accounts, etc. which can be used in order to test services
* Processors for modifying requests and responses when writing or reading recordings (for example, to to avoid recording credential information)
* Patches for overriding functions and methods that don't work well with testing frameworks (such as long-running operations)

Code in the [`azure-sdk-tools/devtools_testutils`](https://github.com/Azure/azure-sdk-for-python/tree/master/tools/azure-sdk-tools/devtools_testutils) directory provides concrete implementations of the features provided in `scenario_tests` that are oriented around use in SDK testing and that you can use directly in your unit tests.

## Define credentials
When you run tests in playback mode, they use a fake credentials file, located at `tools/azure-sdk-tools/devtools_testutils/mgmt_settings_real.py` to simulate authenticating with Azure. The test framework uses the values stored in the `mgmt_settings_real.py` to take care of authenticating clients for you.

In live mode, the credentials need to be real so that we can actually connect to the service. Copy the `mgmt_settings_fake.py` file to a new file named `mgmt_settings_real.py` within the same directory. Then make the following changes:
1. Change the value of the `SUBSCRIPTION_ID` variable to your organizations subscription ID. (If you don't have it, you can find it in the "Overview" section of the "Subscriptions" blade in the [Azure portal](https://portal.azure.com/).)
2. Create a `.env` file at the root of the repository (in the same directory as the `sdk`, `tools`, `eng` folders). In this file you can define any environment variables you need for a test and that will be loaded by the `AzureTestCase` file. Start by defining `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` which are available after creating a Service Principal or can be retrieved from the Azure Portal if you have already created a Service Principal.
3. Change the `get_azure_core_credentials(**kwargs):` function to construct and return a `ClientSecretCredential` object. The `client_id`, `client_secret`, `tenant_id` are provided when you create a service principal. These values can be found in the Azure Portal The `mgmt_settings_real.py` file should look like this:
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


## Create Live Test Resources
The Azure Python SDK library has two ways of providing live resources to our tests:
* Using an individualized preparer
    * [Storage preparer](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/storage_testcase.py)
    * [In line use](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/storage/azure-storage-blob/tests/test_blob_client.py#L49-L61) for the blob client
* Using an ArmTemplate and the PowerShellPreparer (we will show the latter)
    * [PowerShell preparer](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/powershell_preparer.py)
    * [In line use](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/schemaregistry/azure-schemaregistry/tests/test_schema_registry.py#L30-L39) for the schemaregistry library

If your library has a management plane library, you can build a preparer specific to your service using the storage preparer as an example. It is recommended that you use a PowerShellPreparer for new libraries and those without management plane libraries. The `PowerShellPreparer` uses the `New-TestResources.ps1` script to deploy resources using an ARM Template.

1. Create an Azure Resource Management Template for your specific service and the configuration you need. This can be done in the portal by creating the resources and at the very last step (Review + create) clicking "Download a template for automation". This template should be saved in a file named `test-resources.json` under the directory that contains your library (`sdk/<my_library>/test-resources.json`).
2. Use the [`New-TestResources.ps1`](https://github.com/Azure/azure-sdk-for-python/tree/master/eng/common/TestResources#on-the-desktop) script to deploy those resources.
3. Set the environment variables returned from step 2 in your current shell or create a `.env` file at the root of the repo to hold these secrets. If you choose the latter method, you will have to make sure all the key-value pairs are in the format `<key_name>=<value>`, free of quotations and the `${env:<key_name>} = '<value>'` formatting used in PowerShell. The names of the environment variables should be in the pattern `<LIBRARY>_...`, ie. `TABLES_PRIMARY_KEY`, `FORMRECOGNIZER_ACCOUNT_URL`, `EVENTHUBS_SECRET_KEY`.
4. Create a partial implementation of the PowerShellPreparer to pass in your specific environment variables. An example implementation is shown below for schemaregistry

```python
import functools
from devtools_testutils import PowerShellPreparer

MyServicePreparer = functool.partial(
    PowerShellPreparer, "<my_service_directory>",
    schemaregistry_endpoint="fake_resource.servicebus.windows.net",
    schemaregistry_group="fakegroup"
)
```

The parameters for the functool are:
* The `PowerShellPreparer` class
* The library folder that holds your code (ie. `sdk/schemaregistry`). This value is used to search your environment variables.
* The keys that you need returned from your environment variables and a fake value for replacing the actual value in the recordings.

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
    * Building your preparer is simple, you'll use the `functools.partial` method to do so. The arguments are in the following order:
        1. `PowerShellPreparer` class
        2. The directory that you are building your library from. In our schemaregistry example, it's just `schemaregistry`.
        3. The remaining arguments are going to be key-value kwargs. The key is going to be any environment variable that you need for your tests, spelled exactly the same as it is in the environment variable. The value is a **fake** value to replace your real value in the recording. The fake value should be a close copy of the real value and a unique value to the other key-value pairs.
* At the top of your test class you should include any helper methods you will need. Most libraries will have a client creation method to eliminate repetitive code.
* Following your helper methods will be your actual tests. All test methods must start with "test". The preparer built at the top of the file should decorate your test in the fashion: `@MyPreparer()`.
    * The signature of your test will always contain `self`, and following self will be all the keys that you need from your preparer. A test does not need to have every key passed into it, the test framework will take care of passing in only the parameters specifically requested in the test signature.

If you need logging functionality for your testing, pytest also offers [logging](https://docs.pytest.org/en/stable/logging.html) capabilities either inline through the `caplog` fixture or with command line flags.

## An example test
An example test for schemaregistry looks like:
```python
class AppConfigTestCase(AzureTestCase):

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

The test infrastructure heavily leverages the `assert` keyword, which tests if the condition following it is true, and if it is not the program will raise an `AssertionError`. When writing tests, any uncaught exception results in a failure, from an assert or from the code itself (ie. `TypeError`, `ValueError`, `HttpResponseError`, etc.). The assert statements are testing that all the exected properties of the returned object are not `None`, and the last two assert statements verify that the tested properties are a given value. The last two lines of the test use a [context manager](https://docs.python.org/3/library/contextlib.html) used from the `pytest` library that tests whether the following block of code will raise a certain exception. The context manager represents the following code block:

## Run and record the test

From your terminal run the `pytest` command to run all the tests that you have written so far.

```bash
(env)azure-sdk-for-python\sdk\api-learn\implementation-tutorial> pytest
```

Your update should run smooth and have 4 passing tests. Now if you look at the contents of your `tests` directory there should be a new directory called `recording` with four `.yaml` files. Each `yaml` file is a recording for a single test. To run a test in playback mode change the `testsettings_local.cfg` to `live-mode: false` and rerun the tests with the same command. The test infrastructure will use the `.yaml` recordings to mock the HTTP traffic and run the tests.

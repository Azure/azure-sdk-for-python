# Python SDK testing guide

This guide walks through the setup necessary to run tests in the Azure SDK for Python, gives an overview of the shared
testing infrastructure, and demonstrates how to write and run tests for a service.

### Table of contents

- [Python SDK testing guide](#python-sdk-testing-guide)
        - [Table of contents](#table-of-contents)
    - [Set up your development environment](#set-up-your-development-environment)
        - [SDK root directory](#sdk-root-directory)
        - [Dependency installation](#dependency-installation)
        - [Open code in IDE](#open-code-in-ide)
    - [Integrate with the pytest test framework](#integrate-with-the-pytest-test-framework)
    - [Tox](#tox)
    - [The `devtools_testutils` package](#the-devtools_testutils-package)
    - [Write or run tests](#write-or-run-tests)
        - [Perform one-time test proxy setup](#perform-one-time-test-proxy-setup)
        - [Set up test resources](#set-up-test-resources)
        - [Configure credentials](#configure-credentials)
        - [Start the test proxy server](#start-the-test-proxy-server)
        - [Deliver environment variables to tests](#deliver-environment-variables-to-tests)
        - [Write your tests](#write-your-tests)
        - [Configure live or playback testing mode](#configure-live-or-playback-testing-mode)
        - [Run and record tests](#run-and-record-tests)
        - [Run tests with out-of-repo recordings](#run-tests-with-out-of-repo-recordings)
        - [Sanitize secrets](#sanitize-secrets)
            - [Special case: SAS tokens](#special-case-sas-tokens)
    - [Functional vs. unit tests](#functional-vs-unit-tests)
    - [Further reading](#further-reading)
    - [Deprecated testing instructions](#deprecated-testing-instructions)
        - [Define credentials (deprecated)](#define-credentials-deprecated)
        - [Create live test resources (deprecated)](#create-live-test-resources-deprecated)
        - [Write your tests (deprecated)](#write-your-tests-deprecated)
        - [An example test (deprecated)](#an-example-test-deprecated)
        - [Run and record the test (deprecated)](#run-and-record-the-test-deprecated)
        - [Purging secrets (deprecated)](#purging-secrets-deprecated)
            - [Special case: Shared Access Signature (deprecated)](#special-case-shared-access-signature-deprecated)

## Set up your development environment

The Azure SDK Python team creates libraries that are compatible with Python 3.6 and up. We walk through setting up a
Python virtual environment for Python 3.6, but having a virtual environment for each minor version can make it
easier to debug PRs locally.

* Python 3.7+: Use the [python website](https://www.python.org/downloads/) or the one-click experience from the Windows store ([3.7](https://www.microsoft.com/p/python-37/9nj46sx7x90p), [3.8](https://www.microsoft.com/p/python-38/9mssztt1n39l), [3.9](https://www.microsoft.com/p/python-39/9p7qfqmjrfp7), [3.10](https://www.microsoft.com/p/python-310/9pjpw5ldxlz5)) (Windows only).
* Python 3.6: Use the [python website](https://www.python.org/downloads/release/python-3614/)
```cmd
C:\Users> python -m venv env
C:\Users> env\scripts\activate       # PowerShell only
C:\Users> source env\bin\activate    # Linux shell (Bash, ZSH, etc.) only
C:\Users> env\scripts\activate.bat   # Windows CMD only
(env) C:\Users>
```
To create virtual environment for different versions of Python use the `-p` flag to pass the specific Python executable you want to use
```cmd
C:\Users> python -m venv -p <path/to/Python/Python36/python.exe> py36_venv
```

### SDK root directory

In the root directory of our SDK, a number of mandatory files have been added. When creating your own SDK, these files can be copied from the [`sdk/template`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/template) project, and modified to your needs.

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

```
(env) azure-sdk-for-python\sdk\my-service\my-package> pip install -r dev_requirements.txt
```
Next we will install our Python SDK to the virtual environment as an 'editable install' - this means that as we work on the implementation, we will be able to run the package as it develops, as opposed to having to periodically rebuild and reinstall.
```
(env) azure-sdk-for-python\sdk\my-service\my-package> pip install -e .
```

We should now be able to open an interactive Python terminal, and execute code from our new SDK
```
(env) azure-sdk-for-python\sdk\my-service\my-package> python

>>> import azure.my_package
>>> print(azure.my_package.__version__)
0.0.1
```

### Open code in IDE

Open the directory for your package in your preferred editor, for example VSCode.
```cmd
(env) azure-sdk-for-python\sdk\my-service\my-package> code .
```

## Integrate with the pytest test framework

As a quick background, the Azure SDK uses the [pytest](https://docs.pytest.org/en/latest/) test runner to support creating unit and functional tests for Track 2 Azure libraries. To intall `pytest` run `pip install pytest` from your virtual environment, you can confirm the installation was successful by running `pytest -V`. The commands will run all files of the form `test_*.py` or `*_test.py` in the provided directory and its subdirectories; for more information check out the [docs][pytest_invocation].

With `pytest` you can provide a either a directory or a specific test file to run:
```cmd
(env) azure-sdk-for-python\sdk\my-service\my-package> pytest tests
(env) azure-sdk-for-python\sdk\my-service\my-package> pytest tests\<test_file.py>
```

In addition you can provide keywords to run specific tests within the suite or within a specific file:
```cmd
(env) azure-sdk-for-python\sdk\my-service\my-package> pytest tests -k <keyword>
(env) azure-sdk-for-python\sdk\my-service\my-package> pytest <test_file.py> -k <keyword>
```

If you have print statements in your tests for debugging you can add the `-s` flag to send those print statements to standard output:
```cmd
(env) azure-sdk-for-python\sdk\my-service\my-package> pytest <test_file.py> -s
```

## Tox

The Python SDK uses the [tox project](https://tox.readthedocs.io/en/latest/) to automate releases, run tests, run linters, and build our documentation. The `tox.ini` file is located at `azure-sdk-for-python/eng/tox/tox.ini` for reference. You do not need to make any changes to the tox file for tox to work with your project. Tox will create a directory (`.tox`) in the head of your branch. The first time you run tox commands it may take several moments, but subsequent runs will be quicker. To install tox run the following command from within your virtual environment.
`(env) > pip install tox tox-monorepo`.

To run a tox command from your directory use the following commands:
```cmd
(env) azure-sdk-for-python\sdk\my-service\my-package> tox -c ../../../eng/tox/tox.ini -e sphinx
(env) azure-sdk-for-python\sdk\my-service\my-package> tox -c ../../../eng/tox/tox.ini -e pylint
(env) azure-sdk-for-python\sdk\my-service\my-package> tox -c ../../../eng/tox/tox.ini -e mypy
(env) azure-sdk-for-python\sdk\my-service\my-package> tox -c ../../../eng/tox/tox.ini -e pyright
(env) azure-sdk-for-python\sdk\my-service\my-package> tox -c ../../../eng/tox/tox.ini -e verifytypes
(env) azure-sdk-for-python\sdk\my-service\my-package> tox -c ../../../eng/tox/tox.ini -e whl
(env) azure-sdk-for-python\sdk\my-service\my-package> tox -c ../../../eng/tox/tox.ini -e sdist
(env) azure-sdk-for-python\sdk\my-service\my-package> tox -c ../../../eng/tox/tox.ini -e samples
(env) azure-sdk-for-python\sdk\my-service\my-package> tox -c ../../../eng/tox/tox.ini -e apistub
```
A quick description of the five commands above:
* sphinx: documentation generation using the inline comments written in our code
* lint: runs pylint to make sure our code adheres to the style guidance
* mypy: runs the mypy static type checker for Python to make sure that our types are valid.
* pyright: runs the pyright static type checker for Python to make sure that our types are valid.
* verifytypes: runs pyright's verifytypes tool to verify the type completeness of the library.
* whl: creates a whl package for installing our package
* sdist: creates a zipped distribution of our files that the end user could install with pip
* samples: runs all of the samples in the `samples` directory and verifies they are working correctly
* apistub: runs the [apistubgenerator](https://github.com/Azure/azure-sdk-tools/tree/main/packages/python-packages/apiview-stub-generator) tool on your code

## The `devtools_testutils` package

The Azure SDK team has created some in house tools to make testing easier. These additional tools are located in the
`devtools_testutils` package that was installed with your `dev_requirements.txt`. In this package is the
[AzureRecordedTestCase][azure_recorded_test_case] class that every service test class should inherit from.
AzureRecordedTestCase provides a number of utility functions for authenticating clients during tests, naming test
resources, and sanitizing credentials in recordings.

The `devtools_testutils` package also has other classes and functions to provide test utility, which are documented in
the
[package README](https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/README.md).

## Write or run tests

Newer SDK tests utilize the [Azure SDK Tools Test Proxy][proxy_general_docs] to record and playback HTTP interactions.
To migrate an existing test suite to use the test proxy, or to learn more about using the test proxy, refer to the
[test proxy migration guide][proxy_migration_guide].

### Perform one-time test proxy setup

The test proxy uses a self-signed certificate to communicate with HTTPS. Follow the general setup instructions [here][proxy_cert_docs] to trust this certificate locally.

### Set up test resources

Live Azure resources will be necessary in order to run live tests and produce recordings. There are PowerShell test
resource management commands, documented in [/eng/common/TestResources][test_resources], that streamline this process.
Both pure ARM templates (`test-resources.json`) and BICEP files (`test-resources.bicep`) are supported.

If you haven't yet set up a `test-resources` file for test resource deployment and/or want to use test resources of
your own, you can just configure credentials to target these resources instead.

To create a `test-resources` file:
1. Create an Azure Resource Management Template for your specific service and the configuration you need. This can be
done in the [Portal][azure_portal] by creating a resource, and at the very last step (Review + Create), clicking
"Download a template for automation".
2. Save this template to a `test-resources.json` file under the directory that contains your package
(`sdk/<my-service>/test-resources.json`) or create a `test-resources.bicep` file. You can refer to
[Key Vault's][kv_test_resources] as an example.
3. Add templates for any additional resources in a grouped `"resources"` section of `test-resources`
([example][kv_test_resources_resources]).
4. Add an `"outputs"` section to `test-resources` that describes any environment variables necessary for accessing
these resources ([example][kv_test_resources_outputs]).

### Configure credentials

Python SDK tests use a `.env` file to store test credentials. This `.env` file should be placed at either the root of
`azure-sdk-for-python` in your local file system, or in the directory containing the repo. The `python-dotenv` package
is used to read this file -- documentation of the package and how to format a `.env` file can be found in the
[package's README][python-dotenv_readme].

If using a `New-TestResources` script from [/eng/common/TestResources][test_resources], the script should output any
environment variables necessary to run live tests for the service. After storing these variables in your `.env` file
-- with appropriate formatting -- your credentials and test configuration variables will be set in your environment when
running tests.

If your service doesn't have a `test-resources` file for test deployment, you'll need to set environment variables
for `AZURE_SUBSCRIPTION_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` at minimum.

1. Set the `AZURE_SUBSCRIPTION_ID` variable to your organization's subscription ID. You can find it in the "Overview"
section of the "Subscriptions" blade in the [Azure Portal][azure_portal].
2. Define the `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` of a test service principal. If you do not
have a service principal, use the Azure CLI's [az ad sp create-for-rbac][azure_cli_service_principal] command (ideally,
using your alias as the service principal's name prefix):
```
az login
az ad sp create-for-rbac --name "{your alias}-tests" --role Contributor
```

The command will output a set of credentials. Set `AZURE_TENANT_ID` to the value of `"tenant"`, `AZURE_CLIENT_ID` to the
value of `"appId"`, and `AZURE_CLIENT_SECRET` to the value of `"password"`.

### Start the test proxy server

The test proxy has to be available in order for tests to work; this is done automatically with a `pytest` fixture.

Create a `conftest.py` file within your package's test directory (`sdk/{service}/{package}/tests`), and inside it add a
session-level fixture that accepts `devtools_testutils.test_proxy` as a parameter (and has `autouse` set to `True`):

```python
import pytest
from devtools_testutils import test_proxy

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return
```

For more details about how this fixture starts up the test proxy, or the test proxy itself, refer to the
[test proxy migration guide][test_proxy_startup].

### Deliver environment variables to tests

To target the correct resources in tests, use the [EnvironmentVariableLoader][env_var_loader] from `devtools_testutils`
to fetch environment variables and provide them to tests. The EnvironmentVariableLoader is meant to decorate test
methods and inject environment variables particular to a given service. Below is an example of how to create a custom
decorator, using the EnvironmentVariableLoader, that provides the values of environment variables `TESTSERVICE_ENDPOINT`
and `TESTSERVICE_SECRET` to tests for a service called "testservice":

```python
import functools
from devtools_testutils import EnvironmentVariableLoader

ServicePreparer = functools.partial(
    EnvironmentVariableLoader,
    "testservice",
    testservice_endpoint="https://fake_endpoint.testservice.windows.net",
    testservice_secret="fakesecret"
)
```

The parameters for the `functools.partial` method are:

- The EnvironmentVariableLoader class
- The service folder that holds your code (in this example, `sdk/testservice`). This value is used to search your
  environment variables for the appropriate values.
- The remaining arguments are key-value kwargs, with the keys being the environment variables needed for the tests, and
  the value being a fake value to use in recordings.
  - These values should have the same formatting as the real values because they are used in playback mode and will need
  to pass any client side validation. The fake value should also be a unique value to the other key-value pairs.

A method that's decorated by the ServicePreparer from the example would be called with `testservice_endpoint` and
`testservice_secret` as keyword arguments. These arguments use the real values from your `.env` file as the variable
values in live mode, and the fake values specified in the decorator in playback mode.

> **Note:** The EnvironmentVariableLoader expects environment variables for service tests to be prefixed with the
> service name (e.g. `KEYVAULT_` for Key Vault tests). You'll need to set environment variables for
> `{SERVICE}_TENANT_ID`, `{SERVICE}_CLIENT_ID`, and `{SERVICE}_CLIENT_SECRET` for a service principal when using this
> class.

### Write your tests

In your package's `tests` directory (`sdk/{service}/{package}/tests`), create a file with the naming pattern
`test_<what_you_are_testing>.py`. The base of each testing file will be roughly the same (in this example we use Schema
Registry for the sake of demonstration):

```python
import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

from azure.schemaregistry import SchemaRegistryClient

SchemaRegistryPreparer = functools.partial(
    EnvironmentVariableLoader,
    'schemaregistry',
    schemaregistry_endpoint="https://fake_resource.servicebus.windows.net",
    schemaregistry_group="fakegroup",
)

# The test class name needs to start with "Test" to get collected by pytest
class TestSchemaRegistry(AzureRecordedTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_schemareg_client(self, endpoint):
        credential = self.get_credential(SchemaRegistryClient)
        client = self.create_client_from_credential(SchemaRegistryClient, credential=credential, endpoint=endpoint)
        return client

    ...

    # Write your test cases, each starting with "test_":
    @SchemaRegistryPreparer()
    @recorded_by_proxy
    def test_client_creation(self, schemaregistry_endpoint):
        client = self.create_schemareg_client(schemaregistry_endpoint)
        assert client is not None

```

There's a lot going on in the example, so we'll take this piece by piece:

* Import everything you will need in your tests, and include the line `from devtools_testutils import
AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy`.
  * AzureRecordedTestCase was touched on in the [`devtools_testutils` package](#the-devtoolstestutils-package) section,
  and EnvironmentVariableLoader was touched on in the
  [Deliver environment variables to tests](#deliver-environment-variables-to-tests) section.
  * `recorded_by_proxy` is a decorator that must be used directly on top of recorded test methods in order to
  produce recordings. Unit tests, which aren't recorded, don't need to use this decorator. Unit tests are discussed in
  [Functional vs. unit tests](#functional-vs-unit-tests).
* Include any helper methods you will need at the top of your test class. Most libraries will have a client creation
  method to eliminate repetitive code.
* Following your helper methods will be your actual tests. All test method names must start with "test_". The preparer
  defined at the top of the file should decorate your test in the fashion: `@MyPreparer()`.
  * The signature of your test method will always contain `self`, and following `self` will be all the keys that you
  need from your preparer. A test does not need to accept every key from the preparer; the test framework will only pass
  in the parameters specifically requested in the test method signature.
* Within tests, use the `assert` keyword to assert conditions that you expect to be true.

If you need logging functionality for your testing, pytest also offers [logging][pytest_logging] capabilities either
inline through the `caplog` fixture or with command line flags.

### Configure live or playback testing mode

"Live" tests refer to tests that make requests to actual Azure resources. "Playback" tests require a recording for each
test; the test proxy will compare the requests/responses that would be made during each test with requests/responses in
the recording.

To run live tests, set the environment variable `AZURE_TEST_RUN_LIVE` to "true" in your environment or `.env` file.
Live test runs will produce recordings unless the environment variable `AZURE_SKIP_LIVE_RECORDING` is set to "true" as
well. To run tests in playback, either set `AZURE_TEST_RUN_LIVE` to "false" or leave it unset.

### Run and record tests

With the `AZURE_TEST_RUN_LIVE` environment variable set to "true", use `pytest` to run your test(s) in live mode.

```
(env) azure-sdk-for-python\sdk\my-service\my-package> pytest tests
```

After tests finish running, there should folder called `recordings` inside your package's `tests` directory. Each
recording in this folder will be a `.json` file that captures the HTTP traffic that was generated while running the test
matching the file's name. If you set the `AZURE_TEST_RUN_LIVE` environment variable to "false" and re-run tests, they
should pass again -- this time, in playback mode (i.e. without making actual HTTP requests).

### Run tests with out-of-repo recordings

If the package being tested stores its recordings outside the `azure-sdk-for-python` repository -- i.e. the
[recording migration guide][recording_move] has been followed and the package contains an `assets.json` file -- there
won't be a `recordings` folder in the `tests` directory. Instead, the package's `assets.json` file will point to a tag
in the `azure-sdk-assets` repository that contains the recordings. This is the preferred recording configuration.

Running live or playback tests is the same in this configuration as it was in the previous section. The only changes are
to the process of updating recordings.

#### Update test recordings

##### Environment prerequisites

- The targeted library is already migrated to use the test proxy.
- Git version > 2.30.0 is to on the machine and in the path. Git is used by the script and test proxy.
- Global [git config settings][git_setup] are configured for `user.name` and `user.email`.
  - These settings are also set with environment variables `GIT_COMMIT_OWNER` and `GIT_COMMIT_EMAIL`, respectively (in your environment or your local `.env` file).
- Membership in the `azure-sdk-write` GitHub group.

Test recordings will be updated if tests are run while `AZURE_TEST_RUN_LIVE` is set to "true" and
`AZURE_SKIP_LIVE_RECORDING` is unset or "false". Since the recordings themselves are no longer in the
`azure-sdk-for-python` repo, though, these updates will be reflected in a git-excluded `.assets` folder at the root of
the repo.

The `.assets` folder contains one or more directories with random names, which each are a git directory containing
recordings. If you `cd` into the folder containing your package's recordings, you can use `git status` to view the
recording updates you've made. You can also use other `git` commands; for example, `git diff {file name}` to see
specific file changes, or `git restore {file name}` to undo changes you don't want to keep.

To find the directory containing your package's recordings, open the `.breadcrumb` file in the `.assets` folder. This
file lists a package name on each line, followed by the recording directory name; for example:
```
sdk/{service}/{package}/assets.json;2Km2Z8755;python/{service}/{package}_<10-character-commit-SHA>
```
The recording directory in this case is `2Km2Z8755`, the string between the two semicolons.

After verifying that your recording updates look correct, you can use the [`manage_recordings.py`][manage_recordings]
script from `azure-sdk-for-python/scripts` to push these recordings to the `azure-sdk-assets` repo. This script accepts
a verb and a **relative** path to your package's `assets.json` file (this path is optional, and simply `assets.json`
by default). For example, from the root of the `azure-sdk-for-python` repo:
```
python scripts/manage_recordings.py push -p sdk/{service}/{package}/assets.json
```

The verbs that can be provided to this script are "push", "restore", and "reset":
- **push**: pushes recording updates to a new assets repo tag and updates the tag pointer in `assets.json`.
- **restore**: fetches recordings from the assets repo, based on the tag pointer in `assets.json`.
- **reset**: discards any pending changes to recordings, based on the tag pointer in `assets.json`.

After pushing your recordings, the `assets.json` file for your package will be updated to point to a new `Tag` that
contains the updates. Include this `assets.json` update in any pull request to update the recordings pointer in the
upstream repo.

More details about the recording management commands and management script are documented in
[`manage_recordings.py`][manage_recordings].

### Sanitize secrets

The `.json` files created from running tests in live mode can include authorization details, account names, shared
access signatures, and other secrets. The recordings are included in our public GitHub repository, making it important
for us to remove any secrets from these recordings before committing them to the repository.

There are two primary ways to keep secrets from being written into recordings:

1. The `EnvironmentVariableLoader` will automatically sanitize the values of captured environment variables with the
  provided fake values.
2. Sanitizers can be registered via `add_*_sanitizer` methods in `devtools_testutils`. For example, the general-use
  method for sanitizing recording bodies, headers, and URIs is `add_general_string_sanitizer`. Other sanitizers are
  available for more specific scenarios and can be found at [devtools_testutils/sanitizers.py][py_sanitizers].

As a simple example of registering a sanitizer, you can provide the exact value you want to sanitize from recordings as
the `target` in the general string sanitizer. To replace all instances of the string "my-key-vault" with "fake-vault" in
recordings, you could add something like the following in the package's `conftest.py` file:

```python
from devtools_testutils import add_general_string_sanitizer, test_proxy

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_general_string_sanitizer(target="my-key-vault", value="fake-vault")
```

Note that the sanitizer fixture accepts the `test_proxy` fixture as a parameter to ensure the proxy is started
beforehand (see [Start the test proxy server](#start-the-test-proxy-server)).

For a more advanced scenario, where we want to sanitize the account names of all storage endpoints in recordings, we
could instead use `add_general_regex_sanitizer`:

```python
add_general_regex_sanitizer(
    regex="(?<=\\/\\/)[a-z]+(?=(?:|-secondary)\\.(?:table|blob|queue)\\.core\\.windows\\.net)",
    value="fakeendpoint",
)
```

`add_general_regex_sanitizer` accepts a regex, replacement value, and capture group as keyword-only arguments. In the
snippet above, any storage endpoint URIs that match the specified URI regex will have their account name replaced with
"fakeendpoint". A request made to `https://tableaccount-secondary.table.core.windows.net` will be recorded as being
made to `https://fakeendpoint-secondary.table.core.windows.net`, and URIs will also be sanitized in bodies and headers.

For more details about sanitizers and their options, please refer to [devtools_testutils/sanitizers.py][py_sanitizers].

#### Special case: SAS tokens

Tests that use a Shared Access Signature (SAS) token to authenticate a client should use the
[`AzureRecordedTestCase.generate_sas`][generate_sas] method to generate the token. This will automatically register a
sanitizer to keep this token out of test recordings. An example of using this method can be found
[here][generate_sas_example].

`generate_sas` accepts any number of positional arguments: the first being the method that creates the SAS, and the
remaining positional arguments being positional arguments for the SAS-generating method. Any keyword arguments given to
`generate_sas` will be passed to the SAS-generating method as well. The generated token will be returned and its value
will be sanitized.

## Functional vs. unit tests

The tests written above are functional tests: they generate HTTP traffic and send data to the service. For tests that
don't need to make HTTP requests -- i.e. unit tests -- the best practice is to have a separate test class from the one
containing functional tests. For example, the `azure-data-tables` package has client-side validation for the table name
and properties of the entity; below is an example of how these could be tested:

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


## Further reading

For information about more advanced testing scenarios, refer to the [advanced tests notes][advanced_tests_notes].


## Deprecated testing instructions

> The testing framework described in this section was used before today's test proxy was adopted. These instructions are
> deprecated and shouldn't be used to write new tests, but may be helpful in understanding and working with test suites
> that haven't migrated to the new system.

Older SDK tests are based on the `scenario_tests` subpackage located in [`azure-sdk-for-python/tools/azure-devtools/src/azure_devtools`](https://pypi.org/project/azure-devtools/). `scenario_tests` is a general, mostly abstracted framework which provides several useful features for writing SDK tests, ie:
* HTTP interaction recording and playback using [vcrpy](https://pypi.python.org/pypi/vcrpy)
* Creation and cleanup of helper resources, such as resource groups, storage accounts, etc. which can be used in order to test services
* Processors for modifying requests and responses when writing or reading recordings (for example, to to avoid recording credential information)
* Patches for overriding functions and methods that don't work well with testing frameworks (such as long-running operations)

Older tests that used `vcrpy` for recording relied on the
[`AzureTestCase`](https://github.com/Azure/azure-sdk-for-python/blob/c4cbcee52fbe486472c6b28af68f751dd3e2d016/tools/azure-sdk-tools/devtools_testutils/azure_testcase.py#L104)
class, which was a precursor to today's `AzureRecordedTestCase`.

Code in the [`azure-sdk-tools/devtools_testutils`](https://github.com/Azure/azure-sdk-for-python/tree/main/tools/azure-sdk-tools/devtools_testutils) directory provides concrete implementations of the features provided in `scenario_tests` that are oriented around use in SDK testing and that you can use directly in your unit tests.

### Define credentials (deprecated)

When you run tests in playback mode, they use a fake credentials file, located at [`tools/azure-sdk-tools/devtools_testutils/mgmt_settings_fake.py`][mgmt_settings_fake] to simulate authenticating with Azure.

In live mode, the credentials need to be real so that the tests are able to connect to the service. Create a `.env` file at the root of the repository (in the same directory as the `sdk`, `tools`, `eng` folders). In this file you can define any environment variables you need for a test and that will be loaded by the `AzureTestCase` file.
1. Add the `SUBSCRIPTION_ID` variable with your organizations subscription ID. If you don't have it, you can find it in the "Overview" section of the "Subscriptions" blade in the [Azure portal](https://portal.azure.com/).
2. Define the `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` which are available after creating a Service Principal or can be retrieved from the Azure Portal if you have already created a Service Principal. If you do not have a Service Principal, check out the [Azure docs](https://docs.microsoft.com/cli/azure/ad/sp?view=azure-cli-latest#az_ad_sp_create_for_rbac) on a simple one line command to create one. The recommended practice is to include your alias or name in the Service Principal name.
    Your `.env` file stores secrets in plain text so it is important that the contents of this file are not committed to the git repository.
3. Create the `tools/azure-sdk-tools/devtools_testutils/testsettings_local.cfg` file and copy and paste the following line:
```
live-mode: true
```

### Create live test resources (deprecated)

The Azure Python SDK library has two ways of providing live resources to our tests:
* Using an ArmTemplate and the EnvironmentVariableLoader (we will demonstrate this one)
    * [EnvironmentVariableLoader implementation](https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/envvariable_loader.py)
    * [In line use](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/schemaregistry/azure-schemaregistry/tests/test_schema_registry.py#L30-L39) for the schemaregistry library
* Using an individualized preparer such as the storage preparer
    * [Storage preparer implementation](https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/storage_testcase.py)
    * [In line use](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-storage-blob/tests/test_blob_client.py#L49-L61) for the blob client

If your library has a management plane library, you can build a preparer specific to your service using the storage preparer as an example. It is recommended that you use a EnvironmentVariableLoader for new libraries and those without management plane libraries. The `EnvironmentVariableLoader` is compatible with the `New-TestResources.ps1` script to deploy resources using an ARM Template. This script and information about running it can be found in the [`eng/common/TestResources`][test_resources] directory. For more information about the engineering systems in Azure SDK, check out their [wiki][engsys_wiki]

1. Create an Azure Resource Management Template for your specific service and the configuration you need. This can be done in the portal by creating the resources and at the very last step (Review + Create) clicking "Download a template for automation". Save this template to a `test-resources.json` file under the directory that contains your library (`sdk/<my-library>/test-resources.json`).
2. Use the [`New-TestResources.ps1`](https://github.com/Azure/azure-sdk-for-python/tree/main/eng/common/TestResources#on-the-desktop) script to deploy those resources.
3. Set the environment variables returned from step 2 in your current shell or add them to your `.env` file at the root of the repo to save these secrets. If you choose the latter method, you will have to make sure all the key-value pairs are in the format `<key_name>=<value>`, rather than the  `${env:<key_name>} = '<value>'` formatting used in PowerShell. The names of the environment variables should be in all capital letters, snake case, and be prefixed with the library name. Ie. `TABLES_PRIMARY_KEY`, `FORMRECOGNIZER_ACCOUNT_URL`, `EVENTHUBS_SECRET_KEY`. If the name of the service is more than one word, like Form Recognizer, don't include an underscore between the words. Use `FORMRECOGNIZER_ACCOUNT_URL`, not `FORM_RECOGNIZER_ACCOUNT_URL`.
4. Create a partial implementation of the EnvironmentVariableLoader to pass in your specific environment variables. An example implementation is shown below for schemaregistry

```python
import functools
from devtools_testutils import EnvironmentVariableLoader

MyServicePreparer = functools.partial(
    EnvironmentVariableLoader, "<my_service_directory>",
    schemaregistry_endpoint="fake_resource.servicebus.windows.net/",
    schemaregistry_group="fakegroup"
)
```

The parameters for the `functools.partial` method are:
* The `EnvironmentVariableLoader` class
* The library folder that holds your code (ie. `sdk/schemaregistry`). This value is used to search your environment variables for the appropriate values.
* The remaining arguments are key-value kwargs, with the keys being the environment variables needed for the tests, and the value being a fake value for replacing the actual value in the recordings. The fake value in this implementation will replace the real value in the recording to make sure the secret keys are not committed to the recordings. These values should closely resemble the values because they are used in playback mode and will need to pass any client side validation. The fake value should also be a unique value to the other key-value pairs.

### Write your tests (deprecated)

In the `tests` directory create a file with the naming pattern `test_<what_you_are_testing>.py`. The base of each testing file will be roughly the same:

```python
import functools
import pytest

from devtools_testutils import AzureTestCase, EnvironmentVariableLoader

from azure.schemaregistry import SchemaRegistryClient

SchemaRegistryPreparer = functools.partial(
    EnvironmentVariableLoader, 'schemaregistry',
    schemaregistry_endpoint="fake_resource.servicebus.windows.net/",
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

* Import everything you will need in your tests as normal, add to your imports the line `from devtools_testutils import AzureTestCase, EnvironmentVariableLoader`. These two objects give our tests a lot of the desired powers.
* `AzureTestCase`: the test class should inherit from this object (`class TestSchemaRegistry(AzureTestCase)`), doing so sets up the recording infrastructure and the client creation methods.
* `EnvironmentVariableLoader`: this loader serves two purposes.
    * First, it will provide the live keys we need to test our package against live resources.
    * Second, it will keep those same live keys out of our recordings to make sure that we are not leaking our secrets into the recordings.
* At the top of your test class you should include any helper methods you will need. Most libraries will have a client creation method to eliminate repetitive code.
* Following your helper methods will be your actual tests. All test methods must start with "test". The preparer built at the top of the file should decorate your test in the fashion: `@MyPreparer()`.
    * The signature of your test will always contain `self`, and following self will be all the keys that you need from your preparer. A test does not need to have every key passed into it, the test framework will take care of passing in only the parameters specifically requested in the test signature.

If you need logging functionality for your testing, pytest also offers [logging](https://docs.pytest.org/en/stable/logging.html) capabilities either inline through the `caplog` fixture or with command line flags.

### An example test (deprecated)
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

### Run and record the test (deprecated)

From your terminal run the `pytest` command to run all the tests that you have written so far.

```cmd
(env)azure-sdk-for-python\sdk\my-directory\my-library> pytest
```

Your update should run smooth and have green dots representing passing tests. Now if you look at the contents of your `tests` directory there should be a new directory called `recording` with four `.yaml` files. Each `yaml` file is a recording for a single test. To run a test in playback mode change the `testsettings_local.cfg` to `live-mode: false` and rerun the tests with the same command. The test infrastructure will use the automatically created `.yaml` recordings to mock the HTTP traffic and run the tests.

### Purging secrets (deprecated)

The `yaml` files created from running tests in live mode store the request and response interactions between the library and the service and this can include authorization, account names, shared access signatures, and other secrets. The recordings are included in our public GitHub repository, making it important for us to remove any secrets from these recordings before committing them to the repository. There are two easy ways to remove secrets. The first is the `EnvironmentVariableLoader` implementation, discussed above. This method will automatically purge the keys with the provided fake values. The second way is to use the `self.scrubber.register_name_pair(key, fake_key)` method (This method is a function of the base `AzureTestCase` class), which is used when a secret is dynamically created during a test. For example, [Tables](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/tables/azure-data-tables/tests/_shared/cosmos_testcase.py#L86-L89) uses this method to replace storage account names with standard names.

#### Special case: Shared Access Signature (deprecated)

Tests that use the Shared Access Signature (SAS) to authenticate a client should use the [`AzureTestCase.generate_sas`](https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/azure_testcase.py#L357-L370) method to generate the SAS and purge the value from the recordings. An example of using this method can be found [here](https://github.com/Azure/azure-sdk-for-python/blob/78650ba08523c14227ce8139cba5f4d1e6ed7956/sdk/tables/azure-data-tables/tests/test_table_entity.py#L1628-L1636). The method takes any number of positional arguments, with the first being the method that creates the SAS, and any number of keyword arguments (**kwargs). The method will be purged appropriately and allow for these tests to be run in playback mode.


<!-- Links -->
[advanced_tests_notes]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests-advanced.md
[azure_cli_service_principal]: https://docs.microsoft.com/cli/azure/ad/sp?view=azure-cli-latest#az-ad-sp-create-for-rbac
[azure_devtools]: https://pypi.org/project/azure-devtools/
[azure_portal]: https://portal.azure.com/
[azure_recorded_test_case]: https://github.com/Azure/azure-sdk-for-python/blob/7e66e3877519a15c1d4304eb69abf0a2281773/tools/azure-sdk-tools/devtools_testutils/azure_recorded_testcase.py#L44

[engsys_wiki]: https://dev.azure.com/azure-sdk/internal/_wiki/wikis/internal.wiki/48/Create-a-new-Live-Test-pipeline?anchor=test-resources.json
[env_var_loader]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/envvariable_loader.py

[generate_sas]: https://github.com/Azure/azure-sdk-for-python/blob/bf4749babb363e2dc972775f4408036e31f361b4/tools/azure-sdk-tools/devtools_testutils/azure_recorded_testcase.py#L196
[generate_sas_example]: https://github.com/Azure/azure-sdk-for-python/blob/3e3fbe818eb3c80ffdf6f9f1a86affd7e879b6ce/sdk/tables/azure-data-tables/tests/test_table_entity.py#L1691
[git_setup]: https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup
[git_token]: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

[kv_test_resources]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/test-resources.json
[kv_test_resources_outputs]: https://github.com/Azure/azure-sdk-for-python/blob/fbdb860630bcc13c1e355828231161849a9bd5a4/sdk/keyvault/test-resources.json#L255
[kv_test_resources_resources]: https://github.com/Azure/azure-sdk-for-python/blob/fbdb860630bcc13c1e355828231161849a9bd5a4/sdk/keyvault/test-resources.json#L116

[manage_recordings]: https://github.com/Azure/azure-sdk-for-python/blob/main/scripts/manage_recordings.py
[mgmt_settings_fake]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/mgmt_settings_fake.py

[packaging]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/packaging.md
[proxy_cert_docs]: https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/documentation/test-proxy/trusting-cert-per-language.md
[proxy_general_docs]: https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy/README.md
[proxy_migration_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md
[py_sanitizers]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/sanitizers.py
[pytest_invocation]: https://pytest.org/latest/how-to/usage.html
[pytest_logging]: https://docs.pytest.org/en/stable/logging.html
[python-dotenv_readme]:https://github.com/theskumar/python-dotenv

[recording_move]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/recording_migration_guide.md

[test_proxy_startup]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md#start-the-proxy-server
[test_resources]: https://github.com/Azure/azure-sdk-for-python/tree/main/eng/common/TestResources#readme

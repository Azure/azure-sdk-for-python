# Python SDK testing guide

This guide walks through the setup necessary to run tests in the Azure SDK for Python, gives an overview of the shared
testing infrastructure, and demonstrates how to write and run tests for a service.

## Table of contents

- [Python SDK testing guide](#python-sdk-testing-guide) - [Table of contents](#table-of-contents)
  - [Set up your development environment](#set-up-your-development-environment)
    - [SDK root directory](#sdk-root-directory)
    - [Dependency installation](#dependency-installation)
    - [Open code in IDE](#open-code-in-ide)
  - [Integrate with the pytest test framework](#integrate-with-the-pytest-test-framework)
  - [Tox](#tox)
  - [The `devtools_testutils` package](#the-devtools_testutils-package)
  - [Write or run tests](#write-or-run-tests)
    - [Set up test resources](#set-up-test-resources)
    - [Configure credentials](#configure-test-variables)
    - [Start the test proxy server](#start-the-test-proxy-server)
    - [Deliver environment variables to tests](#deliver-environment-variables-to-tests)
    - [Write your tests](#write-your-tests)
    - [Configure live or playback testing mode](#configure-live-or-playback-testing-mode)
    - [Run and record tests](#run-and-record-tests)
    - [Update test recordings](#update-test-recordings)
    - [Sanitize secrets](#sanitize-secrets)
      - [Special case: SAS tokens](#special-case-sas-tokens)
      - [Opt out of specific sanitizers](#opt-out-of-specific-sanitizers)
  - [Functional vs. unit tests](#functional-vs-unit-tests)
  - [Further reading](#further-reading)

## Set up your development environment

The Azure SDK Python team creates libraries that are compatible with Python 3.8 and up. We walk through setting up a
Python virtual environment for Python 3.8, but having a virtual environment for each minor version can make it
easier to debug PRs locally.

- Python 3.8+: Use the [python website](https://www.python.org/downloads/) or the one-click experience from the Windows store ([3.8](https://www.microsoft.com/p/python-38/9mssztt1n39l), [3.9](https://www.microsoft.com/p/python-39/9p7qfqmjrfp7), [3.10](https://www.microsoft.com/p/python-310/9pjpw5ldxlz5), [3.11](https://apps.microsoft.com/detail/9nrwmjp3717k?hl=en-us&gl=US), [3.12](https://apps.microsoft.com/detail/9ncvdn91xzqp?hl=en-us&gl=US)) (Windows only).


```cmd
C:\Users> python -m venv env
C:\Users> env\scripts\activate       # PowerShell only
C:\Users> source env\bin\activate    # Linux shell (Bash, ZSH, etc.) only
C:\Users> env\scripts\activate.bat   # Windows CMD only
(env) C:\Users>
```

To create virtual environment for different versions of Python use the `-p` flag to pass the specific Python executable you want to use

```cmd
C:\Users> python -m venv -p <path/to/Python/Python38/python.exe> py38_venv
```

### SDK root directory

In the root directory of our SDK, a number of mandatory files have been added. When creating your own SDK, these files can be copied from the [`sdk/template`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/template) project, and modified to your needs.

- README.md. This is the description and guidance for customers or your SDK. Please see the guide on writing a README to make sure you have the complete [content requirements and formatting](https://review.learn.microsoft.com/help/platform/reference-document-sdk-client-libraries#readme).
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

As a quick background, the Azure SDK uses the [pytest](https://docs.pytest.org/en/latest/) test runner to support creating unit and functional tests for Track 2 Azure libraries. To install `pytest` run `pip install pytest` from your virtual environment, you can confirm the installation was successful by running `pytest -V`. The commands will run all files of the form `test_*.py` or `*_test.py` in the provided directory and its subdirectories; for more information check out the [docs][pytest_invocation].

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

The Python SDK uses the [tox project](https://tox.wiki/en/latest/) to automate releases, run tests, run linters, and build our documentation. The `tox.ini` file is located at `azure-sdk-for-python/eng/tox/tox.ini` for reference. You do not need to make any changes to the tox file for tox to work with your project. Tox will create a directory (`.tox`) in the head of your branch. The first time you run tox commands it may take several moments, but subsequent runs will be quicker. To install tox run the following command from within your virtual environment.
`(env) > pip install "tox<5"`.

To run a tox command from your directory use the following commands:

```cmd
(env) azure-sdk-for-python\sdk\my-service\my-package> tox run -e sphinx -c ../../../eng/tox/tox.ini --root .
(env) azure-sdk-for-python\sdk\my-service\my-package> tox run -e pylint -c ../../../eng/tox/tox.ini --root .
(env) azure-sdk-for-python\sdk\my-service\my-package> tox run -e mypy -c ../../../eng/tox/tox.ini --root .
(env) azure-sdk-for-python\sdk\my-service\my-package> tox run -e pyright -c ../../../eng/tox/tox.ini --root .
(env) azure-sdk-for-python\sdk\my-service\my-package> tox run -e verifytypes -c ../../../eng/tox/tox.ini --root .
(env) azure-sdk-for-python\sdk\my-service\my-package> tox run -e whl -c ../../../eng/tox/tox.ini --root .
(env) azure-sdk-for-python\sdk\my-service\my-package> tox run -e sdist -c ../../../eng/tox/tox.ini --root .
(env) azure-sdk-for-python\sdk\my-service\my-package> tox run -e samples -c ../../../eng/tox/tox.ini --root .
(env) azure-sdk-for-python\sdk\my-service\my-package> tox run -e apistub -c ../../../eng/tox/tox.ini --root .
```

A quick description of the nine commands above:

- sphinx: documentation generation using the inline comments written in our code
- lint: runs pylint to make sure our code adheres to the style guidance
- mypy: runs the mypy static type checker for Python to make sure that our types are valid.
- pyright: runs the pyright static type checker for Python to make sure that our types are valid.
- verifytypes: runs pyright's verifytypes tool to verify the type completeness of the library.
- whl: creates a whl package for installing our package
- sdist: creates a zipped distribution of our files that the end user could install with pip
- samples: runs all of the samples in the `samples` directory and verifies they are working correctly
- apistub: runs the [apistubgenerator](https://github.com/Azure/azure-sdk-tools/tree/main/packages/python-packages/apiview-stub-generator) tool on your code

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

Newer SDK tests utilize the [Azure SDK Tools Test Proxy][proxy_general_docs] to record and playback HTTP interactions, while also automatically sanitizing sensitive information from recordings.
To migrate an existing test suite to use the test proxy, or to learn more about using the test proxy, refer to the
[test proxy migration guide][proxy_migration_guide].

### Set up test resources

Live Azure resources will be necessary in order to run live tests and produce recordings. There are PowerShell test
resource management commands, documented in [/eng/common/TestResources][test_resources], that streamline this process.
Both pure ARM templates (`test-resources.json`) and BICEP files (`test-resources.bicep`) are supported.

User-based authentication is preferred when using test resources. To enable this:
- Use the [`-UserAuth` command flag][user_auth_flag] when running the `New-TestResources` script.
- Choose a development tool to authenticate with by setting an `AZURE_TEST_USE_*_AUTH` environment variable to "true" (tests will authenticate as the tool's logged-in user). The following tools are supported, listed in the order that authentication will be attempted in if requested:
  1. Azure PowerShell: set `AZURE_TEST_USE_PWSH_AUTH`.
  2. Azure CLI (`az`): set `AZURE_TEST_USE_CLI_AUTH`.
  3. Visual Studio Code: set `AZURE_TEST_USE_VSCODE_AUTH`.
  4. Azure Developer CLI (`azd`): set `AZURE_TEST_USE_AZD_AUTH`.
- Ensure you're logged into the tool you choose -- if
you used `New-TestResources.ps1` to deploy resources, you'll already have logged in with Azure PowerShell.

**Important:** these environment variables will only be successfully used if test credentials are fetched with the
[`AzureRecordedTestCase.get_credential`][get_credential] method. See [Write your tests](#write-your-tests) for details.

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

### Configure test variables

Python SDK tests use a `.env` file to store test credentials and resource variables. This `.env` file should be placed
at either the root of `azure-sdk-for-python` in your local file system, or in the directory containing the repo. The
`python-dotenv` package is used to read this file -- documentation of the package and how to format a `.env` file can
be found in the [package's README][python-dotenv_readme].

If using a `New-TestResources` script from [/eng/common/TestResources][test_resources], the script should output any
environment variables necessary to run live tests for the service. After storing these variables in your `.env` file
-- formatted as `VARIABLE=value` on separate lines -- your credentials and test configuration variables will be set in
our environment when running tests.

If you used the [`-UserAuth` command flag][user_auth_flag] to deploy test resources, choose a development tool to
authenticate with by setting an `AZURE_TEST_USE_*_AUTH` environment variable to "true". The following tools are supported, listed in the order that authentication will be attempted in if requested:
  1. Azure PowerShell: set `AZURE_TEST_USE_PWSH_AUTH`.
  2. Azure CLI (`az`): set `AZURE_TEST_USE_CLI_AUTH`.
  3. Visual Studio Code: set `AZURE_TEST_USE_VSCODE_AUTH`.
  4. Azure Developer CLI (`azd`): set `AZURE_TEST_USE_AZD_AUTH`.

**Important:** these environment variables will only be successfully used if test credentials are fetched with the
[`AzureRecordedTestCase.get_credential`][get_credential] method. See [Write your tests](#write-your-tests) for details.

If your service doesn't have a `test-resources` file for test deployment, you'll need to set environment variables
for authentication at minimum. For user-based authentication, use `AZURE_TEST_USE_*_AUTH` as described above.

For service principal authentication:
1. Set the `AZURE_SUBSCRIPTION_ID` variable to your organization's subscription ID. You can find it in the "Overview"
   section of the "Subscriptions" blade in the [Azure Portal][azure_portal].
2. Define the `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` of a test service principal. If you do not
   have a service principal, use the Azure CLI's [az ad sp create-for-rbac][azure_cli_service_principal] command
   (ideally, using your alias as the service principal's name prefix):

```
az login
az ad sp create-for-rbac --name "{your alias}-tests" --role Contributor
```

The command will output a set of credentials. Set `AZURE_TENANT_ID` to the value of `"tenant"`, `AZURE_CLIENT_ID` to the
value of `"appId"`, and `AZURE_CLIENT_SECRET` to the value of `"password"`.

### Start the test proxy server

The test proxy has to be available in order for tests to work; this is done automatically with a `pytest` fixture.

Create a `conftest.py` file within your package's test directory (`sdk/{service}/{package}/tests`), and inside it add a
session-level fixture that accepts the `test_proxy` fixture as a parameter (and has `autouse` set to `True`):

```python
import pytest

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
# test_proxy auto-starts the test proxy
# patch_sleep and patch_async_sleep streamline tests by disabling wait times during LRO polling
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy, patch_sleep, patch_async_sleep):
    return
```

As shown in the example, it's recommended to also request the `patch_sleep` and `patch_async_sleep` fixtures unless
your tests have a unique need to use `time.sleep` or `asyncio.sleep` during playback tests (this is unusual). All of
these fixtures are imported by the central [`/sdk/conftest.py`][central_conftest], so `pytest` will automatically
resolve the references.

For more details about how this fixture starts up the test proxy, or the test proxy itself, refer to the
[test proxy migration guide][test_proxy_startup].

### Deliver environment variables to tests

Refer to the [documentation in `devtools_testutils`][env_var_docs] and use the
[`devtools_testutils.EnvironmentVariableLoader`][env_var_loader] to fetch environment variables and provide them to
tests.

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

- Import everything you will need in your tests, and include the line `from devtools_testutils import
AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy`.
  - AzureRecordedTestCase was touched on in the [`devtools_testutils` package](#the-devtools_testutils-package) section,
    and EnvironmentVariableLoader was touched on in the
    [Deliver environment variables to tests](#deliver-environment-variables-to-tests) section.
  - `recorded_by_proxy` is a decorator that must be used directly on top of recorded test methods in order to
    produce recordings. Unit tests, which aren't recorded, don't need to use this decorator. Unit tests are discussed in
    [Functional vs. unit tests](#functional-vs-unit-tests).
- Include any helper methods you will need at the top of your test class. Most libraries will have a client creation
  method to eliminate repetitive code.
- Following your helper methods will be your actual tests. All test method names must start with "test\_". The preparer
  defined at the top of the file should decorate your test in the fashion: `@MyPreparer()`.
  - The signature of your test method will always contain `self`, and following `self` will be all the keys that you
    need from your preparer. A test does not need to accept every key from the preparer; the test framework will only pass
    in the parameters specifically requested in the test method signature.
- Fetch a credential for your service client with [`self.get_credential`][get_credential]. This is necessary for the
  credential to be usable in playback tests, and for it to make use of the authentication method selected by
  `AZURE_TEST_USE_*_AUTH` environment variables.
- Within tests, use the `assert` keyword to assert conditions that you expect to be true.

If you need logging functionality for your testing, pytest also offers [logging][pytest_logging] capabilities either
inline through the `caplog` fixture or with command line flags.

If your tests use shared resources or configuration that needs to be set up at test-running time, you can refer to the
[Pre-test setup][setup] section of our advanced testing guide for recommended practices.

### Configure live or playback testing mode

"Live" tests refer to tests that make requests to actual Azure resources. "Playback" tests require a recording for each
test; the test proxy will compare the requests/responses that would be made during each test with requests/responses in
the recording.

To run live tests, set the environment variable `AZURE_TEST_RUN_LIVE` to "true" in your environment or `.env` file.
Live test runs will produce recordings unless the environment variable `AZURE_SKIP_LIVE_RECORDING` is set to "true" as
well. To run tests in playback, either set `AZURE_TEST_RUN_LIVE` to "false" or leave it unset.

### Run and record tests

First, refer to the [Configure test variables](#configure-test-variables) section to ensure environment variables are
set for test resources and authentication. With the `AZURE_TEST_RUN_LIVE` environment variable set to "true", use
`pytest` to run your test(s) in live mode.

```
(env) azure-sdk-for-python\sdk\my-service\my-package> pytest tests
```

This will generate test recordings and enable playback testing. Set `AZURE_TEST_RUN_LIVE` to "false" and run tests with
the same command to verify that playback tests pass.

Playback test errors most frequently indicate a need to add/remove sanitizers and/or add matchers (see
[Sanitize secrets](#sanitize-secrets)). If you encounter any unexpected errors, refer to the
[test proxy troubleshooting guide][troubleshooting_guide].

If tests were recorded for a new library, there should now be a folder called `recordings` inside your package's
`tests` directory. Each recording in this folder will be a `.json` file that captures the HTTP traffic that was
generated while running the test matching the file's name.

The final step in setting up recordings is to move these files out of the `azure-sdk-for-python` and into the
`azure-sdk-assets` repository. The [recording migration guide][recording_move] describes how to do so. This step only
needs to be completed once. Your library will have an `assets.json` file at its root, which stores the
`azure-sdk-assets` tag that contains the current set of recordings.

From this point on, recordings will automatically be fetched when tests are run in playback mode -- either from a local
cache (described in [Update test recordings](#update-test-recordings)), or from `azure-sdk-assets` if they're not
locally available.

#### Update test recordings

##### Environment prerequisites

- The targeted library is already migrated to use the test proxy.
- Git version > 2.30.0 is installed on the machine and in the path. Git is used by the script and test proxy.
- Global [git config settings][git_setup] are configured for `user.name` and `user.email`.
  - These settings are also set with environment variables `GIT_COMMIT_OWNER` and `GIT_COMMIT_EMAIL`, respectively (in your environment or your local `.env` file).
- Membership in the `azure-sdk-write` GitHub group.

Test recordings will be updated if tests are run while `AZURE_TEST_RUN_LIVE` is set to "true" and
`AZURE_SKIP_LIVE_RECORDING` is unset or "false". These recording updates will be reflected in a git-excluded `.assets`
folder at the root of the repo.

The `.assets` folder contains one or more directories with random names, which each are a git directory containing
recordings. To find the directory containing your package's recordings, you can use the [`manage_recordings.py`][manage_recordings]
script from `azure-sdk-for-python/scripts`. This script accepts a verb and a **relative** path to your package's
`assets.json` file (this path is optional, and is simply `assets.json` by default).

For example, to view the location of `azure-keyvault-keys`'s recordings, from a current working directory at the root
of the repo, run the following command:

```
python scripts/manage_recordings.py locate -p sdk/keyvault/azure-keyvault-keys
```

The output will include an absolute path to the recordings directory; in this case:

```
C:/azure-sdk-for-python/.assets/Y0iKQSfTwa/python
```

If you `cd` into the folder containing your package's recordings, you can use `git status` to view the recording
updates you've made. You can also use other `git` commands; for example, `git diff {file name}` to see specific file
changes, or `git restore {file name}` to undo changes you don't want to keep.

After verifying that your recording updates look correct, you can use [`manage_recordings.py`][manage_recordings] to
push your recordings to the `azure-sdk-assets` repo:

```
python scripts/manage_recordings.py push -p sdk/{service}/{package}/assets.json
```

The verbs that can be provided to this script are "locate", "push", "show", "restore", and "reset":

- **locate**: prints the location of the library's locally cached recordings.
- **push**: pushes recording updates to a new assets repo tag and updates the tag pointer in `assets.json`.
- **show**: prints the contents of the provided `assets.json` file.
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

By default, the test proxy server sanitizes several [common patterns][test_proxy_sanitizers] of secrets, but there are additional
steps you can take to ensure that any other sensitive information is removed from recordings.

There are two primary ways to keep secrets from being written into recordings:

1. The `EnvironmentVariableLoader` will automatically sanitize the values of captured environment variables with the
   provided fake values.
2. Additional sanitizers can be registered via `add_*_sanitizer` methods in `devtools_testutils`. For example, the general-use
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

In the past, it was recommended that the tests using Shared Access Signature (SAS) tokens should use the `AzureRecordedTestCase.generate_sas` method to generate the token and automatically register a sanitizer to keep this token out of test recordings. This method is now deprecated since the test proxy automatically sanitizes SAS tokens. If you have tests that use SAS tokens, you can remove the usage of the `generate_sas` method.

#### Opt out of specific sanitizers

Since, in some cases, the default sanitizers might be considered too aggressive and breaks tests during playback, you can opt out of certain sanitizers using the `remove_batch_sanitizers` function in your respective `conftest.py` files. For example:

```python
from devtools_testutils import remove_batch_sanitizers, test_proxy


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    ...
    #  Remove the following body key sanitizer: AZSDK3493: $..name
    remove_batch_sanitizers(["AZSDK3493"])
```

A list of sanitizers and their IDs can be found [here][test_proxy_sanitizers]. However, **please be mindful when opting out of a sanitizer, and ensure that no sensitive data is being exposed**.

Some sanitizers IDs that are often opted out of are:
  - `AZSDK2003`: `Location` - Header regex sanitizer
  - `AZSDK3430`: `$..id` - Body key sanitizer
  - `AZSDK3493`: `$..name` - Body key sanitizer

## Functional vs. unit tests

The tests written above are functional tests: they generate HTTP traffic and send data to the service. Client operations
that interact with the service should be tested by functional tests wherever possible.

Tests that don't make HTTP requests -- e.g. tests for model serialization or mocked service interactions for complex
scenarios --  can be referred to as "unit tests". For unit tests, the best practice is to have a separate test class
from the one containing functional tests. For example, the `azure-data-tables` package has client-side validation for
the table name and properties of the entity; below is an example of how these could be tested:

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

<!-- Links -->

[advanced_tests_notes]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests-advanced.md
[azure_cli_service_principal]: https://docs.microsoft.com/cli/azure/ad/sp?view=azure-cli-latest#az-ad-sp-create-for-rbac
[azure_portal]: https://portal.azure.com/
[azure_recorded_test_case]: https://github.com/Azure/azure-sdk-for-python/blob/7e66e3877519a15c1d4304eb69abf0a2281773/tools/azure-sdk-tools/devtools_testutils/azure_recorded_testcase.py#L44
[central_conftest]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/conftest.py
[env_var_docs]: https://github.com/Azure/azure-sdk-for-python/tree/main/tools/azure-sdk-tools/devtools_testutils#use-the-environmentvariableloader
[env_var_loader]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/envvariable_loader.py
[generate_sas]: https://github.com/Azure/azure-sdk-for-python/blob/bf4749babb363e2dc972775f4408036e31f361b4/tools/azure-sdk-tools/devtools_testutils/azure_recorded_testcase.py#L196
[get_credential]: https://github.com/Azure/azure-sdk-for-python/blob/20cf5b0bd9b87f90bd5ad4fd36358d3b257f95c5/tools/azure-sdk-tools/devtools_testutils/azure_recorded_testcase.py#L96
[git_setup]: https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup
[kv_test_resources]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/test-resources.json
[kv_test_resources_outputs]: https://github.com/Azure/azure-sdk-for-python/blob/fbdb860630bcc13c1e355828231161849a9bd5a4/sdk/keyvault/test-resources.json#L255
[kv_test_resources_resources]: https://github.com/Azure/azure-sdk-for-python/blob/fbdb860630bcc13c1e355828231161849a9bd5a4/sdk/keyvault/test-resources.json#L116
[manage_recordings]: https://github.com/Azure/azure-sdk-for-python/blob/main/scripts/manage_recordings.py
[packaging]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/packaging.md
[proxy_general_docs]: https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy/README.md
[proxy_migration_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md
[py_sanitizers]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/sanitizers.py
[pytest_invocation]: https://pytest.org/latest/how-to/usage.html
[pytest_logging]: https://docs.pytest.org/en/stable/logging.html
[python-dotenv_readme]: https://github.com/theskumar/python-dotenv
[recording_move]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/recording_migration_guide.md
[setup]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests-advanced.md#pre-test-setup
[test_proxy_sanitizers]: https://github.com/Azure/azure-sdk-tools/blob/57382d5dc00b10a2f9cfd597293eeee0c2dbd8fd/tools/test-proxy/Azure.Sdk.Tools.TestProxy/Common/SanitizerDictionary.cs#L65
[test_proxy_startup]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md#start-the-proxy-server
[test_resources]: https://github.com/Azure/azure-sdk-for-python/tree/main/eng/common/TestResources#readme
[troubleshooting_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_troubleshooting.md
[user_auth_flag]: https://github.com/Azure/azure-sdk-for-python/blob/main/eng/common/TestResources/New-TestResources.ps1.md#-userauth

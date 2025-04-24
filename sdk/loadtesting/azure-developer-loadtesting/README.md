# Azure Load Testing client library for Python

Azure Load Testing provides client library in python to the user by which they can interact natively with Azure Load Testing service. Azure Load Testing is a fully managed load-testing service that enables you to generate high-scale load. The service simulates traffic for your applications, regardless of where they're hosted. Developers, testers, and quality assurance (QA) engineers can use it to optimize application performance, scalability, or capacity.

## Documentation

Various documentation is available to help you get started

- [API reference documentation][api_reference_doc]
- [Product Documentation][product_documentation]

## Getting started

### Prequisites

- Python 3.8 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure LoadTesting resource.

### Installing the package

```bash
python -m pip install azure-developer-loadtesting
```

### Create with an Azure Active Directory Credential

To use an [Azure Active Directory (AAD) token credential][authenticate_with_token],
provide an instance of the desired credential type obtained from the
[azure-identity][azure_identity_credentials] library.

To authenticate with AAD, you must first [pip][pip] install [`azure-identity`][azure_identity_pip]

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.

As an example, sign in via the Azure CLI `az login` command and [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python) will authenticate as that user.

Use the returned token credential to authenticate the client.

### Create the client

Azure Developer LoadTesting SDK has 2 sub-clients of the main client (`LoadTestingClient`) to interact with the service, 'LoadTestAdministrationClient' for administrative operations and 'LoadTestRunClient' to run tests/test-profiles.

```python
from azure.developer.loadtesting import LoadTestAdministrationClient

# for managing authentication and authorization
# can be installed from pypi, follow: https://pypi.org/project/azure-identity/
# using DefaultAzureCredentials, read more at: https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python
from azure.identity import DefaultAzureCredential

client = LoadTestAdministrationClient(endpoint='<endpoint>', credential=DefaultAzureCredential())
```

`<endpoint>` refers to the data-plane endpoint/URL of the resource.

The data-plane endpoint is obtained from Control Plane APIs. To obtain the data-plane endpoint for your resource, follow [this documentation][obtaining_data_plane_uri].

## Key concepts

The Azure Load Test client library for python allows you to interact with each of these components through the use of clients. There are two top-level clients which are the main entry points for the library

- `LoadTestAdministrationClient` (`azure.developer.loadtesting.LoadTestAdministrationClient`)
- `LoadTestRunClient` (`azure.developer.loadtesting.LoadTestRunClient`)

These two clients also have there asynchronous counterparts, which are 
- `LoadTestAdministrationClient` (`azure.developer.loadtesting.aio.LoadTestAdministrationClient`)
- `LoadTestRunClient` (`azure.developer.loadtesting.aio.LoadTestRunClient`)

### Load Test Administration Client

The `LoadTestAdministrationClient` is used to administer and configure the load tests, test profiles, app components and metrics.

#### Test

A test specifies the test script, and configuration settings for running a load test. You can create one or more tests in an Azure Load Testing resource.

#### App Component

When you run a load test for an Azure-hosted application, you can monitor resource metrics for the different Azure application components (server-side metrics). While the load test runs, and after completion of the test, you can monitor and analyze the resource metrics in the Azure Load Testing dashboard.

#### Metrics

During a load test, Azure Load Testing collects metrics about the test execution. There are two types of metrics:

1. Client-side metrics give you details reported by the test engine. These metrics include the number of virtual users, the request response time, the number of failed requests, or the number of requests per second.

2. Server-side metrics are available for Azure-hosted applications and provide information about your Azure application components. Metrics can be for the number of database reads, the type of HTTP responses, or container resource consumption.

### Test Run Client

The `LoadTestRunClient`  is used to start and stop test runs corresponding to a load test. It can also be used to start and stop test profile runs corresponding to a test profile. A test run represents one execution of a load test. It collects the logs associated with running the Apache JMeter or Locust script, the load test YAML configuration, the list of app components to monitor, and the results of the test.

### Data-Plane Endpoint

Data-plane of Azure Load Testing resources is addressable using the following URL format:

`00000000-0000-0000-0000-000000000000.aaa.cnt-prod.loadtesting.azure.com`

The first GUID `00000000-0000-0000-0000-000000000000` is the unique identifier used for accessing the Azure Load Testing resource. This is followed by  `aaa` which is the Azure region of the resource.

The data-plane endpoint is obtained from Control Plane APIs. To obtain the data-plane endpoint for your resource, follow [this documentation][obtaining_data_plane_uri].

**Example:** `1234abcd-12ab-12ab-12ab-123456abcdef.eastus.cnt-prod.loadtesting.azure.com`

In the above example, `eastus` represents the Azure region `East US`.

## Examples

### Creating a load test 

```python
from azure.developer.loadtesting import LoadTestAdministrationClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
import os

TEST_ID = "some-test-id"  
DISPLAY_NAME = "my-load-test"  

# set SUBSCRIPTION_ID as an environment variable
SUBSCRIPTION_ID = os.environ["SUBSCRIPTION_ID"]  

client = LoadTestAdministrationClient(endpoint='<endpoint>', credential=DefaultAzureCredential())

try:
    result = client.create_or_update_test(
        TEST_ID,
        {
            "description": "",
            "displayName": "My New Load Test",
            "loadTestConfiguration": {
                "engineInstances": 1,
                "splitAllCSVs": False,
            },
            "passFailCriteria": {
                "passFailMetrics": {
                    "condition1": {
                        "clientmetric": "response_time_ms",
                        "aggregate": "avg",
                        "condition": ">",
                        "value": 300
                    },
                    "condition2": {
                        "clientmetric": "error",
                        "aggregate": "percentage",
                        "condition": ">",
                        "value": 50
                    },
                    "condition3": {
                        "clientmetric": "latency",
                        "aggregate": "avg",
                        "condition": ">",
                        "value": 200,
                        "requestName": "GetCustomerDetails"
                    }
                }
            },
            "secrets": {
                "secret1": {
                    "value": "https://sdk-testing-keyvault.vault.azure.net/secrets/sdk-secret",
                    "type": "AKV_SECRET_URI"
                }
            },
            "environmentVariables": {
                "my-variable": "value"
            }
        }
    )
    print(result)
except HttpResponseError as e:
     print('Service responded with error: {}'.format(e.response.json()))

```

### Uploading test script file to a Test

```python
from azure.developer.loadtesting import LoadTestAdministrationClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# This sample uploads a JMX Test Script File
TEST_ID = "some-test-id"  
FILE_NAME = "some-file-name.jmx"  

client = LoadTestAdministrationClient(endpoint='<endpoint>', credential=DefaultAzureCredential())

try:

    # uploading .jmx file to a test
    resultPoller = client.begin_upload_test_file(TEST_ID, FILE_NAME, open("sample.jmx", "rb"))

    # getting result of LRO poller with timeout of 600 secs
    validationResponse = resultPoller.result(600)
    print(validationResponse)
    
except HttpResponseError as e:
    print("Failed with error: {}".format(e.response.json()))
```

### Running a Test

```python
from azure.developer.loadtesting import LoadTestRunClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

TEST_ID = "some-test-id"  
TEST_RUN_ID = "some-testrun-id" 
DISPLAY_NAME = "my-load-test-run"  

client = LoadTestRunClient(endpoint='<endpoint>', credential=DefaultAzureCredential())

try:
    testRunPoller = client.begin_test_run(
    TEST_RUN_ID,
        {
            "testId": TEST_ID,
            "displayName": "My New Load Test Run",
        }
    )

    #waiting for test run status to be completed with timeout = 3600 seconds
    result = testRunPoller.result(3600)
    
    print(result)
except HttpResponseError as e:
    print("Failed with error: {}".format(e.response.json()))
```

## Troubleshooting

### Logging

This SDK uses Python standard [logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` keyword argument.
Do note that DEBUG level logging can contain sensitive information:

```python
import sys
import logging
from azure.identity import DefaultAzureCredential

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLogLevel(logging.DEBUG)

# Configure console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# Enable logging for a client
client = LoadTestAdministrationClient(endpoint='<endpoint>', credential=DefaultAzureCredential(), logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single call, even when it isn't enabled for the whole client

```python
client.create_or_update_test(..., logging_enable=True)
```

## Next steps

More samples can be found [here](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/loadtesting/azure-developer-loadtesting/samples).

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/
[api_reference_doc]: https://docs.microsoft.com/rest/api/loadtesting/
[product_documentation]: https://azure.microsoft.com/services/load-testing/
[obtaining_data_plane_uri]: https://learn.microsoft.com/rest/api/loadtesting/data-plane-uri
[python_logging]: https://docs.python.org/3/library/logging.html
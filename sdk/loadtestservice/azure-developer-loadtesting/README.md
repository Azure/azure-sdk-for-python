
# Azure Load Testing client library for Python
Azure Load Testing provides client library in python to the user by which they can interact natively with Azure Load Testing service. Azure Load Testing is a fully managed load-testing service that enables you to generate high-scale load. The service simulates traffic for your applications, regardless of where they're hosted. Developers, testers, and quality assurance (QA) engineers can use it to optimize application performance, scalability, or capacity.

## Documentation
Various documentation is available to help you get started

<!-- - [Source code][source_code] -->
- [API reference documentation][api_reference_doc]
- [Product Documentation][product_documentation]

## Getting started

### Installing the package

```bash
python -m pip install azure-developer-loadtesting
```

#### Prequisites

- Python 3.7 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure Developer LoadTesting instance.

#### Create with an Azure Active Directory Credential

To use an [Azure Active Directory (AAD) token credential][authenticate_with_token],
provide an instance of the desired credential type obtained from the
[azure-identity][azure_identity_credentials] library.

To authenticate with AAD, you must first [pip][pip] install [`azure-identity`][azure_identity_pip]

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.

As an example, sign in via the Azure CLI `az login` command and [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python) will authenticate as that user.

Use the returned token credential to authenticate the client.

#### Create the client

The data plane URI should be provided as the endpoint to create the client. 

```python
from azure.developer.loadtesting import LoadTestingClient

# for managing authentication and authorization
# can be installed from pypi, follow: https://pypi.org/project/azure-identity/
# using DefaultAzureCredentials, read more at: https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python
from azure.identity import DefaultAzureCredential

client = LoadTestingClient(endpoint='<endpoint>', credential=DefaultAzureCredential())
```
## Key concepts

The following components make up the Azure Load Testing service. The Azure Load Test client library for Java allows you to interact with each of these components through the use of clients. There are two top-level clients which are the main entry points for the library

- `LoadTestingClient` (`azure.developer.loadtesting.LoadTestingClient`)

- Async `LoadTestingClient` (`azure.developer.loadtesting.aio.LoadTestingClient`)

The two clients have similar methods in them except the methods in the async client are async as well.

The top-level clients have two sub-clients

- `load_test_runs` (`azure.developer.loadtesting.LoadTestingClient.load_test_runs`)

- `load_test_administration` (`azure.developer.loadtesting.LoadTestingClient.load_test_administration`)

These sub-clients are used for managing and using different components of the service.

### Load Test Administration Client

The `load_test_administration` sub-clients is used to administer and configure the load tests, app components and metrics.

#### Test

A test specifies the test script, and configuration settings for running a load test. You can create one or more tests in an Azure Load Testing resource.

#### App Component

When you run a load test for an Azure-hosted application, you can monitor resource metrics for the different Azure application components (server-side metrics). While the load test runs, and after completion of the test, you can monitor and analyze the resource metrics in the Azure Load Testing dashboard.

#### Metrics

During a load test, Azure Load Testing collects metrics about the test execution. There are two types of metrics:

1. Client-side metrics give you details reported by the test engine. These metrics include the number of virtual users, the request response time, the number of failed requests, or the number of requests per second.

2. Server-side metrics are available for Azure-hosted applications and provide information about your Azure application components. Metrics can be for the number of database reads, the type of HTTP responses, or container resource consumption.

### Test Run Client

The `load_test_runs` sub-clients is used to start and stop test runs corresponding to a load test. A test run represents one execution of a load test. It collects the logs associated with running the Apache JMeter script, the load test YAML configuration, the list of app components to monitor, and the results of the test.

### Data-Plane Endpoint

Data-plane of Azure Load Testing resources is addressable using the following URL format:

`00000000-0000-0000-0000-000000000000.aaa.cnt-prod.loadtesting.azure.com`

The first GUID `00000000-0000-0000-0000-000000000000` is the unique identifier used for accessing the Azure Load Testing resource. This is followed by  `aaa` which is the Azure region of the resource.

The data-plane endpoint is obtained from Control Plane APIs.

**Example:** `1234abcd-12ab-12ab-12ab-123456abcdef.eus.cnt-prod.loadtesting.azure.com`

In the above example, `eus` represents the Azure region `East US`.

## Examples

### Creating a load test 
```python
from azure.developer.loadtesting import LoadTestingClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

TEST_ID = "some-test-id"  
DISPLAY_NAME = "my-load-test"  
SUBSCRIPTION_ID = os.environ["SUBSCRIPTION_ID"]  

client = LoadTestingClient(endpoint='<endpoint>', credential=DefaultAzureCredential())

try:
    result = client.load_test_administration.create_or_update_test(
        TEST_ID,
        {
            "description": "",
            "displayName": DISPLAY_NAME,
            "loadTestConfig": {
                "engineInstances": 1,
                "splitAllCSVs": False,
            },
            "secrets": {},
            "environmentVariables": {},
            "passFailCriteria": {"passFailMetrics": {}}
        },
    )
    print(result)
except HttpResponseError as e:
     print('Service responded with error: {}'.format(e.response.json()))

```

### Uploading .jmx file to a Test
```python
from azure.developer.loadtesting import LoadTestingClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

TEST_ID = "some-test-id"  
FILE_ID = "some-file-id"  

client = LoadTestingClient(endpoint='<endpoint>', credential=DefaultAzureCredential())

try:

    result = client.load_test_administration.upload_test_file(TEST_ID, FILE_ID, open("sample.jmx", "rb"))
    print(result)
except HttpResponseError as e:
    print("Failed with error: {}".format(e.response.json()))
```

### Running a Test
```python
from azure.developer.loadtesting import LoadTestingClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

TEST_ID = "some-test-id"  
TEST_RUN_ID = "some-testrun-id" 
DISPLAY_NAME = "my-load-test-run"  

client = LoadTestingClient(endpoint='<endpoint>', credential=DefaultAzureCredential())

try:
    result = client.load_test_runs.create_or_update_test(
        TEST_RUN_ID,
        {
            "testId": TEST_ID,
            "displayName": DISPLAY_NAME,
        },
    )
    print(result)
except HttpResponseError as e:
    print("Failed with error: {}".format(e.response.json()))
```

## Next steps

More samples can be found [here](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/loadtestservice/azure-developer-loadtesting/samples).

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
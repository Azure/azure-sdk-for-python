# Azure Container Registry client library for Python

Azure Container Registry is a NoSQL data storage service that can be accessed from anywhere in the world via authenticated calls using HTTP or HTTPS.
Tables scales as needed to support the amount of data inserted, and allow for the storing of data with non-complex accessing.
The Azure Container Registry client can be used to access Azure Storage or Cosmos accounts.

[Source code][source_code] | [Package (PyPI)][Tables_pypi] | [API reference documentation][Tables_ref_docs] | [Samples][Tables_samples]

## Getting started
The Azure Container Registry SDK can access an Azure Container Registry account.

### Prerequisites
* Python 2.7, or 3.6 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription] and an ACR account.

#### Create account

### Install the package
Install the Azure Container Registry client library for Python with [pip][pip_link]:
```bash
pip install --pre azure-containerregistry
```

#### Create the client


## Key concepts
Common uses of the ACR include:

### Clients
Two different clients are provided to interact with the various components of the Table Service:


## Examples

The following sections provide several code snippets covering some of the most common Table tasks, including:



## Optional Configuration
Optional keyword arguments can be passed in at the client and per-operation level. The azure-core [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.


### Retry Policy configuration

Use the following keyword arguments when instantiating a client to configure the retry policy:

* __retry_total__ (int): Total number of retries to allow. Takes precedence over other counts.
Pass in `retry_total=0` if you do not want to retry on requests. Defaults to 10.
* __retry_connect__ (int): How many connection-related errors to retry on. Defaults to 3.
* __retry_read__ (int): How many times to retry on read errors. Defaults to 3.
* __retry_status__ (int): How many times to retry on bad status codes. Defaults to 3.
* __retry_to_secondary__ (bool): Whether the request should be retried to secondary, if able.
This should only be enabled of RA-GRS accounts are used and potentially stale data can be handled.
Defaults to `False`.

### Other client / per-operation configuration

Other optional configuration keyword arguments that can be specified on the client or per-operation.

**Client keyword arguments:**

* __connection_timeout__ (int): Optionally sets the connect and read timeout value, in seconds.
* __transport__ (Any): User-provided transport to send the HTTP request.

**Per-operation keyword arguments:**

* __raw_response_hook__ (callable): The given callback uses the response returned from the service.
* __raw_request_hook__ (callable): The given callback uses the request before being sent to service.
* __client_request_id__ (str): Optional user specified identification of the request.
* __user_agent__ (str): Appends the custom value to the user-agent header to be sent with the request.
* __logging_enable__ (bool): Enables logging at the DEBUG level. Defaults to False. Can also be passed in at
the client level to enable it for all requests.
* __headers__ (dict): Pass in custom headers as key, value pairs. E.g. `headers={'CustomValue': value}`


## Troubleshooting

### General
Azure Container Registry clients raise exceptions defined in [Azure Core][azure_core_readme]. When you interact with the Azure table library using the Python SDK, errors returned by the service respond ot the same HTTP status codes for [REST API][tables_rest] requests. The Table service operations will throw a `HttpResponseError` on failure with helpful [error codes][tables_error_codes].

For examples, if you try to create a table that already exists, a `409` error is returned indicating "Conflict".
```python
from azure.data.tables import TableServiceClient
from azure.core.exceptions import HttpResponseError
table_name = 'YourTableName'

service_client = TableServiceClient.from_connection_string(connection_string)

# Create the table if it does not already exist
tc = service_client.create_table_if_not_exists(table_name)

try:
    service_client.create_table(table_name)
except HttpResponseError:
    print("Table with name {} already exists".format(table_name))
```

### Logging
This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument:
```python
import sys
import logging
from azure.data.tables import TableServiceClient
# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# This client will log detailed information about its HTTP sessions, at DEBUG level
service_client = TableServiceClient.from_connection_string("your_connection_string", logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it is not enabled for the client:
```python
service_client.create_entity(entity=my_entity, logging_enable=True)
```

## Next steps

Several Azure Container Registry Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Tables.


## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][msft_oss_coc]. For more information see the [Code of Conduct FAQ][msft_oss_coc_faq] or contact [opencode@microsoft.com][contact_msft_oss] with any additional questions or comments.

<!-- LINKS -->
[pip_link]:https://pypi.org/project/pip/
[azure_core_ref_docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.html
[azure_core_readme]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md
[python_logging]: https://docs.python.org/3/library/logging.html
[msft_oss_coc]:https://opensource.microsoft.com/codeofconduct/
[msft_oss_coc_faq]:https://opensource.microsoft.com/codeofconduct/faq/
[contact_msft_oss]:mailto:opencode@microsoft.com


![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python/sdk/tables/azure-data-tables/README.png)
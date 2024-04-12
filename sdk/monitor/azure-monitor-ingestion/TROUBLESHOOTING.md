# Troubleshooting Azure Monitor Ingestion client library issues

This troubleshooting guide contains instructions to diagnose frequently encountered issues while using the Azure Monitor Ingestion client library for Python.

## Table of contents

* [General troubleshooting](#general-troubleshooting)
    * [Enable client logging](#enable-client-logging)
    * [Troubleshooting authentication issues with ingestion requests](#authentication-errors)
    * [Troubleshooting running async APIs](#errors-with-running-async-apis)
* [Troubleshooting logs ingestion](#troubleshooting-logs-ingestion)
    * [Troubleshooting authorization errors](#troubleshooting-authorization-errors)
    * [Troubleshooting missing logs](#troubleshooting-missing-logs)
    * [Troubleshooting slow logs upload](#troubleshooting-slow-logs-upload)
* [Extra azure-core configurations](#extra-azure-core-configurations)

## General troubleshooting

The Monitor Ingestion library raises exceptions defined in [Azure Core][azure_core_exceptions].

### Enable client logging

To troubleshoot issues with the Azure Monitor Ingestion library, it's important to first enable logging to monitor the behavior of the application. The errors and warnings in the logs generally provide useful insights into what went wrong and sometimes include corrective actions to fix issues.

This library uses the standard [logging][python_logging] library for logging. Basic information about HTTP sessions, such as URLs and headers, is logged at the `INFO` level. Detailed `DEBUG` level logging, including request/response bodies and unredacted headers, can be enabled on a client with the `logging_enable` argument:

```python
import logging
import sys
from azure.monitor.ingestion import LogsIngestionClient

# Create a logger for the 'azure.monitor.ingestion' SDK
logger = logging.getLogger('azure.monitor.ingestion')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

client = LogsIngestionClient(endpoint, credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation, even when it isn't enabled for the client:

```python
client.upload(rule_id, stream_name, logs, logging_enable=True)
```

For logging documentation with examples, see [Configure logging in the Azure libraries for Python][sdk_logging_docs].

### Authentication errors

Azure Monitor Ingestion supports Azure Active Directory authentication. Credentials can be passed through the `LogsIngestionClient` constructor. To provide a valid credential, you can use the `azure-identity` library. For more information on getting started, see the [README][create_client_readme] of the Azure Monitor Ingestion library. For more information on the various types of credential supported in `azure-identity`, see the [Azure Identity documentation][identity_docs].

For more help on troubleshooting authentication errors, see the Azure Identity client library [troubleshooting guide][identity_troubleshooting].

### Errors with running async APIs

The async transport is designed to be opt-in. The [aiohttp](https://pypi.org/project/aiohttp/) framework is one of the supported implementations of async transport. It's not installed by default. You need to install it separately as follows:

```sh
pip install aiohttp
```

## Troubleshooting logs ingestion

### Troubleshooting authorization errors

If you get an HTTP response error with status code 403 and error message similar to the following, it means that the provided credential has insufficient permissions to upload logs to the specified Data Collection Endpoint (DCE) and Data Collection Rule (DCR) ID.

```text
Upload failed: (OperationFailed) The authentication token provided does not have access to ingest data for the data collection rule with immutable Id...
```

To resolve this issue:

1. Check that the application or user making the request has sufficient permissions:
   * See this document to [manage access to data collection rule][dcr_role_permissions].
   * To ingest logs, ensure the user or service principal is assigned the **Monitoring Metrics Publisher** role for the DCR.
1. If the user or application is granted sufficient privileges to upload logs, ensure you're authenticating as that user/application. If you're authenticating using the [DefaultAzureCredential][default_azure_credential], check the logs to verify that the credential used is the one you expected. To enable logging, see the [Enable client logging](#enable-client-logging) section.
1. The permissions may take up to 30 minutes to propagate. So, if the permissions were granted recently, retry after some time.

### Troubleshooting missing logs

When you send logs to Azure Monitor for ingestion, the request may succeed, but you may not see the data appearing in the designated Log Analytics workspace table as configured in the DCR. To investigate and resolve this issue, ensure the following items:

* Double-check that you're using the correct DCE when creating the `LogsIngestionClient`. Using the wrong endpoint can result in data not being properly sent to the Log Analytics workspace.

* Make sure you provide the correct DCR ID to the `upload` method. The DCR ID is an immutable identifier that determines the transformation rules applied to the uploaded logs and directs them to the appropriate Log Analytics workspace table.

* Verify that the custom table specified in the DCR exists in the Log Analytics workspace. Ensure that you provide the accurate name of the custom table to the upload method. Mismatched table names can lead to logs not being stored correctly.

* Confirm that the logs you're sending adhere to the format expected by the DCR. The data should be an array of JSON objects, structured according to the requirements specified in the DCR. Additionally, it's essential to encode the request body in UTF-8 to avoid any data transmission issues.

* Keep in mind that data ingestion may take some time, especially if you're sending data to a specific table for the first time. In such cases, allow up to 15 minutes for the data to be fully ingested and available for querying and analysis.

### Troubleshooting slow logs upload

If you experience delays when uploading logs, it could be due to reaching service limits, which may trigger the rate limiter to throttle your client. To determine if your client has reached service limits, you can enable logging and check if the service is returning errors with an HTTP status code 429. For more information on service limits, see the [Azure Monitor service limits documentation][ingestion_service_limits].

To enable client logging and to troubleshoot this issue further, see the [Enable client logging](#enable-client-logging) section.

## Extra azure-core configurations

Some properties, including `retry_mode`, `timeout`, and `connection_verify`, can be configured by passing them in as keyword arguments to the library method calls. See [configurations][azure_core_config] for a list of all such properties.

<!-- LINKS -->
[azure_core_config]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#configurations
[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[create_client_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-ingestion#create-the-client
[data_collection_rule]: https://learn.microsoft.com/azure/azure-monitor/essentials/data-collection-rule-overview
[data_collection_rule_structure]: https://learn.microsoft.com/azure/azure-monitor/essentials/data-collection-rule-structure
[dcr_immutable_id]: https://learn.microsoft.com/azure/azure-monitor/logs/tutorial-logs-ingestion-portal#collect-information-from-the-dcr
[dcr_role_permissions]: https://learn.microsoft.com/azure/azure-monitor/logs/tutorial-logs-ingestion-portal#assign-permissions-to-the-dcr
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md#authenticate-with-defaultazurecredential
[identity_docs]: https://learn.microsoft.com/python/api/overview/azure/identity-readme
[identity_troubleshooting]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/TROUBLESHOOTING.md
[ingestion_service_limits]: https://learn.microsoft.com/azure/azure-monitor/service-limits#logs-ingestion-api
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-logging

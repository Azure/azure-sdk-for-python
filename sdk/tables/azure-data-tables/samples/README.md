---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-data-tables
urlFragment: tables-samples
---

# Samples for Azure Tables client library for Python

These code samples show common scenario operations with the Azure Text Analytics client library.
The async versions of the samples require Python 3.5 or later.

You can authenticate your client with a Tables API key:
* See [sample_authentication.py][sample_authentication] and [sample_authentication_async.py][sample_authentication_async] for how to authenticate in the above cases.

These sample programs show common scenarios for the Text Analytics client's offerings.

|**File Name**|**Description**|
|-------------|---------------|
|[sample_create_client.py][create_client] and [sample_create_client_async.py][create_client_async]|Instantiate a table client|Authorizing a `TableServiceClient` object|
|[sample_create_delete_table.py][create_delete_table] and [sample_create_delete_table_async.py][create_delete_table_async]|Creating a table in a storage account|
|[sample_insert_delete_entities.py][insert_delete_entities] and [sample_insert_delete_entities_async.py][insert_delete_entities_async]|Inserting and deleting individual entities into a table|
|[sample_query_table.py][query_table] and [sample_query_table_async.py][query_table_async]|Querying entities in a table|

### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure storage account](https://docs.microsoft.com/azure/storage/common/storage-account-overview) to use this package
 or you must have a [Azure Cosmos Account](https://docs.microsoft.com/azure/cosmos-db/account-overview).

## Setup

1. Install the Azure Data Tables client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install --pre azure-data-tables
```


2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_detect_language.py`

## Next steps

Check out the [API reference documentation][api_reference_documentation] to learn more about
what you can do with the Azure Text Analytics client library.


<!-- LINKS -->
[api_reference_documentation]: https://aka.ms/azsdk/python/tables/docs

[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/samples_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/samples_authentication_async.py

[create_delete_table]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/sample_create_delete_table.py
[create_delete_table_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/sample_create_delete_table_async.py

[insert_delete_entities_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/sample_insert_delete_entities.py
[insert_delete_entities_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/sample_insert_delete_entities_async.py

[query_table]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/sample_insert_delete_entities_async.py
[query_table_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/sample_insert_delete_entities_async.py

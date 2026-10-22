# Migrate from Purview Catalog to Purview DataMap

This guide is intended to assist in the migration to Azure Purview DataMap client library [`azure-purview-datamap`](https://pypi.org/project/azure-purview-datamap/) from [`azure-purview-catalog`](https://pypi.org/project/azure-purview-catalog/). It will focus on side-by-side comparisons for similar operations between the two packages.

For those new to the Purview Data Map library, please refer to the README file and samples in [`azure-purview-datamap`](https://aka.ms/azure-sdk-for-python/purview-datamap) for the `azure-purview-datamap` library rather than this guide.

## Table of contents

- [Migration benefits](#migration-benefits)
- [General changes](#general-changes)
  - [Package and client name](#package-and-client-name)
- [Additional samples](#additional-samples)

## Migration benefits

> Note: `azure-purview-catalog` has been <b>deprecated</b>. Please upgrade to `azure-purview-datamap` for continued support.


The new Purview DataMap library `azure-purview-datamap` includes the service models together with the DataMap APIs [API Document](https://learn.microsoft.com/rest/api/purview/datamapdataplane/operation-groups). The client name and the operation names have slightly changed but the main functionality remains the same.

## General changes

### Package and client name

Previously in `azure-purview-catalog`, the client name is PurviewCatalogClient.

```python
from azure.purview.catalog import PurviewCatalogClient
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
client = PurviewCatalogClient(endpoint="https://<my-account-name>.purview.azure.com", credential=credential)
```

Now in `azure-purview-datamap`, the client name is DataMapClient.

```python
from azure.purview.datamap import DataMapClient
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
client = DataMapClient(endpoint="https://<my-account-name>.purview.azure.com", credential=credential)
```

### Operation name

The operation names have slightly changed but the main functionality remains the same. Please check the below examples.

#### Get all types
```python
# azure-purview-catalog
response = client.types.get_all_type_definitions()

# azure-purview-datamap
response = client.type_definition.get()
```

## Additional samples

For more examples, see [Samples for Purview DataMap](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/purview/azure-purview-datamap#examples).
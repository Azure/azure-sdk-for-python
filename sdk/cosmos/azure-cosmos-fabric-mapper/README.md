# Azure Cosmos DB Fabric Mirror Mapper client library for Python

This package provides an **optional**, **separately installable** Python library that translates
a subset of Cosmos-style SQL queries into parameterized SQL suitable for querying a Fabric
mirrored table, then maps tabular results back to Cosmos-like result shapes.

Key capabilities:

- Transparent query translation from Cosmos SQL to Fabric SQL for the supported subset
- Secure credential pass-through with no secrets in logs or exceptions
- Result shape mapping from tabular rows to Cosmos-like documents
- ORDER BY support as a side-benefit for queries not supported in the Cosmos Python SDK today
- Aggregation-friendly: run expensive aggregations against Fabric mirror instead of Cosmos
- Dual driver support: `mssql-python` (recommended) and `pyodbc` (legacy)

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos-fabric-mapper)
| [Package (PyPI)](https://pypi.org/project/azure-cosmos-fabric-mapper/)

## Getting started

### Prerequisites

- Python 3.9 or later
- An Azure Cosmos DB account with Fabric Mirroring enabled
- A Fabric Warehouse endpoint with the mirrored database and table

### Install the package

**Recommended**: With `mssql-python` (pure Python, no system dependencies on Windows):

```bash
pip install azure-cosmos-fabric-mapper[sql]
```

No system ODBC driver installation required on Windows.

For Linux/macOS, minimal system libraries are needed:

**Linux (Debian/Ubuntu):**
```bash
apt-get install -y libltdl7 libkrb5-3 libgssapi-krb5-2
pip install azure-cosmos-fabric-mapper[sql]
```

**macOS:**
```bash
brew install openssl
pip install azure-cosmos-fabric-mapper[sql]
```

**Alternative**: With `pyodbc` (legacy, requires system ODBC driver):

```bash
pip install azure-cosmos-fabric-mapper[odbc]
```

The `pyodbc` option requires the **ODBC Driver 18 for SQL Server** to be installed separately:

- **Windows**: Download installer from [Microsoft](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)
- **Linux**: Follow [installation guide](https://learn.microsoft.com/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server)
- **macOS**: Use Homebrew: `brew install microsoft/mssql-release/msodbcsql18`

> **Note**: The `mssql-python` driver is recommended for most users as it eliminates the need
> for system-level ODBC driver installation. Both drivers provide the same functionality
> and are officially supported by Microsoft for Fabric SQL endpoints.

## Key concepts

### Query translation

The mapper translates Cosmos-style SQL queries into parameterized Fabric SQL. Supported
Cosmos SQL features include:

- `SELECT` projections (including `SELECT *`, `SELECT VALUE`)
- `FROM c` (container alias)
- `WHERE` filters with boolean expressions, comparisons, `AND`/`OR`/`NOT`
- Parameterized queries (`@param`)
- `ORDER BY` (single/multi-column, ASC/DESC)
- `OFFSET`/`LIMIT` pagination
- `TOP` limit
- `GROUP BY` / `HAVING`
- Aggregations: `COUNT`, `SUM`, `MAX`, `MIN`, `AVG`

### Result mapping

Tabular rows returned from Fabric are mapped back into Cosmos-like document shapes
(list of dicts), preserving the expected result format for downstream consumers.

### Security

- Credentials are never logged or persisted
- Query parameters are never interpolated into SQL strings (strict parameterization)
- Diagnostic output automatically redacts secrets via regex-based redaction
- Azure AD authentication via `DefaultAzureCredential`

## Examples

### Standalone usage

```python
from azure.cosmos.fabric_mapper import MirrorServingConfiguration, run_mirrored_query
from azure.cosmos.fabric_mapper.sdk_hook import MirroredQueryRequest

# Configure Fabric mirror connection
config = MirrorServingConfiguration(
    fabric_server="your-fabric-endpoint.datawarehouse.fabric.microsoft.com",
    fabric_database="your-database",
    fabric_table="your-table",
    fabric_schema="dbo",
)

# Run a Cosmos-style query against the Fabric mirror
request = MirroredQueryRequest(
    query="SELECT * FROM c WHERE c.partitionKey = @pk ORDER BY c.id",
    parameters=[{"name": "@pk", "value": "partition1"}],
)

results = run_mirrored_query(request, config)
# returns list of dicts matching Cosmos result shape
```

### Integration with Cosmos SDK

To enable mirror serving in the Azure Cosmos DB Python SDK:

1. Install this mapper package (see above).
2. Patch the Cosmos SDK with mirror serving support.
3. Configure mirror serving when creating the Cosmos client:

```python
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

client = CosmosClient(
    url="https://my-account.documents.azure.com:443/",
    credential=DefaultAzureCredential(),
    enable_mirror_serving=True,
    mirror_config={
        "fabric_server": "your-fabric.datawarehouse.fabric.microsoft.com",
        "fabric_database": "your-database",
        "fabric_table": "your-table",
        "fabric_schema": "dbo",
    },
)

container = client.get_database_client("mydb").get_container_client("mycont")
items = container.query_items(
    query="SELECT * FROM c WHERE c.category = @cat ORDER BY c.price",
    parameters=[{"name": "@cat", "value": "electronics"}],
)
```

### Migrating from `pyodbc` to `mssql-python`

No code changes required. Update the install command:

```bash
# Before (pyodbc)
pip install azure-cosmos-fabric-mapper[odbc]

# After (mssql-python)
pip install azure-cosmos-fabric-mapper[sql]
```

Both drivers use the same DB-API 2.0 interface and connection string format.

## Troubleshooting

### Common issues

- **`UnsupportedCosmosQueryError`**: The query uses a Cosmos SQL feature not yet supported
  (e.g., subqueries, JOINs, UDFs). Simplify the query or use the Cosmos SDK directly.
- **Connection failures**: Verify that the Fabric Warehouse endpoint is correct and that
  your Azure AD credentials have read access to the Fabric SQL endpoint.
- **Schema mismatch**: The Fabric mirror schema must match the Cosmos container structure.
  Verify column names and types in the mirrored table.

### Known limitations

- **Regex-based parser keyword collisions**: Column names containing SQL keywords as
  substrings (e.g., `c.order_date`, `c.group_name`) may be mis-parsed.
- **String literals with SQL keywords**: Literals like `'ORDER processing'` may cause
  parse failures. Use parameterized queries (`@param`) instead.
- **Replication lag**: Fabric mirror has eventual consistency (typically seconds to minutes).
- **Read-only**: The mapper only supports read operations; writes must go through Cosmos DB.

## Next steps

- Review the [API contract documentation](specs/001-fabric-mirror-mapper/contracts/python-api.md)
  for detailed translation rules and supported query patterns.
- See the [specs/001-fabric-mirror-mapper/](specs/001-fabric-mirror-mapper/) directory for
  design documents and architecture details.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to
agree to a Contributor License Agreement (CLA) declaring that you have the right to, and
actually do, grant us the rights to use your contribution. For details, visit
[https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA-bot will automatically determine whether you need
to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow
the instructions provided by the bot. You will only need to do this once across all repos
using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information, see the
[Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact
[opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or
comments.

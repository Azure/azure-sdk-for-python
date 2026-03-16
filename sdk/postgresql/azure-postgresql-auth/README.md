# Azure PostgreSQL Auth client library for Python

The Azure PostgreSQL Auth client library provides Microsoft Entra ID authentication for Python database drivers connecting to Azure Database for PostgreSQL. It supports psycopg2, psycopg3, and SQLAlchemy with automatic token management and connection pooling.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/postgresql/azure-postgresql-auth)
| [Package (PyPI)](https://pypi.org/project/azure-postgresql-auth/)
| [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/postgresql/azure-postgresql-auth/samples)

## Getting started

### Prerequisites

- Python 3.9 or later
- An Azure subscription
- An Azure Database for PostgreSQL Server instance with Entra ID authentication enabled
- A credential object that implements the [TokenCredential](https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.tokencredential) interface

### Install the package

Install the core package:

```bash
pip install azure-postgresql-auth
```

Install with driver-specific extras:

```bash
# For psycopg3 (recommended for new projects)
pip install "azure-postgresql-auth[psycopg3]"

# For psycopg2 (legacy support)
pip install "azure-postgresql-auth[psycopg2]"

# For SQLAlchemy
pip install "azure-postgresql-auth[sqlalchemy]"
```

Install Azure Identity for credential support:

```bash
pip install azure-identity
```

Note: If using async credentials in `azure.identity.aio`, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/):

```bash
pip install aiohttp
```

## Key concepts

### Authentication flow

1. **Token Acquisition**: Uses Azure Identity credentials to acquire access tokens from Microsoft Entra ID.
2. **Automatic Refresh**: Tokens are acquired for each new database connection.
3. **Secure Transport**: Tokens are passed as passwords in PostgreSQL connection strings over SSL.
4. **Server Validation**: Azure Database for PostgreSQL validates the token and establishes the authenticated connection.
5. **User Mapping**: The token's user principal name (UPN) is mapped to a PostgreSQL user for authorization.

### Token scopes

The library requests the following OAuth2 scopes:

- **Database scope**: `https://ossrdbms-aad.database.windows.net/.default` (primary)
- **Management scope**: `https://management.azure.com/.default` (fallback for managed identities)

### Driver support

- **psycopg3**: Modern PostgreSQL driver (recommended for new projects) — sync and async support
- **psycopg2**: Legacy PostgreSQL driver — synchronous only
- **SQLAlchemy**: ORM/Core interface using event listeners — sync and async engine support

### Security features

- **Token-based authentication**: No passwords stored or transmitted
- **Automatic expiration**: Tokens expire and are refreshed automatically
- **SSL enforcement**: All connections require SSL encryption
- **Principle of least privilege**: Only database-specific scopes are requested

## Examples

### Configuration

The samples use environment variables to configure database connections. Copy `.env.example` into a `.env` file
in the same directory as the sample and update the variables:

```
POSTGRES_SERVER=<your-server.postgres.database.azure.com>
POSTGRES_DATABASE=<your_database_name>
```

### psycopg2 — Connection pooling

```python
from azure_postgresql_auth.psycopg2 import EntraConnection
from azure.identity import DefaultAzureCredential
from psycopg2 import pool
from functools import partial

credential = DefaultAzureCredential()
connection_factory = partial(EntraConnection, credential=credential)

connection_pool = pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=5,
    host="your-server.postgres.database.azure.com",
    database="your_database",
    connection_factory=connection_factory,
)
conn = connection_pool.getconn()
with conn.cursor() as cur:
    cur.execute("SELECT 1")
```

### psycopg2 — Direct connection

```python
from azure_postgresql_auth.psycopg2 import EntraConnection
from azure.identity import DefaultAzureCredential

with EntraConnection(
    "postgresql://your-server.postgres.database.azure.com:5432/your_database",
    credential=DefaultAzureCredential(),
) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
```

### psycopg3 — Synchronous connection

```python
from azure_postgresql_auth.psycopg3 import EntraConnection
from azure.identity import DefaultAzureCredential
from psycopg_pool import ConnectionPool

with ConnectionPool(
    conninfo="postgresql://your-server.postgres.database.azure.com:5432/your_database",
    connection_class=EntraConnection,
    kwargs={"credential": DefaultAzureCredential()},
    min_size=1,
    max_size=5,
) as pg_pool:
    with pg_pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
```

### psycopg3 — Asynchronous connection

```python
from azure_postgresql_auth.psycopg3 import AsyncEntraConnection
from azure.identity.aio import DefaultAzureCredential
from psycopg_pool import AsyncConnectionPool

async with AsyncConnectionPool(
    conninfo="postgresql://your-server.postgres.database.azure.com:5432/your_database",
    connection_class=AsyncEntraConnection,
    kwargs={"credential": DefaultAzureCredential()},
    min_size=1,
    max_size=5,
) as pg_pool:
    async with pg_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1")
```

### SQLAlchemy — Synchronous engine

> For more information, see SQLAlchemy's documentation on
> [controlling how parameters are passed to the DBAPI connect function](https://docs.sqlalchemy.org/en/20/core/engines.html#controlling-how-parameters-are-passed-to-the-dbapi-connect-function).

```python
from sqlalchemy import create_engine
from azure_postgresql_auth.sqlalchemy import enable_entra_authentication
from azure.identity import DefaultAzureCredential

engine = create_engine(
    "postgresql+psycopg://your-server.postgres.database.azure.com/your_database",
    connect_args={"credential": DefaultAzureCredential()},
)
enable_entra_authentication(engine)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
```

### SQLAlchemy — Asynchronous engine

```python
from sqlalchemy.ext.asyncio import create_async_engine
from azure_postgresql_auth.sqlalchemy import enable_entra_authentication_async
from azure.identity import DefaultAzureCredential

engine = create_async_engine(
    "postgresql+psycopg://your-server.postgres.database.azure.com/your_database",
    connect_args={"credential": DefaultAzureCredential()},
)
enable_entra_authentication_async(engine)

async with engine.connect() as conn:
    result = await conn.execute(text("SELECT 1"))
```

## Troubleshooting

### Authentication errors

If you get "password authentication failed", ensure your Azure identity has been granted access to the database:

```sql
-- Run as a database administrator
CREATE ROLE "your-user@your-domain.com" WITH LOGIN;
GRANT ALL PRIVILEGES ON DATABASE your_database TO "your-user@your-domain.com";
```

### Connection timeouts

Increase the connection timeout for slow networks:

```python
conn = EntraConnection.connect(
    "postgresql://server:5432/db",
    credential=DefaultAzureCredential(),
    connect_timeout=30,
)
```

### Windows async compatibility

On Windows, you may need to set the event loop policy for async usage:

```python
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

### Debug logging

Enable debug logging to troubleshoot authentication issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next steps

### Additional documentation

For more information about Azure Database for PostgreSQL Entra ID authentication, see the
[Azure documentation](https://learn.microsoft.com/azure/postgresql/security/security-entra-configure).

### Samples

Explore [sample code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/postgresql/azure-postgresql-auth/samples) for psycopg2, psycopg3, and SQLAlchemy.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fpostgresql%2Fazure-postgresql-auth%2FREADME.png)

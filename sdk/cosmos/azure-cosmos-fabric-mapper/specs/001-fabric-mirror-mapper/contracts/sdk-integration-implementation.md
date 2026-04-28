# Cosmos SDK Integration: Implementation Guide

This document provides **concrete code examples** for integrating the `azure-cosmos-fabric-mapper` package into the Azure Cosmos DB Python SDK.

## Integration Overview

The integration requires 3 changes to the Cosmos SDK:

1. **Add configuration option** for mirror serving (opt-in, defaults to disabled)
2. **Add dynamic import boundary** with clear error when mapper is missing
3. **Delegate execution** to mapper hook when mirror serving is enabled

---

## 1. Add Mirror Serving Configuration

### Client-level configuration

Add `mirror_config` parameter to `CosmosClient.__init__()` (no global enable flag):

```python
# In azure/cosmos/cosmos_client.py

class CosmosClient:
    def __init__(
        self,
        url: str,
        credential: Any,
        consistency_level: Optional[str] = None,
        # ... existing params ...
        mirror_config: Optional[Dict[str, Any]] = None,  # NEW PARAMETER
    ):
        """Initialize Cosmos client.
        
        Args:
            url: Cosmos DB account endpoint
            credential: Authentication credential
            mirror_config: Optional Fabric mirror configuration for per-request routing.
                          Requires azure-cosmos-fabric-mapper package when used.
                          Dict with keys:
                - fabric_server: Fabric SQL endpoint
                - fabric_database: Database name
                - fabric_table: Table name
                - fabric_schema: Schema name (default: "dbo")
        """
        self._url = url
        self._credential = credential
        self._mirror_config = mirror_config
        # ... rest of initialization ...
```

---

## 2. Add Dynamic Import Boundary with Error Handling

Create a new module `azure/cosmos/_mirror_integration.py`:

```python
"""Integration layer for optional Fabric mirror serving."""

from typing import Any, Dict, List, Optional


class MirrorServingNotAvailableError(Exception):
    """Raised when mirror serving is requested but mapper package is not installed."""
    
    def __init__(self):
        super().__init__(
            "Mirror serving was requested but the azure-cosmos-fabric-mapper package "
            "is not installed.\n\n"
            "To enable this feature, install the mapper package:\n"
            "  pip install azure-cosmos-fabric-mapper[odbc]\n\n"
            "Or disable mirror serving for this query:\n"
            "  - Set use_mirror_serving=False in query_items() call\n"
            "  - Or remove mirror_config from CosmosClient constructor"
        )


def _lazy_import_mapper():
    """Dynamically import mapper package only when needed.
    
    Returns:
        Module handle to azure_cosmos_fabric_mapper.sdk_hook.contract
        
    Raises:
        MirrorServingNotAvailableError: If package is not installed
    """
    try:
        from azure_cosmos_fabric_mapper.sdk_hook import contract
        return contract
    except ImportError as exc:
        raise MirrorServingNotAvailableError() from exc


def execute_mirrored_query(
    query: str,
    parameters: Optional[List[Dict[str, Any]]],
    mirror_config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Execute query against Fabric mirror using mapper package.
    
    Args:
        query: Cosmos SQL query text
        parameters: List of parameter dicts with 'name' and 'value' keys
        mirror_config: Dict with fabric_server, fabric_database, fabric_table, fabric_schema
        
    Returns:
        List of Cosmos-like document dicts
        
    Raises:
        MirrorServingNotAvailableError: If mapper package not installed
        UnsupportedCosmosQueryError: If query uses unsupported features
        DriverError: If connection to Fabric fails
    """
    contract = _lazy_import_mapper()
    
    # Import mapper types
    from azure_cosmos_fabric_mapper import MirrorServingConfiguration
    from azure_cosmos_fabric_mapper.credentials import DefaultAzureSqlCredential
    from azure_cosmos_fabric_mapper.driver import get_driver_client
    
    # Convert Cosmos parameter format to mapper format
    param_dict = {}
    if parameters:
        for param in parameters:
            # Cosmos uses [{"name": "@pk", "value": "val"}]
            # Mapper uses {"pk": "val"} (without @ prefix)
            param_name = param["name"].lstrip("@")
            param_dict[param_name] = param["value"]
    
    # Build configuration
    config = MirrorServingConfiguration(
        fabric_server=mirror_config["fabric_server"],
        fabric_database=mirror_config["fabric_database"],
        fabric_table=mirror_config["fabric_table"],
        fabric_schema=mirror_config.get("fabric_schema", "dbo"),
    )
    
    # Create credentials
    credentials = DefaultAzureSqlCredential()
    
    # Create request
    request = contract.MirroredQueryRequest(
        query=query,
        parameters=param_dict,
    )
    
    # Execute using default credentials and auto-selected driver
    # (prefers mssql-python, falls back to pyodbc if unavailable)
    results = contract.run_mirrored_query(
        request=request,
        config=config,
        credentials=credentials,
        driver_client=get_driver_client(config, credentials),
    )
    
    return results
```

---

## 3. Integrate into Query Execution Path

Modify `ContainerProxy.query_items()` to add conditional routing:

```python
# In azure/cosmos/container.py

from typing import Any, Dict, Iterable, List, Optional
from ._mirror_integration import execute_mirrored_query, MirrorServingNotAvailableError


class ContainerProxy:
    def query_items(
        self,
        query: str,
        parameters: Optional[List[Dict[str, Any]]] = None,
        partition_key: Optional[Any] = None,
        enable_cross_partition_query: bool = False,
        max_item_count: Optional[int] = None,
        use_mirror_serving: Optional[bool] = None,  # NEW PARAMETER
        **kwargs
    ) -> Iterable[Dict[str, Any]]:
        """Query items in the container.
        
        Args:
            query: Cosmos SQL query
            parameters: Query parameters
            partition_key: Optional partition key for single-partition query
            enable_cross_partition_query: Enable cross-partition queries
            max_item_count: Max items per page
            use_mirror_serving: If True, route query to Fabric mirror (requires mirror_config
                               on client). If False or None, use Cosmos DB (default).
            
        Returns:
            Iterable of item dicts
            
        Raises:
            MirrorServingNotAvailableError: If mirror serving requested but mapper not installed
            ValueError: If mirror serving requested but mirror_config not provided on client
        """
        # NEW: Check if mirror serving is requested for this query
        if use_mirror_serving:
            # Validate configuration
            if not self.client_connection._mirror_config:
                raise ValueError(
                    "Mirror serving was requested (use_mirror_serving=True) but mirror_config "
                    "was not provided to CosmosClient constructor. Please provide mirror_config "
                    "or set use_mirror_serving=False to use Cosmos DB."
                )
            
            # Delegate to mapper
            try:
                return execute_mirrored_query(
                    query=query,
                    parameters=parameters,
                    mirror_config=self.client_connection._mirror_config,
                )
            except MirrorServingNotAvailableError:
                # Re-raise with context
                raise
            except Exception as exc:
                # Wrap mapper exceptions with context
                raise RuntimeError(
                    f"Mirror serving query failed: {exc}. "
                    "You can disable mirror serving for this query with use_mirror_serving=False"
                ) from exc
        
        # EXISTING: Default Cosmos execution path
        return self._query_items_original(
            query=query,
            parameters=parameters,
            partition_key=partition_key,
            enable_cross_partition_query=enable_cross_partition_query,
            max_item_count=max_item_count,
            **kwargs
        )
    
    def _query_items_original(self, query, parameters, partition_key, enable_cross_partition_query, max_item_count, **kwargs):
        """Original query_items implementation (existing SDK code)."""
        # ... existing implementation ...
        pass
```

---

## 4. Usage Examples

### Scenario 1: Default behavior (no mirror serving)

```python
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

# Default behavior - no changes to existing code
client = CosmosClient(
    url="https://my-account.documents.azure.com:443/",
    credential=DefaultAzureCredential()
)

container = client.get_database_client("mydb").get_container_client("mycont")

# No use_mirror_serving specified = uses Cosmos DB (default)
items = container.query_items(
    query="SELECT * FROM c WHERE c.category = @cat",
    parameters=[{"name": "@cat", "value": "electronics"}]
)
# Executes against Cosmos DB as normal
```

### Scenario 2: Per-request mirror serving with mapper installed

```python
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

# Provide mirror config (doesn't enable it globally)
client = CosmosClient(
    url="https://my-account.documents.azure.com:443/",
    credential=DefaultAzureCredential(),
    mirror_config={  # NEW: Optional config for mirror serving
        "fabric_server": "my-fabric.msit-datawarehouse.fabric.microsoft.com",
        "fabric_database": "mydb",
        "fabric_table": "mycont",
        "fabric_schema": "dbo",
    }
)

container = client.get_database_client("mydb").get_container_client("mycont")

# Point read from Cosmos DB (low latency)
item = container.query_items(
    query="SELECT * FROM c WHERE c.id = @id",
    parameters=[{"name": "@id", "value": "123"}],
    use_mirror_serving=False  # Explicitly use Cosmos DB
)

# Expensive aggregation from Fabric mirror (cheaper, faster for analytics)
count = container.query_items(
    query="SELECT VALUE COUNT(1) FROM c WHERE c.category = @cat",
    parameters=[{"name": "@cat", "value": "electronics"}],
    use_mirror_serving=True  # Route to Fabric mirror
)
# Executes against Fabric mirror, returns Cosmos-like results

# ORDER BY query from Fabric mirror (not supported in Cosmos Python SDK)
items = container.query_items(
    query="SELECT * FROM c WHERE c.category = @cat ORDER BY c.price DESC",
    parameters=[{"name": "@cat", "value": "electronics"}],
    use_mirror_serving=True  # Use Fabric for ORDER BY support
)
```

### Scenario 3: Mirror serving requested WITHOUT mapper installed

```python
from azure.cosmos import CosmosClient

client = CosmosClient(
    url="https://my-account.documents.azure.com:443/",
    credential=DefaultAzureCredential(),
    mirror_config={"fabric_server": "...", "fabric_database": "...", "fabric_table": "..."}
)

container = client.get_database_client("mydb").get_container_client("mycont")

try:
    items = container.query_items(
        query="SELECT * FROM c",
        use_mirror_serving=True  # Request mirror serving
    )
except MirrorServingNotAvailableError as exc:
    print(exc)
    # Output:
    # Mirror serving was requested but the azure-cosmos-fabric-mapper package is not installed.
    #
    # To enable this feature, install the mapper package:
    #   pip install azure-cosmos-fabric-mapper[odbc]
    #
    # Or disable mirror serving for this query:
    #   - Set use_mirror_serving=False in query_items() call
    #   - Or remove mirror_config from CosmosClient constructor
```

---

## 5. Testing Requirements

The Cosmos SDK should add these tests:

### Test 1: Default behavior (no mirror serving requested)

```python
def test_query_items_default_behavior():
    """When use_mirror_serving not specified, queries execute against Cosmos DB."""
    client = CosmosClient(
        url=COSMOS_URL,
        credential=CREDENTIAL,
        mirror_config={"fabric_server": "...", "fabric_database": "...", "fabric_table": "..."}
    )
    container = client.get_database_client("db").get_container_client("cont")
    
    # Should not attempt to import mapper when use_mirror_serving not specified
    with patch('azure.cosmos._mirror_integration._lazy_import_mapper') as mock_import:
        items = list(container.query_items(query="SELECT * FROM c"))
        mock_import.assert_not_called()
    
    # Should not attempt to import mapper when use_mirror_serving=False
    with patch('azure.cosmos._mirror_integration._lazy_import_mapper') as mock_import:
        items = list(container.query_items(query="SELECT * FROM c", use_mirror_serving=False))
        mock_import.assert_not_called()
```

### Test 2: Mirror serving requested, mapper missing

```python
def test_mirror_serving_requested_but_mapper_missing():
    """When mirror serving requested but mapper missing, should raise clear error."""
    client = CosmosClient(
        url=COSMOS_URL,
        credential=CREDENTIAL,
        mirror_config={"fabric_server": "...", "fabric_database": "...", "fabric_table": "..."}
    )
    container = client.get_database_client("db").get_container_client("cont")
    
    with pytest.raises(MirrorServingNotAvailableError) as exc_info:
        list(container.query_items(query="SELECT * FROM c", use_mirror_serving=True))
    
    assert "pip install azure-cosmos-fabric-mapper" in str(exc_info.value)
```

### Test 3: Mirror serving requested with mapper installed

```python
def test_mirror_serving_delegates_to_mapper_when_requested():
    """When use_mirror_serving=True and mapper installed, queries delegated to mapper."""
    client = CosmosClient(
        url=COSMOS_URL,
        credential=CREDENTIAL,
        mirror_config={
            "fabric_server": "test.fabric.com",
            "fabric_database": "db",
            "fabric_table": "tbl"
        }
    )
    container = client.get_database_client("db").get_container_client("cont")
    
    with patch('azure.cosmos._mirror_integration.execute_mirrored_query') as mock_exec:
        mock_exec.return_value = [{"id": "1", "name": "test"}]
        
        # Request mirror serving
        items = list(container.query_items(
            query="SELECT * FROM c WHERE c.category = @cat",
            parameters=[{"name": "@cat", "value": "books"}],
            use_mirror_serving=True
        ))
        
        # Verify mapper was called with correct arguments
        mock_exec.assert_called_once()
        args = mock_exec.call_args
        assert args.kwargs["query"] == "SELECT * FROM c WHERE c.category = @cat"
        assert args.kwargs["parameters"] == [{"name": "@cat", "value": "books"}]
        assert args.kwargs["mirror_config"]["fabric_server"] == "test.fabric.com"
```

---

## Summary of SDK Changes

| File | Change Type | Description |
|------|-------------|-------------|
| `cosmos_client.py` | Addition | Add `mirror_config` param (optional) |
| `_mirror_integration.py` | New file | Dynamic import + error handling + delegation logic |
| `container.py` | Modification | Add `use_mirror_serving` param and conditional routing in `query_items()` |
| `tests/unit/test_mirror_integration.py` | New file | Unit tests for per-request mirror serving behavior |

**Total lines added**: ~200 lines  
**Impact on existing code**: Minimal (one conditional branch in query path, one new optional parameter)  
**Breaking changes**: None  
**Per-request control**: Users decide Cosmos DB vs Fabric mirror on each query

---

## Migration Path for Existing Users

Existing Cosmos SDK users will see **zero impact** unless they explicitly opt in:

1. **No code changes required**: Default behavior unchanged (no `use_mirror_serving` = uses Cosmos DB)
2. **Per-request opt-in**: Must set `use_mirror_serving=True` on specific queries
3. **Graceful degradation**: Clear error if mapper package missing when mirror serving requested
4. **Fine-grained control**: Can choose Cosmos DB vs Fabric mirror on a query-by-query basis
5. **Easy to test**: Add mirror_config to client, experiment with `use_mirror_serving=True` on select queries

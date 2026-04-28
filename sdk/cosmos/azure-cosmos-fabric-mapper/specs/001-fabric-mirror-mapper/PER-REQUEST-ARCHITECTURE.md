# Architecture Update: Per-Request Mirror Serving Control

**Date**: February 2, 2026  
**Status**: Implemented in SDK Integration Guide  
**Impact**: SDK Integration Implementation Only (No Mapper Code Changes)

## Change Summary

**Previous Architecture** (Client-Level Control):
```python
# ALL queries routed to mirror when enabled
client = CosmosClient(url="...", credential=..., enable_mirror_serving=True, mirror_config={...})
items = container.query_items(query="SELECT * FROM c")  # Goes to mirror
```

**New Architecture** (Per-Request Control):
```python
# Mirror config provided, but each query decides where to go
client = CosmosClient(url="...", credential=..., mirror_config={...})

# Point read from Cosmos DB
item = container.query_items(query="SELECT * FROM c WHERE c.id = @id", use_mirror_serving=False)

# Aggregation from Fabric mirror
count = container.query_items(query="SELECT VALUE COUNT(1) FROM c", use_mirror_serving=True)
```

## Rationale

**Problem with Client-Level Control**:
- All-or-nothing: either ALL queries use mirror, or NONE do
- No way to optimize individual query routing
- Point reads forced through mirror even when Cosmos DB would be faster
- Expensive aggregations forced through Cosmos DB even when Fabric would be cheaper

**Benefits of Per-Request Control**:
- ✅ **Fine-grained optimization**: Route expensive queries to Fabric, fast queries to Cosmos
- ✅ **Gradual adoption**: Test mirror serving on select queries before full rollout
- ✅ **Cost optimization**: Use cheap Fabric mirror for analytics, use Cosmos for transactional workloads
- ✅ **Flexibility**: Change routing decision per query without redeploying

## What Changed

### 1. SDK Integration Implementation Guide
**File**: `specs/001-fabric-mirror-mapper/contracts/sdk-integration-implementation.md`

**Changes**:
- ❌ Removed: `enable_mirror_serving` client-level flag
- ✅ Added: `use_mirror_serving` per-request parameter on `query_items()`
- ✅ Updated: All usage examples to show per-request control
- ✅ Updated: Error messages to reflect per-request usage
- ✅ Updated: Test cases to validate per-request behavior

### 2. Mapper Code
**No changes required** - The mapper already supports being called or not called. It's agnostic to how the SDK decides when to invoke it.

### 3. Spec (User Story 1)
**File**: `specs/001-fabric-mirror-mapper/spec.md`

**Updated**:
- User Story 1 now emphasizes "selectively route queries on a per-request basis"
- Added Acceptance Scenario 2: Queries without mirror serving flag use Cosmos DB
- Added Acceptance Scenario 4: Optimize costs by routing queries appropriately

### 4. Plan
**File**: `specs/001-fabric-mirror-mapper/plan.md`

**Updated**:
- SDK integration section now describes per-request control
- Usage examples updated to show selective routing
- Testing strategy updated to validate per-request behavior

## Implementation in Cosmos SDK

### Client Constructor
```python
class CosmosClient:
    def __init__(
        self,
        url: str,
        credential: Any,
        mirror_config: Optional[Dict[str, Any]] = None,  # Optional config
    ):
        self._mirror_config = mirror_config
```

### Query Method
```python
class ContainerProxy:
    def query_items(
        self,
        query: str,
        parameters: Optional[List[Dict[str, Any]]] = None,
        use_mirror_serving: Optional[bool] = None,  # NEW PARAMETER
        **kwargs
    ) -> Iterable[Dict[str, Any]]:
        if use_mirror_serving:
            # Validate mirror_config exists
            # Delegate to mapper
            return execute_mirrored_query(query, parameters, self.client_connection._mirror_config)
        
        # Default: use Cosmos DB
        return self._query_items_original(query, parameters, **kwargs)
```

## Migration Impact

**Existing Code**: No impact - default behavior unchanged

**New Adoption Pattern**:
```python
# 1. Add mirror_config to client
client = CosmosClient(url="...", credential=..., mirror_config={...})

# 2. Selectively enable for expensive queries
analytical_results = container.query_items(
    query="SELECT VALUE COUNT(1) FROM c WHERE c.category = @cat",
    parameters=[{"name": "@cat", "value": "books"}],
    use_mirror_serving=True  # Use Fabric for aggregation
)

# 3. Keep point reads on Cosmos DB
item = container.query_items(
    query="SELECT * FROM c WHERE c.id = @id",
    parameters=[{"name": "@id", "value": "123"}],
    use_mirror_serving=False  # or omit parameter (default=False)
)
```

## Use Cases

| Query Type | Recommended Routing | Reason |
|------------|---------------------|--------|
| Point read (single partition) | Cosmos DB (`use_mirror_serving=False`) | Low latency, strong consistency |
| Aggregation (COUNT, SUM, AVG) | Fabric mirror (`use_mirror_serving=True`) | Cheaper, faster for analytics |
| ORDER BY | Fabric mirror (`use_mirror_serving=True`) | Not supported in Cosmos Python SDK today |
| Cross-partition scan | Fabric mirror (`use_mirror_serving=True`) | Cheaper for large scans |
| Write operation | Cosmos DB | Fabric mirror is read-only |
| Transactional query | Cosmos DB | Need strong consistency guarantees |

## Testing Requirements

SDK must validate:
1. ✅ Default behavior (no `use_mirror_serving`) uses Cosmos DB
2. ✅ `use_mirror_serving=False` explicitly uses Cosmos DB
3. ✅ `use_mirror_serving=True` without `mirror_config` raises clear error
4. ✅ `use_mirror_serving=True` with `mirror_config` delegates to mapper
5. ✅ Mapper package missing raises `MirrorServingNotAvailableError`

## Backward Compatibility

- ✅ **Zero breaking changes**: New optional parameter only
- ✅ **Default unchanged**: Existing code continues to work
- ✅ **Opt-in**: Must explicitly set `use_mirror_serving=True`
- ✅ **Clear errors**: Helpful messages when misconfigured

## Documentation Updates

All SDK integration examples now show per-request control:
- ✅ Quick start example
- ✅ Usage scenarios (3 scenarios)
- ✅ Test examples (3 test cases)
- ✅ Migration guide
- ✅ Error handling examples

## Next Steps

1. SDK team reviews updated integration guide
2. SDK team implements per-request routing in `query_items()`
3. SDK team adds unit tests for per-request behavior
4. Test with real workloads to validate routing decisions
5. Document best practices for when to use Cosmos vs Fabric

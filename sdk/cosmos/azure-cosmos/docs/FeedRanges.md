# Feed Ranges in the Python SDK for Azure Cosmos DB

Feed ranges represent a scope within a container, defined by a range of partition key hash values. They enable sub-container-level operations such as parallel query processing, scoped change feed consumption, and workload distribution across multiple workers.

For general information about partitioning, see:
- [Partitioning overview](https://learn.microsoft.com/azure/cosmos-db/partitioning-overview)
- [Partition Keys in the Python SDK](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md)

---

## What Are Feed Ranges?

A feed range is an opaque representation of a subset of data within a container.  Each feed range corresponds to a contiguous range of partition key hash values.  The set of all feed ranges returned by `read_feed_ranges()` covers the entire container without overlap, and every item belongs to exactly one feed range.

> **Important:** Feed ranges are returned as `dict[str, Any]` values and must be treated as opaque.  
> Do **not** manually construct, parse, or depend on the internal structure of a feed range dictionary.  
> Use only the container methods described below to create, compare, and consume feed ranges.

---

## When to Use Feed Ranges

| Scenario | Description |
|----------|-------------|
| **Parallel query processing** | Read all feed ranges, then query each range independently across multiple workers. Each worker processes a non-overlapping subset of the data. |
| **Scoped change feed** | Consume the change feed for a specific feed range rather than the entire container, enabling fan-out architectures for change processing. |
| **Workload distribution** | Assign feed ranges to different threads, processes, or machines to distribute work evenly across a container's data. |
| **Session token management** | Track session tokens per feed range for fine-grained session consistency when managing your own session tokens across multiple clients. |
| **Partition key to feed range mapping** | Convert partition key values to feed ranges to determine which worker or scope a specific partition key belongs to. |

---

## API Reference

### `read_feed_ranges()`

Returns all feed ranges for the container. The number of feed ranges corresponds to the number of physical partitions.

```python
# Sync
feed_ranges = list(container.read_feed_ranges())

# Async
feed_ranges = [fr async for fr in container.read_feed_ranges()]
```

**Parameters:**
- `force_refresh` *(bool, optional)* – When `True`, refreshes the cached partition key ranges before returning. Use this after a known partition split. Default: `False`.

**Returns:** `Iterable[dict[str, Any]]` (sync) / `AsyncIterable[dict[str, Any]]` (async)

---

### `feed_range_from_partition_key()`

Converts a partition key value to its corresponding feed range. Useful for determining which feed range a specific partition key belongs to.

```python
# Sync
feed_range = container.feed_range_from_partition_key("Seattle")

# Async
feed_range = await container.feed_range_from_partition_key("Seattle")
```

**Parameters:**
- `partition_key` *(PartitionKeyType)* – The partition key value. If set to `None`, returns the feed range for partition keys with JSON null. See [Partition Keys](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md) for supported value types.

**Returns:** `dict[str, Any]`

---

### `is_feed_range_subset()`

Checks whether one feed range is fully contained within another.

```python
# Sync
is_subset = container.is_feed_range_subset(
    parent_feed_range=container_feed_range,
    child_feed_range=pk_feed_range
)

# Async
is_subset = await container.is_feed_range_subset(
    parent_feed_range=container_feed_range,
    child_feed_range=pk_feed_range
)
```

**Parameters:**
- `parent_feed_range` *(dict[str, Any])* – The feed range to test as the superset.
- `child_feed_range` *(dict[str, Any])* – The feed range to test as the subset.

**Returns:** `bool` – `True` if the child feed range is fully contained within the parent.

---

### `query_items()` with `feed_range`

Scopes a SQL query to a specific feed range. This is useful for parallel query execution where each worker queries a different feed range.

```python
# Sync
items = list(container.query_items(
    query="SELECT * FROM c WHERE c.status = 'active'",
    feed_range=feed_range
))

# Async
items = [item async for item in container.query_items(
    query="SELECT * FROM c WHERE c.status = 'active'",
    feed_range=feed_range
)]
```

> **Note:** `feed_range` and `partition_key` are **mutually exclusive** parameters.  
> Providing both will raise a `ValueError`.

---

### `query_items_change_feed()` with `feed_range`

Scopes change feed consumption to a specific feed range. This enables fan-out architectures where each worker processes changes for a non-overlapping subset of the container.

```python
# Sync
response = container.query_items_change_feed(
    feed_range=feed_range,
    start_time="Beginning"
)
for item in response:
    process(item)

# Async
response = container.query_items_change_feed(
    feed_range=feed_range,
    start_time="Beginning"
)
async for item in response:
    process(item)
```

> **Note:** `feed_range`, `partition_key`, and `partition_key_range_id` are **mutually exclusive** parameters.

---

### `get_latest_session_token()`

Gets the most up-to-date session token for a specific feed range from a list of session token and feed range pairs. This is a **provisional** API intended for advanced session token management scenarios.

```python
# Sync
session_token = container.get_latest_session_token(
    feed_ranges_to_session_tokens=[(feed_range, token), ...],
    target_feed_range=target_feed_range
)

# Async (must be awaited)
session_token = await container.get_latest_session_token(
    feed_ranges_to_session_tokens=[(feed_range, token), ...],
    target_feed_range=target_feed_range
)
```

> **Note:** In the async client, `get_latest_session_token()` is a coroutine and **must be awaited**.

See the [session_token_management.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/session_token_management.py) (sync) and [session_token_management_async.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/session_token_management_async.py) (async) samples for complete examples.

---

## Feed Ranges vs. Partition Keys

Feed ranges and partition keys both define a scope within a container, but they operate at different levels:

| | Partition Key | Feed Range |
|---|---|---|
| **Granularity** | A single logical partition (one partition key value) | Zero, one, or many logical partitions (a hash range) |
| **Source** | Defined by your data model; you supply the value | Returned by `read_feed_ranges()` or derived from a partition key |
| **Relationship** | A partition key maps to exactly one feed range | A feed range can contain multiple partition keys |
| **Use case** | Point reads, single-partition queries | Parallel processing, scoped change feed, workload distribution |

You can convert between them:
```python
# Partition key → Feed range
feed_range = container.feed_range_from_partition_key("my_partition_key")

# Check which container feed range contains a partition key's feed range
for container_fr in container.read_feed_ranges():
    if container.is_feed_range_subset(container_fr, feed_range):
        print("Partition key belongs to this feed range")
        break
```

---

## Important Considerations

### Feed Ranges Are Opaque
Feed ranges are returned as `dict[str, Any]`. Their internal structure may change between SDK versions. Always use the provided API methods rather than constructing or parsing feed range dictionaries.

### Serialization for Storage
If you need to persist feed ranges (e.g., to assign ranges to workers across restarts), you can safely serialize them with `json.dumps()` and deserialize with `json.loads()`:

```python
import json

# Serialize for storage
serialized = json.dumps(feed_range)

# Deserialize for later use
feed_range = json.loads(serialized)
```

### Partition Splits and Stale Feed Ranges
As your container's data grows, physical partitions may split, changing the set of feed ranges. The SDK handles stale feed ranges gracefully:

- **Queries with `feed_range`**: The SDK automatically resolves stale feed ranges and routes the query correctly.
- **Change feed with `feed_range`**: The SDK detects "feed range gone" conditions and transparently handles the split.
- **To get updated feed ranges**: Call `container.read_feed_ranges(force_refresh=True)`.

### Mutual Exclusivity
When using feed ranges with `query_items()` or `query_items_change_feed()`, the `feed_range` parameter is mutually exclusive with `partition_key` (and `partition_key_range_id` for change feed). Providing both will raise a `ValueError`.

---

## Samples

For complete, runnable examples, see:
- [feed_range_management.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/feed_range_management.py) – Sync sample covering all feed range operations
- [feed_range_management_async.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/feed_range_management_async.py) – Async sample with `asyncio.gather()` for parallel processing
- [session_token_management.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/session_token_management.py) – Session token management using feed ranges

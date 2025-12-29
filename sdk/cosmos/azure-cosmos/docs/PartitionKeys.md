# Partition Keys in the Python SDK for Azure Cosmos DB

Partition keys determine how your data is logically distributed across physical partitions for scalability and performance in Azure Cosmos DB. Selecting an appropriate partition key is one of the most important design decisions you will make when modeling data.

For general best practices, see:
- [Choosing a partition key](https://learn.microsoft.com/azure/cosmos-db/partitioning-overview#choose-a-partition-key)

---
## Defining a Partition Key on Container Creation
When you create a container you must define its partition key path (e.g. `/partition_key`). You may also specify the hashing algorithm kind and version (e.g. Hash v2). Use the `PartitionKey` class:

```python
from azure.cosmos import PartitionKey

container = database.create_container_if_not_exists(
    id="items",
    partition_key=PartitionKey(path="/partition_key", kind="Hash", version=2)
)
```

---
## Supplying Partition Key Values for Container Operations
You can provide the partition key value in two ways for container APIs depending on the operation:

1. Pass the value explicitly via the `partition_key` parameter:
   ```python
   document = {
       'id': 'item_id',
       'partition_key': 'partition_key_value',
       'otherProperty': 'value'
   }
   container.read_item(item=document['id'], partition_key=document['partition_key'])
   ```
2. Embed the partition key property in the document you supply via `body` (the SDK extracts it):
   ```python
   doc = {"id": "item_id", "partition_key": "partition_key_value", "otherProperty": "value"}
   container.create_item(body=doc)
   ```

---
## Valid Partition Key Value Types
The SDK accepts a broad set of types for a single (logical) partition key component:
```python
Union[None, bool, float, int, str, Type[NonePartitionKeyValue], Type[NullPartitionKeyValue], Sequence[Union[str, int, float, bool, None]]
```
These include two special sentinel values that disambiguate absence vs explicit null:

- **`NonePartitionKeyValue`**: Indicates the partition key property is **absent** in the stored item (the property was omitted).
- **`NullPartitionKeyValue`**: Indicates the partition key property exists and its JSON value is **null**.

> Why two sentinels? Python `None` can mean either "explicitly null" *or* "perform a cross-partition operation" depending on the API. These sentinels remove ambiguity.

---
## Creating Items with Special Partition Key States

### Item with NO partition key property (use `NonePartitionKeyValue` for reads)
Omit the property when creating the item:
```python
import azure.cosmos.partition_key as pk

doc = {"id": "item_without_pk"}  # no partition_key field
container.create_item(body=doc)

retrieved = container.read_item(item="item_without_pk", partition_key=pk.NonePartitionKeyValue)
```

### Item with an explicit JSON null partition key (use `NullPartitionKeyValue` OR `None` for most point ops)
Set the property to `None` in the Python dict:
```python
doc = {"id": "item_with_null_pk", "partition_key": None}
container.create_item(body=doc)

# Reads (point operations) – either works
a = container.read_item(item="item_with_null_pk", partition_key=None)  # treated as null value
b = container.read_item(item="item_with_null_pk", partition_key=pk.NullPartitionKeyValue)
```

---
## Choosing the Correct Value When Calling APIs
| Scenario | Use This Partition Key Argument |
|----------|---------------------------------|
| Item lacked the partition key property | `NonePartitionKeyValue` |
| Item has partition key explicitly null (JSON `null`) – point read / replace / delete | `None` OR `NullPartitionKeyValue` |
| Query constrained to the null value | `NullPartitionKeyValue` (NOT plain `None`) |
| Cross-partition query (scan all logical partitions) | `None` |

---
## Queries with None Caveat
For `query_items` and `query_conflicts`:
- Passing `partition_key=None` signals a **cross-partition** query. It does **not** filter to items whose key is null.
- To restrict to items whose partition key value is JSON null, you must pass `partition_key=pk.NullPartitionKeyValue`.

Example (query only null-key items):
```python
import azure.cosmos.partition_key as pk

results = list(container.query_items(
    query="SELECT * FROM c WHERE c.type = 'Example'",
    partition_key=pk.NullPartitionKeyValue
))
```

---
## Summary Decision Guide
- Omit property to create an item with *no* partition key value; later read with `NonePartitionKeyValue`.
- Set property to `None` to create an item whose partition key value is JSON null; read with `None` or `NullPartitionKeyValue`.
- Use `NullPartitionKeyValue` for queries targeting the null value.
- Use plain `None` for cross-partition queries.

---
## Related Links
- [Azure Cosmos DB partitioning overview](https://learn.microsoft.com/azure/cosmos-db/partitioning-overview)
- [SDK samples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/samples/README.md)

---

# Partition Keys In Python SDK for Azure Cosmos DB
Partition keys are used in Azure Cosmos DB to distribute data across multiple partitions for scalability and performance. 
A partition key is a property of your items that is used to determine the partition in which the item will be stored. 
Choosing an appropriate partition key is crucial for optimizing the performance and scalability of your Cosmos DB containers.
For the best practices on choosing a partition key, refer to the official documentation:
- [Choosing a partition key](https://learn.microsoft.com/azure/cosmos-db/partitioning-overview#choose-a-partition-key)

## Defining a Partition Key
When creating a new container, you must specify a partition key definition. This includes the partition key path, hashing algorithm, and version. 
This can be done using the `PartitionKey` class from the `azure.cosmos` module.

## Passing in Partition Keys For Container Operations
There are two ways to provide a partition key value when performing operations on items in a container:
1. Pass in the value directly to the `partition_key` parameter' of the API. 
   ```python
   container.read_item(item='item_id', partition_key='partition_key_value')
   ```
1. Pass in a document that contains the partition key property through the `body` parameter. 
   ```python
   document = {
       'id': 'item_id',
       'partition_key': 'partition_key_value',
       'otherProperty': 'value'
   }
   container.create_item(body=document)
   ```
### Partition Key Values
Partition key values can be of various types, here is the type hint for reference:
```python
Union[None, bool, float, int, str, Type[NonePartitionKeyValue], Type[NullPartitionKeyValue], _Empty, _Undefined]
```
There are two special types of partition key values:
- `NonePartitionKeyValue`: This value should be used when the partition key is not set in the item. 
  It indicates that the item does not have a value for the partition key property.
  - To create an item with no partition key value simply omit the partition key property from the document. This is 
    true for any operation that accepts the `body` parameter as input instead of using the `partition_key` parameter:
    ```python
    import azure.cosmos.partition_key as partition_key

    document = {
        'id': 'item_id',
    }
    container.create_item(body=document)
    ```
  - To read an item with no partition key value, use `NonePartitionKeyValue` as the partition key:
    ```python
    import azure.cosmos.partition_key as partition_key

    item = container.read_item(item='item_id', partition_key=partition_key.NonePartitionKeyValue)
    ```
- `NullPartitionKeyValue`: This value should be used when the partition key is explicitly set to `null` in the item. 
  - To create an item with a `null` partition key value, set the partition key property to `None` in the document.
    This is true for any operation that accepts the `body` parameter as input instead of using the `partition_key` parameter:
    ```python
    document = {
        'id': 'item_id',
        'partition_key': None,
    }
    container.create_item(body=document)
    ```
  - To read an item with a `null` partition key value, use `NullPartitionKeyValue` as the partition key. 
  Alternatively, you can also use `None`:
    ```python
    import azure.cosmos.partition_key as partition_key
    item = container.read_item(item='item_id', partition_key=partition_key.NullPartitionKeyValue)
    # or
    item = container.read_item(item='item_id', partition_key=None)
    ```


### Caveats with NullPartitionKeyValue 
For the `query_items` and `query_conflicts` operations, you have to use `NullPartitionKeyValue` to filter items with a `null` partition key value.
If you use `None`, it will NOT match items with a `null` partition key value instead it will perform a cross partition query.


   

**Is your feature request related to a problem? Please describe.**

It was widely discussed whether the event handler should receive a batch of events or a single event.
Currently in 5.0.0 GA JS' event handler accepts a list of events while other three languages use singe event.
In Dec 2019, Elena reached out to 11 customers that tried eventhubs track2 peviews. Receiving batch was one of the main wishes from customers. 
(Elena's email was sent on 12/16/2019 with title "Event Hubs SDK - customer outreach")


**Describe the solution you'd like**

Currently Python has `EventHubConsumerClient.receive(on_event, **kwargs)`.
The new feature will add new method `receive_batch(on_event_batch, **kwargs)` into `EventHubConsumerClient`. 
It calls the user callback on_event_batch(partition_context, event_batch).
For flow control, the kwargs will have three parameters - `prefetch` for link credit size, `max_batch_size` and max_wait_time.
max_batch_size is the expected size of the list of events within the max_wait_time. 
max_wait_time determines the longest waiting time between two calls of user callback `on_event_batch`.  `receive_batch` accumulates events up to max_batch_size and call `on_event_batch` within max_wait_time and call the callback with the list of events (could be an empty list).

A 0 max_wait_time means not to wait and call the callback function immediately with at most one fetch from the event hub. If the number of pre-fetched events is larger than the max_batch_size, there is no need to fetch. Otherwise fetch only once from the event hub and call the callback with up to max_batch_size events. 

Usually `on_event_batch` should have a list with size max_batch_size. But it may have an empty list of events or fewer than max_batch_size list.

A user can call both `receive` and `receive_batch` from one `EventHubConsumerClient`.

API is
```python
class EventHubConsumerClient(ClientBase):

    ...

    async def receive_batch(
        self,
        on_event_batch: Callable[["PartitionContext", List["EventData"]], Awaitable[None]],
        max_batch_size: int, 
        max_wait_time: float,
        *,
        partition_id: Optional[str] = None,
        owner_level: Optional[int] = None,
        prefetch: int = 300,
        track_last_enqueued_event_properties: bool = False,
        starting_position: Optional[
            Union[str, int, datetime.datetime, Dict[str, Any]]
        ] = None,
        starting_position_inclusive: Union[bool, Dict[str, bool]] = False,
        on_error: Optional[
            Callable[["PartitionContext", Exception], Awaitable[None]]
        ] = None,
        on_partition_initialize: Optional[
            Callable[["PartitionContext"], Awaitable[None]]
        ] = None,
        on_partition_close: Optional[
            Callable[["PartitionContext", "CloseReason"], Awaitable[None]]
        ] = None
    ) -> None:
```
**Sample code**
```python
import asyncio
import os
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]
BLOB_CONTAINER_NAME = "your-blob-container-name"  # Please make sure the blob container resource exists.


async def on_event_batch(partition_context, event_batch):
    if event_batch:
        print("Received events from partition: {}.".format(partition_context.partition_id))
        # Put your code here.

        await partition_context.update_checkpoint(event_batch[-1])
    else:
        # this is a heartbeat. Do something if you want.
        pass


async def receive(client):
    """
    Without specifying partition_id, the receive will try to receive events from all partitions and if provided with
    a checkpoint store, the client will load-balance partition assignment with other EventHubConsumerClient instances
    which also try to receive events from all partitions and use the same storage resource.
    """
    await client.receive_batch(
        on_event=on_event_batch,
        max_batch_size=100,
        max_wait_time=3,
        starting_position="-1",  # "-1" is from the beginning of the partition.
    )
    # With specified partition_id, load-balance will be disabled, for example:
    # await client.receive_batch(on_event_batch=on_event_batch, max_batch_size=100, max_wait_time=3, partition_id='0'))


async def main():
    checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION_STR, BLOB_CONTAINER_NAME)
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        consumer_group="$Default",
        checkpoint_store=checkpoint_store,  # For load-balancing and checkpoint. Leave None for no load-balancing.
    )
    async with client:
        await receive(client)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

**Describe alternatives you've considered**
1. Make `EventHubConsumerClient.receive(on_event, **kwargs)` to have a "batch" mode. on_event can accept either an single event or a batch. But this will add complexity to specific users. A single user will use either receive_batch, or receive. Plus, max_batch_size will be meaningless for singe event callback.

**Additional context**
None
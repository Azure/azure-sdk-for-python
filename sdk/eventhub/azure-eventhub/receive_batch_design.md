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

Refer to _consumer_client_async.pyi of this PR for API

**Sample code**
Refer to recv_batch_with_checkpoint_async.py of this PR

**Describe alternatives you've considered**
1. Make `EventHubConsumerClient.receive(on_event, **kwargs)` to have a "batch" mode. on_event can accept either an single event or a batch. But this will add complexity to specific users. A single user will use either receive_batch, or receive. Plus, max_batch_size will be meaningless for singe event callback.

**Additional context**
None
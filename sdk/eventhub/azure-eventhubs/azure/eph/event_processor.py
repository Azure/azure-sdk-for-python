from typing import Callable
import uuid
import asyncio
from azure.eventhub import EventPosition, EventHubError
from azure.eventhub.aio import EventHubClient
from ._cancellation_token import CancellationToken
from .checkpoint_manager import CheckpointManager
from .partition_manager import PartitionManager
from .partition_processor import PartitionProcessor


class EventProcessor(object):
    def __init__(self, consumer_group_name: str, eventhub_client: EventHubClient,
                 partition_processor_callable: Callable[[str, str, str, CheckpointManager], PartitionProcessor],
                 partition_manager: PartitionManager, **kwargs):
        """

        :param consumer_group_name:
        :param eventhub_client:
        :param partition_processor_callable:
        :param partition_manager:
        :param initial_event_position:
        :param max_batch_size:
        """
        self.consumer_group_name = consumer_group_name
        self.eventhub_client = eventhub_client
        self.eventhub_name = eventhub_client.eh_name
        self.partition_processor_callable = partition_processor_callable
        self.partition_manager = partition_manager
        self.initial_event_position = kwargs.get("initial_event_position", "-1")
        self.max_batch_size = kwargs.get("max_batch_size", 300)
        self.max_wait_time = kwargs.get("max_wait_time")
        self.tasks = []
        self.cancellation_token = CancellationToken()
        self.instance_id = str(uuid.uuid4())
        self.partition_ids = None

    async def start(self):
        client = self.eventhub_client
        partition_ids = await client.get_partition_ids()
        self.partition_ids = partition_ids

        claimed_list = await self._claim_partitions()
        await self._start_claimed_partitions(claimed_list)

    async def stop(self):
        self.cancellation_token.cancel()
        await self.partition_manager.close()

    async def _claim_partitions(self):
        partitions_ownership = await self.partition_manager.list_ownership(self.eventhub_name, self.consumer_group_name)
        partitions_ownership_dict = dict()
        for ownership in partitions_ownership:
            partitions_ownership_dict[ownership["partition_id"]] = ownership

        to_claim_list = []
        for pid in self.partition_ids:
            p_ownership = partitions_ownership_dict.get(pid)
            if p_ownership:
                to_claim_list.append(p_ownership)
            else:
                new_ownership = dict()
                new_ownership["eventhub_name"] = self.eventhub_name
                new_ownership["consumer_group_name"] = self.consumer_group_name
                new_ownership["instance_id"] = self.instance_id
                new_ownership["partition_id"] = pid
                new_ownership["owner_level"] = 1  # will increment in preview 3
                to_claim_list.append(new_ownership)
        claimed_list = await self.partition_manager.claim_ownership(to_claim_list)
        return claimed_list

    async def _start_claimed_partitions(self, claimed_partitions):
        consumers = []
        for partition in claimed_partitions:
            partition_id = partition["partition_id"]
            offset = partition.get("offset")
            offset = offset or self.initial_event_position
            consumer = self.eventhub_client.create_consumer(self.consumer_group_name, partition_id,
                                                            EventPosition(str(offset)))
            consumers.append(consumer)

            partition_processor = self.partition_processor_callable(
                eventhub_name=self.eventhub_name,
                consumer_group_name=self.consumer_group_name,
                partition_id=partition_id,
                checkpoint_manager=CheckpointManager(partition_id, self.eventhub_name, self.consumer_group_name,
                                                     self.instance_id, self.partition_manager)
            )

            loop = asyncio.get_running_loop()
            task = loop.create_task(
                _receive(consumer, partition_processor, self.max_wait_time, self.cancellation_token))
            self.tasks.append(task)

        await asyncio.gather(*self.tasks)
        await asyncio.gather(*[consumer.close() for consumer in consumers])


async def _receive(partition_consumer, partition_processor, max_wait_time, cancellation_token):
    try:
        async with partition_consumer:
            while not cancellation_token.is_cancelled:
                events = await partition_consumer.receive(timeout=max_wait_time)
                await partition_processor.process_events(events)
            else:
                await partition_processor.close(reason="Cancelled")
                await partition_consumer.close()
    except EventHubError as eh_err:
        await partition_consumer.close()
        await partition_processor.close(reason=eh_err)
    except Exception as err:
        await partition_processor.process_error(err)

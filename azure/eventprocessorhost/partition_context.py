# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------
import asyncio
import logging
from eventprocessorhost.checkpoint import Checkpoint

class PartitionContext:
    """
    Encapsulates information related to an Event Hubs partition used by AbstractEventProcessor
    """
    def __init__(self, host, partition_id, eh_path, consumer_group_name, pump_loop=None):
        self.host = host
        self.partition_id = partition_id
        self.eh_path = eh_path
        self.consumer_group_name = consumer_group_name
        self.offset = "-1"
        self.sequence_number = 0
        self.lease = None
        self.pump_loop = pump_loop or asyncio.get_event_loop()

    def set_offset_and_sequence_number(self, event_data):
        """
        Updates offset based on event
        """
        if not event_data:
            raise Exception(event_data)
        self.offset = event_data.offset
        self.sequence_number = event_data.sequence_number

    async def get_initial_offset_async(self): # throws InterruptedException, ExecutionException
        """
        Returns the initial offset for processing the partition.
        """
        logging.info("Calling user-provided initial offset provider %s %s",
                     self.host.guid, self.partition_id)
        starting_checkpoint = await self.host.storage_manager\
                                        .get_checkpoint_async(self.partition_id)
        if not starting_checkpoint:
            # No checkpoint was ever stored. Use the initialOffsetProvider instead
            # defaults to "-1"
            self.offset = self.host.eph_options.initial_offset_provider
            self.sequence_number = -1
        else:
            self.offset = starting_checkpoint.offset
            self.sequence_number = starting_checkpoint.sequence_number

        logging.info("%s %s Initial offset/sequenceNumber provided %s/%s",
                     self.host.guid, self.partition_id, self.offset, self.sequence_number)
        return self.offset

    async def checkpoint_async(self):
        """
        Generates a checkpoint for the partition using the curren offset and sequenceNumber for
        and persists to the checkpoint manager
        """
        captured_checkpoint = Checkpoint(self.partition_id, self.offset, self.sequence_number)
        await self.persist_checkpoint_async(captured_checkpoint)

    async def checkpoint_async_event_data(self, event_data):
        """
        Stores the offset and sequenceNumber from the provided received EventData instance,
        then writes those values to the checkpoint store via the checkpoint manager.
        (Params) eventData :A received EventData with valid offset and sequenceNumber
        Throws ArgumentNullException If suplied eventData is null
        Throws ArgumentOutOfRangeException If the sequenceNumber is less than the
        last checkpointed value
        """
        if not event_data:
            raise ValueError("event_data")
        if event_data.sequence_number > self.sequence_number:
            #We have never seen this sequence number yet
            raise ValueError("Argument Out Of Range event_data x-opt-sequence-number")

        await self.persist_checkpoint_async(Checkpoint(self.partition_id,
                                                       event_data.offset,
                                                       event_data.sequence_number))

    def to_string(self):
        """
        Returns the parition context in the following format:
        "PartitionContext({EventHubPath}{ConsumerGroupName}{PartitionId}{SequenceNumber})"
        """
        return "PartitionContext({}{}{}{})".format(self.eh_path,
                                                   self.consumer_group_name,
                                                   self.partition_id,
                                                   self.sequence_number)

    async def persist_checkpoint_async(self, checkpoint):
        """
        Persists the checkpoint
        """
        logging.debug("PartitionPumpCheckpointStart %s %s %s %s",
                      self.host.guid, checkpoint.partition_id,
                      checkpoint.offset, checkpoint.sequence_number)
        try:
            in_store_checkpoint = await self.host.storage_manager \
                                                 .get_checkpoint_async(checkpoint.partition_id)
            if not in_store_checkpoint \
               or checkpoint.sequence_number >= in_store_checkpoint.sequence_number:
                if not in_store_checkpoint:
                    logging.info("persisting checkpoint %s", str(checkpoint.__dict__))
                    await self.host.storage_manager \
                              .create_checkpoint_if_not_exists_async(checkpoint.partition_id)

                await self.host.storage_manager.update_checkpoint_async(self.lease, checkpoint)
                self.lease.offset = checkpoint.offset
                self.lease.sequence_number = checkpoint.sequence_number
            else:
                msg = "Ignoring out of date checkpoint with offset %s/sequence number %s because \
                       current persisted checkpoint has higher offset %s/sequence number %s"
                logging.error(msg, checkpoint.offset, checkpoint.sequence_number,
                              in_store_checkpoint.offset, in_store_checkpoint.sequence_number)
                raise Exception("offset/sequenceNumber invalid")

        except Exception as err:
            logging.error("PartitionPumpCheckpointError %s %s %s",
                          self.host.guid, checkpoint.partition_id, repr(err))
            raise
        finally:
            logging.debug("PartitionPumpCheckpointStop %s %s",
                          self.host.guid, checkpoint.partition_id)

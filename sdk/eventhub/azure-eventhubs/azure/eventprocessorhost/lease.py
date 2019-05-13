# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------


class Lease:
    """
    Lease contains partition processing state metadata used to manage partition state.
    """

    def __init__(self):
        self.partition_id = None
        self.sequence_number = None
        self.owner = None
        self.token = None
        self.epoch = 0
        self.event_processor_context = None

    def with_partition_id(self, partition_id):
        """
        Init with partition Id.

        :param partition_id: ID of a given partition.
        :type partition_id: str
        """
        self.partition_id = partition_id
        self.owner = None
        self.token = None
        self.epoch = 0
        self.event_processor_context = None

    def with_source(self, lease):
        """
        Init with existing lease.

        :param lease: An existing Lease.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        """
        self.partition_id = lease.partition_id
        self.epoch = lease.epoch
        self.owner = lease.owner
        self.token = lease.token
        self.event_processor_context = lease.event_processor_context

    async def is_expired(self):
        """
        Determines whether the lease is expired. By default lease never expires.
        Deriving class implements the lease expiry logic.

        :rtype: bool
        """
        return False

    def increment_epoch(self):
        """
        Increment lease epoch.
        """
        self.epoch += 1
        return self.epoch

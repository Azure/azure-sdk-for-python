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

    def with_partition_id(self, partition_id):
        """
        Init with partition Id
        """
        self.partition_id = partition_id
        self.owner = None
        self.token = None
        self.epoch = 0

    def with_source(self, lease):
        """
        Init with existing lease
        """
        self.partition_id = lease.partition_id
        self.epoch = lease.epoch
        self.owner = lease.owner
        self.token = lease.token

    def is_expired(self):
        """
        Determines whether the lease is expired. By default lease never expires.
        Deriving class implements the lease expiry logic.
        """
        return False

    def increment_epoch(self):
        """
        Increment lease epoch
        """
        self.epoch += 1
        return self.epoch
    
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import asyncio
import json

from azure.eventprocessorhost.lease import Lease


class AzureBlobLease(Lease):
    """
    Azure Blob Lease
    """

    def __init__(self):
        """
        Init Azure Blob Lease.
        """
        super()
        Lease.__init__(self)
        self.offset = None
        self.state = lambda: None

    def serializable(self):
        """
        Returns Serialiazble instance of `__dict__`.
        """
        serial = self.__dict__.copy()
        del serial['state']
        return serial

    def with_lease(self, lease):
        """
        Init with exisiting lease.
        """
        super().with_source(lease)

    def with_blob(self, blob):
        """
        Init Azure Blob Lease with existing blob.
        """
        content = json.loads(blob.content)
        self.partition_id = content["partition_id"]
        self.owner = content["owner"]
        self.token = content["token"]
        self.epoch = content["epoch"]
        self.offset = content["offset"]
        self.sequence_number = content["sequence_number"]
        self.event_processor_context = content.get("event_processor_context")

    def with_source(self, lease):
        """
        Init Azure Blob Lease from existing.
        """
        super().with_source(lease)
        self.offset = lease.offset
        self.sequence_number = lease.sequence_number

    async def is_expired(self):
        """
        Check and return Azure Blob Lease state using Storage API.
        """
        if asyncio.iscoroutinefunction(self.state):
            current_state = await self.state()
        else:
            current_state = self.state()
        if current_state:
            return current_state != "leased"
        return False
    
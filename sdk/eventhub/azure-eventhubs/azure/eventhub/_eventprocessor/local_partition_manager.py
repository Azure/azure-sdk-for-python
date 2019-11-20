# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from .sqlite3_partition_manager import Sqlite3PartitionManager


class InMemoryPartitionManager(Sqlite3PartitionManager):
    """A partition manager that stores checkpoint and load balancer partition ownership data in memory.
    This is for mock test only.

    """
    def __init__(self):
        super(InMemoryPartitionManager, self).__init__(db_filename=":memory:")


class FileBasedPartitionManager(Sqlite3PartitionManager):
    """A partition manager that stores checkpoint and load balancer partition ownership data in a file.
    Do not use this

    """
    def __init__(self, filename):
        super(FileBasedPartitionManager, self).__init__(db_filename=filename)

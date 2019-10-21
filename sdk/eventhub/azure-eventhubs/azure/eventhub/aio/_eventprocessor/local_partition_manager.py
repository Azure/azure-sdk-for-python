# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from .sqlite3_partition_manager import Sqlite3PartitionManager


class InMemoryPartitionManager(Sqlite3PartitionManager):
    def __init__(self):
        super(InMemoryPartitionManager, self).__init__(db_filename=":memory:")


class FileBasedPartitionManager(Sqlite3PartitionManager):
    def __init__(self, filename):
        super(FileBasedPartitionManager, self).__init__(db_filename=filename)

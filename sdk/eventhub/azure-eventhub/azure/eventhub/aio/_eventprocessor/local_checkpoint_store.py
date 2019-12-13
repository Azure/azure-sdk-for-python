# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from .sqlite3_checkpoint_store import Sqlite3CheckpointStore


class InMemoryCheckpointStore(Sqlite3CheckpointStore):
    """A checkpoint store that stores checkpoint and load balancer partition ownership data in memory.
    This is for mock test only.

    """
    def __init__(self) -> None:
        super(InMemoryCheckpointStore, self).__init__(db_filename=":memory:")


class FileBasedCheckpointStore(Sqlite3CheckpointStore):
    """A checkpoint store that stores checkpoint and load balancer partition ownership data in a file.
    This is for internal test only.

    """
    def __init__(self, filename: str) -> None:
        super(FileBasedCheckpointStore, self).__init__(db_filename=filename)

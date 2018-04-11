# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import asyncio


def test_get_partition_ids(partition_manager):
    """
    Test that partition manger returns all the partitions for an event hub
    """
    loop = asyncio.get_event_loop()
    pids = loop.run_until_complete(partition_manager.get_partition_ids_async())
    assert pids == ["0", "1"]

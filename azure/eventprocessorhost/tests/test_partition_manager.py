# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import asyncio
import sys


def test_get_partition_ids(partition_manager):
    """
    Test that partition manger returns all the partitions for an event hub
    """
    sys.excepthook = _execpt_hook
    loop = asyncio.get_event_loop()
    is_live, mgr = partition_manager
    if is_live:
        pids = loop.run_until_complete(mgr.get_partition_ids_async())
        assert pids == ["0", "1"]

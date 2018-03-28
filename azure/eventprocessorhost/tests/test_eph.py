# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import asyncio


def test_eph_start(eph):
    """
    Test that the processing host starts correctly
    """
    is_live, host = eph
    loop = asyncio.get_event_loop()
    if is_live:
        loop.run_until_complete(host.open_async())
        loop.run_until_complete(host.close_async())

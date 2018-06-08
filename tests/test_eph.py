# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import asyncio
import pytest


def test_eph_start(eph):
    """
    Test that the processing host starts correctly
    """
    pytest.skip("Not working yet")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(eph.open_async())
    loop.run_until_complete(eph.close_async())

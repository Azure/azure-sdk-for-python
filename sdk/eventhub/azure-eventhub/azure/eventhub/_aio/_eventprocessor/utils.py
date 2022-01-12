# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import asyncio


def get_running_loop() -> asyncio.AbstractEventLoop:
    try:
        return asyncio.get_running_loop()
    except AttributeError:  # 3.5 / 3.6
        loop = (
            asyncio._get_running_loop()  # pylint: disable=protected-access, no-member
        )
        if loop is None:
            raise RuntimeError("No running event loop")
        return loop

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
from typing import Type


def get_running_async_lock_class() -> Type:
    """Get a lock class from the async library that the current context is running under.

    :return: The running async library's Lock class.
    :rtype: Type[Lock]
    :raises RuntimeError: if the current context is not running under an async library.
    """

    try:
        import asyncio  # pylint: disable=do-not-import-asyncio

        # Check if we are running in an asyncio event loop.
        asyncio.get_running_loop()
        return asyncio.Lock
    except RuntimeError as err:
        # Otherwise, assume we are running in a trio event loop if it has already been imported.
        if "trio" in sys.modules:
            import trio  # pylint: disable=networking-import-outside-azure-core-transport

            return trio.Lock
        raise RuntimeError("An asyncio or trio event loop is required.") from err

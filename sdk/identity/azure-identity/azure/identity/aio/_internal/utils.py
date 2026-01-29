# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
from functools import cache
from typing import Type


@cache
def get_running_async_library() -> str:
    """Get the name of the async library that the current context is running under.

    :return: The name of the running async library.
    :rtype: str
    :raises RuntimeError: if the current context is not running under an async library.
    """

    try:
        import asyncio  # pylint: disable=do-not-import-asyncio

        # Check if we are running in an asyncio event loop.
        asyncio.get_running_loop()
        return "asyncio"
    except RuntimeError as err:
        # Otherwise, assume we are running in a trio event loop if it has already been imported.
        if "trio" in sys.modules:
            return "trio"
        raise RuntimeError("An asyncio or trio event loop is required.") from err


def get_running_async_lock_class() -> Type:
    """Get a lock class from the async library that the current context is running under.

    :return: The running async library's Lock class.
    :rtype: Type[Lock]
    :raises RuntimeError: if the current context is not running under an async library.
    """
    if get_running_async_library() == "trio":
        import trio  # pylint: disable=networking-import-outside-azure-core-transport,import-error

        return trio.Lock

    import asyncio  # pylint: disable=do-not-import-asyncio

    return asyncio.Lock


def get_current_loop_id() -> int:
    """Get an identifier for the current async loop.

    :return: An identifier for the current async loop.
    :rtype: int
    :raises RuntimeError: if the current context is not running under an async library.
    """
    if get_running_async_library() == "trio":
        import trio  # pylint: disable=networking-import-outside-azure-core-transport,import-error

        return id(trio.lowlevel.current_trio_token())

    import asyncio  # pylint: disable=do-not-import-asyncio

    return id(asyncio.get_running_loop())

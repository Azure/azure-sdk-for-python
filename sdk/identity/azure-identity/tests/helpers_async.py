# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import functools
from unittest import mock

from helpers import validating_transport


def get_completed_future(result=None):
    future = asyncio.Future()
    future.set_result(result)
    return future


def wrap_in_future(fn):
    """Return a completed Future whose result is the return of fn.

    Added to simplify using unittest.Mock in async code. Python 3.8's AsyncMock would be preferable.
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        return get_completed_future(result)

    return wrapper


class AsyncMockTransport(mock.MagicMock):
    """MagicMock with do-nothing aenter/exit, for mocking async transport.

    aenter/exit here return completed Futures so they needn't be declared async. If they were async functions,
    2.7 would raise SyntaxError on importing this module.

    3.9.0, or a future version of 3.8, will obviate this class by implementing aenter/exit on MagicMock
    (https://bugs.python.org/issue38093).
    """

    # pylint:disable=attribute-defined-outside-init

    async def __aenter__(self):
        self.entered = True

    async def __aexit__(self, *exc_info):
        self.exited = True


def async_validating_transport(requests, responses):
    sync_transport = validating_transport(requests, responses)
    return AsyncMockTransport(send=wrap_in_future(sync_transport.send))


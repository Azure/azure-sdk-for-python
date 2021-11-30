# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import TYPE_CHECKING

from uamqp.async_ops import ConnectionAsync

if TYPE_CHECKING:
    from uamqp.authentication import JWTTokenAsync

    try:
        from typing_extensions import Protocol
    except ImportError:
        Protocol = object  # type: ignore

    class ConnectionManager(Protocol):
        async def get_connection(
            self, host: str, auth: "JWTTokenAsync"
        ) -> ConnectionAsync:
            pass

        async def close_connection(self) -> None:
            pass

        async def reset_connection_if_broken(self) -> None:
            pass


class _SeparateConnectionManager(object):
    def __init__(self, **kwargs) -> None:
        pass

    async def get_connection(self, host: str, auth: "JWTTokenAsync") -> None:
        pass  # return None

    async def close_connection(self) -> None:
        pass

    async def reset_connection_if_broken(self) -> None:
        pass


def get_connection_manager(**kwargs) -> "ConnectionManager":
    return _SeparateConnectionManager(**kwargs)

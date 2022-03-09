# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import TYPE_CHECKING

from uamqp import Connection

if TYPE_CHECKING:
    from uamqp.authentication import JWTTokenAuth

    try:
        from typing_extensions import Protocol
    except ImportError:
        Protocol = object  # type: ignore

    class ConnectionManager(Protocol):
        def get_connection(self, host, auth):
            # type: (str, 'JWTTokenAuth') -> Connection
            pass

        def close_connection(self):
            pass

        def reset_connection_if_broken(self):
            pass


class _SeparateConnectionManager(object):
    def __init__(self, **kwargs):
        pass

    def get_connection(self, host, auth):  # pylint:disable=unused-argument, no-self-use
        # type: (str, JWTTokenAuth) -> None
        return None

    def close_connection(self):
        # type: () -> None
        pass

    def reset_connection_if_broken(self):
        # type: () -> None
        pass


def get_connection_manager(**kwargs):
    # type: (...) -> 'ConnectionManager'
    return _SeparateConnectionManager(**kwargs)

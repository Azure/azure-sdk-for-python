# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from __future__ import annotations
import sys

import asyncio
import logging
import functools
from typing import Dict, Optional, TYPE_CHECKING

from uamqp import authentication

from .._common.constants import JWT_TOKEN_SCOPE, TOKEN_TYPE_JWT, TOKEN_TYPE_SASTOKEN

if TYPE_CHECKING:
    from ..aio._servicebus_client_async import ServiceBusClient

_log = logging.getLogger(__name__)


def get_running_loop():
    try:
        return asyncio.get_running_loop()
    except AttributeError:  # 3.5 / 3.6
        loop = None
        try:
            loop = asyncio._get_running_loop()  # pylint: disable=protected-access
        except AttributeError:
            _log.warning(
                "This version of Python is deprecated, please upgrade to >= v3.5.3"
            )
        if loop is None:
            _log.warning("No running event loop")
            loop = asyncio.get_event_loop()
        return loop
    except RuntimeError:
        # For backwards compatibility, create new event loop
        _log.warning("No running event loop")
        return asyncio.get_event_loop()


async def create_authentication(client: ServiceBusClient):
    # pylint: disable=protected-access
    try:
        # ignore mypy's warning because token_type is Optional
        token_type = client._credential.token_type  # type: ignore
    except AttributeError:
        token_type = TOKEN_TYPE_JWT
    if token_type == TOKEN_TYPE_SASTOKEN:
        auth = authentication.JWTTokenAsync(
            client._auth_uri,
            client._auth_uri,
            # Since we have handled the token type, the type is already narrowed.
            functools.partial(client._credential.get_token, client._auth_uri),  # type: ignore
            token_type=token_type,
            timeout=client._config.auth_timeout,
            http_proxy=client._config.http_proxy,
            transport_type=client._config.transport_type,
            custom_endpoint_hostname=client._config.custom_endpoint_hostname,
            port=client._config.connection_port,
            verify=client._config.connection_verify
        )
        await auth.update_token()
        return auth
    return authentication.JWTTokenAsync(
        client._auth_uri,
        client._auth_uri,
        # Same as mentioned above.
        functools.partial(client._credential.get_token, JWT_TOKEN_SCOPE),  # type: ignore
        token_type=token_type,
        timeout=client._config.auth_timeout,
        http_proxy=client._config.http_proxy,
        transport_type=client._config.transport_type,
        refresh_window=300,
        custom_endpoint_hostname=client._config.custom_endpoint_hostname,
        port=client._config.connection_port,
        verify=client._config.connection_verify
    )


def get_dict_with_loop_if_needed(
    loop: Optional[asyncio.AbstractEventLoop],
) -> Dict[str, asyncio.AbstractEventLoop]:
    if sys.version_info >= (3, 10):
        if loop:
            raise ValueError(
                "Starting Python 3.10, asyncio no longer supports loop as a parameter."
            )
    elif loop:
        return {"loop": loop}
    return {}

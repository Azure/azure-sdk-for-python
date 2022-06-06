# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import sys

import asyncio
import logging
import functools

from uamqp import authentication

from .._common.constants import JWT_TOKEN_SCOPE, TOKEN_TYPE_JWT, TOKEN_TYPE_SASTOKEN


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


async def create_authentication(client):
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
            functools.partial(client._credential.get_token, client._auth_uri),
            token_type=token_type,
            timeout=client._config.auth_timeout,
            http_proxy=client._config.http_proxy,
            transport_type=client._config.transport_type,
        )
        await auth.update_token()
        return auth
    return authentication.JWTTokenAsync(
        client._auth_uri,
        client._auth_uri,
        functools.partial(client._credential.get_token, JWT_TOKEN_SCOPE),
        token_type=token_type,
        timeout=client._config.auth_timeout,
        http_proxy=client._config.http_proxy,
        transport_type=client._config.transport_type,
        refresh_window=300,
    )


def get_dict_with_loop_if_needed(loop):
    if sys.version_info >= (3, 10):
        if loop:
            raise ValueError(
                "Starting Python 3.10, asyncio no longer supports loop as a parameter."
            )
    elif loop:
        return {"loop": loop}
    return {}

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

"""asyncpg integration for SQLAlchemy asynchronous engines."""

from __future__ import annotations

from typing import Any

from azure.core.credentials_async import AsyncTokenCredential

try:
    from sqlalchemy.engine import URL, make_url
    from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
except ImportError as e:
    raise ImportError(
        "SQLAlchemy dependencies are not installed. Install them with: pip install azure-postgresql-auth[sqlalchemy]"
    ) from e

from azure_postgresql_auth.core import get_entra_conninfo_async
from azure_postgresql_auth.errors import CredentialValueError, EntraConnectionValueError


def create_asyncpg_engine(
    url: str | URL,
    credential: AsyncTokenCredential,
    **kwargs: Any,
) -> AsyncEngine:
    """Create an asyncpg SQLAlchemy engine authenticated with Microsoft Entra ID.

    The returned engine obtains Entra connection information asynchronously whenever
    SQLAlchemy creates a physical connection for its pool.

    :param url: SQLAlchemy URL using the ``postgresql+asyncpg`` dialect.
    :param credential: Credential used to acquire Microsoft Entra access tokens.
    :param kwargs: Keyword arguments forwarded to ``create_async_engine``. Values
        supplied through ``connect_args`` are forwarded to ``asyncpg.connect``.
    :return: An asynchronous SQLAlchemy engine.
    :raises ~azure_postgresql_auth.CredentialValueError: If ``credential`` is not an
        ``AsyncTokenCredential``.
    :raises ImportError: If ``asyncpg`` is not installed.
    """
    if not isinstance(credential, AsyncTokenCredential):
        raise CredentialValueError("credential is required and must be an AsyncTokenCredential for asyncpg")

    try:
        import asyncpg
    except ImportError as e:
        raise ImportError(
            "asyncpg dependencies are not installed. Install them with: pip install azure-postgresql-auth[asyncpg]"
        ) from e

    parsed_url = make_url(url)
    connect_args = parsed_url.translate_connect_args(username="user", database="database")
    connect_args.update(dict(parsed_url.query))
    connect_args.update(kwargs.pop("connect_args", {}))

    if "sslmode" in connect_args and "ssl" not in connect_args:
        connect_args["ssl"] = connect_args["sslmode"]
    connect_args.pop("sslmode", None)

    async def async_creator() -> Any:
        try:
            entra_conninfo = await get_entra_conninfo_async(credential)
        except Exception as e:
            raise EntraConnectionValueError("Could not retrieve Entra credentials") from e

        connection_kwargs = {
            **connect_args,
            "user": connect_args.get("user", entra_conninfo["user"]),
            "password": connect_args.get("password", entra_conninfo["password"]),
        }
        return await asyncpg.connect(**connection_kwargs)

    return create_async_engine(parsed_url, async_creator=async_creator, **kwargs)

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from __future__ import annotations

from typing import Any

from azure.core.credentials_async import AsyncTokenCredential
from azure_postgresql_auth.core import get_entra_conninfo_async
from azure_postgresql_auth.errors import (
    CredentialValueError,
    EntraConnectionValueError,
)

try:
    from psycopg import AsyncConnection
except ImportError as e:
    raise ImportError(
        "psycopg3 dependencies are not installed. Install them with: pip install azure-postgresql-auth[psycopg3]"
    ) from e


class AsyncEntraConnection(AsyncConnection):
    """Asynchronous connection class for using Entra authentication with Azure PostgreSQL."""

    @classmethod
    async def connect(cls, *args: Any, **kwargs: Any) -> "AsyncEntraConnection":
        """Establishes an asynchronous PostgreSQL connection using Entra authentication.

        This method automatically acquires Microsoft Entra ID credentials when user or password
        are not provided in the connection parameters.

        :param args: Positional arguments forwarded to the parent connection method.
        :type args: Any
        :return: An open asynchronous connection to the PostgreSQL database.
        :rtype: AsyncEntraConnection
        :raises ~azure_postgresql_auth.CredentialValueError:
            If the provided credential is not a valid AsyncTokenCredential.
        :raises ~azure_postgresql_auth.EntraConnectionValueError:
            If Entra connection credentials cannot be retrieved.
        """
        credential = kwargs.pop("credential", None)
        if credential is None or not isinstance(credential, (AsyncTokenCredential)):
            raise CredentialValueError(
                "credential is required and must be an AsyncTokenCredential for async connections"
            )

        # Check if we need to acquire Entra authentication info
        if not kwargs.get("user") or not kwargs.get("password"):
            try:
                entra_conninfo = await get_entra_conninfo_async(credential)
            except Exception as e:
                raise EntraConnectionValueError("Could not retrieve Entra credentials") from e
            # Always use the token password when Entra authentication is needed
            kwargs["password"] = entra_conninfo["password"]
            if not kwargs.get("user"):
                # If user isn't already set, use the username from the token
                kwargs["user"] = entra_conninfo["user"]
        return await super().connect(*args, **kwargs)

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from __future__ import annotations

from typing import Any

from azure.core.credentials import TokenCredential
from azure_postgresql_auth.core import get_entra_conninfo
from azure_postgresql_auth.errors import (
    CredentialValueError,
    EntraConnectionValueError,
)

try:
    from psycopg import Connection
except ImportError as e:
    raise ImportError(
        "psycopg3 dependencies are not installed. Install them with: pip install azure-postgresql-auth[psycopg3]"
    ) from e


class EntraConnection(Connection):
    """Synchronous connection class for using Entra authentication with Azure PostgreSQL."""

    @classmethod
    def connect(cls, *args: Any, **kwargs: Any) -> "EntraConnection":
        """Establishes a synchronous PostgreSQL connection using Entra authentication.

        This method automatically acquires Microsoft Entra ID credentials when user or password
        are not provided in the connection parameters.

        :param args: Positional arguments forwarded to the parent connection method.
        :type args: Any
        :return: An open synchronous connection to the PostgreSQL database.
        :rtype: EntraConnection
        :raises ~azure_postgresql_auth.CredentialValueError:
            If the provided credential is not a valid TokenCredential.
        :raises ~azure_postgresql_auth.EntraConnectionValueError:
            If Entra connection credentials cannot be retrieved.
        """
        credential = kwargs.pop("credential", None)
        if credential is None or not isinstance(credential, (TokenCredential)):
            raise CredentialValueError("credential is required and must be a TokenCredential for sync connections")

        # Check if we need to acquire Entra authentication info
        if not kwargs.get("user") or not kwargs.get("password"):
            try:
                entra_conninfo = get_entra_conninfo(credential)
            except Exception as e:
                raise EntraConnectionValueError("Could not retrieve Entra credentials") from e
            # Always use the token password when Entra authentication is needed
            kwargs["password"] = entra_conninfo["password"]
            if not kwargs.get("user"):
                # If user isn't already set, use the username from the token
                kwargs["user"] = entra_conninfo["user"]
        return super().connect(*args, **kwargs)

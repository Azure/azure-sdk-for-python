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
    from psycopg2.extensions import connection, make_dsn, parse_dsn
except ImportError as e:
    # Provide a helpful error message if psycopg2 dependencies are missing
    raise ImportError(
        "psycopg2 dependencies are not installed. Install them with: pip install azure-postgresql-auth[psycopg2]"
    ) from e


class EntraConnection(connection):
    """Synchronous connection class for using Entra authentication with Azure PostgreSQL.

    This connection class automatically acquires Microsoft Entra ID credentials when user
    or password are not provided in the DSN or connection parameters.

    :param dsn: PostgreSQL connection string (Data Source Name).
    :type dsn: str
    :keyword credential: Azure credential for token acquisition.
    :paramtype credential: ~azure.core.credentials.TokenCredential
    :keyword user: Database username. If not provided, extracted from Entra token.
    :paramtype user: str or None
    :keyword password: Database password. If not provided, uses Entra access token.
    :paramtype password: str or None
    :raises ~azure_postgresql_auth.CredentialValueError:
        If the provided credential is not a valid TokenCredential.
    :raises ~azure_postgresql_auth.EntraConnectionValueError:
        If Entra connection credentials cannot be retrieved.
    """

    def __init__(self, dsn: str, **kwargs: Any) -> None:
        # Extract current DSN params
        dsn_params = parse_dsn(dsn) if dsn else {}

        credential = kwargs.pop("credential", None)
        if credential is None or not isinstance(credential, (TokenCredential)):
            raise CredentialValueError("credential is required and must be a TokenCredential for sync connections")

        # Check if user and password are already provided
        has_user = "user" in dsn_params or "user" in kwargs
        has_password = "password" in dsn_params or "password" in kwargs

        # Only get Entra credentials if user or password is missing
        if not has_user or not has_password:
            try:
                entra_creds = get_entra_conninfo(credential)
            except Exception as e:
                raise EntraConnectionValueError("Could not retrieve Entra credentials") from e

            # Only update missing credentials
            if not has_user and "user" in entra_creds:
                dsn_params["user"] = entra_creds["user"]
            if not has_password and "password" in entra_creds:
                dsn_params["password"] = entra_creds["password"]

        # Update DSN params with any kwargs (kwargs take precedence)
        dsn_params.update(kwargs)

        # Create new DSN with updated credentials
        new_dsn = make_dsn(**dsn_params)

        # Call parent constructor with updated DSN only
        super().__init__(new_dsn)

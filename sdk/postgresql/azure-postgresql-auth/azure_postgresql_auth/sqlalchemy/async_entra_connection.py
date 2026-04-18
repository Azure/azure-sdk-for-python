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
    from sqlalchemy import event
    from sqlalchemy.engine import Dialect
    from sqlalchemy.ext.asyncio import AsyncEngine
except ImportError as e:
    # Provide a helpful error message if SQLAlchemy dependencies are missing
    raise ImportError(
        "SQLAlchemy dependencies are not installed. Install them with: pip install azure-postgresql-auth[sqlalchemy]"
    ) from e


def enable_entra_authentication_async(engine: AsyncEngine) -> None:
    """Enable Microsoft Entra ID authentication for an async SQLAlchemy engine.

    This function registers an event listener that automatically provides
    Entra ID credentials for each database connection. A credential must be
    provided via connect_args when creating the engine. Event handlers do not
    support async behavior so the token fetching will still be synchronous.

    :param engine: The async SQLAlchemy Engine to enable Entra authentication for.
    :type engine: ~sqlalchemy.ext.asyncio.AsyncEngine
    """

    @event.listens_for(engine.sync_engine, "do_connect")
    def provide_token(
        dialect: Dialect, conn_rec: Any, cargs: Any, cparams: dict[str, Any]  # pylint: disable=unused-argument
    ) -> None:
        """Event handler that provides Entra credentials for each sync connection.

        :param dialect: The SQLAlchemy dialect being used.
        :type dialect: ~sqlalchemy.engine.Dialect
        :param conn_rec: The connection record.
        :type conn_rec: Any
        :param cargs: The positional connection arguments.
        :type cargs: Any
        :param cparams: The keyword connection parameters.
        :type cparams: dict[str, Any]
        """
        credential = cparams.get("credential", None)
        if credential is None or not isinstance(credential, (TokenCredential)):
            raise CredentialValueError(
                "credential is required and must be a TokenCredential. "
                "Pass it via connect_args={'credential': DefaultAzureCredential()}"
            )
        # Check if credentials are already present
        has_user = "user" in cparams
        has_password = "password" in cparams

        # Only get Entra credentials if user or password is missing
        if not has_user or not has_password:
            try:
                entra_creds = get_entra_conninfo(credential)
            except Exception as e:
                raise EntraConnectionValueError("Could not retrieve Entra credentials") from e
            # Only update missing credentials
            if not has_user and "user" in entra_creds:
                cparams["user"] = entra_creds["user"]
            if not has_password and "password" in entra_creds:
                cparams["password"] = entra_creds["password"]

        # Strip helper-only param before DBAPI connect to avoid 'invalid connection option'
        if "credential" in cparams:
            del cparams["credential"]

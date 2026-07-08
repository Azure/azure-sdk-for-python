# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
SQLAlchemy integration for Azure PostgreSQL with Entra ID authentication.

This module provides integration between SQLAlchemy and Microsoft Entra ID
authentication for PostgreSQL connections. It automatically handles token acquisition
and credential injection through SQLAlchemy's event system.

Requirements:
    Install with: pip install azure-postgresql-auth[sqlalchemy]

    This will install:
    - sqlalchemy>=2.0.0

Functions:
    enable_entra_authentication: Enable Entra ID authentication for synchronous SQLAlchemy engines
    enable_entra_authentication_async: Enable Entra ID authentication for asynchronous SQLAlchemy engines
"""

from .async_entra_connection import enable_entra_authentication_async
from .entra_connection import enable_entra_authentication

__all__ = [
    "enable_entra_authentication",
    "enable_entra_authentication_async",
]

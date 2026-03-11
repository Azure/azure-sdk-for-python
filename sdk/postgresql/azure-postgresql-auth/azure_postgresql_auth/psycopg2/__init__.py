# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
Psycopg2 support for Microsoft Entra ID authentication with Azure Database for PostgreSQL.

This module provides a connection class that handles Microsoft Entra ID token acquisition
and authentication for synchronous PostgreSQL connections.

Requirements:
    Install with: pip install azure-postgresql-auth[psycopg2]

    This will install:
    - psycopg2-binary>=2.9.0

Classes:
    EntraConnection: Synchronous connection class with Entra ID authentication
"""

from .entra_connection import (
    EntraConnection,
)

__all__ = [
    "EntraConnection",
]

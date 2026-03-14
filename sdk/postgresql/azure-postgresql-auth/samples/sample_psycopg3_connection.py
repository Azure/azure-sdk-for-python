# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_psycopg3_connection.py

DESCRIPTION:
    This sample demonstrates how to connect to Azure PostgreSQL using psycopg3
    with both synchronous and asynchronous Entra ID authentication.

USAGE:
    python sample_psycopg3_connection.py
"""

import argparse
import asyncio
import os
import sys

from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from dotenv import load_dotenv
from psycopg_pool import AsyncConnectionPool, ConnectionPool

from azure_postgresql_auth.psycopg3 import AsyncEntraConnection, EntraConnection

# Load environment variables from .env file
load_dotenv()
SERVER = os.getenv("POSTGRES_SERVER")
DATABASE = os.getenv("POSTGRES_DATABASE", "postgres")


def main_sync() -> None:
    """Synchronous connection example using psycopg with Entra ID authentication."""

    # We use the EntraConnection class to enable synchronous Entra-based authentication for database access.
    # This class is applied whenever the connection pool creates a new connection, ensuring that Entra
    # authentication tokens are properly managed and refreshed so that each connection uses a valid token.
    #
    # For more details, see: https://www.psycopg.org/psycopg3/docs/api/connections.html#psycopg.Connection.connect
    pool = ConnectionPool(
        conninfo=f"postgresql://{SERVER}:5432/{DATABASE}",
        min_size=1,
        max_size=5,
        open=False,
        connection_class=EntraConnection,
        kwargs={"credential": DefaultAzureCredential()},
    )
    with pool, pool.connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT now()")
        result = cur.fetchone()
        print(f"Sync - Database time: {result}")


async def main_async() -> None:
    """Asynchronous connection example using psycopg with Entra ID authentication."""

    # We use the AsyncEntraConnection class to enable asynchronous Entra-based authentication for database access.
    # This class is applied whenever the connection pool creates a new connection, ensuring that Entra
    # authentication tokens are properly managed and refreshed so that each connection uses a valid token.
    #
    # For more details, see: https://www.psycopg.org/psycopg3/docs/api/connections.html#psycopg.Connection.connect
    pool = AsyncConnectionPool(
        conninfo=f"postgresql://{SERVER}:5432/{DATABASE}",
        min_size=1,
        max_size=5,
        open=False,
        connection_class=AsyncEntraConnection,
        kwargs={"credential": AsyncDefaultAzureCredential()},
    )
    async with pool, pool.connection() as conn, conn.cursor() as cur:
        await cur.execute("SELECT now()")
        result = await cur.fetchone()
        print(f"Async - Database time: {result}")


async def main(mode: str = "async") -> None:
    """Main function that runs sync and/or async examples based on mode.

    Args:
        mode: "sync", "async", or "both" to determine which examples to run
    """
    if mode in ("sync", "both"):
        print("=== Running Synchronous Example ===")
        try:
            main_sync()
            print("Sync example completed successfully!")
        except Exception as e:
            print(f"Sync example failed: {e}")

    if mode in ("async", "both"):
        if mode == "both":
            print("\n=== Running Asynchronous Example ===")
        else:
            print("=== Running Asynchronous Example ===")
        try:
            await main_async()
            print("Async example completed successfully!")
        except Exception as e:
            print(f"Async example failed: {e}")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Demonstrate psycopg connections with Microsoft Entra ID authentication"
    )
    parser.add_argument(
        "--mode",
        choices=["sync", "async", "both"],
        default="both",
        help="Run synchronous, asynchronous, or both examples (default: both)",
    )
    args = parser.parse_args()

    # Set Windows event loop policy for compatibility if needed
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main(args.mode))

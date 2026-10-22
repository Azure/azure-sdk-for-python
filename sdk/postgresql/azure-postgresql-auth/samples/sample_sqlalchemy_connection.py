# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_sqlalchemy_connection.py

DESCRIPTION:
    This sample demonstrates how to connect to Azure PostgreSQL using SQLAlchemy
    with both synchronous and asynchronous Entra ID authentication.

USAGE:
    python sample_sqlalchemy_connection.py
"""

import argparse
import asyncio
import os
import sys

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

from azure_postgresql_auth.sqlalchemy import (
    enable_entra_authentication,
    enable_entra_authentication_async,
)

# Load environment variables from .env file
load_dotenv()
SERVER = os.getenv("POSTGRES_SERVER")
DATABASE = os.getenv("POSTGRES_DATABASE", "postgres")


def main_sync() -> None:
    """Synchronous connection example using SQLAlchemy with Entra ID authentication."""

    # Create a synchronous engine
    engine = create_engine(
        f"postgresql+psycopg://{SERVER}/{DATABASE}",
        connect_args={"credential": DefaultAzureCredential()},
    )

    # We add an event listener to the engine to enable synchronous Entra authentication
    # for database access. This event listener is triggered whenever the connection pool
    # backing the engine creates a new connection, ensuring that Entra authentication tokens
    # are properly managed and refreshed so that each connection uses a valid token.
    #
    # For more details, see: https://docs.sqlalchemy.org/en/20/core/engines.html#controlling-how-parameters-are-passed-to-the-dbapi-connect-function
    enable_entra_authentication(engine)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT now()"))
        row = result.fetchone()
        print(f"Sync - Database time: {row[0] if row else 'Unknown'}")

    # Clean up the engine
    engine.dispose()


async def main_async() -> None:
    """Asynchronous connection example using SQLAlchemy with Entra ID authentication."""

    # Create an asynchronous engine
    engine = create_async_engine(
        f"postgresql+psycopg://{SERVER}/{DATABASE}",
        connect_args={"credential": DefaultAzureCredential()},
    )

    # We add an event listener to the engine to enable asynchronous Entra authentication
    # for database access. This event listener is triggered whenever the connection pool
    # backing the engine creates a new connection, ensuring that Entra authentication tokens
    # are properly managed and refreshed so that each connection uses a valid token.
    #
    # For more details, see: https://docs.sqlalchemy.org/en/20/core/engines.html#controlling-how-parameters-are-passed-to-the-dbapi-connect-function
    enable_entra_authentication_async(engine)

    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT now()"))
        row = result.fetchone()
        print(f"Async Core - Database time: {row[0] if row else 'Unknown'}")

    # Clean up the engine
    await engine.dispose()


async def main(mode: str = "async") -> None:
    """Main function that runs sync and/or async examples based on mode.

    Args:
        mode: "sync", "async", or "both" to determine which examples to run
    """
    if mode in ("sync", "both"):
        print("=== Running Synchronous SQLAlchemy Example ===")
        try:
            main_sync()
            print("Sync example completed successfully!")
        except Exception as e:
            print(f"Sync example failed: {e}")

    if mode in ("async", "both"):
        if mode == "both":
            print("\n=== Running Asynchronous SQLAlchemy Example ===")
        else:
            print("=== Running Asynchronous SQLAlchemy Example ===")
        try:
            await main_async()
            print("Async example completed successfully!")
        except Exception as e:
            print(f"Async example failed: {e}")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Demonstrate SQLAlchemy connections with Microsoft Entra ID authentication"
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

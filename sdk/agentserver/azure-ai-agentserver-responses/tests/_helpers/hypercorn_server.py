# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Shared Hypercorn test-server helper for disconnect tests.

Provides an async context manager that starts a real HTTP server with
Hypercorn, enabling tests to exercise genuine TCP disconnect behavior.
"""

from __future__ import annotations

import asyncio
import socket
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import httpx
from hypercorn.asyncio import serve as _hc_serve
from hypercorn.config import Config as _HcConfig


@asynccontextmanager
async def hypercorn_server(
    app: Any,
    *,
    startup_delay: float = 0.5,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Start *app* on a free port with Hypercorn and yield an httpx client.

    Usage::

        async with hypercorn_server(app) as client:
            resp = await client.post("/responses", json={...})
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    hc_config = _HcConfig()
    hc_config.bind = [f"127.0.0.1:{port}"]
    shutdown_event = asyncio.Event()

    server_task = asyncio.create_task(
        _hc_serve(app, hc_config, shutdown_trigger=shutdown_event.wait)  # type: ignore[arg-type]
    )
    await asyncio.sleep(startup_delay)

    try:
        async with httpx.AsyncClient(
            base_url=f"http://127.0.0.1:{port}",
            timeout=httpx.Timeout(30.0),
        ) as client:
            yield client
    finally:
        shutdown_event.set()
        await asyncio.wait_for(server_task, timeout=5.0)

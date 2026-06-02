#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""Supervisor: keeps /readiness alive while app crashes and restarts.

This is PID 1 in the container. It:
  1. Runs a tiny HTTP server on port 8088 (the platform-facing port)
  2. Spawns app.py on an internal port (8089)
  3. Always responds 200 to GET /readiness
  4. Proxies POST /invocations (and everything else) to the app
  5. Restarts the app immediately on crash

Because this process never exits, the platform never sees a readiness failure,
and the session survives across app crashes.
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import subprocess
import sys

from aiohttp import ClientSession, ClientTimeout, web

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [supervisor] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("supervisor")

EXTERNAL_PORT = 8088
INTERNAL_PORT = 8089
APP_BASE = f"http://127.0.0.1:{INTERNAL_PORT}"

# ── App process management ────────────────────────────────────────────────────

_app_proc: subprocess.Popen | None = None


def _start_app() -> subprocess.Popen:
    env = os.environ.copy()
    env["PORT"] = str(INTERNAL_PORT)
    logger.info("Starting agent on port %d...", INTERNAL_PORT)
    proc = subprocess.Popen(
        [sys.executable, "app.py"],
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    logger.info("Agent PID %d", proc.pid)
    return proc


async def _monitor_loop():
    """Restart app on crash."""
    global _app_proc
    while True:
        if _app_proc is not None:
            ret = _app_proc.poll()
            if ret is not None:
                if ret == 0:
                    logger.info("Agent exited cleanly. Supervisor stopping.")
                    raise SystemExit(0)
                logger.warning("💥 Agent crashed (exit %d). Restarting...", ret)
                _app_proc = _start_app()
        await asyncio.sleep(0.3)


# ── HTTP handlers ─────────────────────────────────────────────────────────────


async def handle_readiness(_request: web.Request) -> web.Response:
    """Always-healthy readiness check."""
    return web.json_response({"status": "healthy"})


async def handle_proxy(request: web.Request) -> web.StreamResponse:
    """Proxy everything else to the app, waiting for it to be ready first."""
    session: ClientSession = request.app["client_session"]

    # Wait for the app to be ready (poll /readiness on internal port)
    for _ in range(30):  # up to ~6 seconds
        try:
            async with session.get(f"{APP_BASE}/readiness") as check:
                if check.status == 200:
                    break
        except Exception:
            pass
        await asyncio.sleep(0.2)

    url = f"{APP_BASE}{request.path_qs}"
    headers = dict(request.headers)
    headers.pop("Host", None)
    headers.pop("host", None)
    body = await request.read()

    try:
        async with session.request(
            request.method, url, headers=headers, data=body
        ) as resp:
            # Check if SSE — stream it back
            if "text/event-stream" in resp.content_type:
                proxy_resp = web.StreamResponse(
                    status=resp.status,
                    headers={
                        "Content-Type": "text/event-stream",
                        "Cache-Control": "no-cache",
                    },
                )
                await proxy_resp.prepare(request)
                async for chunk in resp.content.iter_any():
                    await proxy_resp.write(chunk)
                await proxy_resp.write_eof()
                return proxy_resp
            else:
                return web.Response(
                    body=await resp.read(),
                    status=resp.status,
                    content_type=resp.content_type,
                )
    except Exception:
        return web.json_response(
            {"error": "Agent is restarting. Retry in a moment."},
            status=503,
        )


# ── App lifecycle ─────────────────────────────────────────────────────────────


async def on_startup(app: web.Application):
    global _app_proc
    app["client_session"] = ClientSession(timeout=ClientTimeout(total=300))
    _app_proc = _start_app()
    app["monitor_task"] = asyncio.create_task(_monitor_loop())


async def on_cleanup(app: web.Application):
    app["monitor_task"].cancel()
    await app["client_session"].close()
    if _app_proc and _app_proc.poll() is None:
        _app_proc.terminate()
        try:
            _app_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _app_proc.kill()


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    app.router.add_get("/readiness", handle_readiness)
    # Catch-all proxy for all other routes
    app.router.add_route("*", "/{path:.*}", handle_proxy)

    logger.info("Supervisor starting on port %d", EXTERNAL_PORT)
    web.run_app(app, host="0.0.0.0", port=EXTERNAL_PORT, print=None)


if __name__ == "__main__":
    main()

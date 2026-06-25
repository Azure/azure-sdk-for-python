# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DEMO_MODE-only diagnostic: capture a full, untruncated HTTP trace of the
durable-task create (``POST /tasks``) with an oversized attachment, from INSIDE
the hosted container (where the hosted-agent managed-identity credential is valid).

External callers get HTTP 403 ``hosted_agent_required`` for task writes, so the
real ``500`` the service returns for an oversized attachment can only be observed
in-container. This drives the real core SDK client so the request is byte-faithful,
wrapping the transport to dump the request line/query/headers/full body and the
full response status/headers/body. Only the bearer token VALUE is redacted.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from azure.core.pipeline.transport import AioHttpTransport, AsyncHttpTransport
from azure.identity.aio import DefaultAzureCredential

from azure.ai.agentserver.core.durable._client import HostedTaskProvider
from azure.ai.agentserver.core.durable._models import TaskCreateRequest


def _redact_headers(headers) -> dict:
    out = {}
    for k, v in dict(headers or {}).items():
        if str(k).lower() == "authorization":
            scheme = v.split(" ", 1)[0] if isinstance(v, str) and " " in v else "Bearer"
            out[k] = f"{scheme} <REDACTED — live hosted-agent bearer token>"
        else:
            out[k] = v
    return out


def _body_bytes(obj) -> bytes:
    for attr in ("content", "body", "data"):
        v = getattr(obj, attr, None)
        if isinstance(v, bytes):
            return v
        if isinstance(v, str):
            return v.encode("utf-8")
    return b""


class _CapturingTransport(AsyncHttpTransport):
    def __init__(self, inner: AsyncHttpTransport) -> None:
        self.inner = inner
        self.records: list[dict] = []

    async def send(self, request, **kwargs):
        rec = {
            "method": getattr(request, "method", "?"),
            "url": str(getattr(request, "url", "?")),
            "req_headers": _redact_headers(getattr(request, "headers", {})),
            "req_body": _body_bytes(request),
        }
        response = await self.inner.send(request, **kwargs)
        body = b""
        try:
            await response.load_body()
            body = response.body() or b""
        except Exception as exc:  # noqa: BLE001
            body = f"<could not buffer response body: {exc!r}>".encode("utf-8")
        rec.update(
            {
                "status": getattr(response, "status_code", "?"),
                "reason": getattr(response, "reason", ""),
                "resp_headers": dict(getattr(response, "headers", {}) or {}),
                "resp_body": body,
            }
        )
        self.records.append(rec)
        return response

    async def open(self) -> None:
        await self.inner.open()

    async def close(self) -> None:
        await self.inner.close()

    async def __aenter__(self) -> "_CapturingTransport":
        await self.open()
        return self

    async def __aexit__(self, *a) -> None:
        await self.close()


def _format(rec: dict, attach_bytes: int, attach_key: str) -> str:
    rb = rec.get("req_body", b"")
    sb = rec.get("resp_body", b"")
    out = [
        "=" * 100,
        "RAW HTTP TRACE — durable-task create (POST /tasks) with oversized attachment",
        "captured IN-CONTAINER (hosted-agent credential) at " f"{datetime.now(timezone.utc).isoformat()}",
        f"attachment: key={attach_key!r} value_size={attach_bytes} bytes "
        "(task-attachments SOT limit: 2 MB/attachment — this is well under it)",
        "=" * 100,
        "",
        "################  REQUEST  ################",
        f"{rec.get('method')} {rec.get('url')}",
        "",
        "--- request headers ---",
    ]
    out += [f"{k}: {v}" for k, v in rec.get("req_headers", {}).items()]
    out += [
        "",
        f"--- request body ({len(rb)} bytes, UNTRUNCATED) ---",
        rb.decode("utf-8", errors="replace"),
        "",
        "################  RESPONSE  ################",
        f"HTTP {rec.get('status')} {rec.get('reason', '')}".rstrip(),
        "",
        "--- response headers ---",
    ]
    out += [f"{k}: {v}" for k, v in rec.get("resp_headers", {}).items()]
    out += [
        "",
        f"--- response body ({len(sb)} bytes, UNTRUNCATED) ---",
        sb.decode("utf-8", errors="replace") if sb else "<empty response body>",
        "=" * 100,
    ]
    return "\n".join(out)


async def capture_oversized_task_trace(project_endpoint: str, agent_name: str, attach_bytes: int = 300 * 1024) -> str:
    """Issue one oversized ``POST /tasks`` with the hosted-agent credential and
    return a fully-formatted, untruncated request+response trace.

    Mirrors the field set the real durable path builds (``_manager.py`` task
    create): ``title``, ``payload`` (input ref + metadata + turn-start),
    ``source``, ``tags``, and the oversized input spilled to
    ``attachments["_input"]`` — so the request is faithful and only the spilled
    attachment size differs.
    """
    pad = "A long research input. "
    big = (pad * ((attach_bytes // len(pad)) + 1))[:attach_bytes]
    session_id = f"task-trace-{uuid.uuid4().hex}"
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    req = TaskCreateRequest(
        agent_name=agent_name,
        session_id=session_id,
        status="in_progress",
        id=f"durable-resp-{uuid.uuid4().hex}",
        title="durable-response oversized task-trace diagnostic",
        payload={"input": {"_attachment": "_input"}, "metadata": {}, "_turn_started_at": now_iso},
        source={"type": "agentserver.task", "name": "handler", "server_version": "2.0.0b7"},
        tags={"_task_name": "handler"},
        lease_owner=f"{agent_name}|session:{session_id}",
        lease_instance_id=f"trace-{uuid.uuid4().hex[:12]}",
        lease_duration_seconds=60,
        attachments={"_input": big},
    )
    cap = _CapturingTransport(AioHttpTransport())
    err = None
    async with DefaultAzureCredential() as cred:
        provider = HostedTaskProvider(project_endpoint, cred, transport=cap)
        try:
            await provider.create(req)
        except Exception as exc:  # noqa: BLE001
            err = repr(exc)
    if not cap.records:
        return f"NO HTTP RECORD CAPTURED. SDK error: {err}"
    text = _format(cap.records[-1], attach_bytes, "_input")
    if err:
        text += f"\n\nSDK raised: {err}\n"
    return text

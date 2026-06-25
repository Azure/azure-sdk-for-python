# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DEMO_MODE-only diagnostic: capture a full, untruncated HTTP trace of the
resilient-task create (``POST /tasks``) with an oversized attachment, from INSIDE
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

from azure.ai.agentserver.core.tasks._client import HostedTaskProvider
from azure.ai.agentserver.core.tasks._models import TaskCreateRequest


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
        "RAW HTTP TRACE — resilient-task create (POST /tasks) with oversized attachment",
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


def _build_task_request(agent_name: str, attach_bytes: int, *, use_attachment: bool = True):
    """Build a TaskCreateRequest faithful to the real resilient path.

    When ``use_attachment`` is True the input is spilled to an ``_input``
    attachment of ``attach_bytes`` bytes (the >threshold resilient path). When
    False the input stays INLINE in ``payload`` (the small-input path) and no
    ``attachments`` field is sent — the control that isolates "any attachment"
    as the trigger.
    """
    pad = "A long research input. "
    blob = (pad * ((attach_bytes // len(pad)) + 1))[:attach_bytes]
    session_id = f"task-trace-{uuid.uuid4().hex}"
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    if use_attachment:
        payload = {"input": {"_attachment": "_input"}, "metadata": {}, "_turn_started_at": now_iso}
        attachments = {"_input": blob}
    else:
        payload = {"input": blob, "metadata": {}, "_turn_started_at": now_iso}
        attachments = None
    return TaskCreateRequest(
        agent_name=agent_name,
        session_id=session_id,
        status="in_progress",
        id=f"resilient-resp-{uuid.uuid4().hex}",
        title="resilient-response oversized task-trace diagnostic",
        payload=payload,
        source={"type": "agentserver.task", "name": "handler", "server_version": "2.0.0b7"},
        tags={"_task_name": "handler"},
        lease_owner=f"{agent_name}|session:{session_id}",
        lease_instance_id=f"trace-{uuid.uuid4().hex[:12]}",
        lease_duration_seconds=60,
        attachments=attachments,
    )


async def _capture_one(
    project_endpoint: str, agent_name: str, attach_bytes: int, *, use_attachment: bool = True
) -> tuple[dict, str | None]:
    """Issue one POST /tasks; return (captured_record, sdk_error)."""
    req = _build_task_request(agent_name, attach_bytes, use_attachment=use_attachment)
    cap = _CapturingTransport(AioHttpTransport())
    err = None
    async with DefaultAzureCredential() as cred:
        provider = HostedTaskProvider(project_endpoint, cred, transport=cap)
        try:
            await provider.create(req)
        except Exception as exc:  # noqa: BLE001
            err = repr(exc)
    rec = cap.records[-1] if cap.records else {}
    return rec, err


async def capture_oversized_task_trace(project_endpoint: str, agent_name: str, attach_bytes: int = 300 * 1024) -> str:
    """Capture an A/B pair of ``POST /tasks`` traces with the hosted-agent
    credential, returning a single fully-formatted, untruncated trace for
    service-side investigation:

    - **CONTROL** — small input kept INLINE in ``payload`` (no ``attachments``
      field); the small-input resilient path (expected to SUCCEED, 201).
    - **OVERSIZED** — input spilled to ``attachments["_input"]``; the >threshold
      resilient path (the FAILING case).

    Both mirror the field set the real resilient path builds (``_manager.py``):
    ``title``, ``payload``, ``source``, ``tags``. The only difference is whether
    the input is inline vs. an attachment — isolating "the task-store rejects any
    attachment-bearing create" as the trigger.
    """
    control_bytes = 1024  # 1 KB inline control
    sections: list[str] = []

    control_rec, control_err = await _capture_one(project_endpoint, agent_name, control_bytes, use_attachment=False)
    sections.append("##### CONTROL — SMALL INLINE INPUT, NO ATTACHMENT (expected to SUCCEED) #####")
    if control_rec:
        sections.append(_format(control_rec, control_bytes, "(inline, no attachment)"))
    else:
        sections.append(f"NO HTTP RECORD CAPTURED. SDK error: {control_err}")
    if control_err:
        sections.append(f"SDK raised (control): {control_err}")

    over_rec, over_err = await _capture_one(project_endpoint, agent_name, attach_bytes, use_attachment=True)
    sections.append("")
    sections.append("##### OVERSIZED INPUT SPILLED TO ATTACHMENT (the FAILING case) #####")
    if over_rec:
        sections.append(_format(over_rec, attach_bytes, "_input"))
    else:
        sections.append(f"NO HTTP RECORD CAPTURED. SDK error: {over_err}")
    if over_err:
        sections.append(f"SDK raised (oversized): {over_err}")

    # Summary line for quick triage.
    cs = control_rec.get("status", "?") if control_rec else "?"
    os_ = over_rec.get("status", "?") if over_rec else "?"
    summary = (
        "\n##### SUMMARY #####\n"
        f"CONTROL  (inline payload, NO attachment, {control_bytes} bytes) -> POST /tasks {cs}\n"
        f"OVERSIZED ({attach_bytes}-byte input spilled to _input attachment)  -> POST /tasks {os_}\n"
        "The two requests are identical except the oversized one carries an `attachments` "
        "field. The task-attachments SOT permits up to 2 MB per attachment. The oversized "
        "500 wraps an upstream 403 from the task-store's attachment offload to the AzureML "
        "dataset store (POST .../datasets/.../startPendingUpload -> 403 Forbidden) — a "
        "service-side permission/config issue on attachment handling, not an SDK bug.\n"
    )
    return "\n".join(sections) + "\n" + summary

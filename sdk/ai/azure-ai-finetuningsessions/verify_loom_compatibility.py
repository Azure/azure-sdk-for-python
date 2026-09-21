# pylint: disable=line-too-long,useless-suppression,too-many-lines
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline, side-by-side Loom compatibility proof using unmodified SDK sources.

Run with the existing Python environment (azure-core and the SDK dependencies
must already be installed):

    python verify_loom_compatibility.py --loom-repo C:\\path\\to\\loom

The parent imports neither SDK. Two fresh, isolated Python subprocesses import
azure.ai.finetuningsessions from their respective source roots, run the same 20
cases with real clients and buffered fake transports, and return JSON snapshots.
Both workers use their default routes without a route-selection flag. URLs are checked at the
transport boundary, NEVER rewritten by this verifier. No install, generation,
temporary source copy, package alias, test-module import, or service is involved.

Internal inspection interface:

    python verify_loom_compatibility.py --snapshot <package-directory>
    python verify_loom_compatibility.py --snapshot <package-directory> --legacy-routes

Snapshots contain no wall-clock timestamps, process IDs, random request IDs, or task reprs.
They retain complete JSON request/result bodies and numeric types. Only header
casing, a validated client-request UUID, and the exact Python/platform user-agent
suffix are normalized. The SDK user-agent moniker/version remain checked.
Narrow surface allowances and excluded contracts are printed by the parent.
Exit codes: 0 = pass, 1 = case/comparison failure, 2 = setup/worker failure.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
from collections import deque
from contextlib import redirect_stdout
from dataclasses import dataclass
from enum import Enum
import hashlib
import importlib
import inspect
import json
import logging
import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any, Callable
from urllib.parse import urlencode
from uuid import UUID

PACKAGE = Path(__file__).resolve().parent
MODULE = Path("azure/ai/finetuningsessions")
NAMESPACE = "azure.ai.finetuningsessions"
ENDPOINT = "https://offline.invalid/api/projects/compatibility"
ROUTE = "/fine_tuning/sessions"
SESSION = "session_workload"
BASE_MODEL = "offline-base-model"
PREVIEW = "FineTuningSessions=V1Preview"
KEY = "offline-verifier-key-not-a-secret"
TOKEN = "offline-verifier-token-not-a-secret"
IMAGE = b"\xff\xd8\xffoffline-jpeg"
IMAGE_WIRE = {
    "type": "image",
    "data": base64.b64encode(IMAGE).decode("ascii"),
    "format": "jpeg",
    "expected_tokens": 2,
}
METADATA = {"enabled": True, "nested": {"values": [1, 0.5, None, False, "caf\u00e9"]}}
LORA = {
    "rank": 16,
    "alpha": 32.0,
    "seed": 7,
    "freeze_vision_tower": False,
    "freeze_multi_modal_projector": True,
}
ADAM = {"learning_rate": 0.0001, "beta1": 0.9, "beta2": 0.999, "eps": 1e-8, "weight_decay": 0.01}
SAMPLING = {"max_tokens": 8, "temperature": 0.7, "top_p": 0.9, "top_k": -1, "seed": 17, "stop_criteria": [0]}
LOSS_CONFIG = {"clip_low_threshold": 0.2, "clip_high_threshold": 0.3, "tau_pos": 1.0, "tau_neg": 1.5}
IDENTITIES = (
    ("session_canonical", "session_canonical", "session_canonical"),
    ("model_legacy", "session_legacy", "model_legacy"),
    ("raw", "session_raw", "model_raw"),
)
CHECKPOINT_PATHS = ("model_source/checkpoint_source", "loom://model_source/weights/checkpoint_source")
MIXED_INPUT = {"chunks": [{"tokens": [1, 2]}, IMAGE_WIRE, {"tokens": [3]}]}
BATCH = [
    {
        "model_input": {"chunks": [{"tokens": [1, 2, 3]}]},
        "loss_fn_inputs": {
            "target_tokens": {"data": [2.0, 3.0, 4.0]},
            "weights": {"data": [0.0, 1.0, 1.0]},
            "advantages": {"data": [0.0, 0.5, 1.0]},
            "logprobs": {"data": [-0.1, -0.2, -0.3]},
        },
    },
    {
        "model_input": MIXED_INPUT,
        "loss_fn_inputs": {
            "target_tokens": {"data": [2.0, 0.0, 0.0, 3.0, 4.0]},
            "weights": {"data": [0.0, 0.0, 0.0, 1.0, 1.0]},
        },
    },
]
FORWARD = {
    "loss_fn_output_type": "scalar",
    "loss_fn_outputs": [{"logprobs": [None, -0.5, -1.0]}, {"logprobs": [-0.4, None, -0.6, 0.0, -0.2]}],
    "per_datum_logprobs": [{"data": [-0.5, -1.0]}, {"data": [-0.4, -0.6, -0.2]}],
    "metrics": {"prefill_tokens": 8, "prefill_duration_s": 0.25, "prefill_cache_hit_tokens": None, **METADATA},
}
BACKWARD = {**FORWARD, "metrics": {**FORWARD["metrics"], "total_loss:sum": 1.25}}
# Use float-valued optimizer metrics supported by BOTH existing schemas. Do not
# conceal the legacy dict[str, float] versus regenerated JSON annotation change.
OPTIMIZER = {"metrics": {"skyrl.ai/grad_norm": 0.75, "step_count": 3.0}}
SAMPLES = {
    "sequences": [
        {"tokens": [31, 32], "text": "caf\u00e9", "logprobs": [-0.5, -1.0]},
        {"tokens": [33], "text": None, "logprobs": None},
    ],
    "prompt_logprobs": [None, -0.25],
    "topk_prompt_logprobs": [None, [[31, -0.5], [32, -1.25]]],
    "metrics": {"sample_tokens": 3, "sample_duration_s": 0.25, **METADATA},
}

NORMALIZATIONS = [
    "Header names are case-insensitive; all non-exempt header values are compared.",
    "x-ms-client-request-id must be a UUID on every request; only its random value is omitted.",
    "User-Agent must have the expected SDK moniker/version; only the exact Python/platform suffix is removed.",
    "JSON object ordering/whitespace and Python tuple/list JSON encoding are not wire differences; scalar numeric types are preserved.",
    "Package origins/source hashes differ by design; both SDKs use their default routes without rewriting or selection flags.",
    "Signature annotations are not compared; parameter names, kinds, defaults, binding, and selected real calls are checked.",
]
LIMITATIONS = [
    "Generated operations.get is excluded: Loom's OperationResult and the public raw RequestStatus union are different contracts.",
    "Generated sessions.create/body-alias adapters are not a paired baseline contract here; creation uses the real convenience APIs.",
    "All begin_* methods are excluded: Loom's generated 202/Operation-Location LRO contract is not its HTTP-200 protocol.",
    "Generated wire parity covers sessions.get/list/heartbeat and checkpoints.get/list with per-operation api_version='v1' only.",
    "Generated-only types/annotations and internal class locations are not whole-schema parity claims; exercised model JSON/attributes are exact.",
    "Immediate fixture completion proves client behavior, not service/GPU correctness, retry timing, multi-chunk concurrency, or background heartbeats.",
]
MODEL_ADDITIONS = frozenset(
    {
        "ActionOperation",
        "CompleteResponse",
        "CompletedRequest",
        "CreateSessionResponse",
        "DeleteSessionResponse",
        "FailedRequest",
        "ImageFormat",
        "MisalignmentErrorDetailsResource",
        "PendingOperation",
        "PendingRequest",
        "RequestStatus",
        "TrainingType",
        "_MisalignmentErrorType",
        "_MisalignmentSteer",
    }
)
FEATURE_ADDITIONS = {
    "AGENT_INSIGHTS_V1_PREVIEW": "AgentInsights=V1Preview",
    "ROUTINES_V2_PREVIEW": "Routines=V2Preview",
    "SKILLS_V1_PREVIEW": "Skills=V1Preview",
    "DATA_GENERATION_JOBS_V1_PREVIEW": "DataGenerationJobs=V1Preview",
    "MODELS_V1_PREVIEW": "Models=V1Preview",
    "AGENTS_OPTIMIZATION_V2_PREVIEW": "AgentsOptimization=V2Preview",
    "MODEL_ROUTER_CONTROLS_V1_PREVIEW": "ModelRouterControls=V1Preview",
}
SYNC_METHODS = (
    "create",
    "create_from_checkpoint",
    "forward",
    "forward_backward",
    "optim_step",
    "save_weights",
    "save_weights_for_sampler",
    "sample",
    "heartbeat",
    "close",
    "delete",
)
ASYNC_METHODS = (
    "create_session",
    "create_session_from_checkpoint",
    "forward",
    "forward_post",
    "forward_async",
    "forward_backward",
    "forward_backward_post",
    "forward_backward_async",
    "optim_step",
    "optim_step_post",
    "optim_step_async",
    "save_weights",
    "save_weights_post",
    "save_weights_async",
    "save_weights_for_sampler_async",
    "save_weights_and_get_sampling_client_async",
    "sample",
    "close_session",
    "delete_session",
)
GENERATED_METHODS = ("sessions.get", "sessions.list", "sessions.heartbeat", "checkpoints.get", "checkpoints.list")
ERROR_FIELDS = (
    "status_code",
    "max_batch_size",
    "actual_batch_size",
    "retry_after_sec",
    "reason",
    "session_id",
    "error_code",
    "debug_ref",
    "operation_completed",
    "field",
)


def _dump(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(",", ":"))


def _plain(value: Any) -> Any:
    """Strict JSON conversion: no repr/string fallback that could hide a change."""
    if isinstance(value, Enum):
        return _plain(value.value)
    if value is None or type(value) in (bool, int, float, str):
        return value
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if isinstance(value, dict) and all(isinstance(key, str) for key in value):
        return {key: _plain(item) for key, item in value.items()}
    raise TypeError(f"Unexpected non-JSON snapshot value: {type(value).__name__}")


def _signature(target: Any) -> list[dict[str, Any]]:
    result = []
    for name, parameter in inspect.signature(target).parameters.items():
        if name in ("self", "cls"):
            continue
        entry = {"name": name, "kind": parameter.kind.name}
        if parameter.default is not inspect.Parameter.empty:
            entry["default"] = _plain(parameter.default)
        result.append(entry)
    return result


def _source_hashes(package: Path) -> dict[str, str]:
    return {
        path.relative_to(package).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((package / MODULE).rglob("*"))
        if path.is_file() and (path.suffix == ".py" or path.name == "py.typed")
    }


def _check_package(path: Path) -> Path:
    path = path.resolve()
    if not (path / MODULE / "__init__.py").is_file():
        raise ValueError(f"Not a source package containing {NAMESPACE}: {path}")
    return path


def _offline_environment() -> None:
    # Child-only changes: never let the caller's identity, proxy, or telemetry
    # environment affect the snapshot or expose real credentials in its headers.
    for name in (
        "COGNITIVE_SUBSCRIPTION_ID",
        "AZURE_SUBSCRIPTION_ID",
        "AZURE_HTTP_USER_AGENT",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "no_proxy",
    ):
        os.environ.pop(name, None)
    os.environ.update(
        {
            "X_COGNITIVE_SUBSCRIPTION_ID": "offline-subscription",
            "LOOM_AZURE_RESOURCE_ID": "/subscriptions/offline/resourceGroups/offline/providers/Microsoft.CognitiveServices/accounts/offline",
            "LOOM_AZURE_RESOURCE_TENANT_ID": "offline-tenant",
            "LOOM_AZURE_RESOURCE_LOCATION": "offline-region",
            "LOOM_WORKSPACE_RESOURCE_ID": "/subscriptions/offline/resourceGroups/offline/providers/Microsoft.MachineLearningServices/workspaces/offline",
            "FINETUNING_VERBOSE_HTTP": "0",
            "LOOM_POLL_WARN_SEC": "0",
            "AZURE_AI_FINETUNING_SESSIONS_OPERATION_TIMEOUT_SEC": "5",
            "AZURE_TRACING_ENABLED": "false",
        }
    )


def _install_offline_guard() -> None:
    """Deny network, subprocesses, and filesystem writes within this worker.

    The asyncio loop is created BEFORE installing the hook because Windows may
    use a local socket pair for its internal wakeup mechanism. No SDK is imported
    until AFTER the guard is active; no service connection, even loopback, is allowed.
    """
    forbidden = {
        "socket.connect",
        "socket.bind",
        "socket.getaddrinfo",
        "socket.gethostbyname",
        "socket.gethostbyaddr",
        "socket.sendto",
        "socket.sendmsg",
        "subprocess.Popen",
        "os.system",
        "os.exec",
        "os.spawn",
        "os.remove",
        "os.rename",
        "os.rmdir",
        "os.mkdir",
        "os.link",
        "os.symlink",
        "os.truncate",
        "os.chmod",
        "os.chown",
        "os.utime",
        "shutil.copyfile",
        "shutil.rmtree",
    }
    write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND

    def audit(event: str, args: tuple[Any, ...]) -> None:
        if event in forbidden:
            raise RuntimeError(f"Offline/read-only verifier forbids {event}")
        if event == "open":
            _, mode, flags = args
            if (isinstance(flags, int) and flags & write_flags) or (
                isinstance(mode, str) and any(c in mode for c in "wax+")
            ):
                raise RuntimeError("Offline/read-only verifier forbids opening files for writing")

    sys.addaudithook(audit)


@dataclass(frozen=True)
class _Reply:
    method: str
    url: str
    body: Any
    payload: Any
    status: int = 200


class _Case:
    def __init__(self, name: str, context: "_Context", token_auth: bool = False) -> None:
        self.name, self.context, self.token_auth = name, context, token_auth
        self.replies: deque[_Reply] = deque()
        self.requests: list[dict[str, Any]] = []
        self.token_calls: list[Any] = []
        self.checks = 0

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(label)

    def equal(self, actual: Any, expected: Any, label: str) -> None:
        self.check(_dump(actual) == _dump(expected), f"{label}: expected {_dump(expected)}, got {_dump(actual)}")

    def expect(
        self, method: str, suffix: str, payload: Any, *, body: Any = None, status: int = 200, query: tuple = ()
    ) -> None:
        url = ENDPOINT + ROUTE + suffix + "?" + urlencode((("api-version", "v1"), *query))
        self.replies.append(_Reply(method, url, body, payload, status))

    def operation(
        self,
        action: str,
        body: Any,
        result: dict,
        request_id: str,
        *,
        resource: str = SESSION,
        server_id: str | None = None,
        query: tuple = (),
        failed: bool = False,
    ) -> None:
        self.expect(
            "POST",
            f"/{resource}/{action}",
            {
                "request_id": request_id,
                "session_id": server_id or resource,
                "status": "pending",
            },
            body=body,
            query=query,
        )
        self.expect(
            "GET", f"/{resource}/request/{request_id}", result if failed else {"status": "completed", "result": result}
        )

    def create(self, server_id: str, resource: str, body: dict, request_id: str) -> None:
        self.expect("POST", "", {"session_id": server_id, "request_id": request_id, "status": "pending"}, body=body)
        self.expect("GET", f"/{resource}/request/{request_id}", {"status": "completed", "result": {}})

    def receive(self, request: Any, options: dict) -> _Reply:
        headers = {key.lower(): value for key, value in request.headers.items()}
        request_id = headers.pop("x-ms-client-request-id", None)
        agent = headers.get("user-agent")
        if isinstance(agent, str):
            headers["user-agent"] = agent.removesuffix(self.context.user_agent_suffix)
        content = request.content
        body = None if content is None else json.loads(content)
        record = {
            "method": request.method,
            "url": request.url,
            "headers": headers,
            "body": body,
            "options": _plain(options),
        }
        self.requests.append(record)
        self.check(isinstance(request_id, str), "Client request ID header must be present")
        UUID(request_id)
        self.equal(agent, self.context.user_agent, "SDK user agent including runtime suffix")
        for keyword in ("api_version", "use_legacy_routes", "body"):
            self.check(keyword not in options, f"{keyword} leaked to transport")
        self.equal(headers.get("accept"), "application/json", "Accept header")
        self.equal(headers.get("foundry-features"), PREVIEW, "Preview opt-in header")
        if self.token_auth:
            self.equal(headers.get("authorization"), f"Bearer {TOKEN}", "Fake bearer authentication")
            self.check("api-key" not in headers, "Bearer request must not contain an API key")
        else:
            self.equal(headers.get("api-key"), KEY, "Fake API key authentication")
            self.check("authorization" not in headers, "Key request must not contain bearer authentication")
        self.check(bool(self.replies), "Unexpected extra request: possible retry, route fallback, or heartbeat")
        reply = self.replies.popleft()
        self.equal(request.method, reply.method, "HTTP method")
        # Deliberately compare the entire actual URL, not a normalized path or
        # parsed/sorted query. A /fine_tuning_sessions route reaching here is a failure.
        self.equal(request.url, reply.url, "URL at the transport boundary")
        self.equal(body, reply.body, "Complete JSON request body")
        return reply

    def finish(self, output: Any = None, error: Exception | None = None) -> dict:
        if error is None:
            try:
                self.equal(len(self.replies), 0, "All scripted responses must be consumed")
            except Exception as exc:
                error = exc
        result = {
            "ok": error is None,
            "checks": self.checks,
            "requests": self.requests,
            "token_calls": self.token_calls,
            "remaining_responses": len(self.replies),
        }
        if error is None:
            result["output"] = output
        else:
            result["error"] = {"type": type(error).__name__, "message": str(error)}
        return result


def _transport_types() -> tuple[type, type]:
    # Worker-only imports. These are real azure-core transport/response ABCs,
    # not clients or pipeline mocks and not imports from either test suite.
    from azure.core.exceptions import HttpResponseError
    from azure.core.pipeline.transport import HttpTransport, AsyncHttpTransport, HttpResponse, AsyncHttpResponse
    from azure.core.utils import case_insensitive_dict

    class _Buffer:
        def initialize(self, reply: _Reply) -> None:
            self.status_code = reply.status
            self.reason = "OK" if reply.status < 400 else "Offline fixture error"
            self.headers = case_insensitive_dict({"content-type": "application/json"})
            self.content_type = "application/json"
            self._body = _dump(reply.payload).encode("utf-8")
            self.is_closed = False
            self.is_stream_consumed = False

        @property
        def content(self) -> bytes:
            return self._body

        def body(self) -> bytes:
            return self._body

        def text(self, encoding: str | None = None) -> str:
            return self._body.decode(encoding or "utf-8")

        def json(self) -> Any:
            return json.loads(self._body)

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise HttpResponseError(response=self)

    class _SyncResponse(_Buffer, HttpResponse):
        def __init__(self, request: Any, reply: _Reply) -> None:
            HttpResponse.__init__(self, request, None)
            self.initialize(reply)

        def read(self) -> bytes:
            self.is_stream_consumed = True
            return self._body

        def close(self) -> None:
            self.is_closed = True

        def iter_bytes(self, **kwargs: Any):
            yield self._body

        def iter_raw(self, **kwargs: Any):
            yield self._body

        def stream_download(self, pipeline: Any, **kwargs: Any):
            return self.iter_bytes(**kwargs)

    class _AsyncResponse(_Buffer, AsyncHttpResponse):
        def __init__(self, request: Any, reply: _Reply) -> None:
            AsyncHttpResponse.__init__(self, request, None)
            self.initialize(reply)

        async def read(self) -> bytes:
            self.is_stream_consumed = True
            return self._body

        async def close(self) -> None:
            self.is_closed = True

        async def iter_bytes(self, **kwargs: Any):
            yield self._body

        async def iter_raw(self, **kwargs: Any):
            yield self._body

        def stream_download(self, pipeline: Any, **kwargs: Any):
            return self.iter_bytes(**kwargs)

        async def __aexit__(self, *args: Any) -> None:
            await self.close()

    class _SyncTransport(HttpTransport):
        def __init__(self, case: _Case) -> None:
            self.case = case

        def send(self, request: Any, **kwargs: Any) -> _SyncResponse:
            return _SyncResponse(request, self.case.receive(request, kwargs))

        def open(self) -> None:
            pass

        def close(self) -> None:
            pass

        def __enter__(self):
            self.open()
            return self

        def __exit__(self, *args: Any) -> None:
            self.close()

        def sleep(self, duration: float) -> None:
            raise AssertionError("Immediate offline fixtures must not trigger transport retries/sleeps")

    class _AsyncTransport(AsyncHttpTransport):
        def __init__(self, case: _Case) -> None:
            self.case = case

        async def send(self, request: Any, **kwargs: Any) -> _AsyncResponse:
            return _AsyncResponse(request, self.case.receive(request, kwargs))

        async def open(self) -> None:
            pass

        async def close(self) -> None:
            pass

        async def __aenter__(self):
            await self.open()
            return self

        async def __aexit__(self, *args: Any) -> None:
            await self.close()

        async def sleep(self, duration: float) -> None:
            raise AssertionError("Immediate offline fixtures must not trigger transport retries/sleeps")

    return _SyncTransport, _AsyncTransport


class _Context:
    def __init__(self, legacy_routes: bool) -> None:
        self.sdk = importlib.import_module(NAMESPACE)
        self.aio = importlib.import_module(NAMESPACE + ".aio")
        self.models = importlib.import_module(NAMESPACE + ".models")
        self.model_base = importlib.import_module(NAMESPACE + "._utils.model_base")
        self.async_patch = importlib.import_module(NAMESPACE + ".aio._patch")
        self.legacy_routes = legacy_routes
        self.moniker = f"azsdk-python-ai-finetuningsessions/{self.sdk.__version__}"
        self.user_agent_suffix = f" Python/{platform.python_version()} ({platform.platform()})"
        self.user_agent = self.moniker + self.user_agent_suffix
        self.sync_transport, self.async_transport = _transport_types()
        # The ONLY SDK behavior patched by the harness: starting background
        # heartbeats. Explicit heartbeat operations still use the real pipeline.
        self.sdk.FineTuningSession._start_heartbeat = lambda *args, **kwargs: None
        self.async_patch._start_heartbeat = lambda *args, **kwargs: None

    def client(self, case: _Case, asynchronous: bool = False) -> Any:
        from azure.core.credentials import AccessToken, AzureKeyCredential

        class _Credential:
            def get_token(self, *scopes: str, **kwargs: Any) -> Any:
                case.token_calls.append({"scopes": list(scopes), "options": _plain(kwargs)})
                return AccessToken(TOKEN, 4102444800)

        class _AsyncCredential:
            async def get_token(self, *scopes: str, **kwargs: Any) -> Any:
                return _Credential().get_token(*scopes, **kwargs)

        transport = (self.async_transport if asynchronous else self.sync_transport)(case)
        credential = (
            (_AsyncCredential() if asynchronous else _Credential()) if case.token_auth else AzureKeyCredential(KEY)
        )
        options = {
            "transport": transport,
            "retry_total": 0,
            "allow_insecure_http": False,
            # Forces selected per-operation api_version='v1' to work rather than
            # accidentally passing because the public client default is also v1.
            "api_version": "configured-not-on-wire",
            "logging_enable": False,
        }
        if self.legacy_routes:
            options["use_legacy_routes"] = True
        client_type = (self.aio if asynchronous else self.sdk).FineTuningSessionClient
        return client_type(ENDPOINT, credential, **options)

    def value(self, value: Any) -> Any:
        return json.loads(json.dumps(value, cls=self.model_base.SdkJSONEncoder, allow_nan=False))

    def model(self, case: _Case, value: Any, name: str, expected: dict, fields: tuple = ()) -> dict:
        case.equal(type(value).__name__, name, "Result model class")
        wire = self.value(value)
        case.equal(wire, expected, "Complete serialized result")
        case.equal(self.value(value.as_dict()), expected, "Model.as_dict() result")
        attributes = {field: self.value(getattr(value, field)) for field in fields}
        case.equal(attributes, {field: expected.get(field) for field in fields}, "Typed attribute values")
        return {"class": name, "json": wire, "attributes": attributes}

    def batch(self) -> list:
        m = self.models
        return [
            m.Datum(
                model_input=m.ModelInput(chunks=[m.ModelInputChunk(tokens=[1, 2, 3])]),
                loss_fn_inputs=m.LossFnInputs(
                    **{name: m.TensorData(**value) for name, value in BATCH[0]["loss_fn_inputs"].items()}
                ),
            ),
            m.Datum(
                model_input=self.mixed_input(),
                loss_fn_inputs=m.LossFnInputs(
                    **{name: m.TensorData(**value) for name, value in BATCH[1]["loss_fn_inputs"].items()}
                ),
            ),
        ]

    def mixed_input(self) -> Any:
        m = self.models
        return m.ModelInput(
            chunks=[
                m.ModelInputChunk(tokens=[1, 2]),
                m.ImageChunk(data=IMAGE, format="jpeg", expected_tokens=2),
                m.ModelInputChunk(tokens=[3]),
            ]
        )

    def exception(self, case: _Case, exc: Exception, name: str, expected: dict) -> dict:
        from azure.core.exceptions import HttpResponseError

        case.equal(type(exc).__name__, name, "Typed exception class")
        case.check(isinstance(exc, self.sdk.FineTuningSessionsError), "Exception must retain the SDK base class")
        case.check(isinstance(exc, HttpResponseError), "Exception must remain catchable as HttpResponseError")
        for field, value in expected.items():
            case.equal(getattr(exc, field), value, f"Exception.{field}")
        return {
            "class": type(exc).__name__,
            "message": str(exc),
            "args": _plain(exc.args),
            "metadata": {field: _plain(getattr(exc, field)) for field in ERROR_FIELDS if hasattr(exc, field)},
            "hierarchy": [base.__name__ for base in type(exc).__mro__],
        }


def _surface(ctx: _Context, case: _Case, client: Any) -> dict:
    modules = {"root": ctx.sdk, "aio": ctx.aio, "models": ctx.models}
    modules.update({name: importlib.import_module(NAMESPACE + "." + name) for name in ("operations", "aio.operations")})
    exports = {}
    for name, module in modules.items():
        names = list(module.__all__)
        case.check(
            len(names) == len(set(names)) and all(hasattr(module, item) for item in names),
            f"{name}.__all__ exports resolve at runtime",
        )
        exports[name] = sorted(names)
    signatures = {
        "sync.client": _signature(ctx.sdk.FineTuningSessionClient),
        "async.client": _signature(ctx.aio.FineTuningSessionClient),
        "sync.session": _signature(ctx.sdk.FineTuningSession),
    }
    for name in SYNC_METHODS:
        method = getattr(ctx.sdk.FineTuningSession, name)
        case.check(callable(method), f"FineTuningSession.{name} is callable")
        signatures["sync." + name] = _signature(method)
    for name in ASYNC_METHODS:
        method = getattr(ctx.aio.FineTuningSessionClient, name)
        case.check(inspect.iscoroutinefunction(method), f"Async client.{name} is an async callable")
        signatures["async." + name] = _signature(method)
    generated = {}
    for prefix, module in (("sync", modules["operations"]), ("async", modules["aio.operations"])):
        for name in GENERATED_METHODS:
            group, operation = name.split(".")
            operation_type = getattr(module, "SessionsOperations" if group == "sessions" else "CheckpointsOperations")
            generated[f"{prefix}.{name}"] = _signature(getattr(operation_type, operation))
    enums = {
        name: {member: item.value for member, item in getattr(ctx.models, name).__members__.items()}
        for name in (
            "CheckpointType",
            "FoundryFeaturesOptInKeys",
            "LossFn",
            "OperationStatus",
            "OperationType",
            "SessionStatus",
            "SessionType",
        )
    }
    groups = sorted(name for name in vars(client) if not name.startswith("_"))
    case.equal(
        groups, sorted(("sessions", "training", "checkpoints", "sampling", "operations")), "Client operation groups"
    )
    case.check(ctx.sdk.EngineDeadError is ctx.sdk.TrainingEngineError, "EngineDeadError alias")
    case.check(ctx.sdk.MalformedDatumError is ctx.sdk.RequestValidationError, "MalformedDatumError alias")
    return {
        "version": ctx.sdk.__version__,
        "exports": exports,
        "signatures": signatures,
        "generated_signatures": generated,
        "enums": enums,
        "client_groups": groups,
    }


def _serialization(ctx: _Context, case: _Case, client: Any) -> dict:
    del client
    m = ctx.models
    output = {}
    for name, value, expected, fields in (
        ("LoRAConfig", m.LoRAConfig(**LORA), LORA, tuple(LORA)),
        ("AdamParams", m.AdamParams(**ADAM), ADAM, tuple(ADAM)),
        ("SamplingParams", m.SamplingParams(**SAMPLING), SAMPLING, tuple(SAMPLING)),
        ("LossFnConfig", m.LossFnConfig(**LOSS_CONFIG), LOSS_CONFIG, tuple(LOSS_CONFIG)),
        (
            "FromCheckpoint",
            m.FromCheckpoint(source_session_id="session_source", checkpoint_id="checkpoint_source"),
            {"source_session_id": "session_source", "checkpoint_id": "checkpoint_source"},
            ("source_session_id", "checkpoint_id"),
        ),
        ("ModelInput", ctx.mixed_input(), MIXED_INPUT, ("chunks",)),
    ):
        output[name] = ctx.model(case, value, name, expected, fields)
    image = m.ImageChunk(data=IMAGE, format="jpeg", expected_tokens=2)
    case.equal(ctx.value(image), IMAGE_WIRE, "Image bytes are base64 on the wire")
    restored = m.ImageChunk(IMAGE_WIRE)
    case.check(restored.data == IMAGE and restored.length == 2, "Image bytes and token length round-trip")
    case.equal(ctx.value(ctx.batch()), BATCH, "Mixed-image Datum/LossFnInputs/TensorData construction")
    request = m.CreateSessionRequest(type="training", base_model=BASE_MODEL, user_metadata=METADATA)
    expected_request = {"type": "training", "base_model": BASE_MODEL, "user_metadata": METADATA}
    output["CreateSessionRequest"] = ctx.model(
        case, request, "CreateSessionRequest", expected_request, ("type", "base_model", "user_metadata", "lora_config")
    )
    error = m.ApiError(
        code="invalid_request",
        message="Invalid input",
        details=[m.ApiError(code="field", message="Bad data")],
        additional_info=METADATA,
        debug_info={"ref": "offline"},
    )
    error_wire = {
        "error": {
            "code": "invalid_request",
            "message": "Invalid input",
            "details": [{"code": "field", "message": "Bad data"}],
            "additionalInfo": METADATA,
            "debugInfo": {"ref": "offline"},
        }
    }
    output["ApiErrorResponse"] = ctx.model(
        case, m.ApiErrorResponse(error=error), "ApiErrorResponse", error_wire, ("error",)
    )
    round_trip = ctx.model_base._deserialize(m.ApiErrorResponse, error_wire)
    case.equal(ctx.value(round_trip.error.additional_info), METADATA, "ApiError additionalInfo attribute round-trip")
    case.equal(round_trip.error.details[0].code, "field", "Nested error models deserialize")
    constructors = {
        "FineTuningSessionsError": {},
        "BatchTooLargeError": {"max_batch_size": 1, "actual_batch_size": 2},
        "NoCapacityError": {"retry_after_sec": 1.5, "reason": "engine_busy"},
        "RateLimitedError": {"retry_after_sec": 2.0, "reason": "rate_limited"},
        "TrainingEngineError": {"session_id": SESSION, "error_code": "worker_crashed", "debug_ref": "offline"},
        "OperationResultUnavailableError": {
            "operation_completed": True,
            "error_code": "operation_completed_result_unavailable",
            "debug_ref": "offline",
        },
        "ContentionError": {"retry_after_sec": 0.5, "reason": "busy"},
        "RequestValidationError": {"field": "data", "error_code": "invalid_request", "debug_ref": "offline"},
        "RequestRetryableError": {"retry_after_sec": 1.0, "error_code": "request_timeout", "debug_ref": "offline"},
    }
    output["exceptions"] = {
        name: ctx.exception(case, getattr(ctx.sdk, name)("offline error", **fields), name, fields)
        for name, fields in constructors.items()
    }
    case.check(issubclass(ctx.sdk.RateLimitedError, ctx.sdk.NoCapacityError), "Rate limit remains a capacity error")
    return output


def _create_options(ctx: _Context, index: int) -> tuple[dict, dict]:
    options = {
        "base_model": BASE_MODEL,
        "user_metadata": METADATA,
        "training_type": "DeveloperTier",
        "timeout_sec": 5.0,
    }
    body = {"type": "training", "base_model": BASE_MODEL, "user_metadata": METADATA, "training_type": "DeveloperTier"}
    if index == 1:
        options["lora_config"], body["lora_config"] = ctx.models.LoRAConfig(**LORA), LORA
    if index == 2:
        options["from_checkpoint"] = ctx.models.FromCheckpoint(
            source_session_id="model_source", checkpoint_id="checkpoint_source"
        )
        body["from_checkpoint"] = {"source_session_id": "session_source", "checkpoint_id": "checkpoint_source"}
    return options, body


def _checkpoint_expected(request_id: str, path: str, result: dict) -> dict:
    return {
        "type": "save_checkpoint",
        "operation_id": request_id,
        "status": "succeeded",
        "checkpoint_id": path,
        "path": "",
        **result,
    }


def _sync_create(ctx: _Context, case: _Case, client: Any) -> list:
    output = []
    for index, (raw, canonical, resource) in enumerate(IDENTITIES):
        options, body = _create_options(ctx, index)
        case.create(raw, resource, body, f"create_{index}")
        session = ctx.sdk.FineTuningSession.create(client, **options)
        state = {
            "session_id": session.session_id,
            "resource_id": session._resource_session_id,
            "heartbeat_id": session._heartbeat_session_id,
        }
        case.equal(
            state,
            {"session_id": canonical, "resource_id": resource, "heartbeat_id": canonical},
            "Canonical versus actual resource identity",
        )
        case.check(session._heartbeat_thread is None, "No background heartbeat thread")
        case.operation("checkpoint", {"path": "identity"}, {}, f"identity_{index}", resource=resource, server_id=raw)
        saved = session.save_weights("identity")
        output.append(
            {
                "state": state,
                "followup": ctx.model(
                    case,
                    saved,
                    "SaveCheckpointOperationResult",
                    _checkpoint_expected(f"identity_{index}", "identity", {}),
                    ("checkpoint_id", "path"),
                ),
            }
        )
    return output


def _sync_checkpoint_create(ctx: _Context, case: _Case, client: Any) -> list:
    output = []
    for index, path in enumerate(CHECKPOINT_PATHS):
        body = {
            "type": "training",
            "base_model": BASE_MODEL,
            "from_checkpoint": {"source_session_id": "session_source", "checkpoint_id": "checkpoint_source"},
        }
        case.create("model_resumed", "model_resumed", body, f"resume_{index}")
        session = ctx.sdk.FineTuningSession.create_from_checkpoint(
            client, checkpoint_path=path, base_model=BASE_MODEL, timeout_sec=5.0
        )
        state = {"session_id": session.session_id, "resource_id": session._resource_session_id}
        case.equal(state, {"session_id": "session_resumed", "resource_id": "model_resumed"}, "Resumed session identity")
        output.append(state)
    return output


def _training_plan(case: _Case, action: str, request_id: str, configured: bool = False) -> tuple[dict, str, tuple]:
    if action == "optim_step":
        body, payload = {"adam_params": ADAM}, OPTIMIZER
        expected = {**payload, "grad_norm": 0.75, "step_count": 3}
        model, fields, discriminator = "OptimStepOperationResult", ("grad_norm", "step_count", "metrics"), "optim_step"
    else:
        inputs = {"data": BATCH, "loss_fn": "importance_sampling" if configured else "cross_entropy"}
        if configured:
            inputs["loss_fn_config"] = LOSS_CONFIG
        body = {"forward_input" if action == "forward" else "forward_backward_input": inputs}
        payload = FORWARD if action == "forward" else BACKWARD
        expected = {**payload, **({"total_loss": 1.25} if action == "forward_backward" else {})}
        model, fields, discriminator = (
            "ForwardBackwardOperationResult",
            ("total_loss", "loss_fn_output_type", "loss_fn_outputs", "per_datum_logprobs", "metrics"),
            "forward_backward",
        )
    case.operation(action, body, payload, request_id)
    return (
        {**expected, "operation_id": request_id, "status": "succeeded", "type": discriminator},
        model,
        ("operation_id", "status", "type", *fields),
    )


def _sync_training(ctx: _Context, case: _Case, client: Any) -> dict:
    session = ctx.sdk.FineTuningSession(client, SESSION)
    output = {}
    for action in ("forward", "forward_backward", "optim_step"):
        configured = action == "forward_backward"
        expected, model, fields = _training_plan(case, action, action, configured)
        argument = ctx.models.AdamParams(**ADAM) if action == "optim_step" else ctx.batch()
        options = (
            {"loss_fn": "importance_sampling", "loss_fn_config": ctx.models.LossFnConfig(**LOSS_CONFIG)}
            if configured
            else {}
        )
        result = getattr(session, action)(argument, **options)
        output[action] = ctx.model(case, result, model, expected, fields)
    return output


def _sync_checkpoints(ctx: _Context, case: _Case, client: Any) -> list:
    session = ctx.sdk.FineTuningSession(client, SESSION)
    output = []
    for index, payload in enumerate(
        ({"path": "loom://session_workload/weights/train"}, {"checkpoint_id": "server_override", "path": "server_path"})
    ):
        request_id = f"save_{index}"
        case.operation("checkpoint", {"path": "train"}, payload, request_id)
        output.append(
            ctx.model(
                case,
                session.save_weights("train"),
                "SaveCheckpointOperationResult",
                _checkpoint_expected(request_id, "train", payload),
                ("checkpoint_id", "path"),
            )
        )
    for index, path in enumerate((None, "sampler_explicit")):
        body = {"seq_id": 7, "sampling_session_seq_id": 2}
        if path is not None:
            body["path"] = path
        payload = {"type": "save_weights_for_sampler", "sampling_session_id": "sampling_workload"}
        request_id = f"sampler_{index}"
        case.operation("checkpoint_sample", body, payload, request_id)
        result = session.save_weights_for_sampler(7, sampling_session_seq_id=2, path=path)
        expected = {
            **payload,
            "type": "save_sampler_weights",
            "checkpoint_id": path or "ss2_seq7",
            "operation_id": request_id,
            "status": "succeeded",
        }
        output.append(
            ctx.model(
                case, result, "SaveSamplerWeightsOperationResult", expected, ("checkpoint_id", "sampling_session_id")
            )
        )
    return output


def _sample_plan(ctx: _Context, case: _Case, index: int) -> tuple[Any, dict, dict]:
    prompt = [1, 2] if index == 0 else ctx.mixed_input()
    prompt_wire = {"chunks": [{"tokens": [1, 2]}]} if index == 0 else MIXED_INPUT
    options = {
        "checkpoint_id": "sampler_explicit",
        "num_samples": 2,
        "sampling_session_id": "sampling_workload",
        "seq_id": 7,
        "prompt_logprobs": True,
        "topk_prompt_logprobs": 2,
    }
    body = {
        "prompt": prompt_wire,
        "sampling_params": SAMPLING,
        **{key: value for key, value in options.items() if key != "checkpoint_id"},
    }
    request_id = f"sample_{index}"
    case.operation("sample", body, SAMPLES, request_id, query=(("checkpoint_id", "sampler_explicit"),))
    return prompt, options, {**SAMPLES, "type": "sample", "status": "succeeded", "operation_id": request_id}


def _sample_result(ctx: _Context, case: _Case, result: Any, expected: dict) -> dict:
    value = ctx.model(
        case,
        result,
        "SampleOperationResult",
        expected,
        ("sequences", "prompt_logprobs", "topk_prompt_logprobs", "metrics"),
    )
    case.equal(result.sequences[0].tokens, [31, 32], "Sample token IDs remain integers")
    case.equal(result.sequences[0].text, "caf\u00e9", "Sample text")
    case.check(result.sequences[1].text is None and result.sequences[1].logprobs is None, "Nullable sequence fields")
    return value


def _sync_sampling(ctx: _Context, case: _Case, client: Any) -> list:
    session = ctx.sdk.FineTuningSession(client, SESSION)
    output = []
    for index in range(2):
        prompt, options, expected = _sample_plan(ctx, case, index)
        result = session.sample(prompt, ctx.models.SamplingParams(**SAMPLING), **options)
        output.append(_sample_result(ctx, case, result, expected))
    return output


def _sync_lifecycle(ctx: _Context, case: _Case, client: Any) -> list:
    output = []
    for raw, canonical, resource in IDENTITIES:
        session = ctx.sdk.FineTuningSession(client, raw)
        case.expect("POST", f"/{resource}/heartbeat", {"session_id": resource})
        heartbeat = ctx.model(case, session.heartbeat(), "HeartbeatResponse", {"session_id": resource}, ("session_id",))
        case.expect("POST", f"/{resource}/complete", {})
        case.equal(session.close(), None, "Close return value")
        for status in (200, 404):
            case.expect("DELETE", f"/{resource}", {}, status=status)
            case.equal(session.delete(), None, "Delete is idempotent")
        case.check(session._heartbeat_stop.is_set() and session._heartbeat_thread is None, "Lifecycle stops heartbeats")
        output.append(
            {"session_id": session.session_id, "resource_id": session._resource_session_id, "heartbeat": heartbeat}
        )
        case.equal(session.session_id, canonical, "Lifecycle canonical session ID")
    return output


def _generated_specs() -> list[tuple]:
    timestamp = "2026-09-17T12:00:00Z"
    summary = {
        "session_id": SESSION,
        "base_model": BASE_MODEL,
        "status": "running",
        "is_lora": True,
        "lora_rank": 16,
        "corrupted": False,
        "last_request_time": timestamp,
    }
    session = {
        "session_id": SESSION,
        "type": "training",
        "status": "running",
        "model_data": {"base_model": BASE_MODEL, "lora_config": LORA, "model_name": "offline-model"},
    }
    page = {"data": [summary], "cursor": {"offset": 3, "limit": 2, "total_count": 4}}
    checkpoints = {
        "checkpoints": [
            {"checkpoint_id": "train", "checkpoint_type": "training", "time": timestamp},
            {"checkpoint_id": "sampler", "checkpoint_type": "sampler", "time": timestamp},
        ]
    }
    return [
        (
            "sessions.get",
            "GET",
            f"/{SESSION}",
            {"session_id": SESSION},
            session,
            "Session",
            ("session_id", "status", "model_data"),
            (),
        ),
        (
            "sessions.list",
            "GET",
            "",
            {"offset": 3, "limit": 2},
            page,
            "SessionList",
            ("data", "cursor"),
            (("limit", 2), ("offset", 3)),
        ),
        (
            "sessions.heartbeat",
            "POST",
            f"/{SESSION}/heartbeat",
            {"session_id": SESSION},
            {"session_id": SESSION},
            "HeartbeatResponse",
            ("session_id",),
            (),
        ),
        (
            "checkpoints.get",
            "GET",
            f"/{SESSION}/checkpoints/train",
            {"session_id": SESSION, "checkpoint_id": "train"},
            {"base_model": BASE_MODEL, "is_lora": True, "lora_rank": 16},
            "CheckpointInfo",
            ("base_model", "is_lora", "lora_rank"),
            (),
        ),
        (
            "checkpoints.list",
            "GET",
            f"/{SESSION}/checkpoints",
            {"session_id": SESSION},
            checkpoints,
            "CheckpointList",
            ("checkpoints",),
            (),
        ),
    ]


def _generated_call(case: _Case, client: Any, spec: tuple, hooks: list) -> tuple[Any, dict]:
    name, method, suffix, arguments, payload, _, _, query = spec
    case.expect(method, suffix, payload, query=query)
    group, operation = name.split(".")
    target = getattr(getattr(client, group), operation)

    def on_response(response: Any) -> None:
        hooks.append(
            {
                "method": response.http_request.method,
                "url": response.http_request.url,
                "status": response.http_response.status_code,
            }
        )

    options = {
        **arguments,
        "foundry_features": PREVIEW,
        "api_version": "v1",
        "headers": {"x-compatibility-probe": "shared"},
        "raw_response_hook": on_response,
    }
    inspect.signature(target).bind(**options)
    case.check(True, f"{name} legacy api_version/headers/hook keywords bind")
    return target, options


def _sync_generated(ctx: _Context, case: _Case, client: Any) -> dict:
    output, hooks = {}, []
    for spec in _generated_specs():
        target, options = _generated_call(case, client, spec, hooks)
        result = target(**options)
        output[spec[0]] = ctx.model(case, result, spec[5], spec[4], spec[6])
    case.equal(len(hooks), 5, "All real generated calls invoke response hooks")
    case.check(
        all(request["headers"].get("x-compatibility-probe") == "shared" for request in case.requests),
        "Per-operation custom headers reach transport",
    )
    return {"results": output, "hooks": hooks}


def _http_errors() -> tuple:
    return (
        (
            413,
            {
                "detail": {
                    "message": "Batch size (2) exceeds the maximum allowed (1)",
                    "field": "forward_backward_input.data",
                }
            },
            "BatchTooLargeError",
            {"max_batch_size": 1, "actual_batch_size": 2},
        ),
        (
            422,
            {
                "detail": {
                    "type": "validation_error",
                    "message": "Invalid offline datum",
                    "field": "forward_backward_input.data",
                    "error_code": "invalid_request",
                    "debug_ref": "debug_fixture",
                }
            },
            "RequestValidationError",
            {"field": "forward_backward_input.data", "error_code": "invalid_request", "debug_ref": "debug_fixture"},
        ),
    )


def _poll_errors() -> tuple:
    return (
        (
            {
                "status": "failed",
                "error": "Offline engine stopped",
                "error_code": "worker_crashed",
                "debug_ref": "debug_fixture",
            },
            "TrainingEngineError",
            {"session_id": SESSION, "error_code": "worker_crashed", "debug_ref": "debug_fixture"},
        ),
        (
            {
                "status": "failed",
                "error": "Completed result unavailable",
                "error_code": "operation_completed_result_unavailable",
                "should_retry": True,
                "debug_ref": "debug_fixture",
            },
            "OperationResultUnavailableError",
            {
                "operation_completed": True,
                "error_code": "operation_completed_result_unavailable",
                "debug_ref": "debug_fixture",
            },
        ),
    )


def _error_plan(case: _Case, index: int, specification: tuple, polling: bool) -> tuple[str, dict]:
    body = {"forward_backward_input": {"data": BATCH, "loss_fn": "cross_entropy"}}
    if polling:
        payload, name, fields = specification
        case.operation("forward_backward", body, payload, f"failed_{index}", failed=True)
    else:
        status, payload, name, fields = specification
        case.expect("POST", f"/{SESSION}/forward_backward", payload, body=body, status=status)
    return name, fields


def _sync_errors(ctx: _Context, case: _Case, client: Any, *, polling: bool = False) -> list:
    session, output = ctx.sdk.FineTuningSession(client, SESSION), []
    for index, spec in enumerate(_poll_errors() if polling else _http_errors()):
        name, fields = _error_plan(case, index, spec, polling)
        try:
            session.forward_backward(ctx.batch())
        except ctx.sdk.FineTuningSessionsError as exc:
            output.append(ctx.exception(case, exc, name, fields))
        else:
            raise AssertionError(f"Expected terminal {name}")
    return output


async def _async_create(ctx: _Context, case: _Case, client: Any) -> list:
    output, resource_map = [], {}
    for index, (raw, canonical, resource) in enumerate(IDENTITIES):
        options, body = _create_options(ctx, index)
        case.create(raw, resource, body, f"create_{index}")
        session_id = await client.create_session(**options)
        resource_map[canonical] = resource
        case.equal(session_id, canonical, "Async canonical session ID")
        case.equal(client._session_resource_ids, resource_map, "Async resource ID map")
        case.equal(client._heartbeat_tasks, {}, "No background heartbeat tasks")
        case.operation("checkpoint", {"path": "identity"}, {}, f"identity_{index}", resource=resource, server_id=raw)
        saved = await client.save_weights(session_id, "identity")
        output.append(
            {
                "session_id": session_id,
                "resource_map": dict(client._session_resource_ids),
                "followup": ctx.model(
                    case,
                    saved,
                    "SaveCheckpointOperationResult",
                    _checkpoint_expected(f"identity_{index}", "identity", {}),
                    ("checkpoint_id", "path"),
                ),
            }
        )
    return output


async def _async_checkpoint_create(ctx: _Context, case: _Case, client: Any) -> list:
    output = []
    for index, path in enumerate(CHECKPOINT_PATHS):
        body = {
            "type": "training",
            "base_model": BASE_MODEL,
            "from_checkpoint": {"source_session_id": "session_source", "checkpoint_id": "checkpoint_source"},
        }
        case.create("model_resumed", "model_resumed", body, f"resume_{index}")
        session_id = await client.create_session_from_checkpoint(
            checkpoint_path=path, base_model=BASE_MODEL, timeout_sec=5.0
        )
        case.equal(session_id, "session_resumed", "Async resumed identity")
        case.equal(client._session_resource_ids, {"session_resumed": "model_resumed"}, "Async resumed resource map")
        output.append({"session_id": session_id, "resource_map": dict(client._session_resource_ids)})
    return output


async def _resolve_handle(case: _Case, handle: Any, *, posted_at: int, pending: bool = False) -> Any:
    case.equal(len(case.requests), posted_at + 1, "Submission completes before returning the handle")
    if pending:
        case.equal(type(handle).__name__, "PendingRequests", "POST-only handle type")
        case.check(inspect.iscoroutinefunction(handle.poll_result), "PendingRequests.poll_result is async")
        return await handle.poll_result(poll_min_sec=0.001, poll_max_sec=0.001)
    case.check(isinstance(handle, asyncio.Future), "Two-stage async API returns an awaitable Future/Task")
    result = await handle
    case.check(handle.done() and not handle.cancelled(), "Returned task resolves normally")
    return result


async def _async_training(ctx: _Context, case: _Case, client: Any) -> dict:
    output = {}
    for action in ("forward", "forward_backward", "optim_step"):
        variants = ("",) if action == "optim_step" else ("", "_post", "_async")
        for variant in variants:
            name = action + variant
            configured = action == "forward_backward"
            expected, model, fields = _training_plan(case, action, name, configured)
            options = (
                {"loss_fn": "importance_sampling", "loss_fn_config": ctx.models.LossFnConfig(**LOSS_CONFIG)}
                if configured
                else {}
            )
            if name == "forward_backward_async":
                options.update(poll_min_sec=0.001, poll_max_sec=0.001, max_chunks_per_wave=1)
            argument = ctx.models.AdamParams(**ADAM) if action == "optim_step" else ctx.batch()
            before = len(case.requests)
            result = await getattr(client, name)(SESSION, argument, **options)
            if variant:
                result = await _resolve_handle(case, result, posted_at=before, pending=variant == "_post")
            output[name] = ctx.model(case, result, model, expected, fields)
    return output


async def _async_checkpoints(ctx: _Context, case: _Case, client: Any) -> dict:
    output = {}
    for variant in ("_post", "_async"):
        name = "optim_step" + variant
        expected, model, fields = _training_plan(case, "optim_step", name)
        before = len(case.requests)
        options = {"poll_min_sec": 0.001, "poll_max_sec": 0.001} if variant == "_async" else {}
        handle = await getattr(client, name)(SESSION, ctx.models.AdamParams(**ADAM), **options)
        result = await _resolve_handle(case, handle, posted_at=before, pending=variant == "_post")
        output[name] = ctx.model(case, result, model, expected, fields)
    for variant in ("", "_post", "_async"):
        name = "save_weights" + variant
        options = {"step_number": 7, "metrics": METADATA} if variant else {}
        payload = {"path": "loom://session_workload/weights/train"}
        case.operation("checkpoint", {"path": "train", **options}, payload, name)
        before = len(case.requests)
        result = await getattr(client, name)(SESSION, "train", **options)
        if variant:
            result = await _resolve_handle(case, result, posted_at=before, pending=variant == "_post")
        output[name] = ctx.model(
            case,
            result,
            "SaveCheckpointOperationResult",
            _checkpoint_expected(name, "train", payload),
            ("checkpoint_id", "path"),
        )
    return output


async def _async_sampling(ctx: _Context, case: _Case, client: Any) -> list:
    output = []
    for index in range(3):
        name = "save_weights_for_sampler_async" if index == 0 else "save_weights_and_get_sampling_client_async"
        body = {"seq_id": 0, "path": "sampler_explicit"}
        if index:
            body["sampling_session_seq_id"] = index
        payload = {"type": "save_weights_for_sampler", "sampling_session_id": "sampling_workload"}
        request_id = f"sampler_{index}"
        case.operation("checkpoint_sample", body, payload, request_id)
        before = len(case.requests)
        handle = await getattr(client, name)(SESSION, "sampler_explicit")
        result = await _resolve_handle(case, handle, posted_at=before)
        expected = {
            **payload,
            "type": "save_sampler_weights",
            "checkpoint_id": "sampler_explicit",
            "operation_id": request_id,
            "status": "succeeded",
        }
        output.append(
            ctx.model(
                case, result, "SaveSamplerWeightsOperationResult", expected, ("checkpoint_id", "sampling_session_id")
            )
        )
    case.equal(
        client._sampling_session_seq,
        {SESSION: 2},
        "Ephemeral sampler sequence increments independently of persisted save",
    )
    for index in range(2):
        prompt, options, expected = _sample_plan(ctx, case, index)
        result = await client.sample(SESSION, prompt, ctx.models.SamplingParams(**SAMPLING), **options)
        output.append(_sample_result(ctx, case, result, expected))
    return output


async def _async_lifecycle(ctx: _Context, case: _Case, client: Any) -> list:
    output = []
    for index, (raw, canonical, resource) in enumerate(IDENTITIES):
        case.create(raw, resource, {"type": "training", "base_model": BASE_MODEL}, f"lifecycle_{index}")
        session_id = await client.create_session(base_model=BASE_MODEL, timeout_sec=5.0)
        case.equal(session_id, canonical, "Lifecycle canonical ID")
        case.equal(client._session_resource_ids[session_id], resource, "Lifecycle resource map")
        # Background heartbeats are disabled. Explicitly exercise the real
        # generated heartbeat using the resource retained by create_session.
        case.expect("POST", f"/{resource}/heartbeat", {"session_id": resource})
        heartbeat = await client.sessions.heartbeat(
            client._session_resource_ids[session_id], foundry_features=PREVIEW, api_version="v1"
        )
        output.append(ctx.model(case, heartbeat, "HeartbeatResponse", {"session_id": resource}, ("session_id",)))
        case.expect("POST", f"/{resource}/complete", {})
        case.equal(await client.close_session(session_id), None, "Async close result")
        case.expect("DELETE", f"/{resource}", {}, status=404 if index == 2 else 200)
        case.equal(await client.delete_session(session_id), None, "Async delete result")
        case.equal(client._session_resource_ids, {}, "Delete clears canonical/resource mapping even on 404")
    case.expect("DELETE", f"/{SESSION}", {}, status=404)
    case.equal(await client.delete_session(SESSION), None, "Deleting an already absent session is idempotent")
    case.equal(client._heartbeat_tasks, {}, "Lifecycle leaves no heartbeat tasks")
    return output


async def _async_generated(ctx: _Context, case: _Case, client: Any) -> dict:
    output, hooks = {}, []
    case.equal(
        sorted(name for name in vars(client) if not name.startswith("_")),
        sorted(("sessions", "training", "checkpoints", "sampling", "operations")),
        "Async client operation groups",
    )
    for spec in _generated_specs():
        target, options = _generated_call(case, client, spec, hooks)
        result = await target(**options)
        output[spec[0]] = ctx.model(case, result, spec[5], spec[4], spec[6])
    case.equal(len(hooks), 5, "All real async generated calls invoke response hooks")
    case.check(
        all(request["headers"].get("x-compatibility-probe") == "shared" for request in case.requests),
        "Async per-operation headers reach transport",
    )
    return {"results": output, "hooks": hooks}


async def _async_errors(ctx: _Context, case: _Case, client: Any, *, polling: bool = False) -> list:
    output = []
    for index, spec in enumerate(_poll_errors() if polling else _http_errors()):
        name, fields = _error_plan(case, index, spec, polling)
        try:
            await client.forward_backward(SESSION, ctx.batch())
        except ctx.sdk.FineTuningSessionsError as exc:
            output.append(ctx.exception(case, exc, name, fields))
        else:
            raise AssertionError(f"Expected terminal {name}")
    return output


SYNC_CASES: tuple[tuple[str, Callable], ...] = (
    ("surface_and_signatures", _surface),
    ("serialization_and_error_contracts", _serialization),
    ("sync_create_identifiers", _sync_create),
    ("sync_create_from_checkpoint", _sync_checkpoint_create),
    ("sync_training", _sync_training),
    ("sync_checkpoints", _sync_checkpoints),
    ("sync_sampling", _sync_sampling),
    ("sync_lifecycle", _sync_lifecycle),
    ("sync_generated_reads", _sync_generated),
    ("sync_http_errors", _sync_errors),
    ("sync_poll_errors", lambda ctx, case, client: _sync_errors(ctx, case, client, polling=True)),
)
ASYNC_CASES: tuple[tuple[str, Callable], ...] = (
    ("async_create_identifiers", _async_create),
    ("async_create_from_checkpoint", _async_checkpoint_create),
    ("async_training", _async_training),
    ("async_checkpoint_pipeline", _async_checkpoints),
    ("async_sampling", _async_sampling),
    ("async_lifecycle", _async_lifecycle),
    ("async_generated_reads", _async_generated),
    ("async_http_errors", _async_errors),
    ("async_poll_errors", lambda ctx, case, client: _async_errors(ctx, case, client, polling=True)),
)
CASE_NAMES = tuple(name for name, _ in (*SYNC_CASES, *ASYNC_CASES))


async def _run_async_cases(ctx: _Context, results: dict) -> None:
    for name, function in ASYNC_CASES:
        case = _Case(name, ctx, token_auth=name == "async_generated_reads")
        existing_tasks = asyncio.all_tasks()
        output, error = None, None
        try:
            async with ctx.client(case, asynchronous=True) as client:
                output = await asyncio.wait_for(function(ctx, case, client), timeout=15.0)
        except Exception as exc:
            error = exc
        # A failing handle assertion must not leave its polling task running
        # into another case. No heartbeat/task leakage is treated as success.
        pending = asyncio.all_tasks() - existing_tasks
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
        if error is None:
            try:
                case.equal(len(pending), 0, "No unawaited SDK tasks remain after the case")
            except Exception as exc:
                error = exc
        results[name] = case.finish(output, error)


def _snapshot(package: Path, legacy_routes: bool) -> dict:
    sys.dont_write_bytecode = True
    _offline_environment()
    if any(name == NAMESPACE or name.startswith(NAMESPACE + ".") for name in sys.modules):
        raise RuntimeError("SDK was already imported; refusing a contaminated snapshot process")
    package = _check_package(package)
    before = _source_hashes(package)
    # Windows asyncio may create an internal wakeup socket here. The SDK has not
    # been imported, and all later socket connections (including loopback) fail.
    loop = asyncio.new_event_loop()
    _install_offline_guard()
    sys.path.insert(0, str(package))
    try:
        logging.getLogger("azure").setLevel(logging.CRITICAL)
        from azure.core.settings import settings

        settings.tracing_enabled = False
        ctx = _Context(legacy_routes)
        expected_origin = (package / MODULE / "__init__.py").resolve()
        if Path(ctx.sdk.__file__).resolve() != expected_origin:
            raise RuntimeError(f"Imported the wrong SDK: {ctx.sdk.__file__}; expected {expected_origin}")
        results: dict[str, dict] = {}
        for name, function in SYNC_CASES:
            case = _Case(name, ctx, token_auth=name == "sync_generated_reads")
            try:
                with ctx.client(case) as client:
                    output = function(ctx, case, client)
                results[name] = case.finish(output)
            except Exception as exc:
                results[name] = case.finish(error=exc)
        loop.run_until_complete(_run_async_cases(ctx, results))
        origins = {}
        for name, module in sorted(sys.modules.items()):
            if name == NAMESPACE or name.startswith(NAMESPACE + "."):
                path = Path(module.__file__).resolve()
                path.relative_to((package / MODULE).resolve())  # Raises on any cross-root import.
                origins[name] = path.relative_to(package).as_posix()
        after = _source_hashes(package)
        if before != after:
            raise RuntimeError("SDK source files changed during the read-only snapshot")
        return {
            "schema": 1,
            "namespace": NAMESPACE,
            "source": {
                "package": str(package),
                "origin": str(expected_origin),
                "imported_modules": origins,
                "sha256": hashlib.sha256(_dump(before).encode()).hexdigest(),
                "unchanged": True,
            },
            "runtime": {
                "legacy_routes": legacy_routes,
                "network_guard": True,
                "write_guard": True,
                "heartbeat_start_disabled": True,
                "bytecode_writes": False,
            },
            "normalizations": NORMALIZATIONS,
            "limitations": LIMITATIONS,
            "cases": results,
            "counts": {
                "cases": len(results),
                "checks": sum(item["checks"] for item in results.values()),
                "requests": sum(len(item["requests"]) for item in results.values()),
            },
        }
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.run_until_complete(loop.shutdown_default_executor())
        loop.close()


def _differences(left: Any, right: Any, path: str = "") -> list[str]:
    """Type-sensitive recursive diff; bool/int/float are NOT interchangeable."""
    if type(left) is not type(right):
        return [f"{path}: Loom={_dump(left)}; public={_dump(right)}"]
    if isinstance(left, dict):
        result = []
        for key in sorted(left.keys() | right.keys()):
            child = f"{path}.{key}" if path else key
            if key not in left:
                result.append(f"{child}: public-only value {_dump(right[key])}")
            elif key not in right:
                result.append(f"{child}: missing public value (Loom={_dump(left[key])})")
            else:
                result.extend(_differences(left[key], right[key], child))
        return result
    if isinstance(left, list):
        result = [] if len(left) == len(right) else [f"{path}: lengths Loom={len(left)}, public={len(right)}"]
        for index, (old, new) in enumerate(zip(left, right)):
            result.extend(_differences(old, new, f"{path}[{index}]"))
        return result
    return [] if left == right else [f"{path}: Loom={_dump(left)}; public={_dump(right)}"]


def _surface_allowances(left: dict, right: dict) -> tuple[dict, dict, list[str]]:
    # Work on copies: snapshots always retain the full actual observed surface.
    left, right = json.loads(_dump(left)), json.loads(_dump(right))
    notes = []
    for group, old in left["exports"].items():
        new = right["exports"].get(group, [])
        extras = set(new) - set(old)
        allowed = extras if group == "root" else extras & MODEL_ADDITIONS if group == "models" else set()
        if allowed:
            right["exports"][group] = sorted(set(new) - allowed)
            notes.append(f"Additive {group} exports: {', '.join(sorted(allowed))}")
    enum_name = "FoundryFeaturesOptInKeys"
    for name, value in FEATURE_ADDITIONS.items():
        if name not in left["enums"][enum_name] and right["enums"][enum_name].get(name) == value:
            del right["enums"][enum_name][name]
            notes.append(f"Additive shared Foundry feature: {name}={value}")
    for target, keyword in (
        ("sync.client", "use_legacy_routes"),
        ("async.client", "use_legacy_routes"),
        ("async.client", "allow_insecure_http"),
    ):
        old, new = left["signatures"][target], right["signatures"][target]
        addition = {"name": keyword, "kind": "KEYWORD_ONLY", "default": False}
        if not any(item["name"] == keyword for item in old) and addition in new:
            new.remove(addition)
            reason = (
                "legacy accepted this flag through **kwargs"
                if keyword == "allow_insecure_http"
                else "ignored compatibility option; neither worker sets it"
            )
            notes.append(f"{target}: explicit {keyword}=False ({reason})")
    api_version = {"name": "api_version", "kind": "KEYWORD_ONLY"}
    for target, old in left["generated_signatures"].items():
        new = right["generated_signatures"].get(target, [])
        if (
            api_version in old
            and not any(item["name"] == "api_version" for item in new)
            and any(item["kind"] == "VAR_KEYWORD" for item in new)
        ):
            old.remove(api_version)
            notes.append(f"{target}: api_version accepted through **kwargs; real v1 wire request checked")
    return left, right, notes


def _run_worker(package: Path, *, legacy_routes: bool) -> dict:
    command = [sys.executable, "-I", "-B", "-X", "utf8", str(Path(__file__).resolve()), "--snapshot", str(package)]
    if legacy_routes:
        command.append("--legacy-routes")
    completed = subprocess.run(
        command, cwd=package, capture_output=True, text=True, encoding="utf-8", timeout=120, check=False
    )
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Snapshot did not produce JSON for {package}:\n{completed.stdout}\n{completed.stderr}"
        ) from exc
    if completed.returncode not in (0, 1) or "fatal" in report:
        raise RuntimeError(f"Snapshot setup failed for {package}: {_dump(report)}\n{completed.stderr}")
    expected_runtime = {
        "legacy_routes": legacy_routes,
        "network_guard": True,
        "write_guard": True,
        "heartbeat_start_disabled": True,
        "bytecode_writes": False,
    }
    if report.get("schema") != 1 or report.get("namespace") != NAMESPACE or report.get("runtime") != expected_runtime:
        raise RuntimeError("Unexpected snapshot schema, namespace, or isolation flags")
    source = report.get("source", {})
    if (
        Path(source.get("package", "")).resolve() != package
        or Path(source.get("origin", "")).resolve() != (package / MODULE / "__init__.py").resolve()
        or source.get("unchanged") is not True
    ):
        raise RuntimeError("Snapshot source origin/integrity verification failed")
    if set(report.get("cases", {})) != set(CASE_NAMES):
        raise RuntimeError("Snapshot did not execute exactly the required 20 cases")
    if completed.returncode != (0 if all(case["ok"] for case in report["cases"].values()) else 1):
        raise RuntimeError("Snapshot exit code disagrees with its case outcomes")
    return report


def _compare(loom: dict, public: dict) -> int:
    failed, allowances = [], []
    for name in CASE_NAMES:
        left, right = loom["cases"][name], public["cases"][name]
        differences = []
        if not left["ok"] or not right["ok"]:
            differences.append(
                f"Case must succeed independently in both SDKs; Loom={left.get('error')}, public={right.get('error')}"
            )
        elif name == "surface_and_signatures":
            old_surface, new_surface, allowances = _surface_allowances(left["output"], right["output"])
            left, right = {**left, "output": old_surface}, {**right, "output": new_surface}
        differences.extend(_differences(left, right, name))
        if differences:
            failed.append(name)
        print(
            f"{'FAIL' if differences else 'PASS'} {name}: requests {len(left['requests'])}/{len(right['requests'])}, checks {left['checks']}/{right['checks']} (Loom/public)"
        )
        for difference in differences[:20]:
            print("  " + difference)
        if len(differences) > 20:
            print(f"  ... {len(differences) - 20} further differences; use --snapshot to inspect full actual records.")
    print("\nExplicitly allowed surface differences:")
    for note in allowances or ["None observed."]:
        print("  " + note)
    print("\nNormalization rules:")
    for note in NORMALIZATIONS:
        print("  " + note)
    print("\nScope limits (not passing compatibility checks):")
    for note in LIMITATIONS:
        print("  " + note)
    print(
        f"\n{'FAIL' if failed else 'PASS'}: {len(CASE_NAMES) - len(failed)}/{len(CASE_NAMES)} paired cases; requests {loom['counts']['requests']}/{public['counts']['requests']}; checks {loom['counts']['checks']}/{public['counts']['checks']} (Loom/public)."
    )
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--loom-repo", type=Path, help="Loom checkout containing azure-ai-finetuningsessions")
    parser.add_argument("--snapshot", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--legacy-routes", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.snapshot is not None:
        if args.loom_repo is not None:
            parser.error("--snapshot and --loom-repo are mutually exclusive")
        try:
            with redirect_stdout(sys.stderr):
                report = _snapshot(args.snapshot, args.legacy_routes)
            print(_dump(report))
            return 0 if all(case["ok"] for case in report["cases"].values()) else 1
        except Exception as exc:
            print(_dump({"fatal": {"type": type(exc).__name__, "message": str(exc)}}))
            return 2
    if args.loom_repo is None or args.legacy_routes:
        parser.error("--loom-repo is required; --legacy-routes is for internal --snapshot mode only")
    try:
        public_package = _check_package(PACKAGE)
        loom_package = _check_package(args.loom_repo / "azure-ai-finetuningsessions")
        if (public_package / MODULE / "__init__.py").samefile(loom_package / MODULE / "__init__.py"):
            raise ValueError("Loom and public source roots must be different packages")
        print(f"Loom source:   {loom_package}\nPublic source: {public_package}")
        loom = _run_worker(loom_package, legacy_routes=False)
        public = _run_worker(public_package, legacy_routes=False)
        return _compare(loom, public)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"Verifier setup failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Isolated exhaustive public-surface and raw-operation parity probe."""

from __future__ import annotations

import argparse
import asyncio
import base64
from contextlib import redirect_stdout
from copy import deepcopy
from enum import Enum
import importlib
import importlib.util
import inspect
import json
import logging
from pathlib import Path
import platform
import subprocess
import sys
import types
import typing
from uuid import UUID

NAMESPACE = "azure.ai.finetuningsessions"
MODULE = Path("azure/ai/finetuningsessions")
RAW_RESULT = {"type": "sample", "operation_id": "op", "status": "succeeded", "sequences": []}
RAW_BEGIN = {
    "sessions.begin_create": "", "sessions.begin_unload": "/a/complete",
    "training.begin_forward_backward": "/a/forward_backward", "training.begin_optim_step": "/a/optim_step",
    "checkpoints.begin_save": "/a/checkpoint", "checkpoints.begin_save_sampler_weights": "/a/checkpoint_sample",
    "sampling.begin_sample": "/a/sample",
}
SERVICE_RAW_MODES = (
    "pending", "cls", "resume", "custom", "custom_continuation", "post202", "post503", "poll404", "poll503",
    "failed", "engine_dead", "retryable", "result_unavailable", "unknown_status", "missing_result",
    "wrong_request", "wrong_session", "nonobject", "missing_request_id", "empty_token",
)
SERVICE_SECURITY_MODES = (
    "remote_http", "remote_http_opt_in", "loopback_http", "loopback_http_opt_in", "cross_origin",
    "prepopulated_cross_origin", "prepopulated_other_path", "distinct_override", "equivalent_https_port",
    "downgrade", "redirect_cross_origin", "post408", "post429", "post500", "post503", "get_retry", "explicit_post_retry",
)
SERVICE_MODEL_MODES = (
    "rank_missing_mapping", "rank_none_mapping", "rank_missing_keyword", "rank_none_keyword",
    "config_missing_mapping", "config_none_mapping", "config_missing_keyword", "config_none_keyword",
    "nested_rank_missing", "nested_rank_none", "response_format_mapping", "response_format_keyword",
    "response_format_omitted", "sampling_alias",
)


def _service_case_names():
    return {
        *(f"service:{side}:{target}:{mode}" for side in ("sync", "async") for target in RAW_BEGIN for mode in SERVICE_RAW_MODES),
        *(f"security:{side}:{mode}" for side in ("sync", "async") for mode in SERVICE_SECURITY_MODES),
        *(f"model:{mode}" for mode in SERVICE_MODEL_MODES),
    }


def typename(value):
    if value is inspect.Signature.empty:
        return {"empty": True}
    if value is None or value is type(None):
        return "None"
    if isinstance(value, typing.ForwardRef):
        return typename(value.__forward_arg__)
    if isinstance(value, str):
        return value.strip("'\"").replace("_models.", "").replace(NAMESPACE + ".models.", "")
    origin, args = typing.get_origin(value), typing.get_args(value)
    if origin is not None:
        return {"origin": typename(origin), "args": [typename(v) for v in args]}
    if isinstance(value, Enum):
        return {"enum": type(value).__name__, "value": value.value}
    if hasattr(value, "__name__"):
        return value.__name__
    return str(value).replace("typing.", "")


def evaluate(value, owner, models):
    """Resolve names only; retain unions, requiredness and all nested types."""
    namespace = dict(vars(typing))
    namespace.update(vars(sys.modules[owner.__module__]))
    namespace.update(vars(models))
    namespace["_models"] = models
    try:
        unions = importlib.import_module(NAMESPACE + "._unions")
    except ModuleNotFoundError as exc:
        if exc.name != NAMESPACE + "._unions":
            raise
        unions = importlib.import_module(NAMESPACE + "._types")
    namespace["_types"] = unions
    namespace["_unions"] = unions
    namespace["TokenCredential"] = importlib.import_module("azure.core.credentials").TokenCredential
    namespace["AsyncTokenCredential"] = importlib.import_module("azure.core.credentials_async").AsyncTokenCredential
    if isinstance(value, str):
        value = typing.ForwardRef(value)
    return typing._eval_type(value, namespace, namespace, type_params=())


def signature(function, models):
    unwrapped = inspect.unwrap(function)
    sig = inspect.signature(function)
    def annotation(value):
        if value is inspect.Signature.empty:
            return typename(value)
        return typename(evaluate(value, unwrapped, models))
    return {
        "parameters": [
            {"name": p.name, "kind": p.kind.name, "type": annotation(p.annotation),
             "default": typename(p.default) if p.default is inspect.Signature.empty else p.default}
            for p in sig.parameters.values() if p.name not in ("self", "cls")
        ],
        "returns": annotation(sig.return_annotation),
        "async": inspect.iscoroutinefunction(unwrapped),
    }


def surface():
    sdk = importlib.import_module(NAMESPACE)
    models = importlib.import_module(NAMESPACE + ".models")
    base = importlib.import_module(NAMESPACE + "._utils.model_base")
    if hasattr(models, "SamplingOperationResult") and models.SamplingOperationResult is not models.SampleOperationResult:
        raise AssertionError("SamplingOperationResult must be an identical alias, not a subclass or replacement")
    report = {"version": sdk.__version__, "modules": {}, "models": {}, "clients": {}, "exceptions": {}}
    for suffix in ("", ".aio", ".models", ".operations", ".aio.operations"):
        module = importlib.import_module(NAMESPACE + suffix)
        report["modules"][suffix] = list(module.__all__)
    for name in models.__all__:
        cls = getattr(models, name)
        if issubclass(cls, Enum):
            report["models"][name] = {"enum": [(k, v.value) for k, v in cls.__members__.items()]}
            continue
        fields = {}
        owners = {}
        for parent in reversed(cls.__mro__):
            for field, annotation in parent.__dict__.get("__annotations__", {}).items():
                if not field.startswith("_"):
                    fields[field] = typename(evaluate(annotation, parent, models))
                    owners[field] = parent
        metadata = {}
        for field, owner in owners.items():
            descriptor = inspect.getattr_static(cls, field)
            metadata[field] = {
                "type": fields[field], "wire_name": descriptor._rest_name_input or field,
                "visibility": descriptor._visibility, "discriminator": descriptor._is_discriminator,
                "format": descriptor._format,
            }
        report["models"][name] = {
            "signature": signature(cls.__init__, models),
            "overloads": [signature(fn, models) for fn in typing.get_overloads(cls.__init__)],
            "fields": metadata,
            "properties": sorted(n for n in dir(cls) if not n.startswith("_") and isinstance(inspect.getattr_static(cls, n), property)),
        }
    for suffix in ("", ".aio", ".operations", ".aio.operations"):
        module = importlib.import_module(NAMESPACE + suffix)
        for name in module.__all__:
            cls = getattr(module, name)
            if not inspect.isclass(cls):
                continue
            if issubclass(cls, Exception):
                report["exceptions"][name] = {
                    "signature": signature(cls.__init__, models),
                    "bases": [c.__name__ for c in cls.__mro__],
                }
                continue
            methods = {}
            for method in sorted({"__init__"} | {n for n in dir(cls) if not n.startswith("_")}):
                function = getattr(cls, method)
                if callable(function):
                    methods[method] = {
                        "signature": signature(function, models),
                        "overloads": [signature(fn, models) for fn in typing.get_overloads(inspect.unwrap(function))],
                    }
            report["clients"][suffix + "." + name] = methods
    # Every public model gets mapping/keyword construction and serialization.
    def sample(annotation, depth=0):
        if depth > 8:
            return None
        origin, args = typing.get_origin(annotation), typing.get_args(annotation)
        if origin in (typing.Union, types.UnionType):
            return sample(next(a for a in args if a is not type(None)), depth + 1)
        if origin is typing.Literal:
            return args[0].value if isinstance(args[0], Enum) else args[0]
        if origin is list:
            return [sample(args[0], depth + 1)]
        if origin is tuple:
            return [sample(a, depth + 1) for a in args]
        if origin in (dict, typing.Mapping):
            return {"sample": sample(args[-1], depth + 1)}
        if annotation is typing.Any:
            return {"nested": [1, 1.5, None, False, "utf8-café"]}
        if annotation is str:
            return "example"
        if annotation is int:
            return 2
        if annotation is float:
            return 0.5
        if annotation is bool:
            return True
        if annotation is bytes:
            return b"\xff\xd8\xfftest"
        if inspect.isclass(annotation) and issubclass(annotation, Enum):
            return next(iter(annotation)).value
        if inspect.isclass(annotation) and issubclass(annotation, base.Model):
            return model_input(annotation, depth + 1)
        if getattr(annotation, "__name__", "") == "datetime":
            return "2026-09-22T00:00:00Z"
        raise TypeError(f"No fixture for {annotation}")
    def model_input(cls, depth=0):
        values = {}
        for parent in reversed(cls.__mro__):
            for field, annotation in parent.__dict__.get("__annotations__", {}).items():
                if field.startswith("_"):
                    continue
                actual = evaluate(annotation, parent, models)
                if cls.__name__ == "ApiError" and field == "details":
                    values[field] = []
                else:
                    values[field] = sample(actual, depth)
        if cls.__name__ == "ImageChunk":
            values.update(type="image", format="jpeg", data=b"\xff\xd8\xfftest")
        return values
    def record(value):
        return json.loads(json.dumps(value, cls=base.SdkJSONEncoder))
    serialization = {}
    for name in models.__all__:
        cls = getattr(models, name)
        if issubclass(cls, Enum):
            continue
        data = model_input(cls)
        observations = []
        for constructor in (lambda: cls(data), lambda: cls(**data)):
            try:
                obj = constructor()
                observations.append({
                    "class": type(obj).__name__, "all": record(obj),
                    "writable": record(obj.as_dict(exclude_readonly=True)),
                    "attributes": {field: record(getattr(obj, field)) for field in report["models"][name]["fields"]},
                })
            except Exception as exc:
                observations.append({"error": type(exc).__name__, "message": str(exc)})
        serialization[name] = observations
    report["serialization"] = serialization
    return report


async def raw_operations(harness, service_contracts=False):
    from io import BytesIO
    from azure.core.polling import NoPolling, AsyncNoPolling

    ctx = harness._Context(False)
    saved_responses = {}

    class ContinuationPolling(NoPolling):
        def get_continuation_token(self):
            saved_responses["offline-token"] = self._initial_response
            return "offline-token"

        @classmethod
        def from_continuation_token(cls, token, **kwargs):
            if token != "offline-token":
                raise AssertionError("Unexpected continuation token")
            return kwargs["client"], saved_responses[token], kwargs["deserialization_callback"]

    class AsyncContinuationPolling(ContinuationPolling, AsyncNoPolling):
        async def run(self):
            pass

    common = {"foundry_features": harness.PREVIEW, "api_version": "v1"}
    result = deepcopy(RAW_RESULT)
    calls = [
        ("sessions.create", [], {"body": {"type": "training", "base_model": "m"}}, "POST", "", {"type": "training", "base_model": "m"}, {"session_id": "session_a", "request_id": "op"}),
        ("sessions.list", [], {}, "GET", "", None, {"data": [], "cursor": {"offset": 0, "limit": 20, "total_count": 0}}),
        ("sessions.get", ["a /%"], {}, "GET", "/a%20%2F%25", None, {"session_id": "a", "status": "running", "type": "training", "model_data": {"base_model": "m"}}),
        ("sessions.heartbeat", ["a"], {}, "POST", "/a/heartbeat", None, {"session_id": "a"}),
        ("checkpoints.list", ["a"], {}, "GET", "/a/checkpoints", None, {"checkpoints": []}),
        ("checkpoints.get", ["a", "cp"], {}, "GET", "/a/checkpoints/cp", None, {"base_model": "m", "is_lora": True, "lora_rank": 4}),
        ("operations.get", ["a", "op /"], {}, "GET", "/a/request/op%20%2F", None, result),
        ("sessions.begin_create", [], {"body": {}}, "POST", "", {}, {"result": result}),
        ("sessions.begin_unload", ["a"], {}, "POST", "/a/complete", None, {"result": result}),
        ("training.begin_forward_backward", ["a"], {"body": {}}, "POST", "/a/forward_backward", {}, {"result": result}),
        ("training.begin_optim_step", ["a"], {"body": {}}, "POST", "/a/optim_step", {}, {"result": result}),
        ("checkpoints.begin_save", ["a"], {"body": {}}, "POST", "/a/checkpoint", {}, {"result": result}),
        ("checkpoints.begin_save_sampler_weights", ["a"], {"body": {}}, "POST", "/a/checkpoint_sample", {}, {"result": result}),
        ("sampling.begin_sample", ["a"], {"body": {}}, "POST", "/a/sample", {}, {"result": result}),
    ]
    outcomes = {}
    for asynchronous in (False, True):
        for target, args, params, verb, path, body, payload in calls:
            is_lro = ".begin_" in target
            modes = ("normal", "cls", "stream", "raw_stream", "bytes", "io", "custom_poll", "continuation", "default_poll")
            for mode in modes:
                if mode in ("bytes", "io") and "body" not in params:
                    continue
                if mode in ("custom_poll", "continuation", "default_poll") and not is_lro:
                    continue
                name = f"{'async' if asynchronous else 'sync'}:{target}:{mode}"
                case = harness._Case(name, ctx)
                client = ctx.client(case, asynchronous)
                options = dict(params)
                options.update(common)
                if is_lro:
                    options["polling"] = (
                        (AsyncContinuationPolling() if asynchronous else ContinuationPolling())
                        if mode in ("custom_poll", "continuation") else mode == "default_poll"
                    )
                if service_contracts and is_lro and mode == "default_poll":
                    options["polling_interval"] = 0
                    case.allow_zero_poll_sleep = True
                if mode == "cls":
                    options["cls"] = lambda response, value, headers: {"value": ctx.value(value), "headers": dict(headers), "status": response.http_response.status_code}
                if mode in ("stream", "raw_stream"):
                    options["stream"] = True
                    if mode == "raw_stream":
                        options["decompress"] = False
                if mode in ("bytes", "io"):
                    raw = json.dumps(body).encode()
                    options["body"] = raw if mode == "bytes" else BytesIO(raw)
                # Case's request observer also supports the IO request body.
                actual_payload = payload
                if service_contracts and is_lro and mode == "default_poll":
                    session_id = "session_a" if target == "sessions.begin_create" else "a"
                    actual_payload = {"session_id": session_id, "request_id": "op", "status": "pending"}
                case.expect(verb, path, actual_payload, body=body,
                            status=202 if asynchronous and is_lro and not service_contracts else 200)
                if service_contracts and is_lro and mode == "default_poll":
                    case.expect("GET", f"/{session_id}/request/op", actual_payload)
                    case.expect("GET", f"/{session_id}/request/op",
                                {**actual_payload, "status": "completed", "result": result})
                group, method = target.split(".")
                try:
                    value = getattr(getattr(client, group), method)(*args, **options)
                    if asynchronous:
                        value = await value
                    if is_lro:
                        if mode == "continuation":
                            token = value.continuation_token()
                            options["continuation_token"] = token
                            value = getattr(getattr(client, group), method)(*args, **options)
                            if asynchronous:
                                value = await value
                        poller = value
                        value = await value.result() if asynchronous else value.result()
                    elif mode in ("stream", "raw_stream") and target != "sessions.create":
                        chunks = [chunk async for chunk in value] if asynchronous else list(value)
                        value = {"stream": b"".join(chunks).decode()}
                    output = {"type": type(value).__name__, "value": ctx.value(value)}
                    if service_contracts and is_lro and mode == "default_poll":
                        output["poller"] = {"status": poller.status(), "done": poller.done()}
                        output["sleeps"] = case.poll_sleeps
                    outcomes[name] = case.finish(output)
                except Exception as exc:
                    # These are existing invalid/raw option combinations. Their
                    # exact error type/message is part of preview compatibility.
                    if is_lro and (mode in ("stream", "raw_stream") or (asynchronous and mode == "default_poll")):
                        if mode in ("stream", "raw_stream"):
                            case.replies.clear()  # Rejected before any HTTP send.
                        outcomes[name] = case.finish({"rejected": type(exc).__name__, "message": str(exc)})
                    else:
                        outcomes[name] = case.finish(error=exc)
                finally:
                    if asynchronous:
                        await client.close()
                    else:
                        client.close()
            for status in ((200,) if asynchronous and is_lro else ()) + ((202,) if not asynchronous and is_lro else ()) + (400, 401, 404, 409, 418):
                name = f"{'async' if asynchronous else 'sync'}:{target}:error{status}"
                case = harness._Case(name, ctx)
                client = ctx.client(case, asynchronous)
                case.expect(verb, path, {"error": {"code": "bad", "message": "fixture", "param": "x"}}, body=body, status=status)
                try:
                    value = getattr(getattr(client, target.split('.')[0]), target.split('.')[1])(*args, **params, **common, **({"polling": False} if is_lro else {}))
                    if asynchronous:
                        value = await value
                    if service_contracts and asynchronous and is_lro and status == 200:
                        # Keep the original error200 fixture/case ID. Explicit
                        # NoPolling now accepts HTTP 200 even without a result.
                        value = await value.result()
                        outcomes[name] = case.finish({"accepted": 200, "type": type(value).__name__, "value": ctx.value(value)})
                    else:
                        outcomes[name] = case.finish(error=AssertionError("Expected the same HTTP error as the frozen preview"))
                except Exception as exc:
                    error = getattr(exc, "error", None)
                    outcomes[name] = case.finish({"type": type(exc).__name__, "message": str(exc), "error": ctx.value(error) if isinstance(error, dict) else str(error)})
                finally:
                    if asynchronous:
                        await client.close()
                    else:
                        client.close()
    return outcomes


async def service_operations(harness):
    """Independent fixed service fixtures; never import tests or learn outputs.

    These supplement, not replace, every original raw fixture. Real clients,
    pipelines, pollers, serializers and transports execute under the same guard.
    """
    from azure.core.credentials import AzureKeyCredential
    from azure.core.polling import NoPolling, AsyncNoPolling

    ctx = harness._Context(False)
    outcomes = {}
    common = {"foundry_features": harness.PREVIEW, "api_version": "v1", "polling_interval": 0,
              "headers": {"x-contract-probe": "preserved"}, "params": {"api-version": "v1", "custom": "value"},
              "connection_timeout": 2, "read_timeout": 3, "retry_total": 7}
    query = (("custom", "value"),)
    bodies = {
        "sessions.begin_create": {"type": "training", "base_model": harness.BASE_MODEL, "lora_config": harness.LORA},
        "sessions.begin_unload": None,
        "training.begin_forward_backward": {"forward_backward_input": {"data": harness.BATCH, "loss_fn": "cross_entropy"}},
        "training.begin_optim_step": {"adam_params": harness.ADAM},
        "checkpoints.begin_save": {"path": "contract", "step_number": 1, "metrics": {"value": 1.0}},
        "checkpoints.begin_save_sampler_weights": {"path": "contract", "seq_id": 0},
        "sampling.begin_sample": {"prompt": {"chunks": [{"tokens": [1, 2]}]},
                                  "sampling_params": {**harness.SAMPLING, "response_format": {"type": "json_object"}},
                                  "num_samples": 1},
    }
    results = {
        "sessions.begin_create": ("OperationResult", {"type": "create"}),
        "sessions.begin_unload": ("OperationResult", {"type": "unload"}),
        "training.begin_forward_backward": ("ForwardBackwardOperationResult", {"type": "forward_backward", **harness.BACKWARD, "total_loss": 1.25}),
        "training.begin_optim_step": ("OptimStepOperationResult", {"type": "optim_step", **harness.OPTIMIZER, "grad_norm": 0.75, "step_count": 3}),
        "checkpoints.begin_save": ("SaveCheckpointOperationResult", {"type": "save_checkpoint", "checkpoint_id": "contract", "path": "loom://a/weights/contract"}),
        "checkpoints.begin_save_sampler_weights": ("SaveSamplerWeightsOperationResult", {"type": "save_sampler_weights", "checkpoint_id": "contract", "sampling_session_id": "sampler"}),
        "sampling.begin_sample": ("SampleOperationResult", {"type": "sample", **harness.SAMPLES}),
    }
    builders = {
        "sessions.begin_create": "build_sessions_create_request", "sessions.begin_unload": "build_sessions_unload_request",
        "training.begin_forward_backward": "build_training_forward_backward_request", "training.begin_optim_step": "build_training_optim_step_request",
        "checkpoints.begin_save": "build_checkpoints_save_request", "checkpoints.begin_save_sampler_weights": "build_checkpoints_save_sampler_weights_request",
        "sampling.begin_sample": "_build_sampling_request",
    }
    bad_http = {"error": {"code": "bad", "message": "fixture", "param": "x"}}
    for asynchronous in (False, True):
        for target, path in RAW_BEGIN.items():
            for mode in SERVICE_RAW_MODES:
                name = f"service:{'async' if asynchronous else 'sync'}:{target}:{mode}"
                case = harness._Case(name, ctx)
                case.allow_zero_poll_sleep = True
                transport = (ctx.async_transport if asynchronous else ctx.sync_transport)(case)
                client_type = (ctx.aio if asynchronous else ctx.sdk).FineTuningSessionClient
                client = client_type(harness.ENDPOINT, AzureKeyCredential(harness.KEY), transport=transport,
                                     retry_total=5, retry_backoff_factor=0, retry_on_methods=["GET", "POST"], logging_enable=False)
                session_id = "session_a" if target == "sessions.begin_create" else "a"
                args = [] if target == "sessions.begin_create" else ["a"]
                body = bodies[target]
                model, data = results[target]
                result = {**deepcopy(data), "operation_id": "op", "status": "succeeded"}
                accepted = {"request_id": "op", "session_id": session_id, "status": "pending"}
                completed = {**accepted, "status": "completed", "result": result}
                options = deepcopy(common)
                if body is not None:
                    options["body"] = deepcopy(body)
                expected_error = None
                expected_fields = {}
                poll_count = 0
                initial_status = 200
                initial = accepted
                terminal = completed
                poll_status = 200
                if mode == "cls":
                    options["cls"] = lambda response, value, headers: {
                        "value": ctx.value(value), "headers": dict(headers), "status": response.http_response.status_code}
                if mode in ("custom", "custom_continuation"):
                    saved = {}

                    class Custom(NoPolling):
                        def initialize(self, client, response, callback):
                            case.equal(response.http_response.status_code, 200, "Custom polling sees the real HTTP 200")
                            case.equal(response.http_response.json(), {**accepted, "result": result}, "Unchanged custom initial response")
                            super().initialize(client, response, callback)

                        def get_continuation_token(self):
                            saved["response"] = self._initial_response
                            return "fixed-custom-token"

                        @classmethod
                        def from_continuation_token(cls, token, **kwargs):
                            case.equal(token, "fixed-custom-token", "Custom continuation token passthrough")
                            return kwargs["client"], saved["response"], kwargs["deserialization_callback"]

                    class AsyncCustom(Custom, AsyncNoPolling):
                        async def run(self):
                            pass

                    options["polling"] = AsyncCustom() if asynchronous else Custom()
                    initial = {**accepted, "result": result}
                elif mode == "post202":
                    initial_status, initial = 202, bad_http
                    expected_error = ("HttpResponseError", "(bad) fixture\nCode: bad\nMessage: fixture", 202)
                elif mode == "post503":
                    initial_status, initial = 503, {"reason": "engine_busy", "message": "fixture"}
                    expected_error = ("NoCapacityError", "fixture", 503)
                    expected_fields = {"reason": "engine_busy", "retry_after_sec": None}
                elif mode == "missing_request_id":
                    initial = {"session_id": session_id, "status": "pending"}
                    expected_error = ("HttpResponseError", "Invalid request acceptance: request_id must be a nonempty string without control characters or dot segments", 200)
                elif mode == "empty_token":
                    options["continuation_token"] = ""
                    expected_error = ("ValueError", "continuation_token must not be empty", None)
                else:
                    poll_count = 2 if mode == "pending" else 1
                    if mode == "poll404":
                        poll_status, terminal = 404, bad_http
                        expected_error = ("ResourceNotFoundError", "(bad) fixture\nCode: bad\nMessage: fixture", 404)
                    elif mode == "poll503":
                        poll_status, terminal = 503, {"reason": "engine_busy", "message": "fixture"}
                        expected_error = ("NoCapacityError", "fixture", 503)
                        expected_fields = {"reason": "engine_busy", "retry_after_sec": None}
                    elif mode in ("failed", "engine_dead", "retryable", "result_unavailable"):
                        terminal = {**accepted, "status": "failed", "error": "fixture"}
                        expected_error = ("HttpResponseError", "Request op failed: fixture", 200)
                        if mode == "engine_dead":
                            terminal.update(error_code="engine_dead", debug_ref="fixed-ref")
                            expected_error = ("TrainingEngineError", "fixture", 200)
                            expected_fields = {"session_id": session_id, "error_code": "engine_dead", "debug_ref": "fixed-ref"}
                        elif mode == "retryable":
                            terminal.update(error_code="transient", should_retry=True, retry_after_sec=2)
                            expected_error = ("RequestRetryableError", "fixture", 200)
                            expected_fields = {"error_code": "transient", "retry_after_sec": 2.0}
                        elif mode == "result_unavailable":
                            terminal.update(error_code="operation_completed_result_unavailable", should_retry=True)
                            expected_error = ("OperationResultUnavailableError", "fixture", 200)
                            expected_fields = {"error_code": "operation_completed_result_unavailable", "operation_completed": True}
                    elif mode == "unknown_status":
                        terminal = {**accepted, "status": "unexpected"}
                        expected_error = ("HttpResponseError", "Unexpected request envelope status 'unexpected'", 200)
                    elif mode == "missing_result":
                        terminal = {**accepted, "status": "completed"}
                        expected_error = ("HttpResponseError", "Invalid completed request envelope: result must be an object", 200)
                    elif mode in ("wrong_request", "wrong_session"):
                        field = "request_id" if mode == "wrong_request" else "session_id"
                        terminal = {**completed, field: "other"}
                        expected_error = ("HttpResponseError", f"Polling response {field} does not match the request", 200)
                    elif mode == "nonobject":
                        terminal = []
                        expected_error = ("HttpResponseError", "Invalid request polling response: expected a JSON object", 200)
                if mode != "empty_token":
                    case.expect("POST", path, initial, body=body, status=initial_status, query=query)
                if poll_count == 2:
                    case.expect("GET", f"/{session_id}/request/op", accepted, query=query)
                if poll_count:
                    case.expect("GET", f"/{session_id}/request/op", terminal, status=poll_status, query=query)
                if mode == "resume":
                    case.expect("GET", f"/{session_id}/request/op", completed, query=query)
                if expected_error is not None:
                    error_type, message, status = expected_error
                    # Azure Core parses top-level message as OData, otherwise
                    # HttpResponseError.__str__ appends the buffered body (2048
                    # character limit). Derive it from fixed fixtures only.
                    if mode in ("post503", "poll503"):
                        message = "(None) fixture\nCode: None\nMessage: fixture"
                    elif status == 200:
                        envelope = initial if mode == "missing_request_id" else terminal
                        message = (message + "\nContent: " + harness._dump(envelope))[:2048]
                    expected_error = (error_type, message, status)
                poller = None
                try:
                    group, method = target.split(".")
                    function = getattr(getattr(client, group), method)
                    try:
                        pending_poller = function(*args, **options)
                        poller = await pending_poller if asynchronous else pending_poller
                        value = await poller.result() if asynchronous else poller.result()
                    except Exception as exc:
                        if expected_error is None:
                            raise
                        observed = (type(exc).__name__, str(exc), getattr(exc, "status_code", None))
                        case.equal(observed, expected_error, "Exact service error class, message and HTTP status")
                        for field, expected in expected_fields.items():
                            case.equal(getattr(exc, field), expected, f"Service error {field}")
                        if poller is not None:
                            # Core's async wait sets _done only on success;
                            # sync done means its background thread has exited.
                            case.equal((poller.status(), poller.done()), ("Failed", not asynchronous), "Terminal failure state")
                        output = {"error": list(observed), "fields": expected_fields}
                    else:
                        case.check(expected_error is None, "Expected service failure must not resolve successfully")
                        expected_value = {"value": result, "headers": {"Operation-Location": None}, "status": 200} if mode == "cls" else result
                        case.equal(ctx.value(value), expected_value, "Exact typed/cls result, including all nested fields")
                        case.equal(type(value).__name__, "dict" if mode == "cls" else model, "Exact result model class")
                        case.equal((poller.status(), poller.done()), ("succeeded" if mode.startswith("custom") else "Succeeded", True), "Completed poller state")
                        if mode in ("resume", "custom_continuation"):
                            token = poller.continuation_token()
                            if mode == "resume":
                                case.equal(json.loads(base64.urlsafe_b64decode(token)), {
                                    "kind": NAMESPACE + ".request", "version": 1, "endpoint": harness.ENDPOINT,
                                    "operation": builders[target], "api_version": "v1", "session_id": session_id, "request_id": "op",
                                }, "Continuation locator contains exactly the bound fields, no body/credentials")
                            resumed = function(*args, **{**options, "continuation_token": token})
                            if asynchronous:
                                resumed = await resumed
                            value = await resumed.result() if asynchronous else resumed.result()
                            case.equal(ctx.value(value), result, "Continuation result without a second POST")
                        output = {"type": type(value).__name__, "value": ctx.value(value), "status": poller.status(), "done": poller.done()}
                    case.equal(sum(r["method"] == "POST" for r in case.requests), 0 if mode == "empty_token" else 1, "Never replay POST")
                    case.equal(sum(r["method"] == "GET" for r in case.requests), poll_count + (mode == "resume"), "Exactly the scripted GETs")
                    case.equal(case.poll_sleeps, [0.0] if mode == "pending" else [], "Only the explicit zero-delay pending wait")
                    for request in case.requests:
                        case.equal(request["headers"].get("x-contract-probe"), "preserved", "Custom header retained on POST and GET")
                        case.equal(request["options"], {"stream": True, "connection_timeout": 2, "read_timeout": 3}, "Exact transport options after policy consumption")
                    outcomes[name] = case.finish(output)
                except Exception as exc:
                    outcomes[name] = case.finish(error=exc)
                finally:
                    if asynchronous:
                        await client.close()
                    else:
                        client.close()
    return outcomes


async def security_operations(harness):
    """Default-pipeline key/header boundaries and retry policy, without private SDK helpers."""
    from azure.core.credentials import AzureKeyCredential
    from azure.core.pipeline.policies import RetryPolicy, AsyncRetryPolicy
    from azure.core.rest import HttpRequest

    ctx = harness._Context(False)
    context_headers = {
        "apim-subscription-id": "offline-subscription",
        "azure-resource-id": "/subscriptions/offline/resourceGroups/offline/providers/Microsoft.CognitiveServices/accounts/offline",
        "azure-resource-tenant-id": "offline-tenant", "azure-resource-location": "offline-region",
        "x-workspace-resource-id": "/subscriptions/offline/resourceGroups/offline/providers/Microsoft.MachineLearningServices/workspaces/offline",
    }

    class SecurityCase(harness._Case):
        def receive(self, request, options):
            headers = {k.lower(): v for k, v in request.headers.items()}
            UUID(headers.pop("x-ms-client-request-id"))
            self.equal(headers.get("user-agent"), ctx.user_agent, "Exact user agent")
            headers["user-agent"] = ctx.moniker
            body = None if request.content is None else json.loads(request.content)
            record = {"method": request.method, "url": request.url, "headers": headers, "body": body, "options": harness._plain(options)}
            self.requests.append(record)
            self.check(bool(self.replies), "No unexpected send/retry/redirect")
            reply = self.replies.popleft()
            self.equal(request.method, reply.method, "Exact security probe method")
            self.equal(request.url, reply.url, "Exact security probe URL")
            self.equal(body, reply.body, "Exact security probe body")
            self.equal(headers, self.expected_headers.pop(0), "All request headers, including credentials and identity scope")
            return reply

    outcomes = {}
    for asynchronous in (False, True):
        for mode in SERVICE_SECURITY_MODES:
            name = f"security:{'async' if asynchronous else 'sync'}:{mode}"
            case = SecurityCase(name, ctx)
            case.expected_headers = []
            endpoint = harness.ENDPOINT
            if mode.startswith("remote_http"):
                endpoint = endpoint.replace("https:", "http:")
            elif mode.startswith("loopback_http"):
                endpoint = "http://localhost/api/projects/compatibility"
            own_url = endpoint + harness.ROUTE + "/a/heartbeat?api-version=v1"
            foreign_url = "https://other.invalid/api/projects/compatibility" + harness.ROUTE + "/a/heartbeat?api-version=v1"
            url = own_url
            key, direct = True, True
            if mode in ("cross_origin", "prepopulated_cross_origin", "distinct_override"):
                url, key, direct = foreign_url, False, False
            elif mode == "prepopulated_other_path":
                url, direct = endpoint + "/unrelated", False
            elif mode == "equivalent_https_port":
                url = own_url.replace("offline.invalid", "offline.invalid:443")
            elif mode == "downgrade":
                url = own_url.replace("https:", "http:")
            method = "GET" if mode == "get_retry" else "POST"
            body = None if method == "GET" else {}
            supplied = {"accept": "application/json", "foundry-features": harness.PREVIEW}
            if method == "POST":
                supplied["content-type"] = "application/json"
            if mode.startswith("prepopulated"):
                supplied.update(context_headers)
            elif mode == "distinct_override":
                supplied.update({k: "caller-owned" for k in context_headers})
            base_headers = {"user-agent": ctx.moniker, "accept": "application/json", "foundry-features": harness.PREVIEW}
            if method == "POST":
                base_headers.update({"content-type": "application/json", "content-length": "2"})
            expected_headers = {**base_headers, **({"api-key": harness.KEY} if key else {}),
                                **(context_headers if direct else {})}
            if mode == "distinct_override":
                expected_headers.update({k: "caller-owned" for k in context_headers})
            blocked = mode in ("remote_http", "remote_http_opt_in", "loopback_http", "downgrade")
            status = int(mode[4:]) if mode.startswith("post") else 200
            if not blocked:
                if mode in ("get_retry", "explicit_post_retry"):
                    case.replies.append(harness._Reply(method, url, body, {}, 503))
                    case.expected_headers.append(expected_headers)
                case.replies.append(harness._Reply(method, url, body, {}, 307 if mode == "redirect_cross_origin" else status,
                                                   {"Location": foreign_url} if mode == "redirect_cross_origin" else None))
                case.expected_headers.append(expected_headers)
                if mode == "redirect_cross_origin":
                    case.replies.append(harness._Reply(method, foreign_url, body, {}))
                    case.expected_headers.append(base_headers)
            transport = (ctx.async_transport if asynchronous else ctx.sync_transport)(case)
            options = {"transport": transport, "retry_total": 3, "retry_backoff_factor": 0,
                       "retry_on_methods": ["GET", "POST"], "allow_insecure_http": mode.endswith("opt_in"),
                       "logging_enable": False}
            if mode == "explicit_post_retry":
                policy = AsyncRetryPolicy if asynchronous else RetryPolicy
                options["retry_policy"] = policy(retry_total=1, retry_backoff_factor=0, retry_on_methods=["GET", "POST"])
            client_type = (ctx.aio if asynchronous else ctx.sdk).FineTuningSessionClient
            client = None
            try:
                client = client_type(endpoint, AzureKeyCredential(harness.KEY), **options)
                request = HttpRequest(method, url, headers=supplied, **({"content": b"{}"} if body is not None else {}))
                try:
                    response = client.send_request(request, retry_total=3, retry_on_methods=["GET", "POST"])
                    if asynchronous:
                        response = await response
                except ValueError as exc:
                    case.check(blocked, "Only the fixed TLS failures are allowed")
                    case.equal(str(exc), "API key authentication requires HTTPS. allow_insecure_http=True only permits the configured loopback HTTP origin (localhost, 127.0.0.1, [::1]).", "Exact insecure-key error")
                    output = {"rejected": "ValueError", "message": str(exc)}
                else:
                    case.check(not blocked, "Unsafe key transport must fail before send")
                    case.equal(response.status_code, status, "Final status (default POST retry stays disabled)")
                    output = {"status": response.status_code}
                expected_count = 0 if blocked else 2 if mode in ("get_retry", "explicit_post_retry", "redirect_cross_origin") else 1
                case.equal(len(case.requests), expected_count, "Exact retry/redirect/send count")
                case.equal(case.expected_headers, [], "All independent header expectations consumed")
                case.equal(case.poll_sleeps, [], "No retry/backoff sleep")
                outcomes[name] = case.finish(output)
            except Exception as exc:
                outcomes[name] = case.finish(error=exc)
            finally:
                if client is not None:
                    if asynchronous:
                        await client.close()
                    else:
                        client.close()
    return outcomes


def model_contracts(harness):
    ctx = harness._Context(False)
    m = ctx.models
    outcomes = {}
    for mode in SERVICE_MODEL_MODES:
        case = harness._Case("model:" + mode, ctx)
        try:
            if mode.startswith(("rank_", "config_", "nested_")):
                rank = mode.startswith("rank_") or mode.startswith("nested_")
                if mode.startswith("rank_"):
                    data = {"rank": None} if "none" in mode else {}
                    constructor = m.LoRAConfig
                else:
                    data = {"type": "training", "base_model": harness.BASE_MODEL}
                    if mode.startswith("nested_"):
                        data["lora_config"] = {"rank": None} if "none" in mode else {}
                    elif "none" in mode:
                        data["lora_config"] = None
                    constructor = m.CreateSessionRequest
                try:
                    constructor(data) if mode.endswith("mapping") else constructor(**data)
                except ValueError as exc:
                    expected = "lora_config.rank is required; pass LoRAConfig(rank=<integer>)" if rank else "lora_config is required; pass LoRAConfig(rank=<integer>)"
                    case.equal(str(exc), expected, "Required-field rejection without a fabricated default")
                    output = {"rejected": "ValueError", "message": str(exc)}
                else:
                    raise AssertionError("Missing/null required LoRA field was accepted")
            elif mode == "sampling_alias":
                case.check(m.SamplingOperationResult is m.SampleOperationResult, "Exact class identity, not a copy/subclass")
                wire = {**harness.SAMPLES, "type": "sample", "operation_id": "op", "status": "succeeded"}
                for constructor in (m.SampleOperationResult, m.SamplingOperationResult):
                    case.equal(ctx.value(constructor(wire)), wire, "Alias preserves full nullable sampling serialization")
                output = {"identical": True, "value": wire}
            else:
                data = deepcopy(harness.SAMPLING)
                if mode != "response_format_omitted":
                    data["response_format"] = {"type": "json_schema", "json_schema": {"name": "fixed", "schema": {"type": "object"}}}
                value = m.SamplingParams(data) if mode.endswith("mapping") else m.SamplingParams(**data)
                case.equal(ctx.value(value), data, "Exact response_format serialization/omission")
                case.equal(ctx.value(value.response_format), data.get("response_format"), "Optional response_format attribute")
                output = {"value": ctx.value(value)}
            outcomes[case.name] = case.finish(output)
        except Exception as exc:
            outcomes[case.name] = case.finish(error=exc)
    return outcomes


def _validate_service_report(report):
    cases = report.get("service", {})
    if set(cases) != _service_case_names():
        raise ValueError("Candidate did not execute exactly the fixed service-contract case inventory")
    if any(not c.get("ok") or c.get("remaining_responses") != 0 or c.get("checks", 0) < 1 for c in cases.values()):
        raise ValueError("Independent service-contract cases failed")


def worker(package, harness_path, service_contracts=False):
    # Do not add the reference source root to sys.path: its legacy azure parent
    # initializers would override the installed wheel's PEP 420 namespace.
    spec = importlib.util.spec_from_file_location("_loom_offline_harness", harness_path)
    harness = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = harness
    spec.loader.exec_module(harness)
    harness._offline_environment()
    loop = asyncio.new_event_loop()
    # Extend only fixture input decoding for binary/file-like request bodies.
    original_receive = harness._Case.receive
    def receive(case, request, options):
        content = request.content
        if hasattr(content, "read"):
            request._data = content.read()
        return original_receive(case, request, options)
    harness._Case.receive = receive
    # Windows platform discovery can invoke a subprocess/open NUL. Cache it
    # before the read-only guard, never relax that guard for SDK execution.
    platform.platform()
    harness._install_offline_guard()
    sys.path.insert(0, str(package))
    logging.getLogger("azure").setLevel(logging.CRITICAL)
    try:
        origin = Path(importlib.import_module(NAMESPACE).__file__).resolve()
        if origin != (package / MODULE / "__init__.py").resolve():
            raise RuntimeError(f"Wrong SDK imported: {origin}")
        public = surface()
        raw = loop.run_until_complete(raw_operations(harness, service_contracts))
        report = {"surface": public, "raw": raw}
        if service_contracts:
            report["service"] = {
                **loop.run_until_complete(service_operations(harness)),
                **loop.run_until_complete(security_operations(harness)),
                **model_contracts(harness),
            }
        return report
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


def _apply_training_type_contract(report):
    """Add only the reviewed enum and four annotation sites to a baseline report.

    Expected values are fixed here, never copied from candidate output. Exports,
    enum members, constructor defaults, wire metadata, and all other types still
    undergo the original exhaustive comparison.
    """
    result = deepcopy(report)
    surface = result["surface"]
    exports = surface["modules"][".models"]
    if "TrainingType" in exports or "TrainingType" in surface["models"]:
        raise RuntimeError("The reference already exposes TrainingType")
    if exports.count("SessionType") != 1:
        raise RuntimeError("The reference SessionType export changed")
    exports.insert(exports.index("SessionType") + 1, "TrainingType")
    surface["models"]["TrainingType"] = {
        "enum": [["GLOBAL_STANDARD", "GlobalStandard"], ["DATAZONE_STANDARD", "DatazoneStandard"],
                 ["DEVELOPER_TIER", "DeveloperTier"]]
    }
    original = {"origin": "Union", "args": ["str", "None"]}
    expected = {"origin": "Union", "args": ["str", "TrainingType", "None"]}
    model = surface["models"]["CreateSessionRequest"]
    field = model["fields"]["training_type"]
    if field["type"] != original or field["wire_name"] != "training_type":
        raise RuntimeError("The reference training_type field changed")
    field["type"] = deepcopy(expected)

    def widen(signature):
        fields = [p for p in signature["parameters"] if p["name"] == "training_type"]
        if len(fields) != 1 or fields[0] != {
            "name": "training_type", "kind": "KEYWORD_ONLY", "type": original, "default": None,
        }:
            raise RuntimeError("The reference training_type parameter changed")
        fields[0]["type"] = deepcopy(expected)

    widen(model["overloads"][0])
    widen(surface["clients"][".FineTuningSession"]["create"]["signature"])
    widen(surface["clients"][".aio.FineTuningSessionClient"]["create_session"]["signature"])
    return result


def _apply_service_contracts(report, harness):
    """Project fixed service changes from an exact original-fixture oracle.

    Never consume candidate output here. The source is still independently
    hash-verified against Loom; these observation guards reject baseline drift,
    including extra fields, defaults, methods and changed serializer probes.
    """
    harness._require_baseline(report["surface"],
        "d46c1d9a22c83953cc81a0501a00541293fd2b734644fd8eecaeafa6f8ab6c4e", "complete surface after TrainingType")
    harness._require_baseline(report["raw"],
        "cbf4dbe14d07295a5086b99f29236030d1b1efd59f3fa807718c0e4515abdec9", "336 original raw cases")
    result = deepcopy(report)
    api = result["surface"]

    def require_parameter(sig, name, original, expected):
        parameters = [p for p in sig["parameters"] if p["name"] == name]
        old = {"name": name, "kind": "KEYWORD_ONLY", "type": original, "default": None}
        if parameters != [old]:
            raise ValueError(f"Unexpected baseline parameter: {name}")
        parameters[0].update(type=expected, default={"empty": True})

    for name, field, value in (("LoRAConfig", "rank", "int"), ("CreateSessionRequest", "lora_config", "LoRAConfig")):
        model = api["models"][name]
        model["fields"][field]["type"] = value
        require_parameter(model["overloads"][0], field, {"origin": "Union", "args": [value, "None"]}, value)
    for client, method in ((".FineTuningSession", "create"), (".FineTuningSession", "create_from_checkpoint"),
                           (".aio.FineTuningSessionClient", "create_session"),
                           (".aio.FineTuningSessionClient", "create_session_from_checkpoint")):
        require_parameter(api["clients"][client][method]["signature"], "lora_config",
                          {"origin": "Union", "args": ["LoRAConfig", "None"]}, "LoRAConfig")
    annotation = {"origin": "Union", "args": [{"origin": "dict", "args": ["str", "Any"]}, "None"]}
    sampling = api["models"]["SamplingParams"]
    sampling["fields"]["response_format"] = {
        "type": deepcopy(annotation), "wire_name": "response_format", "visibility": ["read", "create", "update", "delete", "query"],
        "discriminator": False, "format": None,
    }
    sampling["overloads"][0]["parameters"].append(
        {"name": "response_format", "kind": "KEYWORD_ONLY", "type": deepcopy(annotation), "default": None})
    # Fixed value produced by the existing model probe for Dict[str, Any].
    response_format = {"sample": {"nested": [1, 1.5, None, False, "utf8-caf\u00e9"]}}
    for name in ("SamplingParams", "SampleRequest"):
        for observation in api["serialization"][name]:
            for kind in ("all", "writable", "attributes"):
                target = observation[kind] if name == "SamplingParams" else observation[kind]["sampling_params"]
                target["response_format"] = deepcopy(response_format)
    api["modules"][".models"].append("SamplingOperationResult")
    api["models"]["SamplingOperationResult"] = deepcopy(api["models"]["SampleOperationResult"])
    api["serialization"]["SamplingOperationResult"] = deepcopy(api["serialization"]["SampleOperationResult"])
    for asynchronous in (False, True):
        for target in RAW_BEGIN:
            prefix = f"{'async' if asynchronous else 'sync'}:{target}"
            case = result["raw"][prefix + ":default_poll"]
            request = case["requests"][0]
            # Azure Core RedirectPolicy.configure_redirects consumes
            # permit_redirects before transport, as RetryPolicy does retry_total.
            get = deepcopy(request)
            get.update(method="GET", body=None)
            session_id = "session_a" if target == "sessions.begin_create" else "a"
            get["url"] = harness.ENDPOINT + harness.ROUTE + f"/{session_id}/request/op?api-version=v1"
            get["headers"].pop("content-type", None)
            get["headers"].pop("content-length", None)
            case["requests"].extend([deepcopy(get), deepcopy(get)])
            case["checks"] += 26  # Existing observer: thirteen independent checks per GET.
            case["output"] = {"type": "SampleOperationResult", "value": deepcopy(RAW_RESULT),
                              "poller": {"status": "Succeeded", "done": True}, "sleeps": [0.0]}
            if asynchronous:
                result["raw"][prefix + ":cls"]["output"]["value"]["status"] = 200
                result["raw"][prefix + ":error200"]["output"] = {"accepted": 200, "type": "OperationResult", "value": {}}
    return result


def _apply_review_contracts(report, harness, contracts):
    result = deepcopy(report)
    if "training-type-enum" in contracts:
        result = _apply_training_type_contract(result)
    if "raw-request-id-polling" in contracts:
        result = _apply_service_contracts(result, harness)
    result["raw"] = harness._apply_review_header_contract(result["raw"], raw=True)
    for client, original in ((".FineTuningSessionClient", "TokenCredential"),
                             (".aio.FineTuningSessionClient", "AsyncTokenCredential")):
        parameter = result["surface"]["clients"][client]["__init__"]["signature"]["parameters"][1]
        if parameter != {"name": "credential", "kind": "POSITIONAL_OR_KEYWORD", "type": original, "default": {"empty": True}}:
            raise ValueError("The immutable baseline credential parameter changed")
        parameter["type"] = {"origin": "Union", "args": [original, "AzureKeyCredential"]}
    model = result["surface"]["models"]["ModelInput"]
    if model["fields"]["chunks"]["type"] != {"origin": "list", "args": ["ModelInputChunk"]} or model["overloads"] != []:
        raise ValueError("The immutable baseline ModelInput annotation/overloads changed")
    chunks = {"origin": "list", "args": [{"origin": "Union", "args": ["ModelInputChunk", "ImageChunk"]}]}
    model["fields"]["chunks"]["type"] = chunks
    model["overloads"] = [
        {"parameters": [{"name": "chunks", "kind": "KEYWORD_ONLY", "type": chunks, "default": {"empty": True}}],
         "returns": "None", "async": False},
        {"parameters": [{"name": "mapping", "kind": "POSITIONAL_OR_KEYWORD", "type": {"origin": "Mapping", "args": ["str", "Any"]}, "default": {"empty": True}}],
         "returns": "None", "async": False},
    ]
    return result


def main():
    platform.platform()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--review-deltas", type=Path, help="Explicit, versioned post-baseline bug-fix contracts")
    parser.add_argument("--training-type-enum", action="store_true", help="Apply only the reviewed additive TrainingType contract")
    parser.add_argument("--service-contracts", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--artifacts", type=Path, help="Directory for unmodified reference and candidate worker JSON")
    args = parser.parse_args()
    if args.worker:
        with redirect_stdout(sys.stderr):
            report = worker(args.worker.resolve(), args.harness.resolve(), args.service_contracts)
        print(json.dumps(report, sort_keys=True, ensure_ascii=True))
        return 0
    if args.reference is None or args.candidate is None:
        parser.error("--reference and --candidate are required unless --worker is used")
    sys.path.insert(0, str(args.harness.parent))
    import verify_compatibility as harness
    contracts = harness._review_contracts(json.loads(args.review_deltas.read_text(encoding="utf-8"))) if args.review_deltas else []
    reports = []
    for side, package in (("reference", args.reference), ("candidate", args.candidate)):
        command = [sys.executable, "-I", "-B", "-X", "utf8", str(Path(__file__).resolve()),
                   "--worker", str(package.resolve()), "--harness", str(args.harness.resolve())]
        if side == "candidate" and "raw-request-id-polling" in contracts:
            command.append("--service-contracts")
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf8", timeout=120)
        if result.returncode:
            raise RuntimeError(result.stderr + result.stdout)
        report = json.loads(result.stdout)
        reports.append(report)
        if args.artifacts:
            args.artifacts.mkdir(parents=True, exist_ok=True)
            (args.artifacts / f"{side}-surface.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if contracts:
        reports[0] = _apply_review_contracts(reports[0], harness, contracts)
        print("Applied only fixed reviewed contracts; original reference fixtures and all 336 raw case IDs retained.")
    if args.training_type_enum and "training-type-enum" not in contracts:
        reports[0] = _apply_training_type_contract(reports[0])
        print("Applied only the exact TrainingType export, members, and four annotation sites; all other fields remain exact.")
    candidate = deepcopy(reports[1])
    service_failures = []
    if "raw-request-id-polling" in contracts:
        try:
            _validate_service_report(candidate)
        except ValueError as exc:
            service_failures.append(str(exc))
        cases = candidate.pop("service", {})
        print(f"Independent service cases: {len(cases)}; failures: {sum(not c.get('ok') for c in cases.values())}")
        for name, case in [(n, c) for n, c in cases.items() if not c.get("ok")][:8]:
            print(name, case.get("error"))
    differences = harness._differences(reports[0], candidate) + service_failures
    if args.artifacts:
        (args.artifacts / "expected-surface.json").write_text(json.dumps(reports[0], indent=2), encoding="utf-8")
        (args.artifacts / "surface-differences.json").write_text(json.dumps(differences, indent=2), encoding="utf-8")
    print(f"Public models/enums: {len(reports[0]['surface']['models'])}; raw cases: {len(reports[0]['raw'])}")
    for delta in differences[:60]:
        print(delta)
    failed = {side: [name for name, case in report['raw'].items() if not case['ok']]
              for side, report in zip(('reference', 'candidate'), reports)}
    print('Case failures:', {side: len(names) for side, names in failed.items()})
    for name in failed['reference'][:6]:
        print(name, reports[0]['raw'][name].get('error'))
    print(f"{'FAIL' if differences else 'MATCH'}: {len(differences)} API/behavior differences")
    return 1 if differences or any(failed.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
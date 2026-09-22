"""Isolated exhaustive public-surface and raw-operation parity probe."""

from __future__ import annotations

import argparse
import asyncio
from contextlib import redirect_stdout
from enum import Enum
import importlib
import importlib.util
import inspect
import json
import logging
from pathlib import Path
import subprocess
import sys
import types
import typing

NAMESPACE = "azure.ai.finetuningsessions"
MODULE = Path("azure/ai/finetuningsessions")


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
    namespace["_types"] = importlib.import_module(NAMESPACE + "._types")
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


async def raw_operations(harness):
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
    result = {"type": "sample", "operation_id": "op", "status": "succeeded", "sequences": []}
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
                case.expect(verb, path, payload, body=body, status=202 if asynchronous and is_lro else 200)
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
                        value = await value.result() if asynchronous else value.result()
                    elif mode in ("stream", "raw_stream") and target != "sessions.create":
                        chunks = [chunk async for chunk in value] if asynchronous else list(value)
                        value = {"stream": b"".join(chunks).decode()}
                    output = {"type": type(value).__name__, "value": ctx.value(value)}
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
                        await value
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


def worker(package, harness_path):
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
    harness._install_offline_guard()
    sys.path.insert(0, str(package))
    logging.getLogger("azure").setLevel(logging.CRITICAL)
    try:
        origin = Path(importlib.import_module(NAMESPACE).__file__).resolve()
        if origin != (package / MODULE / "__init__.py").resolve():
            raise RuntimeError(f"Wrong SDK imported: {origin}")
        public = surface()
        raw = loop.run_until_complete(raw_operations(harness))
        return {"surface": public, "raw": raw}
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--review-deltas", type=Path, help="Explicit, versioned post-baseline bug-fix contracts")
    args = parser.parse_args()
    if args.worker:
        with redirect_stdout(sys.stderr):
            report = worker(args.worker.resolve(), args.harness.resolve())
        print(json.dumps(report, sort_keys=True, ensure_ascii=True))
        return 0
    if args.reference is None or args.candidate is None:
        parser.error("--reference and --candidate are required unless --worker is used")
    sys.path.insert(0, str(args.harness.parent))
    from verify_loom_compatibility import _differences, _apply_review_header_contract
    reports = []
    for package in (args.reference, args.candidate):
        result = subprocess.run([sys.executable, "-I", "-B", "-X", "utf8", str(Path(__file__).resolve()),
                                 "--worker", str(package.resolve()), "--harness", str(args.harness.resolve())],
                                capture_output=True, text=True, encoding="utf8")
        if result.returncode:
            raise RuntimeError(result.stderr + result.stdout)
        reports.append(json.loads(result.stdout))
    if args.review_deltas:
        deltas = json.loads(args.review_deltas.read_text(encoding="utf-8"))
        if deltas.get("fixture_contracts") != ["direct-context-headers", "dual-auth-credential-annotations", "multimodal-model-input-typing"]:
            raise RuntimeError("Unsupported review comparison contract")
        reports[0]["raw"] = _apply_review_header_contract(reports[0]["raw"], raw=True)
        for client, original in ((".FineTuningSessionClient", "TokenCredential"),
                                 (".aio.FineTuningSessionClient", "AsyncTokenCredential")):
            parameter = reports[0]["surface"]["clients"][client]["__init__"]["signature"]["parameters"][1]
            if parameter["type"] != original:
                raise RuntimeError("The immutable baseline credential annotation changed unexpectedly")
            parameter["type"] = {"origin": "Union", "args": [original, "AzureKeyCredential"]}
        model_input = reports[0]["surface"]["models"]["ModelInput"]
        expected_chunks = {"origin": "list", "args": ["ModelInputChunk"]}
        if model_input["fields"]["chunks"]["type"] != expected_chunks:
            raise RuntimeError("The immutable token-only ModelInput annotation changed unexpectedly")
        chunks = {"origin": "list", "args": [{"origin": "Union", "args": ["ModelInputChunk", "ImageChunk"]}]}
        model_input["fields"]["chunks"]["type"] = chunks
        model_input["overloads"] = [
            {"parameters": [{"name": "chunks", "kind": "KEYWORD_ONLY", "type": chunks, "default": {"empty": True}}],
             "returns": "None", "async": False},
            {"parameters": [{"name": "mapping", "kind": "POSITIONAL_OR_KEYWORD", "type": {"origin": "Mapping", "args": ["str", "Any"]}, "default": {"empty": True}}],
             "returns": "None", "async": False},
        ]
        print("Applied only recorded header, dual-auth, and multimodal typing contracts; all other fields remain exact.")
    differences = _differences(*reports)
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
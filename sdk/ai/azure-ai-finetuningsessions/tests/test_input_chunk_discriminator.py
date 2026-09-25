# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Input-chunk inheritance, validation, and actual offline request serialization.

The package under test is selected by the test runner, not by this module.
Unknown SDK discriminator round trips do not promise service acceptance. Text
constructor normalization is deliberately distinguished from image validation.
"""

from __future__ import annotations

import asyncio
import base64
import json
import socket
from collections import UserDict
from copy import deepcopy
from io import BytesIO
from types import MappingProxyType
from typing import Any, get_args, get_origin, get_type_hints

import pytest
from azure.ai.finetuningsessions import FineTuningSession, FineTuningSessionClient, models
from azure.ai.finetuningsessions._patch import _SdkJSONEncoder
from azure.ai.finetuningsessions._utils.model_base import SdkJSONEncoder, _deserialize
from azure.ai.finetuningsessions.aio import FineTuningSessionClient as AsyncFineTuningSessionClient
from azure.ai.finetuningsessions.models import ImageChunk, InputChunk, InputChunkType, ModelInput, ModelInputChunk
from azure.ai.finetuningsessions.models import _models as generated
from azure.ai.finetuningsessions.models import _patch as model_patch
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.policies import UserAgentPolicy
from azure.core.pipeline.transport import AsyncHttpTransport, HttpTransport

# Valid, locally generated 1x1 RGB images: no Pillow dependency in SDK tests.
_IMAGES = {
    "jpeg": (
        "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwg"
        "JC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIy"
        "MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAED"
        "ASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQA"
        "AAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6"
        "Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKz"
        "tLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEB"
        "AQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKR"
        "obHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0"
        "dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna"
        "4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDi6KKK+ZP3E//Z"
    ),
    "png": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC",
    "webp": "UklGRjwAAABXRUJQVlA4IDAAAADQAQCdASoBAAEAAUAmJaACdLoB+AADsAD+8ut//NgVzXPv9//S4P0uD9Lg/9KQAAA=",
}
_CONSTRUCTORS = ("keywords", "mapping", "readonly-mapping", "user-mapping")
_ENDPOINT = "https://unit.invalid/api/projects/p"
_SESSION = "session_deadbeef"
_REQUEST_ID = "00000000-0000-4000-8000-000000000001"
_USER_AGENT = "input-chunk-discriminator-tests"
_PREVIEW = "FineTuningSessions=V1Preview"
_PARAMS = {
    "max_tokens": 8,
    "temperature": 0.75,
    "top_p": 0.9,
    "top_k": 4,
    "seed": 123,
    "stop_criteria": [0],
    "response_format": {"type": "json_object"},
}
_LOSS_INPUTS = {
    "target_tokens": {"data": [2.0, 3.0]},
    "weights": {"data": [1.0, 0.5]},
    "advantages": {"data": [0.25, 0.5]},
    "logprobs": {"data": [-0.1, -0.2]},
}


def _construct(model: Any, source: dict, constructor: str) -> Any:
    if constructor == "keywords":
        return model(**source)
    if constructor == "readonly-mapping":
        return model(MappingProxyType(source))
    if constructor == "user-mapping":
        return model(UserDict(source))
    return model(source)


def _wire(value: Any) -> Any:
    return json.loads(json.dumps(value, cls=_SdkJSONEncoder, exclude_readonly=True))


def _assert_wire(value: Any, expected: dict) -> None:
    assert value.as_dict() == expected
    assert _wire(value) == expected
    assert json.loads(json.dumps(value, cls=SdkJSONEncoder, exclude_readonly=True)) == expected


def _image_wire(image_format: str = "png") -> dict:
    return {"type": "image", "data": _IMAGES[image_format], "format": image_format, "expected_tokens": 7}


def _prompt_wire(layout: str = "mixed", *, tagged: bool = True) -> dict:
    chunks = [{"tokens": [1, 2]}, {"tokens": []}, {"tokens": [3, 2**31 - 1]}]
    if layout == "mixed":
        chunks = [chunks[0], _image_wire("jpeg"), chunks[1], _image_wire("png"), chunks[2], _image_wire("webp")]
    if tagged:
        for chunk in chunks:
            if "tokens" in chunk:
                chunk["type"] = "text"
    return {"chunks": chunks}


def _prompt(layout: str, constructor: str) -> ModelInput:
    legacy = _prompt_wire(layout, tagged=False)
    if constructor == "mapping":
        return ModelInput(legacy)
    chunks = [
        (
            ModelInputChunk(tokens=chunk["tokens"])
            if "tokens" in chunk
            else ImageChunk(
                data=base64.b64decode(chunk["data"], validate=True),
                format=chunk["format"],
                expected_tokens=chunk["expected_tokens"],
            )
        )
        for chunk in legacy["chunks"]
    ]
    return ModelInput(chunks=chunks)


def test_public_exports_preserve_existing_classes_and_add_open_base() -> None:
    for name in ("InputChunk", "InputChunkType", "ModelInputChunk", "ImageChunk", "ModelInput"):
        assert models.__all__.count(name) == 1
    assert models.ModelInputChunk is ModelInputChunk is generated.ModelInputChunk
    assert models.ImageChunk is ImageChunk is model_patch.ImageChunk
    assert models.ModelInput is ModelInput is model_patch.ModelInput
    assert issubclass(ImageChunk, generated.ImageChunk)
    assert issubclass(ModelInput, generated.ModelInput)
    assert issubclass(ImageChunk, InputChunk)
    assert issubclass(ModelInputChunk, InputChunk)
    assert get_type_hints(InputChunk)["type"] is str
    annotation = get_type_hints(ModelInput, localns={"_models": models})["chunks"]
    assert get_origin(annotation) is list
    (element,) = get_args(annotation)
    # Python 3.10 can retain this forward string inside a built-in generic.
    # Check the exact reference and resolve it, rather than skipping the type.
    if isinstance(element, str):
        assert element == "_models.InputChunk"
        element = models.InputChunk
    assert element is InputChunk
    assert {member.name: member.value for member in InputChunkType} == {"TEXT": "text", "IMAGE": "image"}
    assert isinstance(InputChunkType.TEXT, str)
    assert InputChunkType.TEXT == "text"
    assert InputChunkType.IMAGE == "image"


@pytest.mark.parametrize("constructor", _CONSTRUCTORS)
@pytest.mark.parametrize("tokens", [[], [1, 2], [0, 2**31 - 1]], ids=["empty", "ordinary", "int32-boundary"])
def test_text_auto_tag_preserves_tokens_and_constructor_input(constructor: str, tokens: list[int]) -> None:
    source = {"tokens": deepcopy(tokens)}
    before = deepcopy(source)
    chunk = _construct(ModelInputChunk, source, constructor)
    assert type(chunk) is ModelInputChunk
    assert isinstance(chunk, InputChunk)
    assert chunk.type == InputChunkType.TEXT
    assert chunk.tokens == tokens
    _assert_wire(chunk, {"type": "text", "tokens": tokens})
    assert source == before


@pytest.mark.parametrize("constructor", ["keywords", "mapping"])
@pytest.mark.parametrize(
    "marker", ["image", "future", "", None, 0], ids=["image", "unknown", "empty", "null", "number"]
)
def test_text_constructor_normalizes_marker_instead_of_strict_validation(constructor: str, marker: Any) -> None:
    """Characterize generated behavior; do not invent a strict text validator."""
    source = {"type": marker, "tokens": [1, 2]}
    before = deepcopy(source)
    chunk = _construct(ModelInputChunk, source, constructor)
    _assert_wire(chunk, {"type": "text", "tokens": [1, 2]})
    assert source == before


@pytest.mark.parametrize("constructor", _CONSTRUCTORS)
@pytest.mark.parametrize("image_format", _IMAGES)
@pytest.mark.parametrize("explicit_type", [False, True], ids=["default-tag", "explicit-tag"])
def test_image_inherits_generated_fields_and_round_trips_base64(constructor, image_format, explicit_type) -> None:
    expected = _image_wire(image_format)
    source = deepcopy(expected)
    if not explicit_type:
        del source["type"]
    image_bytes = base64.b64decode(expected["data"], validate=True)
    if constructor == "keywords":
        source["data"] = image_bytes
    before = deepcopy(source)
    image = _construct(ImageChunk, source, constructor)
    assert isinstance(image, generated.ImageChunk)
    assert isinstance(image, InputChunk)
    assert image.type == InputChunkType.IMAGE
    assert image.data == image_bytes
    assert image.format == image_format
    assert image.length == image.expected_tokens == 7
    _assert_wire(image, expected)
    restored = _deserialize(InputChunk, _wire(image))
    assert type(restored) is ImageChunk
    assert restored.data == image_bytes
    _assert_wire(restored, expected)
    assert source == before


@pytest.mark.parametrize("constructor", _CONSTRUCTORS)
@pytest.mark.parametrize("marker", ["text", "future", "", None, 0], ids=["text", "unknown", "empty", "null", "number"])
def test_image_rejects_explicit_incorrect_or_null_discriminator(constructor: str, marker: Any) -> None:
    source = {**_image_wire(), "type": marker}
    if constructor == "keywords":
        source["data"] = base64.b64decode(source["data"], validate=True)
    before = deepcopy(source)
    with pytest.raises(ValueError, match="image type must be 'image'"):
        _construct(ImageChunk, source, constructor)
    assert source == before


@pytest.mark.parametrize("variant", ["text", "jpeg", "png", "webp"])
def test_generated_base_deserializer_dispatches_to_public_variants(variant: str) -> None:
    source = {"type": "text", "tokens": [1, 2]} if variant == "text" else _image_wire(variant)
    before = deepcopy(source)
    chunk = _deserialize(InputChunk, source)
    assert type(chunk) is (ModelInputChunk if variant == "text" else ImageChunk)
    _assert_wire(chunk, before)
    assert source == before


@pytest.mark.parametrize("constructor", _CONSTRUCTORS)
@pytest.mark.parametrize("tagged", [False, True], ids=["legacy-text", "tagged-text"])
def test_model_input_mapping_deserializes_ordered_public_subclasses(constructor: str, tagged: bool) -> None:
    source = _prompt_wire(tagged=tagged)
    before = deepcopy(source)
    model_input = _construct(ModelInput, source, constructor)
    assert [type(chunk) for chunk in model_input.chunks] == [
        ModelInputChunk,
        ImageChunk,
        ModelInputChunk,
        ImageChunk,
        ModelInputChunk,
        ImageChunk,
    ]
    assert all(isinstance(chunk, InputChunk) for chunk in model_input.chunks)
    _assert_wire(model_input, _prompt_wire())
    restored = ModelInput(_wire(model_input))
    assert [type(chunk) for chunk in restored.chunks] == [type(chunk) for chunk in model_input.chunks]
    _assert_wire(restored, _prompt_wire())
    assert source == before


@pytest.mark.parametrize("constructor", ["keywords", "mapping"])
def test_model_input_tags_only_token_mappings_with_an_absent_type(constructor: str) -> None:
    source = {"chunks": [{"tokens": [1]}, {}, {"opaque": True}, {"type": None, "tokens": [2]}]}
    before = deepcopy(source)
    model_input = _construct(ModelInput, source, constructor)
    expected = deepcopy(before)
    expected["chunks"][0]["type"] = "text"
    assert type(model_input.chunks[0]) is ModelInputChunk
    assert all(type(chunk) is InputChunk for chunk in model_input.chunks[1:])
    _assert_wire(model_input, expected)
    assert source == before


@pytest.mark.parametrize("constructor", ["keywords", "mapping"])
@pytest.mark.parametrize("marker", ["future-kind", "encoded_text", "vendor.audio.v2"])
def test_open_base_accepts_future_discriminator_strings(constructor: str, marker: str) -> None:
    source = {"type": marker}
    chunk = _construct(InputChunk, source, constructor)
    assert type(chunk) is InputChunk
    assert chunk.type == marker
    _assert_wire(chunk, source)


@pytest.mark.parametrize("route", ["base-mapping", "base-deserializer", "model-input"])
@pytest.mark.parametrize("marker", ["future-kind", "encoded_text", ""])
def test_unknown_base_preserves_payload_without_promising_service_acceptance(route: str, marker: str) -> None:
    source = {
        "type": marker,
        "tokens": [1, 2],
        "data": "opaque-not-base64",
        "extension": {"type": "image", "tokens": [3], "values": [None, False]},
    }
    before = deepcopy(source)
    if route == "base-mapping":
        chunk = InputChunk(source)
    elif route == "base-deserializer":
        chunk = _deserialize(InputChunk, source)
    else:
        model_input = ModelInput({"chunks": [source]})
        _assert_wire(model_input, {"chunks": [before]})
        chunk = model_input.chunks[0]
    assert type(chunk) is InputChunk
    assert chunk.type == marker
    _assert_wire(chunk, before)
    assert source == before


@pytest.mark.parametrize("constructor", ["keywords", "mapping"])
@pytest.mark.parametrize("representation", ["wire-mapping", "generated-image"])
@pytest.mark.parametrize(
    "updates,error_type,message",
    [
        pytest.param({"data": None}, TypeError, "image data must be bytes", id="null-data"),
        pytest.param({"data": "%%%not-base64%%%"}, TypeError, "image data must be bytes", id="invalid-base64"),
        pytest.param({"data": ""}, ValueError, "does not match the image signature", id="empty-data"),
        pytest.param({"data": "bm90LWltYWdl"}, ValueError, "does not match the image signature", id="bad-signature"),
        pytest.param({"format": "jpeg"}, ValueError, "does not match the image signature", id="format-mismatch"),
        pytest.param({"format": "gif"}, ValueError, "image format must be jpeg, png, or webp", id="unsupported-format"),
        pytest.param({"expected_tokens": 0}, ValueError, "expected_tokens must be positive", id="zero-tokens"),
        pytest.param({"expected_tokens": -1}, ValueError, "expected_tokens must be positive", id="negative-tokens"),
    ],
)
def test_invalid_image_cannot_bypass_model_input_validation(
    constructor, representation, updates, error_type, message
) -> None:
    image = {**_image_wire(), **updates}
    before = deepcopy(image)
    chunk = generated.ImageChunk(image) if representation == "generated-image" else image
    with pytest.raises(error_type, match=message):
        _construct(ModelInput, {"chunks": [{"tokens": [1]}, chunk]}, constructor)
    assert image == before


@pytest.mark.parametrize("constructor", ["keywords", "mapping"])
@pytest.mark.parametrize("representation", ["wire-mapping", "public-image", "generated-image"])
@pytest.mark.parametrize("image_count", [64, 65])
def test_image_count_limit_counts_deserialized_images_only(constructor, representation, image_count) -> None:
    assert model_patch.MAX_IMAGES_PER_EXAMPLE == 64
    images = [_image_wire() for _ in range(image_count)]
    before = deepcopy(images)
    if representation != "wire-mapping":
        image_type = ImageChunk if representation == "public-image" else generated.ImageChunk
        images = [image_type(image) for image in images]
    source = {"chunks": [{"tokens": [1]}, *images, {"tokens": []}]}
    if image_count == 65:
        with pytest.raises(ValueError, match="model input supports at most 64 images"):
            _construct(ModelInput, source, constructor)
    else:
        model_input = _construct(ModelInput, source, constructor)
        assert len(model_input.chunks) == 66
        assert all(type(chunk) is ImageChunk for chunk in model_input.chunks[1:-1])
        _assert_wire(
            model_input, {"chunks": [{"tokens": [1], "type": "text"}, *before, {"tokens": [], "type": "text"}]}
        )
    assert [_wire(image) for image in images] == before


@pytest.mark.parametrize("constructor", ["keywords", "mapping"])
def test_image_byte_limit_boundary_and_model_specific_token_budget_are_unchanged(constructor, monkeypatch) -> None:
    assert model_patch.MAX_IMAGE_BYTES == 10_000_000
    data = base64.b64decode(_IMAGES["png"], validate=True)
    monkeypatch.setattr(model_patch, "MAX_IMAGE_BYTES", len(data))
    source = {**_image_wire(), "expected_tokens": 4097}
    model_input = _construct(ModelInput, {"chunks": [source]}, constructor)
    assert type(model_input.chunks[0]) is ImageChunk
    assert model_input.chunks[0].length == 4097
    _assert_wire(model_input, {"chunks": [source]})
    oversized = {**source, "data": base64.b64encode(data + b"x").decode("ascii")}
    before = deepcopy(oversized)
    with pytest.raises(ValueError, match=f"exceeds the {len(data)}-byte limit"):
        _construct(ModelInput, {"chunks": [oversized]}, constructor)
    assert oversized == before


@pytest.mark.parametrize("constructor", ["keywords", "mapping"])
def test_sampled_sequence_tokens_never_receive_an_input_discriminator(constructor: str) -> None:
    source = {"tokens": [7, 8], "text": "answer", "logprobs": [-0.1, -0.2]}
    before = deepcopy(source)
    sequence = _construct(models.SampledSequence, source, constructor)
    assert not isinstance(sequence, InputChunk)
    _assert_wire(sequence, before)
    result = models.SampleOperationResult(sequences=[sequence])
    expected = {"type": "sample", "sequences": [before]}
    _assert_wire(result, expected)
    restored = _deserialize(models.OperationResult, expected)
    assert type(restored.sequences[0]) is models.SampledSequence
    assert "type" not in restored.sequences[0]
    _assert_wire(restored, expected)
    assert source == before


@pytest.mark.parametrize("constructor", ["keywords", "mapping"])
def test_mutable_chunk_list_edits_are_visible_to_both_serializers(constructor: str) -> None:
    model_input = _construct(ModelInput, {"chunks": [{"tokens": [1]}, _image_wire()]}, constructor)
    chunks = model_input.chunks
    assert chunks is model_input.chunks
    chunks.append(ModelInputChunk(tokens=[3]))
    chunks[0].tokens.append(2)
    expected = {"chunks": [{"type": "text", "tokens": [1, 2]}, _image_wire(), {"type": "text", "tokens": [3]}]}
    _assert_wire(model_input, expected)
    chunks[1:2] = [ImageChunk(_image_wire("jpeg")), ModelInputChunk(tokens=[])]
    expected["chunks"][1:2] = [_image_wire("jpeg"), {"type": "text", "tokens": []}]
    assert type(chunks.pop()) is ModelInputChunk
    expected["chunks"].pop()
    chunks.reverse()
    expected["chunks"].reverse()
    _assert_wire(model_input, expected)
    assert model_input.chunks is chunks
    chunks.clear()
    _assert_wire(model_input, {"chunks": []})
    model_input.chunks = [ImageChunk(_image_wire("webp"))]
    model_input.chunks.insert(0, ModelInputChunk(tokens=[9]))
    _assert_wire(model_input, {"chunks": [{"type": "text", "tokens": [9]}, _image_wire("webp")]})


class _RequestCaptured(Exception):
    """Stop at the real transport boundary, before any polling or remote I/O."""


class _Capture:
    def __init__(self) -> None:
        self.requests: list[dict] = []
        self.closed = False

    def record(self, request: Any) -> None:
        content = request.content
        if hasattr(content, "read"):
            content = content.read()
        raw = content.encode("utf-8") if isinstance(content, str) else content
        self.requests.append(
            {
                "method": request.method,
                "url": request.url,
                "headers": dict(request.headers),
                "raw": raw,
                "body": json.loads(raw),
            }
        )
        raise _RequestCaptured


class _SyncTransport(HttpTransport):
    def __init__(self, capture: _Capture) -> None:
        self.capture = capture

    def send(self, request: Any, **kwargs: Any) -> Any:
        self.capture.record(request)

    def open(self) -> None:
        pass

    def close(self) -> None:
        self.capture.closed = True

    def __exit__(self, *args: object) -> None:
        self.close()


class _AsyncTransport(AsyncHttpTransport):
    def __init__(self, capture: _Capture) -> None:
        self.capture = capture

    async def send(self, request: Any, **kwargs: Any) -> Any:
        self.capture.record(request)

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        self.capture.closed = True

    async def __aexit__(self, *args: object) -> None:
        await self.close()


def _isolate_io(monkeypatch: Any) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Discriminator tests must not perform network I/O")

    # Called inside a running loop: Windows needs a socket pair to create it.
    for name in ("connect", "connect_ex"):
        monkeypatch.setattr(socket.socket, name, forbidden)
    for name in ("create_connection", "getaddrinfo"):
        monkeypatch.setattr(socket, name, forbidden)
    monkeypatch.setattr(FineTuningSession, "_start_heartbeat", lambda self: None)
    for name in (
        "X_COGNITIVE_SUBSCRIPTION_ID",
        "COGNITIVE_SUBSCRIPTION_ID",
        "AZURE_SUBSCRIPTION_ID",
        "LOOM_AZURE_RESOURCE_ID",
        "LOOM_AZURE_RESOURCE_TENANT_ID",
        "LOOM_AZURE_RESOURCE_LOCATION",
        "LOOM_WORKSPACE_RESOURCE_ID",
    ):
        monkeypatch.delenv(name, raising=False)


def _request_model(operation: str, prompt: ModelInput) -> Any:
    if operation == "sample":
        return models.SampleRequest(
            prompt=prompt,
            sampling_params=models.SamplingParams(**deepcopy(_PARAMS)),
            num_samples=2,
            prompt_logprobs=True,
            topk_prompt_logprobs=2,
        )
    datum = models.Datum(model_input=prompt, loss_fn_inputs=models.LossFnInputs(deepcopy(_LOSS_INPUTS)))
    if operation == "forward_backward":
        return models.ForwardBackwardRequest(
            forward_backward_input=models.ForwardBackwardInput(data=[datum], loss_fn="cross_entropy")
        )
    return models.ForwardRequest(forward_input=models.ForwardInput(data=[datum], loss_fn="cross_entropy"))


def _expected_body(operation: str, prompt: dict) -> dict:
    if operation == "sample":
        return {
            "prompt": deepcopy(prompt),
            "sampling_params": deepcopy(_PARAMS),
            "num_samples": 2,
            "prompt_logprobs": True,
            "topk_prompt_logprobs": 2,
        }
    return {
        f"{operation}_input": {
            "data": [{"model_input": deepcopy(prompt), "loss_fn_inputs": deepcopy(_LOSS_INPUTS)}],
            "loss_fn": "cross_entropy",
        }
    }


async def _capture_request(
    asynchronous, operation, request_model, monkeypatch, *, raw_body=None, token_list=None
) -> dict:
    capture = _Capture()
    with monkeypatch.context() as isolated:
        _isolate_io(isolated)
        client_type = AsyncFineTuningSessionClient if asynchronous else FineTuningSessionClient
        transport = _AsyncTransport(capture) if asynchronous else _SyncTransport(capture)
        client = client_type(
            _ENDPOINT,
            AzureKeyCredential("fixture-key"),
            transport=transport,
            retry_total=0,
            user_agent_policy=UserAgentPolicy(base_user_agent=_USER_AGENT, user_agent_use_env=False),
            headers={"x-ms-client-request-id": _REQUEST_ID},
        )
        try:
            with pytest.raises(_RequestCaptured):
                if raw_body is not None:
                    group = client.sampling if operation == "sample" else client.training
                    options = {"params": {"checkpoint_id": "base"}} if operation == "sample" else {}
                    result = getattr(group, f"begin_{operation}")(
                        _SESSION, raw_body, api_version="v1", foundry_features=_PREVIEW, **options
                    )
                else:
                    target = client if asynchronous else FineTuningSession(client, _SESSION)
                    args = [_SESSION] if asynchronous else []
                    if operation == "sample":
                        result = target.sample(
                            *args,
                            request_model.prompt if token_list is None else token_list,
                            request_model.sampling_params,
                            checkpoint_id="base",
                            num_samples=2,
                            prompt_logprobs=True,
                            topk_prompt_logprobs=2,
                        )
                    else:
                        data = getattr(request_model, f"{operation}_input").data
                        result = getattr(target, operation)(*args, data, loss_fn="cross_entropy")
                if asynchronous:
                    await result
        finally:
            if asynchronous:
                await client.close()
            else:
                client.close()
    assert capture.closed
    assert len(capture.requests) == 1
    return capture.requests[0]


def _assert_request(request: dict, operation: str, expected: dict, *, raw: bool = False, stream: bool = False) -> None:
    query = "api-version=v1"
    if operation == "sample":
        query = "checkpoint_id=base&api-version=v1" if raw else "api-version=v1&checkpoint_id=base"
    assert request["method"] == "POST"
    assert request["url"] == f"{_ENDPOINT}/fine_tuning/sessions/{_SESSION}/{operation}?{query}"
    assert request["body"] == expected
    expected_headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "foundry-features": _PREVIEW,
        "x-ms-client-request-id": _REQUEST_ID,
        "user-agent": _USER_AGENT,
        "api-key": "fixture-key",
    }
    # Azure Core leaves framing to the concrete transport for an IO[bytes] body.
    if not stream:
        expected_headers["content-length"] = str(len(request["raw"]))
    assert {key.lower(): value for key, value in request["headers"].items()} == expected_headers


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "aio"])
@pytest.mark.parametrize("operation", ["forward", "forward_backward", "sample"])
@pytest.mark.parametrize("layout", ["text", "mixed"])
@pytest.mark.parametrize("constructor", ["keywords", "mapping"])
def test_convenience_transport_emits_complete_discriminated_requests(
    asynchronous, operation, layout, constructor, monkeypatch
) -> None:
    request_model = _request_model(operation, _prompt(layout, constructor))
    expected = _expected_body(operation, _prompt_wire(layout))
    _assert_wire(request_model, expected)
    recorded = asyncio.run(_capture_request(asynchronous, operation, request_model, monkeypatch))
    _assert_request(recorded, operation, expected)
    _assert_wire(request_model, expected)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "aio"])
@pytest.mark.parametrize("operation", ["forward_backward", "sample"])
@pytest.mark.parametrize("body_form", ["model", "tagged-mapping", "legacy-mapping", "bytes", "stream"])
def test_raw_transport_preserves_models_and_explicit_wire_bodies(
    asynchronous, operation, body_form, monkeypatch
) -> None:
    request_model = _request_model(operation, _prompt("mixed", "mapping"))
    expected = _expected_body(operation, _prompt_wire(tagged=body_form != "legacy-mapping"))
    before = _wire(request_model)
    body = request_model if body_form == "model" else deepcopy(expected)
    if body_form in ("bytes", "stream"):
        body = json.dumps(body).encode("utf-8")
        if body_form == "stream":
            body = BytesIO(body)
    recorded = asyncio.run(_capture_request(asynchronous, operation, request_model, monkeypatch, raw_body=body))
    _assert_request(recorded, operation, expected, raw=True, stream=body_form == "stream")
    _assert_wire(request_model, before)
    if body_form.endswith("mapping"):
        assert body == expected


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "aio"])
@pytest.mark.parametrize("tokens", [[], [1, 2], [0, 2**31 - 1]], ids=["empty", "ordinary", "int32-boundary"])
def test_convenience_sampling_token_list_gets_text_tag(asynchronous, tokens, monkeypatch) -> None:
    before = deepcopy(tokens)
    request_model = _request_model("sample", _prompt("text", "keywords"))
    recorded = asyncio.run(_capture_request(asynchronous, "sample", request_model, monkeypatch, token_list=tokens))
    expected = _expected_body("sample", {"chunks": [{"type": "text", "tokens": before}]})
    _assert_request(recorded, "sample", expected)
    assert tokens == before

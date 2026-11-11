# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Focused error-body, retry-hint, and image-construction regressions."""

import base64
from collections import UserDict
from copy import deepcopy
import json
from types import MappingProxyType

import pytest

from azure.ai.finetuningsessions import _exceptions as errors
from azure.ai.finetuningsessions._utils.model_base import SdkJSONEncoder
from azure.ai.finetuningsessions.models import ImageChunk, ModelInput, SampleRequest, SamplingParams
from azure.ai.finetuningsessions.models import _patch as model_patch


class _Response:
    def __init__(self, status_code, headers=None):
        self.status_code = status_code
        self.reason = "fixture"
        self.headers = {} if headers is None else headers

    def json(self):
        return {}

    def text(self):
        return "{}"


class _FloatValue:
    def __init__(self, value):
        self.value = value

    def __float__(self):
        return self.value


class _FloatFailure:
    def __init__(self, error_type):
        self.error_type = error_type

    def __float__(self):
        raise self.error_type("float conversion failed")


_RETRY_HINTS = [
    pytest.param(2, 2.0, 2.0, id="positive-integer"),
    pytest.param(0.25, 0.25, 0.25, id="positive-float"),
    pytest.param("2.5", 2.5, 2.5, id="positive-string"),
    pytest.param(0, 0.0, None, id="zero"),
    pytest.param("0", 0.0, None, id="zero-string"),
    pytest.param(-0.0, 0.0, None, id="negative-zero"),
    pytest.param(False, 0.0, None, id="false"),
    pytest.param(True, 1.0, 1.0, id="true"),
    pytest.param(None, None, None, id="missing"),
    pytest.param(-1, None, None, id="negative-integer"),
    pytest.param("-2.5", None, None, id="negative-string"),
    pytest.param(float("nan"), None, None, id="nan"),
    pytest.param("NaN", None, None, id="nan-string"),
    pytest.param(float("inf"), None, None, id="infinity"),
    pytest.param(float("-inf"), None, None, id="negative-infinity"),
    pytest.param("inf", None, None, id="infinity-string"),
    pytest.param("-inf", None, None, id="negative-infinity-string"),
    pytest.param(10**1000, None, None, id="overflowing-integer"),
    pytest.param("1e10000", None, None, id="overflowing-exponent"),
    pytest.param("", None, None, id="empty-string"),
    pytest.param("later", None, None, id="invalid-string"),
    pytest.param([], None, None, id="list"),
    pytest.param({}, None, None, id="dict"),
    pytest.param(_FloatFailure(OverflowError), None, None, id="custom-overflow"),
    pytest.param(_FloatFailure(TypeError), None, None, id="custom-type-error"),
    pytest.param(_FloatFailure(ValueError), None, None, id="custom-value-error"),
    pytest.param(_FloatValue(0.5), 0.5, 0.5, id="custom-positive"),
    pytest.param(_FloatValue(0.0), 0.0, None, id="custom-zero"),
    pytest.param(_FloatValue(-1.0), None, None, id="custom-negative"),
    pytest.param(_FloatValue(float("nan")), None, None, id="custom-nan"),
    pytest.param(_FloatValue(float("inf")), None, None, id="custom-infinity"),
]


@pytest.mark.parametrize(
    "status_code, expected_type, expected_message",
    [
        (400, None, None),
        (409, errors.TrainingEngineError, "The model's engine has died"),
        (413, errors.BatchTooLargeError, "Batch too large"),
        (422, None, None),
        (429, errors.RateLimitedError, "Rate limited"),
        (500, None, None),
        (503, errors.NoCapacityError, "No available engine capacity"),
        (418, None, None),
    ],
    ids=["400", "409", "413", "422", "429", "500", "503", "unrecognized"],
)
@pytest.mark.parametrize(
    "document",
    ["null", "true", "false", "0", "42", "1.5", '""', '"engine crashed"', "[]", '[{"reason":"engine_busy"}]'],
    ids=["null", "true", "false", "zero", "integer", "float", "empty-string", "string", "empty-list", "list"],
)
def test_http_non_object_json_bodies(status_code, expected_type, expected_message, document):
    body = json.loads(document)
    original = deepcopy(body)
    response = _Response(status_code)

    error = errors._classify_http_error(status_code, body, response=response, session_id="session_test")

    assert body == original
    if expected_type is None:
        assert error is None
    else:
        assert type(error) is expected_type
        assert error.message == expected_message
        assert error.response is response
        if isinstance(error, errors.TrainingEngineError):
            assert error.session_id == "session_test"


@pytest.mark.parametrize("nested", [False, True], ids=["flat", "detail"])
@pytest.mark.parametrize(
    "status_code, detail, expected_type, attributes",
    [
        pytest.param(
            413,
            {"field": "forward_backward_input.data", "message": "Batch size (8) exceeds the maximum allowed (4)"},
            errors.BatchTooLargeError,
            {"actual_batch_size": 8, "max_batch_size": 4},
            id="batch-too-large",
        ),
        pytest.param(413, {"field": "user_metadata", "message": "too large"}, None, {}, id="metadata-too-large"),
        pytest.param(
            503,
            {"reason": "engine_busy", "message": "No engine capacity", "retry_after_sec": "2.5"},
            errors.NoCapacityError,
            {"reason": "engine_busy", "retry_after_sec": 2.5},
            id="capacity",
        ),
        pytest.param(
            503,
            {"reason": "queue_full", "message": "Wait for this operation", "retry_after_sec": 0},
            errors.ContentionError,
            {"reason": "queue_full", "retry_after_sec": 0.0},
            id="contention",
        ),
        pytest.param(
            500,
            {"code": "worker_crashed", "message": "Worker unavailable", "debug_ref": "trace"},
            errors.TrainingEngineError,
            {"error_code": "worker_crashed", "debug_ref": "trace", "session_id": "session_test"},
            id="worker-crashed",
        ),
        pytest.param(
            500,
            {"type": "internal_model_error", "error_message": "No engine capacity"},
            errors.NoCapacityError,
            {"reason": "internal_model_error"},
            id="legacy-capacity",
        ),
        pytest.param(
            409,
            {"reason": "engine_dead", "message": "Session unavailable", "debug_ref": "trace"},
            errors.TrainingEngineError,
            {"error_code": "engine_dead", "debug_ref": "trace", "session_id": "session_test"},
            id="engine-dead",
        ),
        pytest.param(
            400,
            {"type": "validation_error", "field": "data", "message": "Invalid data"},
            errors.RequestValidationError,
            {"error_code": "invalid_request", "field": "data"},
            id="validation-type",
        ),
        pytest.param(
            422,
            {"code": "invalid_request", "message": "Invalid data", "debug_ref": "trace"},
            errors.RequestValidationError,
            {"error_code": "invalid_request", "debug_ref": "trace"},
            id="validation-code",
        ),
        pytest.param(500, {"message": "Unrecognized failure"}, None, {}, id="unknown-server-error"),
        pytest.param(409, {"message": "Unrecognized conflict"}, None, {}, id="unknown-conflict"),
    ],
)
def test_http_supported_object_bodies(status_code, detail, expected_type, attributes, nested):
    body = {"detail": deepcopy(detail)} if nested else deepcopy(detail)
    original = deepcopy(body)
    error = errors._classify_http_error(status_code, body, session_id="session_test")

    assert body == original
    if expected_type is None:
        assert error is None
    else:
        assert type(error) is expected_type
        assert error.message == (detail.get("message") or detail["error_message"])
        for name, expected in attributes.items():
            assert getattr(error, name) == expected


@pytest.mark.parametrize("route", ["503-flat", "503-detail", "429-body", "429-header", "429-fallback"])
@pytest.mark.parametrize("value, http_expected, poll_expected", _RETRY_HINTS)
def test_http_retry_hints(route, value, http_expected, poll_expected):
    if route.startswith("503"):
        detail = {"reason": "engine_busy", "message": "No engine capacity", "retry_after_sec": value}
        body = {"detail": detail} if route == "503-detail" else detail
        error = errors._classify_http_error(503, body)
        assert type(error) is errors.NoCapacityError
        assert error.reason == "engine_busy"
    else:
        body = {"reason": "budget_exhausted", "message": "Budget exhausted"}
        headers = {}
        if route == "429-header":
            headers["Retry-After"] = value
        else:
            body["retry_after_sec"] = value
        if route == "429-fallback":
            headers["Retry-After"] = "3.5"
            if http_expected is None:
                http_expected = 3.5
        response = _Response(429, headers)
        error = errors._classify_http_error(429, body, response=response)
        assert type(error) is errors.RateLimitedError
        assert error.reason == "budget_exhausted"
        assert error.message == "Budget exhausted"
        assert error.response is response
    assert error.retry_after_sec == http_expected


@pytest.mark.parametrize("value, http_expected, poll_expected", _RETRY_HINTS)
def test_poll_retry_hints(value, http_expected, poll_expected):
    envelope = {
        "status": "failed",
        "error": "Try again",
        "error_code": "custom_retryable_failure",
        "should_retry": True,
        "retry_after_sec": value,
        "debug_ref": "trace",
    }
    original = envelope.copy()
    error = errors._classify_poll_failure(envelope)

    assert type(error) is errors.RequestRetryableError
    assert error.retry_after_sec == poll_expected
    assert error.error_code == "custom_retryable_failure"
    assert error.debug_ref == "trace"
    assert error.message == "Try again"
    assert envelope == original


@pytest.mark.parametrize("route", ["503", "429-body", "429-header", "poll"])
def test_unexpected_float_errors_are_not_suppressed(route):
    value = _FloatFailure(RuntimeError)
    with pytest.raises(RuntimeError, match="float conversion failed"):
        if route == "poll":
            errors._classify_poll_failure({"should_retry": True, "retry_after_sec": value})
        elif route == "429-header":
            errors._classify_http_error(429, {}, response=_Response(429, {"Retry-After": value}))
        else:
            errors._classify_http_error(503 if route == "503" else 429, {"retry_after_sec": value})


@pytest.mark.parametrize("completed", [False, True], ids=["failed", "completed"])
def test_terminal_poll_failures_do_not_parse_retry_hint(completed):
    code = "operation_completed_result_unavailable" if completed else "operation_failed_result_unavailable"
    error = errors._classify_poll_failure(
        {"error_code": code, "should_retry": True, "retry_after_sec": _FloatFailure(RuntimeError)}
    )

    assert type(error) is errors.OperationResultUnavailableError
    assert error.operation_completed is completed
    assert error.error_code == code


_IMAGE_CONSTRUCTORS = ["keywords", "bytes-mapping", "json-mapping", "readonly-json-mapping", "user-json-mapping"]
_JPEG = b"\xff\xd8\xffjpeg"


def _image_source(values, constructor):
    source = values.copy()
    if "json" in constructor:
        source = json.loads(json.dumps(source, cls=SdkJSONEncoder))
    if constructor == "readonly-json-mapping":
        return MappingProxyType(source)
    if constructor == "user-json-mapping":
        return UserDict(source)
    return source


def _construct_image(source, constructor):
    return ImageChunk(**source) if constructor == "keywords" else ImageChunk(source)


@pytest.mark.parametrize("constructor", _IMAGE_CONSTRUCTORS)
@pytest.mark.parametrize("explicit_type", [False, True], ids=["omitted-type", "image-type"])
@pytest.mark.parametrize(
    "image_format, data",
    [("jpeg", _JPEG), ("png", b"\x89PNG\r\n\x1a\npng"), ("webp", b"RIFF\x04\x00\x00\x00WEBP")],
    ids=["jpeg", "png", "webp"],
)
def test_image_bytes_and_type_round_trip(constructor, explicit_type, image_format, data):
    values = {"data": data, "format": image_format, "expected_tokens": 12}
    if explicit_type:
        values["type"] = "image"
    source = _image_source(values, constructor)
    original = deepcopy(dict(source))

    image = _construct_image(source, constructor)

    expected = {
        "type": "image",
        "data": base64.b64encode(data).decode("ascii"),
        "format": image_format,
        "expected_tokens": 12,
    }
    assert image.type == "image"
    assert image.data == data
    assert image.length == 12
    assert image.as_dict() == expected
    assert json.loads(json.dumps(image, cls=SdkJSONEncoder)) == expected

    request = SampleRequest(
        num_samples=1,
        prompt=ModelInput(chunks=[image]),
        sampling_params=SamplingParams(max_tokens=8),
    )
    payload = json.loads(json.dumps(request, cls=SdkJSONEncoder, exclude_readonly=True))
    assert payload["prompt"]["chunks"] == [expected]
    assert dict(source) == original


@pytest.mark.parametrize("constructor", _IMAGE_CONSTRUCTORS)
@pytest.mark.parametrize("marker", ["text", "", None, 0], ids=["text", "empty-string", "null", "number"])
def test_image_rejects_explicit_wrong_type(constructor, marker):
    source = _image_source({"type": marker, "data": _JPEG, "format": "jpeg", "expected_tokens": 1}, constructor)
    original = deepcopy(dict(source))

    with pytest.raises(ValueError, match="image type must be 'image'"):
        _construct_image(source, constructor)

    assert dict(source) == original


@pytest.mark.parametrize("constructor", _IMAGE_CONSTRUCTORS)
@pytest.mark.parametrize(
    "updates, error_type, message",
    [
        pytest.param({"data": None}, TypeError, "image data must be bytes", id="missing-bytes"),
        pytest.param({"data": b""}, ValueError, "does not match the image signature", id="empty-bytes"),
        pytest.param({"data": b"not-an-image"}, ValueError, "does not match the image signature", id="wrong-signature"),
        pytest.param({"format": "gif"}, ValueError, "image format must be jpeg, png, or webp", id="unsupported-format"),
        pytest.param({"expected_tokens": 0}, ValueError, "expected_tokens must be positive", id="zero-tokens"),
        pytest.param({"expected_tokens": -1}, ValueError, "expected_tokens must be positive", id="negative-tokens"),
    ],
)
def test_image_validation_is_preserved(constructor, updates, error_type, message):
    source = _image_source({"data": _JPEG, "format": "jpeg", "expected_tokens": 1, **updates}, constructor)
    original = deepcopy(dict(source))

    with pytest.raises(error_type, match=message):
        _construct_image(source, constructor)

    assert dict(source) == original


@pytest.mark.parametrize("constructor", _IMAGE_CONSTRUCTORS)
def test_image_size_limit_is_preserved(constructor, monkeypatch):
    monkeypatch.setattr(model_patch, "MAX_IMAGE_BYTES", len(_JPEG) - 1)
    source = _image_source({"data": _JPEG, "format": "jpeg", "expected_tokens": 1}, constructor)

    with pytest.raises(ValueError, match="image data exceeds"):
        _construct_image(source, constructor)


@pytest.mark.parametrize("constructor", _IMAGE_CONSTRUCTORS)
def test_model_input_image_count_limit_is_preserved(constructor, monkeypatch):
    monkeypatch.setattr(model_patch, "MAX_IMAGES_PER_EXAMPLE", 1)
    source = _image_source({"data": _JPEG, "format": "jpeg", "expected_tokens": 1}, constructor)
    image = _construct_image(source, constructor)

    with pytest.raises(ValueError, match="model input supports at most 1 images"):
        ModelInput(chunks=[image, image])

import importlib
import math
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum, IntEnum

import pytest
from azure.ai.finetuningsessions._utils import model_base
from azure.ai.finetuningsessions.models import ForwardBackwardOperationResult


@pytest.mark.parametrize("value", [None, "", "text", 0, 123, True, False, 0.0, -0.0, 0.125, float("inf")])
@pytest.mark.parametrize("format", [None, "str"])
def test_builtin_scalars_do_not_probe_temporal_protocols(monkeypatch, value, format):
    def temporal_probe(*args):
        raise AssertionError("JSON primitives must not use exception-driven temporal conversion")

    monkeypatch.setattr(model_base, "_serialize_datetime", temporal_probe)
    monkeypatch.setattr(model_base, "_timedelta_as_isostr", temporal_probe)
    result = model_base._serialize(value, format)
    if isinstance(value, int) and format == "str":
        assert result == str(value)
    else:
        assert result is value


def test_nan_and_signed_zero_are_not_coerced():
    value = float("nan")
    assert model_base._serialize(value) is value
    assert math.copysign(1.0, model_base._serialize(-0.0)) == -1.0


def test_enum_and_nonprimitive_wire_formats_are_preserved():
    class Number(IntEnum):
        ONE = 1

    class Text(str, Enum):
        READY = "ready"

    assert model_base._serialize(Number.ONE, "str") == 1
    assert type(model_base._serialize(Text.READY)) is str
    assert model_base._serialize(Text.READY) == "ready"
    assert model_base._serialize(Decimal("1.25")) == 1.25
    assert model_base._serialize(b"abc") == "YWJj"
    assert model_base._serialize(["a", "b"], "commaDelimited") == "a,b"
    timestamp = datetime(2026, 9, 26, 12, 30, tzinfo=timezone.utc)
    assert model_base._serialize(timestamp) == model_base._serialize_datetime(timestamp)
    duration = timedelta(days=1, seconds=2)
    assert model_base._serialize(duration) == model_base._timedelta_as_isostr(duration)


def test_primitive_subclasses_keep_their_existing_protocol_behavior():
    class TimedFloat(float):
        def total_seconds(self):
            return 2

    class NamedInt(int):
        def __str__(self):
            return "named"

    value = TimedFloat(1.25)
    assert model_base._serialize(value) == model_base._timedelta_as_isostr(value)
    assert model_base._serialize(NamedInt(7), "str") == "named"


def test_scalar_registration_is_idempotent_across_helper_reload():
    from azure.ai.finetuningsessions import _scalar_serialization

    installed = model_base._serialize
    original = installed.__wrapped__
    _scalar_serialization.install_scalar_serialization()
    assert model_base._serialize is installed
    importlib.reload(_scalar_serialization).install_scalar_serialization()
    assert model_base._serialize is installed
    assert model_base._serialize.__wrapped__ is original
    assert model_base._serialize({"values": [1.25, "text", None]}) == {"values": [1.25, "text", None]}


def test_tensor_result_keeps_all_values_and_mutable_copy_semantics(monkeypatch):
    def temporal_probe(*args):
        raise AssertionError("Numeric tensor elements must not probe temporal protocols")

    monkeypatch.setattr(model_base, "_serialize_datetime", temporal_probe)
    monkeypatch.setattr(model_base, "_timedelta_as_isostr", temporal_probe)
    values = [index / 16 for index in range(4096)]
    raw = {
        "loss_fn_outputs": [{"logprobs": {"data": values, "dtype": "float32", "shape": [4096]}}],
        "metrics": {"training_tokens": 4096, "training_duration_s": 1.25},
    }
    result = ForwardBackwardOperationResult(raw)
    outputs = result.loss_fn_outputs
    assert outputs[0]["logprobs"]["data"] == values
    assert outputs[0]["logprobs"]["data"] is not values
    outputs[0]["logprobs"]["data"].append(0.125)
    assert len(result.loss_fn_outputs[0]["logprobs"]["data"]) == 4097
    assert len(values) == 4096
    assert result.metrics == raw["metrics"]

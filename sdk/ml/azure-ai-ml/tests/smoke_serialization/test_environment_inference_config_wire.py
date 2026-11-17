# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Guard for the ``Environment.inference_config`` route wire (regression from the arm migration).

The custom-container online-endpoint samples construct ``Environment(inference_config={raw dict})``
directly in Python (not via YAML). The legacy msrest typed field implicitly mapped that snake_case
dict to camelCase wire keys (``livenessRoute``/``readinessRoute``/``scoringRoute``); the arm hybrid
encoder serializes a plain dict verbatim, so without conversion the server rejects it with
"You must specify all three of: liveness, readiness and scoring routes".

This case CANNOT use a baseline-captured golden: main's bare ``.serialize()`` raises on a raw-dict
typed field (``'dict' object has no attribute '_attribute_map'``), so the expected wire is asserted
explicitly here. That also makes the test fail loudly if the fix is ever reverted (the raw dict
would serialize back to snake_case keys).
"""
import pytest

from azure.ai.ml._restclient.arm_ml_service.models import InferenceContainerProperties, Route
from azure.ai.ml.entities import Environment

from _wire import serialize_wire

_LIVENESS = {"port": 8501, "path": "/v1/models/half_plus_two"}
_READINESS = {"port": 8501, "path": "/v1/models/half_plus_two"}
_SCORING = {"port": 8501, "path": "/v1/models/half_plus_two:predict"}

_EXPECTED_INFERENCE_CONFIG = {
    "livenessRoute": _LIVENESS,
    "readinessRoute": _READINESS,
    "scoringRoute": _SCORING,
}


def _env_from_raw_dict():
    """Environment built exactly like the custom-container sample notebook (raw snake_case dict)."""
    return Environment(
        image="docker.io/tensorflow/serving:latest",
        inference_config={
            "liveness_route": dict(_LIVENESS),
            "readiness_route": dict(_READINESS),
            "scoring_route": dict(_SCORING),
        },
    )


def _env_from_arm_model():
    """Environment built the way ``InferenceConfigSchema`` produces it (arm model)."""
    return Environment(
        image="docker.io/tensorflow/serving:latest",
        inference_config=InferenceContainerProperties(
            liveness_route=Route(port=_LIVENESS["port"], path=_LIVENESS["path"]),
            readiness_route=Route(port=_READINESS["port"], path=_READINESS["path"]),
            scoring_route=Route(port=_SCORING["port"], path=_SCORING["path"]),
        ),
    )


@pytest.mark.parametrize("builder", [_env_from_raw_dict, _env_from_arm_model], ids=["raw_dict", "arm_model"])
def test_environment_inference_config_routes_wire(builder):
    """Both construction paths must emit the three camelCase routes the server requires."""
    wire = serialize_wire(builder()._to_rest_object())
    assert wire["properties"]["inferenceConfig"] == _EXPECTED_INFERENCE_CONFIG

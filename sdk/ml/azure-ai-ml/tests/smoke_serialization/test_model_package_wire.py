# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for model-package entities.

See ``test_command_job_wire.py`` for the two-check pattern (serialization guard + wire equivalence).
"""
import pytest

from _builders_model_package import MODEL_PACKAGE_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes


@pytest.mark.parametrize("case_name", sorted(MODEL_PACKAGE_BUILDERS))
def test_model_package_serializes(case_name):
    """The model-package rest object must serialize to wire without raising."""
    entity = MODEL_PACKAGE_BUILDERS[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(MODEL_PACKAGE_BUILDERS))
def test_model_package_wire_matches_expected(case_name):
    """The model-package wire must be byte-identical to the baseline captured from main."""
    entity = MODEL_PACKAGE_BUILDERS[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())

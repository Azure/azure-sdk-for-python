# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for CustomModelFineTuningJob.

See ``test_command_job_wire.py`` for the two-check pattern (serialization guard + wire equivalence).
The finetuning ``_to_rest_object`` builds an arm_ml_service hybrid envelope, so its ``outputs`` are
wrapped with ``to_hybrid_rest_model`` (and ``is_archived`` is set explicitly) to keep the wire
byte-identical to the pre-migration baseline.
"""
import pytest

from _builders import AOAI_FINETUNING_BUILDERS, FINETUNING_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes


@pytest.mark.parametrize("case_name", sorted(FINETUNING_BUILDERS))
def test_custom_finetuning_serializes(case_name):
    """The CustomModelFineTuningJob rest object must serialize to wire without raising."""
    entity = FINETUNING_BUILDERS[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(FINETUNING_BUILDERS))
def test_custom_finetuning_wire_matches_expected(case_name):
    """The CustomModelFineTuningJob wire must be byte-identical to the baseline captured from main."""
    entity = FINETUNING_BUILDERS[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(AOAI_FINETUNING_BUILDERS))
def test_aoai_finetuning_serializes(case_name):
    """The AzureOpenAIFineTuningJob rest object must serialize to wire without raising."""
    entity = AOAI_FINETUNING_BUILDERS[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(AOAI_FINETUNING_BUILDERS))
def test_aoai_finetuning_wire_matches_expected(case_name):
    """The AzureOpenAIFineTuningJob wire must be byte-identical to the baseline captured from main."""
    entity = AOAI_FINETUNING_BUILDERS[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())

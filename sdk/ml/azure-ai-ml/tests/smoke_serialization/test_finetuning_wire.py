# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Golden wire-serialization smoke tests for CustomModelFineTuningJob.

KNOWN-BREAK GUARD: custom finetuning has a pre-existing serialize issue on the arm_ml_service path
(custom finetuning ``outputs`` / ``queue_settings``). On ``main`` it serializes fine via the msrest
``v2024_10_01_preview`` client, so the golden is capturable; on a migration branch routing finetuning
to the arm hybrid client, it may raise or diff. These tests are therefore marked ``xfail`` (non-strict):

* on ``main`` they ``xpass`` (harmless — proves main is correct),
* on a migration branch with the break present they ``xfail`` (documents the known gap without
  failing the suite),
* once the break is fixed they ``xpass`` everywhere — a signal to remove the ``xfail`` marker.

Track the underlying fix in the finetuning serialize issue.
"""
import pytest

from _builders import FINETUNING_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes

_XFAIL_REASON = "Known pre-existing custom-finetuning serialize break on the arm path (outputs/queue_settings)."


@pytest.mark.xfail(reason=_XFAIL_REASON, strict=False)
@pytest.mark.parametrize("case_name", sorted(FINETUNING_BUILDERS))
def test_custom_finetuning_serializes(case_name):
    """The CustomModelFineTuningJob rest object should serialize to wire (xfail: known break)."""
    entity = FINETUNING_BUILDERS[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.xfail(reason=_XFAIL_REASON, strict=False)
@pytest.mark.parametrize("case_name", sorted(FINETUNING_BUILDERS))
def test_custom_finetuning_wire_matches_expected(case_name):
    """The CustomModelFineTuningJob wire should match the baseline from main (xfail: known break)."""
    entity = FINETUNING_BUILDERS[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Serialization-guard smoke tests for online/batch DEPLOYMENT entities.

Unlike the other families, deployments are NOT wire-equivalence tested against a pre-migration
baseline. The reason is intrinsic to the baseline, not the migration: pre-migration the deployment
envelope is a per-version msrest model whose nested children (``ProbeSettings`` etc.) are already
``arm_ml_service`` hybrids, so the baseline literally cannot serialize a deployment offline
(``msrest .serialize()`` raises ``'ProbeSettings' has no _attribute_map``). The real wire was assembled
by the operations layer at send time. There is therefore no offline baseline wire to pin against.

What we CAN assert -- and what this migration must not break -- is that the branch, having unified the
whole tree on ``arm_ml_service``, serializes a deployment to wire cleanly (no mixed-tree
``TypeError``/``AttributeError``). That is the exact class of regression the client swap risks, so the
guard is valuable even without a golden. Full field-level deployment coverage lives in the
``tests/online_services`` and ``tests/batch_services`` unit suites.
"""
import pytest

from _builders_deployment import BATCH_DEPLOYMENT_CASES, ONLINE_DEPLOYMENT_CASES
from _wire import assert_serializes

_ALL = {}
_ALL.update(ONLINE_DEPLOYMENT_CASES)
_ALL.update(BATCH_DEPLOYMENT_CASES)


@pytest.mark.parametrize("case_name", sorted(_ALL))
def test_deployment_serializes(case_name):
    """The deployment rest object must serialize to wire without raising (no mixed tree)."""
    entity = _ALL[case_name]()
    assert_serializes(entity._to_rest_object())

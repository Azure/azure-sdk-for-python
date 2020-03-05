# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure_devtools.scenario_tests.base import ReplayableTest

import pytest

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock  # type: ignore

VCR = ReplayableTest.__module__ + ".vcr.VCR"


def test_default_match_configuration():
    """ReplayableTest should default to VCR's default matching configuration"""

    with mock.patch(VCR) as mock_vcr:
        ReplayableTest("__init__")

    assert not any("match_on" in call.kwargs for call in mock_vcr.call_args_list)


@pytest.mark.parametrize("opt_in", (True, False, None))
def test_match_body(opt_in):
    """match_body should control opting in to vcr.py's in-box body matching, and default to False"""

    mock_vcr = mock.Mock(match_on=())
    with mock.patch(VCR, lambda *_, **__: mock_vcr):
        ReplayableTest("__init__", match_body=opt_in)

    assert ("body" in mock_vcr.match_on) == (opt_in == True)


def test_custom_request_matchers():
    """custom request matchers should be registered with vcr.py and added to the default matchers"""

    matcher = mock.Mock(__name__="mock matcher")

    mock_vcr = mock.Mock(match_on=())
    with mock.patch(VCR, lambda *_, **__: mock_vcr):
        ReplayableTest("__init__", custom_request_matchers=[matcher])

    assert mock.call(matcher.__name__, matcher) in mock_vcr.register_matcher.call_args_list
    assert matcher.__name__ in mock_vcr.match_on

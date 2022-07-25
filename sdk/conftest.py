# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import os
import pytest

from devtools_testutils import recorded_test, test_proxy, variable_recorder


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line("markers", "live_test_only: mark test to be a live test only")
    config.addinivalue_line("markers", "playback_test_only: mark test to be a playback test only")


def pytest_runtest_setup(item):
    is_live_only_test_marked = bool([mark for mark in item.iter_markers(name="live_test_only")])
    if is_live_only_test_marked:
        from devtools_testutils import is_live

        if not is_live():
            pytest.skip("live test only")

    is_playback_test_marked = bool([mark for mark in item.iter_markers(name="playback_test_only")])
    if is_playback_test_marked:
        from devtools_testutils import is_live

        if is_live() and os.environ.get("AZURE_SKIP_LIVE_RECORDING", "").lower() == "true":
            pytest.skip("playback test only")


try:
    from azure_devtools.scenario_tests import AbstractPreparer

    @pytest.fixture(scope="session", autouse=True)
    def clean_cached_resources():
        yield
        AbstractPreparer._perform_pending_deletes()


except ImportError:
    pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call) -> None:
    """Captures test exception info and makes it available to other fixtures."""
    # execute all other hooks to obtain the report object
    outcome = yield
    result = outcome.get_result()
    if result.outcome == "failed":
        error = call.excinfo.value
        # set a test_error attribute on the item (available to other fixtures from request.node)
        setattr(item, "test_error", error)

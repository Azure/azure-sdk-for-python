# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Extra sanitization for this package's recordings.

The test-proxy's default sanitizers redact the account-name portion of the
recorded request URI's host (e.g. "voice-live-tip-resource" -> "Sanitized"),
but they don't know about the Foundry project name embedded later in the
path ("/api/projects/{project-name}"). Without an explicit sanitizer for it,
the real project name would leak into the checked-in recording. This
sanitizer redacts that path segment regardless of what happens to the host.
"""
import pytest
from devtools_testutils import add_uri_regex_sanitizer, test_proxy  # noqa: F401  pylint: disable=unused-import


@pytest.fixture(scope="session", autouse=True)
def add_project_name_sanitizer(test_proxy):  # pylint: disable=redefined-outer-name
    add_uri_regex_sanitizer(regex=r"/api/projects/[^/?]+", value="/api/projects/sanitized-project")

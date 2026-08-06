# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from devtools_testutils import test_proxy  # noqa: F401  pylint: disable=unused-import


@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):  # pylint: disable=redefined-outer-name
    """Starts the test proxy server for the whole test session.

    See https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md
    """
    return

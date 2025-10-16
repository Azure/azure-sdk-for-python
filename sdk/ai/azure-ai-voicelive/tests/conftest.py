"""
Pytest configuration for Azure AI Voice Live SDK tests.
"""

import pytest
import os
import base64
from devtools_testutils import test_proxy, is_live

from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return

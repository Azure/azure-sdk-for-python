"""
Pytest configuration for Azure AI Voice Live SDK tests.
"""

import pytest
import os
import base64
from devtools_testutils import (
    test_proxy,
)

from pathlib import Path

@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parent / "data"

@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return

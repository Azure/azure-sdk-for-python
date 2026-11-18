# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
import pytest


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers():
    """Override the service fixture: these unit tests use only mocked transports."""

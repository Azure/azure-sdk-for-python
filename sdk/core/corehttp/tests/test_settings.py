# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for the global settings."""
from unittest import mock

import pytest

from corehttp.settings import Settings, settings, _convert_bool


def test_global_settings_default():
    assert settings.tracing_enabled is False


def test_global_settings_set():
    settings.tracing_enabled = True
    assert settings.tracing_enabled is True

    settings.tracing_enabled = False
    assert settings.tracing_enabled is False


def test_environment_settings():
    with mock.patch.dict("os.environ", {"SDK_TRACING_ENABLED": "True"}):
        test_settings = Settings()
        assert test_settings.tracing_enabled is True

    with mock.patch.dict("os.environ", {"SDK_TRACING_ENABLED": "False"}):
        test_settings = Settings()
        assert test_settings.tracing_enabled is False


@pytest.mark.parametrize("value", ["Yes", "YES", "yes", "1", "ON", "on", "true", "True", True])
def test_convert_bool(value):
    assert _convert_bool(value)


@pytest.mark.parametrize("value", ["No", "NO", "no", "0", "OFF", "off", "false", "False", False])
def test_convert_bool_false(value):
    assert not _convert_bool(value)

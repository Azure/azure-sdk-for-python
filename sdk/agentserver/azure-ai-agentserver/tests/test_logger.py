# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the _logger module."""
import logging
import pytest


def test_invalid_log_level_raises(monkeypatch):
    """An invalid AGENT_LOG_LEVEL value raises ValueError."""
    monkeypatch.setenv("AGENT_LOG_LEVEL", "BOGUS")
    from azure.ai.agentserver._logger import get_logger

    with pytest.raises(ValueError, match="AGENT_LOG_LEVEL"):
        get_logger()


def test_valid_log_level_is_applied(monkeypatch):
    """A valid AGENT_LOG_LEVEL is respected."""
    monkeypatch.setenv("AGENT_LOG_LEVEL", "debug")
    from azure.ai.agentserver._logger import get_logger

    logger = get_logger()
    assert logger.level == logging.DEBUG

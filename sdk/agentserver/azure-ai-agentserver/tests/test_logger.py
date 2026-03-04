# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the _logger module."""
import logging


def test_invalid_log_level_falls_back_to_warning(monkeypatch):
    """An invalid AGENT_LOG_LEVEL value falls back to WARNING."""
    monkeypatch.setenv("AGENT_LOG_LEVEL", "BOGUS")
    # Re-import to pick up the monkeypatched env
    from azure.ai.agentserver._logger import get_logger

    logger = get_logger()
    assert logger.level == logging.WARNING


def test_valid_log_level_is_applied(monkeypatch):
    """A valid AGENT_LOG_LEVEL is respected."""
    monkeypatch.setenv("AGENT_LOG_LEVEL", "debug")
    from azure.ai.agentserver._logger import get_logger

    logger = get_logger()
    assert logger.level == logging.DEBUG

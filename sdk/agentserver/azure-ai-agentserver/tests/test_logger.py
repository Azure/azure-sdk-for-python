# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the library-scoped logger."""
import logging


def test_library_logger_exists():
    """The azure.ai.agentserver logger is a standard named logger."""
    lib_logger = logging.getLogger("azure.ai.agentserver")
    assert lib_logger.name == "azure.ai.agentserver"


def test_log_level_preserved_across_imports():
    """Importing the server module does not reset a level already set."""
    lib_logger = logging.getLogger("azure.ai.agentserver")
    lib_logger.setLevel(logging.ERROR)

    # Re-importing the base module should not override the level.
    from azure.ai.agentserver.server import _base  # noqa: F401

    assert lib_logger.level == logging.ERROR

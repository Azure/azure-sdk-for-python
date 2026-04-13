# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the library-scoped logger."""
import logging


def test_library_logger_exists() -> None:
    """The library logger uses the expected dotted name."""
    lib_logger = logging.getLogger("azure.ai.agentserver")
    assert lib_logger.name == "azure.ai.agentserver"


def test_log_level_preserved_across_imports() -> None:
    """Importing internal modules does not reset the log level set by user code."""
    lib_logger = logging.getLogger("azure.ai.agentserver")
    lib_logger.setLevel(logging.ERROR)
    from azure.ai.agentserver.core import _base  # noqa: F401
    assert lib_logger.level == logging.ERROR

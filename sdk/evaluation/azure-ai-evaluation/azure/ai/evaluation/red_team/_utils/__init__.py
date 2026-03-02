# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Utility modules for Red Team Agent.

This package provides centralized utilities for retry logic, file operations,
progress tracking, and exception handling used across red team components.
"""

from .retry_utils import (
    RetryManager,
    create_standard_retry_manager,
    create_retry_decorator,
)
from .file_utils import FileManager, create_file_manager
from .progress_utils import ProgressManager, create_progress_manager
from .exception_utils import (
    ExceptionHandler,
    RedTeamError,
    ErrorCategory,
    ErrorSeverity,
    create_exception_handler,
    exception_context,
)

__all__ = [
    "RetryManager",
    "create_standard_retry_manager",
    "create_retry_decorator",
    "FileManager",
    "create_file_manager",
    "ProgressManager",
    "create_progress_manager",
    "ExceptionHandler",
    "RedTeamError",
    "ErrorCategory",
    "ErrorSeverity",
    "create_exception_handler",
    "exception_context",
]

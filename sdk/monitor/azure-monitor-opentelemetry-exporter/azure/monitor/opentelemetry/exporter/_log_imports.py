# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Centralized imports for OpenTelemetry log SDK types.

The OpenTelemetry log SDK (``opentelemetry.sdk._logs``) is an internal module
whose public surface has changed across releases.  This module provides a
single place to handle version-aware fallback imports so that individual
modules don't each need their own try/except blocks.

When an import fails a warning is emitted instead of failing silently.
"""

import logging

_logger = logging.getLogger(__name__)

# The canonical (>=1.39) names live in opentelemetry.sdk._logs.
try:
    from opentelemetry.sdk._logs import (  # noqa: F401
        LogRecordProcessor,
        ReadWriteLogRecord,
        ReadableLogRecord,
        LoggerProvider,
    )
    from opentelemetry.sdk._logs.export import (  # noqa: F401
        BatchLogRecordProcessor,
        LogRecordExporter,
        LogRecordExportResult,
    )
except ImportError:
    _logger.warning(
        "Failed to import from opentelemetry.sdk._logs. "
        "Ensure opentelemetry-sdk>=1.39 is installed.",
        exc_info=True,
    )
    raise

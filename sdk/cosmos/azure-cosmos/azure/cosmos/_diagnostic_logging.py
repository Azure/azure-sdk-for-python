# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Log the diagnostic summary returned by a native operation, not HTTP traffic."""

from __future__ import annotations

from dataclasses import dataclass, replace
import logging
from typing import Any, Mapping, Optional

from ._backend.contracts import BackendResponse

_LOGGER = logging.getLogger("azure.cosmos.diagnostics")


@dataclass(frozen=True)
class DiagnosticLogging:
    """Immutable client defaults or one call's resolved logging configuration."""

    logger: Optional[logging.Logger] = None
    enable_diagnostics_logging: bool = False
    logging_enable: bool = False

    def for_operation(self, options: Mapping[str, Any]) -> DiagnosticLogging:
        """Resolve per-call overrides without changing the client defaults."""
        if "logger" not in options and "logging_enable" not in options:
            return self
        return replace(
            self,
            logger=options.get("logger", self.logger),
            logging_enable=options.get("logging_enable", self.logging_enable),
        )

    @property
    def level(self) -> Optional[int]:
        """Select one severity, or disable summary logging."""
        # Both switches request the same summary; emit it once at INFO.
        if self.enable_diagnostics_logging:
            return logging.INFO
        if self.logging_enable:
            return logging.DEBUG
        return None

    def record(self, operation: str, response: BackendResponse) -> None:
        """Emit a supplied summary with fields available to Python filters."""
        level = self.level
        logger = self.logger if self.logger is not None else _LOGGER
        if level is None or response.diagnostics is None or not logger.isEnabledFor(level):
            return
        diagnostics = str(response.diagnostics)
        logger.log(
            level,
            "Cosmos %s response status=%s diagnostics=%s",
            operation,
            response.status_code,
            diagnostics,
            extra={
                "operation_type": operation,
                "status_code": response.status_code,
                "sub_status_code": response.sub_status,
                "diagnostics": diagnostics,
            },
        )

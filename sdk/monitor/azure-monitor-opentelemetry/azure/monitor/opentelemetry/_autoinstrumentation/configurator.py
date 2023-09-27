# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------


import logging
from warnings import warn

from opentelemetry.sdk._configuration import _OTelSDKConfigurator

from azure.monitor.opentelemetry._constants import (
    _is_attach_enabled,
    _PREVIEW_ENTRY_POINT_WARNING,
)
from azure.monitor.opentelemetry._diagnostics.diagnostic_logging import (
    AzureDiagnosticLogging,
)

_logger = logging.getLogger(__name__)


class AzureMonitorConfigurator(_OTelSDKConfigurator):
    def _configure(self, **kwargs):
        if not _is_attach_enabled():
            warn(_PREVIEW_ENTRY_POINT_WARNING)
        try:
            AzureDiagnosticLogging.enable(_logger)
            super()._configure(**kwargs)
        except ValueError as e:
            _logger.error(
                "Azure Monitor Configurator failed during configuration due to a ValueError: %s", e
            )
            raise e
        except Exception as e:
            _logger.error(
                "Azure Monitor Configurator failed during configuration: %s", e
            )
            raise e

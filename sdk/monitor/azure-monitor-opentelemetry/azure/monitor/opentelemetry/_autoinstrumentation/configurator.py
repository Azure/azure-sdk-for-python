# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------


from warnings import warn

from opentelemetry.sdk._configuration import _OTelSDKConfigurator

from azure.monitor.opentelemetry.exporter._utils import _is_attach_enabled # pylint: disable=import-error,no-name-in-module
from azure.monitor.opentelemetry._constants import _PREVIEW_ENTRY_POINT_WARNING
from azure.monitor.opentelemetry._diagnostics.diagnostic_logging import (
    AzureDiagnosticLogging,
    _ATTACH_FAILURE_CONFIGURATOR,
    _ATTACH_SUCCESS_CONFIGURATOR,
)
from azure.monitor.opentelemetry._diagnostics.status_logger import (
    AzureStatusLogger,
)


class AzureMonitorConfigurator(_OTelSDKConfigurator):
    def _configure(self, **kwargs):
        if not _is_attach_enabled():
            warn(_PREVIEW_ENTRY_POINT_WARNING)
        try:
            super()._configure(**kwargs)
            AzureStatusLogger.log_status(True)
            AzureDiagnosticLogging.info(
                "Azure Monitor Configurator configured successfully.",
                _ATTACH_SUCCESS_CONFIGURATOR
            )
        except Exception as e:
            AzureDiagnosticLogging.error(
                "Azure Monitor Configurator failed during configuration: %s" % str(e),
                _ATTACH_FAILURE_CONFIGURATOR,
            )
            raise e

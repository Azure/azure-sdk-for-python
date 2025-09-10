# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
from typing import Any, Dict, Optional

from opentelemetry.sdk.resources import Resource

from azure.monitor.opentelemetry.exporter._quickpulse._manager import _QuickpulseManager
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    set_statsbeat_live_metrics_feature_set,
)
from azure.monitor.opentelemetry.exporter._configuration import _ConfigurationManager

_logger = logging.getLogger(__name__)


def enable_live_metrics(**kwargs: Any) -> None:  # pylint: disable=C4758
    """Live metrics entry point.

    Expected keyword arguments:
    :param connection_string: The connection string used for your Application Insights resource.
        This parameter configures the Azure Monitor endpoint for telemetry submission.
    :type connection_string: Optional[str]
    :param credential: Token credential, such as ManagedIdentityCredential or
        ClientSecretCredential, used for Azure Active Directory (AAD) authentication. 
        Used as an alternative to connection string authentication. Defaults to None.
    :type credential: Optional[Any]
    :param resource: The OpenTelemetry Resource used for this Python application.
        Contains application metadata (service name, version, environment, etc.).
        This is the primary parameter used by the underlying _QuickpulseExporter
        for application identification and telemetry enrichment.
    :type resource: Optional[Resource]
    :rtype: None
    """
    manager = _QuickpulseManager(**kwargs)
    initialized = manager.initialize()
    if initialized:
        # Register the callback that will be invoked on configuration changes
        _ConfigurationManager().register_callback(get_quickpulse_configuration_callback)
        
    # We can detect feature usage for statsbeat since we are in an opt-in model currently
    # Once we move to live metrics on-by-default, we will have to check for both explicit usage
    # and whether or not user is actually using live metrics (being on live metrics blade in UX)
    set_statsbeat_live_metrics_feature_set()


def get_quickpulse_configuration_callback(settings: Dict[str, str]) -> None:
    """Callback function invoked when configuration changes.
    
    This function handles dynamic enabling/disabling of live metrics based on configuration.
    
    :param settings: Configuration settings from onesettings
    :type settings: Dict[str, str]
    """
    manager = _QuickpulseManager()
    
    # Check if live metrics should be enabled based on configuration
    live_metrics_enabled = _should_enable_live_metrics(settings)
    
    if live_metrics_enabled and not manager.is_initialized():
        # Enable live metrics if it's not currently enabled
        _logger.info("Enabling live metrics based on configuration.")
        # Initialize using the configuration stored in the manager
        manager.initialize()
    elif not live_metrics_enabled and manager.is_initialized():
        # Disable live metrics if it's currently enabled
        _logger.info("Disabling live metrics based on configuration.")
        manager.shutdown()


def _should_enable_live_metrics(settings: Dict[str, str]) -> bool:
    """Determine if live metrics should be enabled based on configuration settings.
    
    :param settings: Configuration settings from onesettings
    :type settings: Dict[str, str]
    :return: True if live metrics should be enabled, False otherwise
    :rtype: bool
    """
    # Check for live metrics configuration settings
    # This could be based on various configuration keys
    live_metrics_setting = settings.get("LIVE_METRICS_ENABLED")
    if live_metrics_setting is not None:
        return live_metrics_setting.lower() in ("true", "1", "yes", "on")
    
    # Default behavior - could be based on other settings or always enabled
    # For now, default to enabled unless explicitly disabled
    return True


def shutdown_live_metrics() -> bool:
    """Shutdown live metrics.
    
    :return: True if shutdown was successful, False otherwise
    :rtype: bool
    """
    return _QuickpulseManager().shutdown()

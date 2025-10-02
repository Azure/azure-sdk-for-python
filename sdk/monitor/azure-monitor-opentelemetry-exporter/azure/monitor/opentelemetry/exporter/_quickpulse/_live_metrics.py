# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
from typing import Any, Dict

from azure.monitor.opentelemetry.exporter._quickpulse._state import get_quickpulse_manager
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    set_statsbeat_live_metrics_feature_set,
)
from azure.monitor.opentelemetry.exporter._configuration._state import get_configuration_manager
from azure.monitor.opentelemetry.exporter._configuration._utils import evaluate_feature
from azure.monitor.opentelemetry.exporter._constants import _ONE_SETTINGS_FEATURE_LIVE_METRICS

_logger = logging.getLogger(__name__)


# pylint:disable=docstring-should-be-keyword
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
    :return: None
    :rtype: None
    """
    manager = get_quickpulse_manager()
    initialized = manager.initialize(**kwargs)
    if initialized:
        # Register the callback that will be invoked on configuration changes
        # Will only be added if QuickpulseManager is initialized successfully
        # Is a NoOp if _ConfigurationManager not initialized
        config_manager = get_configuration_manager()
        # config_manager would be `None` if control plane is disabled
        if config_manager:
            config_manager.register_callback(get_quickpulse_configuration_callback)

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
    manager = get_quickpulse_manager()

    # Check if live metrics should be enabled based on configuration
    live_metrics_enabled = evaluate_feature(
        _ONE_SETTINGS_FEATURE_LIVE_METRICS,
        settings
    )

    if live_metrics_enabled and not manager.is_initialized():
        # Enable live metrics if it's not currently enabled
        # This should be a re-initialization with previous parameters
        if manager._connection_string:  # pylint:disable=protected-access
            manager.initialize(
                connection_string=manager._connection_string,  # pylint:disable=protected-access
                credential=manager._credential,  # pylint:disable=protected-access
                resource=manager._resource  # pylint:disable=protected-access
            )
    elif live_metrics_enabled is False and manager.is_initialized():
        # Disable live metrics if it's currently enabled
        manager.shutdown()


def shutdown_live_metrics() -> bool:
    """Shutdown live metrics.

    :return: True if shutdown was successful, False otherwise
    :rtype: bool
    """
    manager = get_quickpulse_manager()
    return manager.shutdown()

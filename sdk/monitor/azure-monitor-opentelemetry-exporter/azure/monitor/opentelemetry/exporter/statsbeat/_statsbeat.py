# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
from typing import Dict, TYPE_CHECKING

from azure.monitor.opentelemetry.exporter.statsbeat._manager import (
    StatsbeatConfig,
)
from azure.monitor.opentelemetry.exporter.statsbeat._state import get_statsbeat_manager
from azure.monitor.opentelemetry.exporter._configuration._state import get_configuration_manager
from azure.monitor.opentelemetry.exporter._configuration._utils import evaluate_feature
from azure.monitor.opentelemetry.exporter._constants import _ONE_SETTINGS_FEATURE_SDK_STATS
from azure.monitor.opentelemetry.exporter.statsbeat._utils import _sdkstats_debug

if TYPE_CHECKING:
    from azure.monitor.opentelemetry.exporter.export._base import BaseExporter


logger = logging.getLogger(__name__)


# pyright: ignore
def collect_statsbeat_metrics(exporter: "BaseExporter") -> None:  # pyright: ignore
    _sdkstats_debug("collection initialization requested")
    config = StatsbeatConfig.from_exporter(exporter)
    if config:
        manager = get_statsbeat_manager()
        initialized = manager.initialize(config)
        _sdkstats_debug(f"collection initialization result={initialized}")
        if initialized:
            # Register the callback that will be invoked on configuration changes to statsbeat
            # Is a NoOp if _ConfigurationManager not initialized
            config_manager = get_configuration_manager()
            # config_manager would be `None` if control plane is disabled
            if config_manager:
                config_manager.register_callback(get_statsbeat_configuration_callback)
                _sdkstats_debug("OneSettings callback registration result=registered")
            else:
                _sdkstats_debug("OneSettings callback registration result=control-plane-disabled")


def get_statsbeat_configuration_callback(settings: Dict[str, str]):
    """Callback function invoked when configuration changes.

    This function handles dynamic enabling/disabling of statbeat based on configuration.
    Also updates statsbeat config if ingestion endpoint changes.

    :param settings: Configuration settings from onesettings
    :type settings: Dict[str, str]
    """
    from azure.monitor.opentelemetry.exporter._constants import (
        _ONE_SETTINGS_DEFAULT_STATS_CONNECTION_STRING_KEY,
    )
    settings[_ONE_SETTINGS_DEFAULT_STATS_CONNECTION_STRING_KEY] = "InstrumentationKey=00000000-0000-0000-0000-000000000000;IngestionEndpoint=https://tst-data.stats.monitor.azure.com/"

    manager = get_statsbeat_manager()

    # Check if SDK stats should be enabled based on configuration
    sdk_stats_enabled = evaluate_feature(_ONE_SETTINGS_FEATURE_SDK_STATS, settings)
    _sdkstats_debug(
        f"OneSettings callback setting_count={len(settings)} sdk_stats_enabled={sdk_stats_enabled}"
    )
    if sdk_stats_enabled is False:
        # Only an explicit OneSettings disable overrides the built-in enabled default.
        _sdkstats_debug("OneSettings action=shutdown")
        manager.shutdown()
        return

    current_config = manager.get_current_config()
    # Since config is preserved between shutdowns,
    # It will only be None if never initialized
    if not current_config:
        _sdkstats_debug("OneSettings update skipped reason=manager-not-initialized")
        return
    # Get updated config from settings. Missing or invalid connection string configuration falls back
    # to the current built-in Breeze connection string in StatsbeatConfig.from_config.
    updated_config = StatsbeatConfig.from_config(current_config, settings)
    if updated_config:
        initialized = manager.initialize(updated_config)
        _sdkstats_debug(f"OneSettings update result={initialized}")
    else:
        _sdkstats_debug("OneSettings update skipped reason=no-valid-config")


def shutdown_statsbeat_metrics() -> bool:
    return get_statsbeat_manager().shutdown()

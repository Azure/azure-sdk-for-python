# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
from functools import partial
from typing import Dict, TYPE_CHECKING

from azure.monitor.opentelemetry.exporter.statsbeat._manager import (
    StatsbeatConfig,
)
from azure.monitor.opentelemetry.exporter.statsbeat._state import get_statsbeat_manager
from azure.monitor.opentelemetry.exporter._configuration._state import get_configuration_manager
from azure.monitor.opentelemetry.exporter._configuration._utils import evaluate_feature
from azure.monitor.opentelemetry.exporter._constants import _ONE_SETTINGS_FEATURE_SDK_STATS

if TYPE_CHECKING:
    from azure.monitor.opentelemetry.exporter.export._base import BaseExporter


logger = logging.getLogger(__name__)


# pyright: ignore
def collect_statsbeat_metrics(exporter: "BaseExporter") -> None:  # pyright: ignore
    config = StatsbeatConfig.from_exporter(exporter)
    if config:
        config_manager = get_configuration_manager()
        if config_manager and config_manager.is_initialized():
            config_manager.register_callback(get_statsbeat_configuration_callback)
            config_manager.register_initial_configuration_callback(
                partial(_initialize_statsbeat_from_initial_configuration, config)
            )
        else:
            get_statsbeat_manager().initialize(config)


def _initialize_statsbeat_from_initial_configuration(
    base_config: StatsbeatConfig, settings: Dict[str, str]
) -> None:
    """Initialize SDK Stats after the first OneSettings request attempt."""
    manager = get_statsbeat_manager()
    if settings:
        sdk_stats_enabled = evaluate_feature(_ONE_SETTINGS_FEATURE_SDK_STATS, settings)
        if sdk_stats_enabled is False:
            return
        config = StatsbeatConfig.from_config(base_config, settings)
    else:
        config = base_config

    if config:
        manager.initialize(config)


def get_statsbeat_configuration_callback(settings: Dict[str, str]):
    """Callback function invoked when configuration changes.

    This function handles dynamic enabling/disabling of statbeat based on configuration.
    Also updates statsbeat config if ingestion endpoint changes.

    :param settings: Configuration settings from onesettings
    :type settings: Dict[str, str]
    """
    manager = get_statsbeat_manager()

    # Check if SDK stats should be enabled based on configuration
    sdk_stats_enabled = evaluate_feature(_ONE_SETTINGS_FEATURE_SDK_STATS, settings)
    if sdk_stats_enabled is False:
        # Only an explicit OneSettings disable overrides the built-in enabled default.
        manager.shutdown()
        return

    current_config = manager.get_current_config()
    # Since config is preserved between shutdowns,
    # It will only be None if never initialized
    if not current_config:
        return
    # Get updated config from settings. Missing or invalid connection string configuration falls back
    # to the current built-in Breeze connection string in StatsbeatConfig.from_config.
    updated_config = StatsbeatConfig.from_config(current_config, settings)
    if updated_config:
        manager.initialize(updated_config)


def shutdown_statsbeat_metrics() -> bool:
    return get_statsbeat_manager().shutdown()

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
from typing import Dict
from azure.monitor.opentelemetry.exporter.statsbeat._manager import (
    StatsbeatConfig,
    StatsbeatManager,
)
from azure.monitor.opentelemetry.exporter._configuration import _ConfigurationManager

logger = logging.getLogger(__name__)

def collect_statsbeat_metrics(exporter) -> None:  # pyright: ignore
    config = StatsbeatConfig.from_exporter(exporter)
    if config:
        initialized = StatsbeatManager().initialize(config)
        if initialized:
            # Register the callback that will be invoked on configuration changes to statsbeat
            _ConfigurationManager().register_callback(get_statsbeat_configuration_callback)

def get_statsbeat_configuration_callback(settings: Dict[str, str]):
    current_config = StatsbeatManager().get_current_config()
    if not current_config:
        logger.warning("Statsbeat is not initialized. Ignoring configuration update.")
        return

    # Get updated config from settings
    updated_config = StatsbeatConfig.from_config(current_config, settings)
    if updated_config:
        StatsbeatManager().initialize(updated_config)


def shutdown_statsbeat_metrics() -> bool:
    return StatsbeatManager().shutdown()

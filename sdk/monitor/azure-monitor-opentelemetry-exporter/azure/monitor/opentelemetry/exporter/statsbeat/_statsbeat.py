# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from azure.monitor.opentelemetry.exporter.statsbeat._manager import (
    StatsbeatConfig,
    StatsbeatManager,
)


def collect_statsbeat_metrics(exporter) -> None:  # pyright: ignore
    config = StatsbeatConfig.from_exporter(exporter)
    StatsbeatManager().initialize(config)


def shutdown_statsbeat_metrics() -> bool:
    return StatsbeatManager().shutdown()

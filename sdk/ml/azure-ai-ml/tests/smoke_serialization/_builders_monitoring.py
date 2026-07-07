# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builders for monitoring (MonitorSchedule) entities.

Each builder loads one of the committed monitoring YAML configs via ``load_schedule`` and returns
the resulting ``MonitorSchedule`` entity. The smoke harness then calls ``_to_rest_object()`` and
asserts the serialized wire body is byte-identical to the captured baseline. These configs exercise
every monitor signal type (data drift, data quality, prediction drift, feature attribution,
model performance, custom, generation safety/quality, generation token statistics, out-of-the-box).
"""
import os

from azure.ai.ml.entities._load_functions import load_schedule

# Monitoring YAML configs live under tests/test_configs/monitoring/yaml_configs. Resolve relative to
# this file (tests/smoke_serialization/) so the suite is cwd-independent.
_CONFIG_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "test_configs", "monitoring", "yaml_configs")
)


def _load(config_name):
    """Load a MonitorSchedule entity from a committed monitoring YAML config.

    :param config_name: The YAML file name (e.g. ``"data_drift.yaml"``).
    :return: The loaded MonitorSchedule entity.
    :rtype: ~azure.ai.ml.entities.MonitorSchedule
    """
    return load_schedule(os.path.join(_CONFIG_DIR, config_name))


def build_monitor_data_drift():
    """MonitorSchedule with a data-drift signal and recurrence trigger."""
    return _load("data_drift.yaml")


def build_monitor_data_quality():
    """MonitorSchedule with a data-quality signal."""
    return _load("data_quality.yaml")


def build_monitor_prediction_drift():
    """MonitorSchedule with a prediction-drift signal."""
    return _load("prediction_drift.yaml")


def build_monitor_feature_attribution_drift():
    """MonitorSchedule with a feature-attribution-drift signal."""
    return _load("feature_attribution_drift.yaml")


def build_monitor_model_performance():
    """MonitorSchedule with a model-performance signal."""
    return _load("model_performance.yaml")


def build_monitor_custom():
    """MonitorSchedule with a custom monitoring signal."""
    return _load("custom.yaml")


def build_monitor_generation_safety():
    """MonitorSchedule with a generation-safety-quality signal."""
    return _load("generation_safety.yaml")


def build_monitor_generation_token_statistics():
    """MonitorSchedule with a generation-token-statistics signal."""
    return _load("generation_token_statistics.yaml")


def build_monitor_out_of_the_box():
    """MonitorSchedule with an out-of-the-box monitor definition.

    EXCLUDED from the suite: a monitor with no explicit signals hits a pre-existing
    ``UnboundLocalError: local variable '_signals' referenced before assignment`` in
    ``MonitorDefinition._to_rest_object`` (reproduces on pre-migration code, unrelated to the
    client migration). Cover it once the no-signals path is fixed.
    """
    return _load("out_of_the_box.yaml")


def build_monitor_no_target_baseline_data():
    """MonitorSchedule without target/baseline data."""
    return _load("no_target_baseline_data.yaml")


MONITORING_BUILDERS = {
    "monitor_data_drift": build_monitor_data_drift,
    "monitor_data_quality": build_monitor_data_quality,
    "monitor_prediction_drift": build_monitor_prediction_drift,
    "monitor_feature_attribution_drift": build_monitor_feature_attribution_drift,
    "monitor_model_performance": build_monitor_model_performance,
    "monitor_custom": build_monitor_custom,
    "monitor_generation_safety": build_monitor_generation_safety,
    "monitor_generation_token_statistics": build_monitor_generation_token_statistics,
    "monitor_no_target_baseline_data": build_monitor_no_target_baseline_data,
}

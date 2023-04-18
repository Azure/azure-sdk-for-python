import json

import pytest

from azure.ai.ml.entities._load_functions import load_schedule
from azure.ai.ml._restclient.v2023_04_01_preview.models import Schedule as RestSchedule


@pytest.mark.unittest
class TestMonitorSchedule:
    def test_data_drift_basic(self) -> None:
        json_path = "tests/test_configs/monitoring/rest_json_configs/data_drift_rest.json"
        yaml_path = "tests/test_configs/monitoring/yaml_configs/data_drift.yaml"

        with open(json_path, "r") as f:
            loaded_json = json.load(f)

        deserialized_schedule = RestSchedule.deserialize(loaded_json)

        monitor_schedule = load_schedule(yaml_path)

        assert monitor_schedule._to_rest_object().as_dict() == deserialized_schedule.as_dict()

    def test_prediction_drift_basic(self) -> None:
        json_path = "tests/test_configs/monitoring/rest_json_configs/prediction_drift_rest.json"
        yaml_path = "tests/test_configs/monitoring/yaml_configs/prediction_drift.yaml"

        with open(json_path, "r") as f:
            loaded_json = json.load(f)

        deserialized_schedule = RestSchedule.deserialize(loaded_json)

        monitor_schedule = load_schedule(yaml_path)

        assert monitor_schedule._to_rest_object().as_dict() == deserialized_schedule.as_dict()

    def test_data_quality_basic(self) -> None:
        json_path = "tests/test_configs/monitoring/rest_json_configs/data_quality_rest.json"
        yaml_path = "tests/test_configs/monitoring/yaml_configs/data_quality.yaml"

        with open(json_path, "r") as f:
            loaded_json = json.load(f)

        deserialized_schedule = RestSchedule.deserialize(loaded_json)

        monitor_schedule = load_schedule(yaml_path)

        assert monitor_schedule._to_rest_object().as_dict() == deserialized_schedule.as_dict()

    def test_feature_attribution_drift_basic(self) -> None:
        json_path = "tests/test_configs/monitoring/rest_json_configs/feature_attribution_drift_rest.json"
        yaml_path = "tests/test_configs/monitoring/yaml_configs/feature_attribution_drift.yaml"

        with open(json_path, "r") as f:
            loaded_json = json.load(f)

        deserialized_schedule = RestSchedule.deserialize(loaded_json)

        monitor_schedule = load_schedule(yaml_path)

        assert monitor_schedule._to_rest_object().as_dict() == deserialized_schedule.as_dict()

    def test_custom_basic(self) -> None:
        json_path = "tests/test_configs/monitoring/rest_json_configs/custom_rest.json"
        yaml_path = "tests/test_configs/monitoring/yaml_configs/custom.yaml"

        with open(json_path, "r") as f:
            loaded_json = json.load(f)

        deserialized_schedule = RestSchedule.deserialize(loaded_json)

        monitor_schedule = load_schedule(yaml_path)

        assert monitor_schedule._to_rest_object().as_dict() == deserialized_schedule.as_dict()


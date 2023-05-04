import json

import yaml
import pytest

from azure.ai.ml.entities._schedule.schedule import Schedule
from azure.ai.ml.entities._load_functions import load_schedule
from azure.ai.ml._restclient.v2023_04_01_preview.models import Schedule as RestSchedule


def validate_to_from_rest_translation(json_path: str, yaml_path: str) -> None:
    with open(json_path, "r") as f:
        loaded_json = json.load(f)

    deserialized_schedule = RestSchedule.deserialize(loaded_json)

    monitor_schedule = load_schedule(yaml_path)

    assert monitor_schedule._to_rest_object().as_dict() == deserialized_schedule.as_dict()

    with open(yaml_path, "r") as f:
        yaml_dict = yaml.safe_load(f)

    yaml_dict.pop("name", None)
    assert json.loads(json.dumps(yaml_dict)) == json.loads(
        json.dumps(Schedule._from_rest_object(deserialized_schedule)._to_dict())
    )


@pytest.mark.unittest
class TestMonitorSchedule:
    def test_data_drift_basic(self) -> None:
        json_path = "tests/test_configs/monitoring/rest_json_configs/data_drift_rest.json"
        yaml_path = "tests/test_configs/monitoring/yaml_configs/data_drift.yaml"

        validate_to_from_rest_translation(json_path, yaml_path)

    def test_prediction_drift_basic(self) -> None:
        json_path = "tests/test_configs/monitoring/rest_json_configs/prediction_drift_rest.json"
        yaml_path = "tests/test_configs/monitoring/yaml_configs/prediction_drift.yaml"

        validate_to_from_rest_translation(json_path, yaml_path)

    def test_data_quality_basic(self) -> None:
        json_path = "tests/test_configs/monitoring/rest_json_configs/data_quality_rest.json"
        yaml_path = "tests/test_configs/monitoring/yaml_configs/data_quality.yaml"

        validate_to_from_rest_translation(json_path, yaml_path)

    def test_feature_attribution_drift_basic(self) -> None:
        json_path = "tests/test_configs/monitoring/rest_json_configs/feature_attribution_drift_rest.json"
        yaml_path = "tests/test_configs/monitoring/yaml_configs/feature_attribution_drift.yaml"

        validate_to_from_rest_translation(json_path, yaml_path)

    @pytest.mark.skip(reason="model performance not supported in PuP")
    def test_model_performance_basic(self) -> None:
        json_path = "tests/test_configs/monitoring/rest_json_configs/model_performance_rest.json"
        yaml_path = "tests/test_configs/monitoring/yaml_configs/model_performance.yaml"

        validate_to_from_rest_translation(json_path, yaml_path)

    def test_custom_basic(self) -> None:
        json_path = "tests/test_configs/monitoring/rest_json_configs/custom_rest.json"
        yaml_path = "tests/test_configs/monitoring/yaml_configs/custom.yaml"

        validate_to_from_rest_translation(json_path, yaml_path)

import json

import pytest

from azure.ai.ml.entities._load_functions import load_schedule
from azure.ai.ml._restclient.v2023_04_01_preview.models import Schedule


@pytest.mark.unittest
class TestMonitorSchedule:
    def test_data_drift_basic(self) -> None:
        json_path = "tests/test_configs/monitoring/data_drift_rest.json"
        yaml_path = "tests/test_configs/monitoring/data_drift.yaml"

        with open(json_path, "r") as f:
            loaded_json = json.load(f)

        deserialized_schedule = Schedule.deserialize(loaded_json)

        monitor_schedule = load_schedule(yaml_path)

        assert monitor_schedule._to_rest_object().as_dict() == deserialized_schedule.as_dict()


from typing import Callable

from devtools_testutils import AzureRecordedTestCase
import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.entities._load_functions import load_schedule
from azure.ai.ml.entities._monitoring.schedule import MonitorSchedule
from azure.ai.ml._utils._arm_id_utils import is_ARM_id_for_resource


@pytest.mark.timeout(600)
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.core_sdk_test
class TestMonitorSchedule(AzureRecordedTestCase):
    def test_data_drift_schedule_create(
        self, client: MLClient, data_with_2_versions: str, randstr: Callable[[str], str]
    ):
        test_path = "tests/test_configs/monitoring/yaml_configs/data_drift.yaml"

        schedule_name = randstr("schedule_name")

        params_override = [
            {"name": schedule_name},
            {
                "create_monitor.monitoring_signals.testSignal.target_dataset.dataset.input_dataset.path": f"azureml:{data_with_2_versions}:1"
            },
            {"create_monitor.monitoring_signals.testSignal.target_dataset.dataset.input_dataset.type": "uri_folder"},
            {
                "create_monitor.monitoring_signals.testSignal.baseline_dataset.input_dataset.path": f"azureml:{data_with_2_versions}:2"
            },
            {"create_monitor.monitoring_signals.testSignal.baseline_dataset.input_dataset.type": "uri_folder"},
        ]

        schedule = load_schedule(test_path, params_override=params_override)
        # not testing monitoring target expansion right now
        schedule.create_monitor.monitoring_target = None
        # bug in service when deserializing lookback_period is not supported yet
        schedule.create_monitor.monitoring_signals["testSignal"].target_dataset.lookback_period = None

        created_schedule = client.schedules.begin_create_or_update(schedule).result()

        # test ARM id resolution
        assert isinstance(created_schedule, MonitorSchedule)
        assert is_ARM_id_for_resource(created_schedule.create_monitor.compute, AzureMLResourceType.COMPUTE)

        data_drift_signal = created_schedule.create_monitor.monitoring_signals["testSignal"]
        assert data_drift_signal.target_dataset
        assert is_ARM_id_for_resource(
            data_drift_signal.target_dataset.dataset.input_dataset.path, AzureMLResourceType.DATA
        )
        assert data_drift_signal.baseline_dataset
        assert is_ARM_id_for_resource(data_drift_signal.baseline_dataset.input_dataset.path, AzureMLResourceType.DATA)

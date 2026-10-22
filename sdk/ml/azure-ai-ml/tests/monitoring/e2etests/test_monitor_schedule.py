from typing import Callable, Union

from azure.ai.ml.entities._monitoring.thresholds import NumericalDriftMetrics, CategoricalDriftMetrics

from devtools_testutils import AzureRecordedTestCase, is_live
import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.constants._monitoring import (
    DEFAULT_DATA_QUALITY_SIGNAL_NAME,
    DEFAULT_PREDICTION_DRIFT_SIGNAL_NAME,
    DEFAULT_DATA_DRIFT_SIGNAL_NAME,
    MonitorSignalType,
    MonitorDatasetContext,
    MonitorFeatureType,
    MonitorMetricName,
    DEPLOYMENT_MODEL_INPUTS_NAME_KEY,
    DEPLOYMENT_MODEL_INPUTS_VERSION_KEY,
    DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY,
    DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY,
)
from azure.ai.ml.entities._load_functions import load_schedule
from azure.ai.ml.entities import MonitorSchedule, DataDriftSignal, DataQualitySignal, PredictionDriftSignal
from azure.ai.ml.entities._monitoring.thresholds import (
    DataDriftMetricThreshold,
    DataQualityMetricThreshold,
    PredictionDriftMetricThreshold,
)
from azure.ai.ml._utils._arm_id_utils import (
    is_ARM_id_for_resource,
    is_ARM_id_for_parented_resource,
    AMLVersionedArmId,
)
from azure.ai.ml._utils.utils import snake_to_camel


@pytest.mark.timeout(600)
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.production_experiences_test
class TestMonitorSchedule(AzureRecordedTestCase):
    def test_data_drift_schedule_create(
        self, client: MLClient, data_with_2_versions: str, randstr: Callable[[str], str]
    ):
        test_path = "tests/test_configs/monitoring/yaml_configs/data_drift.yaml"
        created_schedule = create_and_assert_basic_schedule_fields(client, test_path, randstr, data_with_2_versions)

    def test_prediction_drift_schedule_create(
        self, client: MLClient, data_with_2_versions: str, randstr: Callable[[str], str]
    ):
        test_path = "tests/test_configs/monitoring/yaml_configs/prediction_drift.yaml"
        created_schedule = create_and_assert_basic_schedule_fields(client, test_path, randstr, data_with_2_versions)

    def test_data_quality_schedule_create(
        self, client: MLClient, data_with_2_versions: str, randstr: Callable[[str], str]
    ):
        test_path = "tests/test_configs/monitoring/yaml_configs/data_quality.yaml"
        created_schedule = create_and_assert_basic_schedule_fields(client, test_path, randstr, data_with_2_versions)

    @pytest.mark.skipif(
        condition=is_live(), reason="complicated logic, consult SDK team if this needs to be re-recorded"
    )
    @pytest.mark.skip(reason="Endpoint does not exist anymore")
    def test_out_of_box_schedule(self, client: MLClient):
        test_path = "tests/test_configs/monitoring/yaml_configs/out_of_the_box.yaml"
        endpoint_name = "iris-endpoint"
        deployment_name = "my-iris-deployment"
        monitor_schedule = load_schedule(
            test_path,
            params_override=[
                {
                    "create_monitor.monitoring_target.endpoint_deployment_id": f"azureml:{endpoint_name}:{deployment_name}"
                }
            ],
        )
        created_schedule: MonitorSchedule = client.schedules.begin_create_or_update(monitor_schedule).result()

        (
            model_inputs_name,
            model_inputs_version,
            model_outputs_name,
            model_outputs_version,
            model_inputs_type,
            model_outputs_type,
        ) = get_model_inputs_outputs_from_deployment(client, endpoint_name, deployment_name)

        assert is_ARM_id_for_parented_resource(
            created_schedule.create_monitor.monitoring_target.endpoint_deployment_id,
            snake_to_camel(AzureMLResourceType.ONLINE_ENDPOINT),
            AzureMLResourceType.DEPLOYMENT,
        )

        for signal_name in [
            DEFAULT_DATA_DRIFT_SIGNAL_NAME,
            DEFAULT_PREDICTION_DRIFT_SIGNAL_NAME,
            DEFAULT_DATA_QUALITY_SIGNAL_NAME,
        ]:
            assert signal_name in created_schedule.create_monitor.monitoring_signals
            signal = created_schedule.create_monitor.monitoring_signals[signal_name]
            if signal.type == MonitorSignalType.DATA_DRIFT:
                check_default_datasets(signal, model_inputs_name, model_inputs_version, model_inputs_type, True)

                assert signal.metric_thresholds.numerical.normalized_wasserstein_distance == 0.1
                assert signal.metric_thresholds.categorical.jensen_shannon_distance == 0.1
            elif signal.type == MonitorSignalType.PREDICTION_DRIFT:
                check_default_datasets(signal, model_outputs_name, model_outputs_version, model_outputs_type, False)

                assert signal.metric_thresholds.numerical.normalized_wasserstein_distance == 0.1
                assert signal.metric_thresholds.categorical.jensen_shannon_distance == 0.1
            elif signal.type == MonitorSignalType.DATA_QUALITY:
                check_default_datasets(signal, model_inputs_name, model_inputs_version, model_inputs_type, True)

                # service bug clobbering the applicable feature type
                """assert signal.metric_thresholds == [
                    DataQualityMetricThreshold(
                        applicable_feature_type=MonitorFeatureType.NUMERICAL,
                        threshold=0,
                        metric_name=MonitorMetricName.NULL_VALUE_RATE
                    ),
                    DataQualityMetricThreshold(
                        applicable_feature_type=MonitorFeatureType.NUMERICAL,
                        threshold=0,
                        metric_name=MonitorMetricName.DATA_TYPE_ERROR_RATE
                    ),
                    DataQualityMetricThreshold(
                        applicable_feature_type=MonitorFeatureType.NUMERICAL,
                        threshold=0,
                        metric_name=MonitorMetricName.OUT_OF_BOUND_RATE
                    ),
                    DataQualityMetricThreshold(
                        applicable_feature_type=MonitorFeatureType.CATEGORICAL,
                        threshold=0,
                        metric_name=MonitorMetricName.NULL_VALUE_RATE
                    ),
                    DataQualityMetricThreshold(
                        applicable_feature_type=MonitorFeatureType.CATEGORICAL,
                        threshold=0,
                        metric_name=MonitorMetricName.DATA_TYPE_ERROR_RATE
                    ),
                    DataQualityMetricThreshold(
                        applicable_feature_type=MonitorFeatureType.CATEGORICAL,
                        threshold=0,
                        metric_name=MonitorMetricName.OUT_OF_BOUND_RATE
                    ),
                ]"""

    @pytest.mark.skipif(
        condition=is_live(), reason="complicated logic, consult SDK team if this needs to be re-recorded"
    )
    @pytest.mark.skip(reason="Endpoint does not exist anymore")
    def test_default_target_baseline_dataset(self, client: MLClient):
        test_path = "tests/test_configs/monitoring/yaml_configs/no_target_baseline_data.yaml"
        endpoint_name = "iris-endpoint"
        deployment_name = "my-iris-deployment"
        monitor_schedule = load_schedule(
            test_path,
            params_override=[
                {
                    "create_monitor.monitoring_target.endpoint_deployment_id": f"azureml:{endpoint_name}:{deployment_name}"
                }
            ],
        )
        created_schedule: MonitorSchedule = client.schedules.begin_create_or_update(monitor_schedule).result()

        (
            model_inputs_name,
            model_inputs_version,
            model_outputs_name,
            model_outputs_version,
            model_inputs_type,
            model_outputs_type,
        ) = get_model_inputs_outputs_from_deployment(client, endpoint_name, deployment_name)

        for signal_name in [
            DEFAULT_DATA_DRIFT_SIGNAL_NAME,
            DEFAULT_DATA_QUALITY_SIGNAL_NAME,
            DEFAULT_PREDICTION_DRIFT_SIGNAL_NAME,
        ]:
            assert signal_name in created_schedule.create_monitor.monitoring_signals
            signal = created_schedule.create_monitor.monitoring_signals[signal_name]
            if signal.type == MonitorSignalType.DATA_DRIFT:
                check_default_datasets(signal, model_inputs_name, model_inputs_version, model_inputs_type, True)
            elif signal.type == MonitorSignalType.PREDICTION_DRIFT:
                check_default_datasets(signal, model_outputs_name, model_outputs_version, model_outputs_type, False)
            elif signal.type == MonitorSignalType.DATA_QUALITY:
                check_default_datasets(signal, model_inputs_name, model_inputs_version, model_inputs_type, True)


def get_model_inputs_outputs_from_deployment(client: MLClient, endpoint_name: str, deployment_name: str):
    online_deployment = client.online_deployments.get(deployment_name, endpoint_name)

    model_inputs_name = online_deployment.tags.get(DEPLOYMENT_MODEL_INPUTS_NAME_KEY)
    model_inputs_version = online_deployment.tags.get(DEPLOYMENT_MODEL_INPUTS_VERSION_KEY)
    model_outputs_name = online_deployment.tags.get(DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY)
    model_outputs_version = online_deployment.tags.get(DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY)
    model_inputs_type = client.data.get(model_inputs_name, model_inputs_version).type
    model_outputs_type = client.data.get(model_outputs_name, model_outputs_version).type

    return (
        model_inputs_name,
        model_inputs_version,
        model_outputs_name,
        model_outputs_version,
        model_inputs_type,
        model_outputs_type,
    )


def check_default_datasets(
    signal: Union[DataQualitySignal, DataDriftSignal],
    dataset_name: str,
    dataset_version: str,
    dataset_type: str,
    is_model_inputs: bool,
):
    assert dataset_name in signal.production_data.input_data.path
    assert dataset_version in signal.production_data.input_data.path
    if is_model_inputs:
        assert signal.production_data.data_context == MonitorDatasetContext.MODEL_INPUTS
    else:
        assert signal.production_data.data_context == MonitorDatasetContext.MODEL_OUTPUTS
    assert signal.production_data.input_data.type == dataset_type

    assert dataset_name in signal.reference_data.input_data.path
    assert dataset_version in signal.production_data.input_data.path
    if is_model_inputs:
        assert signal.production_data.data_context == MonitorDatasetContext.MODEL_INPUTS
    else:
        assert signal.production_data.data_context == MonitorDatasetContext.MODEL_OUTPUTS
    assert signal.reference_data.input_data.type == dataset_type


def create_and_assert_basic_schedule_fields(
    client: MLClient, test_path: str, randstr: Callable[[str], str], data_with_2_versions: str
):
    schedule_name = randstr("schedule_name")

    params_override = [
        {"name": schedule_name},
        {
            "create_monitor.monitoring_signals.testSignal.production_data.input_data.path": f"azureml:{data_with_2_versions}:1"
        },
        {"create_monitor.monitoring_signals.testSignal.production_data.input_data.type": "uri_folder"},
        {
            "create_monitor.monitoring_signals.testSignal.reference_data.input_data.path": f"azureml:{data_with_2_versions}:2"
        },
        {"create_monitor.monitoring_signals.testSignal.reference_data.input_data.type": "uri_folder"},
    ]

    schedule = load_schedule(test_path, params_override=params_override)
    # not testing monitoring target expansion right now
    schedule.create_monitor.monitoring_target = None
    # bug in service when deserializing lookback_period is not supported yet
    schedule.create_monitor.monitoring_signals["testSignal"].production_data.data_window_size = None

    created_schedule = client.schedules.begin_create_or_update(schedule).result()

    # test ARM id resolution
    assert isinstance(created_schedule, MonitorSchedule)

    data_drift_signal = created_schedule.create_monitor.monitoring_signals["testSignal"]
    assert data_drift_signal.production_data
    assert is_ARM_id_for_resource(data_drift_signal.production_data.input_data.path, AzureMLResourceType.DATA)
    assert data_drift_signal.reference_data
    assert is_ARM_id_for_resource(data_drift_signal.reference_data.input_data.path, AzureMLResourceType.DATA)

    return created_schedule

import json
import os
from pathlib import Path
from typing import List, Optional
from unittest.mock import patch

import pytest
import yaml
from marshmallow.exceptions import ValidationError

from azure.ai.ml import load_job
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import AutoMLJob as RestAutoMLJob
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import AutoNCrossValidations
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import Classification as RestClassification
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import ClassificationPrimaryMetrics
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    ClassificationTrainingSettings as RestClassificationTrainingSettings,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import ColumnTransformer as RestColumnTransformer
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import CustomNCrossValidations
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import Forecasting as RestForecasting
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import ForecastingPrimaryMetrics
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    ForecastingSettings as RestForecastingSettings,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    ForecastingTrainingSettings as RestForecastingTrainingSettings,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import JobBase, LogVerbosity, MLTableJobInput
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import Regression as RestRegression
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import RegressionPrimaryMetrics
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    RegressionTrainingSettings as RestRegressionTrainingSettings,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    TableVerticalFeaturizationSettings as RestTableFeaturizationSettings,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    TableVerticalLimitSettings as RestTableVerticalLimitSettings,
)
from azure.ai.ml._schema.automl.table_vertical.regression import AutoMLRegressionSchema
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._utils.utils import camel_to_snake, to_iso_duration_format_mins
from azure.ai.ml.constants import TabularTrainingMode
from azure.ai.ml.constants._common import AZUREML_PRIVATE_FEATURES_ENV_VAR, BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._job.automl import AutoMLConstants, AutoMLTransformerParameterKeys
from azure.ai.ml.entities import Job
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.exceptions import ValidationException
from azure.ai.ml.entities._job.automl.tabular.featurization_settings import TabularFeaturizationSettings
from azure.ai.ml.entities._job.automl.tabular.forecasting_settings import ForecastingSettings
from azure.ai.ml.entities._job.automl.tabular.limit_settings import TabularLimitSettings
from azure.ai.ml.entities._job.automl.training_settings import TrainingSettings


@pytest.fixture(autouse=True)
def set_env_var() -> None:
    with patch.dict(os.environ, {AZUREML_PRIVATE_FEATURES_ENV_VAR: "True"}):
        yield


@pytest.fixture
def limits_expected() -> RestTableVerticalLimitSettings:
    return RestTableVerticalLimitSettings(
        max_trials=40,
        timeout=to_iso_duration_format_mins(180),
        max_concurrent_trials=5,
        enable_early_termination=True,
        exit_score=0.85,
        max_nodes=None,
    )


@pytest.fixture
def classification_training_settings_expected() -> RestClassificationTrainingSettings:
    return RestClassificationTrainingSettings(
        enable_dnn_training=True,
        enable_model_explainability=True,
        ensemble_model_download_timeout="PT2M",
    )


@pytest.fixture
def forecasting_training_settings_expected() -> RestForecastingTrainingSettings:
    return RestForecastingTrainingSettings(
        enable_dnn_training=True,
        enable_model_explainability=True,
        ensemble_model_download_timeout="PT2M",
    )


@pytest.fixture
def regression_training_settings_expected() -> RestRegressionTrainingSettings:
    return RestRegressionTrainingSettings(
        enable_dnn_training=True,
        enable_model_explainability=True,
        ensemble_model_download_timeout="PT2M",
    )


@pytest.fixture
def featurization_settings_expected() -> RestTableFeaturizationSettings:
    with open("./tests/test_configs/automl_job/featurization_config.json", "r") as f:
        cfg = json.load(f)
    transformer_dict = {}
    for key, item in cfg["transformer_params"].items():
        transformer_dict[AutoMLTransformerParameterKeys[camel_to_snake(key).upper()].value] = [
            RestColumnTransformer(fields=o["fields"], parameters=o["parameters"]) for o in item
        ]
    return RestTableFeaturizationSettings(
        blocked_transformers=cfg["blocked_transformers"],
        column_name_and_types=cfg["column_name_and_types"],
        dataset_language=cfg["dataset_language"],
        enable_dnn_featurization=cfg["enable_dnn_featurization"],
        mode=AutoMLConstants.CUSTOM,
        transformer_params=transformer_dict,
    )


@pytest.fixture
def compute_binding_expected(mock_workspace_scope: OperationScope) -> str:
    return "/subscriptions/test_subscription/resourceGroups/test_resource_group/providers/Microsoft.MachineLearningServices/workspaces/test_workspace_name/computes/cpu-cluster"


@pytest.fixture
def expected_training_data() -> MLTableJobInput:
    return MLTableJobInput(
        uri="/subscriptions/test_subscription/resourceGroups/test_resource_group/providers/Microsoft.MachineLearningServices/workspaces/test_workspace_name/data/insurance-training-data/versions/1",
    )


@pytest.fixture
def expected_validation_data() -> MLTableJobInput:
    return MLTableJobInput(
        uri="/subscriptions/test_subscription/resourceGroups/test_resource_group/providers/Microsoft.MachineLearningServices/workspaces/test_workspace_name/data/insurance-validation-data/versions/1",
    )


@pytest.fixture
def expected_test_data() -> MLTableJobInput:
    return MLTableJobInput(
        uri="/subscriptions/test_subscription/resourceGroups/test_resource_group/providers/Microsoft.MachineLearningServices/workspaces/test_workspace_name/data/insurance-test-data/versions/1",
    )


@pytest.fixture
def expected_target_column_name() -> str:
    return "safedriver"


@pytest.fixture
def expected_cv_split_column_names() -> List:
    return ["Quantity"]


@pytest.fixture
def expected_n_cross_validations() -> CustomNCrossValidations:
    return CustomNCrossValidations(value=2)


@pytest.fixture
def expected_validation_data_size() -> int:
    return 0.2


@pytest.fixture
def expected_forecasting_settings(mock_workspace_scope: OperationScope) -> RestForecastingSettings:
    from azure.ai.ml._restclient.v2023_04_01_preview.models import (
        CustomForecastHorizon,
        CustomTargetLags,
        CustomTargetRollingWindowSize,
    )

    return RestForecastingSettings(
        country_or_region_for_holidays="US",
        forecast_horizon=CustomForecastHorizon(value=10),
        target_lags=CustomTargetLags(values=[20]),
        target_rolling_window_size=CustomTargetRollingWindowSize(value=3),
        time_column_name="abc",
        time_series_id_column_names=["xyz"],
    )


@pytest.fixture
def expected_regression_job(
    mock_workspace_scope: OperationScope,
    limits_expected: RestTableVerticalLimitSettings,
    regression_training_settings_expected: RestRegressionTrainingSettings,
    featurization_settings_expected: RestTableFeaturizationSettings,
    expected_training_data: MLTableJobInput,
    expected_validation_data: MLTableJobInput,
    expected_test_data: MLTableJobInput,
    expected_validation_data_size: int,
    expected_cv_split_column_names: List,
    expected_n_cross_validations: CustomNCrossValidations,
    expected_target_column_name: str,
    compute_binding_expected: str,
) -> JobBase:
    return _get_rest_automl_job(
        RestRegression(
            target_column_name=expected_target_column_name,
            training_data=expected_training_data,
            validation_data=expected_validation_data,
            validation_data_size=expected_validation_data_size,
            cv_split_column_names=expected_cv_split_column_names,
            n_cross_validations=expected_n_cross_validations,
            test_data=expected_test_data,
            featurization_settings=featurization_settings_expected,
            limit_settings=limits_expected,
            training_settings=regression_training_settings_expected,
            primary_metric=RegressionPrimaryMetrics.NORMALIZED_MEAN_ABSOLUTE_ERROR,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomljob",
    )


@pytest.fixture
def expected_classification_job(
    mock_workspace_scope: OperationScope,
    limits_expected: RestTableVerticalLimitSettings,
    classification_training_settings_expected: RestClassificationTrainingSettings,
    featurization_settings_expected: RestTableFeaturizationSettings,
    expected_training_data: MLTableJobInput,
    expected_validation_data: MLTableJobInput,
    expected_test_data: MLTableJobInput,
    expected_validation_data_size: int,
    expected_cv_split_column_names: List,
    expected_n_cross_validations: CustomNCrossValidations,
    expected_target_column_name: str,
    compute_binding_expected: str,
) -> JobBase:
    return _get_rest_automl_job(
        RestClassification(
            target_column_name=expected_target_column_name,
            positive_label="label",
            training_data=expected_training_data,
            validation_data=expected_validation_data,
            test_data=expected_test_data,
            validation_data_size=expected_validation_data_size,
            cv_split_column_names=expected_cv_split_column_names,
            n_cross_validations=expected_n_cross_validations,
            featurization_settings=featurization_settings_expected,
            limit_settings=limits_expected,
            training_settings=classification_training_settings_expected,
            primary_metric=ClassificationPrimaryMetrics.ACCURACY,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomljob",
    )


@pytest.fixture
def expected_forecasting_job(
    mock_workspace_scope: OperationScope,
    limits_expected: RestTableVerticalLimitSettings,
    forecasting_training_settings_expected: RestForecastingTrainingSettings,
    featurization_settings_expected: RestTableFeaturizationSettings,
    expected_forecasting_settings: RestForecastingSettings,
    expected_training_data: MLTableJobInput,
    expected_validation_data: MLTableJobInput,
    expected_test_data: MLTableJobInput,
    expected_validation_data_size: int,
    expected_cv_split_column_names: List,
    expected_n_cross_validations: CustomNCrossValidations,
    expected_target_column_name: str,
    compute_binding_expected: str,
) -> JobBase:
    return _get_rest_automl_job(
        RestForecasting(
            target_column_name=expected_target_column_name,
            training_data=expected_training_data,
            validation_data=expected_validation_data,
            test_data=expected_test_data,
            validation_data_size=expected_validation_data_size,
            cv_split_column_names=expected_cv_split_column_names,
            n_cross_validations=expected_n_cross_validations,
            featurization_settings=featurization_settings_expected,
            limit_settings=limits_expected,
            training_settings=forecasting_training_settings_expected,
            primary_metric=ForecastingPrimaryMetrics.R2_SCORE,
            forecasting_settings=expected_forecasting_settings,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomljob",
    )


def _get_rest_automl_job(automl_task, name, compute_id):
    properties = RestAutoMLJob(
        experiment_name="automl",
        compute_id=compute_id,
        task_details=automl_task,
        properties={},
        outputs={},
        tags={},
    )
    result = JobBase(properties=properties)
    result.name = name
    return result


@pytest.fixture
def loaded_regression_full_job(mock_machinelearning_client: OperationScope) -> AutoMLJob:
    test_schema_path = Path("./tests/test_configs/automl_job/automl_job_mock_regression.yaml")
    job = load_job(test_schema_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
    return _add_automl_default_properties(job)


@pytest.fixture
def loaded_classification_full_job(mock_machinelearning_client: OperationScope) -> AutoMLJob:
    test_schema_path = Path("./tests/test_configs/automl_job/automl_job_mock_classification.yaml")
    job = load_job(test_schema_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
    return _add_automl_default_properties(job)


@pytest.fixture
def loaded_forecasting_full_job(mock_machinelearning_client: OperationScope) -> AutoMLJob:
    test_schema_path = Path("./tests/test_configs/automl_job/automl_job_mock_forecasting.yaml")
    job = load_job(test_schema_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
    return _add_automl_default_properties(job)


def _add_automl_default_properties(automl_job):
    automl_job.training.enable_onnx_compatible_models = False
    automl_job.training.enable_stack_ensemble = True
    automl_job.training.enable_vote_ensemble = True
    automl_job.limits.max_cores_per_trial = -1
    automl_job.limits.trial_timeout_minutes = 30
    return automl_job


# AutoMLJob Yaml with auto values for target_lags and featurization_config
@pytest.fixture
def loaded_regression_job_auto_fields(mock_machinelearning_client) -> AutoMLJob:
    test_schema_path = Path("./tests/test_configs/automl_job/automl_job_mock_auto.yaml")
    job = load_job(test_schema_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
    return job


@pytest.mark.automl_test
@pytest.mark.unittest
class TestAutoMLTabularSchema:
    def _validate_automl_tabular_job(self, automl_job):
        assert isinstance(automl_job, AutoMLJob)
        assert automl_job.training_data and isinstance(automl_job.training_data, Input)
        assert automl_job.validation_data and isinstance(automl_job.validation_data, Input)
        assert automl_job.test_data and isinstance(automl_job.test_data, Input)
        assert automl_job.limits and isinstance(automl_job.limits, TabularLimitSettings)
        assert automl_job.training and isinstance(automl_job.training, TrainingSettings)
        assert automl_job.featurization and isinstance(automl_job.featurization, TabularFeaturizationSettings)
        assert automl_job.compute and isinstance(automl_job.compute, str)

    def test_deserialized_classification_job(
        self,
        mock_workspace_scope: OperationScope,
        loaded_classification_full_job: AutoMLJob,
        expected_classification_job: JobBase,
    ):
        self._validate_automl_tabular_job(loaded_classification_full_job)
        assert loaded_classification_full_job._to_rest_object().as_dict() == expected_classification_job.as_dict()

    def test_deserialized_forecasting_job(
        self,
        mock_workspace_scope: OperationScope,
        loaded_forecasting_full_job: AutoMLJob,
        expected_forecasting_job: JobBase,
    ):
        self._validate_automl_tabular_job(loaded_forecasting_full_job)
        assert loaded_forecasting_full_job.forecasting_settings and isinstance(
            loaded_forecasting_full_job.forecasting_settings, ForecastingSettings
        )
        assert loaded_forecasting_full_job._to_rest_object().as_dict() == expected_forecasting_job.as_dict()

    def test_deserialized_regression_job(
        self,
        mock_workspace_scope: OperationScope,
        loaded_regression_full_job: AutoMLJob,
        expected_regression_job: JobBase,
    ):
        self._validate_automl_tabular_job(loaded_regression_full_job)
        assert loaded_regression_full_job._to_rest_object().as_dict() == expected_regression_job.as_dict()

    def test_deserialize_regression_job(
        self,
        mock_workspace_scope,
        expected_regression_job: JobBase,
        loaded_regression_full_job: AutoMLJob,
    ):
        # test deserialzing an AutoML job from REST with the REST formatted featurization config
        from_rest_job = AutoMLJob._from_rest_object(expected_regression_job)
        assert from_rest_job == loaded_regression_full_job

    def test_auto_off_field_job(
        self, mock_workspace_scope: OperationScope, loaded_regression_job_auto_fields: AutoMLJob
    ) -> None:
        rest_job = loaded_regression_job_auto_fields._to_rest_object()
        # Change to REST representation to test the from REST behavior
        assert rest_job.properties.task_details.featurization_settings.mode == "auto"
        # # MFE returns just the string "auto" for the featurization_config
        rest_job.properties.task_details.featurization_settings.mode = "auto"
        from_rest_job = AutoMLJob._from_rest_object(rest_job)
        assert from_rest_job.featurization.mode == AutoMLConstants.AUTO
        serialized_job = from_rest_job._to_dict()
        assert serialized_job[AutoMLConstants.FEATURIZATION_YAML]["mode"] == AutoMLConstants.AUTO

        # test what happens when featurization config is 'off' in featurization settings. the value should be sent as is
        loaded_regression_job_auto_fields.featurization.mode = AutoMLConstants.OFF
        rest_job_with_off = loaded_regression_job_auto_fields._to_rest_object()
        assert rest_job_with_off.properties.task_details.featurization_settings.mode == "off"
        # MFE returns just the string "auto" for the featurization_config
        rest_job_with_off.properties.task_details.featurization_settings.mode = "off"
        from_rest_job_with_off = AutoMLJob._from_rest_object(rest_job_with_off)
        assert from_rest_job_with_off.featurization.mode == AutoMLConstants.OFF

    def test_invalid_yaml(self):
        test_schema_path = Path("./tests/test_configs/automl_job/automl_job_missing_required_fields.yaml")
        context = {BASE_PATH_CONTEXT_KEY: Path(test_schema_path).parent}
        schema = AutoMLRegressionSchema(context=context)
        with open(test_schema_path, "r") as f:
            cfg = yaml.safe_load(f)
            with pytest.raises(ValidationError) as ve:
                AutoMLJob(**schema.load(cfg))
            error_dict = json.loads(str.replace(str(ve.value), "'", '"'))
            assert error_dict["task"][0] == "Missing data for required field."
            assert error_dict["training_data"][0] == "Field may not be null."
            assert error_dict["target_column_name"][0] == "Missing data for required field."

    def test_auto_n_cv_schema(
        self,
        loaded_classification_full_job: AutoMLJob,
    ):
        loaded_classification_full_job.n_cross_validations = "auto"
        obj = loaded_classification_full_job._to_rest_object()
        assert isinstance(
            obj.properties.task_details.n_cross_validations, AutoNCrossValidations
        ), "N cross validations not an object of AutoNCrossValidations"

    def test_value_n_cv_schema(
        self,
        loaded_classification_full_job: AutoMLJob,
    ):
        obj = loaded_classification_full_job._to_rest_object()
        assert isinstance(
            obj.properties.task_details.n_cross_validations, CustomNCrossValidations
        ), "N cross validations not an object of CustomNCrossValidations"

    @pytest.mark.parametrize(
        "yaml_path, max_nodes, training_mode, is_error",
        [
            ("./tests/test_configs/automl_job/automl_job_mock_regression.yaml", None, None, False),
            (
                "./tests/test_configs/automl_job/automl_job_mock_regression_auto_mode.yaml",
                4,
                TabularTrainingMode.AUTO,
                False,
            ),
            (
                "./tests/test_configs/automl_job/automl_job_mock_regression_distributed_mode.yaml",
                4,
                TabularTrainingMode.DISTRIBUTED,
                False,
            ),
            (
                "./tests/test_configs/automl_job/automl_job_mock_regression_non_distributed_mode.yaml",
                4,
                TabularTrainingMode.NON_DISTRIBUTED,
                False,
            ),
            ("./tests/test_configs/automl_job/automl_job_mock_regression_invalid_mode.yaml", None, None, True),
            ("./tests/test_configs/automl_job/automl_job_mock_classification.yaml", None, None, False),
            (
                "./tests/test_configs/automl_job/automl_job_mock_classification_auto_mode.yaml",
                4,
                TabularTrainingMode.AUTO,
                False,
            ),
            (
                "./tests/test_configs/automl_job/automl_job_mock_classification_distributed_mode.yaml",
                4,
                TabularTrainingMode.DISTRIBUTED,
                False,
            ),
            (
                "./tests/test_configs/automl_job/automl_job_mock_classification_non_distributed_mode.yaml",
                None,
                TabularTrainingMode.NON_DISTRIBUTED,
                False,
            ),
            ("./tests/test_configs/automl_job/automl_job_mock_classification_invalid_mode.yaml", None, None, True),
            ("./tests/test_configs/automl_job/automl_job_mock_forecasting.yaml", None, None, False),
            (
                "./tests/test_configs/automl_job/automl_job_mock_forecasting_auto_mode.yaml",
                4,
                TabularTrainingMode.AUTO,
                False,
            ),
            (
                "./tests/test_configs/automl_job/automl_job_mock_forecasting_distributed_mode.yaml",
                4,
                TabularTrainingMode.DISTRIBUTED,
                False,
            ),
            (
                "./tests/test_configs/automl_job/automl_job_mock_forecasting_non_distributed_mode.yaml",
                None,
                TabularTrainingMode.NON_DISTRIBUTED,
                False,
            ),
            ("./tests/test_configs/automl_job/automl_job_mock_forecasting_invalid_mode.yaml", None, None, True),
        ],
    )
    def test_tabular_training_modes_and_max_nodes(
        self,
        yaml_path: str,
        max_nodes: Optional[int],
        training_mode: Optional[TabularTrainingMode],
        is_error: bool,
    ):
        if is_error:
            with pytest.raises(ValidationError):
                loaded_job = load_job(Path(yaml_path))
        else:
            loaded_job = load_job(Path(yaml_path))
            assert loaded_job.training.training_mode == training_mode, "Training mode initialized incorrectly"
            assert loaded_job.limits.max_nodes == max_nodes, "Max nodes initialized incorrectly"

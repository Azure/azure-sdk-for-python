import os
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest

from azure.ai.ml import load_job
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import AutoMLJob as RestAutoMLJob
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import BanditPolicy as RestBanditPolicy
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import (
    ClassificationMultilabelPrimaryMetrics,
    ClassificationPrimaryMetrics,
)
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import (
    ImageClassification as RestImageClassification,
)
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import (
    ImageClassificationMultilabel as RestImageClassificationMultilabel,
)
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import (
    ImageInstanceSegmentation as RestImageInstanceSegmentation,
)
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import ImageLimitSettings as RestImageLimitSettings
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import (
    ImageModelDistributionSettingsClassification as RestImageClassificationSearchSpace,
)
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import (
    ImageModelDistributionSettingsObjectDetection as RestImageObjectDetectionSearchSpace,
)
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import (
    ImageModelSettingsClassification,
    ImageModelSettingsObjectDetection,
)
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import (
    ImageObjectDetection as RestImageObjectDetection,
)
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import (
    ImageSweepLimitSettings as RestImageSweepLimitSettings,
)
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import ImageSweepSettings as RestImageSweepSettings
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import (
    InstanceSegmentationPrimaryMetrics,
    JobBase,
    LogVerbosity,
    MLTableJobInput,
    ObjectDetectionPrimaryMetrics,
)
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._utils.utils import dump_yaml_to_file, load_yaml, to_iso_duration_format_mins
from azure.ai.ml.automl import (
    ImageClassificationSearchSpace,
    ImageLimitSettings,
    ImageObjectDetectionSearchSpace,
    ImageSweepSettings,
)
from azure.ai.ml.constants._common import AZUREML_PRIVATE_FEATURES_ENV_VAR
from azure.ai.ml.entities import Job
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob


@pytest.fixture(autouse=True)
def set_env_var() -> None:
    with patch.dict(os.environ, {AZUREML_PRIVATE_FEATURES_ENV_VAR: "True"}):
        yield


@pytest.fixture
def compute_binding_expected(mock_workspace_scope: OperationScope) -> str:
    return "/subscriptions/test_subscription/resourceGroups/test_resource_group/providers/Microsoft.MachineLearningServices/workspaces/test_workspace_name/computes/cpu-cluster"


@pytest.fixture
def expected_image_limits(run_type: str) -> RestImageLimitSettings:
    return RestImageLimitSettings(
        timeout=to_iso_duration_format_mins(60),
        max_concurrent_trials=1,
        max_trials=2 if run_type == "automode" else 1,
    )


@pytest.fixture
def expected_image_training_data() -> MLTableJobInput:
    return MLTableJobInput(
        uri="/subscriptions/test_subscription/resourceGroups/test_resource_group/providers/Microsoft.MachineLearningServices/workspaces/test_workspace_name/data/image-training-data/versions/1",
    )


@pytest.fixture
def expected_image_validation_data() -> MLTableJobInput:
    return MLTableJobInput(
        uri="/subscriptions/test_subscription/resourceGroups/test_resource_group/providers/Microsoft.MachineLearningServices/workspaces/test_workspace_name/data/image-validation-data/versions/1",
    )


@pytest.fixture
def expected_image_target_column_name() -> str:
    return "label"


@pytest.fixture
def expected_image_sweep_settings() -> RestImageSweepSettings:
    return RestImageSweepSettings(
        limits=RestImageSweepLimitSettings(
            max_concurrent_trials=4,
            max_trials=20,
        ),
        sampling_algorithm="grid",
        early_termination=RestBanditPolicy(
            slack_factor=0.2,
            evaluation_interval=10,
        ),
    )


@pytest.fixture
def expected_image_model_settings_classification() -> ImageModelSettingsClassification:
    return ImageModelSettingsClassification(
        checkpoint_frequency=1,
        early_stopping=True,
        early_stopping_delay=2,
        early_stopping_patience=2,
        evaluation_frequency=1,
    )


@pytest.fixture
def expected_image_model_settings_object_detection() -> ImageModelSettingsObjectDetection:
    return ImageModelSettingsObjectDetection(
        checkpoint_frequency=1,
        early_stopping=True,
        early_stopping_delay=2,
        early_stopping_patience=2,
        evaluation_frequency=1,
    )


@pytest.fixture
def expected_image_search_space_settings() -> List[RestImageClassificationSearchSpace]:
    return [
        RestImageClassificationSearchSpace(
            gradient_accumulation_step="choice(1,2)",
            learning_rate="uniform(0.005,0.05)",
            model_name="choice('vitb16r224','vits16r224')",
            number_of_epochs="choice(15,30)",
        ),
        RestImageClassificationSearchSpace(
            learning_rate="uniform(0.005,0.05)",
            model_name="choice('seresnext','resnest50')",
            training_crop_size="choice(224,256)",
            validation_crop_size="choice(224,256)",
            validation_resize_size="choice(288,320,352)",
        ),
    ]


@pytest.fixture
def expected_image_object_detection_search_space_settings() -> List[RestImageObjectDetectionSearchSpace]:
    return [
        RestImageObjectDetectionSearchSpace(
            model_name="choice('maskrcnn_resnet50_fpn')",
            learning_rate="uniform(0.005,0.05)",
            warmup_cosine_lr_warmup_epochs="choice(0,3)",
            optimizer="choice('sgd','adam','adamw')",
            min_size="choice(600,800)",
        ),
    ]


@pytest.fixture
def expected_image_classification_job(
    mock_workspace_scope: OperationScope,
    run_type: str,
    expected_image_target_column_name: str,
    expected_image_training_data: MLTableJobInput,
    expected_image_validation_data: MLTableJobInput,
    expected_image_limits: RestImageLimitSettings,
    expected_image_sweep_settings: RestImageSweepSettings,
    expected_image_model_settings_classification: ImageModelSettingsClassification,
    expected_image_search_space_settings: List[RestImageClassificationSearchSpace],
    compute_binding_expected: str,
) -> JobBase:
    return _get_rest_automl_job(
        RestImageClassification(
            target_column_name=expected_image_target_column_name,
            training_data=expected_image_training_data,
            validation_data=expected_image_validation_data,
            limit_settings=expected_image_limits,
            sweep_settings=expected_image_sweep_settings if run_type == "sweep" else None,
            model_settings=expected_image_model_settings_classification,
            search_space=expected_image_search_space_settings if run_type == "sweep" else None,
            primary_metric=ClassificationPrimaryMetrics.ACCURACY,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomlimagejob",
    )


@pytest.fixture
def expected_image_classification_multilabel_job(
    mock_workspace_scope: OperationScope,
    run_type: str,
    expected_image_target_column_name: str,
    expected_image_training_data: MLTableJobInput,
    expected_image_validation_data: MLTableJobInput,
    expected_image_limits: RestImageLimitSettings,
    expected_image_sweep_settings: RestImageSweepSettings,
    expected_image_model_settings_classification: ImageModelSettingsClassification,
    expected_image_search_space_settings: List[RestImageClassificationSearchSpace],
    compute_binding_expected: str,
) -> JobBase:
    return _get_rest_automl_job(
        RestImageClassificationMultilabel(
            target_column_name=expected_image_target_column_name,
            training_data=expected_image_training_data,
            validation_data=expected_image_validation_data,
            limit_settings=expected_image_limits,
            sweep_settings=expected_image_sweep_settings if run_type == "sweep" else None,
            model_settings=expected_image_model_settings_classification,
            search_space=expected_image_search_space_settings if run_type == "sweep" else None,
            primary_metric=ClassificationMultilabelPrimaryMetrics.IOU,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomlimagejob",
    )


@pytest.fixture
def expected_image_object_detection_job(
    mock_workspace_scope: OperationScope,
    run_type: str,
    expected_image_target_column_name: str,
    expected_image_training_data: MLTableJobInput,
    expected_image_validation_data: MLTableJobInput,
    expected_image_limits: RestImageLimitSettings,
    expected_image_sweep_settings: RestImageSweepSettings,
    expected_image_model_settings_object_detection: ImageModelSettingsObjectDetection,
    expected_image_object_detection_search_space_settings: List[RestImageObjectDetectionSearchSpace],
    compute_binding_expected: str,
) -> JobBase:
    return _get_rest_automl_job(
        RestImageObjectDetection(
            target_column_name=expected_image_target_column_name,
            training_data=expected_image_training_data,
            validation_data=expected_image_validation_data,
            limit_settings=expected_image_limits,
            sweep_settings=expected_image_sweep_settings if run_type == "sweep" else None,
            model_settings=expected_image_model_settings_object_detection,
            search_space=expected_image_object_detection_search_space_settings if run_type == "sweep" else None,
            primary_metric=ObjectDetectionPrimaryMetrics.MEAN_AVERAGE_PRECISION,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomlimagejob",
    )


@pytest.fixture
def expected_image_instance_segmentation_job(
    mock_workspace_scope: OperationScope,
    run_type: str,
    expected_image_target_column_name: str,
    expected_image_training_data: MLTableJobInput,
    expected_image_validation_data: MLTableJobInput,
    expected_image_limits: RestImageLimitSettings,
    expected_image_sweep_settings: RestImageSweepSettings,
    expected_image_model_settings_object_detection: ImageModelSettingsObjectDetection,
    expected_image_object_detection_search_space_settings: List[RestImageObjectDetectionSearchSpace],
    compute_binding_expected: str,
) -> JobBase:
    return _get_rest_automl_job(
        RestImageInstanceSegmentation(
            target_column_name=expected_image_target_column_name,
            training_data=expected_image_training_data,
            validation_data=expected_image_validation_data,
            limit_settings=expected_image_limits,
            sweep_settings=expected_image_sweep_settings if run_type == "sweep" else None,
            model_settings=expected_image_model_settings_object_detection,
            search_space=expected_image_object_detection_search_space_settings if run_type == "sweep" else None,
            primary_metric=InstanceSegmentationPrimaryMetrics.MEAN_AVERAGE_PRECISION,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomlimagejob",
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
def loaded_image_classification_job(
    mock_machinelearning_client: OperationScope, run_type: str, tmp_path: Path
) -> AutoMLJob:
    test_schema_path = Path("./tests/test_configs/automl_job/automl_image_classification_job_mock.yaml")

    test_config = load_yaml(test_schema_path)
    if run_type == "automode":
        test_config["limits"]["max_trials"] = 2
    if run_type != "sweep":
        # Remove search_space and sweep sections from the yaml
        del test_config["search_space"]
        del test_config["sweep"]

    test_yaml_path = tmp_path / "job.yml"
    dump_yaml_to_file(test_yaml_path, test_config)
    job = load_job(test_yaml_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

    return job


@pytest.fixture
def loaded_image_classification_multilabel_job(
    mock_machinelearning_client: OperationScope,
    run_type: str,
    tmp_path: Path,
) -> AutoMLJob:
    test_schema_path = Path("./tests/test_configs/automl_job/automl_image_classification_multilabel_job_mock.yaml")

    test_config = load_yaml(test_schema_path)
    if run_type == "automode":
        test_config["limits"]["max_trials"] = 2
    if run_type != "sweep":
        # Remove search_space and sweep sections from the yaml
        del test_config["search_space"]
        del test_config["sweep"]

    test_yaml_path = tmp_path / "job.yml"
    dump_yaml_to_file(test_yaml_path, test_config)
    job = load_job(test_yaml_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

    return job


@pytest.fixture
def loaded_image_object_detection_job(
    mock_machinelearning_client: OperationScope, run_type: str, tmp_path: Path
) -> AutoMLJob:
    test_schema_path = Path("./tests/test_configs/automl_job/automl_image_object_detection_job_mock.yaml")

    test_config = load_yaml(test_schema_path)
    if run_type == "automode":
        test_config["limits"]["max_trials"] = 2
    if run_type != "sweep":
        # Remove search_space and sweep sections from the yaml
        del test_config["search_space"]
        del test_config["sweep"]

    test_yaml_path = tmp_path / "job.yml"
    dump_yaml_to_file(test_yaml_path, test_config)
    job = load_job(test_yaml_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

    return job


@pytest.fixture
def loaded_image_instance_segmentation_job(
    mock_machinelearning_client: OperationScope, run_type: str, tmp_path: Path
) -> AutoMLJob:
    test_schema_path = Path("./tests/test_configs/automl_job/automl_image_instance_segmentation_job_mock.yaml")

    test_config = load_yaml(test_schema_path)
    if run_type == "automode":
        test_config["limits"]["max_trials"] = 2
    if run_type != "sweep":
        # Remove search_space and sweep sections from the yaml
        del test_config["search_space"]
        del test_config["sweep"]

    test_yaml_path = tmp_path / "job.yml"
    dump_yaml_to_file(test_yaml_path, test_config)
    job = load_job(test_yaml_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

    return job


@pytest.mark.unittest
class TestAutoMLImageSchema:
    @pytest.mark.parametrize("run_type", ["single", "sweep", "automode"])
    def test_deserialized_image_classification_job(
        self,
        mock_workspace_scope: OperationScope,
        run_type: str,
        expected_image_classification_job: JobBase,
        loaded_image_classification_job: AutoMLJob,
    ):
        self._validate_automl_image_classification_jobs(loaded_image_classification_job, run_type)
        assert (
            loaded_image_classification_job._to_rest_object().as_dict() == expected_image_classification_job.as_dict()
        )

    @pytest.mark.parametrize("run_type", ["single", "sweep", "automode"])
    def test_deserialized_image_classification_multilabel_job(
        self,
        mock_workspace_scope: OperationScope,
        run_type: str,
        expected_image_classification_multilabel_job: JobBase,
        loaded_image_classification_multilabel_job: AutoMLJob,
    ):
        self._validate_automl_image_classification_jobs(loaded_image_classification_multilabel_job, run_type)
        assert (
            loaded_image_classification_multilabel_job._to_rest_object().as_dict()
            == expected_image_classification_multilabel_job.as_dict()
        )

    @pytest.mark.parametrize("run_type", ["single", "sweep", "automode"])
    def test_deserialized_image_object_detection_job(
        self,
        mock_workspace_scope: OperationScope,
        run_type: str,
        expected_image_object_detection_job: JobBase,
        loaded_image_object_detection_job: AutoMLJob,
    ):
        self._validate_automl_image_object_detection_jobs(loaded_image_object_detection_job, run_type)
        assert (
            loaded_image_object_detection_job._to_rest_object().as_dict()
            == expected_image_object_detection_job.as_dict()
        )

    @pytest.mark.parametrize("run_type", ["single", "sweep", "automode"])
    def test_deserialized_image_instance_segmentation_job(
        self,
        mock_workspace_scope: OperationScope,
        run_type: str,
        expected_image_instance_segmentation_job: JobBase,
        loaded_image_instance_segmentation_job: AutoMLJob,
    ):
        self._validate_automl_image_object_detection_jobs(loaded_image_instance_segmentation_job, run_type)
        assert (
            loaded_image_instance_segmentation_job._to_rest_object().as_dict()
            == expected_image_instance_segmentation_job.as_dict()
        )

    def _validate_automl_image_classification_jobs(self, automl_job, run_type):
        assert isinstance(automl_job, AutoMLJob)
        assert automl_job.training_data and isinstance(automl_job.training_data, Input)
        assert automl_job.validation_data and isinstance(automl_job.validation_data, Input)
        assert automl_job.limits and isinstance(automl_job.limits, ImageLimitSettings)
        assert automl_job.compute and isinstance(automl_job.compute, str)
        assert automl_job.training_parameters and isinstance(
            automl_job.training_parameters, ImageModelSettingsClassification
        )
        if run_type == "sweep":
            assert automl_job.sweep and isinstance(automl_job.sweep, ImageSweepSettings)
            assert automl_job.search_space and isinstance(automl_job.search_space, List)
            for item in automl_job.search_space:
                assert isinstance(item, ImageClassificationSearchSpace)
        else:
            assert automl_job.sweep is None
            assert automl_job.search_space is None

    def _validate_automl_image_object_detection_jobs(self, automl_job, run_type):
        assert isinstance(automl_job, AutoMLJob)
        assert automl_job.training_data and isinstance(automl_job.training_data, Input)
        assert automl_job.validation_data and isinstance(automl_job.validation_data, Input)
        assert automl_job.limits and isinstance(automl_job.limits, ImageLimitSettings)
        assert automl_job.compute and isinstance(automl_job.compute, str)
        assert automl_job.training_parameters and isinstance(
            automl_job.training_parameters, ImageModelSettingsObjectDetection
        )
        if run_type == "sweep":
            assert automl_job.sweep and isinstance(automl_job.sweep, ImageSweepSettings)
            assert automl_job.search_space and isinstance(automl_job.search_space, List)
            for item in automl_job.search_space:
                assert isinstance(item, ImageObjectDetectionSearchSpace)
        else:
            assert automl_job.sweep is None
            assert automl_job.search_space is None

    @pytest.mark.parametrize("run_type", ["single", "sweep", "automode"])
    def test_deserialize_image_classification_job(
        self,
        mock_workspace_scope,
        run_type,
        expected_image_classification_job: JobBase,
        loaded_image_classification_job: AutoMLJob,
    ):
        # test expected job when deserialized is same as loaded one.
        from_rest_job = AutoMLJob._from_rest_object(expected_image_classification_job)
        assert from_rest_job == loaded_image_classification_job

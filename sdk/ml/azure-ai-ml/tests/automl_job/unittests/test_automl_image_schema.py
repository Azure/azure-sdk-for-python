import os
import sys
from copy import deepcopy
from email.mime import image
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest
from marshmallow.exceptions import ValidationError

from azure.ai.ml import load_job
from azure.ai.ml._restclient.v2023_04_01_preview.models._azure_machine_learning_workspaces_enums import (
    LearningRateScheduler,
    ModelSize,
    StochasticOptimizer,
    ValidationMetricType,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import AutoMLJob as RestAutoMLJob
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import BanditPolicy as RestBanditPolicy
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    ClassificationMultilabelPrimaryMetrics,
    ClassificationPrimaryMetrics,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    ImageClassification as RestImageClassification,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    ImageClassificationMultilabel as RestImageClassificationMultilabel,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    ImageInstanceSegmentation as RestImageInstanceSegmentation,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import ImageLimitSettings as RestImageLimitSettings
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    ImageModelDistributionSettingsClassification as RestImageClassificationSearchSpace,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    ImageModelDistributionSettingsObjectDetection as RestImageObjectDetectionSearchSpace,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    ImageModelSettingsClassification as RestImageModelSettingsClassification,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    ImageModelSettingsObjectDetection as RestImageModelSettingsObjectDetection,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    ImageObjectDetection as RestImageObjectDetection,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import ImageSweepSettings as RestImageSweepSettings
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    InstanceSegmentationPrimaryMetrics,
    JobBase,
    LogVerbosity,
    MLTableJobInput,
    ObjectDetectionPrimaryMetrics,
)
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._utils.utils import camel_to_snake, dump_yaml_to_file, load_yaml, to_iso_duration_format_mins
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
from azure.ai.ml.entities._job.automl.image import (
    ImageModelSettingsClassification,
    ImageModelSettingsObjectDetection,
    image_classification_job,
    image_instance_segmentation_job,
    image_object_detection_job,
)


@pytest.fixture(autouse=True)
def set_env_var() -> None:
    with patch.dict(os.environ, {AZUREML_PRIVATE_FEATURES_ENV_VAR: "True"}):
        yield


@pytest.fixture
def compute_binding_expected(mock_workspace_scope: OperationScope) -> str:
    return "/subscriptions/test_subscription/resourceGroups/test_resource_group/providers/Microsoft.MachineLearningServices/workspaces/test_workspace_name/computes/cpu-cluster"


@pytest.fixture
def expected_image_limits(run_type: str) -> RestImageLimitSettings:
    maxTrials = 1
    maxConcurrentTrials = 1
    if run_type == "sweep":
        maxTrials = 20
        maxConcurrentTrials = 4
    elif run_type == "automode":
        maxTrials = 2

    return RestImageLimitSettings(
        timeout=to_iso_duration_format_mins(60),
        max_concurrent_trials=maxConcurrentTrials,
        max_trials=maxTrials,
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
        sampling_algorithm="grid",
        early_termination=RestBanditPolicy(
            slack_factor=0.2,
            evaluation_interval=10,
        ),
    )


@pytest.fixture
def expected_image_model_settings_classification() -> RestImageModelSettingsClassification:
    return RestImageModelSettingsClassification(
        checkpoint_frequency=1,
        early_stopping=True,
        early_stopping_delay=2,
        early_stopping_patience=2,
        evaluation_frequency=1,
    )


@pytest.fixture
def expected_image_model_settings_object_detection() -> RestImageModelSettingsObjectDetection:
    return RestImageModelSettingsObjectDetection(
        log_training_metrics="Disable",
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
            ams_gradient="choice(True,False)",
        ),
        RestImageClassificationSearchSpace(
            learning_rate="uniform(0.005,0.05)",
            model_name="choice('seresnext','resnest50')",
            training_crop_size="choice(224,256)",
            validation_crop_size="choice(224,256)",
            validation_resize_size="choice(288,320,352)",
            ams_gradient="False",
        ),
    ]


@pytest.fixture
def expected_image_object_detection_search_space_settings() -> List[RestImageObjectDetectionSearchSpace]:
    return [
        RestImageObjectDetectionSearchSpace(
            model_name="choice('yolov5')",
            learning_rate="uniform(0.0001,0.01)",
            model_size="choice('small','medium')",
        ),
        RestImageObjectDetectionSearchSpace(
            model_name="choice('fasterrcnn_resnet50_fpn')",
            learning_rate="uniform(0.005,0.05)",
            warmup_cosine_lr_warmup_epochs="choice(0,3)",
            optimizer="choice('sgd','adam','adamw')",
            min_size="choice(600,800)",
        ),
    ]


@pytest.fixture
def expected_image_instance_segmentation_search_space_settings() -> List[RestImageObjectDetectionSearchSpace]:
    return [
        RestImageObjectDetectionSearchSpace(
            model_name="choice('maskrcnn_resnet50_fpn')",
            learning_rate="uniform(0.005,0.05)",
            warmup_cosine_lr_warmup_epochs="choice(0,3)",
            optimizer="choice('sgd','adam','adamw')",
            min_size="choice(600,800)",
        )
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
    expected_image_model_settings_classification: RestImageModelSettingsClassification,
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
    expected_image_model_settings_classification: RestImageModelSettingsClassification,
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
    expected_image_model_settings_object_detection: RestImageModelSettingsObjectDetection,
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
    expected_image_model_settings_object_detection: RestImageModelSettingsObjectDetection,
    expected_image_instance_segmentation_search_space_settings: List[RestImageObjectDetectionSearchSpace],
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
            search_space=expected_image_instance_segmentation_search_space_settings if run_type == "sweep" else None,
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
        test_config["limits"]["max_concurrent_trials"] = 1
    elif run_type == "single":
        test_config["limits"]["max_trials"] = 1
        test_config["limits"]["max_concurrent_trials"] = 1
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
        test_config["limits"]["max_concurrent_trials"] = 1
    elif run_type == "single":
        test_config["limits"]["max_trials"] = 1
        test_config["limits"]["max_concurrent_trials"] = 1
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
        test_config["limits"]["max_concurrent_trials"] = 1
    elif run_type == "single":
        test_config["limits"]["max_trials"] = 1
        test_config["limits"]["max_concurrent_trials"] = 1
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
        test_config["limits"]["max_concurrent_trials"] = 1
    elif run_type == "single":
        test_config["limits"]["max_trials"] = 1
        test_config["limits"]["max_concurrent_trials"] = 1
    if run_type != "sweep":
        # Remove search_space and sweep sections from the yaml
        del test_config["search_space"]
        del test_config["sweep"]

    test_yaml_path = tmp_path / "job.yml"
    dump_yaml_to_file(test_yaml_path, test_config)
    job = load_job(test_yaml_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

    return job


@pytest.mark.automl_test
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

    def test_model_name_validation_image_classification(
        self,
        tmp_path: Path,
    ):
        test_schema_path = Path("./tests/test_configs/automl_job/automl_image_classification_job_mock.yaml")

        test_config = load_yaml(test_schema_path)

        # Add model name which is not supported for classification
        test_config["training_parameters"]["model_name"] = "yolov5"

        test_yaml_path = tmp_path / "job.yml"
        dump_yaml_to_file(test_yaml_path, test_config)

        with pytest.raises(ValidationError):
            load_job(test_yaml_path)

    def test_model_name_validation_image_object_detection(
        self,
        tmp_path: Path,
    ):
        test_schema_path = Path("./tests/test_configs/automl_job/automl_image_object_detection_job_mock.yaml")

        test_config = load_yaml(test_schema_path)
        # Add model name which is not supported for image object detection
        test_config["training_parameters"]["model_name"] = "maskrcnn_resnet101_fpn"

        test_yaml_path = tmp_path / "job.yml"
        dump_yaml_to_file(test_yaml_path, test_config)

        with pytest.raises(ValidationError):
            load_job(test_yaml_path)

    def test_model_name_validation_image_instance_segmentation(
        self,
        tmp_path: Path,
    ):
        test_schema_path = Path("./tests/test_configs/automl_job/automl_image_instance_segmentation_job_mock.yaml")

        test_config = load_yaml(test_schema_path)
        # Add model name which is not supported for image instance segmentation
        test_config["training_parameters"]["model_name"] = "vitb16r224"

        test_yaml_path = tmp_path / "job.yml"
        dump_yaml_to_file(test_yaml_path, test_config)

        with pytest.raises(ValidationError):
            load_job(test_yaml_path)

    def test_image_classification_schema_validation(self, tmp_path: Path):
        test_schema_path = Path("./tests/test_configs/automl_job/automl_image_classification_job_mock.yaml")
        test_config = load_yaml(test_schema_path)

        # Test Model Name
        test_config_copy = deepcopy(test_config)
        test_config_copy["search_space"][0]["model_name"]["values"].append("yolov5")
        test_yaml_path = tmp_path / "job.yml"
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Value 'yolov5' passed is not in set"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["model_name"] = 1
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Value 1 passed is not in set"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["model_name"] = 100.5
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Value 100.5 passed is not in set"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["model_name"] = True
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Value True passed is not in set"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["model_name"] = "vitb16r224"
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        assert isinstance(load_job(test_yaml_path), image_classification_job.ImageClassificationJob)

        # Test AMS Gradient
        test_config_copy = deepcopy(test_config)
        test_config_copy["search_space"][0]["ams_gradient"] = {"type": "choice", "values": [1.2, 2.5]}
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Not a valid boolean"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["ams_gradient"] = {"type": "choice", "values": [True, False]}
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        assert isinstance(load_job(test_yaml_path), image_classification_job.ImageClassificationJob)

        # Test early_stopping_delay
        test_config_copy = deepcopy(test_config)
        test_config_copy["search_space"][0]["early_stopping_delay"] = {"type": "choice", "values": [1.2, 2.5]}
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Not a valid integer"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["early_stopping_delay"] = {
            "type": "uniform",
            "min_value": 1,
            "max_value": 15,
        }
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Not a valid integer"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["early_stopping_delay"] = 10.5
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Not a valid integer"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["early_stopping_delay"] = "test"
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Not a valid integer"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["early_stopping_delay"] = True
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Not a valid integer"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["early_stopping_delay"] = {"type": "choice", "values": [1, 2, 3]}
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        assert isinstance(load_job(test_yaml_path), image_classification_job.ImageClassificationJob)

        # test LRSChedular Enum
        test_config_copy = deepcopy(test_config)
        test_config_copy["search_space"][0]["learning_rate_scheduler"] = {
            "type": "choice",
            "values": ["random_lr_scheduler1", "random_lr_scheduler2"],
        }
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Value 'random_lr_scheduler1' passed is not in set"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0][
            "learning_rate_scheduler"
        ] = f"{camel_to_snake(LearningRateScheduler.WARMUP_COSINE)}"
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        assert isinstance(load_job(test_yaml_path), image_classification_job.ImageClassificationJob)

        test_config_copy["search_space"][0]["learning_rate_scheduler"] = {
            "type": "choice",
            "values": [
                f"{camel_to_snake(LearningRateScheduler.WARMUP_COSINE)}",
                f"{camel_to_snake(LearningRateScheduler.STEP)}",
            ],
        }
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        assert isinstance(load_job(test_yaml_path), image_classification_job.ImageClassificationJob)

        # test Optimizer
        test_config_copy = deepcopy(test_config)
        test_config_copy["search_space"][0]["optimizer"] = {"type": "choice", "values": ["random1", "random2"]}
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Value 'random1' passed is not in set"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["optimizer"] = f"{camel_to_snake(StochasticOptimizer.ADAM)}"
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        assert isinstance(load_job(test_yaml_path), image_classification_job.ImageClassificationJob)

        test_config_copy["search_space"][0]["optimizer"] = {
            "type": "choice",
            "values": [f"{camel_to_snake(StochasticOptimizer.SGD)}", f"{camel_to_snake(StochasticOptimizer.ADAM)}"],
        }
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        assert isinstance(load_job(test_yaml_path), image_classification_job.ImageClassificationJob)

        # test validation_resize_size
        test_config_copy = deepcopy(test_config)
        test_config_copy["search_space"][0]["validation_resize_size"] = {"type": "choice", "values": ["255", "230"]}
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Not a valid integer"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["validation_resize_size"] = {"type": "choice", "values": [255.1, 230.1]}
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Not a valid integer"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["validation_resize_size"] = {"type": "choice", "values": [255, 230]}
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        assert isinstance(load_job(test_yaml_path), image_classification_job.ImageClassificationJob)

    def test_object_detection_schema_validation(self, tmp_path: Path):
        test_schema_path = Path("./tests/test_configs/automl_job/automl_image_object_detection_job_mock.yaml")
        test_config = load_yaml(test_schema_path)

        # Test Model Name
        test_config_copy = deepcopy(test_config)
        test_config_copy["search_space"][0]["model_name"]["values"].append("resnext")
        test_yaml_path = tmp_path / "job.yml"
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Value 'resnext' passed is not in set"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["model_name"] = "yolov5"
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        assert isinstance(load_job(test_yaml_path), image_object_detection_job.ImageObjectDetectionJob)

        # Test model size
        test_config_copy = deepcopy(test_config)
        test_config_copy["search_space"][0]["model_size"] = {"type": "uniform", "min_value": 10, "max_value": 100}
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Value 'uniform' passed is not in set"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["model_size"] = {"type": "choice", "values": [10, 100]}
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Value 100 passed is not in set"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["model_size"] = f"{camel_to_snake(ModelSize.SMALL)}"
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        assert isinstance(load_job(test_yaml_path), image_object_detection_job.ImageObjectDetectionJob)

        test_config_copy["search_space"][0]["model_size"] = {
            "type": "choice",
            "values": [f"{camel_to_snake(ModelSize.SMALL)}", f"{camel_to_snake(ModelSize.LARGE)}"],
        }
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        assert isinstance(load_job(test_yaml_path), image_object_detection_job.ImageObjectDetectionJob)

    def test_instance_segmentation_schema_validation(self, tmp_path: Path):
        test_schema_path = Path("./tests/test_configs/automl_job/automl_image_instance_segmentation_job_mock.yaml")
        test_config = load_yaml(test_schema_path)

        # Test Model Name
        test_config_copy = deepcopy(test_config)
        test_config_copy["search_space"][0]["model_name"]["values"].append("vitb16r224")
        test_yaml_path = tmp_path / "job.yml"
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Value 'vitb16r224' passed is not in set"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["model_name"] = "maskrcnn_resnet18_fpn"
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        assert isinstance(load_job(test_yaml_path), image_instance_segmentation_job.ImageInstanceSegmentationJob)

        # Test validation metric type
        test_config_copy = deepcopy(test_config)
        test_config_copy["search_space"][0]["validation_metric_type"] = {"type": "choice", "values": ["type1", "type2"]}
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        with pytest.raises(ValidationError, match="Value 'type1' passed is not in set"):
            load_job(test_yaml_path)

        test_config_copy["search_space"][0]["validation_metric_type"] = f"{camel_to_snake(ValidationMetricType.COCO)}"
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        assert isinstance(load_job(test_yaml_path), image_instance_segmentation_job.ImageInstanceSegmentationJob)

        test_config_copy["search_space"][0]["validation_metric_type"] = {
            "type": "choice",
            "values": [f"{camel_to_snake(ValidationMetricType.COCO)}", f"{camel_to_snake(ValidationMetricType.VOC)}"],
        }
        dump_yaml_to_file(test_yaml_path, test_config_copy)
        assert isinstance(load_job(test_yaml_path), image_instance_segmentation_job.ImageInstanceSegmentationJob)

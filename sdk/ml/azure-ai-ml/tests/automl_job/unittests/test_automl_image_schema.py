import os
from pathlib import Path
from typing import List
import pytest
from unittest.mock import patch
from azure.ai.ml._utils.utils import to_iso_duration_format_mins
from azure.ai.ml.constants import AZUREML_PRIVATE_FEATURES_ENV_VAR
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._restclient.v2022_02_01_preview.models._models_py3 import (
    AutoMLJob as RestAutoMLJob,
    BanditPolicy as RestBanditPolicy,
    ClassificationPrimaryMetrics,
    ClassificationMultilabelPrimaryMetrics,
    ImageClassificationMultilabel as RestImageClassificationMultilabel,
    ImageObjectDetection as RestImageObjectDetection,
    ImageInstanceSegmentation as RestImageInstanceSegmentation,
    ImageClassification as RestImageClassification,
    ImageLimitSettings as RestImageLimitSettings,
    ImageSweepSettings as RestImageSweepSettings,
    ImageSweepLimitSettings as RestImageSweepLimitSettings,
    ImageModelDistributionSettingsClassification as RestImageClassificationSearchSpace,
    ImageModelDistributionSettingsObjectDetection as RestImageObjectDetectionSearchSpace,
    ImageModelSettings,
    ImageModelSettingsClassification,
    ImageVerticalDataSettings as RestImageVerticalDataSettings,
    InstanceSegmentationPrimaryMetrics,
    JobBaseData,
    LogVerbosity,
    MLTableJobInput,
    ObjectDetectionPrimaryMetrics,
    TestDataSettings,
    TrainingDataSettings,
    ImageVerticalValidationDataSettings,
)
from azure.ai.ml.entities import Job
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.automl import (
    ImageLimitSettings,
    ImageSweepSettings,
    ImageClassificationSearchSpace,
    ImageObjectDetectionSearchSpace,
)


@pytest.fixture(autouse=True)
def set_env_var() -> None:
    with patch.dict(os.environ, {AZUREML_PRIVATE_FEATURES_ENV_VAR: "True"}):
        yield


@pytest.fixture
def compute_binding_expected(mock_workspace_scope: OperationScope) -> str:
    return "/subscriptions/test_subscription/resourceGroups/test_resource_group/providers/Microsoft.MachineLearningServices/workspaces/test_workspace_name/computes/cpu-cluster"


@pytest.fixture
def expected_image_limits() -> RestImageLimitSettings:
    return RestImageLimitSettings(
        timeout=to_iso_duration_format_mins(60),
        max_concurrent_trials=1,
        max_trials=1,
    )


@pytest.fixture
def expected_image_data_settings() -> RestImageVerticalDataSettings:
    training_data = TrainingDataSettings(
        data=Input(
            path="/subscriptions/test_subscription/resourceGroups/test_resource_group/providers/Microsoft.MachineLearningServices/workspaces/test_workspace_name/data/image-training-data/versions/1",
            type="mltable",
        ),
    )
    validation_data = ImageVerticalValidationDataSettings(
        data=Input(
            path="/subscriptions/test_subscription/resourceGroups/test_resource_group/providers/Microsoft.MachineLearningServices/workspaces/test_workspace_name/data/image-validation-data/versions/1",
            type="mltable",
        ),
    )
    data = RestImageVerticalDataSettings(
        target_column_name="label",
        training_data=training_data,
        validation_data=validation_data,
    )
    # update data
    data.training_data.data = MLTableJobInput(uri=data.training_data.data.path)
    data.validation_data.data = MLTableJobInput(uri=data.validation_data.data.path)
    return data


@pytest.fixture
def expected_image_sweep_settings() -> RestImageSweepSettings:
    return RestImageSweepSettings(
        limits=RestImageSweepLimitSettings(
            max_concurrent_trials=4,
            max_trials=20,
        ),
        sampling_algorithm="grid",
        early_termination=RestBanditPolicy(
            slack_factor="0.2",
            evaluation_interval=10,
        ),
    )


@pytest.fixture
def expected_image_model_settings_classification() -> ImageModelSettings:
    return ImageModelSettingsClassification(
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
    expected_image_data_settings: RestImageVerticalDataSettings,
    expected_image_limits: RestImageLimitSettings,
    expected_image_sweep_settings: RestImageSweepSettings,
    expected_image_model_settings_classification: ImageModelSettings,
    expected_image_search_space_settings: List[RestImageClassificationSearchSpace],
    compute_binding_expected: str,
) -> JobBaseData:
    return _get_rest_automl_job(
        RestImageClassification(
            data_settings=expected_image_data_settings,
            limit_settings=expected_image_limits,
            sweep_settings=expected_image_sweep_settings,
            model_settings=expected_image_model_settings_classification,
            search_space=expected_image_search_space_settings,
            primary_metric=ClassificationPrimaryMetrics.ACCURACY,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomlimagejob",
    )


@pytest.fixture
def expected_image_classification_multilabel_job(
    mock_workspace_scope: OperationScope,
    expected_image_data_settings: RestImageVerticalDataSettings,
    expected_image_limits: RestImageLimitSettings,
    expected_image_sweep_settings: RestImageSweepSettings,
    expected_image_model_settings_classification: ImageModelSettings,
    expected_image_search_space_settings: List[RestImageClassificationSearchSpace],
    compute_binding_expected: str,
) -> JobBaseData:
    return _get_rest_automl_job(
        RestImageClassificationMultilabel(
            data_settings=expected_image_data_settings,
            limit_settings=expected_image_limits,
            sweep_settings=expected_image_sweep_settings,
            model_settings=expected_image_model_settings_classification,
            search_space=expected_image_search_space_settings,
            primary_metric=ClassificationMultilabelPrimaryMetrics.IOU,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomlimagejob",
    )


@pytest.fixture
def expected_image_object_detection_job(
    mock_workspace_scope: OperationScope,
    expected_image_data_settings: RestImageVerticalDataSettings,
    expected_image_limits: RestImageLimitSettings,
    expected_image_sweep_settings: RestImageSweepSettings,
    expected_image_model_settings_classification: ImageModelSettings,
    expected_image_object_detection_search_space_settings: List[RestImageObjectDetectionSearchSpace],
    compute_binding_expected: str,
) -> JobBaseData:
    return _get_rest_automl_job(
        RestImageObjectDetection(
            data_settings=expected_image_data_settings,
            limit_settings=expected_image_limits,
            sweep_settings=expected_image_sweep_settings,
            model_settings=expected_image_model_settings_classification,
            search_space=expected_image_object_detection_search_space_settings,
            primary_metric=ObjectDetectionPrimaryMetrics.MEAN_AVERAGE_PRECISION,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomlimagejob",
    )


@pytest.fixture
def expected_image_instance_segmentation_job(
    mock_workspace_scope: OperationScope,
    expected_image_data_settings: RestImageVerticalDataSettings,
    expected_image_limits: RestImageLimitSettings,
    expected_image_sweep_settings: RestImageSweepSettings,
    expected_image_model_settings_classification: ImageModelSettings,
    expected_image_object_detection_search_space_settings: List[RestImageObjectDetectionSearchSpace],
    compute_binding_expected: str,
) -> JobBaseData:
    return _get_rest_automl_job(
        RestImageInstanceSegmentation(
            data_settings=expected_image_data_settings,
            limit_settings=expected_image_limits,
            sweep_settings=expected_image_sweep_settings,
            model_settings=expected_image_model_settings_classification,
            search_space=expected_image_object_detection_search_space_settings,
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
    result = JobBaseData(properties=properties)
    result.name = name
    return result


@pytest.fixture
def loaded_image_classification_job(mock_machinelearning_client: OperationScope) -> AutoMLJob:
    test_schema_path = Path("./tests/test_configs/automl_job/automl_image_classification_job_mock.yaml")
    job = Job.load(test_schema_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
    return job


@pytest.fixture
def loaded_image_classification_multilabel_job(mock_machinelearning_client: OperationScope) -> AutoMLJob:
    test_schema_path = Path("./tests/test_configs/automl_job/automl_image_classification_multilabel_job_mock.yaml")
    job = Job.load(test_schema_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
    return job


@pytest.fixture
def loaded_image_object_detection_job(mock_machinelearning_client: OperationScope) -> AutoMLJob:
    test_schema_path = Path("./tests/test_configs/automl_job/automl_image_object_detection_job_mock.yaml")
    job = Job.load(test_schema_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
    return job


@pytest.fixture
def loaded_image_instance_segmentation_job(mock_machinelearning_client: OperationScope) -> AutoMLJob:
    test_schema_path = Path("./tests/test_configs/automl_job/automl_image_instance_segmentation_job_mock.yaml")
    job = Job.load(test_schema_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
    return job


@pytest.mark.unittest
class TestAutoMLImageSchema:
    def test_deserialized_image_classification_job(
        self,
        mock_workspace_scope: OperationScope,
        expected_image_classification_job: JobBaseData,
        loaded_image_classification_job: AutoMLJob,
    ):
        self._validate_automl_image_classification_jobs(loaded_image_classification_job)
        assert (
            loaded_image_classification_job._to_rest_object().as_dict() == expected_image_classification_job.as_dict()
        )

    def test_deserialized_image_classification_multilabel_job(
        self,
        mock_workspace_scope: OperationScope,
        expected_image_classification_multilabel_job: JobBaseData,
        loaded_image_classification_multilabel_job: AutoMLJob,
    ):
        self._validate_automl_image_classification_jobs(loaded_image_classification_multilabel_job)
        assert (
            loaded_image_classification_multilabel_job._to_rest_object().as_dict()
            == expected_image_classification_multilabel_job.as_dict()
        )

    def test_deserialized_image_object_detection_job(
        self,
        mock_workspace_scope: OperationScope,
        expected_image_object_detection_job: JobBaseData,
        loaded_image_object_detection_job: AutoMLJob,
    ):
        self._validate_automl_image_object_detection_jobs(loaded_image_object_detection_job)
        assert (
            loaded_image_object_detection_job._to_rest_object().as_dict()
            == expected_image_object_detection_job.as_dict()
        )

    def test_deserialized_image_instance_segmentation_job(
        self,
        mock_workspace_scope: OperationScope,
        expected_image_instance_segmentation_job: JobBaseData,
        loaded_image_instance_segmentation_job: AutoMLJob,
    ):
        self._validate_automl_image_object_detection_jobs(loaded_image_instance_segmentation_job)
        assert (
            loaded_image_instance_segmentation_job._to_rest_object().as_dict()
            == expected_image_instance_segmentation_job.as_dict()
        )

    def _validate_automl_image_classification_jobs(self, automl_job):
        assert isinstance(automl_job, AutoMLJob)
        assert automl_job._data and isinstance(automl_job._data, RestImageVerticalDataSettings)
        assert automl_job.limits and isinstance(automl_job.limits, ImageLimitSettings)
        assert automl_job.compute and isinstance(automl_job.compute, str)
        assert automl_job.image_model and isinstance(automl_job.image_model, ImageModelSettings)
        assert automl_job.sweep and isinstance(automl_job.sweep, ImageSweepSettings)
        assert automl_job.search_space and isinstance(automl_job.search_space, List)
        for item in automl_job.search_space:
            assert isinstance(item, ImageClassificationSearchSpace)

    def _validate_automl_image_object_detection_jobs(self, automl_job):
        assert isinstance(automl_job, AutoMLJob)
        assert automl_job._data and isinstance(automl_job._data, RestImageVerticalDataSettings)
        assert automl_job.limits and isinstance(automl_job.limits, ImageLimitSettings)
        assert automl_job.compute and isinstance(automl_job.compute, str)
        assert automl_job.image_model and isinstance(automl_job.image_model, ImageModelSettings)
        assert automl_job.sweep and isinstance(automl_job.sweep, ImageSweepSettings)
        assert automl_job.search_space and isinstance(automl_job.search_space, List)
        for item in automl_job.search_space:
            assert isinstance(item, ImageObjectDetectionSearchSpace)

    def test_deserialize_image_classification_job(
        self,
        mock_workspace_scope,
        expected_image_classification_job: JobBaseData,
        loaded_image_classification_job: AutoMLJob,
    ):
        # test expected job when deserialized is same as loaded one.
        from_rest_job = AutoMLJob._from_rest_object(expected_image_classification_job)
        assert from_rest_job == loaded_image_classification_job

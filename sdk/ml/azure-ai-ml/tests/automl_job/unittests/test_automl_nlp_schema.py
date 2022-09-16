import os
from pathlib import Path
from unittest.mock import patch

import pytest

from azure.ai.ml import load_job
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import AutoMLJob as RestAutoMLJob
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import (
    ClassificationPrimaryMetrics,
    JobBase,
    LogVerbosity,
    MLTableJobInput,
)
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import (
    NlpVerticalFeaturizationSettings as RestNlpFeaturizationSettings,
)
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import (
    NlpVerticalLimitSettings as RestNlpVerticalLimitSettings,
)
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import TextClassification as RestTextClassification
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import (
    TextClassificationMultilabel as RestTextClassificationMultilabel,
)
from azure.ai.ml._restclient.v2022_06_01_preview.models._models_py3 import TextNer as RestTextNer
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._utils.utils import to_iso_duration_format_mins
from azure.ai.ml.automl import NlpFeaturizationSettings, NlpLimitSettings
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
def nlp_limits_expected() -> RestNlpVerticalLimitSettings:
    return RestNlpVerticalLimitSettings(
        timeout=to_iso_duration_format_mins(30),
        max_concurrent_trials=2,
    )


@pytest.fixture
def nlp_featurization_settings_expected() -> RestNlpFeaturizationSettings:
    return RestNlpFeaturizationSettings(
        dataset_language="eng",
    )


@pytest.fixture
def expected_nlp_training_data() -> MLTableJobInput:
    return MLTableJobInput(
        uri="/subscriptions/test_subscription/resourceGroups/test_resource_group/providers/Microsoft.MachineLearningServices/workspaces/test_workspace_name/data/nlp-training-data/versions/1",
    )


@pytest.fixture
def expected_nlp_validation_data() -> MLTableJobInput:
    return MLTableJobInput(
        uri="/subscriptions/test_subscription/resourceGroups/test_resource_group/providers/Microsoft.MachineLearningServices/workspaces/test_workspace_name/data/nlp-validation-data/versions/1",
    )


@pytest.fixture
def expected_nlp_target_column_name() -> str:
    return "label_column"


@pytest.fixture
def expected_text_classification_job(
    mock_workspace_scope: OperationScope,
    nlp_limits_expected: RestNlpVerticalLimitSettings,
    nlp_featurization_settings_expected: RestNlpFeaturizationSettings,
    expected_nlp_target_column_name: str,
    expected_nlp_training_data: MLTableJobInput,
    expected_nlp_validation_data: MLTableJobInput,
    compute_binding_expected: str,
) -> JobBase:
    return _get_rest_automl_job(
        RestTextClassification(
            target_column_name=expected_nlp_target_column_name,
            training_data=expected_nlp_training_data,
            validation_data=expected_nlp_validation_data,
            featurization_settings=nlp_featurization_settings_expected,
            limit_settings=nlp_limits_expected,
            primary_metric=ClassificationPrimaryMetrics.ACCURACY,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomlnlpjob",
    )


@pytest.fixture
def expected_text_classification_multilabel_job(
    mock_workspace_scope: OperationScope,
    nlp_limits_expected: RestNlpVerticalLimitSettings,
    nlp_featurization_settings_expected: RestNlpFeaturizationSettings,
    expected_nlp_target_column_name: str,
    expected_nlp_training_data: MLTableJobInput,
    expected_nlp_validation_data: MLTableJobInput,
    compute_binding_expected: str,
) -> JobBase:
    return _get_rest_automl_job(
        RestTextClassificationMultilabel(
            target_column_name=expected_nlp_target_column_name,
            training_data=expected_nlp_training_data,
            validation_data=expected_nlp_validation_data,
            featurization_settings=nlp_featurization_settings_expected,
            limit_settings=nlp_limits_expected,
            primary_metric=ClassificationPrimaryMetrics.ACCURACY,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomlnlpjob",
    )


@pytest.fixture
def expected_text_ner_job(
    mock_workspace_scope: OperationScope,
    nlp_limits_expected: RestNlpVerticalLimitSettings,
    nlp_featurization_settings_expected: RestNlpFeaturizationSettings,
    expected_nlp_training_data: MLTableJobInput,
    expected_nlp_validation_data: MLTableJobInput,
    compute_binding_expected: str,
) -> JobBase:
    return _get_rest_automl_job(
        RestTextNer(
            training_data=expected_nlp_training_data,
            validation_data=expected_nlp_validation_data,
            featurization_settings=nlp_featurization_settings_expected,
            limit_settings=nlp_limits_expected,
            primary_metric=ClassificationPrimaryMetrics.ACCURACY,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomlnlpjob",
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
def loaded_text_classification_job(mock_machinelearning_client: OperationScope) -> AutoMLJob:
    return _load_automl_job_from_path(
        mock_machinelearning_client,
        Path("./tests/test_configs/automl_job/automl_job_text_classification_mock.yaml"),
    )


@pytest.fixture
def loaded_text_classification_multilabel_job(mock_machinelearning_client: OperationScope) -> AutoMLJob:
    return _load_automl_job_from_path(
        mock_machinelearning_client,
        Path("./tests/test_configs/automl_job/automl_job_text_classification_multilabel_mock.yaml"),
    )


@pytest.fixture
def loaded_text_ner_job(mock_machinelearning_client: OperationScope) -> AutoMLJob:
    return _load_automl_job_from_path(
        mock_machinelearning_client,
        Path("./tests/test_configs/automl_job/automl_job_text_ner_mock.yaml"),
    )


def _load_automl_job_from_path(mock_machinelearning_client: OperationScope, schema_path: Path) -> AutoMLJob:
    job = load_job(schema_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
    return job


@pytest.mark.unittest
class TestAutoMLNLPSchema:
    def test_deserialized_nlp_text_classification_job(
        self,
        mock_workspace_scope: OperationScope,
        loaded_text_classification_job: AutoMLJob,
        expected_text_classification_job: JobBase,
    ):
        self._validate_automl_nlp_job(loaded_text_classification_job)
        assert loaded_text_classification_job._to_rest_object().as_dict() == expected_text_classification_job.as_dict()

    def test_deserialized_nlp_text_classification_multilabel_job(
        self,
        mock_workspace_scope: OperationScope,
        loaded_text_classification_multilabel_job: AutoMLJob,
        expected_text_classification_multilabel_job: JobBase,
    ):
        self._validate_automl_nlp_job(loaded_text_classification_multilabel_job)
        assert (
            loaded_text_classification_multilabel_job._to_rest_object().as_dict()
            == expected_text_classification_multilabel_job.as_dict()
        )

    def test_deserialized_nlp_text_ner_job(
        self,
        mock_workspace_scope: OperationScope,
        loaded_text_ner_job: AutoMLJob,
        expected_text_ner_job: JobBase,
    ):
        self._validate_automl_nlp_job(loaded_text_ner_job)
        assert loaded_text_ner_job._to_rest_object().as_dict() == expected_text_ner_job.as_dict()

    def _validate_automl_nlp_job(self, automl_job):
        assert isinstance(automl_job, AutoMLJob)
        assert automl_job.training_data and isinstance(automl_job.training_data, Input)
        assert automl_job.validation_data and isinstance(automl_job.validation_data, Input)
        assert automl_job.limits and isinstance(automl_job.limits, NlpLimitSettings)
        assert automl_job.featurization and isinstance(automl_job.featurization, NlpFeaturizationSettings)
        assert automl_job.compute and isinstance(automl_job.compute, str)

    def test_deserialize_text_classification_job(
        self,
        mock_workspace_scope,
        expected_text_classification_job: JobBase,
        loaded_text_classification_job: AutoMLJob,
    ):
        # test expected_job when deserialized is same as loaded one.
        from_rest_job = AutoMLJob._from_rest_object(expected_text_classification_job)
        assert from_rest_job == loaded_text_classification_job

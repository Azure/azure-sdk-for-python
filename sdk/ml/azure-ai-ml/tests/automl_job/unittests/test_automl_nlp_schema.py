import os
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest

from azure.ai.ml import load_job
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import AutoMLJob as RestAutoMLJob
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import BanditPolicy as RestBanditPolicy
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    ClassificationPrimaryMetrics,
    JobBase,
    LogVerbosity,
    MLTableJobInput,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import NlpFixedParameters as RestNlpFixedParameters
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    NlpParameterSubspace as RestNlpParameterSubspace,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import NlpSweepSettings as RestNlpSweepSettings
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    NlpVerticalFeaturizationSettings as RestNlpFeaturizationSettings,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    NlpVerticalLimitSettings as RestNlpVerticalLimitSettings,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import TextClassification as RestTextClassification
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import (
    TextClassificationMultilabel as RestTextClassificationMultilabel,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models._models_py3 import TextNer as RestTextNer
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._utils.utils import dump_yaml_to_file, load_yaml, to_iso_duration_format_mins
from azure.ai.ml.automl import (
    NlpFeaturizationSettings,
    NlpFixedParameters,
    NlpLimitSettings,
    NlpSearchSpace,
    NlpSweepSettings,
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
def nlp_limits_expected(run_type: str) -> RestNlpVerticalLimitSettings:
    max_trials = 1
    max_concurrent_trials = 1
    max_nodes = 1
    if run_type == "sweep":
        max_trials = 4
        max_concurrent_trials = 4
        max_nodes = 16
    return RestNlpVerticalLimitSettings(
        timeout=to_iso_duration_format_mins(30),
        trial_timeout=to_iso_duration_format_mins(10),
        max_nodes=max_nodes,
        max_concurrent_trials=max_concurrent_trials,
        max_trials=max_trials,
    )


@pytest.fixture
def nlp_sweep_settings_expected() -> RestNlpSweepSettings:
    return RestNlpSweepSettings(
        sampling_algorithm="grid",
        early_termination=RestBanditPolicy(
            slack_amount=0.02,
            evaluation_interval=10,
        ),
    )


@pytest.fixture
def nlp_fixed_parameters_expected() -> RestNlpFixedParameters:
    return RestNlpFixedParameters(
        training_batch_size=32,
        warmup_ratio=0.1,
    )


@pytest.fixture
def nlp_search_space_expected() -> List[RestNlpParameterSubspace]:
    return [
        RestNlpParameterSubspace(
            model_name="choice('bert-base-cased','bert-base-uncased')",
            learning_rate="uniform(0.000005,0.00005)",
            learning_rate_scheduler="choice('linear','cosine_with_restarts')",
        ),
        RestNlpParameterSubspace(
            model_name="choice('roberta-base','roberta-large')",
            learning_rate="uniform(0.000002,0.000008)",
            gradient_accumulation_steps="choice(1,2,3)",
        ),
    ]


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
    run_type: str,
    nlp_limits_expected: RestNlpVerticalLimitSettings,
    nlp_sweep_settings_expected: RestNlpSweepSettings,
    nlp_fixed_parameters_expected: RestNlpFixedParameters,
    nlp_search_space_expected: List[RestNlpParameterSubspace],
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
            sweep_settings=nlp_sweep_settings_expected if run_type == "sweep" else None,
            fixed_parameters=nlp_fixed_parameters_expected,
            search_space=nlp_search_space_expected if run_type == "sweep" else None,
            primary_metric=ClassificationPrimaryMetrics.ACCURACY,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomlnlpjob",
    )


@pytest.fixture
def expected_text_classification_multilabel_job(
    mock_workspace_scope: OperationScope,
    run_type: str,
    nlp_limits_expected: RestNlpVerticalLimitSettings,
    nlp_sweep_settings_expected: RestNlpSweepSettings,
    nlp_fixed_parameters_expected: RestNlpFixedParameters,
    nlp_search_space_expected: List[RestNlpParameterSubspace],
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
            sweep_settings=nlp_sweep_settings_expected if run_type == "sweep" else None,
            fixed_parameters=nlp_fixed_parameters_expected,
            search_space=nlp_search_space_expected if run_type == "sweep" else None,
            primary_metric=ClassificationPrimaryMetrics.ACCURACY,
            log_verbosity=LogVerbosity.DEBUG,
        ),
        compute_id=compute_binding_expected,
        name="simpleautomlnlpjob",
    )


@pytest.fixture
def expected_text_ner_job(
    mock_workspace_scope: OperationScope,
    run_type: str,
    nlp_limits_expected: RestNlpVerticalLimitSettings,
    nlp_sweep_settings_expected: RestNlpSweepSettings,
    nlp_fixed_parameters_expected: RestNlpFixedParameters,
    nlp_search_space_expected: List[RestNlpParameterSubspace],
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
            sweep_settings=nlp_sweep_settings_expected if run_type == "sweep" else None,
            fixed_parameters=nlp_fixed_parameters_expected,
            search_space=nlp_search_space_expected if run_type == "sweep" else None,
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
def loaded_text_classification_job(
    mock_machinelearning_client: OperationScope, run_type: str, tmp_path: Path
) -> AutoMLJob:
    return _load_automl_job_from_path(
        mock_machinelearning_client,
        run_type,
        tmp_path,
        Path("./tests/test_configs/automl_job/automl_job_text_classification_mock.yaml"),
    )


@pytest.fixture
def loaded_text_classification_multilabel_job(
    mock_machinelearning_client: OperationScope, run_type: str, tmp_path: Path
) -> AutoMLJob:
    return _load_automl_job_from_path(
        mock_machinelearning_client,
        run_type,
        tmp_path,
        Path("./tests/test_configs/automl_job/automl_job_text_classification_multilabel_mock.yaml"),
    )


@pytest.fixture
def loaded_text_ner_job(mock_machinelearning_client: OperationScope, run_type: str, tmp_path: Path) -> AutoMLJob:
    return _load_automl_job_from_path(
        mock_machinelearning_client,
        run_type,
        tmp_path,
        Path("./tests/test_configs/automl_job/automl_job_text_ner_mock.yaml"),
    )


def _load_automl_job_from_path(
    mock_machinelearning_client: OperationScope, run_type: str, tmp_path: Path, schema_path: Path
) -> AutoMLJob:
    test_config = load_yaml(schema_path)
    if run_type == "single":
        test_config["limits"]["max_trials"] = 1
        test_config["limits"]["max_concurrent_trials"] = 1
        test_config["limits"]["max_nodes"] = 1
        del test_config["search_space"]
        del test_config["sweep"]

    test_yaml_path = tmp_path / "job.yml"
    dump_yaml_to_file(test_yaml_path, test_config)
    job = load_job(test_yaml_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
    return job


@pytest.mark.automl_test
@pytest.mark.unittest
class TestAutoMLNLPSchema:
    @pytest.mark.parametrize("run_type", ["single", "sweep"])
    def test_deserialized_nlp_text_classification_job(
        self,
        mock_workspace_scope: OperationScope,
        run_type: str,
        loaded_text_classification_job: AutoMLJob,
        expected_text_classification_job: JobBase,
    ):
        self._validate_automl_nlp_job(loaded_text_classification_job, run_type)
        assert loaded_text_classification_job._to_rest_object().as_dict() == expected_text_classification_job.as_dict()

    @pytest.mark.parametrize("run_type", ["single", "sweep"])
    def test_deserialized_nlp_text_classification_multilabel_job(
        self,
        mock_workspace_scope: OperationScope,
        run_type: str,
        loaded_text_classification_multilabel_job: AutoMLJob,
        expected_text_classification_multilabel_job: JobBase,
    ):
        self._validate_automl_nlp_job(loaded_text_classification_multilabel_job, run_type)
        assert (
            loaded_text_classification_multilabel_job._to_rest_object().as_dict()
            == expected_text_classification_multilabel_job.as_dict()
        )

    @pytest.mark.parametrize("run_type", ["single", "sweep"])
    def test_deserialized_nlp_text_ner_job(
        self,
        mock_workspace_scope: OperationScope,
        run_type: str,
        loaded_text_ner_job: AutoMLJob,
        expected_text_ner_job: JobBase,
    ):
        self._validate_automl_nlp_job(loaded_text_ner_job, run_type)
        assert loaded_text_ner_job._to_rest_object().as_dict() == expected_text_ner_job.as_dict()

    def _validate_automl_nlp_job(self, automl_job, run_type):
        assert isinstance(automl_job, AutoMLJob)
        assert automl_job.training_data and isinstance(automl_job.training_data, Input)
        assert automl_job.validation_data and isinstance(automl_job.validation_data, Input)
        assert automl_job.limits and isinstance(automl_job.limits, NlpLimitSettings)
        assert automl_job.featurization and isinstance(automl_job.featurization, NlpFeaturizationSettings)
        assert automl_job.compute and isinstance(automl_job.compute, str)
        assert automl_job.training_parameters and isinstance(automl_job.training_parameters, NlpFixedParameters)

        if run_type == "sweep":
            assert automl_job.sweep and isinstance(automl_job.sweep, NlpSweepSettings)
            assert automl_job.search_space and isinstance(automl_job.search_space, list)
            for item in automl_job.search_space:
                assert isinstance(item, NlpSearchSpace)
        else:
            assert automl_job.sweep is None
            assert automl_job.search_space is None

    @pytest.mark.parametrize("run_type", ["single", "sweep"])
    def test_deserialize_text_classification_job(
        self,
        mock_workspace_scope,
        run_type,
        expected_text_classification_job: JobBase,
        loaded_text_classification_job: AutoMLJob,
    ):
        # test expected_job when deserialized is same as loaded one.
        from_rest_job = AutoMLJob._from_rest_object(expected_text_classification_job)
        assert from_rest_job == loaded_text_classification_job

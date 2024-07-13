import pytest
from pathlib import Path
from typing import Dict, cast
from azure.ai.ml import load_job
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.entities._job.finetuning.finetuning_job import FineTuningJob
from azure.ai.ml.entities._job.finetuning.custom_model_finetuning_job import CustomModelFineTuningJob
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    FineTuningJob as RestFineTuningJob,
)


@pytest.fixture
def loaded_custom_model_finetuning_job_full(mock_machinelearning_client: OperationScope) -> FineTuningJob:
    test_schema_path = Path(
        "./tests/test_configs/finetuning_job/e2e_configs/custom_model_finetuning_job/mock_custom_model_finetuning_job_full.yaml"
    )
    job = load_job(test_schema_path)
    rest_object = CustomModelFineTuningJob._to_rest_object(job)
    return rest_object


@pytest.fixture
def loaded_custom_model_finetuning_job_as_dict(mock_machinelearning_client: OperationScope) -> FineTuningJob:
    test_schema_path = Path(
        "./tests/test_configs/finetuning_job/e2e_configs/custom_model_finetuning_job/mock_custom_model_finetuning_job_full.yaml"
    )
    job = load_job(test_schema_path)
    rest_object = CustomModelFineTuningJob._to_rest_object(job)
    return rest_object


@pytest.fixture
def train_dataset() -> Input:
    return Input(type="uri_file", path="./samsum_dataset/small_train.jsonl")


@pytest.fixture
def validation_dataset() -> Input:
    return Input(type="uri_file", path="./samsum_dataset/small_validation.jsonl")


@pytest.fixture
def mlflow_model_llama() -> Input:
    return Input(type="mlflow_model", path="azureml://registries/azureml-meta/models/Llama-2-7b/versions/9")


@pytest.fixture
def hyperparameters() -> Dict[str, str]:
    return {"per_device_train_batch_size": "1", "learning_rate": "0.00002", "num_train_epochs": "1"}


@pytest.fixture
def expected_custom_model_finetuning_job_full(
    train_dataset, validation_dataset, mlflow_model_llama, hyperparameters
) -> RestFineTuningJob:
    custom_model_finetuning_job = CustomModelFineTuningJob(
        task="textCompletion",
        model=mlflow_model_llama,
        training_data=train_dataset,
        validation_data=validation_dataset,
        name="simple_custom_model_finetuning_job",
        hyperparameters=hyperparameters,
        tags={"foo_tag": "bar"},
        properties={"my_property": "my_value"},
        experiment_name="llama-finetuning-experiment",
        display_name="llama-display-name-1234",
        outputs={"registered_model": Output(type="mlflow_model", name="llama-finetune-registered-1234")},
    )
    return CustomModelFineTuningJob._to_rest_object(custom_model_finetuning_job)


class TestCustomModelFineTuningJobSchema:
    def _validate_finetuning_job(self, finetuning_job: FineTuningJob):
        assert isinstance(finetuning_job, FineTuningJob)
        assert finetuning_job.training_data and isinstance(finetuning_job.training_data, Input)
        assert finetuning_job.validation_data and isinstance(finetuning_job.validation_data, Input)
        assert finetuning_job.model and isinstance(finetuning_job.model, Input)
        mlflow_model = cast(Input, finetuning_job.model)
        assert mlflow_model.type == "mlflow_model"

    def test_custom_model_finetuning_job_full_rest_transform(
        self, expected_custom_model_finetuning_job_full, loaded_custom_model_finetuning_job_full
    ):
        # self._validate_finetuning_job(loaded_custom_model_finetuning_job_full)

        loaded_job = loaded_custom_model_finetuning_job_full.as_dict()
        expected_job = expected_custom_model_finetuning_job_full.as_dict()
        assert loaded_job == expected_job

    def test_custom_model_finetuning_job_load_from_dict_using_schema(
        self, expected_custom_model_finetuning_job_full, loaded_custom_model_finetuning_job_as_dict
    ):
        # self._validate_finetuning_job(loaded_custom_model_finetuning_job_full)

        assert loaded_custom_model_finetuning_job_as_dict is not None

import pytest
from pathlib import Path
from typing import cast
from azure.ai.ml import load_job
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.entities._job.finetuning.finetuning_job import FineTuningJob
from azure.ai.ml.entities._job.finetuning.azure_openai_finetuning_job import AzureOpenAIFineTuningJob
from azure.ai.ml.entities._job.finetuning.azure_openai_hyperparameters import AzureOpenAIHyperparameters
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    FineTuningJob as RestFineTuningJob,
)


@pytest.fixture
def loaded_azure_openai_model_finetuning_job_full(mock_machinelearning_client: OperationScope) -> FineTuningJob:
    test_schema_path = Path(
        "./tests/test_configs/finetuning_job/e2e_configs/custom_model_finetuning_job/mock_azure_openai_finetuning_job_full.yaml"
    )
    job = load_job(test_schema_path)
    mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
    return job


@pytest.fixture
def train_dataset() -> Input:
    return Input(type="uri_file", path="https://foo/bar/train.jsonl")


@pytest.fixture
def validation_dataset() -> Input:
    return Input(type="uri_file", path="https://foo/bar/validation.jsonl")


@pytest.fixture
def mlflow_model_gpt4() -> Input:
    return Input(type="mlflow_model", path="azureml://registries/azure-openai-v2/models/gpt4/versions/9")


@pytest.fixture
def hyperparameters() -> AzureOpenAIHyperparameters:
    return AzureOpenAIHyperparameters(
        batch_size=1,
        learning_rate_multiplier=0.00002,
        n_epochs=1,
    )


@pytest.fixture
def expected_azure_openai_finetuning_job_full(
    train_dataset, validation_dataset, mlflow_model_gpt4, hyperparameters
) -> RestFineTuningJob:
    custom_model_finetuning_job = AzureOpenAIFineTuningJob(
        task="chat_completion",
        model=mlflow_model_gpt4,
        training_data=train_dataset,
        validation_data=validation_dataset,
        name="simple_azure_openai_finetuning_job",
        hyperparameters=hyperparameters,
        tags={"foo_tag": "bar"},
        properties={"my_property": "my_value"},
        experiment_name="gpt4-finetuning-experiment",
        display_name="gpt4-display-name-1234",
        outputs={"registered_model": Output(type="mlflow_model", name="gpt4-finetune-registered-1234")},
    )
    return AzureOpenAIFineTuningJob._to_rest_object(custom_model_finetuning_job)


class TestAzureOpenAIFineTuningJobSchema:
    def _validate_finetuning_job(self, finetuning_job: FineTuningJob):
        assert isinstance(finetuning_job, FineTuningJob)
        assert finetuning_job.training_data and isinstance(finetuning_job.training_data, Input)
        assert finetuning_job.validation_data and isinstance(finetuning_job.validation_data, Input)
        assert finetuning_job.model and isinstance(finetuning_job.model, Input)
        mlflow_model = cast(Input, finetuning_job.model)
        assert mlflow_model.type == "mlflow_model"

    def test_azure_openai_finetuning_job_full(
        self, expected_azure_openai_finetuning_job_full, loaded_azure_openai_model_finetuning_job_full
    ):
        self._validate_finetuning_job(loaded_azure_openai_model_finetuning_job_full)

        assert (
            loaded_azure_openai_model_finetuning_job_full._to_rest_object().as_dict()
            == expected_azure_openai_finetuning_job_full.as_dict()
        )

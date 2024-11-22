import pytest
from pathlib import Path
from typing import Dict
from azure.ai.ml import load_job
from azure.ai.ml.entities import JobResources, QueueSettings
from azure.ai.ml.entities._job.finetuning.custom_model_finetuning_job import (
    CustomModelFineTuningJob,
)
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml._restclient.v2024_10_01_preview.models import (
    FineTuningJob as RestFineTuningJob,
)


@pytest.fixture
def maas_rest_finetuning_job() -> RestFineTuningJob:
    test_schema_path = Path(
        "./tests/test_configs/finetuning_job/e2e_configs/custom_model_finetuning_job/mock_custom_model_finetuning_job_full.yaml"
    )
    job = load_job(test_schema_path)
    rest_object = CustomModelFineTuningJob._to_rest_object(job)
    return rest_object


@pytest.fixture
def maap_rest_finetuning_job_amlcompute() -> RestFineTuningJob:
    test_schema_path = Path(
        "./tests/test_configs/finetuning_job/e2e_configs/custom_model_finetuning_job/mock_maap_finetuning_job_amlcompute.yaml"
    )
    job = load_job(test_schema_path)
    rest_object = CustomModelFineTuningJob._to_rest_object(job)
    return rest_object


@pytest.fixture
def maap_rest_finetuning_job_instance_types() -> RestFineTuningJob:
    test_schema_path = Path(
        "./tests/test_configs/finetuning_job/e2e_configs/custom_model_finetuning_job/mock_maap_finetuning_job_instance_types.yaml"
    )
    job = load_job(test_schema_path)
    rest_object = CustomModelFineTuningJob._to_rest_object(job)
    return rest_object


@pytest.fixture
def maap_rest_finetuning_job_queue_settings() -> RestFineTuningJob:
    test_schema_path = Path(
        "./tests/test_configs/finetuning_job/e2e_configs/custom_model_finetuning_job/mock_maap_finetuning_job_queue_settings.yaml"
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
    return Input(
        type="mlflow_model", path="azureml://registries/azureml-meta/models/Llama-2-7b/versions/9"
    )


@pytest.fixture
def hyperparameters() -> Dict[str, str]:
    return {"per_device_train_batch_size": "1", "learning_rate": "0.00002", "num_train_epochs": "1"}


@pytest.fixture
def finetuning_job(
    train_dataset, validation_dataset, mlflow_model_llama, hyperparameters
) -> CustomModelFineTuningJob:
    finetuning_job = CustomModelFineTuningJob(
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
        outputs={
            "registered_model": Output(type="mlflow_model", name="llama-finetune-registered-1234")
        },
    )
    return finetuning_job


@pytest.fixture
def maas_finetuning_job(finetuning_job) -> CustomModelFineTuningJob:
    return finetuning_job


@pytest.fixture
def maap_finetuning_job_amlcompute(finetuning_job) -> CustomModelFineTuningJob:
    finetuning_job.compute = "amlcompute"
    return finetuning_job


@pytest.fixture
def expected_rest_maap_finetuning_job_amlcompute(
    maap_finetuning_job_amlcompute,
) -> RestFineTuningJob:
    return CustomModelFineTuningJob._to_rest_object(maap_finetuning_job_amlcompute)


@pytest.fixture
def maap_finetuning_job_instance_types(finetuning_job) -> CustomModelFineTuningJob:
    finetuning_job.resources = JobResources(instance_types=["STANDARD_NC6", "STANDARD_D2_V2"])
    return finetuning_job


@pytest.fixture
def expected_rest_maap_finetuning_job_instance_types(
    maap_finetuning_job_instance_types,
) -> RestFineTuningJob:
    return CustomModelFineTuningJob._to_rest_object(maap_finetuning_job_instance_types)


@pytest.fixture
def maap_finetuning_job_queue_settings(finetuning_job) -> CustomModelFineTuningJob:
    finetuning_job.compute = "amlcompute"
    finetuning_job.queue_settings = QueueSettings(job_tier="Standard")
    return finetuning_job


@pytest.fixture
def expected_rest_maap_finetuning_job_queue_settings(
    maap_finetuning_job_queue_settings,
) -> RestFineTuningJob:
    return CustomModelFineTuningJob._to_rest_object(maap_finetuning_job_queue_settings)


@pytest.fixture
def expected_maas_finetuning_job_rest_obj(maas_finetuning_job) -> RestFineTuningJob:
    return CustomModelFineTuningJob._to_rest_object(maas_finetuning_job)


class TestCustomModelFineTuningJobSchema:

    def test_custom_model_finetuning_job_full_rest_transform(
        self,
        expected_maas_finetuning_job_rest_obj,
        maas_rest_finetuning_job,
    ):
        assert maas_rest_finetuning_job == expected_maas_finetuning_job_rest_obj

    def test_maap_finetuning_job_amlcompute_rest_compare(
        self, maap_rest_finetuning_job_amlcompute, expected_rest_maap_finetuning_job_amlcompute
    ):
        assert maap_rest_finetuning_job_amlcompute == expected_rest_maap_finetuning_job_amlcompute

    def test_maap_finetuning_job_instance_types_rest_compare(
        self,
        maap_rest_finetuning_job_instance_types,
        expected_rest_maap_finetuning_job_instance_types,
    ):
        assert (
            maap_rest_finetuning_job_instance_types
            == expected_rest_maap_finetuning_job_instance_types
        )

    def test_maap_finetuning_job_queue_settings_rest_compare(
        self,
        maap_rest_finetuning_job_queue_settings,
        expected_rest_maap_finetuning_job_queue_settings,
    ):
        assert (
            maap_rest_finetuning_job_queue_settings
            == expected_rest_maap_finetuning_job_queue_settings
        )

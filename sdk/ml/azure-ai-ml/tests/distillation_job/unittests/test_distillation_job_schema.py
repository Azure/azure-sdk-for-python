from pathlib import Path
from typing import Dict

import pytest

from azure.ai.ml import load_job
from azure.ai.ml._restclient.v2024_01_01_preview.models import FineTuningJob as RestFineTuningJob
from azure.ai.ml.constants import DataGenerationTaskType, DataGenerationType
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.distillation.distillation_job import DistillationJob
from azure.ai.ml.entities._job.distillation.distillation_types import (
    DistillationPromptSettings,
    EndpointRequestSettings,
)
from azure.ai.ml.entities._job.finetuning.finetuning_job import FineTuningJob
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration


@pytest.fixture
def loaded_distillation_job_as_rest_obj() -> FineTuningJob:
    test_schema_path = Path("./tests/test_configs/distillation_job/mock_distillation_job_full.yaml")
    job = load_job(test_schema_path)
    print(f"The job is {job} of type {type(job)}")
    rest_object = DistillationJob._to_rest_object(job)
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
        type="mlflow_model", path="azureml://registries/azureml-meta/models/Meta-Llama-3.1-8B-Instruct/versions/1"
    )


@pytest.fixture
def hyperparameters() -> Dict[str, str]:
    return {"learning_rate": "0.00002", "num_train_epochs": "1", "per_device_train_batch_size": "1"}


@pytest.fixture
def inference_parameters() -> Dict:
    return {"temperature": 0.1, "max_tokens": 100, "top_p": 0.95}


@pytest.fixture
def endpoint_request_settings() -> EndpointRequestSettings:
    return EndpointRequestSettings(request_batch_size=5, min_endpoint_success_ratio=0.7)


@pytest.fixture
def prompt_settings() -> DistillationPromptSettings:
    return DistillationPromptSettings(enable_chain_of_thought=False, enable_chain_of_density=False)


@pytest.fixture
def teacher_model_endpoint() -> str:
    return "Llama-3-1-405B-Instruct-BASE"


@pytest.fixture
def expected_distillation_job_as_rest_obj(
    teacher_model_endpoint,
    train_dataset,
    validation_dataset,
    mlflow_model_llama,
    hyperparameters,
    inference_parameters,
    endpoint_request_settings,
    prompt_settings,
) -> RestFineTuningJob:
    distillaton_job = DistillationJob(
        data_generation_type=DataGenerationType.LabelGeneration,
        data_generation_task_type=DataGenerationTaskType.MATH,
        teacher_model_endpoint=teacher_model_endpoint,
        student_model=mlflow_model_llama,
        training_data=train_dataset,
        validation_data=validation_dataset,
        inference_parameters=inference_parameters,
        endpoint_request_settings=endpoint_request_settings,
        prompt_settings=prompt_settings,
        hyperparameters=hyperparameters,
        experiment_name="Distillation-Math-Test-1234",
        name="distillation_job_test",
        description="Distill Llama 3.1 8b model using Llama 3.1 405B teacher model",
        outputs={"registered_model": Output(type="mlflow_model", name="llama-3-1-8b-distilled-1234")},
        resources=ResourceConfiguration(instance_type="Standard_D2_v2"),
    )

    return DistillationJob._to_rest_object(distillaton_job)


class TestDistillationJobSchema:
    def test_distillation_job_full_rest_transform(
        self, expected_distillation_job_as_rest_obj, loaded_distillation_job_as_rest_obj
    ):
        assert loaded_distillation_job_as_rest_obj == expected_distillation_job_as_rest_obj

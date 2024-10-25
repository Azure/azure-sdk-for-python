from pathlib import Path

from azure.ai.ml import load_job
from azure.ai.ml._restclient.v2024_01_01_preview.models import FineTuningJob
from azure.ai.ml.constants import DataGenerationTaskType, DataGenerationType
from azure.ai.ml.entities import NoneCredentialConfiguration, ServerlessConnection, WorkspaceConnection
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.distillation.distillation_job import DistillationJob
from azure.ai.ml.entities._job.distillation.endpoint_request_settings import EndpointRequestSettings
from azure.ai.ml.entities._job.distillation.prompt_settings import PromptSettings
from azure.ai.ml.entities._job.distillation.teacher_model_settings import TeacherModelSettings
from azure.ai.ml.entities._job.finetuning.finetuning_job import FineTuningJob
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration


def loaded_distillation_job_as_rest_obj(path: str) -> FineTuningJob:
    test_schema_path = Path(path)
    job = load_job(test_schema_path)
    rest_object = DistillationJob._to_rest_object(job)
    return rest_object


class TestDistillationJobSchema:
    def test_distillation_job_full_rest_transform(self):
        distillation_job = DistillationJob(
            data_generation_type=DataGenerationType.LABEL_GENERATION,
            data_generation_task_type=DataGenerationTaskType.MATH,
            teacher_model_endpoint_connection=WorkspaceConnection(
                type="custom",
                credentials=NoneCredentialConfiguration(),
                name="Llama-3-1-405B-Instruct-BASE",
                target="None",
            ),
            student_model=Input(
                type="mlflow_model",
                path="azureml://registries/azureml-meta/models/Meta-Llama-3.1-8B-Instruct/versions/1",
            ),
            training_data=Input(type="uri_file", path="./samsum_dataset/small_train.jsonl"),
            validation_data=Input(type="uri_file", path="./samsum_dataset/small_validation.jsonl"),
            teacher_model_settings=TeacherModelSettings(
                inference_parameters={"temperature": 0.1, "max_tokens": 100, "top_p": 0.95},
                endpoint_request_settings=EndpointRequestSettings(request_batch_size=5, min_endpoint_success_ratio=0.7),
            ),
            prompt_settings=PromptSettings(enable_chain_of_thought=False, enable_chain_of_density=False),
            hyperparameters={"learning_rate": "0.00002", "num_train_epochs": "1", "per_device_train_batch_size": "1"},
            experiment_name="Distillation-Math-Test-1234",
            name="distillation_job_test",
            description="Distill Llama 3.1 8b model using Llama 3.1 405B teacher model",
            outputs={"registered_model": Output(type="mlflow_model", name="llama-3-1-8b-distilled-1234")},
            resources=ResourceConfiguration(instance_type="Standard_D2_v2"),
        )
        sdk_rest_object = DistillationJob._to_rest_object(distillation_job)

        path = "./tests/test_configs/distillation_job/mock_distillation_job_full.yaml"
        cli_rest_object = loaded_distillation_job_as_rest_obj(path)
        assert sdk_rest_object == cli_rest_object

    def test_distillation_job_input_rest_transform(self):
        distillation_job = DistillationJob(
            data_generation_type=DataGenerationType.LABEL_GENERATION,
            data_generation_task_type=DataGenerationTaskType.SUMMARIZATION,
            teacher_model_endpoint_connection=ServerlessConnection(
                name="Llama-3-1-405B-Instruct-BASE", endpoint="http://foo.com", api_key="FAKEKEY"
            ),
            student_model=Input(
                type="mlflow_model",
                path="azureml://registries/azureml-meta/models/Meta-Llama-3.1-8B-Instruct/versions/1",
            ),
            training_data=Input(type="uri_file", path="train_data:1"),
            validation_data=Input(type="uri_file", path="validation_data:1"),
            teacher_model_settings=TeacherModelSettings(
                inference_parameters={"frequency_penalty": 1, "presence_penalty": 1},
                endpoint_request_settings=EndpointRequestSettings(min_endpoint_success_ratio=0.9),
            ),
            prompt_settings=PromptSettings(
                enable_chain_of_thought=False, enable_chain_of_density=True, max_len_summary=220
            ),
            hyperparameters={"num_train_epochs": "3"},
            experiment_name="Distillation-Math-Test-1234",
            name="distillation_job_test",
            description="Distill Llama 3.1 8b model using Llama 3.1 405B teacher model",
            outputs={"registered_model": Output(type="mlflow_model", name="llama-3-1-8b-distilled-1234")},
            resources=ResourceConfiguration(instance_type="Standard_D2_v3"),
        )
        sdk_rest_object = DistillationJob._to_rest_object(distillation_job)

        path = "./tests/test_configs/distillation_job/mock_distillation_job_input.yaml"
        cli_rest_object = loaded_distillation_job_as_rest_obj(path)
        assert sdk_rest_object == cli_rest_object

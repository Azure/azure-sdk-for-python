import pytest

from azure.ai.ml import Input
from azure.ai.ml.constants import AssetTypes, DataGenerationTaskType, DataGenerationType
from azure.ai.ml.model_customization import distillation
from azure.ai.ml.entities import NoneCredentialConfiguration, ServerlessConnection, WorkspaceConnection
from azure.ai.ml.entities._job.distillation.distillation_job import DistillationJob
from azure.ai.ml.entities._job.distillation.endpoint_request_settings import EndpointRequestSettings
from azure.ai.ml.entities._job.distillation.prompt_settings import PromptSettings


class TestDistillationJob:
    def test_distillation_function(self):
        distillation_job = distillation(
            experiment_name="llama-test",
            data_generation_type=DataGenerationType.DATA_GENERATION,
            data_generation_task_type=DataGenerationTaskType.SUMMARIZATION,
            teacher_model_endpoint_connection=ServerlessConnection(name="llama", endpoint="None", api_key="TESTKEY"),
            student_model="llama-student",
            training_data="azureml:something:1",
        )

        assert isinstance(distillation_job, DistillationJob), "distillation job not created correctly"

        distillation_job.validation_data = Input(type=AssetTypes.URI_FILE, path="bar_path")
        distillation_job.set_prompt_settings(prompt_settings=PromptSettings(enable_chain_of_density=True))
        distillation_job.set_teacher_model_settings(
            inference_parameters={"temperature": 0.2, "max_tokens": 100},
            endpoint_request_settings=EndpointRequestSettings(request_batch_size=2),
        )
        distillation_job.set_finetuning_settings(hyperparameters={"num_epochs": 2, "learning_rate": 0.00002})

        assert distillation_job.prompt_settings == PromptSettings(
            enable_chain_of_density=True
        ), "Prompt settings not set correctly"
        assert distillation_job.teacher_model_settings.inference_parameters == {
            "temperature": 0.2,
            "max_tokens": 100,
        }, "Inference parameters not set correctly"
        assert distillation_job.teacher_model_settings.endpoint_request_settings == EndpointRequestSettings(
            request_batch_size=2
        ), "Endpoint request settings not set correctly"
        assert distillation_job.hyperparameters == {
            "num_epochs": 2,
            "learning_rate": 0.00002,
        }, "Hyperparameters not set correctly"

    def test_distillation_function_fails_no_training_data(self):
        with pytest.raises(ValueError) as exception:
            _ = distillation(
                experiment_name="llama-test",
                data_generation_type=DataGenerationType.LABEL_GENERATION,
                data_generation_task_type=DataGenerationTaskType.NLI,
                teacher_model_endpoint_connection=WorkspaceConnection(
                    type="custom", credentials=NoneCredentialConfiguration(), name="llama", target="None"
                ),
                student_model="llama-student",
                validation_data="azureml:foo:1",
            )
        error_msg = (
            f"Training data can not be None when data generation type is set to {DataGenerationType.LABEL_GENERATION}."
        )
        assert str(exception.value) == error_msg

    def test_distillation_function_fails_no_validation_data(self):
        with pytest.raises(ValueError) as exception:
            _ = distillation(
                experiment_name="llama-test",
                data_generation_type=DataGenerationType.LABEL_GENERATION,
                data_generation_task_type=DataGenerationTaskType.NLI,
                teacher_model_endpoint_connection=WorkspaceConnection(
                    type="custom", credentials=NoneCredentialConfiguration(), name="llama", target="None"
                ),
                student_model="llama-student",
                training_data="azureml:foo:1",
            )
        error_msg = f"Validation data can not be None when data generation type is set to {DataGenerationType.LABEL_GENERATION}."
        assert str(exception.value) == error_msg

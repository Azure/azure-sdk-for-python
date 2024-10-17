import pytest

from azure.ai.ml import Input, distillation
from azure.ai.ml.constants import AssetTypes, DataGenerationTaskType, DataGenerationType
from azure.ai.ml.distillation import DistillationPromptSettings, EndpointRequestSettings
from azure.ai.ml.entities._job.distillation.distillation_job import DistillationJob


class TestDistillationJob:
    def test_distillation_function(self):
        distillation_job = distillation(
            experiment_name="llama-test",
            data_generation_type=DataGenerationType.DataGeneration,
            data_generation_task_type=DataGenerationTaskType.SUMMARIZATION,
            teacher_model_endpoint="test-endpoint",
            student_model="llama-student",
            training_data=Input(type=AssetTypes.URI_FILE, path="foo_path"),
        )

        assert isinstance(distillation_job, DistillationJob), "distillation job not created correctly"

        distillation_job.validation_data = Input(type=AssetTypes.URI_FILE, path="bar_path")
        distillation_job.set_prompt_settings(prompt_settings=DistillationPromptSettings(enable_chain_of_density=True))
        distillation_job.set_teacher_model_settings(
            inference_parameters={"temperature": 0.2, "max_tokens": 100},
            endpoint_request_settings=EndpointRequestSettings(request_batch_size=2),
        )
        distillation_job.set_finetuning_settings(hyperparameters={"num_epochs": 2, "learning_rate": 0.00002})
        assert distillation_job.prompt_settings == DistillationPromptSettings(
            enable_chain_of_density=True
        ), "Prompt settings not set correctly"
        assert distillation_job.inference_parameters == {
            "temperature": 0.2,
            "max_tokens": 100,
        }, "Inference parameters not set correctly"
        assert distillation_job.endpoint_request_settings == EndpointRequestSettings(
            request_batch_size=2
        ), "Endpoint request settings not set correctly"
        assert distillation_job.hyperparameters == {
            "num_epochs": 2,
            "learning_rate": 0.00002,
        }, "Hyperparameters not set correctly"

    def test_distillation_function_fails(self):
        with pytest.raises(ValueError):
            _ = distillation(
                experiment_name="llama-test",
                data_generation_type=DataGenerationType.LabelGeneration,
                data_generation_task_type=DataGenerationTaskType.NLI,
                teacher_model_endpoint="test-endpoint",
                student_model="llama-student",
            )

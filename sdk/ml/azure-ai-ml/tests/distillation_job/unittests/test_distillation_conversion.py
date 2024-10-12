import pytest

from azure.ai.ml._restclient.v2024_01_01_preview.models import MLFlowModelJobInput, UriFileJobInput
from azure.ai.ml.constants import DataGenerationTaskType
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.distillation.distillation_job import DistillationJob
from azure.ai.ml.entities._job.distillation.distillation_types import (
    DistillationPromptSettings,
    EndpointRequestSettings,
)
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration


class TestDistillationJobConversion:
    @pytest.mark.parametrize(
        "data_generation_task_type",
        [
            DataGenerationTaskType.NLI,
            # DataGenerationTaskType.NLU_QA,
            # DataGenerationTaskType.CONVERSATION,
            # DataGenerationTaskType.MATH,
            # DataGenerationTaskType.SUMMARIZATION,
        ],
    )
    def test_distillation_job_conversation(self, data_generation_task_type: str):
        distillation_job = DistillationJob(
            data_generation_type="Label_Generation",
            data_generation_task_type=data_generation_task_type,
            teacher_model_endpoint="foo_bar",
            student_model=Input(
                type=AssetTypes.MLFLOW_MODEL,
                path="azureml://registries/azureml-meta/models/Meta-Llama-3.1-8B-Instruct/versions/1",
            ),
            training_data=Input(type=AssetTypes.URI_FILE, path="foo.json1"),
            validation_data=None,
            inference_parameters={"temperature": 0.1},
            endpoint_request_settings=EndpointRequestSettings(request_batch_size=2, min_endpoint_success_ratio=0.8),
            prompt_settings=DistillationPromptSettings(enable_chain_of_thought=True),
            hyperparameters={"bar": "baz"},
            name="llama-distillation",
            experiment_name="bar_experiment",
            outputs={"registered_model": Output(type="mlflow_model", name="llama-distilled")},
        )

        rest_object = distillation_job._to_rest_object()
        assert isinstance(
            rest_object.properties.fine_tuning_details.model, MLFlowModelJobInput
        ), "Model is not MLFlowModelJobInput"
        assert isinstance(
            rest_object.properties.fine_tuning_details.training_data, UriFileJobInput
        ), "Training data is not UriFileJobInput"

        original_object = DistillationJob._from_rest_object(rest_object)
        # assert distillation_job == original_object, "Conversion to/from rest object failed"
        assert (
            original_object.data_generation_task_type.lower() == data_generation_task_type.lower()
        ), "Data Generation Task Type not set correctly"
        assert original_object.data_generation_type == "Label_Generation", "Data Generation Type not set correctly"

        assert original_object.teacher_model_endpoint == "foo_bar", "Teacher model endpoint name not set correctly"

        assert isinstance(original_object.student_model, Input), "Student model is not Input"
        assert original_object.student_model.type == AssetTypes.MLFLOW_MODEL, "Student model type is not mlflow_model"
        assert (
            original_object.student_model.path
            == "azureml://registries/azureml-meta/models/Meta-Llama-3.1-8B-Instruct/versions/1"
        ), "Student model path not set correctly"

        assert isinstance(original_object.training_data, Input), "Training data is not Input"
        assert original_object.training_data.type == AssetTypes.URI_FILE, "Training data type not set correctly"
        assert original_object.training_data.path == "foo.json1", "Training data path not set correctly"
        assert original_object.validation_data is None, "Validation data not set correctly"

        assert original_object._inference_parameters == {"temperature": 0.1}, "Inference parameters not set correctly"
        assert original_object._hyperparameters == {"bar": "baz"}, "Hyperparameters not set correctly"
        assert original_object.name == "llama-distillation", "Name not set correctly"
        assert original_object.experiment_name == "bar_experiment", "Experiment name not set correctly"

        assert isinstance(
            original_object._endpoint_request_settings, EndpointRequestSettings
        ), "Endpoint request settings is not EndpointRequestSettings"
        assert (
            original_object._endpoint_request_settings.request_batch_size == 2
        ), "Request batch size not set correctly"
        assert (
            original_object._endpoint_request_settings.min_endpoint_success_ratio == 0.8
        ), "Min endpoint success ration not set correctly"

        assert isinstance(
            original_object._prompt_settings, DistillationPromptSettings
        ), "Prompt settings is not DistillationPromptSettings"
        assert original_object._prompt_settings.enable_chain_of_thought, "Chain of thought not set correctly"
        assert not original_object._prompt_settings.enable_chain_of_density, "Chain of density not set correctly"
        assert original_object._prompt_settings.max_len_summary == 80, "Custom prompt not set correctly"

        assert distillation_job == original_object, "Conversion to/from rest object failed"

    @pytest.mark.parametrize(
        "data_generation_task_type",
        [
            DataGenerationTaskType.NLI,
            # DataGenerationTaskType.NLU_QA,
            # DataGenerationTaskType.CONVERSATION,
            # DataGenerationTaskType.MATH,
            # DataGenerationTaskType.SUMMARIZATION,
        ],
    )
    def test_distillation_job_read_from_wire(self, data_generation_task_type: str):
        distillation_job = DistillationJob(
            data_generation_type="Data_Generation",
            data_generation_task_type=data_generation_task_type,
            teacher_model_endpoint="llama-teacher",
            student_model=Input(
                type=AssetTypes.MLFLOW_MODEL,
                path="azureml://registries/azureml-meta/models/Meta-Llama-3.1-8B/versions/1",
            ),
            training_data=Input(type=AssetTypes.URI_FILE, path="./alex_dataset/math_train.json1"),
            validation_data=Input(type=AssetTypes.URI_FILE, path="./alex_dataset/math_val.json1"),
            inference_parameters={"max_tokens": 248},
            endpoint_request_settings=None,
            prompt_settings=DistillationPromptSettings(enable_chain_of_thought=True),
            hyperparameters=None,
            resources=ResourceConfiguration(instance_type="Standard_Bar"),
            name="llama-distillation",
            experiment_name="llama-experiment",
            tags={"bar": "baz"},
            properties={"foo": "baz"},
            outputs={"registered_model": Output(type="mlflow_model", name="llama-distilled")},
        )

        dict_object = distillation_job._to_dict()
        print(f"Dict object is {dict_object}")
        assert dict_object["data_generation_type"] == "data_generation", "Data Generation Task not set correctly"
        assert (
            dict_object["data_generation_task_type"] == data_generation_task_type
        ), "Data Generation Task Type not set correctly"
        assert dict_object["name"] == "llama-distillation", "Name not set correctly"
        assert dict_object["experiment_name"] == "llama-experiment", "Experiment name not set correctly"
        assert dict_object["tags"] == {"bar": "baz"}, "Tags not set correctly"
        assert dict_object["properties"]["foo"] == "baz", "Properties not set correctly"

        assert dict_object["teacher_model_endpoint"] == "llama-teacher", "Teacher model endpoint name not set correctly"
        assert dict_object["student_model"]["type"] == "mlflow_model", "Student model type not set correctly"
        assert (
            dict_object["student_model"]["path"]
            == "azureml://registries/azureml-meta/models/Meta-Llama-3.1-8B/versions/1"
        ), "Student model path not set correctly"

        assert dict_object["training_data"]["type"] == AssetTypes.URI_FILE, "Training data type not set correctly"
        assert (
            dict_object["training_data"]["path"] == "azureml:./alex_dataset/math_train.json1"
        ), "Training data path not set correctly"
        assert dict_object["validation_data"]["type"] == AssetTypes.URI_FILE, "Validation data type not set correctly"
        assert (
            dict_object["validation_data"]["path"] == "azureml:./alex_dataset/math_val.json1"
        ), "Validation data path not set correctly"

        assert dict_object["inference_parameters"] == {"max_tokens": 248}, "Inference parameters not set correctly"
        assert dict_object["prompt_settings"]["enable_chain_of_thought"], "Enable chain of thought not set correctly"
        assert not dict_object["prompt_settings"][
            "enable_chain_of_density"
        ], "Enable chain of density not set correctly"
        assert dict_object["prompt_settings"]["max_len_summary"] == 80, "Max len summary not set correctly"

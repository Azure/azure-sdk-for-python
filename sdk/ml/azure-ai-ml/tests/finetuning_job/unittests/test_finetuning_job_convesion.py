from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input, Output
from typing import Optional, Dict
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    UriFileJobInput,
    MLFlowModelJobInput,
)
from azure.ai.ml.constants._job.finetuning import FineTuningTaskTypes
from azure.ai.ml.entities._job.finetuning.custom_model_finetuning_job import CustomModelFineTuningJob
from azure.ai.ml.entities._job.finetuning.azure_openai_finetuning_job import AzureOpenAIFineTuningJob
from azure.ai.ml.entities._job.finetuning.azure_openai_hyperparameters import AzureOpenAIHyperparameters
import pytest


@pytest.mark.finetuning_test
@pytest.mark.unittest
class TestCustomModelFineTuningJob:
    @pytest.mark.parametrize(
        "task",
        [
            FineTuningTaskTypes.CHAT_COMPLETION,
            FineTuningTaskTypes.TEXT_COMPLETION,
            FineTuningTaskTypes.TEXT_CLASSIFICATION,
            FineTuningTaskTypes.QUESTION_ANSWERING,
            FineTuningTaskTypes.TEXT_SUMMARIZATION,
            FineTuningTaskTypes.TOKEN_CLASSIFICATION,
            FineTuningTaskTypes.TEXT_TRANSLATION,
            FineTuningTaskTypes.IMAGE_CLASSIFICATION,
            FineTuningTaskTypes.IMAGE_INSTANCE_SEGMENTATION,
            FineTuningTaskTypes.IMAGE_OBJECT_DETECTION,
            FineTuningTaskTypes.VIDEO_MULTI_OBJECT_TRACKING,
        ],
    )
    def test_custom_model_finetuning_job_conversion(self, task: str):
        # Create Custom Model FineTuning Job
        custom_model_finetuning_job = self._get_custom_model_finetuning_job(
            task=task,
            display_name="llama-display-name",
            training_data=Input(type=AssetTypes.URI_FILE, path="https://foo/bar/train.csv"),
            validation_data=Input(type=AssetTypes.URI_FILE, path="https://foo/bar/test.csv"),
            hyperparameters={"foo": "bar"},
            model=Input(
                type=AssetTypes.MLFLOW_MODEL, path="azureml://registries/azureml-meta/models/Llama-2-7b/versions/9"
            ),
            name="llama-finetuning",
            experiment_name="foo_exp",
            tags={"foo_tag": "bar"},
            properties={"my_property": True},
            outputs={"registered_model": Output(type="mlflow_model", name="llama-finetune-registered")},
        )
        rest_obj = custom_model_finetuning_job._to_rest_object()
        assert isinstance(
            rest_obj.properties.fine_tuning_details.model, MLFlowModelJobInput
        ), "Model is not MLFlowModelJobInput"
        assert isinstance(
            rest_obj.properties.fine_tuning_details.training_data, UriFileJobInput
        ), "Training data is not UriFileJobInput"
        assert isinstance(
            rest_obj.properties.fine_tuning_details.validation_data, UriFileJobInput
        ), "Validation data is not UriFileJobInput"

        original_obj = CustomModelFineTuningJob._from_rest_object(rest_obj)
        assert custom_model_finetuning_job == original_obj, "Conversion to/from rest object failed"
        assert original_obj.task.lower() == task.lower(), "Task not set correctly"
        assert original_obj.display_name == "llama-display-name", "Display name not set correctly"
        assert original_obj.name == "llama-finetuning", "Name not set correctly"
        assert original_obj.experiment_name == "foo_exp", "Experiment name not set correctly"
        assert original_obj.tags == {"foo_tag": "bar"}, "Tags not set correctly"
        assert original_obj.properties == {"my_property": True}, "Properties not set correctly"
        # check if the original job inputs were restored
        assert isinstance(original_obj.training_data, Input), "Training data is not Input"
        assert original_obj.training_data.type == AssetTypes.URI_FILE, "Training data type not set correctly"
        assert original_obj.training_data.path == "https://foo/bar/train.csv", "Training data path not set correctly"
        assert isinstance(original_obj.validation_data, Input), "Test data is not Input"
        assert original_obj.validation_data.type == AssetTypes.URI_FILE, "Test data type not set correctly"
        assert original_obj.validation_data.path == "https://foo/bar/test.csv", "Test data path not set correctly"
        assert original_obj.hyperparameters == {"foo": "bar"}, "Hyperparameters not set correctly"
        assert isinstance(original_obj.model, Input), "Model is not Input"
        assert original_obj.model.type == AssetTypes.MLFLOW_MODEL, "Model type not set correctly"
        assert (
            original_obj.model.path == "azureml://registries/azureml-meta/models/Llama-2-7b/versions/9"
        ), "Model path not set correctly"

        assert isinstance(original_obj.outputs["registered_model"], Output), "Output is not Output"
        mlflow_model_output = original_obj.outputs["registered_model"]
        assert mlflow_model_output.type == "mlflow_model", "Output type not set correctly"
        assert mlflow_model_output.name == "llama-finetune-registered", "Output name not set correctly"

    @pytest.mark.parametrize(
        "task",
        [
            FineTuningTaskTypes.CHAT_COMPLETION,
            FineTuningTaskTypes.TEXT_COMPLETION,
            FineTuningTaskTypes.TEXT_CLASSIFICATION,
            FineTuningTaskTypes.QUESTION_ANSWERING,
            FineTuningTaskTypes.TEXT_SUMMARIZATION,
            FineTuningTaskTypes.TOKEN_CLASSIFICATION,
            FineTuningTaskTypes.TEXT_TRANSLATION,
            FineTuningTaskTypes.IMAGE_CLASSIFICATION,
            FineTuningTaskTypes.IMAGE_INSTANCE_SEGMENTATION,
            FineTuningTaskTypes.IMAGE_OBJECT_DETECTION,
            FineTuningTaskTypes.VIDEO_MULTI_OBJECT_TRACKING,
        ],
    )
    def test_custom_model_finetuning_job_read_from_wire(self, task: str):
        custom_model_finetuning_job = self._get_custom_model_finetuning_job(
            task=task,
            display_name="llama-display-name",
            training_data=Input(type=AssetTypes.URI_FILE, path="./samsum_dataset/small_train.jsonl"),
            validation_data=Input(type=AssetTypes.URI_FILE, path="./samsum_dataset/small_validation.jsonl"),
            hyperparameters={"foo": "bar"},
            model=Input(
                type=AssetTypes.MLFLOW_MODEL, path="azureml://registries/azureml-meta/models/Llama-2-7b/versions/9"
            ),
            name="llama-finetuning",
            experiment_name="foo_exp",
            tags={"foo_tag": "bar"},
            properties={"my_property": True},
            outputs={"registered_model": Output(type="mlflow_model", name="llama-finetune-registered")},
        )
        dict_obj = custom_model_finetuning_job._to_dict()
        assert dict_obj["task"].lower() == task.lower(), "Task not set correctly"
        assert dict_obj["display_name"] == "llama-display-name", "Display name not set correctly"
        assert dict_obj["name"] == "llama-finetuning", "Name not set correctly"
        assert dict_obj["experiment_name"] == "foo_exp", "Experiment name not set correctly"
        assert dict_obj["tags"] == {"foo_tag": "bar"}, "Tags not set correctly"
        assert dict_obj["properties"]["my_property"] == "True", "Properties not set correctly"
        # check if the original job inputs were restored
        assert dict_obj["training_data"]["type"] == AssetTypes.URI_FILE, "Training data type not set correctly"
        assert (
            dict_obj["training_data"]["path"] == "azureml:./samsum_dataset/small_train.jsonl"
        ), "Training data path not set correctly"
        assert dict_obj["validation_data"]["type"] == AssetTypes.URI_FILE, "validation data type not set correctly"
        assert (
            dict_obj["validation_data"]["path"] == "azureml:./samsum_dataset/small_validation.jsonl"
        ), "Validation data path not set correctly"
        assert dict_obj["hyperparameters"] == {"foo": "bar"}, "Hyperparameters not set correctly"
        assert dict_obj["model"]["type"] == AssetTypes.MLFLOW_MODEL, "Model type not set correctly"
        assert (
            dict_obj["model"]["path"] == "azureml://registries/azureml-meta/models/Llama-2-7b/versions/9"
        ), "Model path not set correctly"

    @pytest.mark.parametrize(
        "task",
        [
            FineTuningTaskTypes.CHAT_COMPLETION,
            FineTuningTaskTypes.TEXT_COMPLETION,
            FineTuningTaskTypes.TEXT_CLASSIFICATION,
            FineTuningTaskTypes.QUESTION_ANSWERING,
            FineTuningTaskTypes.TEXT_SUMMARIZATION,
            FineTuningTaskTypes.TOKEN_CLASSIFICATION,
            FineTuningTaskTypes.TEXT_TRANSLATION,
            FineTuningTaskTypes.IMAGE_CLASSIFICATION,
            FineTuningTaskTypes.IMAGE_INSTANCE_SEGMENTATION,
            FineTuningTaskTypes.IMAGE_OBJECT_DETECTION,
            FineTuningTaskTypes.VIDEO_MULTI_OBJECT_TRACKING,
        ],
    )
    def test_azure_openai_finetuning_job_conversion(self, task: str):
        # Create Custom Model FineTuning Job
        custom_model_finetuning_job = self._get_azure_openai_finetuning_job(
            task=task,
            training_data=Input(type=AssetTypes.URI_FILE, path="https://foo/bar/train.csv"),
            validation_data=Input(type=AssetTypes.URI_FILE, path="https://foo/bar/test.csv"),
            hyperparameters=AzureOpenAIHyperparameters(batch_size=2, n_epochs=3, learning_rate_multiplier=0.5),
            model=Input(
                type=AssetTypes.MLFLOW_MODEL, path="azureml://registries/azure-openai-v2/models/gpt-4/versions/1"
            ),
            name="gpt4-finetuning",
            experiment_name="foo_exp",
            tags={"foo_tag": "bar"},
            properties={"my_property": True},
        )
        rest_obj = custom_model_finetuning_job._to_rest_object()
        assert isinstance(
            rest_obj.properties.fine_tuning_details.model, MLFlowModelJobInput
        ), "Model is not MLFlowModelJobInput"
        assert isinstance(
            rest_obj.properties.fine_tuning_details.training_data, UriFileJobInput
        ), "Training data is not UriFileJobInput"
        assert isinstance(
            rest_obj.properties.fine_tuning_details.validation_data, UriFileJobInput
        ), "Validation data is not UriFileJobInput"

        original_obj = AzureOpenAIFineTuningJob._from_rest_object(rest_obj)
        assert custom_model_finetuning_job == original_obj, "Conversion to/from rest object failed"
        assert original_obj.task.lower() == task.lower(), "Task not set correctly"
        assert original_obj.name == "gpt4-finetuning", "Name not set correctly"
        assert original_obj.experiment_name == "foo_exp", "Experiment name not set correctly"
        assert original_obj.tags == {"foo_tag": "bar"}, "Tags not set correctly"
        assert original_obj.properties == {"my_property": True}, "Properties not set correctly"
        # check if the original job inputs were restored
        assert isinstance(original_obj.training_data, Input), "Training data is not Input"
        assert original_obj.training_data.type == AssetTypes.URI_FILE, "Training data type not set correctly"
        assert original_obj.training_data.path == "https://foo/bar/train.csv", "Training data path not set correctly"
        assert isinstance(original_obj.validation_data, Input), "Test data is not Input"
        assert original_obj.validation_data.type == AssetTypes.URI_FILE, "Test data type not set correctly"
        assert original_obj.validation_data.path == "https://foo/bar/test.csv", "Test data path not set correctly"
        assert original_obj.hyperparameters.batch_size == 2, "Batch size not set correctly"
        assert original_obj.hyperparameters.n_epochs == 3, "n_epochs not set correctly"
        assert (
            original_obj.hyperparameters.learning_rate_multiplier == 0.5
        ), "learning_rate_multiplier not set correctly"
        assert isinstance(original_obj.model, Input), "Model is not Input"
        assert original_obj.model.type == AssetTypes.MLFLOW_MODEL, "Model type not set correctly"
        assert (
            original_obj.model.path == "azureml://registries/azure-openai-v2/models/gpt-4/versions/1"
        ), "Model path not set correctly"

    def _get_custom_model_finetuning_job(
        self,
        *,
        model: Input,
        task: str,
        training_data: Input,
        validation_data: Optional[Input] = None,
        hyperparameters: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> CustomModelFineTuningJob:
        custom_model_finetuning_job = CustomModelFineTuningJob(
            task=task,
            model=model,
            training_data=training_data,
            validation_data=validation_data,
            hyperparameters=hyperparameters,
            **kwargs,
        )
        return custom_model_finetuning_job

    def _get_azure_openai_finetuning_job(
        self,
        *,
        model: Input,
        task: str,
        training_data: Input,
        validation_data: Optional[Input] = None,
        hyperparameters: Optional[AzureOpenAIHyperparameters] = None,
        **kwargs,
    ) -> AzureOpenAIFineTuningJob:
        custom_model_finetuning_job = AzureOpenAIFineTuningJob(
            task=task,
            model=model,
            training_data=training_data,
            validation_data=validation_data,
            hyperparameters=hyperparameters,
            **kwargs,
        )
        return custom_model_finetuning_job

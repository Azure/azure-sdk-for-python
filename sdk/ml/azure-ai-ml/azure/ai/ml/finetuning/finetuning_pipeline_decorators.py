"""Entrypoints for creating F tasks."""

from typing import Optional, Dict
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._builders.base_node import pipeline_node_decorator
from azure.ai.ml.entities._job.finetuning.custom_model_finetuning import CustomModelFineTuningJob
from azure.ai.ml.entities._job.finetuning.azure_openai_finetuning import AzureOpenAIFineTuningJob
from azure.ai.ml._restclient.v2024_01_01_preview.models import ModelProvider, AzureOpenAiHyperParameters


@pipeline_node_decorator
def azure_open_ai(
    *,
    model: Input,
    task: str,
    training_data: Input,
    validation_data: Optional[Input] = None,
    hyperparameters: Optional[AzureOpenAiHyperParameters] = None,
    **kwargs,
) -> AzureOpenAIFineTuningJob:
    azure_openai_finetuning_job = AzureOpenAIFineTuningJob()
    azure_openai_finetuning_job.model = model
    azure_openai_finetuning_job.task = task
    azure_openai_finetuning_job.training_data = training_data
    azure_openai_finetuning_job.validation_data = validation_data
    azure_openai_finetuning_job.hyperparameters = hyperparameters


@pipeline_node_decorator
def custom(
    *,
    model: Input,
    task: str,
    training_data: Input,
    validation_data: Optional[Input] = None,
    hyperparameters: Optional[Dict[str, str]] = None,
    **kwargs,
) -> CustomModelFineTuningJob:
    custom_model_finetuning_job = CustomModelFineTuningJob()
    custom_model_finetuning_job.model = model
    custom_model_finetuning_job.task = task
    custom_model_finetuning_job.training_data = training_data
    custom_model_finetuning_job.validation_data = validation_data
    custom_model_finetuning_job.hyperparameters = hyperparameters

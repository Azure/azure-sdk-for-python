# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entrypoint for creating Distillation task."""
from typing import Any, Dict, Optional, Union

from azure.ai.ml.constants import DataGenerationType
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.distillation.distillation_job import DistillationJob
from azure.ai.ml.entities._job.distillation.distillation_types import PromptSettings, TeacherModelSettings
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration
from azure.ai.ml.entities._workspace.connections.workspace_connection import WorkspaceConnection


def distillation(
    experiment_name: str,
    data_generation_type: str,
    data_generation_task_type: str,
    teacher_model_endpoint_connection: WorkspaceConnection,
    student_model: Union[Input, str],
    training_data: Optional[Union[Input, str]] = None,
    validation_data: Optional[Union[Input, str]] = None,
    teacher_model_settings: Optional[TeacherModelSettings] = None,
    prompt_settings: Optional[PromptSettings] = None,
    hyperparameters: Optional[Dict] = None,
    resources: Optional[ResourceConfiguration] = None,
    **kwargs: Any,
) -> "DistillationJob":
    """Function to create a Distillation job.

    A distillation job is used to transfer knowledge from a teacher model to student model by a two step process of
    generating synthetic data from the teacher model and then finetuning the student model with the generated
    synthetic data.

    :keyword experiment_name: The name of the experiment.
    :paramtype experiment_name: str
    :keyword data_generation_type: The type of data generation to perform.

            Acceptable values: data_generation, label_generation
    :paramtype data_generation_type: str
    :keyword data_generation_task_type: The type of data to generate

            Acceptable values: NLI, NLU_QA, CONVERSATION, MATH, SUMMARIZATION
    :paramtype: data_generation_task_type: str
    :keyword teacher_model_endpoint: The name of the teacher model endpoint to use
    :paramtype: teacher_model_endpoint: str
    :keyword student_model: The model to train
    :paramtype student_model: Input
    :keyword training_data: The training data to use. Training data can be None if `data_generation_type` is
            `data_generation`. Otherwise, training data should contain the question but not the labels.
    :type training_data: Optional[Input]
    :keyword validation_data: The validation data to use. Validation data can be None and will created by
            partitioning the training_data. If validation data is not None, it should contain the questions but not
            the labels.
    :paramtype validation_data: Optional[Input]
    :keyword teacher_model_settings: The settings for the teacher model. Accepts both the inference parameters and
            endpoint settings.

            Acceptable keys for inference parameters: temperature, max_tokens, top_p, frequency_penalty,
            presence_penalty, stop

    :paramtype teacher_model_settings: Optional[TeacherModelSettings]
    :keyword prompt_settings: The settings for the prompt that affect the system prompt used for data generation.
    :paramtype prompt_settings: Optional[DistillationPromptSettings]
    :keyword hyperparameters: The hyperparameters to use for finetuning.
    :paramtype hyperparameters: Optional[Dict]
    :keyword resources: The compute resource to use for the data generation step in the distillation job.
    :paramtype resources: Optional[ResourceConfiguration]
    """
    if isinstance(student_model, str):
        student_model = Input(type=AssetTypes.URI_FILE, path=student_model)
    if isinstance(training_data, str):
        training_data = Input(type=AssetTypes.URI_FILE, path=training_data)
    if isinstance(validation_data, str):
        validation_data = Input(type=AssetTypes.URI_FILE, path=validation_data)

    if training_data is None and data_generation_type == DataGenerationType.LabelGeneration:
        raise ValueError(
            f"Training data can only be None when data generation type is set to "
            f"{DataGenerationType.DataGeneration}."
        )

    return DistillationJob(
        data_generation_type=data_generation_type,
        data_generation_task_type=data_generation_task_type,
        teacher_model_endpoint_connection=teacher_model_endpoint_connection,
        student_model=student_model,
        training_data=training_data,
        validation_data=validation_data,
        teacher_model_settings=teacher_model_settings,
        prompt_settings=prompt_settings,
        hyperparameters=hyperparameters,
        resources=resources,
        experiment_name=experiment_name,
        **kwargs,
    )

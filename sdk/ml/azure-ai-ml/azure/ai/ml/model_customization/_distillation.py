# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entrypoint for creating Distillation task."""
from typing import Any, Dict, Optional, Union

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants import DataGenerationType
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.distillation.distillation_job import DistillationJob
from azure.ai.ml.entities._job.distillation.prompt_settings import PromptSettings
from azure.ai.ml.entities._job.distillation.teacher_model_settings import TeacherModelSettings
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration
from azure.ai.ml.entities._workspace.connections.workspace_connection import WorkspaceConnection


@experimental
def distillation(
    *,
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

        Acceptable values: label_generation
    :paramtype data_generation_type: str
    :keyword data_generation_task_type: The type of data to generate

        Acceptable values: NLI, NLU_QA, CONVERSATION, MATH, SUMMARIZATION
    :paramtype data_generation_task_type: str
    :keyword teacher_model_endpoint_connection: The kind of teacher model connection that includes the name, endpoint
        url, and api_key.
    :paramtype teacher_model_endpoint_connection: WorkspaceConnection
    :keyword student_model: The model to train
    :paramtype student_model: typing.Union[Input, str]
    :keyword training_data: The training data to use. Should contain the questions but not the labels, defaults to None
    :paramtype training_data: typing.Optional[typing.Union[Input, str]], optional
    :keyword validation_data: The validation data to use. Should contain the questions but not the labels, defaults to
        None
    :paramtype validation_data: typing.Optional[typing.Union[Input, str]], optional
    :keyword teacher_model_settings: The settings for the teacher model. Accepts both the inference parameters and
        endpoint settings, defaults to None

        Acceptable keys for inference parameters: temperature, max_tokens, top_p, frequency_penalty, presence_penalty,
        stop
    :paramtype teacher_model_settings: typing.Optional[TeacherModelSettings], optional
    :keyword prompt_settings: The settings for the prompt that affect the system prompt used for data generation,
        defaults to None
    :paramtype prompt_settings: typing.Optional[PromptSettings], optional
    :keyword hyperparameters: The hyperparameters to use for finetuning, defaults to None
    :paramtype hyperparameters: typing.Optional[typing.Dict], optional
    :keyword resources: The compute resource to use for the data generation step in the distillation job, defaults to
        None
    :paramtype resources: typing.Optional[ResourceConfiguration], optional
    :raises ValueError: Raises ValueError if there is no training data and data generation type is 'label_generation'
    :return: A DistillationJob to submit
    :rtype: DistillationJob
    """
    if isinstance(student_model, str):
        student_model = Input(type=AssetTypes.URI_FILE, path=student_model)
    if isinstance(training_data, str):
        training_data = Input(type=AssetTypes.URI_FILE, path=training_data)
    if isinstance(validation_data, str):
        validation_data = Input(type=AssetTypes.URI_FILE, path=validation_data)

    if training_data is None and data_generation_type == DataGenerationType.LABEL_GENERATION:
        raise ValueError(
            f"Training data can not be None when data generation type is set to "
            f"{DataGenerationType.LABEL_GENERATION}."
        )

    if validation_data is None and data_generation_type == DataGenerationType.LABEL_GENERATION:
        raise ValueError(
            f"Validation data can not be None when data generation type is set to "
            f"{DataGenerationType.LABEL_GENERATION}."
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

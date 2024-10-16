# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entrypoint for creating Distillation task."""
from typing import Any, Dict, Optional, Union

from azure.ai.ml.constants import DataGenerationType
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.distillation.distillation_job import DistillationJob
from azure.ai.ml.entities._job.distillation.distillation_types import (
    DistillationPromptSettings,
    EndpointRequestSettings,
)
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration


def distillation(
    experiment_name: str,
    data_generation_type: str,
    data_generation_task_type: str,
    teacher_model_endpoint: str,
    student_model: Union[Input, str],
    training_data: Optional[Input] = None,
    validation_data: Optional[Input] = None,
    inference_parameters: Optional[Dict] = None,
    endpoint_request_settings: Optional[EndpointRequestSettings] = None,
    prompt_settings: Optional[DistillationPromptSettings] = None,
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
    :keyword inference_parameters: The parameters that each inference request will use when generating synthetic data.

            Acceptable keys: temperature, max_tokens, top_p, frequency_penalty, presence_penalty, stop
    :paramtype inference_parameters: Optional[Dict]
    :keyword endpoint_request_settings: The settings to use for sending requests to the teacher model endpoint.
    :paramtype endpoint_request_settings: Optional[EndpointRequestSettings]
    :keyword prompt_settings: The settings for the prompt that affect the system prompt used for data generation.
    :paramtype prompt_settings: Optional[DistillationPromptSettings]
    :keyword hyperparameters: The hyperparameters to use for finetuning.
    :paramtype hyperparameters: Optional[Dict]
    :keyword resources: The compute resource to use for the data generation step in the distillation job.
    :paramtype resources: Optional[ResourceConfiguration]
    """
    if isinstance(student_model, str):
        student_model = Input(type=AssetTypes.URI_FILE, path=student_model)

    if training_data is None and data_generation_type == DataGenerationType.LabelGeneration:
        raise ValueError(
            f"Training data can only be None when data generation type is set to "
            f"{DataGenerationType.DataGeneration}."
        )

    return DistillationJob(
        data_generation_type=data_generation_type,
        data_generation_task_type=data_generation_task_type,
        teacher_model_endpoint=teacher_model_endpoint,
        student_model=student_model,
        training_data=training_data,
        validation_data=validation_data,
        inference_parameters=inference_parameters,
        endpoint_request_settings=endpoint_request_settings,
        prompt_settings=prompt_settings,
        hyperparameters=hyperparameters,
        resources=resources,
        experiment_name=experiment_name,
        **kwargs,
    )

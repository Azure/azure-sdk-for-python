# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entrypoint for creating Distillation task."""
from typing import Any, Dict, Optional

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
    student_model: Input,
    training_data: Input,
    validation_data: Optional[Input] = None,
    inference_parameters: Optional[Dict] = None,
    endpoint_request_settings: Optional[EndpointRequestSettings] = None,
    prompt_settings: Optional[DistillationPromptSettings] = None,
    hyperparameters: Optional[Dict] = None,
    resources: Optional[ResourceConfiguration] = None,
    **kwargs: Any
) -> "DistillationJob":
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
        **kwargs
    )

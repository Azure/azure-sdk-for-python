# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional, Dict
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.finetuning.custom_model_finetuning_job import (
    CustomModelFineTuningJob,
)
from azure.ai.ml.entities._job.job_resources import JobResources
from azure.ai.ml.entities._job.queue_settings import QueueSettings
from azure.ai.ml._utils._experimental import experimental


@experimental
def create_finetuning_job(
    *,
    model: str,
    task: str,
    training_data: str,
    output_model_name_prefix: str,
    validation_data: Optional[str] = None,
    hyperparameters: Optional[Dict[str, str]] = None,
    compute: Optional[str] = None,
    instance_types: Optional[List[str]] = None,
    job_tier: Optional[str] = None,
    **kwargs,
) -> CustomModelFineTuningJob:

    if not model:
        raise ValueError("model is required")
    if not task:
        raise ValueError("task is required")
    if not training_data:
        raise ValueError("training_data is required")
    if not output_model_name_prefix:
        raise ValueError("output_model_name_prefix is required")

    model_input = Input(
        type=AssetTypes.MLFLOW_MODEL,
        path=model,
    )

    outputs = {"registered_model": Output(type="mlflow_model", name=output_model_name_prefix)}

    # For image tasks this would be mltable, check how to handle this
    training_data_input = Input(
        type=AssetTypes.URI_FILE,
        path=training_data,
    )

    if validation_data:
        validation_data_input = Input(
            type=AssetTypes.URI_FILE,
            path=validation_data,
        )

    job_resources = None
    if instance_types:
        job_resources = JobResources(instance_types=instance_types)

    queue_settings = None
    if job_tier:
        queue_settings = QueueSettings(job_tier=job_tier)

    custom_model_finetuning_job = CustomModelFineTuningJob(
        task=task,
        model=model_input,
        training_data=training_data_input,
        validation_data=validation_data_input,  # pylint: disable=(possibly-used-before-assignment
        hyperparameters=hyperparameters,
        compute=compute,
        resources=job_resources,
        queue_settings=queue_settings,
        outputs=outputs,
        **kwargs,
    )

    return custom_model_finetuning_job

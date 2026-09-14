# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builder for the distillation job entity (smoke serialization suite).

``DistillationJob`` is a private-preview model-customization job whose ``_to_rest_object()`` returns an
``arm_ml_service`` hybrid ``RestFineTuningJob`` (distillation rides the fine-tuning wire envelope). It
was migrated together with the fine-tuning family off the versioned msrest clients.

This case specifically guards the ``properties`` bag: the pre-migration msrest ``FineTuningJob.properties``
was typed ``Dict[str, str]`` and stringified every value on the wire; the arm model preserves native
types, so the entity must stringify the bag itself to stay byte-identical (True -> "True", 0.8 -> "0.8").
"""
from azure.ai.ml.constants import DataGenerationTaskType, DataGenerationType
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.distillation.endpoint_request_settings import EndpointRequestSettings
from azure.ai.ml.entities._job.distillation.prompt_settings import PromptSettings
from azure.ai.ml.entities._workspace.connections.connection_subtypes import ServerlessConnection
from azure.ai.ml.model_customization import distillation


def build_distillation_job():
    """DistillationJob (label-generation, MATH) with teacher/prompt/finetuning settings."""
    job = distillation(
        experiment_name="smoke-distillation",
        data_generation_type=DataGenerationType.LABEL_GENERATION,
        data_generation_task_type=DataGenerationTaskType.MATH,
        teacher_model_endpoint_connection=ServerlessConnection(
            name="smoke-teacher-conn",
            endpoint="https://smoke-teacher.eastus.models.ai.azure.com",
            api_key="smoke-teacher-key",
        ),
        student_model="azureml://registries/azureml-meta/models/Meta-Llama-3.1-8B-Instruct/versions/2",
        training_data=Input(type="uri_file", path="azureml://datastores/workspaceblobstore/paths/train.jsonl"),
        validation_data=Input(type="uri_file", path="azureml://datastores/workspaceblobstore/paths/valid.jsonl"),
        outputs={"registered_model": Output(type="mlflow_model", name="smoke-distilled-model")},
    )
    job.set_teacher_model_settings(
        inference_parameters={"max_tokens": 100, "temperature": "0.7"},
        endpoint_request_settings=EndpointRequestSettings(min_endpoint_success_ratio=0.8),
    )
    job.set_prompt_settings(prompt_settings=PromptSettings(enable_chain_of_thought=True))
    job.set_finetuning_settings(hyperparameters={"learning_rate_multiplier": "0.1"})
    return job


DISTILLATION_BUILDERS = {
    "distillation_label_generation": build_distillation_job,
}

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class AzureMLDistillationProperties:
    EnableDistillation = "azureml.enable_distillation"
    DataGenerationType = "azureml.data_generation_type"
    DataGenerationTaskType = "azureml.data_generation_task_type"
    TeacherModel = "azureml.teacher_model"
    PromptSettings = "azureml.prompt_settings"
    InferenceParameters = "azureml.inference_parameters"
    EndpointRequestSettings = "azureml.endpoint_request_settings"
    InstanceType = "azureml.instance_type"


class EndpointSettings:
    valid_settings = {"request_batch_size", "min_endpoint_success_ratio"}


class PromptSettings:
    valid_settings = {"enable_chain_of_thought", "enable_chain_of_density", "max_len_summary"}

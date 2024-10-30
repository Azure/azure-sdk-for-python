# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class AzureMLDistillationProperties:
    ENABLE_DISTILLATION = "azureml.enable_distillation"
    DATA_GENERATION_TYPE = "azureml.data_generation_type"
    DATA_GENERATION_TASK_TYPE = "azureml.data_generation_task_type"
    TEACHER_MODEL = "azureml.teacher_model"
    INSTANCE_TYPE = "azureml.instance_type"
    CONNECTION_INFORMATION = "azureml.connection_information"


class EndpointSettings:
    VALID_SETTINGS = {"request_batch_size", "min_endpoint_success_ratio"}


class PromptSettingKeys:
    VALID_SETTINGS = {"enable_chain_of_thought", "enable_chain_of_density", "max_len_summary"}

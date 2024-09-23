# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entrypoints for creating AutoML tasks."""
from typing import Optional, Union

from azure.ai.ml.entities._builders.base_node import pipeline_node_decorator
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.synthetic_data_generation.data_job import SyntheticDataGenerationDataTaskJob
from azure.ai.ml.entities._job.synthetic_data_generation.label_job import SyntheticDataGenerationLabelTaskJob
from azure.ai.ml.entities._workspace.connections.connection_subtypes import ServerlessConnection


@pipeline_node_decorator
def label_generation(
    data_generation_task: str,
    data_generation_task_type: str,
    teacher_model_endpoint: Union[ServerlessConnection, str],
    training_data: Input,
    validation_data: Optional[Input] = None,
    inference_parameters: Optional[dict] = None,
    **kwargs
) -> SyntheticDataGenerationLabelTaskJob:
    """Function to create a SyntheticDataGenerationLabelTaskJob.

    :param data_generation_task: The type of synthetic data generation task to perform. Accepted value is
            "Label_Generation".
    :type data_generation_task: Input
    :param data_generation_task_type: The type of synthentic data to create. Possible values include "nli", "nlu_qa",
            "conversational", "math", and "summarization".
    :type data_generation_task_type: str
    :param teacher_model_endpoint: The information to connect to the endpint of the teacher model. Either a
            serverless MaaS connection, which expects the uri and authentication key of the endpoint, or the
            endpoint name is accepted.
    :type teacher_model_endpoint: Union[ServerlessConnection, str]
    :param training_data: The path to the training data
    :type training_data: Input
    :param validation_data: The path to the validation data
    :type validation_data: Optional[Input]
    :param inference_parameters: The parameters to use during inferencing. Example parameters include:
        {
            "temperature": .6,
            "max_tokens": 100
        }
    :type inference_parameters: Optional[dict]

    :return: A job object that can be submitted to an Azure ML compute for execution.
    :rtype: SyntheticDataGenerationLabelTaskJob"""
    return SyntheticDataGenerationLabelTaskJob(
        data_generation_task=data_generation_task,
        data_generation_task_type=data_generation_task_type,
        teacher_model_endpoint=teacher_model_endpoint,
        training_data=training_data,
        validation_data=validation_data,
        inference_parameters=inference_parameters,
        **kwargs
    )


@pipeline_node_decorator
def data_generation(
    data_generation_task: str,
    data_generation_task_type: str,
    teacher_model_endpoint: Union[ServerlessConnection, str],
    training_data: Optional[Input] = None,
    validation_data: Optional[Input] = None,
    inference_parameters: Optional[dict] = None,
    **kwargs
) -> SyntheticDataGenerationDataTaskJob:
    """Function to create a SyntheticDataGenerationDataTaskJob.

    :param data_generation_task: The type of synthetic data generation task to perform. Accepted value is
            "Data_Generation".
    :type data_generation_task: Input
    :param data_generation_task_type: The type of synthentic data to create. Possible values include "nli",
            "nlu_qa", "conversational", "math", and "summarization".
    :type data_generation_task_type: str
    :param teacher_model_endpoint: The information to connect to the endpint of the teacher model. Either a
            serverless MaaS connection, which expects the uri and authentication key of the endpoint, or the endpoint
            name is accepted.
    :type teacher_model_endpoint: Union[ServerlessConnection, str]
    :param training_data: The path to the training data
    :type training_data: Optional[Input]
    :param validation_data: The path to the validation data
    :type validation_data: Optional[Input]
    :param inference_parameters: The parameters to use during inferencing. Example parameters include:
        {
            "temperature": .6,
            "max_tokens": 100
        }
    :type inference_parameters: Optional[dict]

    :return: A job object that can be submitted to an Azure ML compute for execution.
    :rtype: SyntheticDataGenerationDataTaskJob"""
    return SyntheticDataGenerationDataTaskJob(
        data_generation_task=data_generation_task,
        data_generation_task_type=data_generation_task_type,
        teacher_model_endpoint=teacher_model_endpoint,
        training_data=training_data,
        validation_data=validation_data,
        inference_parameters=inference_parameters,
        **kwargs
    )

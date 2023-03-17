# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=redefined-builtin
from typing import Dict, Optional, Union, List
from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import (
    BatchJobResource,
    BatchLoggingLevel,
    DataVersion,
    InferenceDataInputBase,
    JobInput,
    JobOutputV2,
    BatchJob as RestBatchJob,
)
from azure.ai.ml.entities._job.compute_configuration import ComputeConfiguration
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings

# pylint: disable=too-many-instance-attributes
class BatchJob(object):
    """Batch jobs that are created with batch deployments/endpoints invocation.

    This class shouldn't be instantiated directly. Instead, it is used as the return type of batch deployment/endpoint
    invocation and job listing.
    """

    def __init__(
        self,
        *,
        id: Optional[str] = None,
        name: Optional[str] = None,
        type: Optional[str] = None,
        status: Optional[str] = None,
        compute: Optional[ComputeConfiguration] = None,
        dataset: Optional[InferenceDataInputBase] = None,
        description: Optional[str] = None,
        error_threshold: Optional[int] = None,
        input_data: Optional[Dict[str, JobInput]] = None,
        logging_level: Optional[Union[str, BatchLoggingLevel]] = None,
        max_concurrency_per_instance: Optional[int] = None,
        mini_batch_size: Optional[int] = None,
        job_name: Optional[str] = None,
        output_data: Optional[Dict[str, JobOutputV2]] = None,
        output_dataset: Optional[DataVersion] = None,
        output_file_name: Optional[str] = None,
        partition_keys: Optional[List[str]] = None,
        properties: Optional[Dict[str, str]] = None,
        retry_settings: Optional[BatchRetrySettings] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs  # pylint:disable=unused-argument
    ):
        self.id = id
        self.name = name
        self.type = type
        self.status = status
        self.compute = compute
        self.dataset = dataset
        self.description = description
        self.error_threshold = error_threshold
        self.input_data = input_data
        self.logging_level = logging_level
        self.max_concurrency_per_instance = max_concurrency_per_instance
        self.mini_batch_size = mini_batch_size
        self.job_name = job_name
        self.output_data = output_data
        self.output_dataset = output_dataset
        self.output_file_name = output_file_name
        self.partition_keys = partition_keys
        self.properties = properties
        self.retry_settings = retry_settings
        self.tags = tags

    @classmethod
    def _from_rest_object(cls, obj: BatchJobResource) -> "BatchJob":
        batch_job_property = obj.properties
        return cls(
            id=obj.id,
            name=obj.name,
            type=obj.type,
            status=batch_job_property.status,
            compute=batch_job_property.compute,
            dataset=batch_job_property.dataset,
            description=batch_job_property.description,
            error_threshold=batch_job_property.error_threshold,
            input_data=batch_job_property.input_data,
            logging_level=batch_job_property.logging_level,
            max_concurrency_per_instance=batch_job_property.max_concurrency_per_instance,
            mini_batch_size=batch_job_property.mini_batch_size,
            job_name=batch_job_property.name,
            output_data=batch_job_property.output_data,
            output_dataset=batch_job_property.output_dataset,
            output_file_name=batch_job_property.output_file_name,
            partition_keys=batch_job_property.partition_keys,
            properties=batch_job_property.properties,
            retry_settings=batch_job_property.retry_settings,
            tags=batch_job_property.tags,
        )

    def _to_rest_object(self) -> "BatchJobResource":
        batch_job_property = RestBatchJob(
            compute=self.compute,
            dataset=self.dataset,
            description=self.description,
            error_threshold=self.error_threshold,
            input_data=self.input_data,
            logging_level=self.logging_level,
            max_concurrency_per_instance=self.max_concurrency_per_instance,
            mini_batch_size=self.mini_batch_size,
            name=self.job_name,
            output_data=self.output_data,
            output_dataset=self.output_dataset,
            output_file_name=self.output_file_name,
            partition_keys=self.partition_keys,
            properties=self.properties,
            retry_settings=self.retry_settings,
            tags=self.tags,
        )
        return BatchJobResource(properties=batch_job_property)

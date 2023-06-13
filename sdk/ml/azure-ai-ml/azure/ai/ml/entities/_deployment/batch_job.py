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
from azure.ai.ml.entities._system_data import SystemData

# pylint: disable=too-many-instance-attributes
class BatchJob(object):
    """Batch jobs that are created with batch deployments/endpoints invocation.

    :param id: The id of the batch job.
    :type id: str
    :param name: The name of the batch job resource.
    :type name: str
    :param type: Type of the batch job.
    :type type: str
    :param status: Status of the job. Possible values include: "NotStarted", "Starting",
     "Provisioning", "Preparing", "Queued", "Running", "Finalizing", "CancelRequested", "Completed",
     "Failed", "Canceled", "NotResponding", "Paused", "Unknown".
    :type status: str
    :param compute: Compute configuration used to set instance count.
    :type compute: ComputeConfiguration
    :param dataset: Input dataset.
    :type dataset: InferenceDataInputBase
    :param description: The asset description text.
    :type description: str
    :param error_threshold: Error threshold, if the error count for the entire input goes above
        this value,
        the batch inference will be aborted. Range is [-1, int.MaxValue]
        -1 value indicates, ignore all failures during batch inference
        For FileDataset count of file failures
        For TabularDataset, this is the count of record failures, defaults to -1
    :type error_thershold: int
    :param input_data: Input data for the job.
    :type input_data: Dict[str, JobInput]
    :param logging_level: Logging level for batch inference operation. Possible values include:
     "Info", "Warning", "Debug".
    :type logging_level: Union[str, BatchLoggingLevel]
    :param max_concurrency_per_instance: Indicates maximum number of parallelism per instance.
    :type max_concurrency_per_instance: int
    :param mini_batch_size: Size of the mini-batch passed to each batch invocation.
    :type mini_batch_size: int
    :param job_name: Name of the batch job.
    :type job_name: str
    :param ouptut_data: Job output data location.
    :type output_data: Dict[str, JobOutputV2]
    :param output_dataset: Output dataset location
    :type output_dataset: DataVersion
    :param output_file_name: Output file name.
    :type output_file_name: str
    :param partition_keys: Partition keys list used for Named partitioning.
    :type partition_keys: List[str]
    :param properties: The asset property dictionary.
    :type properties: dict[str,str]
    :param retry_settings: Retry Settings for the batch inference operation.
    :type retry_settings: BatchRetrySettings
    :param system_data: System data associated with resource provider.
    :type system_data: SystemData
    :param tags: A set of tags. Tag dictionary. Tags can be added, removed, and updated.
    :type tags: Dict[str,str]





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
        system_data: Optional[SystemData] = None,
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
        self.system_data = system_data
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
            system_data=obj.system_data,
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

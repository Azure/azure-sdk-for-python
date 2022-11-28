# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.batch.batch_job import BatchJobSchema
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings
from azure.ai.ml.entities._deployment.compute_binding import ComputeBinding
from azure.ai.ml.entities._deployment.batch_job_property import BatchJobProperty
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._deployment.data_version import DataVersion
from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import BatchJobResource as RestBatchJobResource

# pylint: disable=too-many-instance-attributes
class BatchJob:
    """Batch Job entity

    :param id: Fully qualified resource ID for the resource. Ex -
     /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/
     providers/{resourceProviderNamespace}/{resourceType}/{resourceName}.
    :type id: str
    :param name: The name of the resource.
    :type name: str
    :param type: The type of the resource. E.g. "Microsoft.Compute/virtualMachines" or
     "Microsoft.Storage/storageAccounts".
    :type type: str
    :param system_data: System data associated with resource provider.
    :type system_data: SystemData
    :param copmute: Compute configuration used to set instance count.
    :type id: ComputeBinding
    :param dataset: Input dataset.
    :type dataset: str
    :param error_threshold: Error threshold, if the error count for the entire input goes above
         this value, the batch inference will be aborted. Range is [-1, int.MaxValue] -1 value
         indicates, ignore all failures during batch inference.
    :type error_threshold: int
    :param input_data:Input data for the job.
    :type input_date: Dict[str, JobInput]
    :param mini_batch_size: Size of the mini-batch passed to each batch invocation.
    :type mini_batch_size: int
    :param batch_job_name: name of batch job property
    :type batch_job_name: str
    :param output_file_name: Output file name.
    :type output_file_name: str
    :param retry_settings: Retry Settings for the batch inference operation.
    :type retry_settings: BatchRetrySettings
    :param status: Status of the job.
    :type status: str
    """

    def __init__(
        self,
        id: str = None, # pylint: disable=redefined-builtin
        name: str = None,
        type: str = None, # pylint: disable=redefined-builtin
        system_data: SystemData = None,
        properties: BatchJobProperty = None,
        **kwargs,
    ):  # pylint: disable=unused-argument
        self.id = id
        self.name = name
        self.type = type
        self.system_data = system_data
        self.properties = properties
        self.compute = properties.compute
        self.dataset = properties.dataset
        self.error_threshold = properties.error_threshold
        self.input_data = properties.input_data
        self.mini_batch_size = properties.mini_batch_size
        self.batch_job_name = properties.name
        self.retry_setting = properties.retry_settings
        self.output_file_name = properties.output_file_name
        self.status = properties.status
        self.output_data = properties.output_data
        self.output_dataset = properties.output_dataset

    # pylint: disable=protected-access
    @classmethod
    def _from_rest_object(cls, job: RestBatchJobResource) -> "BatchJob":
        job_property = job.properties
        return cls(
            id=job.id,
            name=job.name,
            type=job.type,
            properties = job_property,
            system_data= SystemData._from_rest_object(job.system_data),
        )

    @classmethod
    def _from_dict(cls, job: Dict) -> "BatchJob":
        return cls(
        id=job.get("id"),
        name=job.get("name"),
        type=job.get("type"),
        properties = BatchJobProperty._from_dict(job.get("properties")),
        system_data= job.get("system_data"),
        )

    def _to_rest_object(self) -> RestBatchJobResource:
        return RestBatchJobResource(
            properties= self.properties._to_rest_object()
        )

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return BatchJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

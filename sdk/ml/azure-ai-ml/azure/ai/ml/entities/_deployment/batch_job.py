# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.batch.batch_job import BatchJobSchema
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings
from azure.ai.ml.entities._deployment.compute_binding import ComputeBinding
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import BatchJobResource as RestBatchJobResource


class BatchJob:
    """Batch Job entity

    :param id: Fully qualified resource ID for the resource. Ex -
     /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/{resourceProviderNamespace}/{resourceType}/{resourceName}.
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
        id: str = None,
        name: str = None,
        type: str = None,
        system_data: SystemData = None,
        compute: ComputeBinding = None,
        dataset: str = None,
        error_threshold: int = None,
        input_data: Dict= None,
        mini_batch_size: int = None,
        batch_job_name: str = None,
        output_file_name: str = None,
        retry_setting: BatchRetrySettings = None,
        status: str = None,
        **kwargs,
    ):  # pylint: disable=unused-argument
        self.id = id
        self.name = name
        self.type = type
        self.system_data = system_data
        self.compute = compute
        self.dataset = dataset
        self.error_threshold = error_threshold
        self.input_data = input_data
        self.mini_batch_size = mini_batch_size
        self.batch_job_name = batch_job_name
        self.retry_setting = retry_setting
        self.output_file_name = output_file_name
        self.status = status


    @classmethod
    def _from_rest_object(cls, job: RestBatchJobResource) -> "BatchJob":
        job_property = job.properties
        return cls(
            id=job.id,
            name=job.name,
            type=job.type,
            dataset = job_property.dataset,
            error_threshold = job_property.error_threshold,
            input_data = job_property.input_data,
            mini_batch_size = job_property.mini_batch_size,
            batch_job_name = job_property.name,
            retry_setting = job_property.retry_settings,
            system_data= SystemData._from_rest_object(job.system_data),
            status = job_property.status
        )

    
    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return BatchJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.batch.batch_job_property import BatchJobPropertySchema
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings
from azure.ai.ml.entities._deployment.compute_binding import ComputeBinding
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import BatchJob as BatchJobData


class BatchJobProperty:
    """Batch Job Property entity

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
    :param name: name of batch job property
    :type name: str
    :param output_file_name: Output file name.
    :type output_file_name: str
    :param retry_settings: Retry Settings for the batch inference operation.
    :type retry_settings: BatchRetrySettings
    :param status: Status of the job. 
    :type status: str

    """

    def __init__(
        self,
        compute: ComputeBinding = None,
        dataset: str = None,
        error_threshold: int = None,
        input_data: Dict= None,
        mini_batch_size: int = None,
        name: str = None,
        output_file_name: str = None,
        retry_setting: BatchRetrySettings = None,
        status: str = None,
        **kwargs,
    ):  # pylint: disable=unused-argument
        self.compute = compute
        self.dataset = dataset
        self.error_threshold = error_threshold
        self.input_data = input_data
        self.mini_batch_size = mini_batch_size
        self.name = name
        self.output_file_name = output_file_name
        self.retry_setting = retry_setting
        self.status = status

    @classmethod
    def _from_rest_object(cls, obj: BatchJobData) -> "BatchJobProperty":
        return cls(
            compute=obj.compute,
            dataset=obj.dataset,
            error_threshold=obj.error_threshold,
            input_data=obj.input_data,
            minin_batch_szie=obj.mini_batch_size,
            name=obj.name,
            output_file_name = obj.output_file_name,
            retry_setting = obj.retry_settings,
            status = obj.status
        )

    
    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return BatchJobPropertySchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

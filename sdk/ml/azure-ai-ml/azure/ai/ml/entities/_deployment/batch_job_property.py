# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.batch.batch_job_property import BatchJobPropertySchema
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings
from azure.ai.ml.entities._deployment.compute_binding import ComputeBinding
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities import SystemData
from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import BatchJob as BatchJobData


class BatchJobProperty:
    """Batch Job Property entity

    :param id: Fully qualified resource ID for the resource. Ex -
     /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/{resourceProviderNamespace}/{resourceType}/{resourceName}.
    :type id: str
    :param name: The name of the resource.
    :type name: str
    :param type: The type of the resource. E.g. "Microsoft.Compute/virtualMachines" or
     "Microsoft.Storage/storageAccounts".
    :type type: str
    :param properties: Required. [Required] Additional attributes of the entity.
    :type properties: ~azure.mgmt.machinelearningservices.models.BatchJob
    :param system_data: System data associated with resource provider.
    :type system_data: SystemData
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
            retry_setting = obj.retry_settings
        )

    
    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return BatchJobPropertySchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

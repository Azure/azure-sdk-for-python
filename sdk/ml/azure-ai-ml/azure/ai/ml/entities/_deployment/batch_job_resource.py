# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.batch.batch_job_resource import BatchJobResourceSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities import SystemData
from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import BatchJob, BatchJobResource as RestBatchJobResource


class BatchJobResource:
    """Batch Job Resource entity

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
        id: str = None,
        name: str = None,
        type: str = None,
        properties: BatchJob = None,
        system_data: SystemData = None,
        **kwargs,
    ):  # pylint: disable=unused-argument
        self.id = id
        self.name = name
        self.type = type
        self.properties = properties
        self.system_data = system_data

    @classmethod
    def _from_rest_object(cls, job: RestBatchJobResource):
        return BatchJobResource(
            id=job.id,
            name=job.name,
            type=job.type,
            properties=job.properties,
            system_data=job.system_data
        )

    
    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return BatchJobResourceSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

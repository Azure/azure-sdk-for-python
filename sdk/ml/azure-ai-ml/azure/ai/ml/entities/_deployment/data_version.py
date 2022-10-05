# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Union
# from azure.ai.ml._schema._deployment.batch.batch_job_property import OutputDataSchema
from azure.ai.ml._schema.core.fields import ArmStr
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class DataVersion:
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
        datastore_id: ArmStr = None,
        path: str = None,
        **kwargs,
    ):  # pylint: disable=unused-argument
        self.datastore_id = datastore_id
        self.path = path
    # def _to_dict(self) -> Dict:
    #     # pylint: disable=no-member
    #     return OutputDataSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
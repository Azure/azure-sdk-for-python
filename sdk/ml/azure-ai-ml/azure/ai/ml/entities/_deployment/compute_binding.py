# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Union

from azure.ai.ml._schema._deployment.batch.compute_binding import ComputeBindingSchema
from azure.ai.ml._schema.core.fields import ArmStr
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class ComputeBinding:
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
        target: Union[str, ArmStr] = None,
        instance_count: int = None,
        instance_type: str = None,
        location: str = None,
        properties: Dict = None,
        **kwargs,
    ):  # pylint: disable=unused-argument
        self.target = target
        self.instance_count = instance_count
        self.instance_type = instance_type
        self.location = location
        self.properties = properties
    
    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return ComputeBindingSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Dict, Optional

from azure.ai.ml._restclient.arm_ml_service.models import (
    ComputeResource,
    FabricSpark,
    FabricSparkProperties,
    ProvisioningState,
)
from azure.ai.ml._schema.compute.fabricspark_compute import FabricSparkComputeSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.constants._compute import ComputeType
from azure.ai.ml.entities._compute.compute import Compute
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


class FabricSparkCompute(Compute):
    """An existing Fabric custom Spark pool attached to an Azure Machine Learning workspace.

    :keyword name: Name of the AML compute attachment.
    :paramtype name: str
    :keyword fabric_workspace_id: ID of the Fabric workspace containing the resources. Required for attach.
    :paramtype fabric_workspace_id: Optional[str]
    :keyword lakehouse_id: ID of a Lakehouse in the Fabric workspace. Required for attach.
    :paramtype lakehouse_id: Optional[str]
    :keyword environment_id: ID of a published Fabric Environment selecting the custom pool. Required for attach.
    :paramtype environment_id: Optional[str]
    :keyword pool_id: ID of the custom Spark pool selected by the Environment. Required for attach.
    :paramtype pool_id: Optional[str]
    :keyword identity: Optional identity belonging to the AML compute attachment.
    :paramtype identity: Optional[~azure.ai.ml.entities.IdentityConfiguration]
    :keyword pool_name: Name of the pool returned by the service.
    :paramtype pool_name: Optional[str]
    :keyword description: Description of the compute attachment.
    :paramtype description: Optional[str]
    :keyword tags: Tags assigned to the compute attachment.
    :paramtype tags: Optional[Dict[str, str]]
    """

    def __init__(
        self,
        *,
        name: str,
        fabric_workspace_id: Optional[str] = None,
        lakehouse_id: Optional[str] = None,
        environment_id: Optional[str] = None,
        pool_id: Optional[str] = None,
        identity: Optional[IdentityConfiguration] = None,
        pool_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        kwargs[TYPE] = ComputeType.FABRICSPARK
        is_attached_compute = kwargs.pop("is_attached_compute", None)
        modified_on = kwargs.pop("modified_on", None)
        disable_local_auth = kwargs.pop("disable_local_auth", None)
        super().__init__(name=name, description=description, location=kwargs.pop("location", None), tags=tags, **kwargs)
        self.fabric_workspace_id = fabric_workspace_id
        self.lakehouse_id = lakehouse_id
        self.environment_id = environment_id
        self.pool_id = pool_id
        self.pool_name = pool_name
        self.identity = identity
        self.is_attached_compute: Optional[bool] = is_attached_compute
        self.modified_on = modified_on
        self.disable_local_auth = disable_local_auth

    @classmethod
    def _load_from_rest(cls, rest_obj: ComputeResource) -> "FabricSparkCompute":
        prop = rest_obj.properties
        details = prop.properties
        return cls(
            name=rest_obj.name,
            id=rest_obj.id,
            location=rest_obj.location,
            description=prop.description,
            resource_id=prop.resource_id,
            tags=rest_obj.tags,
            fabric_workspace_id=details.fabric_workspace_id if details else None,
            lakehouse_id=details.lakehouse_id if details else None,
            environment_id=details.environment_id if details else None,
            pool_id=details.pool_id if details else None,
            pool_name=details.pool_name if details else None,
            identity=IdentityConfiguration._from_compute_rest_object(rest_obj.identity) if rest_obj.identity else None,
            created_on=prop.created_on,
            modified_on=prop.modified_on,
            disable_local_auth=prop.disable_local_auth,
            provisioning_state=(
                prop.provisioning_state.value
                if isinstance(prop.provisioning_state, ProvisioningState)
                else prop.provisioning_state
            ),
            provisioning_errors=(
                prop.provisioning_errors[0].error.code
                if prop.provisioning_errors and prop.provisioning_errors[0].error
                else None
            ),
            is_attached_compute=prop.is_attached_compute,
        )

    def _to_rest_object(self) -> ComputeResource:
        if not all((self.fabric_workspace_id, self.lakehouse_id, self.environment_id, self.pool_id)):
            message = (
                "Fabric Spark compute attach requires fabric_workspace_id, lakehouse_id, environment_id, and pool_id."
            )
            raise ValidationException(
                message=message,
                target=ErrorTarget.COMPUTE,
                no_personal_data_message=message,
                error_category=ErrorCategory.USER_ERROR,
            )
        return ComputeResource(
            name=self.name,
            location=self.location,
            tags=self.tags,
            identity=self.identity._to_compute_rest_object() if self.identity else None,
            properties=FabricSpark(
                description=self.description,
                resource_id=self.resource_id,
                properties=FabricSparkProperties(
                    fabric_workspace_id=self.fabric_workspace_id,
                    lakehouse_id=self.lakehouse_id,
                    environment_id=self.environment_id,
                    pool_id=self.pool_id,
                ),
            ),
        )

    def _to_dict(self) -> Dict:
        return FabricSparkComputeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs: Any) -> "FabricSparkCompute":
        return cls(**load_from_dict(FabricSparkComputeSchema, data, context, **kwargs))

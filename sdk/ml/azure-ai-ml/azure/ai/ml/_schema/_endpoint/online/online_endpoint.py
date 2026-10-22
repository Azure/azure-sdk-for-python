# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging
from typing import Any

from marshmallow import ValidationError, fields, post_load, validates

from azure.ai.ml._schema._endpoint.endpoint import EndpointSchema
from azure.ai.ml._schema.core.fields import ArmStr, StringTransformedEnum
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AzureMLResourceType, PublicNetworkAccess

module_logger = logging.getLogger(__name__)


class OnlineEndpointSchema(EndpointSchema):
    traffic = fields.Dict(
        keys=fields.Str(),
        values=fields.Int(),
        metadata={
            "description": """a dict with key as deployment name and value as traffic percentage.
             The values need to sum to 100 """
        },
    )
    kind = fields.Str(dump_only=True)

    mirror_traffic = fields.Dict(
        keys=fields.Str(),
        values=fields.Int(),
        metadata={
            "description": """a dict with key as deployment name and value as traffic percentage.
                 Only one key will be accepted and value needs to be less than or equal to 50%"""
        },
    )

    @validates("traffic")
    def validate_traffic(self, data, **kwargs):
        if sum(data.values()) > 100:
            raise ValidationError("Traffic rule percentages must sum to less than or equal to 100%")


class KubernetesOnlineEndpointSchema(OnlineEndpointSchema):
    provisioning_state = fields.Str(metadata={"description": "status of the deployment provisioning operation"})
    compute = ArmStr(azureml_type=AzureMLResourceType.COMPUTE)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities import KubernetesOnlineEndpoint

        return KubernetesOnlineEndpoint(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)


class ManagedOnlineEndpointSchema(OnlineEndpointSchema):
    provisioning_state = fields.Str()
    public_network_access = StringTransformedEnum(
        allowed_values=[PublicNetworkAccess.ENABLED, PublicNetworkAccess.DISABLED]
    )

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities import ManagedOnlineEndpoint

        return ManagedOnlineEndpoint(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields
from marshmallow.decorators import post_load

from azure.ai.ml._schema._utils.utils import validate_arm_str
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml.entities._workspace.serverless_compute import ServerlessComputeSettings


class ServerlessComputeSettingsSchema(PathAwareSchema):
    """Schema for ServerlessComputeSettings.

    :param custom_subnet: The custom subnet to use for serverless computes created in the workspace.
    :type custom_subnet: str. Formatted as ARM ID.
    :param no_public_ip: Whether to disable public ip for the compute. Only valid if custom_subnet is defined.
    :type no_public_ip: bool
    """

    custom_subnet = fields.Str(validate=validate_arm_str)
    no_public_ip = fields.Bool(load_default=False)

    @post_load
    def make(self, data, **_kwargs) -> ServerlessComputeSettings:
        """Create a ServerlessComputeSettings object from the marshmallow schema.

        :param data: The data from which the ServerlessComputeSettings are being loaded.
        :type data: OrderedDict[str, Any]
        :returns: A ServerlessComputeSettings object.
        :rtype: azure.ai.ml.entities._workspace.serverless_compute.ServerlessComputeSettings
        """
        custom_subnet = data.pop("custom_subnet", None)
        no_public_ip = data.pop("no_public_ip", False)
        return ServerlessComputeSettings(custom_subnet, no_public_ip)

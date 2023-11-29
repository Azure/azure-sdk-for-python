# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields
from marshmallow.decorators import post_load, validates

from azure.ai.ml._schema._utils.utils import ArmId
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml.entities._workspace.serverless_compute import ServerlessComputeSettings


class ServerlessComputeSettingsSchema(PathAwareSchema):
    """Schema for ServerlessComputeSettings.

    :param custom_subnet: The custom subnet to use for serverless computes created in the workspace.
    :type custom_subnet: Optional[ArmId]
    :param no_public_ip: Whether to disable public ip for the compute. Only valid if custom_subnet is defined.
    :type no_public_ip: bool
    """

    custom_subnet = fields.Str(allow_none=True)
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
        if custom_subnet == "None":
            custom_subnet = None  # For loading from YAML when the user wants to trigger a removal
        no_public_ip = data.pop("no_public_ip", False)
        return ServerlessComputeSettings(custom_subnet=custom_subnet, no_public_ip=no_public_ip)

    @validates("custom_subnet")
    def validate_custom_subnet(self, data: str, **_kwargs):
        """Validates the custom_subnet field matches the ARM ID format or is a None-recognizable value.

        :param data: The candidate custom_subnet to validate.
        :type data: str
        :raises ValidationError: If the custom_subnet is not formatted as an ARM ID.
        """
        if data == "None" or data is None:
            # If the string is literally "None", then it should be deserialized to None
            pass
        else:
            # Verify that we can transform it to an ArmId if it is not None.
            ArmId(data)

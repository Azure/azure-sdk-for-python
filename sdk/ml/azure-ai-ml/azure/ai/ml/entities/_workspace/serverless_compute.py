# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow.exceptions import ValidationError

from azure.ai.ml._restclient.v2023_08_01_preview.models import (
    ServerlessComputeSettings as RestServerlessComputeSettings,
)
from azure.ai.ml._schema._utils.utils import validate_arm_str


class ServerlessComputeSettings:
    """Settings regarding serverless compute(s) in an Azure ML workspace.

    :param custom_subnet: The name of the subnet to use for serverless compute(s).
    :type custom_subnet: str
    :param no_public_ip: Whether or not to disable public IP addresses for serverless compute(s).
    :type no_public_ip: bool
    """

    custom_subnet: str
    no_public_ip: bool = False

    """
    :param custom_subnet: The ARM ID of the subnet to use for serverless compute(s).
    :type custom_subnet: str. Formatted as an ARM ID.
    :param no_public_ip: Whether or not to disable public IP addresses for serverless compute(s).
    :type no_public_ip: bool
    :raises ValidationError: If the custom_subnet is not formatted as an ARM ID.
    :raises ValidationError: If custom_subnet is None or empty, but no_public_ip is set to True.
    """

    def __init__(self, custom_subnet: str, no_public_ip: bool = False) -> None:
        if custom_subnet:
            # This will raise marshmallow.ValidatonError if the string is incorrectly formatted
            validate_arm_str(custom_subnet)
        elif len(str(custom_subnet or "")) == 0 and no_public_ip:
            raise ValidationError("custom_subnet must be set if no_public_ip is set to True")
        self.custom_subnet = custom_subnet
        self.no_public_ip = no_public_ip

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ServerlessComputeSettings):
            return NotImplemented
        return self.custom_subnet == other.custom_subnet and self.no_public_ip == other.no_public_ip

    def _to_rest_object(self) -> RestServerlessComputeSettings:
        return RestServerlessComputeSettings(
            serverless_compute_custom_subnet=self.custom_subnet,
            serverless_compute_no_public_ip=self.no_public_ip,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestServerlessComputeSettings) -> "ServerlessComputeSettings":
        return ServerlessComputeSettings(
            custom_subnet=obj.serverless_compute_custom_subnet,
            no_public_ip=obj.serverless_compute_no_public_ip,
        )

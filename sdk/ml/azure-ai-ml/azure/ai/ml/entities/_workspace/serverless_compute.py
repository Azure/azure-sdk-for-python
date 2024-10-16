# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, Union

from marshmallow.exceptions import ValidationError

from azure.ai.ml._restclient.v2024_07_01_preview.models import (
    ServerlessComputeSettings as RestServerlessComputeSettings,
)
from azure.ai.ml._schema._utils.utils import ArmId


class ServerlessComputeSettings:
    custom_subnet: Optional[ArmId]
    no_public_ip: bool = False

    def __init__(self, *, custom_subnet: Optional[Union[str, ArmId]] = None, no_public_ip: bool = False) -> None:
        """Settings regarding serverless compute(s) in an Azure ML workspace.

        :keyword custom_subnet: The ARM ID of the subnet to use for serverless compute(s).
        :paramtype custom_subnet: Optional[Union[str, ArmId]]
        :keyword no_public_ip: Whether or not to disable public IP addresses for serverless compute(s).
            Defaults to False.
        :paramtype no_public_ip: bool
        :raises ValidationError: If the custom_subnet is not formatted as an ARM ID.
        """
        if isinstance(custom_subnet, str):
            self.custom_subnet = ArmId(custom_subnet)
        elif isinstance(custom_subnet, ArmId) or custom_subnet is None:
            self.custom_subnet = custom_subnet
        else:
            raise ValidationError("custom_subnet must be a string, ArmId, or None.")
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
        return cls(
            custom_subnet=obj.serverless_compute_custom_subnet,
            no_public_ip=obj.serverless_compute_no_public_ip,
        )

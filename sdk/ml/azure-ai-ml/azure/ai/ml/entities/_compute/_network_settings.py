# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Optional
from marshmallow.exceptions import ValidationError

from azure.ai.ml._schema._utils.utils import validate_arm_str


class NetworkSettings:
    def __init__(
        self,
        *,
        subnet: str,
        vnet_name: Optional[str] = None,
        **kwargs,
    ):
        """Network settings for a compute.

        :param subnet: The subnet name. Can also be provided as an ARM string specifying the location of the subnet.
        :type subnet: str
        :param vnet_name: The virtual network name. Ignored if subnet is provided as an ARM string. Defaults to None.
        :type vnet_name: str, optional

        """
        self.subnet = subnet
        self.vnet_name = vnet_name
        self._public_ip_address = kwargs.pop("public_ip_address", None)
        self._private_ip_address = kwargs.pop("private_ip_address", None)

    @property
    def public_ip_address(self) -> str:
        """Public IP address of the compute instance.

        return: Public IP address.
        rtype: str
        """
        return self._public_ip_address

    @property
    def private_ip_address(self) -> str:
        """Private IP address of the compute instance.

        return: Private IP address.
        rtype: str
        """
        return self._private_ip_address

    def get_subnet_str(self, sub_id: Optional[str] = None, rg: Optional[str] = None) -> str:
        if self.subnet is None:
            return None
        try:
            if validate_arm_str(self.subnet):
                return self.subnet
        except ValidationError:
            return (
                f"/subscriptions/{sub_id}/resourceGroups/{rg}/"
                f"providers/Microsoft.Network/virtualNetworks/{self.vnet_name}/subnets/{self.subnet}"
            )

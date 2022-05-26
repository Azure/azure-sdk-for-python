# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import re

from marshmallow.exceptions import ValidationError
from typing import Any
from collections import OrderedDict

module_logger = logging.getLogger(__name__)


def validate_arm_str(arm_str: str) -> bool:
    reg_str = (
        r"/subscriptions/[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}?/resourcegroups/.*/providers/[a-z.a-z]*/[a-z]*/.*"
    )
    lowered = arm_str.lower()
    match = re.match(reg_str, lowered)
    if match and match.group() == lowered:
        return True
    else:
        raise ValidationError(f"ARM string {arm_str} is not formatted correctly.")


def get_subnet_str(vnet_name: str, subnet: str, sub_id: str = None, rg: str = None) -> str:
    if vnet_name and not subnet:
        raise ValidationError("Subnet is required when vnet name is specified.")
    try:
        if validate_arm_str(subnet):
            return subnet
    except ValidationError:
        return f"/subscriptions/{sub_id}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks/{vnet_name}/subnets/{subnet}"


def replace_key_in_odict(odict: OrderedDict, old_key: Any, new_key: Any):
    if not odict or old_key not in odict:
        return odict
    return OrderedDict([(new_key, v) if k == old_key else (k, v) for k, v in odict.items()])

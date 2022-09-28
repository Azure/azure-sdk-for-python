# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Simple helper methods to avoid re-using lambda's everywhere

from typing import OrderedDict
from azure.ai.ml.constants._registry import ACR_ACCOUNT_FORMAT, STORAGE_ACCOUNT_FORMAT


def storage_account_validator(storage_id: str):
    return STORAGE_ACCOUNT_FORMAT.match(storage_id) is not None


def acr_format_validator(acr_id: str):
    return ACR_ACCOUNT_FORMAT.match(acr_id) is not None


#Display resource id as string, rather than as object with sub-fields.
def convert_arm_resource_id(data: OrderedDict):
    if "arm_resource_id" in data and "resource_id" in data["arm_resource_id"]:
        data["arm_resource_id"] = data["arm_resource_id"]["resource_id"]
    return data
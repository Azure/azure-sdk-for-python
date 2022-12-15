# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Simple helper methods to avoid re-using lambda's everywhere

from azure.ai.ml.constants._registry import ACR_ACCOUNT_FORMAT, STORAGE_ACCOUNT_FORMAT


def storage_account_validator(storage_id: str):
    return STORAGE_ACCOUNT_FORMAT.match(storage_id) is not None


def acr_format_validator(acr_id: str):
    return ACR_ACCOUNT_FORMAT.match(acr_id) is not None

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint:disable=protected-access,no-else-return

from typing import List, Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    AcrDetails as RestAcrDetails,
    ArmResourceId as RestArmResourceId,
    RegistryRegionArmDetails as RestRegistryRegionArmDetails,
    StorageAccountDetails as RestStorageAccountDetails,
    SystemCreatedAcrAccount as RestSystemCreatedAcrAccount,
    SystemCreatedStorageAccount as RestSystemCreatedStorageAccount,
    UserCreatedAcrAccount as RestUserCreatedAcrAccount,
    UserCreatedStorageAccount as RestUserCreatedStorageAccount)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._registry import StorageAccountType


def make_rest_user_storage_from_id(id: str) -> RestStorageAccountDetails:
    return RestStorageAccountDetails(
        user_created_storage_account=RestUserCreatedStorageAccount(
            arm_resource_id=RestArmResourceId(resource_id=id)
        )


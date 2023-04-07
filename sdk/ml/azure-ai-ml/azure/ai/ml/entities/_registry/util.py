# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint:disable=protected-access,no-else-return

from azure.ai.ml._restclient.v2022_10_01_preview.models import ArmResourceId as RestArmResourceId
from azure.ai.ml._restclient.v2022_10_01_preview.models import StorageAccountDetails as RestStorageAccountDetails
from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    UserCreatedStorageAccount as RestUserCreatedStorageAccount,
)


def _make_rest_user_storage_from_id(*, user_id: str) -> RestStorageAccountDetails:
    return RestStorageAccountDetails(
        user_created_storage_account=RestUserCreatedStorageAccount(
            arm_resource_id=RestArmResourceId(resource_id=user_id)
        )
    )

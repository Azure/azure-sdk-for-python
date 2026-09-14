# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.arm_ml_service.models import StorageAccountDetails as RestStorageAccountDetails


def _make_rest_user_storage_from_id(*, user_id: str) -> RestStorageAccountDetails:
    # ``UserCreatedStorageAccount`` was @removed from the shared arm_ml_service model
    # (api-version 2025-12-01); set the wire field directly to preserve the old body:
    # {"userCreatedStorageAccount": {"armResourceId": {"resourceId": <user_id>}}}.
    rest_storage = RestStorageAccountDetails()
    rest_storage["userCreatedStorageAccount"] = {"armResourceId": {"resourceId": user_id}}
    return rest_storage

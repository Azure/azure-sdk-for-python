# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint:disable=protected-access,no-else-return

from copy import deepcopy
from functools import reduce
from typing import List, Optional, Union

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2022_10_01_preview.models import AcrDetails as RestAcrDetails
from azure.ai.ml._restclient.v2022_10_01_preview.models import ArmResourceId as RestArmResourceId
from azure.ai.ml._restclient.v2022_10_01_preview.models import RegistryRegionArmDetails as RestRegistryRegionArmDetails
from azure.ai.ml._restclient.v2022_10_01_preview.models import StorageAccountDetails as RestStorageAccountDetails
from azure.ai.ml._restclient.v2022_10_01_preview.models import SystemCreatedAcrAccount as RestSystemCreatedAcrAccount
from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    SystemCreatedStorageAccount as RestSystemCreatedStorageAccount,
)
from azure.ai.ml._restclient.v2022_10_01_preview.models import UserCreatedAcrAccount as RestUserCreatedAcrAccount
from azure.ai.ml.constants._registry import StorageAccountType
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from .util import _make_rest_user_storage_from_id


# This exists despite not being used by the schema validator because this entire
# class is an output only value from the API.
class SystemCreatedAcrAccount:
    def __init__(
        self,
        *,
        acr_account_sku: str,
        arm_resource_id: Optional[str] = None,
    ):
        """Azure ML ACR account.

        :param acr_account_sku: The storage account service tier. Currently
            only Premium is a valid option for registries.
        :type acr_account_sku: str
        :param arm_resource_id: Resource ID of the ACR account.
        :type arm_resource_id: str. Default value is None.
        """
        self.acr_account_sku = acr_account_sku
        self.arm_resource_id = arm_resource_id

    # acr should technically be a union between str and SystemCreatedAcrAccount,
    # but python doesn't accept self class references apparently.
    # Class method instead of normal function to accept possible
    # string input.
    @classmethod
    def _to_rest_object(cls, acr: Union[str, "SystemCreatedAcrAccount"]) -> RestAcrDetails:
        if hasattr(acr, "acr_account_sku") and acr.acr_account_sku is not None:
            # SKU enum requires input to be a capitalized word,
            # so we format the input to be acceptable as long as spelling is
            # correct.
            acr_account_sku = acr.acr_account_sku.capitalize()
            # We DO NOT want to set the arm_resource_id. The backend provides very
            # unhelpful errors if you provide an empty/null/invalid resource ID,
            # and ignores the value otherwise. It's better to avoid setting it in
            # the conversion in this direction at all.
            return RestAcrDetails(
                system_created_acr_account=RestSystemCreatedAcrAccount(
                    acr_account_sku=acr_account_sku,
                )
            )
        else:
            return RestAcrDetails(
                user_created_acr_account=RestUserCreatedAcrAccount(arm_resource_id=RestArmResourceId(resource_id=acr))
            )

    @classmethod
    def _from_rest_object(cls, rest_obj: RestAcrDetails) -> Optional["Union[str, SystemCreatedAcrAccount]"]:
        if not rest_obj:
            return None
        if hasattr(rest_obj, "system_created_acr_account") and rest_obj.system_created_acr_account is not None:
            resource_id = None
            if rest_obj.system_created_acr_account.arm_resource_id:
                resource_id = rest_obj.system_created_acr_account.arm_resource_id.resource_id
            return SystemCreatedAcrAccount(
                acr_account_sku=rest_obj.system_created_acr_account.acr_account_sku,
                arm_resource_id=resource_id,
            )
        elif hasattr(rest_obj, "user_created_acr_account") and rest_obj.user_created_acr_account is not None:
            res: Optional[str] = rest_obj.user_created_acr_account.arm_resource_id.resource_id
            return res
        else:
            return None


class SystemCreatedStorageAccount:
    def __init__(
        self,
        *,
        storage_account_hns: bool,
        storage_account_type: Optional[StorageAccountType],
        arm_resource_id: Optional[str] = None,
        replicated_ids: Optional[List[str]] = None,
        replication_count: int = 1,
    ):
        """
        :param arm_resource_id: Resource ID of the storage account.
        :type arm_resource_id: str
        :param storage_account_hns: Whether or not this storage account
            has hierarchical namespaces enabled.
        :type storage_account_hns: bool
        :param storage_account_type: Allowed values: "Standard_LRS",
            "Standard_GRS, "Standard_RAGRS", "Standard_ZRS", "Standard_GZRS",
            "Standard_RAGZRS", "Premium_LRS", "Premium_ZRS"
        :type storage_account_type: StorageAccountType
        :param replication_count: The number of replicas of this storage account
            that should be created. Defaults to 1. Values less than 1 are invalid.
        :type replication_count: int
        :param replicated_ids: If this storage was replicated, then this is a
            list of all storage IDs with these settings for this registry.
            Defaults to none for un-replicated storage accounts.
        :type replicated_ids: List[str]
        """
        self.arm_resource_id = arm_resource_id
        self.storage_account_hns = storage_account_hns
        self.storage_account_type = storage_account_type
        self.replication_count = replication_count
        self.replicated_ids = replicated_ids


# Per-region information for registries.
class RegistryRegionDetails:
    def __init__(
        self,
        *,
        acr_config: Optional[List[Union[str, SystemCreatedAcrAccount]]] = None,
        location: Optional[str] = None,
        storage_config: Optional[Union[List[str], SystemCreatedStorageAccount]] = None,
    ):
        """Details for each region a registry is in.

        :param acr_details: List of ACR account details. Each value can either be a
            single string representing the arm_resource_id of a user-created
            acr_details object, or a entire SystemCreatedAcrAccount object.
        :type acr_details: List[Union[str, SystemCreatedAcrAccount]]
        :param location: The location where the registry exists.
        :type location: str
        :param storage_account_details: List of storage accounts. Each value
            can either be a single string representing the arm_resource_id of
            a user-created storage account, or an entire
            SystemCreatedStorageAccount object.
        :type storage_account_details: Union[List[str], SystemCreatedStorageAccount]
        """
        self.acr_config = acr_config
        self.location = location
        self.storage_config = storage_config

    @classmethod
    def _from_rest_object(cls, rest_obj: RestRegistryRegionArmDetails) -> Optional["RegistryRegionDetails"]:
        if not rest_obj:
            return None
        converted_acr_details = []
        if rest_obj.acr_details:
            converted_acr_details = [SystemCreatedAcrAccount._from_rest_object(acr) for acr in rest_obj.acr_details]
        storages: Optional[Union[List[str], SystemCreatedStorageAccount]] = []
        if rest_obj.storage_account_details:
            storages = cls._storage_config_from_rest_object(rest_obj.storage_account_details)

        return RegistryRegionDetails(
            acr_config=converted_acr_details,  # type: ignore[arg-type]
            location=rest_obj.location,
            storage_config=storages,
        )

    def _to_rest_object(self) -> RestRegistryRegionArmDetails:
        converted_acr_details = []
        if self.acr_config:
            converted_acr_details = [SystemCreatedAcrAccount._to_rest_object(acr) for acr in self.acr_config]
        storages = []
        if self.storage_config:
            storages = self._storage_config_to_rest_object()
        return RestRegistryRegionArmDetails(
            acr_details=converted_acr_details,
            location=self.location,
            storage_account_details=storages,
        )

    def _storage_config_to_rest_object(self) -> List[RestStorageAccountDetails]:
        storage = self.storage_config
        # storage_config can either be a single system-created storage account,
        # or list of user-inputted id's.
        if (
            storage is not None
            and not isinstance(storage, list)
            and hasattr(storage, "storage_account_type")
            and storage.storage_account_type is not None
        ):
            # We DO NOT want to set the arm_resource_id. The backend provides very
            # unhelpful errors if you provide an empty/null/invalid resource ID,
            # and ignores the value otherwise. It's better to avoid setting it in
            # the conversion in this direction at all.
            # We don't bother processing storage_account_type because the
            # rest version is case insensitive.
            account = RestStorageAccountDetails(
                system_created_storage_account=RestSystemCreatedStorageAccount(
                    storage_account_hns_enabled=storage.storage_account_hns,
                    storage_account_type=storage.storage_account_type,
                )
            )
            # duplicate this value based on the replication_count
            count = storage.replication_count
            if count < 1:
                raise ValueError(f"Replication count cannot be less than 1. Value was: {count}.")
            return [deepcopy(account) for _ in range(0, count)]
        elif storage is not None and not isinstance(storage, SystemCreatedStorageAccount) and len(storage) > 0:
            return [_make_rest_user_storage_from_id(user_id=user_id) for user_id in storage]
        else:
            return []

    @classmethod
    def _storage_config_from_rest_object(
        cls, rest_configs: Optional[List]
    ) -> Optional[Union[List[str], SystemCreatedStorageAccount]]:
        if not rest_configs:
            return None
        num_configs = len(rest_configs)
        if num_configs == 0:
            return None
        system_created_count = reduce(
            # TODO: Bug Item number: 2883323
            lambda x, y: int(x) + int(y),  # type: ignore
            [
                hasattr(config, "system_created_storage_account") and config.system_created_storage_account is not None
                for config in rest_configs
            ],
        )
        # configs should be mono-typed. Either they're all system created
        # or all user created.
        if system_created_count == num_configs:
            # System created case - assume all elements are duplicates
            # of a single storage configuration.
            # Convert back into a single local representation by
            # combining id's into a list, and using the first element's
            # account type and hns.
            first_config = rest_configs[0].system_created_storage_account
            resource_id = None
            if first_config.arm_resource_id:
                resource_id = first_config.arm_resource_id.resource_id
            # account for ids of duplicated if they exist
            replicated_ids = None
            if num_configs > 1:
                replicated_ids = [
                    config.system_created_storage_account.arm_resource_id.resource_id for config in rest_configs
                ]
            return SystemCreatedStorageAccount(
                storage_account_hns=first_config.storage_account_hns_enabled,
                storage_account_type=(
                    (StorageAccountType(first_config.storage_account_type.lower()))
                    if first_config.storage_account_type
                    else None
                ),
                arm_resource_id=resource_id,
                replication_count=num_configs,
                replicated_ids=replicated_ids,
            )
        elif system_created_count == 0:
            return [config.user_created_storage_account.arm_resource_id.resource_id for config in rest_configs]
        else:
            msg = f"""tried reading in a registry whose storage accounts were not
                mono-managed or user-created. {system_created_count} out of {num_configs} were managed."""
            err = ValidationException(
                message=msg,
                target=ErrorTarget.REGISTRY,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
            log_and_raise_error(err)
            return None

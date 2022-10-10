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


# This exists despite not being used by the schema validator because this entire
# class is an output only value from the API.
@experimental
class SystemCreatedAcrAccount:
    def __init__(
        self,
        *,
        acr_account_sku: str,
        arm_resource_id: str = None,
    ):
        """
        Azure ML ACR account.

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
    def _to_rest_object(cls, acr) -> RestAcrDetails:
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
                user_created_acr_account=RestUserCreatedAcrAccount(
                    arm_resource_id=RestArmResourceId(resource_id=acr))
            )

    @classmethod
    def _from_rest_object(cls, rest_obj: RestAcrDetails) -> "Union[str, SystemCreatedAcrAccount]":
        if not rest_obj:
            return None
        # TODO should we even bother check if both values are set and throw an error? This shouldn't be possible.
        if hasattr(rest_obj, "system_created_acr_account") and rest_obj.system_created_acr_account is not None:
            resource_id = None
            if rest_obj.system_created_acr_account.arm_resource_id:
                resource_id = rest_obj.system_created_acr_account.arm_resource_id.resource_id
            return SystemCreatedAcrAccount(
                acr_account_sku=rest_obj.system_created_acr_account.acr_account_sku,
                arm_resource_id=resource_id,
            )
        elif hasattr(rest_obj, "user_created_acr_account") and rest_obj.user_created_acr_account is not None:
            return rest_obj.user_created_acr_account.arm_resource_id.resource_id
        else:
            return None  # TODO should this throw an error instead?


@experimental
class SystemCreatedStorageAccount:
    def __init__(
        self,
        *,
        storage_account_hns: bool,
        storage_account_type: StorageAccountType,
        arm_resource_id: str = None,
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
        """
        self.arm_resource_id = arm_resource_id
        self.storage_account_hns = storage_account_hns
        self.storage_account_type = storage_account_type

    # storage should technically be a union between str and SystemCreatedStorageAccount,
    # but python doesn't accept self class references apparently.
    # Class method instead of normal function to accept possible
    # string input.

    @classmethod
    def _to_rest_object(cls, storage) -> RestStorageAccountDetails:
        if hasattr(storage, "storage_account_type") and storage.storage_account_type is not None:

            # We DO NOT want to set the arm_resource_id. The backend provides very
            # unhelpful errors if you provide an empty/null/invalid resource ID,
            # and ignores the value otherwise. It's better to avoid setting it in
            # the conversion in this direction at all.
            # We don't bother processing storage_account_type because the
            # rest version is case insensitive.
            account = RestSystemCreatedStorageAccount(
                storage_account_hns_enabled=storage.storage_account_hns,
                storage_account_type=storage.storage_account_type,
            )
            return RestStorageAccountDetails(system_created_storage_account=account)
        else:
            return RestStorageAccountDetails(
                user_created_storage_account=RestUserCreatedStorageAccount(
                    arm_resource_id=RestArmResourceId(resource_id=storage)
                )
            )

    @classmethod
    def _from_rest_object(cls, rest_obj: RestStorageAccountDetails) -> "Union[str, SystemCreatedStorageAccount]":
        if not rest_obj:
            return None
        # TODO should we even bother check if both values are set and throw an error? This shouldn't be possible.
        if rest_obj.system_created_storage_account:
            resource_id = None
            if rest_obj.system_created_storage_account.arm_resource_id:
                resource_id = rest_obj.system_created_storage_account.arm_resource_id.resource_id
            return SystemCreatedStorageAccount(
                storage_account_hns=rest_obj.system_created_storage_account.storage_account_hns_enabled,
                storage_account_type=StorageAccountType(
                    rest_obj.system_created_storage_account.storage_account_type.lower()
                ),  # TODO validate storage account type?
                arm_resource_id=resource_id,
            )
        elif rest_obj.user_created_storage_account:
            return rest_obj.user_created_storage_account.arm_resource_id.resource_id
        else:
            return None  # TODO should this throw an error instead?


# Per-region information for registries.
@experimental
class RegistryRegionDetails:
    def __init__(
        self,
        *,
        acr_config: List[Union[str, SystemCreatedAcrAccount]] = None,
        location: str = None,
        storage_config: List[Union[str, SystemCreatedStorageAccount]] = None,
    ):
        """
        Details for each region a registry is in.

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
        :type storage_account_details: List[Union[str, SystemCreatedStorageAccount]]
        """
        self.acr_config = acr_config
        self.location = location
        self.storage_config = storage_config

    @classmethod
    def _from_rest_object(cls, rest_obj: RestRegistryRegionArmDetails) -> "RegistryRegionDetails":
        if not rest_obj:
            return None
        converted_acr_details = []
        if rest_obj.acr_details:
            converted_acr_details = [SystemCreatedAcrAccount._from_rest_object(
                acr) for acr in rest_obj.acr_details]
        storages = []
        if rest_obj.storage_account_details:
            storages = [SystemCreatedStorageAccount._from_rest_object(
                storages) for storages in rest_obj.storage_account_details]
        return RegistryRegionDetails(
            acr_config=converted_acr_details, location=rest_obj.location, storage_config=storages
        )

    def _to_rest_object(self) -> RestRegistryRegionArmDetails:
        converted_acr_details = []
        if self.acr_config:
            converted_acr_details = [SystemCreatedAcrAccount._to_rest_object(
                acr) for acr in self.acr_config]
        storages = []
        if self.storage_config:
            storages = [SystemCreatedStorageAccount._to_rest_object(
                storage) for storage in self.storage_config]
        return RestRegistryRegionArmDetails(
            acr_details=converted_acr_details,
            location=self.location,
            storage_account_details=storages,
        )

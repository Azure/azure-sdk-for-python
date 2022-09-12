# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Union

from azure.ai.ml.constants._registry import StorageAccountType


# This exists despite not being used by the schema validator because this entire
# class is an output only value from the API.
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
        :type arm_resource_id: str
        """
        self.acr_account_sku = acr_account_sku
        self.arm_resource_id = arm_resource_id


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


# Per-region information for registries.
class RegistryRegionArmDetails:
    def __init__(
        self,
        *,
        acr_config: List[Union[str, SystemCreatedAcrAccount]] = None,
        location: str = None,
        storage_config: List[Union[str, SystemCreatedStorageAccount]] = None,
    ):
        """
        Details for each region a registry is in.

        :param acr_details: List of ACR details. Each value can either be a
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

import pytest

from azure.ai.ml._restclient.v2022_10_01_preview.models import AcrDetails
from azure.ai.ml._restclient.v2022_10_01_preview.models import Registry as RestRegistry
from azure.ai.ml._restclient.v2022_10_01_preview.models import RegistryProperties
from azure.ai.ml._restclient.v2022_10_01_preview.models import RegistryRegionArmDetails as RestRegistryRegionArmDetails
from azure.ai.ml._restclient.v2022_10_01_preview.models import StorageAccountDetails
from azure.ai.ml._restclient.v2022_10_01_preview.models import StorageAccountType as RestStorageAccountType
from azure.ai.ml._restclient.v2022_10_01_preview.models import SystemCreatedAcrAccount, SystemCreatedStorageAccount
from azure.ai.ml.constants._registry import StorageAccountType

# from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.entities import Registry, RegistryRegionArmDetails

loc_1 = "USEast"
tags = {"test": "registry"}
name = "registry name"
# id = "registry id"
description = "registry description"
# There are two places in a registry where tags can live. Which do we care about?
interior_tags = {"properties": "have tags"}
pna = "Enabled"
discovery_url = "www.here-be-registries.com"
ipp = "a publisher name"
mrg = "MRG ID"
registry_uri = "example mlflow uri"
loc_2 = "The Moon"
acr_id_1 = "/subscriptions/sub_id/resourceGroups/some_rg/providers/Microsoft.ContainerRegistry/registries/acr_id"
sku = "a sku value"
acr_id_2 = "/subscriptions/sub_id/resourceGroups/some_rg/providers/Microsoft.ContainerRegistry/registries/acr_id2"
storage_id_1 = (
    "/subscriptions/sub_id/resourceGroups/some_rg/providers/Microsoft.Storage/storageAccounts/some_storage_account"
)
storage_id_2 = (
    "/subscriptions/sub_id/resourceGroups/some_rg/providers/Microsoft.Storage/storageAccounts/some_storage_account2"
)
hns = False


@pytest.mark.unittest
class TestRegistrySchema:
    """Hi. Is this test unexpectedly failing for you due to the following error?

    >       super(Registry, self).__init__(tags=tags, **kwargs)
    E       TypeError: __init__() missing 1 required keyword-only argument: 'location

    That probably means that you downloaded a new version of the 10-01-preview regions.json
    file located in the autorest directory. Don't do that, the original doesn't work for local testing.
    If you must anyway, remove 'location' value from the properties list of the 'RegistryTrackedResource'
    definition, and regenerate you autorest files."""

    def test_deserialize_from_autorest_object(self) -> None:
        rest_registry = RestRegistry(
            location=loc_1,
            tags=tags,
            name=name,
            id="registry id",
            properties=RegistryProperties(
                description=description,
                tags=interior_tags,
                public_network_access=pna,
                discovery_url=discovery_url,
                intellectual_property_publisher=ipp,
                managed_resource_group=mrg,
                ml_flow_registry_uri=registry_uri,
                region_details=[
                    RestRegistryRegionArmDetails(
                        location=loc_2,
                        acr_details=[
                            AcrDetails(user_created_acr_account=acr_id_1),
                            AcrDetails(
                                system_created_acr_account=SystemCreatedAcrAccount(
                                    acr_account_sku=sku, arm_resource_id=acr_id_2
                                )
                            ),
                        ],
                        storage_account_details=[
                            StorageAccountDetails(user_created_storage_account=storage_id_1),
                            StorageAccountDetails(
                                system_created_storage_account=SystemCreatedStorageAccount(
                                    arm_resource_id=storage_id_2,
                                    storage_account_hns_enabled=hns,
                                    storage_account_type=RestStorageAccountType.PREMIUM_LRS,
                                )
                            ),
                        ],
                    )
                ],
            ),
        )
        registry_entity = Registry._from_rest_object(rest_registry)

        assert registry_entity
        assert registry_entity.description == description
        assert registry_entity.location == loc_1
        assert registry_entity.tags == interior_tags
        # TODO https://dev.azure.com/msdata/Vienna/_workitems/edit/1971490/
        # assert registry_entity.name == name #  TODO Local workspace obj doesn't record name besides pushing up to super class. Should we?
        # assert registry_entity.id == id # TODO Local workspace obj doesn't record id. Should we?
        assert registry_entity.public_network_access == pna
        assert registry_entity.discovery_url == discovery_url
        assert registry_entity.intellectual_property_publisher == ipp
        assert registry_entity.managed_resource_group == mrg
        assert registry_entity.mlflow_registry_uri == registry_uri

        assert registry_entity.region_details
        details = registry_entity.region_details
        assert len(details) == 1
        assert details[0].location == loc_2
        assert details[0].acr_config
        assert details[0].storage_config

        acrs = details[0].acr_config
        assert len(acrs) == 2
        assert acrs[0] == acr_id_1
        assert acrs[1].arm_resource_id == acr_id_2
        assert acrs[1].acr_account_sku == sku

        storages = details[0].storage_config
        assert len(storages) == 2
        assert storages[0] == storage_id_1
        assert storages[1].arm_resource_id == storage_id_2
        assert storages[1].storage_account_hns == hns
        assert storages[1].storage_account_type == StorageAccountType.PREMIUM_LRS

    def test_registry_load_from_dict(self):
        registry_as_dict = {
            "name": name,
            "location": loc_1,
            "description": description,
            "tags": tags,
            "public_network_access": pna,
            "replication_locations": [{"location": loc_1, "storage_config": [storage_id_1]}],
            "container_registry": acr_id_1,
        }

        registry = Registry._load(registry_as_dict)
        assert registry
        assert registry.location == loc_1
        assert registry.description == description
        assert registry.tags == tags
        assert registry.public_network_access == pna
        assert registry.region_details[0].acr_config[0] == acr_id_1
        assert registry.region_details[0].location == loc_1
        assert registry.region_details[0].storage_config[0] == storage_id_1

    def test_registry_load_from_dict_failure_cases(self):
        # TODO https://dev.azure.com/msdata/Vienna/_workitems/edit/1971490/
        pass

    def test_registry_dictonary_modifier(self):
        details = [1, 2, 3]
        input1 = {"replication_locations": details}
        Registry._convert_yaml_dict_to_entity_input(input1)
        assert input1["region_details"] == details

        details = [type("", (), {})()]  # empty object for attribute addition testing
        input2 = {"replication_locations": details, "container_registry": "123"}
        Registry._convert_yaml_dict_to_entity_input(input2)
        assert input2["region_details"][0].acr_config == ["123"]

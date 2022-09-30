import pytest

from azure.ai.ml._restclient.v2022_10_01_preview.models import AcrDetails, RegistryProperties, StorageAccountDetails, UserCreatedAcrAccount, UserCreatedStorageAccount
from azure.ai.ml._restclient.v2022_10_01_preview.models import Registry as RestRegistry
from azure.ai.ml._restclient.v2022_10_01_preview.models import RegistryRegionArmDetails as RestRegistryRegionArmDetails
from azure.ai.ml._restclient.v2022_10_01_preview.models import StorageAccountType as RestStorageAccountType
from azure.ai.ml._restclient.v2022_10_01_preview.models import SystemCreatedAcrAccount as RestSystemCreatedAcrAccount
from azure.ai.ml._restclient.v2022_10_01_preview.models import SystemCreatedStorageAccount as RestSystemCreatedStorageAccount
from azure.ai.ml._restclient.v2022_10_01_preview.models import ArmResourceId as RestArmResourceId
from azure.ai.ml.constants._registry import StorageAccountType

# from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.entities import Registry, RegistryRegionDetails, SystemCreatedAcrAccount, SystemCreatedStorageAccount

# Define a bunch of constants to use in crafting test values.
loc_1 = "USEast"
exterior_tags = {"test": "registry"}
name = "registry name"
# id = "registry id"
description = "registry description"
# There are two places in a registry where tags can live. We only care about 
# tags set at the top level, AKA the 'exterior_tags' defined above/
# These interior tags only exists to show that the value technically
# exists due to swagger-side inheritance in the autotest.
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
class TestRegistryEntity:
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
            tags=exterior_tags,
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
                            AcrDetails(user_created_acr_account=UserCreatedAcrAccount(arm_resource_id=RestArmResourceId(resource_id=acr_id_1))),
                            AcrDetails(
                                system_created_acr_account=RestSystemCreatedAcrAccount(
                                    acr_account_sku=sku, arm_resource_id=RestArmResourceId(resource_id=acr_id_2)
                                )
                            ),
                        ],
                        storage_account_details=[
                            StorageAccountDetails(user_created_storage_account=UserCreatedStorageAccount(arm_resource_id=RestArmResourceId(resource_id=storage_id_1))),
                            StorageAccountDetails(
                                system_created_storage_account=RestSystemCreatedStorageAccount(
                                    arm_resource_id=RestArmResourceId(resource_id=storage_id_2),
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
        assert registry_entity.tags == exterior_tags
        # TODO https://dev.azure.com/msdata/Vienna/_workitems/edit/1971490/
        # assert registry_entity.name == name #  TODO Local workspace obj doesn't record name besides pushing up to super class. Should we?
        # assert registry_entity.id == id # TODO Local workspace obj doesn't record id. Should we?
        assert registry_entity.public_network_access == pna
        assert registry_entity.discovery_url == discovery_url
        assert registry_entity.intellectual_property_publisher == ipp
        assert registry_entity.managed_resource_group == mrg
        assert registry_entity.mlflow_registry_uri == registry_uri

        assert registry_entity.replication_locations
        details = registry_entity.replication_locations
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
            "tags": exterior_tags,
            "public_network_access": pna,
            "replication_locations": [{"location": loc_1, "storage_config": [storage_id_1]}],
            "container_registry": acr_id_1,
        }

        registry = Registry._load(registry_as_dict)
        assert registry
        assert registry.location == loc_1
        assert registry.description == description
        assert registry.tags == exterior_tags
        assert registry.public_network_access == pna
        assert registry.replication_locations[0].acr_config[0] == acr_id_1
        assert registry.replication_locations[0].location == loc_1
        assert registry.replication_locations[0].storage_config[0] == storage_id_1

    def test_registry_dictonary_modifier(self):
        details = [type("", (), {})()]  # empty object for attribute addition testing
        input2 = {"replication_locations": details, "container_registry": "123"}
        Registry._convert_yaml_dict_to_entity_input(input2)
        assert input2["replication_locations"][0].acr_config == ["123"]

    def test_system_acr_serialization(self):
        user_acr = "some user id"
        system_acr = SystemCreatedAcrAccount(acr_account_sku="prEmiUm", arm_resource_id="some system id")
        rest_user_acr = SystemCreatedAcrAccount._to_rest_object(user_acr)
        rest_system_acr = SystemCreatedAcrAccount._to_rest_object(system_acr)

        assert isinstance(rest_user_acr, AcrDetails)
        assert isinstance(rest_system_acr, AcrDetails)

        assert rest_user_acr.user_created_acr_account.arm_resource_id.resource_id == "some user id"
        # Ensure that arm_resource_id is never set by entity->rest converter.
        assert rest_system_acr.system_created_acr_account.arm_resource_id == None
        assert rest_system_acr.system_created_acr_account.acr_account_sku == "Premium"

        new_user_acr = SystemCreatedAcrAccount._from_rest_object(rest_user_acr)
        new_system_acr = SystemCreatedAcrAccount._from_rest_object(rest_system_acr)
        # ... but still test that ID is set in the other direction
        rest_system_acr.system_created_acr_account.arm_resource_id = RestArmResourceId(resource_id="another id")
        new_system_acr_2 = SystemCreatedAcrAccount._from_rest_object(rest_system_acr)
        assert new_user_acr == "some user id"
        assert new_system_acr.acr_account_sku == "Premium"
        assert new_system_acr.arm_resource_id == None
        assert new_system_acr_2.arm_resource_id == "another id"

    def test_system_storage_serialization(self):
        user_storage = "some user storage id"
        system_storage = SystemCreatedStorageAccount(storage_account_hns=True, storage_account_type=StorageAccountType.PREMIUM_LRS, arm_resource_id="some managed storage id")

        rest_user_storage = SystemCreatedStorageAccount._to_rest_object(user_storage)
        rest_system_storage = SystemCreatedStorageAccount._to_rest_object(system_storage)
        assert rest_user_storage.user_created_storage_account.arm_resource_id.resource_id == "some user storage id"
        assert rest_system_storage.system_created_storage_account.storage_account_hns_enabled == True
        assert rest_system_storage.system_created_storage_account.storage_account_type == StorageAccountType.PREMIUM_LRS
        # Ensure that arm_resource_id is never set by entity->rest converter.
        assert rest_system_storage.system_created_storage_account.arm_resource_id == None

        # ... but still test that ID is set in the other direction
        rest_system_storage.system_created_storage_account.arm_resource_id = RestArmResourceId(resource_id="another storage id")
        new_user_storage = SystemCreatedStorageAccount._from_rest_object(rest_user_storage)
        new_system_storage = SystemCreatedStorageAccount._from_rest_object(rest_system_storage)

        assert new_user_storage == "some user storage id"
        assert new_system_storage.arm_resource_id == "another storage id"
        assert new_system_storage.storage_account_hns == True
        assert new_system_storage.storage_account_type == StorageAccountType.PREMIUM_LRS

    def test_system_region_details_serialization(self):
        region_detail = RegistryRegionDetails(acr_config=[SystemCreatedAcrAccount(acr_account_sku="Premium")],
            location="USEast2",
            storage_config=[SystemCreatedStorageAccount(storage_account_hns=False, storage_account_type=StorageAccountType.PREMIUM_LRS)])
        rest_region_detail = region_detail._to_rest_object()

        assert rest_region_detail.acr_details[0].system_created_acr_account.acr_account_sku == "Premium"
        assert rest_region_detail.location == "USEast2"
        assert rest_region_detail.storage_account_details[0].system_created_storage_account.storage_account_hns_enabled == False

        new_region_detail = RegistryRegionDetails._from_rest_object(rest_region_detail)

        assert new_region_detail.acr_config[0].acr_account_sku == "Premium"
        assert new_region_detail.location == "USEast2"
        assert new_region_detail.storage_config[0].storage_account_type == StorageAccountType.PREMIUM_LRS

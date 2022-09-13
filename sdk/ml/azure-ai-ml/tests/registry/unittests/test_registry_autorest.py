import pytest

# from azure.ai.ml.constants._registry import StorageAccountType
# from azure.ai.ml.entities._util import load_from_dict
# from azure.ai.ml.entities import Registry

# from azure.ai.ml._restclient.v2022_10_01_preview.models import Registry as RestRegistry
# from azure.ai.ml._restclient.v2022_10_01_preview.models import RegistryProperties, RegistryRegionArmDetails, AcrDetails, StorageAccountDetails, SystemCreatedAcrAccount, SystemCreatedStorageAccount


@pytest.mark.unittest
class TestRegistrySchema:
    def test_deserialize_from_autorest_object(self) -> None:
        # TODO Implement this once Regisy._from_rest_object is implemented
        """rest_registry = RestRegistry(
            location="USEast",
            tags={"test" : "registry"},

            properties=RegistryProperties(
                description="registry description",
                tags={"properties" : "exist"},
                public_network_access="network access",
                discovery_url="www.here-be-registries.com",
                intellectual_property_publisher="a publisher name",
                managed_resource_group="MRG ID",
                ml_flow_registry_uri="example flow uri",
                region_details=[RegistryRegionArmDetails(
                    location="The Moon",
                    acr_details=[
                        AcrDetails(user_created_acr_account="user acr ID"),
                        AcrDetails(system_created_acr_account=SystemCreatedAcrAccount(
                            acr_account_sku="a sku value",
                            arm_resource_id="system acr id"
                        ))],
                    storage_account_details=[
                        StorageAccountDetails(user_created_storage_account="user storage ID"),
                        StorageAccountDetails(system_created_storage_account=SystemCreatedStorageAccount(
                            arm_resource_id="system storage id",
                            storage_account_hns_enabled=False,
                            storage_account_type=StorageAccountType.PREMIUM_LRS
                        ))
                    ]
                )]
            ))
        registry_entity = Registry._from_rest_object(rest_registry)
        assert registry_entity"""

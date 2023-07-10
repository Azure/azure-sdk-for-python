from pathlib import Path

import pytest
import yaml
from marshmallow.exceptions import ValidationError

from azure.ai.ml._schema.registry import RegistrySchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PublicNetworkAccess
from azure.ai.ml.constants._registry import AcrAccountSku, StorageAccountType
from azure.ai.ml.entities import RegistryRegionDetails, SystemCreatedAcrAccount, SystemCreatedStorageAccount
from azure.ai.ml.entities._util import load_from_dict


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestRegistrySchema:
    def test_deserialize_from_yaml(self) -> None:
        path = Path("./tests/test_configs/registry/registry_valid.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            registry = load_from_dict(RegistrySchema, target, context)
            assert registry
            assert registry["name"] == "registry_name"
            assert registry["id"] == "registry_id"
            assert registry["tags"] == {"purpose": "testing", "other_tag": "value"}
            assert registry["location"] == "EastUS2"
            assert registry["public_network_access"] == PublicNetworkAccess.DISABLED
            assert registry["intellectual_property"].publisher == "registry_publisher"
            assert (
                registry["container_registry"]
                == "/subscriptions/sub_id/resourceGroups/some_rg/providers/Microsoft.ContainerRegistry/registries/acr_id"
            )
            assert len(registry["replication_locations"]) == 1

            detail = registry["replication_locations"][0]
            assert isinstance(detail, RegistryRegionDetails)
            assert detail.location == "EastUS"
            storages = detail.storage_config

            assert isinstance(storages, SystemCreatedStorageAccount)
            assert not storages.storage_account_hns
            assert storages.storage_account_type == StorageAccountType.STANDARD_RAGRS
            assert storages.replication_count == 1

    def test_deserialize_from_yaml_with_system_acr(self) -> None:
        path = Path("./tests/test_configs/registry/registry_valid_2.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            registry = load_from_dict(RegistrySchema, target, context)
            assert registry
            assert isinstance(registry["container_registry"], SystemCreatedAcrAccount)
            assert registry["container_registry"].acr_account_sku == AcrAccountSku.PREMIUM

    def test_deserialize_from_yaml_with_no_acr(self) -> None:
        path = Path("./tests/test_configs/registry/registry_valid_3.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            registry = load_from_dict(RegistrySchema, target, context)
            assert registry
            assert isinstance(registry["container_registry"], SystemCreatedAcrAccount)
            assert registry["container_registry"].acr_account_sku == AcrAccountSku.PREMIUM

    def test_deserialize_bad_storage_account_type(self) -> None:
        path = Path("./tests/test_configs/registry/registry_bad_storage_account_type.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            with pytest.raises(Exception) as e_info:
                load_from_dict(RegistrySchema, target, context)
            assert e_info
            assert isinstance(e_info._excinfo[1], ValidationError)
            assert "NOT_A_REAL_ACCOUNT_TYPE" in e_info._excinfo[1].messages[0]
            assert "passed is not in set" in e_info._excinfo[1].messages[0]

    def test_deserialize_bad_arm_resource_id(self) -> None:
        path = Path("./tests/test_configs/registry/registry_bad_arm_resource_id.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            with pytest.raises(Exception) as e_info:
                load_from_dict(RegistrySchema, target, context)
            assert e_info
            assert isinstance(e_info._excinfo[1], ValidationError)
            assert "container_registry" in e_info._excinfo[1].messages[0]
            assert "Invalid value" in e_info._excinfo[1].messages[0]

    def test_deserialize_replication_counts(self) -> None:
        path = Path("./tests/test_configs/registry/registry_valid_replication_count.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            registry = load_from_dict(RegistrySchema, target, context)
            registry["replication_locations"][0].storage_config.replication_count == 5

        path = Path("./tests/test_configs/registry/registry_bad_replication_count.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            with pytest.raises(Exception) as e_info:
                load_from_dict(RegistrySchema, target, context)
            assert e_info
            assert isinstance(e_info._excinfo[1], ValidationError)
            assert "replication_count" in e_info._excinfo[1].messages[0]
            assert "Invalid value" in e_info._excinfo[1].messages[0]

        path = Path("./tests/test_configs/registry/registry_valid_lone_replication_count.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            registry = load_from_dict(RegistrySchema, target, context)
            registry["replication_locations"][0].storage_config.replication_count == 6
            registry["replication_locations"][0].storage_config.storage_account_hns == False
            registry["replication_locations"][0].storage_config.storage_account_type == StorageAccountType.STANDARD_LRS

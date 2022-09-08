from pathlib import Path

import pytest
import yaml
from marshmallow.exceptions import ValidationError

from azure.ai.ml._schema.registry import RegistrySchema
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._util import load_from_dict


@pytest.mark.unittest
class TestRegistrySchema:
    def test_deserialize(self) -> None:
        path = Path("./tests/test_configs/registry/registry_valid.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            registry = load_from_dict(RegistrySchema, target, context)
            assert registry

    def test_deserialize_bad_storage_account_type(self) -> None:
        path = Path("./tests/test_configs/registry/registry_bad_storage_account_type.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            with pytest.raises(Exception) as e_info:
                load_from_dict(RegistrySchema, target, context)
            assert e_info
            assert isinstance(e_info._excinfo[1], ValidationError)
            assert "Must be one of" in e_info._excinfo[1].messages[0]

import pytest
import yaml
from marshmallow import fields
from marshmallow.exceptions import ValidationError
from marshmallow.schema import Schema

from azure.ai.ml import load_data
from azure.ai.ml._schema import ArmStr, ArmVersionedStr
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.constants._common import (
    AZUREML_RESOURCE_PROVIDER,
    BASE_PATH_CONTEXT_KEY,
    NAMED_RESOURCE_ID_FORMAT,
    RESOURCE_ID_FORMAT,
)
from azure.ai.ml.entities import Data


class DummyStr(ArmStr):
    def __init__(self, **kwargs):
        super().__init__()
        self.azureml_type = "dummy"


class FooVersionedStr(ArmVersionedStr):
    def __init__(self, **kwargs):
        super().__init__()
        self.azureml_type = "foo"


class DummySchema(Schema):
    environment = DummyStr()


class FooSchema(Schema):
    model = FooVersionedStr()


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestField:
    def test_arm_str(self, mock_workspace_scope: OperationScope) -> None:
        schema = DummySchema()
        name = "resourceName"

        input_data = {"environment": f"azureml:{name}"}
        output_data = {"environment": name}
        dumped_data = {"environment": f"azureml:{name}"}
        data = schema.load(input_data)
        assert data == output_data
        assert schema.dump(data) == dumped_data

    def test_arm_str_with_fully_arm_id(self, mock_workspace_scope: OperationScope) -> None:
        schema = DummySchema()
        name = "resourceName"
        resource_id_without_version = (
            RESOURCE_ID_FORMAT.format(
                mock_workspace_scope.subscription_id,
                mock_workspace_scope.resource_group_name,
                AZUREML_RESOURCE_PROVIDER,
                mock_workspace_scope.workspace_name,
            )
            + f"/foo/{name}"
        )

        input_data = {"environment": f"azureml:{resource_id_without_version}"}
        output_data = {"environment": resource_id_without_version}
        dumped_data = {"environment": f"azureml:{resource_id_without_version}"}
        data = schema.load(input_data)
        assert data == output_data
        assert schema.dump(data) == dumped_data

    def test_arm_str_failed(self) -> None:
        schema = DummySchema()
        input_data = {"environment": "some_arm_id"}
        with pytest.raises(ValidationError):
            schema.load(input_data)

    def test_arm_versioned_str(self, mock_workspace_scope: OperationScope) -> None:
        name = "resourceName"
        version = "3.14"
        resource_id_without_version = (
            RESOURCE_ID_FORMAT.format(
                mock_workspace_scope.subscription_id,
                mock_workspace_scope.resource_group_name,
                AZUREML_RESOURCE_PROVIDER,
                mock_workspace_scope.workspace_name,
            )
            + f"/foo/{name}"
        )
        non_aml_resource_id_without_version = NAMED_RESOURCE_ID_FORMAT.format(
            mock_workspace_scope.subscription_id,
            mock_workspace_scope.resource_group_name,
            "bar",
            mock_workspace_scope.workspace_name,
            "foo",
            name,
        )

        schema = FooSchema()
        input_data = {"model": f"azureml:{name}:{version}"}
        output_data = {"model": f"{name}:{version}"}
        dumped_data = {"model": f"azureml:{name}:{version}"}
        data = schema.load(input_data)
        assert data == output_data
        assert schema.dump(data) == dumped_data

        schema = FooSchema()
        input_data = {"model": f"azureml:{resource_id_without_version}/versions/{version}"}
        output_data = {"model": f"{resource_id_without_version}/versions/{version}"}
        dumped_data = {"model": f"azureml:{resource_id_without_version}/versions/{version}"}
        data = schema.load(input_data)
        assert data == output_data
        assert schema.dump(data) == dumped_data

        input_data = {"model": f"azureml:{name}/versions/{version}"}
        with pytest.raises(Exception):
            data = schema.load(input_data)

        with pytest.raises(Exception):
            input_data = {"model": f"azureml:{resource_id_without_version}:{version}"}
            data = schema.load(input_data)

        with pytest.raises(Exception):
            input_data = {"model": f"azureml:{resource_id_without_version}"}
            data = schema.load(input_data)

        with pytest.raises(Exception):
            input_data = {"model": f"azureml:{non_aml_resource_id_without_version}"}
            data = schema.load(input_data)

    def test_arm_versioned_str_label(self, mock_workspace_scope: OperationScope) -> None:
        name = "resourceName"
        version = "latest"

        schema = FooSchema()
        input_data = {"model": f"azureml:{name}@{version}"}
        output_data = {"model": f"{name}@{version}"}
        dumped_data = {"model": f"azureml:{name}@{version}"}
        data = schema.load(input_data)
        assert data == output_data
        assert schema.dump(data) == dumped_data

    def test_arm_versioned_str_failed(self, mock_workspace_scope: OperationScope) -> None:
        schema = FooSchema()
        input_data = {"model": "/subscription/something/other/value/name:some_version"}
        with pytest.raises(ValidationError):
            schema.load(input_data)
        input_data = {"model": "azureml:/subscription/something/other/value/name"}
        with pytest.raises(ValidationError):
            schema.load(input_data)
        input_data = {"model": "azureml:/subscription/something/other/value/name/versions"}
        with pytest.raises(ValidationError):
            schema.load(input_data)
        input_data = {"model": "azureml:/subscription/something/other/value/name/versions/"}
        with pytest.raises(ValidationError):
            schema.load(input_data)
        input_data = {"model": "azureml:/subscription/something/other/value/name/"}

    def test_version_types(self, tmp_path):
        data_name = f"version_rand_name"
        p = tmp_path / "version_float.yml"
        p.write_text(
            f"""
name: {data_name}
version: 3.12
path: ./bla"""
        )
        asset = load_data(source=p)
        assert asset.version == "3.12"

        p = tmp_path / "version_int.yml"
        p.write_text(
            f"""
name: {data_name}
version: 3
path: ./bla"""
        )
        asset = load_data(source=p)
        assert asset.version == "3"

        p = tmp_path / "version_str.yml"
        p.write_text(
            f"""
name: {data_name}
version: foobar
path: ./bla"""
        )
        asset = load_data(source=p)
        assert asset.version == "foobar"

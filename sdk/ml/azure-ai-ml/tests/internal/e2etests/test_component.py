# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os.path
from typing import Callable, Dict, List

import pydash
import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient, load_component
from azure.ai.ml._internal.entities import InternalComponent

from .._utils import PARAMETERS_TO_TEST


def create_component(
    client: MLClient,
    component_name: str,
    path="./tests/test_configs/components/helloworld_component.yml",
    params_override=None,
    is_anonymous=False,
):
    default_param_override = [{"name": component_name}]
    if params_override is None:
        params_override = default_param_override
    else:
        params_override += default_param_override

    command_component = load_component(
        source=path,
        params_override=params_override,
    )
    return client.components.create_or_update(command_component, is_anonymous=is_anonymous)


def load_registered_component(
    client: MLClient,
    component_name: str,
    component_version: str,
    omit_fields: List[str],
) -> Dict:
    """Load registered component from server and omit some fields."""
    component_entity = client.components.get(name=component_name, version=component_version)
    component_rest_object = component_entity._to_rest_object()
    return pydash.omit(component_rest_object.properties.component_spec, *omit_fields)


# previous bodiless_matcher fixture doesn't take effect because of typo, please add it in method level if needed


@pytest.mark.usefixtures(
    "recorded_test",
    "enable_internal_components",
    "mock_code_hash",
    "mock_asset_name",
    "mock_component_hash",
)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestComponent(AzureRecordedTestCase):
    @pytest.mark.parametrize(
        "yaml_path,inputs,runsettings_dict,pipeline_runsettings_dict",
        PARAMETERS_TO_TEST,
    )
    def test_component_create(
        self,
        client: MLClient,
        randstr: Callable[[], str],
        yaml_path: str,
        inputs: Dict,
        runsettings_dict: Dict,
        pipeline_runsettings_dict: Dict,
    ) -> None:
        component_name = randstr("component_name")
        component_resource = create_component(client, component_name, path=yaml_path)
        assert component_resource.name == component_name
        assert component_resource.code
        assert component_resource.creation_context

        component = client.components.get(component_name, component_resource.version)
        assert component_resource._to_dict() == component._to_dict()
        assert component_resource.creation_context

    @pytest.mark.parametrize(
        "yaml_path,inputs,runsettings_dict,pipeline_runsettings_dict",
        PARAMETERS_TO_TEST,
    )
    def test_component_load(
        self,
        client: MLClient,
        randstr: Callable[[], str],
        yaml_path: str,
        inputs: Dict,
        runsettings_dict: Dict,
        pipeline_runsettings_dict: Dict,
    ) -> None:
        omit_fields = ["id", "creation_context", "code", "name"]
        component_name = randstr("component_name")

        component_resource = create_component(client, component_name, path=yaml_path)
        loaded_dict = load_registered_component(client, component_name, component_resource.version, omit_fields)

        base_dir = "./tests/test_configs/internal"
        json_path = yaml_path.rsplit(".", 1)[0] + ".json"
        json_path = os.path.join(base_dir, "loaded_from_rest", os.path.relpath(json_path, base_dir))
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        if not os.path.isfile(json_path):
            with open(json_path, "w") as f:
                json.dump(loaded_dict, f, indent=2)
        with open(json_path, "r") as f:
            expected_dict = json.load(f)
            expected_dict["_source"] = "REMOTE.WORKSPACE.COMPONENT"

            # default value for datatransfer
            if expected_dict["type"] == "DataTransferComponent" and "datatransfer" not in expected_dict:
                expected_dict["datatransfer"] = {"allow_overwrite": "True"}

            # skip environment in arm string
            if "environment" in loaded_dict and isinstance(loaded_dict["environment"], str):
                omit_fields.append("environment")
            # TODO: check if loaded environment is expected to be an ordered dict
            assert pydash.omit(loaded_dict, *omit_fields) == pydash.omit(expected_dict, *omit_fields)

    def test_component_code_hash(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        yaml_path = "./tests/test_configs/internal/command-component-reuse/powershell_copy.yaml"
        expected_snapshot_id = "75c43313-4777-b2e9-fe3a-3b98cabfaa77"

        for component_name_key in ["component_name", "component_name2"]:
            component_name = randstr(component_name_key)
            component_resource: InternalComponent = create_component(client, component_name, path=yaml_path)
            assert component_resource.code.endswith(f"codes/{expected_snapshot_id}/versions/1")

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os.path
from typing import Callable, Dict, List

from devtools_testutils import AzureRecordedTestCase, set_bodiless_matcher
import pydash
import pytest

from azure.ai.ml import MLClient, load_component

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


@pytest.mark.fixture(autouse=True)
def bodiless_matching(test_proxy):
    set_bodiless_matcher()


@pytest.mark.usefixtures(
    "recorded_test", "enable_internal_components", "mock_code_hash", "mock_asset_name", "mock_component_hash"
)
@pytest.mark.e2etest
class TestComponent(AzureRecordedTestCase):
    @pytest.mark.parametrize(
        "yaml_path",
        list(map(lambda x: x[0], PARAMETERS_TO_TEST)),
    )
    def test_component_create(self, client: MLClient, randstr: Callable[[], str], yaml_path: str) -> None:
        component_name = randstr("component_name")
        component_resource = create_component(client, component_name, path=yaml_path)
        assert component_resource.name == component_name
        assert component_resource.code
        assert component_resource.creation_context

        component = client.components.get(component_name, component_resource.version)
        assert component_resource._to_dict() == component._to_dict()
        assert component_resource.creation_context

    @pytest.mark.parametrize(
        "yaml_path",
        list(map(lambda x: x[0], PARAMETERS_TO_TEST)),
    )
    def test_component_load(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
        yaml_path: str,
    ) -> None:
        omit_fields = ["id", "creation_context", "code", "name"]
        component_name = randstr("component_name")

        component_resource = create_component(client, component_name, path=yaml_path)
        loaded_dict = load_registered_component(client, component_name, component_resource.version, omit_fields)

        json_path = yaml_path.rsplit(".", 1)[0] + ".loaded_from_rest.json"
        if not os.path.isfile(json_path):
            with open(json_path, "w") as f:
                json.dump(loaded_dict, f, indent=2)
        with open(json_path, "r") as f:
            expected_dict = json.load(f)

            # TODO: check if loaded environment is expected to be an ordered dict
            assert pydash.omit(loaded_dict, *omit_fields) == pydash.omit(expected_dict, *omit_fields)

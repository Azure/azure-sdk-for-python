import yaml
import pytest
import tempfile
from pathlib import Path

from marshmallow import ValidationError

from azure.ai.ml import load_component, Input, Output
from azure.ai.ml.dsl._utils import _change_working_dir
from mldesigner import generate_package
from mldesigner._exceptions import UserErrorException
from mldesigner._generate._generate_package_impl import AssetsUtil

from mldesigner._generate._generators._components_generator import (
    SingleComponentReferenceGenerator,
    ComponentReferenceGenerator,
)
from mldesigner._generate._generators._components_impl_generator import (
    SingleComponentEntityGenerator,
    ComponentImplGenerator,
)
from mldesigner._generate._generators._module_generator import get_unique_component_func_names
from mldesigner._generate._generators._param_generator import ParamGenerator
from .._util import _DSL_TIMEOUT_SECOND

"""
Note: these test requires azure-ai-ml and mldesigner package to run.
"""


def write_expected_file(file_path, content):
    with open(file_path, "w") as f:
        f.write(content)


def assert_file_same(file_path, content):
    # return write_expected_file(file_path, content)
    with open(file_path) as f:
        expected_content = f.read().strip()
    content = content.strip()
    assert expected_content == content


@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestGenerateComponent:
    def test_gen_component_inputs(self) -> None:
        given_inputs = {
            "test1": (
                Input(**{"type": "number", "default": 1, "min": 1, "max": 2, "optional": True}),
                "number (optional, min: 1.0, max: 2.0)",
            ),
            "test2": (
                Input(**{"type": "uri_folder", "description": "a uri folder"}),
                "a uri folder (type: uri_folder)",
            ),
            "test3": (
                Input(**{"type": "mlflow_model", "description": "a mlflow model"}),
                "a mlflow model (type: mlflow_model)",
            ),
            "test4": (
                Input(**{"type": "string", "enum": ["hello", "world"]}),
                "string (enum: ['hello', 'world'])",
            ),
            "test5": (
                Input(**{"type": "boolean", "default": False}),
                "boolean",
            ),
            "test6": (Input(**{"type": "unknown"}), "unknown (type: unknown)"),
        }
        for key, val in given_inputs.items():
            param = ParamGenerator(key, val[0])
            assert param.comment == val[1]

    def test_gen_component_outputs(self) -> None:
        given_inputs = {
            "test1": (
                Output(**{"type": "uri_folder", "description": "a uri folder"}),
                "a uri folder (type: uri_folder)",
            ),
            "test2": (
                Output(**{"type": "mlflow_model", "description": "a mlflow model"}),
                "a mlflow model (type: mlflow_model)",
            ),
            "test3": (Output(**{"type": "unknown"}), "unknown (type: unknown)"),
        }
        for key, val in given_inputs.items():
            param = ParamGenerator(key, val[0])
            assert param.comment == val[1]

    def test_component_name_resolve(self) -> None:
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        components = [
            load_component(path=yaml_file),
            # another version
            load_component(path=yaml_file, params_override=[{"version": "0.0.2"}]),
            # another name with same sanitized name
            load_component(path=yaml_file, params_override=[{"name": "microsoftsamples_command_component__basic"}]),
            # another name with same sanitized name
            load_component(path=yaml_file, params_override=[{"name": "microsoftsamples_command_component___basic"}]),
            # another version with same sanitized version
            load_component(path=yaml_file, params_override=[{"version": "0.0_2"}]),
        ]
        expected_component_names = {
            "microsoftsamples_command_component_basic",
            "microsoftsamples_command_component_basic_0_0_2",
            "microsoftsamples_command_component_basic_0_0_1",
            "microsoftsamples_command_component_basic_0_0_1_a794e8ea_abba_2c71_42d4_8459444d1aca",
            "microsoftsamples_command_component_basic_0_0_2_cc1d24a9_a0a5_8ae4_c393_04420ff3d0b2",
        }

        # run multiple time should get same result
        for _ in range(3):
            results, _ = get_unique_component_func_names(components)
            assert set(results.keys()) == expected_component_names

        # same name+version should raise error
        components = [
            load_component(path=yaml_file),
            load_component(path=yaml_file),
        ]
        _, errors = get_unique_component_func_names(components)
        error_msg = "Duplicate component microsoftsamples_command_component_basic:0.0.1 found. "
        assert len(errors) == 1
        assert error_msg in errors[0]

    def test_gen_local_component(self) -> None:
        yaml_file = "./tests/test_configs/components/input_types_component.yml"
        expected_entity_file = "./tests/dsl/generate_package_expected_files/single_command_component_entity"
        expected_function_file = "./tests/dsl/generate_package_expected_files/single_command_component_ref"
        component_entity = load_component(path=yaml_file)

        entity_generator = SingleComponentEntityGenerator(component_entity=component_entity)
        assert_file_same(expected_entity_file, entity_generator.generate())

        fun_generator = SingleComponentReferenceGenerator(component_entity=component_entity, module_dir=Path("./tests"))
        assert_file_same(expected_function_file, fun_generator.generate())

    def test_gen_package_from_local_components(self):
        components = []
        with open("./tests/dsl/generate_package_expected_files/component_files_to_generate.txt") as f:
            files = f.read().splitlines()
        for file in files:
            components.append(load_component(file))

        expected_entity_file = "./tests/dsl/generate_package_expected_files/_components_impl"
        expected_function_file = "./tests/dsl/generate_package_expected_files/_components"
        components = sorted(components, key=lambda c: f"{c.name}:{c.version}")

        name_2_components, errors = get_unique_component_func_names(components)
        assert len(errors) == 0

        entity_generator = ComponentImplGenerator(name_2_components)
        assert_file_same(expected_entity_file, entity_generator.generate())

        func_generator = ComponentReferenceGenerator(name_2_components, module_dir=Path("./tests"))
        assert_file_same(expected_function_file, func_generator.generate())

    def test_list_asset_to_dict(self):
        asset_list = [
            "path/to/components/",
            "path/to/components/*parallel*/*.yaml",
            "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name1/components/component1",
            "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name1/components/component2",
            "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name1/components/component*",
            "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name2/components/*",
            "azureml://registries/registry1/components/component*",
            "azureml://registries/registry1/components/component1",
            "azureml://registries/registry2/components/component*",
        ]
        asset_dict = AssetsUtil.load_from_list(asset_list)
        assert asset_dict.components == {
            "components": ["path/to/components/", "path/to/components/*parallel*/*.yaml"],
            "registry1": [
                "azureml://registries/registry1/components/component*",
                "azureml://registries/registry1/components/component1",
            ],
            "registry2": [
                "azureml://registries/registry2/components/component*",
            ],
            "ws_name1": [
                "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name1/components/component1",
                "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name1/components/component2",
                "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name1/components/component*",
            ],
            "ws_name2": ["azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name2/components/*"],
        }

        # illegal cases
        asset_list = [
            "azureml://subscriptions/sub_id/resourcegroups/rg_id_1/workspaces/ws_name1/components/component1",
            "azureml://subscriptions/sub_id/resourcegroups/rg_id_2/workspaces/ws_name1/components/component2",
        ]
        with pytest.raises(UserErrorException) as e:
            AssetsUtil.load_from_list(asset_list)
        assert "has conflict module name" in str(e.value)

        asset_list = [
            "azureml://subscriptions/sub_id/resourcegroups/rg_id_1/workspaces/ws_name1/components/component1",
            "azureml://registries/ws_name1/components/component*",
        ]
        with pytest.raises(UserErrorException) as e:
            AssetsUtil.load_from_list(asset_list)
        assert "has conflict module name" in str(e.value)

        # test sanitized workspace name conflict
        asset_list = [
            "azureml://subscriptions/sub_id/resourcegroups/rg_id_1/workspaces/ws_name1/components/component1",
            "azureml://subscriptions/sub_id/resourcegroups/rg_id_1/workspaces/ws-name1/components/component1",
        ]
        with pytest.raises(UserErrorException) as e:
            AssetsUtil.load_from_list(asset_list)
        assert "has conflict module name ws_name1" in str(e.value)

    def test_load_assets_from_file(self):

        assets = {
            "components": {
                "path/to/module1": ["components/**/*parallel*.yaml"],
                "path/to/module2": ["components/**/*command*.yaml"],
            }
        }
        with tempfile.TemporaryDirectory() as temp_dir, _change_working_dir(temp_dir):
            with open("assets.yaml", "w") as f:
                yaml.dump(assets, f)
            generate_package(assets="assets.yaml")

            illegal_assets = [{"unsupported": {}}, {"components": []}, {"components": {"module1": "single_glob"}}]
            for asset in illegal_assets:
                with open("assets.yaml", "w") as f:
                    yaml.dump(asset, f)
                with pytest.raises(ValidationError):
                    generate_package(assets="assets.yaml")

            illegal_module_names = [
                {"components": {"MODULE": []}},
                {"components": {r"module1\sub": []}},
                {"components": {r"module1\\sub": []}},
                {"components": {"/module1": []}},
            ]
            for asset in illegal_module_names:
                with open("assets.yaml", "w") as f:
                    yaml.dump(asset, f)
                with pytest.raises(ValidationError):
                    generate_package(assets="assets.yaml")
            legal_module_names = [
                {"components": {"module1": []}},
                {"components": {"module1/module2": []}},
                {"components": {"module1/module2/": []}},
                {"components": {"module1/module2////": []}},
            ]
            for asset in legal_module_names:
                with open("assets.yaml", "w") as f:
                    yaml.dump(asset, f)
                generate_package(assets="assets.yaml")

    def test_gen_1p_local_component(self) -> None:
        test_root_dir = Path(__file__).parent.parent.parent.parent
        components = []
        with open("./tests/dsl/generate_package_expected_files/internal_component_files_to_generate.txt") as f:
            files = f.read().splitlines()
        for file in files:
            components.append(load_component(test_root_dir / file))

        expected_entity_file = "./tests/dsl/generate_package_expected_files/_internal_components_impl"
        expected_function_file = "./tests/dsl/generate_package_expected_files/_internal_components"
        components = sorted(components, key=lambda c: f"{c.name}:{c.version}")

        name_2_components, errors = get_unique_component_func_names(components)
        assert len(errors) == 0

        entity_generator = ComponentImplGenerator(name_2_components)
        assert_file_same(expected_entity_file, entity_generator.generate())

        func_generator = ComponentReferenceGenerator(name_2_components, module_dir=Path("./tests"))
        assert_file_same(expected_function_file, func_generator.generate())

    def test_gen_groups(self):
        pass

import yaml
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from marshmallow import ValidationError

from azure.ai.ml import load_component, Input, Output, MLClient
from azure.ai.ml.dsl._utils import _change_working_dir
from azure.ai.ml.entities import CommandComponent
from mldesigner import generate
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
from mldesigner._operations import ComponentOperations
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
            load_component(source=yaml_file),
            # another version
            load_component(source=yaml_file, params_override=[{"version": "0.0.2"}]),
            # another name with same sanitized name
            load_component(source=yaml_file, params_override=[{"name": "microsoftsamples_command_component__basic"}]),
            # another name with same sanitized name
            load_component(source=yaml_file, params_override=[{"name": "microsoftsamples_command_component___basic"}]),
            # another version with same sanitized version
            load_component(source=yaml_file, params_override=[{"version": "0.0_2"}]),
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
            load_component(source=yaml_file),
            load_component(source=yaml_file),
        ]
        _, errors = get_unique_component_func_names(components)
        error_msg = "Duplicate component microsoftsamples_command_component_basic:0.0.1 found. "
        assert len(errors) == 1
        assert error_msg in errors[0]

    def test_gen_local_component(self) -> None:
        yaml_file = "./tests/test_configs/components/input_types_component.yml"
        expected_entity_file = "./tests/dsl/generate_package_expected_files/single_command_component_entity"
        expected_function_file = "./tests/dsl/generate_package_expected_files/single_command_component_ref"
        component_entity = load_component(source=yaml_file)

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
            generate(source="assets.yaml")

            illegal_assets = [{"unsupported": {}}, {"components": []}, {"components": {"module1": "single_glob"}}]
            for asset in illegal_assets:
                with open("assets.yaml", "w") as f:
                    yaml.dump(asset, f)
                with pytest.raises(ValidationError):
                    generate(source="assets.yaml")

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
                    generate(source="assets.yaml")
            legal_module_names = [
                {"components": {"module1": []}},
                {"components": {"module1/module2": []}},
                {"components": {"module1/module2/": []}},
                {"components": {"module1/module2////": []}},
            ]
            for asset in legal_module_names:
                with open("assets.yaml", "w") as f:
                    yaml.dump(asset, f)
                generate(source="assets.yaml")

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

    def test_components_with_upper_inputs(self) -> None:
        yaml_file = "./tests/test_configs/components/helloworld_component_upper_inputs.yml"
        expected_entity_file = "./tests/dsl/generate_package_expected_files/helloworld_component_upper_inputs_entity"
        expected_function_file = "./tests/dsl/generate_package_expected_files/helloworld_component_upper_inputs_ref"

        # generate inputs should align with YAML file
        # we will make component function call case insensitive
        component_entity = load_component(source=yaml_file)
        entity_generator = SingleComponentEntityGenerator(component_entity=component_entity)
        assert_file_same(expected_entity_file, entity_generator.generate())

        fun_generator = SingleComponentReferenceGenerator(component_entity=component_entity, module_dir=Path("./tests"))
        assert_file_same(expected_function_file, fun_generator.generate())

    def test_parse_validate_asset_dict(self) -> None:
        asset_list = [
            "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name1/components/*",
            "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name2/components/",
            "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name3/components",
            "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name4/components/component1",
            "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name5/components/component2",
            "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name6/components/component3",
            "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name7/components/component*",
            "azureml://registries/registry1/components/*",
            "azureml://registries/registry2/components/",
            "azureml://registries/registry3/components",
            "azureml://registries/registry4/components/component1",
            "azureml://registries/registry5/components/component2",
            "azureml://registries/registry6/components/component3",
            "azureml://registries/registry7/components/component*",
        ]
        asset_dict = AssetsUtil.load_from_list(asset_list)
        # test validate/filter assets

        class FakeComponent(CommandComponent):
            def __init__(self, name: str):
                self.name = name

        component1 = FakeComponent("component1")
        component2 = FakeComponent("component2")
        components = [component1, component2]
        mock_result = (components, [])
        with patch.object(ComponentOperations, "list_component_versions", return_value=mock_result):
            with patch.object(MLClient, "from_config"):
                assets, pattern_to_components, warnings = AssetsUtil.parse_validate_asset_dict(asset_dict)
                assert assets == {
                    "registry1": ["azureml://registries/registry1/components/*"],
                    "registry2": ["azureml://registries/registry2/components/"],
                    "registry3": ["azureml://registries/registry3/components"],
                    "registry4": ["azureml://registries/registry4/components/component1"],
                    "registry5": ["azureml://registries/registry5/components/component2"],
                    "registry6": [],
                    "registry7": ["azureml://registries/registry7/components/component*"],
                    "ws_name1": [
                        "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name1/components/*"
                    ],
                    "ws_name2": ["azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name2/components/"],
                    "ws_name3": ["azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name3/components"],
                    "ws_name4": [
                        "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name4/components/component1"
                    ],
                    "ws_name5": [
                        "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name5/components/component2"
                    ],
                    "ws_name6": [],
                    "ws_name7": [
                        "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name7/components/component*"
                    ],
                }
                assert pattern_to_components == {
                    "azureml://registries/registry1/components/*": components,
                    "azureml://registries/registry2/components/": components,
                    "azureml://registries/registry3/components": components,
                    "azureml://registries/registry4/components/component1": [component1],
                    "azureml://registries/registry5/components/component2": [component2],
                    "azureml://registries/registry7/components/component*": components,
                    "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name1/components/*": components,
                    "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name2/components/": components,
                    "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name3/components": components,
                    "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name4/components/component1": [
                        component1
                    ],
                    "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name5/components/component2": [
                        component2
                    ],
                    "azureml://subscriptions/sub_id/resourcegroups/rg_id/workspaces/ws_name7/components/component*": [
                        component1,
                        component2,
                    ],
                }
                assert len(warnings) == 0

    def test_components_with_invalid_io_names(self) -> None:
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"
        expected_entity_file = "./tests/dsl/generate_package_expected_files/helloworld_component_enums"
        expected_function_file = "./tests/dsl/generate_package_expected_files/helloworld_component_enums_func"

        # enum options should have legal variable name
        component_entity = load_component(
            path=yaml_file,
            params_override=[
                {
                    "inputs": {"enum_param": {"type": "string", "enum": ["1", "2", "3"], "default": "1"}},
                }
            ],
        )
        entity_generator = SingleComponentEntityGenerator(component_entity=component_entity)
        assert_file_same(expected_entity_file, entity_generator.generate())

        fun_generator = SingleComponentReferenceGenerator(component_entity=component_entity, module_dir=Path("./tests"))
        assert_file_same(expected_function_file, fun_generator.generate())

    def test_generate_cli_commands(self):
        from mldesigner._cli.mldesigner_commands import _entry

        with patch("mldesigner._generate._generate_package_impl._generate") as patched_obj:
            _entry(["generate", "--source", "source1"])
            patched_obj.assert_called_with(source=["source1"], package_name=None, force_regenerate=False)

            _entry(["generate", "--source", "source1", "source2", "--package-name", "a-b-c"])
            patched_obj.assert_called_with(source=["source1", "source2"], package_name="a-b-c", force_regenerate=False)

            _entry(["generate", "--source", "source1", "source2", "--package-name", "a-b-c", "--force"])
            patched_obj.assert_called_with(source=["source1", "source2"], package_name="a-b-c", force_regenerate=True)

    def test_gen_groups(self):
        pass

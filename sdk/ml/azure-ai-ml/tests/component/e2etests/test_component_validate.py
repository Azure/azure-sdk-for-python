from pathlib import Path
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient, load_component
from azure.ai.ml.entities import CommandComponent

from .._util import _COMPONENT_TIMEOUT_SECOND


@pytest.mark.e2etest
@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.usefixtures(
    "recorded_test",
    "mock_code_hash",
    "mock_asset_name",
    "mock_component_hash",
    "enable_environment_id_arm_expansion",
)
@pytest.mark.pipeline_test
class TestComponentValidate(AzureRecordedTestCase):
    def test_component_validate_via_schema(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_path = "./tests/test_configs/components/helloworld_component.yml"
        component: CommandComponent = load_component(source=component_path)
        component.name = None
        component.command += " & echo ${{inputs.non_existent}} & echo ${{outputs.non_existent}}"
        validation_result = client.components.validate(component, skip_remote_validation=False)
        assert validation_result.passed is False
        assert validation_result.error_messages == {
            "name": "Missing data for required field.",
            "command": "Invalid data binding expression: inputs.non_existent, outputs.non_existent",
        }

    @pytest.mark.skip(reason="Enable this test after server-side is ready.")
    def test_component_remote_validate_basic(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_path = "./tests/test_configs/components/helloworld_component.yml"
        # we must use a valid component yaml here, or validation error will be raised in load_component
        component: CommandComponent = load_component(source=component_path)
        component.name = "DPv2_register_flow_test"
        validation_result = client.components.validate(component)
        assert validation_result.passed is False
        assert validation_result._to_dict() == {
            "errors": [
                {
                    "location": f"{Path(component_path).absolute()}#line 3",
                    "message": 'at #/name; "DPv2_register_flow_test" does not match the expected pattern. Component name should only contain lower letter, number, underscore and start with a lower letter.',
                    "path": "name",
                    "value": "DPv2_register_flow_test",
                },
            ],
            "result": "Failed",
        }

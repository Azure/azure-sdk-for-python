import pytest
from marshmallow.exceptions import ValidationError
from marshmallow.schema import Schema

from azure.ai.ml._schema import NestedField, UnionField
from azure.ai.ml._schema._deployment.online.scale_settings_schema import (
    DefaultScaleSettingsSchema,
    TargetUtilizationScaleSettingsSchema,
)
from azure.ai.ml._scope_dependent_operations import OperationScope


class DummySchema(Schema):
    scale_settings = UnionField(
        [NestedField(DefaultScaleSettingsSchema), NestedField(TargetUtilizationScaleSettingsSchema)]
    )


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestScaleSettingsSchema:
    def test_default_scale_settings(self, mock_workspace_scope: OperationScope) -> None:
        schema = DummySchema()
        input_data = {"scale_settings": {"type": "default"}}
        schema.load(input_data)

    def test_target_utilization_scale_settings(self, mock_workspace_scope: OperationScope) -> None:
        schema = DummySchema()
        input_data = {"scale_settings": {"type": "target_utilization"}}
        schema.load(input_data)

    def test_scale_type_missing(self, mock_workspace_scope: OperationScope) -> None:
        schema = DummySchema()
        input_data = {"scale_settings": {}}
        with pytest.raises(ValidationError):
            schema.load(input_data)

    def test_invalid_scale_type(self, mock_workspace_scope: OperationScope) -> None:
        schema = DummySchema()
        input_data = {"scale_settings": {"type": "xxrei"}}
        with pytest.raises(ValidationError):
            schema.load(input_data)

    def test_invalid_fields(self, mock_workspace_scope: OperationScope) -> None:
        schema = DummySchema()
        input_data = {"scale_settings": {"type": "AuTo", "min_instances": 2, "max_instances": 1}}
        with pytest.raises(ValidationError):
            schema.load(input_data)

    def test_manual_missing_instance_count(self, mock_workspace_scope: OperationScope) -> None:
        schema = DummySchema()
        input_data = {"scale_settings": {"type": "Manual", "min_instances": 1, "max_instances": 2}}
        with pytest.raises(ValidationError):
            schema.load(input_data)

    def test_manual_normal_pass(self, mock_workspace_scope: OperationScope) -> None:
        schema = DummySchema()
        input_data = {
            "scale_settings": {
                "type": "target_utilization",
                "min_instances": 1,
                "max_instances": 2,
                "polling_interval": 1,
                "target_utilization_percentage": 80,
            }
        }
        data = schema.load(input_data)
        assert data["scale_settings"].type == "target_utilization"

import pytest
from marshmallow import ValidationError

from azure.ai.ml.entities import PipelineJobSettings
from azure.ai.ml.entities._validation import ValidationResultBuilder


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestValidation:
    def test_from_validation_error_dict(self) -> None:
        validation_error = ValidationError(
            field="_schema",
            message={
                "jobs": {
                    "hello_world_component": {
                        "value": {"component": {"environment": ["Missing data for required field."]}}
                    }
                }
            },
        )
        result = ValidationResultBuilder.from_validation_error(validation_error)
        assert result._to_dict() == {
            "errors": [
                {
                    "message": "Missing data for required field.",
                    "path": "jobs.hello_world_component.component.environment",
                    "value": None,
                }
            ],
            "result": "Failed",
        }

    def test_from_validation_error_2(self):
        validation_error = ValidationError(
            field="_schema",
            message={
                "outputs": {
                    "primitive_is_control": {
                        "value": {
                            "is_control": ["Unknown field."],
                        }
                    }
                }
            },
        )
        result = ValidationResultBuilder.from_validation_error(validation_error, error_on_unknown_field=True)
        assert result._to_dict() == {
            "errors": [
                {
                    "message": "Unknown field.",
                    "path": "outputs.primitive_is_control.is_control",
                    "value": None,
                },
            ],
            "result": "Failed",
        }

        result = ValidationResultBuilder.from_validation_error(validation_error)
        assert result._to_dict() == {
            "warnings": [
                {
                    "message": "Unknown field.",
                    "path": "outputs.primitive_is_control.is_control",
                    "value": None,
                },
            ],
            "result": "Succeeded",
        }

    def test_from_validation_error_union_field(self):
        validation_error = ValidationError(
            field="_schema",
            message={
                "code": [
                    {"_schema": ["Not a valid string."]},
                    {"_schema": ["Not a valid URL."]},
                    {"_schema": ["Not a valid string."]},
                ]
            },
        )
        result = ValidationResultBuilder.from_validation_error(validation_error)
        assert result._to_dict() == {
            "errors": [
                {"message": "Not a valid string.; Not a valid URL.; Not a valid string.", "path": "code", "value": None}
            ],
            "result": "Failed",
        }

    def test_from_validation_error_unknown_field(self):
        validation_error = ValidationError(
            field="_schema",
            message={"jeff_special_option": ["Unknown field."]},
        )
        result = ValidationResultBuilder.from_validation_error(validation_error)
        assert result._to_dict() == {
            "warnings": [{"message": "Unknown field.", "path": "jeff_special_option", "value": None}],
            "result": "Succeeded",
        }

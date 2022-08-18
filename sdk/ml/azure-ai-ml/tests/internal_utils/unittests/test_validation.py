import pytest
from marshmallow import ValidationError

from azure.ai.ml.entities import PipelineJobSettings
from azure.ai.ml.entities._validation import _ValidationResultBuilder


@pytest.mark.unittest
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
        result = _ValidationResultBuilder.from_validation_error(validation_error)
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
        result = _ValidationResultBuilder.from_validation_error(validation_error)
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
        result = _ValidationResultBuilder.from_validation_error(validation_error)
        assert result._to_dict() == {
            "warnings": [{"message": "Unknown field.", "path": "jeff_special_option", "value": None}],
            "result": "Succeeded",
        }

import pytest
import copy
from azure.ai.evaluation._evaluate._evaluate_aoai import _combine_item_schemas


@pytest.fixture
def default_data_source_config():
    return {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["id", "text"],
        },
        "include_sample_schema": False,
    }


class TestCombineItemSchemas:
    """Unit tests for _combine_item_schemas"""

    def test_combine_item_schemas_success(self, default_data_source_config):
        data_source_config = copy.deepcopy(default_data_source_config)
        kwargs = {
            "item_schema": {
                "properties": {
                    "metadata": {"type": "object"},
                    "timestamp": {"type": "string", "format": "date-time"},
                },
                "required": ["metadata"],
            }
        }
        _combine_item_schemas(data_source_config, kwargs)

        expected_properties = {
            "id": {"type": "string"},
            "text": {"type": "string"},
            "metadata": {"type": "object"},
            "timestamp": {"type": "string", "format": "date-time"},
        }
        expected_required = ["id", "text", "metadata"]
        assert data_source_config["item_schema"]["properties"] == expected_properties
        assert data_source_config["item_schema"]["required"] == expected_required

    def test_combine_item_schemas_without_item_schema(self, default_data_source_config):
        data_source_config = copy.deepcopy(default_data_source_config)

        expected_properties = {
            "id": {"type": "string"},
            "text": {"type": "string"},
        }
        expected_required = ["id", "text"]

        # No "item_schema" in kwargs
        kwargs = {}
        _combine_item_schemas(data_source_config, kwargs)
        assert data_source_config["item_schema"]["properties"] == expected_properties
        assert data_source_config["item_schema"]["required"] == expected_required

        # "item_schema" as None in kwargs
        kwargs = {"item_schema": None}
        _combine_item_schemas(data_source_config, kwargs)
        assert data_source_config["item_schema"]["properties"] == expected_properties
        assert data_source_config["item_schema"]["required"] == expected_required

        # "item_schema" is a wrong value in kwargs
        kwargs = {"item_schema": 12345}
        _combine_item_schemas(data_source_config, kwargs)
        assert data_source_config["item_schema"]["properties"] == expected_properties
        assert data_source_config["item_schema"]["required"] == expected_required

        # "item_schema" without "properties" in kwargs
        kwargs = {"item_schema": {}}
        _combine_item_schemas(data_source_config, kwargs)
        assert data_source_config["item_schema"]["properties"] == expected_properties
        assert data_source_config["item_schema"]["required"] == expected_required

    def test_combine_item_schemas_with_empty_external_properties(self, default_data_source_config):
        data_source_config = copy.deepcopy(default_data_source_config)
        kwargs = {
            "item_schema": {
                "properties": {},
                "required": [],
            }
        }
        _combine_item_schemas(data_source_config, kwargs)

        expected_properties = {
            "id": {"type": "string"},
            "text": {"type": "string"},
        }
        expected_required = ["id", "text"]

        assert data_source_config["item_schema"]["properties"] == expected_properties
        assert data_source_config["item_schema"]["required"] == expected_required

    def test_combine_item_schemas_with_external_properties_without_required(self, default_data_source_config):
        data_source_config = copy.deepcopy(default_data_source_config)
        kwargs = {
            "item_schema": {
                "properties": {
                    "metadata": {"type": "object"},
                    "timestamp": {"type": "string", "format": "date-time"},
                },
            }
        }
        _combine_item_schemas(data_source_config, kwargs)

        expected_properties = {
            "id": {"type": "string"},
            "text": {"type": "string"},
            "metadata": {"type": "object"},
            "timestamp": {"type": "string", "format": "date-time"},
        }
        expected_required = ["id", "text"]

        assert data_source_config["item_schema"]["properties"] == expected_properties
        assert data_source_config["item_schema"]["required"] == expected_required

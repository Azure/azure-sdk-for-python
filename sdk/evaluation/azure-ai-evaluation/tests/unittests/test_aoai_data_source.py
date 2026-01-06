# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import pandas as pd
import os
import pathlib
from typing import Dict, Any

from azure.ai.evaluation._evaluate._evaluate_aoai import (
    _generate_data_source_config,
    _get_data_source,
    _build_schema_tree_from_paths,
    WRAPPER_KEY,
)


def _get_file(name):
    """Get the file from the unittest data folder."""
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, name)


@pytest.fixture
def flat_test_data():
    """Fixture for flat structure test data."""
    return pd.DataFrame(
        [
            {
                "query": "What is the capital of France?",
                "response": "Paris is the capital of France.",
                "ground_truth": "Paris",
            },
            {"query": "What is 2+2?", "response": "The answer is 4.", "ground_truth": "4"},
            {
                "query": "Who wrote Hamlet?",
                "response": "William Shakespeare wrote Hamlet.",
                "ground_truth": "Shakespeare",
            },
        ]
    )


@pytest.fixture
def nested_test_data():
    """Fixture for nested structure test data."""
    return pd.DataFrame(
        [
            {
                "item.query": "What security policies exist?",
                "item.context.company.policy.security.passwords.rotation_days": "90",
                "item.context.company.policy.security.network.vpn.required": "true",
                "item.response": "Password rotation is required every 90 days.",
                "item.ground_truth": "Security policies include password rotation.",
            },
            {
                "item.query": "What are the database settings?",
                "item.context.company.infrastructure.database.host": "db.example.com",
                "item.context.company.infrastructure.database.port": "5432",
                "item.response": "The database is PostgreSQL.",
                "item.ground_truth": "PostgreSQL database",
            },
        ]
    )


@pytest.fixture
def flat_test_data_file():
    """Fixture for flat test data file path."""
    return _get_file("flat_test_data.jsonl")


@pytest.fixture
def nested_test_data_file():
    """Fixture for nested test data file path."""
    return _get_file("nested_test_data.jsonl")


@pytest.fixture
def wrapped_flat_test_data_file():
    """Fixture for wrapped flat test data file path."""
    return _get_file("wrapped_flat_test_data.jsonl")


@pytest.fixture
def nested_item_keyword_data():
    """Fixture for data that already contains an 'item' wrapper column."""
    return pd.read_json(_get_file("nested_item_keyword.jsonl"), lines=True)

@pytest.fixture
def nested_item_sample_keyword_data():
    """Fixture for data that already contains an 'item' wrapper column."""
    return pd.read_json(_get_file("nested_item_sample_keyword.jsonl"), lines=True)


@pytest.fixture
def flat_sample_output_data():
    """Fixture for flat data that includes dotted sample metadata (e.g. sample.output_text)."""
    return pd.read_json(_get_file("flat_sample_output.jsonl"), lines=True)


@pytest.mark.unittest
class TestBuildSchemaTreeFromPaths:
    """Test suite for the _build_schema_tree_from_paths helper function."""

    def test_single_level_paths(self):
        """Test building schema with single-level paths."""
        paths = ["query", "response", "ground_truth"]
        schema = _build_schema_tree_from_paths(paths, force_leaf_type="string")

        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert set(schema["properties"].keys()) == {"query", "response", "ground_truth"}
        assert all(prop["type"] == "string" for prop in schema["properties"].values())

    def test_nested_paths(self):
        """Test building schema with nested paths."""
        paths = [
            "context.company.policy.security.passwords.rotation_days",
            "context.company.policy.security.network.vpn.required",
            "query",
        ]
        schema = _build_schema_tree_from_paths(paths, force_leaf_type="string")

        assert schema["type"] == "object"
        assert "context" in schema["properties"]
        assert schema["properties"]["context"]["type"] == "object"

        # Navigate nested structure
        company = schema["properties"]["context"]["properties"]["company"]
        assert company["type"] == "object"

        policy = company["properties"]["policy"]
        assert policy["type"] == "object"

        security = policy["properties"]["security"]
        assert security["type"] == "object"

        # Check leaf nodes
        passwords = security["properties"]["passwords"]
        assert passwords["properties"]["rotation_days"]["type"] == "string"

        network = security["properties"]["network"]
        assert network["properties"]["vpn"]["properties"]["required"]["type"] == "string"

        # Check required arrays exist at each level
        assert "required" in schema
        assert "required" in schema["properties"]["context"]

    def test_empty_paths(self):
        """Test building schema with empty paths list."""
        paths = []
        schema = _build_schema_tree_from_paths(paths, force_leaf_type="object")

        assert schema["type"] == "object"

    def test_mixed_depth_paths(self):
        """Test building schema with paths of different depths."""
        paths = ["simple_field", "nested.field.deep", "nested.field.shallow", "another.path"]
        schema = _build_schema_tree_from_paths(paths, force_leaf_type="string")

        assert "simple_field" in schema["properties"]
        assert schema["properties"]["simple_field"]["type"] == "string"

        assert "nested" in schema["properties"]
        nested = schema["properties"]["nested"]
        assert nested["type"] == "object"
        assert "field" in nested["properties"]


@pytest.mark.unittest
class TestGenerateDataSourceConfig:
    """Test suite for the _generate_data_source_config function."""

    def test_flat_column_mapping(self, flat_test_data):
        """Test generating data source config with flat column mappings."""
        column_mapping = {
            "query": "${data.query}",
            "response": "${data.response}",
            "ground_truth": "${data.ground_truth}",
        }

        config = _generate_data_source_config(flat_test_data, column_mapping)

        assert config["type"] == "custom"
        assert "item_schema" in config
        assert config["item_schema"]["type"] == "object"

        properties = config["item_schema"]["properties"]
        assert "query" in properties
        assert "response" in properties
        assert "ground_truth" in properties

        # All should be strings in flat mode
        assert properties["query"]["type"] == "string"
        assert properties["response"]["type"] == "string"
        assert properties["ground_truth"]["type"] == "string"

    def test_nested_column_mapping_with_wrapper(self, nested_test_data):
        """Test generating data source config with nested paths under wrapper."""
        column_mapping = {
            "query": "${data.item.query}",
            "passwords_rotation": "${data.item.context.company.policy.security.passwords.rotation_days}",
            "vpn_required": "${data.item.context.company.policy.security.network.vpn.required}",
            "response": "${data.item.response}",
        }

        config = _generate_data_source_config(nested_test_data, column_mapping)

        assert config["type"] == "custom"
        assert "item_schema" in config
        schema = config["item_schema"]

        # Should be nested object since paths contain dots
        assert schema["type"] == "object"

        # The wrapper should be stripped, so we should see inner structure
        assert "query" in schema["properties"]
        assert "response" in schema["properties"]
        assert "context" in schema["properties"]

        # Verify nested structure
        context = schema["properties"]["context"]
        assert context["type"] == "object"
        assert "company" in context["properties"]

    def test_nested_column_mapping_without_wrapper(self, nested_test_data):
        """Test generating data source config with nested paths not using standard wrapper."""
        column_mapping = {
            "query": "${data.custom.query}",
            "field": "${data.custom.nested.field}",
        }

        config = _generate_data_source_config(nested_test_data, column_mapping)

        assert config["type"] == "custom"
        assert "item_schema" in config
        schema = config["item_schema"]

        # Should be nested
        assert schema["type"] == "object"
        # Without wrapper stripping, should see 'custom' at top level
        assert "custom" in schema["properties"]

    def test_mixed_data_and_run_outputs(self, flat_test_data):
        """Test column mapping with both data and run.outputs references."""
        column_mapping = {
            "query": "${data.query}",
            "response": "${run.outputs.response}",
            "ground_truth": "${data.ground_truth}",
        }

        config = _generate_data_source_config(flat_test_data, column_mapping)

        # Only data.* paths should be in schema
        properties = config["item_schema"]["properties"]
        assert "query" in properties
        assert "ground_truth" in properties
        # run.outputs.response shouldn't create a schema property directly

    def test_empty_column_mapping(self, flat_test_data):
        """Test with empty column mapping."""
        column_mapping = {}

        config = _generate_data_source_config(flat_test_data, column_mapping)

        # Should return flat schema with no properties
        assert config["type"] == "custom"
        assert config["item_schema"]["type"] == "object"
        assert config["item_schema"]["properties"] == {}

    def test_no_data_references(self, flat_test_data):
        """Test column mapping with no ${data.*} references."""
        column_mapping = {"response": "${run.outputs.response}", "result": "${run.outputs.result}"}

        config = _generate_data_source_config(flat_test_data, column_mapping)

        # Should return flat schema since no data paths referenced
        assert config["type"] == "custom"
        assert "response" in config["item_schema"]["properties"]
        assert "result" in config["item_schema"]["properties"]

    def test_single_nested_path(self, flat_test_data):
        """Test with a single nested path to ensure nested mode activates."""
        column_mapping = {"nested_field": "${data.item.context.field}"}

        config = _generate_data_source_config(flat_test_data, column_mapping)

        # Should generate nested schema
        assert config["type"] == "custom"
        schema = config["item_schema"]
        assert schema["type"] == "object"
        # After wrapper stripping, should see context
        assert "context" in schema["properties"]


@pytest.mark.unittest
class TestGetDataSource:
    """Test suite for the _get_data_source function."""

    def test_flat_data_source_generation(self, flat_test_data):
        """Test generating data source from flat data."""
        column_mapping = {
            "query": "${data.query}",
            "response": "${data.response}",
            "ground_truth": "${data.ground_truth}",
        }

        data_source = _get_data_source(flat_test_data, column_mapping)

        assert data_source["type"] == "jsonl"
        assert "source" in data_source
        assert data_source["source"]["type"] == "file_content"

        content = data_source["source"]["content"]
        assert len(content) == 3

        # Each item should be wrapped
        for item in content:
            assert WRAPPER_KEY in item
            assert "query" in item[WRAPPER_KEY]
            assert "response" in item[WRAPPER_KEY]
            assert "ground_truth" in item[WRAPPER_KEY]

    def test_nested_data_source_generation(self, nested_test_data):
        """Test generating data source from nested data."""
        column_mapping = {
            "query": "${data.item.query}",
            "rotation_days": "${data.item.context.company.policy.security.passwords.rotation_days}",
            "vpn_required": "${data.item.context.company.policy.security.network.vpn.required}",
            "response": "${data.item.response}",
        }

        data_source = _get_data_source(nested_test_data, column_mapping)

        assert data_source["type"] == "jsonl"
        content = data_source["source"]["content"]
        assert len(content) == 2

        # Verify nested structure is built correctly
        first_item = content[0][WRAPPER_KEY]
        assert "query" in first_item
        assert "context" in first_item
        assert "company" in first_item["context"]
        assert "policy" in first_item["context"]["company"]

        # Check leaf values
        passwords = first_item["context"]["company"]["policy"]["security"]["passwords"]
        assert passwords["rotation_days"] == "90"

        vpn = first_item["context"]["company"]["policy"]["security"]["network"]["vpn"]
        assert vpn["required"] == "true"

    def test_data_source_with_run_outputs(self, flat_test_data):
        """Test data source generation with run.outputs mappings."""
        # Add __outputs column to simulate target function output
        flat_test_data["__outputs.model_response"] = [
            "Generated response 1",
            "Generated response 2",
            "Generated response 3",
        ]

        column_mapping = {
            "query": "${data.query}",
            "response": "${run.outputs.model_response}",
            "ground_truth": "${data.ground_truth}",
        }

        data_source = _get_data_source(flat_test_data, column_mapping)

        content = data_source["source"]["content"]

        # run.outputs should be mapped with just leaf name
        for i, item in enumerate(content):
            assert "model_response" in item[WRAPPER_KEY]
            assert item[WRAPPER_KEY]["model_response"] == f"Generated response {i+1}"

    def test_data_source_with_unmapped_columns(self, flat_test_data):
        """Test that unmapped columns are included in output."""
        # Add extra column not in mapping
        flat_test_data["extra_field"] = ["extra1", "extra2", "extra3"]

        column_mapping = {"query": "${data.query}", "response": "${data.response}"}

        data_source = _get_data_source(flat_test_data, column_mapping)

        content = data_source["source"]["content"]

        # Unmapped columns should appear directly in item
        for i, item in enumerate(content):
            assert "extra_field" in item[WRAPPER_KEY]
            assert "ground_truth" in item[WRAPPER_KEY]  # Also unmapped

    def test_data_source_with_none_values(self, flat_test_data):
        """Test data source generation handles None values correctly."""
        flat_test_data.loc[1, "response"] = None

        column_mapping = {
            "query": "${data.query}",
            "response": "${data.response}",
            "ground_truth": "${data.ground_truth}",
        }

        data_source = _get_data_source(flat_test_data, column_mapping)

        content = data_source["source"]["content"]

        # None should be converted to empty string
        assert content[1][WRAPPER_KEY]["response"] == ""

    def test_data_source_with_item_column_and_nested_values(self, nested_item_keyword_data):
        """Ensure rows that already have an 'item' column keep nested dicts intact."""

        column_mapping = {
            "query": "${data.item.query}",
            "response": "${data.item.response}",
            "test_string": "${data.item.test.test_string}",
            "output_text": "${data.sample.output_text}",
            "output_items": "${data.sample.output_items}"
        }

        data_source = _get_data_source(nested_item_keyword_data, column_mapping)
        content = data_source["source"]["content"]

        assert len(content) == len(nested_item_keyword_data)
        first_row = content[0]
        assert WRAPPER_KEY in first_row

        item_payload = first_row[WRAPPER_KEY]
        assert item_payload["query"] == "what is the weather today"
        assert item_payload["response"] == "It is sunny out"
        assert item_payload["test"]["test_string"] == ("baking cakes is a fun pass time when you are bored!")
        # Ensure we did not accidentally nest another 'item' key inside the wrapper
        assert "item" not in item_payload
        assert item_payload["sample"]["output_text"] == "someoutput"
        assert item_payload["sample"]["output_items"] == "['item1', 'item2']"

    def test_data_source_with_item_sample_column_and_nested_values(self, nested_item_sample_keyword_data):
        """Ensure rows that already have an 'item' column keep nested dicts intact."""

        column_mapping = {
            "query": "${data.item.query}",
            "response": "${data.item.response}",
            "test_string": "${data.item.test.test_string}",
            "output_text": "${data.sample.output_text}",
            "output_items": "${data.sample.output_items}"
        }

        data_source = _get_data_source(nested_item_sample_keyword_data, column_mapping)
        content = data_source["source"]["content"]

        assert len(content) == len(nested_item_sample_keyword_data)
        first_row = content[0]
        assert WRAPPER_KEY in first_row

        item_payload = first_row[WRAPPER_KEY]
        assert item_payload["query"] == "what is the weather today"
        assert item_payload["response"] == "It is sunny out"
        assert item_payload["test"]["test_string"] == ("baking cakes is a fun pass time when you are bored!")
        # Ensure we did not accidentally nest another 'item' key inside the wrapper
        assert "item" not in item_payload
        assert item_payload["sample"]["output_text"] == "someoutput"
        assert item_payload["sample"]["output_items"] == "['item1', 'item2']"

    def test_data_source_with_sample_output_metadata(self, flat_sample_output_data):
        """Ensure flat rows that include dotted sample metadata remain accessible."""

        column_mapping = {
            "query": "${data.item.query}",
            "response": "${data.item.response}",
            "test_string": "${data.item.test.test_string}"
        }

        data_source = _get_data_source(flat_sample_output_data, column_mapping)
        content = data_source["source"]["content"]

        assert len(content) == len(flat_sample_output_data)
        row = content[0][WRAPPER_KEY]

        assert row["query"] == "how can i help someone be a good person"
        assert row["test"]["test_string"] == "baking cakes is fun!"
        # sample.output_text should follow the row through normalization without being stringified
        assert row["sample.output_text"] == "someoutput"
        assert row["sample.output_items"] == "['item1', 'item2']"

    def test_data_source_with_numeric_values(self, flat_test_data):
        """Test data source generation converts numeric values to strings."""
        flat_test_data["score"] = [95, 87, 92]
        flat_test_data["confidence"] = [0.95, 0.87, 0.92]

        column_mapping = {"query": "${data.query}", "score": "${data.score}", "confidence": "${data.confidence}"}

        data_source = _get_data_source(flat_test_data, column_mapping)

        content = data_source["source"]["content"]

        # Numeric values should be converted to strings
        assert content[0][WRAPPER_KEY]["score"] == "95"
        assert content[0][WRAPPER_KEY]["confidence"] == "0.95"
        assert isinstance(content[0][WRAPPER_KEY]["score"], str)
        assert isinstance(content[0][WRAPPER_KEY]["confidence"], str)

    def test_empty_dataframe(self):
        """Test data source generation with empty dataframe."""
        empty_df = pd.DataFrame()
        column_mapping = {"query": "${data.query}"}

        data_source = _get_data_source(empty_df, column_mapping)

        assert data_source["type"] == "jsonl"
        assert len(data_source["source"]["content"]) == 0

    def test_complex_nested_structure(self):
        """Test with complex multi-level nested structure."""
        df = pd.DataFrame(
            [
                {
                    "item.a.b.c.d": "deep_value",
                    "item.a.b.x": "mid_value",
                    "item.a.y": "shallow_value",
                    "item.z": "top_value",
                }
            ]
        )

        column_mapping = {
            "deep": "${data.item.a.b.c.d}",
            "mid": "${data.item.a.b.x}",
            "shallow": "${data.item.a.y}",
            "top": "${data.item.z}",
        }

        data_source = _get_data_source(df, column_mapping)

        content = data_source["source"]["content"]
        item = content[0][WRAPPER_KEY]

        # Verify nested structure
        assert item["a"]["b"]["c"]["d"] == "deep_value"
        assert item["a"]["b"]["x"] == "mid_value"
        assert item["a"]["y"] == "shallow_value"
        assert item["z"] == "top_value"

    def test_data_source_preserves_row_order(self, flat_test_data):
        """Test that data source preserves the order of rows."""
        column_mapping = {"query": "${data.query}", "response": "${data.response}"}

        data_source = _get_data_source(flat_test_data, column_mapping)
        content = data_source["source"]["content"]

        # Verify order matches input
        assert content[0][WRAPPER_KEY]["query"] == flat_test_data.iloc[0]["query"]
        assert content[1][WRAPPER_KEY]["query"] == flat_test_data.iloc[1]["query"]
        assert content[2][WRAPPER_KEY]["query"] == flat_test_data.iloc[2]["query"]


@pytest.mark.unittest
class TestDataSourceConfigIntegration:
    """Integration tests for schema and data source generation working together."""

    def test_flat_schema_and_data_alignment(self, flat_test_data):
        """Test that schema and data are aligned for flat structure."""
        column_mapping = {
            "query": "${data.query}",
            "response": "${data.response}",
            "ground_truth": "${data.ground_truth}",
        }

        config = _generate_data_source_config(flat_test_data, column_mapping)
        data_source = _get_data_source(flat_test_data, column_mapping)

        schema_props = config["item_schema"]["properties"]
        data_item = data_source["source"]["content"][0][WRAPPER_KEY]

        # All schema properties should exist in data
        for prop_name in schema_props.keys():
            assert prop_name in data_item

    def test_nested_schema_and_data_alignment(self, nested_test_data):
        """Test that schema and data are aligned for nested structure."""
        column_mapping = {
            "query": "${data.item.query}",
            "rotation_days": "${data.item.context.company.policy.security.passwords.rotation_days}",
            "response": "${data.item.response}",
        }

        config = _generate_data_source_config(nested_test_data, column_mapping)
        data_source = _get_data_source(nested_test_data, column_mapping)

        # Both should handle nested structure consistently
        assert config["item_schema"]["type"] == "object"
        assert WRAPPER_KEY in data_source["source"]["content"][0]

        # Verify nested paths exist in data
        item = data_source["source"]["content"][0][WRAPPER_KEY]
        assert "query" in item
        assert "context" in item
        assert "company" in item["context"]

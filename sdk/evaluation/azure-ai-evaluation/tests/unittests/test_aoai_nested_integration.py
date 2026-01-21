# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from azure.ai.evaluation._evaluate._evaluate_aoai import (
    _generate_data_source_config,
    _get_data_source,
    _begin_eval_run,
    WRAPPER_KEY,
)


@pytest.mark.unittest
class TestAOAINestedDataIntegration:
    """Test suite for AOAI evaluation integration with nested data structures."""

    def test_aoai_eval_run_with_flat_data(self):
        """Test _begin_eval_run with flat data structure."""
        # Setup test data
        input_df = pd.DataFrame(
            [
                {"query": "What is AI?", "response": "AI is...", "ground_truth": "AI"},
                {"query": "What is ML?", "response": "ML is...", "ground_truth": "ML"},
            ]
        )

        column_mapping = {
            "query": "${data.query}",
            "response": "${data.response}",
            "ground_truth": "${data.ground_truth}",
        }

        # Mock the client
        mock_client = Mock()
        mock_run = Mock()
        mock_run.id = "test-run-123"
        mock_client.evals.runs.create.return_value = mock_run

        # Call the function
        run_id = _begin_eval_run(
            client=mock_client,
            eval_group_id="test-group-456",
            run_name="test-run",
            input_data_df=input_df,
            column_mapping=column_mapping,
        )

        # Verify the client was called
        assert run_id == "test-run-123"
        mock_client.evals.runs.create.assert_called_once()

        # Get the call arguments
        call_kwargs = mock_client.evals.runs.create.call_args[1]

        # Verify eval_id
        assert call_kwargs["eval_id"] == "test-group-456"
        assert call_kwargs["name"] == "test-run"

        # Verify data_source structure
        data_source = call_kwargs["data_source"]
        assert data_source["type"] == "jsonl"
        assert "source" in data_source
        assert data_source["source"]["type"] == "file_content"

        # Verify content
        content = data_source["source"]["content"]
        assert len(content) == 2

        # Each item should be wrapped
        for item in content:
            assert WRAPPER_KEY in item
            assert "query" in item[WRAPPER_KEY]
            assert "response" in item[WRAPPER_KEY]
            assert "ground_truth" in item[WRAPPER_KEY]

    def test_aoai_eval_run_with_nested_data(self):
        """Test _begin_eval_run with nested data structure."""
        # Setup nested test data
        input_df = pd.DataFrame(
            [
                {
                    "item.query": "Security question",
                    "item.context.company.policy.security.passwords.rotation_days": "90",
                    "item.context.company.policy.security.network.vpn.required": "true",
                    "item.response": "Password rotation is 90 days.",
                    "item.ground_truth": "90",
                }
            ]
        )

        column_mapping = {
            "query": "${data.item.query}",
            "rotation_days": "${data.item.context.company.policy.security.passwords.rotation_days}",
            "vpn_required": "${data.item.context.company.policy.security.network.vpn.required}",
            "response": "${data.item.response}",
            "ground_truth": "${data.item.ground_truth}",
        }

        # Mock the client
        mock_client = Mock()
        mock_run = Mock()
        mock_run.id = "nested-run-789"
        mock_client.evals.runs.create.return_value = mock_run

        # Call the function
        run_id = _begin_eval_run(
            client=mock_client,
            eval_group_id="nested-group-101",
            run_name="nested-test-run",
            input_data_df=input_df,
            column_mapping=column_mapping,
        )

        # Verify
        assert run_id == "nested-run-789"
        mock_client.evals.runs.create.assert_called_once()

        # Get the data source
        call_kwargs = mock_client.evals.runs.create.call_args[1]
        data_source = call_kwargs["data_source"]
        content = data_source["source"]["content"]

        # Verify nested structure was built
        assert len(content) == 1
        item_root = content[0][WRAPPER_KEY]

        # Check nested paths exist
        assert "query" in item_root
        assert "context" in item_root
        assert "company" in item_root["context"]
        assert "policy" in item_root["context"]["company"]
        assert "security" in item_root["context"]["company"]["policy"]
        assert "passwords" in item_root["context"]["company"]["policy"]["security"]
        assert (
            "rotation_days"
            in item_root["context"]["company"]["policy"]["security"]["passwords"]
        )
        assert (
            item_root["context"]["company"]["policy"]["security"]["passwords"][
                "rotation_days"
            ]
            == "90"
        )

    def test_data_source_config_matches_data_source_for_nested(self):
        """Test that schema config and data source align for nested structures."""
        input_df = pd.DataFrame(
            [
                {
                    "item.query": "Test query",
                    "item.context.field1": "value1",
                    "item.context.field2": "value2",
                    "item.response": "Test response",
                }
            ]
        )

        column_mapping = {
            "query": "${data.item.query}",
            "field1": "${data.item.context.field1}",
            "field2": "${data.item.context.field2}",
            "response": "${data.item.response}",
        }

        # Generate both config and data source
        config = _generate_data_source_config(input_df, column_mapping)
        data_source = _get_data_source(input_df, column_mapping)

        # Verify config structure
        assert config["type"] == "custom"
        schema = config["item_schema"]
        assert schema["type"] == "object"

        # Verify schema has nested structure (wrapper stripped)
        assert "query" in schema["properties"]
        assert "context" in schema["properties"]
        assert schema["properties"]["context"]["type"] == "object"

        # Verify data source structure matches
        content = data_source["source"]["content"]
        item_root = content[0][WRAPPER_KEY]

        # All schema properties should exist in data
        assert "query" in item_root
        assert "context" in item_root
        assert "field1" in item_root["context"]
        assert "field2" in item_root["context"]
        assert "response" in item_root

    def test_data_source_config_matches_data_source_for_flat(self):
        """Test that schema config and data source align for flat structures."""
        input_df = pd.DataFrame([{"query": "Test", "response": "Answer", "score": "5"}])

        column_mapping = {
            "query": "${data.query}",
            "response": "${data.response}",
            "score": "${data.score}",
        }

        # Generate both config and data source
        config = _generate_data_source_config(input_df, column_mapping)
        data_source = _get_data_source(input_df, column_mapping)

        # Verify flat config structure
        assert config["type"] == "custom"
        schema = config["item_schema"]
        assert schema["type"] == "object"

        # Flat mode: properties match mapping keys
        assert set(schema["properties"].keys()) == {"query", "response", "score"}

        # Verify data source
        content = data_source["source"]["content"]
        item_root = content[0][WRAPPER_KEY]

        # All properties should exist
        assert "query" in item_root
        assert "response" in item_root
        assert "score" in item_root

    def test_data_source_with_run_outputs_and_nested_data(self):
        """Test data source generation with both run outputs and nested data."""
        input_df = pd.DataFrame(
            [
                {
                    "item.query": "Test query",
                    "item.context.metadata.id": "123",
                    "__outputs.generated_response": "Generated text",
                }
            ]
        )

        column_mapping = {
            "query": "${data.item.query}",
            "metadata_id": "${data.item.context.metadata.id}",
            "response": "${run.outputs.generated_response}",
        }

        # Generate data source
        data_source = _get_data_source(input_df, column_mapping)

        # Verify structure
        content = data_source["source"]["content"]
        item_root = content[0][WRAPPER_KEY]

        # Nested data paths
        assert "query" in item_root
        assert "context" in item_root
        assert "metadata" in item_root["context"]
        assert item_root["context"]["metadata"]["id"] == "123"

        # Run outputs (just leaf name)
        assert "generated_response" in item_root
        assert item_root["generated_response"] == "Generated text"

    def test_complex_nested_structure_multiple_branches(self):
        """Test nested structure with multiple branches at same level."""
        input_df = pd.DataFrame(
            [
                {
                    "item.user.name": "Alice",
                    "item.user.email": "alice@example.com",
                    "item.system.version": "1.0",
                    "item.system.region": "us-east",
                    "item.query": "Test",
                }
            ]
        )

        column_mapping = {
            "name": "${data.item.user.name}",
            "email": "${data.item.user.email}",
            "version": "${data.item.system.version}",
            "region": "${data.item.system.region}",
            "query": "${data.item.query}",
        }

        # Generate config and data
        config = _generate_data_source_config(input_df, column_mapping)
        data_source = _get_data_source(input_df, column_mapping)

        # Verify schema has both branches
        schema = config["item_schema"]
        assert "user" in schema["properties"]
        assert "system" in schema["properties"]
        assert "query" in schema["properties"]

        # Verify data has both branches
        item_root = data_source["source"]["content"][0][WRAPPER_KEY]
        assert "user" in item_root
        assert "system" in item_root
        assert item_root["user"]["name"] == "Alice"
        assert item_root["user"]["email"] == "alice@example.com"
        assert item_root["system"]["version"] == "1.0"
        assert item_root["system"]["region"] == "us-east"

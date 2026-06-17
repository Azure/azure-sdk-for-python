# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for EndpointBasedEvaluatorDefinition model.

These tests do not contact any service. They validate serialization,
deserialization, and discriminator behavior for the endpoint evaluator model.
"""

import pytest

from azure.ai.projects.models import (
    EndpointBasedEvaluatorDefinition,
    EvaluatorDefinitionType,
    EvaluatorVersion,
    EvaluatorCategory,
    EvaluatorType,
)


class TestEndpointBasedEvaluatorDefinition:
    """Unit tests for EndpointBasedEvaluatorDefinition serialization and construction."""

    def test_create_with_connection_name(self):
        """Creating an endpoint evaluator definition sets the type discriminator."""
        definition = EndpointBasedEvaluatorDefinition(
            connection_name="my-connection",
        )
        assert definition.connection_name == "my-connection"
        assert definition.type == EvaluatorDefinitionType.ENDPOINT

    def test_create_with_all_fields(self):
        """All optional fields are correctly set."""
        definition = EndpointBasedEvaluatorDefinition(
            connection_name="my-connection",
            init_parameters={"type": "object", "properties": {"threshold": {"type": "number"}}},
            data_schema={"type": "object", "properties": {"query": {"type": "string"}}},
            metrics=None,
        )
        assert definition.connection_name == "my-connection"
        assert definition.init_parameters is not None
        assert "threshold" in definition.init_parameters["properties"]
        assert definition.data_schema is not None
        assert definition.metrics is None

    def test_create_from_dict(self):
        """Creating from a dictionary (JSON wire format) works correctly."""
        definition = EndpointBasedEvaluatorDefinition(
            {
                "type": "endpoint",
                "connection_name": "test-conn",
            }
        )
        assert definition.connection_name == "test-conn"
        assert definition.type == EvaluatorDefinitionType.ENDPOINT

    def test_type_is_endpoint_literal(self):
        """The type field is always 'endpoint' regardless of input."""
        definition = EndpointBasedEvaluatorDefinition(connection_name="x")
        assert definition.type == "endpoint"

    def test_evaluator_version_with_endpoint_definition(self):
        """EndpointBasedEvaluatorDefinition integrates with EvaluatorVersion model."""
        version = EvaluatorVersion(
            categories=[EvaluatorCategory.QUALITY],
            evaluator_type=EvaluatorType.CUSTOM,
            definition=EndpointBasedEvaluatorDefinition(
                connection_name="my-endpoint-connection",
            ),
            display_name="My Endpoint Evaluator",
            description="Evaluates using a custom endpoint",
        )
        assert version.definition.connection_name == "my-endpoint-connection"
        assert version.definition.type == EvaluatorDefinitionType.ENDPOINT
        assert version.evaluator_type == EvaluatorType.CUSTOM
        assert EvaluatorCategory.QUALITY in version.categories

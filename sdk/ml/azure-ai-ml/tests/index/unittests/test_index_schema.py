import io
import re
from typing import cast

import pytest
from marshmallow.exceptions import ValidationError

from azure.ai.ml import load_index
from azure.ai.ml.entities import Index

MOCK_STORAGE_PATH = (
    "azureml://subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/"
    + "rg/workspaces/ws/datastores/workspaceblobstore/paths/path/to/file"
)


@pytest.mark.unittest
class TestIndexSchema:
    def test_deserialize(self) -> None:
        """Validate that load_index can deserialize a YAML file."""
        yaml_file = io.StringIO(
            f"""
        name: "foo"
        version: "2"
        stage: "Development"
        description: "Hello World"
        tags: {{"tag1": "foo", "tag2": "bar"}}
        properties: {{"prop1": "foo", "prop2": "bar"}}
        path: {MOCK_STORAGE_PATH!r}
        """
        )

        index = load_index(source=yaml_file)

        assert isinstance(index, Index)

        assert index.name == "foo"
        assert index.version == "2"
        assert index.stage == "Development"
        assert index.description == "Hello World"
        assert index.tags == {"tag1": "foo", "tag2": "bar"}
        assert index.properties == {"prop1": "foo", "prop2": "bar"}
        assert index.path == MOCK_STORAGE_PATH
        assert index.id == None

    def test_missing_name(self) -> None:
        """Validate that load_index fails when no name is provided."""
        yaml_file = io.StringIO(
            f"""
        path: {MOCK_STORAGE_PATH!r}
        """
        )

        with pytest.raises(
            ValidationError, match=re.compile(r'"name"[^\n]+\n\s+"Missing data for required field."', re.MULTILINE)
        ) as excinfo:
            index = load_index(source=yaml_file)

    def test_missing_path(self) -> None:
        """Validate that load_index fails when no path is provided."""
        yaml_file = io.StringIO(
            """
        name: "foo"
        """
        )

        with pytest.raises(
            ValidationError, match=re.compile(r'"path"[^\n]+\n\s+"Missing data for required field."', re.MULTILINE)
        ) as excinfo:
            index = load_index(source=yaml_file)

    def test_minimal(self) -> None:
        """Validate that load_index succeeds when only provided the required fields."""
        yaml_file = io.StringIO(
            f"""
        name: "foo"
        path: {MOCK_STORAGE_PATH!r}
        """
        )

        index = load_index(source=yaml_file)

        assert index.name == "foo"
        assert index.path == MOCK_STORAGE_PATH
        assert index.stage == "Development"
        assert index.version == None
        assert index.description == None
        assert index.tags == {}
        assert index.properties == {}
        assert index.id == None

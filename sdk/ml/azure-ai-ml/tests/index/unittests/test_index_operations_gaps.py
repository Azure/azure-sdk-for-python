import json
from typing import Callable

import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.entities._assets import Index
from azure.ai.ml.entities._indexes import LocalSource, ModelConfiguration
from azure.ai.ml.exceptions import ValidationException

from dataclasses import dataclass
from pathlib import Path
from typing import List, Any
from devtools_testutils import add_uri_regex_sanitizer
from devtools_testutils.fake_credentials import SANITIZED
from azure.ai.ml.constants._common import LONG_URI_REGEX_FORMAT
from azure.ai.ml.entities._indexes import IndexDataSource, GitSource
import random


@pytest.fixture
def randstr():
    """Simple randstr fixture for unit tests that generates random strings without recording infrastructure."""
    def _generate(variable_name: str) -> str:
        return f"test_{random.randint(1, 1000000000000)}"
    return _generate


TEST_CONFIGS = Path(__file__).resolve().parent.parent.parent / "test_configs"

def is_datastore_uri(s: str) -> bool:
    """Check whether the string is a datastore uri.

    Should match the format azureml://subscriptions/{}/resourcegroups/{}/workspaces/{}/datastores/{}/paths/{} }
    """
    return bool(__import__("re").match(LONG_URI_REGEX_FORMAT, s))

@pytest.fixture()
def storage_account_uri_sanitizer():
    add_uri_regex_sanitizer(
        regex=r"https://(?<storage_account_name>[^\.]+).blob\.core\.windows\.net",
        group_for_replace="storage_account_name",
        value=SANITIZED,
        function_scoped=True,
    )

@dataclass


class IndexesVersionInfo:
    name: str
    """The index name."""
    indexes: List[Index]
    """All registered versions of the index."""
    latest: Index
    """The latest version of the index."""

@pytest.mark.unittest
class TestIndexOperationsGaps:
    def test_get_with_both_version_and_label_raises(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        """Validate that get() raises if both version and label are provided."""
        name = randstr("idx")

        with pytest.raises(ValidationException) as ex:
            client.indexes.get(name=name, version="1", label="latest")

        assert "Cannot specify both version and label." in str(ex.value)

    def test_get_with_neither_version_nor_label_raises(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        """Validate that get() raises if neither version nor label is provided."""
        name = randstr("idx")

        with pytest.raises(ValidationException) as ex:
            client.indexes.get(name=name)

        assert "Must provide either version or label." in str(ex.value)

    def test_build_index_unsupported_input_source_type_raises(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        """Validate that build_index raises ValueError for unsupported input_source types."""
        name = randstr("idx")

        # Build a minimal embeddings model configuration object structure expected by the API.
        # Use a simple namespace-like dict via json load/dump to avoid depending on internal constructors.
        # The build_index method expects a ModelConfiguration object with attributes; constructing via Index entity
        # is not appropriate here. Instead, reuse Index entity fields enough to reach unsupported input_source branch.
        # However, build_index is a method on the service; we call it with an intentionally invalid input_source type
        # to trigger the final ValueError branch.

        class DummyModelConfig:
            model_name = "dummy"
            deployment_name = "dummy"
            connection_name = "dummy"

        dummy_embeddings = DummyModelConfig()

        # Pass an unsupported input_source (an int) to trigger the unsupported type ValueError
        with pytest.raises(ValueError) as ex:
            client.indexes.build_index(
                name=name,
                embeddings_model_config=dummy_embeddings,
                input_source=12345,
            )

        assert "Unsupported input source type" in str(ex.value)

@pytest.mark.unittest
class TestIndexCreateOrUpdateValidation:
    def test_create_or_update_missing_version_and_no_autoincrement_raises(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        """Validate that create_or_update raises when version is missing and auto-increment is disabled."""
        name = randstr("index_name")
        # Do not set version and ensure auto-increment is not enabled (default behavior)
        idx = Index(name=name)
        idx.version = None
        # Ensure _auto_increment_version is False to exercise the branch that requires an explicit version
        idx._auto_increment_version = False

        with pytest.raises(ValidationException) as ex:
            client.indexes.create_or_update(idx)

        assert "Must specify a version." in str(ex.value)

@pytest.mark.unittest
class TestIndexValidationBranches:
    def test_build_index_parses_document_path_regex_and_unsupported_input_source_raises(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        """Validate that build_index parses document_path_replacement_regex JSON and raises for unsupported input_source types."""

        index_name = randstr("index_name")

        # Construct a minimal ModelConfiguration required by build_index. Use a simple dummy object with the
        # attributes accessed by build_index to avoid needing to satisfy ModelConfiguration's full constructor.
        class DummyModelConfig:
            model_name = "mymodel"
            deployment_name = "mydeployment"
            connection_name = "myconnection"

        model_config = DummyModelConfig()

        # Provide a JSON string for document_path_replacement_regex to exercise the json.loads branch (uncovered statement).
        document_path_replacement_regex = json.dumps({"match_pattern": "old", "replacement_pattern": "new"})

        # Use an unsupported input_source type (int) to trigger the final ValueError branch without making service calls.
        with pytest.raises(ValueError) as exinfo:
            client.indexes.build_index(
                name=index_name,
                embeddings_model_config=model_config,
                document_path_replacement_regex=document_path_replacement_regex,
                input_source=12345,
            )

        assert "Unsupported input source type" in str(exinfo.value)

@pytest.mark.usefixtures("storage_account_uri_sanitizer")
@pytest.mark.unittest
class TestIndexOperationsGaps_Generated:
    def test_build_index_with_parsed_document_path_regex_and_unsupported_input_source_raises(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        """Verify that providing a JSON document_path_replacement_regex is parsed and that unsupported
        input_source types raise a ValueError with the expected message.
        This exercises the json.loads branch and the code path that constructs CitationRegex when a
        replacement regex is provided, then exercises the final unsupported-type ValueError branch.
        """
        name = randstr("index_name")

        # Build a minimal ModelConfiguration required by the API
        class DummyModelConfig:
            model_name = "gpt-embedding"
            deployment_name = "emb-deploy"
            connection_name = "conn-id"

        embeddings_model_config = DummyModelConfig()

        # Provide a valid JSON string for document_path_replacement_regex to exercise json.loads branch
        replacement = json.dumps({"match_pattern": "old", "replacement_pattern": "new"})

        # Use an unsupported input_source type (int) to trigger the final ValueError
        with pytest.raises(ValueError) as excinfo:
            client.indexes.build_index(
                name=name,
                embeddings_model_config=embeddings_model_config,
                document_path_replacement_regex=replacement,
                input_source=123,  # unsupported type intentionally
            )

        assert str(excinfo.value).startswith("Unsupported input source type")

    def test_build_index_with_invalid_json_raises_value_error_from_json_loads(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        """Provide invalid JSON to document_path_replacement_regex to ensure json.loads raises and the
        exception propagates as a ValueError. This covers the json.loads failure branch.
        """
        name = randstr("index_name")

        class DummyModelConfig:
            model_name = "gpt-embedding"
            deployment_name = "emb-deploy"
            connection_name = "conn-id"

        embeddings_model_config = DummyModelConfig()

        # Invalid JSON (missing a quote)
        invalid_json = '{"match_pattern": "old", "replacement_pattern": new}'

        with pytest.raises(ValueError):
            client.indexes.build_index(
                name=name,
                embeddings_model_config=embeddings_model_config,
                document_path_replacement_regex=invalid_json,
                input_source=123,  # unsupported but JSON parsing should fail first
            )

@pytest.mark.unittest
class TestIndexBuildIndexGaps:
    def test_build_index_with_parsed_document_path_regex_and_unsupported_input_source_raises(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        """Provide a valid JSON document_path_replacement_regex to exercise json.loads branch
        and pass an unsupported input_source type to trigger the final ValueError branch.
        """
        index_name = randstr("index_name")

        # Minimal ModelConfiguration required by build_index; only attribute names used by build_open_ai_protocol
        class DummyModelConfig:
            model_name = "model"
            deployment_name = "deployment"
            connection_name = "conn"

        embeddings_config = DummyModelConfig()

        # Valid JSON for document_path_replacement_regex triggers json.loads -> dict path
        doc_regex_json = json.dumps({"match_pattern": "foo", "replacement_pattern": "bar"})

        with pytest.raises(ValueError) as ex:
            # Pass an unsupported input_source (int) to hit the ValueError at the end of build_index
            client.indexes.build_index(
                name=index_name,
                embeddings_model_config=embeddings_config,
                document_path_replacement_regex=doc_regex_json,
                input_source=12345,
            )

        assert "Unsupported input source type" in str(ex.value)

    def test_build_index_with_invalid_document_path_regex_raises(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        """Provide malformed JSON to document_path_replacement_regex to exercise the json.loads failure path.
        """
        index_name = randstr("index_name")

        class DummyModelConfig:
            model_name = "model"
            deployment_name = "deployment"
            connection_name = "conn"

        embeddings_config = DummyModelConfig()

        # Malformed JSON should raise a ValueError (JSONDecodeError subclass)
        malformed_json = "{not: valid, json}"

        with pytest.raises(ValueError):
            client.indexes.build_index(
                name=index_name,
                embeddings_model_config=embeddings_config,
                document_path_replacement_regex=malformed_json,
                input_source=12345,
            )

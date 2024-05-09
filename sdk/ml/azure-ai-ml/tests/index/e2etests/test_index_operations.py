import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

import pytest
from devtools_testutils import AzureRecordedTestCase, add_uri_regex_sanitizer
from devtools_testutils.fake_credentials import SANITIZED

from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import LONG_URI_REGEX_FORMAT
from azure.ai.ml.entities._assets import Index

TEST_CONFIGS = Path(__file__).resolve().parent.parent.parent / "test_configs"


@dataclass
class IndexesVersionInfo:
    name: str
    """The index name."""
    indexes: List[Index]
    """All registered versions of the index."""
    latest: Index
    """The latest version of the index."""


def is_datastore_uri(s: str) -> bool:
    """Check whether the string is a datastore uri.

    Should match the format azureml://subscriptions/{}/resourcegroups/{}/workspaces/{}/datastores/{}/paths/{}
    """
    return bool(re.match(LONG_URI_REGEX_FORMAT, s))


@pytest.fixture()
def storage_account_uri_sanitizer():
    """Sanitizes URIs of the form NAME.blob.core.windows.net to sanitized.blob.core.windows.net


    This fixture is a stop gap to deal with https://github.com/Azure/azure-sdk-for-python/issues/35447
    """
    add_uri_regex_sanitizer(
        regex=r"https://(?<storage_account_name>[^\.]+).blob\.core\.windows\.net",
        group_for_replace="storage_account_name",
        value=SANITIZED,
        function_scoped=True,
    )


@pytest.fixture()
def index_with_multiple_versions(client: MLClient) -> IndexesVersionInfo:
    """An index with multiple registered versions in the workspace."""
    name = "test_fixture_index_with_multiple_versions"

    versions = ("1", "2")
    indexes = [
        Index(
            name=name,
            version=version,
            stage="Development",
            tags={"tag1": "foo", "tag2": "bar"},
            properties={"prop1": "foo", "prop2": "bar"},
            path=TEST_CONFIGS / "index" / "single_file_index" / "README.md",
        )
        for version in versions
    ]

    # This is a hack to only call create_or_update once for the pytest session
    # Can't set this fixture's scope to "session" since client depends on a function scoped fixture that we don't
    # own.
    if not getattr(index_with_multiple_versions, "__called", False):
        for index in indexes:
            print(client.indexes.create_or_update(index).id)
        setattr(index_with_multiple_versions, "__called", True)

    return IndexesVersionInfo(name=name, indexes=indexes, latest=indexes[-1])


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "storage_account_uri_sanitizer")
class TestIndex(AzureRecordedTestCase):
    def test_create(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        """Validate that we can create an index."""

        index_name = randstr("index_name")
        created_index = client.indexes.create_or_update(
            Index(
                name=index_name,
                version="1",
                stage="Development",
                tags={"tag1": "foo", "tag2": "bar"},
                properties={"prop1": "foo", "prop2": "bar"},
                path=TEST_CONFIGS / "index" / "single_file_index" / "README.md",
            )
        )

        assert created_index.name == index_name
        assert created_index.version == "1"
        assert created_index.stage == "Development"
        assert created_index.tags == {"tag1": "foo", "tag2": "bar"}
        assert created_index.properties == {"prop1": "foo", "prop2": "bar"}
        assert created_index.creation_context is not None
        assert is_datastore_uri(created_index.path), "create_or_update should upload local files to a storage account"

    def test_create_autoincrement_version(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        """Validate that create_or_update will autoincrement the version if Index.version is unset."""

        index_name = randstr("index_name")

        # Create an index without specifying the version, let the service set a version
        created_index = client.indexes.create_or_update(
            # NOTE: We AREN'T setting a version for this index
            Index(
                name=index_name,
                stage="Development",
                description="This is a test index.",
                tags={"tag1": "foo", "tag2": "bar"},
                properties={"prop1": "foo", "prop2": "bar"},
                path=TEST_CONFIGS / "index" / "single_file_index" / "README.md",
            )
        )

        assert created_index.version is not None, "Service should have provided a version for the index"

        assert created_index.name == index_name
        assert created_index.description == "This is a test index."
        assert created_index.stage == "Development"
        assert created_index.tags == {"tag1": "foo", "tag2": "bar"}
        assert created_index.properties == {"prop1": "foo", "prop2": "bar"}
        assert created_index.creation_context is not None
        assert is_datastore_uri(created_index.path), "create_or_update should upload local files to a storage account"

        # Verify that submitting the index again increments the version
        second_created_index = client.indexes.create_or_update(
            # NOTE: We AREN'T setting a version for this index
            Index(
                name=index_name,
                stage="Development",
                path=TEST_CONFIGS / "index" / "single_file_index" / "README.md",
            )
        )

        assert second_created_index.version is not None, "Service should have provided a version for the index"
        assert second_created_index.version != created_index.version

    def test_get_version(self, client: MLClient, index_with_multiple_versions: IndexesVersionInfo) -> None:
        """Validate that we can retrieve an index by name and version"""

        index = index_with_multiple_versions.indexes[0]

        retrieved_index = client.indexes.get(name=index.name, version=index.version)

        assert retrieved_index.name == index.name
        assert retrieved_index.version == index.version
        assert retrieved_index.description == index.description
        assert retrieved_index.stage == index.stage
        assert retrieved_index.tags == index.tags
        assert retrieved_index.properties == index.properties
        assert Path(retrieved_index.path).name == Path(index.path).name

    def test_get_latest_label(self, client: MLClient, index_with_multiple_versions: IndexesVersionInfo) -> None:
        """Validate that we can retrive an index using the latest label"""

        latest_index = index_with_multiple_versions.latest
        latest_version = latest_index.version

        retrieved_index = client.indexes.get(name=latest_index.name, label="latest")

        assert retrieved_index.version == latest_version

        assert retrieved_index.name == latest_index.name
        assert retrieved_index.stage == latest_index.stage
        assert retrieved_index.description == latest_index.description
        assert retrieved_index.tags == latest_index.tags
        assert retrieved_index.properties == latest_index.properties
        assert Path(retrieved_index.path).name == Path(latest_index.path).name

    def test_list(self, client: MLClient, index_with_multiple_versions: IndexesVersionInfo) -> None:
        """Validate that we can list the indexes in a workspace"""
        indexes = list(client.indexes.list())
        known_indexes: List[Index] = [index_with_multiple_versions.name]

        # We aren't asserting an exact match since other tests may have created indexes we are unaware of
        assert {i.name for i in indexes}.issuperset(
            known_indexes
        ), "client.indexes.list does not list indexes that are known to be in workspace"

        assert len(indexes) >= len(known_indexes)

    def test_list_index_versions(self, client: MLClient, index_with_multiple_versions: IndexesVersionInfo) -> None:
        """Validate that we can list the version of a single index"""
        index_versions = list(client.indexes.list(name=index_with_multiple_versions.name))

        assert len(index_versions) == len(index_with_multiple_versions.indexes)
        assert all(i.name == index_with_multiple_versions.name for i in index_versions)
        assert {i.version for i in index_with_multiple_versions.indexes} == {i.version for i in index_versions}

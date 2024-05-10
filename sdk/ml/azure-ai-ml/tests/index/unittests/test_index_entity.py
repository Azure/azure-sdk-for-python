import datetime

import pytest

from azure.ai.ml._restclient.azure_ai_assets_v2024_04_01.azureaiassetsv20240401.models import Index as RestIndex
from azure.ai.ml._restclient.azure_ai_assets_v2024_04_01.azureaiassetsv20240401.models import (
    SystemData as RestSystemData,
)
from azure.ai.ml.entities import Index


@pytest.mark.unittest
class TestIndexEntity:
    def test_index_from_rest(self) -> None:
        rest_index = RestIndex(
            stage="Development",
            description="Hello World",
            tags={"tag1": "foo", "tag2": "bar"},
            properties={"prop1": "foo", "prop2": "bar"},
            id="azureml://locations/eastus/workspaces/my_workspace/indexes/my_index/versions/1",
            storage_uri=(
                "https://mystorageaccount.blob.core.windows.net/"
                + "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX-azureml-blobstore/"
                + "LocalUpload/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/index"
            ),
            system_data=RestSystemData(
                created_at=datetime.datetime(2024, 1, 1),
                created_by="Firstname Lastname",
                created_by_type="User",
                last_modified_at=datetime.datetime(2024, 1, 1),
            ),
        )

        index = Index._from_rest_object(rest_index)

        assert index.stage == "Development"
        assert index.description == "Hello World"

        # FIXME: Every other asset in the SDK exposes the ARM ID and not the asset ID
        assert index.id == "azureml://locations/eastus/workspaces/my_workspace/indexes/my_index/versions/1"

        assert index.name == "my_index"
        assert index.version == "1"
        assert index.stage == "Development"
        assert index.tags == {"tag1": "foo", "tag2": "bar"}
        assert index.properties == {"prop1": "foo", "prop2": "bar"}
        assert index.path == (
            "https://mystorageaccount.blob.core.windows.net/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX-azureml-blobstore/"
            + "LocalUpload/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/index"
        )

    def test_index_to_rest(self) -> None:
        index = Index(
            name="foo",
            version="1",
            stage="Development",
            description="Hello World",
            tags={"tag1": "foo", "tag2": "bar"},
            properties={"prop1": "foo", "prop2": "bar"},
            path=(
                "https://mystorageaccount.blob.core.windows.net/"
                + "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX-azureml-blobstore/"
                + "LocalUpload/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/index"
            ),
        )

        rest_index = index._to_rest_object()

        assert rest_index.stage == "Development"
        assert rest_index.description == "Hello World"
        assert rest_index.stage == "Development"
        assert rest_index.tags == {"tag1": "foo", "tag2": "bar"}
        assert rest_index.properties == {"prop1": "foo", "prop2": "bar"}
        assert rest_index.system_data is None
        assert rest_index.id is None
        assert rest_index.storage_uri == (
            "https://mystorageaccount.blob.core.windows.net/"
            + "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX-azureml-blobstore/"
            + "LocalUpload/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/index"
        )

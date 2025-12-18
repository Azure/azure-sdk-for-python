# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import AzureAISearchIndex, IndexType
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async


class TestIndexesAsync(TestBase):

    # To run this test, use the following command in the \sdk\aiprojects\azure-ai-projects folder:
    # cls & pytest tests\test_indexes_async.py::TestIndexesAsync::test_indexes_async -s
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_indexes_async(self, **kwargs):

        index_name = self.test_indexes_params["index_name"]
        index_version = self.test_indexes_params["index_version"]
        ai_search_connection_name = self.test_indexes_params["ai_search_connection_name"]
        ai_search_index_name = self.test_indexes_params["ai_search_index_name"]

        async with self.create_async_client(**kwargs) as project_client:

            print(
                f"[test_indexes] Create Index `{index_name}` with version `{index_version}`, referencing an existing AI Search resource:"
            )
            index = await project_client.indexes.create_or_update(
                name=index_name,
                version=index_version,
                index=AzureAISearchIndex(connection_name=ai_search_connection_name, index_name=ai_search_index_name),
            )
            print(index)
            TestBase.validate_index(
                index,
                expected_index_type=IndexType.AZURE_SEARCH,
                expected_index_name=index_name,
                expected_index_version=index_version,
                expected_ai_search_connection_name=ai_search_connection_name,
                expected_ai_search_index_name=ai_search_index_name,
            )

            print(f"[test_indexes] Get Index `{index_name}` version `{index_version}`:")
            index = await project_client.indexes.get(name=index_name, version=index_version)
            print(index)
            TestBase.validate_index(
                index,
                expected_index_type=IndexType.AZURE_SEARCH,
                expected_index_name=index_name,
                expected_index_version=index_version,
                expected_ai_search_connection_name=ai_search_connection_name,
                expected_ai_search_index_name=ai_search_index_name,
            )

            print("[test_indexes] List latest versions of all Indexes:")
            empty = True
            async for index in project_client.indexes.list():
                empty = False
                print(index)
                TestBase.validate_index(index)
            assert not empty

            print(f"[test_indexes] Listing all versions of the Index named `{index_name}`:")
            empty = True
            async for index in project_client.indexes.list_versions(name=index_name):
                empty = False
                print(index)
                TestBase.validate_index(index)
            assert not empty

            print(f"[test_indexes] Delete Index `{index_name}` version `{index_version}`.")
            await project_client.indexes.delete(name=index_name, version=index_version)

            print(
                f"[test_indexes] Again delete Index `{index_name}` version `{index_version}`. Since it does not exist, the REST API should return 204 (No content). This call should NOT throw an exception."
            )
            await project_client.indexes.delete(name=index_name, version=index_version)

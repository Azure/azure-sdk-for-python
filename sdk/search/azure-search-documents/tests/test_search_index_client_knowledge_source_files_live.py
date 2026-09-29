# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for synchronous File knowledge source operations."""

from __future__ import annotations

from devtools_testutils import AzureRecordedTestCase

from _capabilities import require_capability
from _search_helpers import live_test, make_index_client, safe_delete

_FILE_CAPABILITIES = (
    "azure.search.documents.indexes.SearchIndexClient.create_or_update_knowledge_source",
    "azure.search.documents.indexes.SearchIndexClient.delete_knowledge_source",
    "azure.search.documents.indexes.SearchIndexClient.upload_knowledge_source_file_multipart",
    "azure.search.documents.indexes.SearchIndexClient.update_knowledge_source_file",
    "azure.search.documents.indexes.SearchIndexClient.list_knowledge_source_files",
    "azure.search.documents.indexes.SearchIndexClient.delete_knowledge_source_file",
    "azure.search.documents.indexes.models.FileKnowledgeSource",
    "azure.search.documents.indexes.models.FileKnowledgeSourceParameters",
    "azure.search.documents.indexes.models.FileUploadMetadata",
    "azure.search.documents.indexes.models.UpdateKnowledgeSourceFileRequest",
    "azure.search.documents.indexes.models.UploadKnowledgeSourceFileMultipartRequest",
    "azure.search.documents.knowledgebases.models.KnowledgeSourceAzureOpenAIVectorizer",
    "azure.search.documents.knowledgebases.models.KnowledgeSourceIngestionParameters",
)


def _build_file_knowledge_source(name, endpoint, deployment, model):
    from azure.search.documents.indexes.models import (
        AzureOpenAIVectorizerParameters,
        FileKnowledgeSource,
        FileKnowledgeSourceParameters,
    )
    from azure.search.documents.knowledgebases.models import (
        KnowledgeSourceAzureOpenAIVectorizer,
        KnowledgeSourceIngestionParameters,
    )

    return FileKnowledgeSource(
        name=name,
        file_parameters=FileKnowledgeSourceParameters(
            ingestion_parameters=KnowledgeSourceIngestionParameters(
                content_extraction_mode="minimal",
                embedding_model=KnowledgeSourceAzureOpenAIVectorizer(
                    azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
                        resource_url=endpoint,
                        deployment_name=deployment,
                        model_name=model,
                    )
                ),
            )
        ),
    )


class TestSearchIndexClientKnowledgeSourceFiles(AzureRecordedTestCase):
    @live_test()
    def test_multipart_upload_update_list_and_delete(
        self,
        endpoint: str,
        search_azure_openai_endpoint: str,
        search_azure_openai_embedding_deployment: str,
        search_azure_openai_embedding_model: str,
    ) -> None:
        require_capability(*_FILE_CAPABILITIES)
        from azure.search.documents.indexes.models import (
            FileUploadMetadata,
            UpdateKnowledgeSourceFileRequest,
            UploadKnowledgeSourceFileMultipartRequest,
        )

        source_name = self.get_resource_name("knowledge-source-files")
        primary_id = None
        annex_id = None

        with make_index_client(endpoint) as client:
            try:
                client.create_or_update_knowledge_source(
                    _build_file_knowledge_source(
                        source_name,
                        search_azure_openai_endpoint,
                        search_azure_openai_embedding_deployment,
                        search_azure_openai_embedding_model,
                    )
                )

                primary_metadata = FileUploadMetadata(
                    file_name="hotels/primary.txt",
                    metadata={"category": "hotel", "city": "Seattle"},
                )
                primary = client.upload_knowledge_source_file_multipart(
                    source_name,
                    UploadKnowledgeSourceFileMultipartRequest(
                        metadata=primary_metadata,
                        content=("primary.txt", b"Historic Harbor Hotel has free parking.", "text/plain"),
                    ),
                )
                primary_id = primary.file_id
                assert primary_id is not None

                annex = client.upload_knowledge_source_file_multipart(
                    source_name,
                    UploadKnowledgeSourceFileMultipartRequest(
                        metadata=FileUploadMetadata(
                            file_name="hotels/annex.txt",
                            metadata={"category": "hotel", "city": "Portland"},
                        ),
                        content=("annex.txt", b"Harbor Hotel Annex has meeting rooms.", "text/plain"),
                    ),
                )
                annex_id = annex.file_id
                assert annex_id is not None

                updated = client.update_knowledge_source_file(
                    source_name,
                    primary_id,
                    UpdateKnowledgeSourceFileRequest(
                        metadata=primary_metadata,
                        content=(
                            "primary.txt",
                            b"Historic Harbor Hotel has free parking and free Wi-Fi.",
                            "text/plain",
                        ),
                    ),
                )
                assert updated.file_id == primary_id
                assert updated.metadata == {"category": "hotel", "city": "Seattle"}

                files = list(
                    client.list_knowledge_source_files(
                        source_name,
                        prefix="hotels/",
                        search="hotels",
                        page_size=1,
                        search_type="prefix",
                    )
                )
                file_ids = [file.file_id for file in files]
                assert set(file_ids) == {primary_id, annex_id}
                assert len(file_ids) == len(set(file_ids))

                client.delete_knowledge_source_file(source_name, primary_id)
                primary_id = None
                client.delete_knowledge_source_file(source_name, annex_id)
                annex_id = None
                assert list(client.list_knowledge_source_files(source_name, prefix="hotels/")) == []
            finally:
                if primary_id is not None:
                    safe_delete(client.delete_knowledge_source_file, source_name, primary_id)
                if annex_id is not None:
                    safe_delete(client.delete_knowledge_source_file, source_name, annex_id)
                safe_delete(client.delete_knowledge_source, source_name)

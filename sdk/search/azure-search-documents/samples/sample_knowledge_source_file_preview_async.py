# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates File knowledge source setup and retrieval using async clients and the 2026-10-01 GA API.

USAGE:
    python sample_knowledge_source_file_preview_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_OPENAI_ENDPOINT - endpoint for your Azure OpenAI resource
    4) AZURE_OPENAI_EMBEDDING_DEPLOYMENT - deployment name for your embedding model
    5) AZURE_OPENAI_EMBEDDING_MODEL - model name for your embedding model

    The Search service's managed identity needs Cognitive Services OpenAI User on
    the embedding resource. Direct uploads do not require a Storage account.
"""

import asyncio
import os

from sample_utils import (
    cleanup_resources_async,
    get_sample_run_tag,
    print_retrieval_summary,
    wait_for_knowledge_source_active_async,
)

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]
run_tag = get_sample_run_tag()
knowledge_source_name = f"hotels-file-ks-{run_tag}"
knowledge_base_name = f"hotels-file-kb-{run_tag}"
upload_file_name = "hotels.txt"


async def main():  # pylint: disable=too-many-locals
    # [START sample_knowledge_source_file_preview_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        AzureOpenAIVectorizerParameters,
        FileUploadMetadata,
        FileKnowledgeSource,
        FileKnowledgeSourceParameters,
        KnowledgeBase,
        KnowledgeSourceReference,
        UpdateKnowledgeSourceFileRequest,
        UploadKnowledgeSourceFileMultipartRequest,
    )
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        FileKnowledgeSourceParams,
        KnowledgeBaseFileReference,
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalMinimalReasoningEffort,
        KnowledgeRetrievalSemanticIntent,
        KnowledgeSourceAzureOpenAIVectorizer,
        KnowledgeSourceIngestionParameters,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        try:
            knowledge_source = FileKnowledgeSource(
                name=knowledge_source_name,
                description="Hotel File knowledge source",
                file_parameters=FileKnowledgeSourceParameters(
                    ingestion_parameters=KnowledgeSourceIngestionParameters(
                        content_extraction_mode="minimal",
                        network_access_mode="public",
                        embedding_model=KnowledgeSourceAzureOpenAIVectorizer(
                            azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
                                resource_url=os.environ["AZURE_OPENAI_ENDPOINT"],
                                deployment_name=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],
                                model_name=os.environ["AZURE_OPENAI_EMBEDDING_MODEL"],
                            )
                        ),
                    )
                ),
            )
            created_knowledge_source = await index_client.create_or_update_knowledge_source(knowledge_source)
            print(f"Created: knowledge source '{created_knowledge_source.name}'")

            retrieved_knowledge_source = await index_client.get_knowledge_source(knowledge_source_name)
            print(f"Retrieved: knowledge source '{retrieved_knowledge_source.name}'")

            status = await index_client.get_knowledge_source_status(knowledge_source_name)
            capacity = status.as_dict().get("fileCapacity")
            if capacity is not None:
                print(
                    f"File capacity: {capacity.get('remainingFileCount')} of {capacity.get('maxFileCount')} remaining"
                )
                print(f"Maximum upload size: {capacity.get('maxFileSizeBytes')} bytes")
                if capacity.get("remainingFileCount") is not None and capacity["remainingFileCount"] < 2:
                    raise RuntimeError("This sample requires capacity for two files.")

            knowledge_base = KnowledgeBase(
                name=knowledge_base_name,
                description="Hotel File knowledge base",
                knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
                output_mode="extractiveData",
                retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
            )
            await index_client.create_or_update_knowledge_base(knowledge_base)

            file_content = b"Historic Harbor Hotel has free parking and a rooftop restaurant."
            file_metadata = FileUploadMetadata(
                file_name=f"hotels/{upload_file_name}",
                metadata={"category": "hotel", "city": "Seattle"},
            )
            uploaded_file = await index_client.upload_knowledge_source_file_multipart(
                name=knowledge_source_name,
                body=UploadKnowledgeSourceFileMultipartRequest(
                    metadata=file_metadata,
                    content=(upload_file_name, file_content, "text/plain"),
                ),
            )
            print(f"Uploaded: file '{uploaded_file.file_name}'")
            print(f"Prefix: {uploaded_file.prefix}; size: {uploaded_file.file_size_bytes} bytes")
            print(f"Service-selected modes: {uploaded_file.parsing_mode}, {uploaded_file.extraction_mode}")
            print(f"Created: {uploaded_file.created_at}; updated: {uploaded_file.last_updated_at}")
            print(f"Processing error: {uploaded_file.error_message}")
            assert uploaded_file.file_id is not None

            annex_file = await index_client.upload_knowledge_source_file_multipart(
                name=knowledge_source_name,
                body=UploadKnowledgeSourceFileMultipartRequest(
                    metadata=FileUploadMetadata(
                        file_name="hotels/annex.txt",
                        metadata={"category": "hotel", "city": "Portland"},
                    ),
                    content=("annex.txt", b"Harbor Hotel Annex has meeting rooms.", "text/plain"),
                ),
            )
            assert annex_file.file_id is not None

            updated_file = await index_client.update_knowledge_source_file(
                file_id=uploaded_file.file_id,
                name=knowledge_source_name,
                body=UpdateKnowledgeSourceFileRequest(
                    metadata=FileUploadMetadata(
                        file_name=f"hotels/{upload_file_name}",
                        metadata={"category": "renovated hotel", "city": "Seattle"},
                    ),
                    content=(
                        upload_file_name,
                        b"Historic Harbor Hotel has free parking, free Wi-Fi, and a rooftop restaurant.",
                        "text/plain",
                    ),
                ),
            )
            print(f"Updated: file '{updated_file.file_name}'")
            assert updated_file.metadata == {"category": "renovated hotel", "city": "Seattle"}
            assert updated_file.parsing_mode is not None
            assert updated_file.extraction_mode in {"minimal", "standard"}

            files = [
                file
                async for file in index_client.list_knowledge_source_files(
                    knowledge_source_name,
                    prefix="hotels/",
                    search="hotels",
                    page_size=1,
                    search_type="prefix",
                )
            ]
            file_ids = [file.file_id for file in files]
            assert set(file_ids) == {uploaded_file.file_id, annex_file.file_id}
            assert len(file_ids) == len(set(file_ids))
            print(f"Paged through {len(files)} files without duplicates")

            await wait_for_knowledge_source_active_async(index_client, knowledge_source_name)
            retrieval_client = KnowledgeBaseRetrievalClient(
                service_endpoint, AzureKeyCredential(key), knowledge_base_name=knowledge_base_name
            )
            try:
                request = KnowledgeBaseRetrievalRequest(
                    include_activity=True,
                    intents=[KnowledgeRetrievalSemanticIntent(search="Which hotel has a rooftop restaurant?")],
                    knowledge_source_params=[
                        FileKnowledgeSourceParams(
                            knowledge_source_name=knowledge_source_name,
                            include_references=True,
                            include_reference_source_data=True,
                        )
                    ],
                )
                retrieval_result = await retrieval_client.retrieve(request)
                print_retrieval_summary(retrieval_result)
                for reference in retrieval_result.references or []:
                    if isinstance(reference, KnowledgeBaseFileReference):
                        print(f"Search-owned citation URL: {reference.citation_url}")
            finally:
                await retrieval_client.close()

            await index_client.delete_knowledge_source_file(knowledge_source_name, uploaded_file.file_id)
            await index_client.delete_knowledge_source_file(knowledge_source_name, annex_file.file_id)
            print("Deleted both uploaded files")
            # [END sample_knowledge_source_file_preview_async]
        finally:
            await cleanup_resources_async(
                index_client,
                knowledge_base_name=knowledge_base_name,
                knowledge_source_name=knowledge_source_name,
            )


if __name__ == "__main__":
    asyncio.run(main())

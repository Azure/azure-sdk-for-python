# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates preview File knowledge source setup and retrieval using async clients.

USAGE:
    python sample_knowledge_source_file_preview_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_OPENAI_ENDPOINT - endpoint for your Azure OpenAI resource
    4) AZURE_OPENAI_EMBEDDING_DEPLOYMENT - deployment name for your embedding model
    5) AZURE_OPENAI_EMBEDDING_MODEL - model name for your embedding model
"""

import asyncio
import os

from sample_utils import (
    cleanup_resources_async,
    get_sample_run_tag,
    print_retrieval_summary,
)


service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]
run_tag = get_sample_run_tag()
knowledge_source_name = f"hotels-file-ks-{run_tag}"
knowledge_base_name = f"hotels-file-kb-{run_tag}"
upload_file_name = "hotels.txt"


async def main():
    # [START sample_knowledge_source_file_preview_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        AzureOpenAIVectorizerParameters,
        FileKnowledgeSource,
        FileKnowledgeSourceParameters,
        KnowledgeBase,
        KnowledgeSourceReference,
    )
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        FileKnowledgeSourceParams,
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

            knowledge_base = KnowledgeBase(
                name=knowledge_base_name,
                description="Hotel File knowledge base",
                knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
                output_mode="extractiveData",
                retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
            )
            await index_client.create_or_update_knowledge_base(knowledge_base)

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
            finally:
                await retrieval_client.close()

            file_content = b"Historic Harbor Hotel has free parking and a rooftop restaurant."
            uploaded_file = await index_client.upload_knowledge_source_file(
                knowledge_source_name,
                file_content,
                filename=upload_file_name,
                content_type="application/octet-stream",
            )
            print(f"Uploaded: file '{uploaded_file.file_name}'")

            files = [file async for file in index_client.list_knowledge_source_files(knowledge_source_name)]
            print(f"Files: {len(files)}")
            # [END sample_knowledge_source_file_preview_async]
        finally:
            await cleanup_resources_async(
                index_client,
                knowledge_base_name=knowledge_base_name,
                knowledge_source_name=knowledge_source_name,
            )


if __name__ == "__main__":
    asyncio.run(main())

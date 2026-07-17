# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates preview Fabric Ontology knowledge source setup and retrieval using async clients.

USAGE:
    python sample_knowledge_source_fabric_ontology_preview_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_OPENAI_ENDPOINT - endpoint for your Azure OpenAI resource
    4) AZURE_OPENAI_API_KEY - key for your Azure OpenAI resource
    5) AZURE_OPENAI_DEPLOYMENT - deployment name for your chat model
    6) AZURE_OPENAI_MODEL - model name for your chat model
    7) AZURE_FABRIC_WORKSPACE_ID - Fabric workspace ID
    8) AZURE_FABRIC_ONTOLOGY_ID - Fabric ontology ID
    9) AZURE_SEARCH_QUERY_SOURCE_AUTHORIZATION - raw bearer token for query source access
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
knowledge_source_name = f"hotels-fabric-ontology-ks-{run_tag}"
knowledge_base_name = f"hotels-fabric-ontology-kb-{run_tag}"


async def main():
    # [START sample_knowledge_source_fabric_ontology_preview_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        AzureOpenAIVectorizerParameters,
        FabricOntologyKnowledgeSource,
        FabricOntologyKnowledgeSourceParameters,
        KnowledgeBase,
        KnowledgeBaseAzureOpenAIModel,
        KnowledgeSourceReference,
    )
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        FabricOntologyKnowledgeSourceParams,
        KnowledgeBaseMessage,
        KnowledgeBaseMessageTextContent,
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalLowReasoningEffort,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        try:
            knowledge_source = FabricOntologyKnowledgeSource(
                name=knowledge_source_name,
                description="Hotel Fabric Ontology knowledge source",
                fabric_ontology_parameters=FabricOntologyKnowledgeSourceParameters(
                    workspace_id=os.environ["AZURE_FABRIC_WORKSPACE_ID"],
                    ontology_id=os.environ["AZURE_FABRIC_ONTOLOGY_ID"],
                ),
            )
            created_knowledge_source = await index_client.create_or_update_knowledge_source(knowledge_source)
            print(f"Created: knowledge source '{created_knowledge_source.name}'")

            retrieved_knowledge_source = await index_client.get_knowledge_source(knowledge_source_name)
            print(f"Retrieved: knowledge source '{retrieved_knowledge_source.name}'")

            knowledge_base = KnowledgeBase(
                name=knowledge_base_name,
                description="Hotel Fabric Ontology knowledge base",
                knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
                output_mode="extractiveData",
                models=[
                    KnowledgeBaseAzureOpenAIModel(
                        azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
                            resource_url=os.environ["AZURE_OPENAI_ENDPOINT"],
                            api_key=os.environ["AZURE_OPENAI_API_KEY"],
                            deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT"],
                            model_name=os.environ["AZURE_OPENAI_MODEL"],
                        )
                    )
                ],
                retrieval_reasoning_effort=KnowledgeRetrievalLowReasoningEffort(),
            )
            await index_client.create_or_update_knowledge_base(knowledge_base)

            retrieval_client = KnowledgeBaseRetrievalClient(
                service_endpoint, AzureKeyCredential(key), knowledge_base_name=knowledge_base_name
            )
            try:
                request = KnowledgeBaseRetrievalRequest(
                    include_activity=True,
                    messages=[
                        KnowledgeBaseMessage(
                            role="user",
                            content=[KnowledgeBaseMessageTextContent(text="What hotel data is available?")],
                        )
                    ],
                    knowledge_source_params=[
                        FabricOntologyKnowledgeSourceParams(
                            knowledge_source_name=knowledge_source_name,
                            include_references=True,
                            include_reference_source_data=True,
                        )
                    ],
                )
                retrieval_result = await retrieval_client.retrieve(
                    request,
                    query_source_authorization=os.environ["AZURE_SEARCH_QUERY_SOURCE_AUTHORIZATION"],
                )
            finally:
                await retrieval_client.close()
            print_retrieval_summary(retrieval_result)
            # [END sample_knowledge_source_fabric_ontology_preview_async]
        finally:
            await cleanup_resources_async(
                index_client,
                knowledge_base_name=knowledge_base_name,
                knowledge_source_name=knowledge_source_name,
            )


if __name__ == "__main__":
    asyncio.run(main())

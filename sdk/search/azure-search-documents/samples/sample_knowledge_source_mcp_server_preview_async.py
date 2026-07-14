# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates preview MCP Server knowledge source setup and retrieval using async clients.

USAGE:
    python sample_knowledge_source_mcp_server_preview_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_OPENAI_ENDPOINT - endpoint for your Azure OpenAI resource
    4) AZURE_OPENAI_API_KEY - key for your Azure OpenAI resource
    5) AZURE_OPENAI_DEPLOYMENT - deployment name for your chat model
    6) AZURE_OPENAI_MODEL - model name for your chat model
    7) AZURE_MCP_SERVER_URL - MCP server URL
    8) AZURE_MCP_TOOL_NAME - MCP tool name
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
knowledge_source_name = f"hotels-mcp-server-ks-{run_tag}"
knowledge_base_name = f"hotels-mcp-server-kb-{run_tag}"


async def main():
    # [START sample_knowledge_source_mcp_server_preview_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        AzureOpenAIVectorizerParameters,
        KnowledgeBase,
        KnowledgeBaseAzureOpenAIModel,
        KnowledgeSourceReference,
        McpServerAutoOutputParsing,
        McpServerKnowledgeSource,
        McpServerKnowledgeSourceParameters,
        McpServerTool,
    )
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseMessage,
        KnowledgeBaseMessageTextContent,
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalLowReasoningEffort,
        McpServerKnowledgeSourceParams,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        try:
            knowledge_source = McpServerKnowledgeSource(
                name=knowledge_source_name,
                description="Hotel MCP server knowledge source",
                mcp_server_parameters=McpServerKnowledgeSourceParameters(
                    server_url=os.environ["AZURE_MCP_SERVER_URL"],
                    tools=[
                        McpServerTool(
                            name=os.environ["AZURE_MCP_TOOL_NAME"],
                            output_parsing=McpServerAutoOutputParsing(),
                        )
                    ],
                ),
            )
            created_knowledge_source = await index_client.create_or_update_knowledge_source(knowledge_source)
            print(f"Created: knowledge source '{created_knowledge_source.name}'")

            retrieved_knowledge_source = await index_client.get_knowledge_source(knowledge_source_name)
            print(f"Retrieved: knowledge source '{retrieved_knowledge_source.name}'")

            knowledge_base = KnowledgeBase(
                name=knowledge_base_name,
                description="Hotel MCP Server knowledge base",
                knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
                output_mode="answerSynthesis",
                retrieval_reasoning_effort=KnowledgeRetrievalLowReasoningEffort(),
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
                            content=[KnowledgeBaseMessageTextContent(text="Find hotel guidance from the MCP server.")],
                        )
                    ],
                    knowledge_source_params=[
                        McpServerKnowledgeSourceParams(
                            knowledge_source_name=knowledge_source_name,
                            include_references=True,
                            include_reference_source_data=True,
                        )
                    ],
                    max_runtime_in_seconds=120,
                )
                retrieval_result = await retrieval_client.retrieve(request)
            finally:
                await retrieval_client.close()
            print_retrieval_summary(retrieval_result)
            # [END sample_knowledge_source_mcp_server_preview_async]
        finally:
            await cleanup_resources_async(
                index_client,
                knowledge_base_name=knowledge_base_name,
                knowledge_source_name=knowledge_source_name,
            )


if __name__ == "__main__":
    asyncio.run(main())

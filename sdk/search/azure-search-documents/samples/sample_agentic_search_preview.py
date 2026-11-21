# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""
DESCRIPTION:
    Run direct agentic Search over hotel documents and inspect issued subqueries,
    termination and token usage. This is SearchClient.search, not KB retrieval.

USAGE:
    python sample_agentic_search_preview.py

    Set AZURE_SEARCH_SERVICE_ENDPOINT and optionally AZURE_SEARCH_API_KEY.
    Requires a November-preview service with agentic Search, semantic search, and
    paid standard Knowledge Retrieval already enabled. Microsoft Retriever 1
    has no free tier. This sample never changes the service's billing settings.
    Without a key, DefaultAzureCredential authenticates the caller.
    A uniquely named index is created and cleaned up; no model deployment is needed.
"""

import os
import uuid

from sample_utils import (
    cleanup_preview_resources,
    get_sample_run_tag,
    prepare_preview_hotel_index,
    preview_hotel_documents,
)


def main():
    # [START sample_agentic_search_preview]
    from azure.core.credentials import AzureKeyCredential
    from azure.identity import DefaultAzureCredential
    from azure.search.documents import ApiVersion, SearchClient
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.models import AgenticSearchDebugInfo, AgenticSearchOptions

    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    name = f"hotels-agentic-{get_sample_run_tag()}-{uuid.uuid4().hex[:6]}"
    documents = preview_hotel_documents()
    created: list[tuple[str, str]] = []
    with DefaultAzureCredential() as identity:
        key = os.environ.get("AZURE_SEARCH_API_KEY")
        credential = AzureKeyCredential(key) if key else identity
        with SearchIndexClient(endpoint, credential, api_version=ApiVersion.V2026_11_01_PREVIEW) as indexes:
            try:
                prepare_preview_hotel_index(indexes, endpoint, credential, name, documents, created)
                with SearchClient(endpoint, name, credential, api_version=ApiVersion.V2026_11_01_PREVIEW) as search:
                    pager = search.search(
                        search_text="Find hotels offering complimentary wireless internet and breakfast.",
                        query_type="agentic",
                        semantic_configuration_name="default",
                        agentic_options=AgenticSearchOptions(max_runtime_in_seconds=30),
                        debug="agentic",
                        select=["id", "title", "content"],
                        top=3,
                    )
                    results = list(pager)
                    assert results
                    assert {item["id"] for item in results} <= {item["id"] for item in documents}
                    info = pager.get_debug_info()
                    assert info is not None
                    debug = info.agentic
                    assert isinstance(debug, AgenticSearchDebugInfo)
                    assert debug.termination_reason != "modelFailed"
                    # The planner can stop without issuing additional subqueries.
                    sub_queries = debug.sub_queries or []
                    assert all(query.search and query.iteration >= 1 for query in sub_queries)
                    assert debug.usage is not None
                    assert debug.usage.agentic_planning_tokens >= 0
                    assert debug.usage.reasoning_tokens >= 0
                    assert debug.usage.agentic_planning_tokens + debug.usage.reasoning_tokens > 0
                    print("Returned hotels:", [item["title"] for item in results])
                    print("Termination:", debug.termination_reason)
                    print("Issued subqueries:", [(query.iteration, query.search) for query in sub_queries])
                    print("Planning tokens:", debug.usage.agentic_planning_tokens)
                    print("Reasoning tokens:", debug.usage.reasoning_tokens)
                    print("Usage includes work on candidates not returned; these are not separate billing totals.")
            finally:
                cleanup_preview_resources(indexes, created)
    # [END sample_agentic_search_preview]


if __name__ == "__main__":
    main()

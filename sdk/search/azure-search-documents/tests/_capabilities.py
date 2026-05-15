# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Capability gates for preview-only test scenarios.

See ``.github/skills/azure-search-documents/references/testing.md`` for the convention.
"""

from __future__ import annotations

import enum
import importlib
import inspect
from typing import Any, Mapping

import pytest

PREVIEW = "2026-05-01-preview"


def _surface(owner: str, kwargs: tuple = (), available_from: str = PREVIEW) -> Mapping[str, Any]:
    return {"owner": owner, "kwargs": kwargs, "available_from": available_from}


# Module aliases to keep the table compact.
_IM = "azure.search.documents.indexes.models"
_KBM = "azure.search.documents.knowledgebases.models"
_M = "azure.search.documents.models"
_IDX = "azure.search.documents.indexes"


def _model_capabilities() -> Mapping[str, Mapping[str, Any]]:
    """One entry per new public model class (existence-only) and per new field on existing models."""
    entries: dict = {}

    # New knowledge-source / parameter / supporting model classes.
    new_classes = [
        # IndexedSql
        f"{_IM}.IndexedSqlKnowledgeSource",
        f"{_IM}.IndexedSqlKnowledgeSourceParameters",
        f"{_IM}.ContentColumnMapping",
        f"{_IM}.EmbeddingColumnMapping",
        # WorkIQ (parameters live in knowledgebases.models)
        f"{_IM}.WorkIQKnowledgeSource",
        f"{_KBM}.WorkIQKnowledgeSourceParams",
        # File
        f"{_IM}.FileKnowledgeSource",
        f"{_IM}.FileKnowledgeSourceParameters",
        # MCP server
        f"{_IM}.McpServerKnowledgeSource",
        f"{_IM}.McpServerKnowledgeSourceParameters",
        f"{_IM}.McpServerAuthentication",
        f"{_IM}.McpServerFoundryConnectionAuthentication",
        f"{_IM}.McpServerFoundryConnectionParameters",
        f"{_IM}.McpServerStoredHeadersAuthentication",
        f"{_IM}.McpServerStoredHeadersParameters",
        f"{_IM}.McpServerHeaders",
        f"{_IM}.McpServerTool",
        f"{_IM}.McpServerOutputParsing",
        f"{_IM}.McpServerAutoOutputParsing",
        f"{_IM}.McpServerJsonOutputParsing",
        f"{_IM}.McpServerOutputParsingJsonParameters",
        f"{_IM}.McpServerSplitOutputParsing",
        f"{_IM}.McpServerOutputParsingSplitParameters",
        f"{_IM}.McpServerNoneOutputParsing",
        # Fabric Data Agent / Ontology
        f"{_IM}.FabricDataAgentKnowledgeSource",
        f"{_IM}.FabricDataAgentKnowledgeSourceParameters",
        f"{_IM}.FabricOntologyKnowledgeSource",
        f"{_IM}.FabricOntologyKnowledgeSourceParameters",
        # SharePoint family (re-introduced preview)
        f"{_IM}.IndexedSharePointKnowledgeSource",
        f"{_IM}.IndexedSharePointKnowledgeSourceParameters",
        f"{_IM}.RemoteSharePointKnowledgeSource",
        f"{_IM}.RemoteSharePointKnowledgeSourceParameters",
        # Skills
        f"{_IM}.AzureMachineLearningSkill",
        f"{_IM}.ChatCompletionSkill",
        f"{_IM}.ChatCompletionCommonModelParameters",
        f"{_IM}.ChatCompletionResponseFormat",
        f"{_IM}.ChatCompletionSchema",
        f"{_IM}.ChatCompletionSchemaProperties",
        f"{_IM}.VisionVectorizeSkill",
        # Indexer cache
        f"{_IM}.SearchIndexerCache",
        f"{_IM}.ServiceIndexersRuntime",
        # KB activity / reference / output mode types
        f"{_KBM}.AIServices",
        f"{_KBM}.AssetStore",
        f"{_KBM}.FreshnessPolicy",
        f"{_KBM}.KnowledgeSourceIngestionParameters",
        f"{_KBM}.KnowledgeRetrievalLowReasoningEffort",
        f"{_KBM}.KnowledgeRetrievalMediumReasoningEffort",
        f"{_KBM}.KnowledgeRetrievalOutputMode",
        f"{_KBM}.KnowledgeBaseModelQueryPlanningActivityRecord",
        f"{_KBM}.KnowledgeBaseModelAnswerSynthesisActivityRecord",
        f"{_KBM}.KnowledgeBaseModelWebSummarizationActivityRecord",
        f"{_KBM}.KnowledgeBaseWorkIQReference",
        f"{_KBM}.WorkIQAttribution",
        f"{_KBM}.PurviewSensitivityLabelInfo",
        # Permission filter and option types
        f"{_IM}.SearchIndexPermissionFilterOption",
        f"{_IM}.PermissionFilter",
        # Debug / hybrid / search request types
        f"{_M}.DebugInfo",
        f"{_M}.HybridSearch",
        f"{_M}.QueryResultDocumentRerankerInput",
        f"{_M}.SemanticDebugInfo",
        f"{_M}.DocumentDebugInfo",
    ]
    for dotted in new_classes:
        entries[dotted] = _surface(dotted)

    # New fields on existing models. Key = "<dotted-class>.<field>", owner = dotted-class, kwargs = (field,).
    field_additions = [
        (f"{_IM}.SearchIndex", "cors_options"),
        (f"{_IM}.SearchIndex", "share_point_connector_app_registration"),
        (f"{_IM}.SearchIndex", "permission_filter_option"),
        (f"{_IM}.SearchIndex", "purview_enabled"),
        (f"{_IM}.SearchField", "sensitivity_label_id"),
        (f"{_IM}.SearchField", "sensitivity_label_name"),
        (f"{_IM}.SearchField", "source_document_id"),
        (f"{_IM}.SearchField", "sharepoint_site_url"),
        (f"{_IM}.SearchField", "permission_filter"),
        (f"{_IM}.SearchIndexer", "cache"),
        (f"{_IM}.SearchIndexerDataSourceConnection", "sub_type"),
        (f"{_IM}.SearchIndexerDataSourceConnection", "indexer_permission_options"),
        (f"{_IM}.SearchIndexerStatus", "runtime"),
        (f"{_IM}.SearchIndexerStatus", "current_state"),
        (f"{_IM}.IndexerExecutionResult", "status_detail"),
        (f"{_IM}.IndexerExecutionResult", "mode"),
        (f"{_IM}.SearchIndexerKnowledgeStore", "parameters"),
        (f"{_IM}.McpServerTool", "inclusion_mode"),
        (f"{_IM}.McpServerTool", "max_output_tokens"),
        (f"{_IM}.SearchResourceEncryptionKey", "is_service_level_key"),
        (f"{_IM}.SearchIndexerDataUserAssignedIdentity", "federated_identity_client_id"),
        (f"{_IM}.SemanticConfiguration", "flighting_opt_in"),
        (f"{_IM}.KnowledgeBase", "cors_options"),
        (f"{_IM}.KnowledgeBase", "retrieval_reasoning_effort"),
        (f"{_IM}.KnowledgeBase", "output_mode"),
        (f"{_IM}.KnowledgeBase", "retrieval_instructions"),
        (f"{_IM}.KnowledgeBase", "answer_instructions"),
        (f"{_IM}.KnowledgeSourceReference", "enable_image_serving"),
        (f"{_IM}.KnowledgeSourceReference", "enable_freshness"),
        (f"{_IM}.WebKnowledgeSourceParameters", "language"),
        (f"{_IM}.WebKnowledgeSourceParameters", "market"),
        (f"{_IM}.WebKnowledgeSourceParameters", "count"),
        (f"{_IM}.WebKnowledgeSourceParameters", "freshness"),
        (f"{_IM}.ContentUnderstandingSkillChunkingProperties", "method"),
        (f"{_IM}.ContentUnderstandingSkillChunkingProperties", "unit"),
        (f"{_IM}.SearchServiceCounters", "knowledge_base_counter"),
        (f"{_IM}.SearchServiceCounters", "knowledge_source_counter"),
        (f"{_IM}.SearchServiceStatistics", "indexers_runtime"),
        (f"{_IM}.SplitSkill", "unit"),
        (f"{_IM}.SplitSkill", "azure_open_ai_tokenizer_parameters"),
        (f"{_KBM}.KnowledgeBaseRetrievalRequest", "messages"),
        (f"{_KBM}.KnowledgeBaseRetrievalRequest", "max_output_size"),
        (f"{_KBM}.KnowledgeBaseRetrievalRequest", "retrieval_reasoning_effort"),
        (f"{_KBM}.KnowledgeBaseRetrievalRequest", "output_mode"),
        (f"{_KBM}.KnowledgeBaseRetrievalRequest", "max_output_documents"),
        (f"{_KBM}.KnowledgeBaseAzureBlobReference", "search_sensitivity_label_info"),
        (f"{_KBM}.KnowledgeBaseIndexedOneLakeReference", "search_sensitivity_label_info"),
        (f"{_KBM}.KnowledgeBaseIndexedSharePointReference", "search_sensitivity_label_info"),
        (f"{_KBM}.KnowledgeBaseRemoteSharePointReference", "search_sensitivity_label_info"),
        (f"{_KBM}.KnowledgeBaseSearchIndexReference", "search_sensitivity_label_info"),
        (f"{_KBM}.KnowledgeSourceParams", "always_query_source"),
        (f"{_KBM}.KnowledgeSourceParams", "fail_on_error"),
        (f"{_KBM}.KnowledgeSourceParams", "max_output_documents"),
        (f"{_KBM}.KnowledgeSourceParams", "enable_image_serving"),
        (f"{_KBM}.KnowledgeSourceIngestionParameters", "ai_services"),
        (f"{_KBM}.KnowledgeSourceIngestionParameters", "asset_store"),
        (f"{_KBM}.KnowledgeSourceIngestionParameters", "freshness_policy"),
        (f"{_M}.VectorizableTextQuery", "query_rewrites"),
        (f"{_M}.VectorQuery", "threshold"),
        (f"{_M}.VectorQuery", "filter_override"),
        (f"{_M}.VectorQuery", "per_document_vector_limit"),
        (f"{_M}.HybridSearch", "max_text_recall_size"),
        (f"{_M}.HybridSearch", "count_and_facet_mode"),
        (f"{_M}.FacetResult", "avg"),
        (f"{_M}.FacetResult", "min"),
        (f"{_M}.FacetResult", "max"),
        (f"{_M}.FacetResult", "sum"),
        (f"{_M}.FacetResult", "cardinality"),
        (f"{_M}.FacetResult", "facets"),
        (f"{_M}.DocumentDebugInfo", "inner_hits"),
        (f"{_M}.DocumentDebugInfo", "semantic"),
        (f"{_M}.SemanticDebugInfo", "reranker_input"),
    ]
    for owner, field in field_additions:
        entries[f"{owner}.{field}"] = _surface(owner, kwargs=(field,))

    # Enum member additions: key = enum dotted path + "." + member; owner = enum class; kwargs = (member,).
    enum_additions = [
        (f"{_IM}.AzureOpenAIModelName", "GPT4_O"),
        (f"{_IM}.AzureOpenAIModelName", "GPT4_O_MINI"),
        (f"{_IM}.AzureOpenAIModelName", "GPT41"),
        (f"{_IM}.AzureOpenAIModelName", "GPT41_MINI"),
        (f"{_IM}.AzureOpenAIModelName", "GPT41_NANO"),
        (f"{_IM}.AzureOpenAIModelName", "GPT5"),
        (f"{_IM}.AzureOpenAIModelName", "GPT51"),
        (f"{_IM}.AzureOpenAIModelName", "GPT52"),
        (f"{_IM}.AzureOpenAIModelName", "GPT54"),
        (f"{_IM}.ChatCompletionExtraParametersBehavior", "PASS_THROUGH"),
        (f"{_IM}.ChatCompletionExtraParametersBehavior", "DROP"),
        (f"{_IM}.ChatCompletionExtraParametersBehavior", "ERROR"),
        (f"{_IM}.ChatCompletionResponseFormatType", "TEXT"),
        (f"{_IM}.ChatCompletionResponseFormatType", "JSON_OBJECT"),
        (f"{_IM}.ChatCompletionResponseFormatType", "JSON_SCHEMA"),
        (f"{_IM}.ContentUnderstandingSkillChunkingUnit", "TOKENS"),
        (f"{_IM}.KnowledgeSourceKind", "INDEXED_SQL"),
        (f"{_IM}.KnowledgeSourceKind", "REMOTE_SHARE_POINT"),
        (f"{_IM}.KnowledgeSourceKind", "WORK_IQ"),
        (f"{_IM}.KnowledgeSourceKind", "FILE"),
        (f"{_IM}.KnowledgeSourceKind", "MCP_SERVER"),
        (f"{_IM}.KnowledgeSourceKind", "FABRIC_DATA_AGENT"),
        (f"{_IM}.KnowledgeSourceKind", "FABRIC_ONTOLOGY"),
        (f"{_IM}.McpServerAuthenticationKind", "FOUNDRY_CONNECTION"),
        (f"{_IM}.McpServerAuthenticationKind", "STORED_HEADERS"),
        (f"{_IM}.McpServerToolInclusionMode", "RERANKED"),
        (f"{_IM}.McpServerToolInclusionMode", "ALWAYS"),
        (f"{_KBM}.KnowledgeBaseActivityRecordType", "WORK_IQ"),
        (f"{_KBM}.KnowledgeBaseActivityRecordType", "FABRIC_DATA_AGENT"),
        (f"{_KBM}.KnowledgeBaseActivityRecordType", "FABRIC_ONTOLOGY"),
        (f"{_KBM}.KnowledgeBaseActivityRecordType", "MODEL_WEB_SUMMARIZATION"),
        (f"{_KBM}.KnowledgeBaseReferenceType", "WORK_IQ"),
        (f"{_KBM}.KnowledgeBaseReferenceType", "FABRIC_DATA_AGENT"),
        (f"{_KBM}.KnowledgeBaseReferenceType", "FABRIC_ONTOLOGY"),
        (f"{_IM}.KnowledgeSourceIngestionPermissionOption", "SENSITIVITY_LABELS"),
        (f"{_IM}.McpServerOutputParsingKind", "AUTO"),
        (f"{_IM}.McpServerOutputParsingKind", "JSON"),
        (f"{_IM}.McpServerOutputParsingKind", "SPLIT"),
        (f"{_IM}.McpServerOutputParsingKind", "NONE"),
        (f"{_IM}.SplitSkillUnit", "AZURE_OPEN_AI_TOKENS"),
    ]
    for owner, member in enum_additions:
        entries[f"{owner}.{member}"] = _surface(owner, kwargs=(member,))

    return entries


def _client_capabilities() -> Mapping[str, Mapping[str, Any]]:
    entries: dict = {}
    # Sync clients.
    method_existence = [
        f"{_IDX}.SearchIndexerClient.resync",
        f"{_IDX}.SearchIndexerClient.reset_documents",
        f"{_IDX}.SearchIndexerClient.reset_skills",
        f"{_IDX}.SearchIndexClient.list_index_stats_summary",
        f"{_IDX}.aio.SearchIndexerClient.resync",
        f"{_IDX}.aio.SearchIndexerClient.reset_documents",
        f"{_IDX}.aio.SearchIndexerClient.reset_skills",
        f"{_IDX}.aio.SearchIndexClient.list_index_stats_summary",
    ]
    for dotted in method_existence:
        entries[dotted] = _surface(dotted)

    method_kwargs = [
        (
            f"{_IDX}.SearchIndexerClient.create_or_update_data_source_connection",
            ("skip_indexer_reset_requirement_for_cache",),
        ),
        (
            f"{_IDX}.SearchIndexerClient.create_or_update_indexer",
            ("skip_indexer_reset_requirement_for_cache", "disable_cache_reprocessing_change_detection"),
        ),
        (
            f"{_IDX}.SearchIndexerClient.create_or_update_skillset",
            ("skip_indexer_reset_requirement_for_cache", "disable_cache_reprocessing_change_detection"),
        ),
        (f"{_IDX}.SearchIndexClient.list_indexes", ("top", "skip", "count")),
        (f"{_IDX}.SearchIndexClient.list_index_names", ("top", "skip", "count")),
        (
            f"{_IDX}.aio.SearchIndexerClient.create_or_update_data_source_connection",
            ("skip_indexer_reset_requirement_for_cache",),
        ),
        (
            f"{_IDX}.aio.SearchIndexerClient.create_or_update_indexer",
            ("skip_indexer_reset_requirement_for_cache", "disable_cache_reprocessing_change_detection"),
        ),
        (
            f"{_IDX}.aio.SearchIndexerClient.create_or_update_skillset",
            ("skip_indexer_reset_requirement_for_cache", "disable_cache_reprocessing_change_detection"),
        ),
        (f"{_IDX}.aio.SearchIndexClient.list_indexes", ("top", "skip", "count")),
        (f"{_IDX}.aio.SearchIndexClient.list_index_names", ("top", "skip", "count")),
    ]
    for dotted, kwargs in method_kwargs:
        for kw in kwargs:
            entries[f"{dotted}.{kw}"] = _surface(dotted, kwargs=(kw,))
    return entries


_CAPS: dict = {
    "SearchClient.search.query_rewrites": _surface("azure.search.documents.SearchClient.search", ("query_rewrites",)),
    "SearchClient.search.hybrid_search": _surface("azure.search.documents.SearchClient.search", ("hybrid_search",)),
    "SearchClient.search.semantic_fields": _surface("azure.search.documents.SearchClient.search", ("semantic_fields",)),
    "SearchClient.search.query_language": _surface("azure.search.documents.SearchClient.search", ("query_language",)),
    "SearchClient.search.speller": _surface("azure.search.documents.SearchClient.search", ("speller",)),
    "SearchClient.search.enable_elevated_read": _surface(
        "azure.search.documents.SearchClient.search", ("enable_elevated_read",)
    ),
    "SearchClient.search.query_source_authorization": _surface(
        "azure.search.documents.SearchClient.search", ("query_source_authorization",)
    ),
    "SearchItemPaged.get_debug_info": _surface("azure.search.documents.SearchItemPaged", ("get_debug_info",)),
    "KnowledgeBaseRetrievalClient": _surface("azure.search.documents.knowledgebases.KnowledgeBaseRetrievalClient"),
    "KnowledgeBaseRetrievalClient.aio": _surface(
        "azure.search.documents.knowledgebases.aio.KnowledgeBaseRetrievalClient"
    ),
}
_CAPS.update(_model_capabilities())
_CAPS.update(_client_capabilities())

CAPABILITIES: Mapping[str, Mapping[str, Any]] = _CAPS


def _resolve(dotted: str) -> Any:
    parts = dotted.split(".")
    for i in range(len(parts), 0, -1):
        try:
            module = importlib.import_module(".".join(parts[:i]))
        except ImportError:
            continue
        obj: Any = module
        for name in parts[i:]:
            obj = getattr(obj, name)
        return obj
    raise ImportError(f"Could not resolve {dotted!r}")


def _has_capability_attr(owner: Any, name: str) -> bool:
    """Detect a capability attribute on a function, enum, or model class."""
    # Method/function signature parameters.
    try:
        if name in inspect.signature(owner).parameters:
            return True
    except (TypeError, ValueError):
        pass
    # Enum member.
    if isinstance(owner, type) and issubclass(owner, enum.Enum):
        return name in owner.__members__
    # Model class: walk MRO for rest_field descriptors.
    if isinstance(owner, type):
        for cls in owner.__mro__:
            descriptor = vars(cls).get(name)
            if descriptor is not None and "RestField" in type(descriptor).__name__:
                return True
        if hasattr(owner, name):
            return True
    return False


def require_capability(*names: str) -> None:
    for name in names:
        try:
            cap = CAPABILITIES[name]
        except KeyError:  # pragma: no cover - misuse
            raise KeyError(f"Unknown capability {name!r}")
        try:
            owner = _resolve(cap["owner"])
        except (ImportError, AttributeError) as exc:
            pytest.skip(f"{name} unavailable: owner {cap['owner']!r} cannot be resolved ({exc})")
        if not cap["kwargs"]:
            # Existence of owner is the capability.
            continue
        missing = [k for k in cap["kwargs"] if not _has_capability_attr(owner, k)]
        if missing:
            pytest.skip(f"{name} unavailable: missing {missing}")

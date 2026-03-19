"""Phase E Part B export-surface contract tests."""

from __future__ import annotations

import importlib


def test_phase_e_exports__all_contains_only_public_symbols() -> None:
    responses = importlib.import_module("azure.ai.agentserver.responses")

    expected = [
        "ResponseHandler",
        "ResponseContext",
        "RuntimeResponseContext",
        "ResponsesServerOptions",
        "ResponseProviderProtocol",
        "InMemoryResponseProvider",
        "TextContentBuilder",
        "OutputItemMessageBuilder",
        "OutputItemBuilder",
        "OutputItemFunctionCallBuilder",
        "OutputItemFunctionCallOutputBuilder",
        "RefusalContentBuilder",
        "OutputItemReasoningItemBuilder",
        "ReasoningSummaryPartBuilder",
        "OutputItemFileSearchCallBuilder",
        "OutputItemWebSearchCallBuilder",
        "OutputItemCodeInterpreterCallBuilder",
        "OutputItemImageGenCallBuilder",
        "OutputItemMcpCallBuilder",
        "OutputItemMcpListToolsBuilder",
        "OutputItemCustomToolCallBuilder",
        "ResponseEventStream",
    ]

    assert responses.__all__ == expected


def test_phase_e_exports__symbols_are_importable_from_top_level() -> None:
    responses = importlib.import_module("azure.ai.agentserver.responses")

    for name in responses.__all__:
        assert hasattr(responses, name)


def test_phase_e_exports__star_import_exposes_only_declared_symbols() -> None:
    namespace: dict[str, object] = {}
    exec("from azure.ai.agentserver.responses import *", {}, namespace)

    exported = {key for key in namespace.keys() if not key.startswith("__")}
    assert exported == {
        "ResponseHandler",
        "ResponseContext",
        "RuntimeResponseContext",
        "ResponsesServerOptions",
        "ResponseProviderProtocol",
        "InMemoryResponseProvider",
        "TextContentBuilder",
        "OutputItemMessageBuilder",
        "OutputItemBuilder",
        "OutputItemFunctionCallBuilder",
        "OutputItemFunctionCallOutputBuilder",
        "RefusalContentBuilder",
        "OutputItemReasoningItemBuilder",
        "ReasoningSummaryPartBuilder",
        "OutputItemFileSearchCallBuilder",
        "OutputItemWebSearchCallBuilder",
        "OutputItemCodeInterpreterCallBuilder",
        "OutputItemImageGenCallBuilder",
        "OutputItemMcpCallBuilder",
        "OutputItemMcpListToolsBuilder",
        "OutputItemCustomToolCallBuilder",
        "ResponseEventStream",
    }

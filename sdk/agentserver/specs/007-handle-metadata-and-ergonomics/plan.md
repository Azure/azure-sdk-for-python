# Implementation Plan: Handle Operations & API Ergonomics

**Branch**: `007-handle-metadata-and-ergonomics` | **Date**: 2026-05-12 | **Spec**: `specs/007-handle-metadata-and-ergonomics/spec.md`  
**Input**: Feature specification from `/specs/007-handle-metadata-and-ergonomics/spec.md`

## Summary

Four backlog items scoped for this spec. Upon investigation, **three are already implemented**:

| # | Feature | Status |
|---|---------|--------|
| 13 | `handle.metadata` snapshot read | ✅ Already on `TaskRun` as a `metadata` property returning `TaskMetadata` + `refresh()` to pull from store |
| 14 | `handle.delete()` | ✅ Already on `TaskRun` with `_provider.delete()` call |
| 15 | `fn.__qualname__` default | ✅ Already uses `func.__qualname__` in `_decorator.py:675` |
| 16 | Dict-like `TaskMetadata` | ❌ **Not yet implemented** — only has method-based API |

**Only item 16 requires implementation.** Add `MutableMapping` protocol support to `TaskMetadata`.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: `azure-ai-agentserver-core` (durable module)  
**Testing**: pytest with pytest-asyncio, existing test_metadata.py  
**Project Type**: Library  
**Constraints**: Python 3.10 compatibility, no new dependencies

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| II. Strong Type Safety | ✅ PASS | `MutableMapping[str, Any]` is precise |
| III. Azure SDK Compliance | ✅ PASS | Standard Python protocol |
| VII. Minimal Surface | ✅ PASS | Adding standard dict protocol to existing class |

## Source Changes

```text
azure-ai-agentserver-core/azure/ai/agentserver/core/durable/
└── _metadata.py         # Add __setitem__, __getitem__, __delitem__, __iter__, __len__, __contains__, keys(), values(), items()

azure-ai-agentserver-core/tests/durable/
└── test_metadata.py     # Add tests for dict protocol
```

## Architecture

`TaskMetadata` will register as a `MutableMapping` via `collections.abc.MutableMapping.register()` rather than inheriting, since it has custom methods (`increment`, `append`, `flush`) that don't exist on `MutableMapping`. The dict protocol methods delegate to `self._data` with dirty-tracking on mutations.

## Complexity Tracking

No constitution violations.

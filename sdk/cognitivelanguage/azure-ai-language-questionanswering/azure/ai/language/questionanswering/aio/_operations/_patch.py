# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Async customization hooks for operations.

Adds client-side ``TypeError`` validation for method overload misuse & required fields.
Mirrors synchronous patch to keep behavior consistent across sync/async clients.
"""

from __future__ import annotations

from io import IOBase
from typing import Any, Mapping, MutableMapping

from ._operations import _QuestionAnsweringClientOperationsMixin as _GeneratedOpsMixin

__all__: list[str] = []


def _getattr(obj: Any, name: str, default: Any = None) -> Any:
    try:
        return getattr(obj, name)
    except AttributeError:
        return default


def _as_mapping(payload: Any):  # type: ignore[override]
    if isinstance(payload, Mapping):
        return payload
    if isinstance(payload, MutableMapping):  # pragma: no cover
        return payload
    return None


def _validate_get_answers_payload(options: Any) -> None:
    if isinstance(options, (IOBase, bytes)):
        return
    mapping = _as_mapping(options)
    if mapping is not None:
        qna_id = mapping.get("qnaId") or mapping.get("qna_id")
        question = mapping.get("question")
    else:
        qna_id = _getattr(options, "qna_id")
        question = _getattr(options, "question")
    if not (qna_id is not None or question):
        raise TypeError("Either 'question' or 'qna_id' must be provided in AnswersOptions.")


def _validate_get_answers_from_text_payload(options: Any) -> None:
    if isinstance(options, (IOBase, bytes)):
        return
    mapping = _as_mapping(options)
    if mapping is not None:
        question = mapping.get("question")
        records = mapping.get("records") or mapping.get("text_documents")
    else:
        question = _getattr(options, "question")
        records = _getattr(options, "text_documents")
    if not question:
        raise TypeError("'question' is required in AnswersFromTextOptions.")
    if not isinstance(records, list) or not records:
        raise TypeError("A non-empty 'records' (text_documents) list is required in AnswersFromTextOptions.")


def _patch_async_methods() -> None:
    if getattr(_GeneratedOpsMixin, "_qa_validation_patched", False):  # pragma: no cover
        return
    original_get_answers = _GeneratedOpsMixin.get_answers
    original_get_answers_from_text = _GeneratedOpsMixin.get_answers_from_text

    async def get_answers(self, knowledge_base_query_options: Any, *, project_name: str, deployment_name: str, **kwargs: Any):  # type: ignore[override]
        _validate_get_answers_payload(knowledge_base_query_options)
        return await original_get_answers(self, knowledge_base_query_options, project_name=project_name, deployment_name=deployment_name, **kwargs)

    async def get_answers_from_text(self, text_query_options: Any, **kwargs: Any):  # type: ignore[override]
        _validate_get_answers_from_text_payload(text_query_options)
        return await original_get_answers_from_text(self, text_query_options, **kwargs)

    _GeneratedOpsMixin.get_answers = get_answers  # type: ignore[assignment]
    _GeneratedOpsMixin.get_answers_from_text = get_answers_from_text  # type: ignore[assignment]
    _GeneratedOpsMixin._qa_validation_patched = True  # type: ignore[attr-defined]


def patch_sdk():
    _patch_async_methods()


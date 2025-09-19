# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customization hooks for operations.

Adds light-weight parameter validation so that misuse raises ``TypeError`` *before* any
network call is attempted. This mirrors prior SDK behavior and enables the tests that
assert client-side ``TypeError`` for malformed calls (rather than connection or
service errors). Keep the exception type as ``TypeError`` per user request.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from __future__ import annotations

from io import IOBase
from typing import Any, Mapping, MutableMapping, Union, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .. import models as _models

from ._operations import _QuestionAnsweringClientOperationsMixin as _GeneratedOpsMixin

__all__: list[str] = []  # exported symbols (none for now)


def _getattr(obj: Any, name: str, default: Any = None) -> Any:
    try:
        return getattr(obj, name)
    except AttributeError:
        return default


def _as_mapping(payload: Any) -> Mapping[str, Any] | None:
    if isinstance(payload, Mapping):  # dict-like already
        return payload  # type: ignore[return-value]
    # Generated model instances are also Mapping subclasses (MutableMapping)
    if isinstance(payload, MutableMapping):  # pragma: no cover (defensive)
        return payload  # type: ignore[return-value]
    return None


def _validate_get_answers_payload(options: Any) -> None:
    """Ensure an AnswersOptions-like object contains either qna_id or question.

    Raises
    ------
    TypeError
        If neither *qna_id* nor *question* are supplied or both are empty.
    """
    if isinstance(options, (IOBase, bytes)):
        # Raw stream payload, skip structural validation (assume caller knows schema)
        return

    mapping = _as_mapping(options)
    if mapping is not None:
        qna_id = mapping.get("qnaId") or mapping.get("qna_id")
        question = mapping.get("question")
    else:
        # Model instance or arbitrary object
        qna_id = _getattr(options, "qna_id")
        question = _getattr(options, "question")

    has_qna_id = qna_id is not None
    has_question = bool(question)
    if not (has_qna_id or has_question):  # keep TypeError (requested) instead of ValueError
        raise TypeError("Either 'question' or 'qna_id' must be provided in AnswersOptions.")


def _validate_get_answers_from_text_payload(options: Any) -> None:
    """Ensure AnswersFromTextOptions-like payload contains required fields.

    Required: question (non-empty str), records/text_documents (non-empty list).
    Raises TypeError on violation (per requirement to keep existing TypeError semantics).
    """
    if isinstance(options, (IOBase, bytes)):
        return

    mapping = _as_mapping(options)
    if mapping is not None:
        question = mapping.get("question")
        # Accept either wire name 'records' or convenience 'text_documents'
        records = mapping.get("records") or mapping.get("text_documents")
    else:
        question = _getattr(options, "question")
        records = _getattr(options, "text_documents")

    if not question:
        raise TypeError("'question' is required in AnswersFromTextOptions.")
    if not isinstance(records, list) or not records:
        raise TypeError("A non-empty 'records' (text_documents) list is required in AnswersFromTextOptions.")


def _patch_sync_methods() -> None:
    # Guard to avoid double patching if patch_sdk called multiple times
    if getattr(_GeneratedOpsMixin, "_qa_validation_patched", False):  # pragma: no cover
        return

    original_get_answers = _GeneratedOpsMixin.get_answers
    original_get_answers_from_text = _GeneratedOpsMixin.get_answers_from_text

    def get_answers(self, knowledge_base_query_options: Any, *, project_name: str, deployment_name: str, **kwargs: Any):  # type: ignore[override]
        _validate_get_answers_payload(knowledge_base_query_options)
        return original_get_answers(self, knowledge_base_query_options, project_name=project_name, deployment_name=deployment_name, **kwargs)

    def get_answers_from_text(self, text_query_options: Any, **kwargs: Any):  # type: ignore[override]
        _validate_get_answers_from_text_payload(text_query_options)
        return original_get_answers_from_text(self, text_query_options, **kwargs)

    # Monkey patch methods
    _GeneratedOpsMixin.get_answers = get_answers  # type: ignore[assignment]
    _GeneratedOpsMixin.get_answers_from_text = get_answers_from_text  # type: ignore[assignment]
    _GeneratedOpsMixin._qa_validation_patched = True  # type: ignore[attr-defined]


def patch_sdk():  # noqa: D401 - short doc retained for consistency
    """Apply runtime customizations (idempotent)."""
    _patch_sync_methods()


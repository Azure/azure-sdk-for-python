# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""


from typing import Any, List, overload, Optional, Union, Tuple, cast, MutableMapping, IO
import copy
from azure.core.tracing.decorator import distributed_trace

from ._operations import QuestionAnsweringOperations as QuestionAnsweringOperationsGenerated  # type: ignore
from .. import models as _models  # type: ignore

JSON = MutableMapping[str, Any]


def _get_positional_body(*args, **kwargs):
    if len(args) > 1:
        raise TypeError("There can only be one positional argument, which is the POST body of this request.")
    if "options" in kwargs:
        raise TypeError("The 'options' parameter is positional only.")
    return args[0] if args else None


def _verify_qna_id_and_question(query_options):
    try:
        qna_id = getattr(query_options, "qna_id", None)
        question = getattr(query_options, "question", None)
    except AttributeError:  # pragma: no cover
        qna_id = None
        question = None
    if not (qna_id or question):
        raise TypeError("You need to pass in either `qna_id` or `question`.")
    if qna_id and question:
        raise TypeError("You can not specify both `qna_id` and `question`.")


def _handle_metadata_filter_conversion(options_input):
    options = copy.deepcopy(options_input)
    filters = getattr(options, "filters", None)
    try:
        if filters and getattr(filters, "metadata_filter", None) and filters.metadata_filter.metadata:
            metadata_input = filters.metadata_filter.metadata
        else:
            metadata_input = None
        in_class = True
    except AttributeError:
        metadata_input = None
        in_class = False
    if not metadata_input:
        return options
    # If items already look like model objects (have .key/.value) or dicts with those keys, leave as-is
    already_structured = all(
        (hasattr(m, "key") and hasattr(m, "value")) or (isinstance(m, dict) and "key" in m and "value" in m)
        for m in metadata_input
    )
    if already_structured:
        return options
    # Otherwise expect sequence of 2-length iterables (tuples/lists)
    try:
        tuple_like = []
        for item in metadata_input:  # type: ignore
            if not hasattr(item, "__len__") or len(item) != 2:  # type: ignore[arg-type]
                raise ValueError("'metadata' must be provided either as model objects or 2-item tuples.")
            tuple_like.append(item)
        metadata_modified = [{"key": t[0], "value": t[1]} for t in tuple_like]
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError("'metadata' must be a sequence of (key, value) tuples or MetadataRecord objects.") from exc
    if in_class:
        filters.metadata_filter.metadata = metadata_modified  # type: ignore[attr-defined]
    return options


def _get_answers_prepare_options(*args: _models.AnswersOptions, **kwargs: Any) -> Tuple[_models.AnswersOptions, Any]:
    options = _get_positional_body(*args, **kwargs) or _models.AnswersOptions(
        qna_id=kwargs.pop("qna_id", None),
        question=kwargs.pop("question", None),
        top=kwargs.pop("top", None),
        user_id=kwargs.pop("user_id", None),
        confidence_threshold=kwargs.pop("confidence_threshold", None),
        answer_context=kwargs.pop("answer_context", None),
        ranker_kind=kwargs.pop("ranker_kind", None),
        filters=kwargs.pop("filters", None),
        short_answer_options=kwargs.pop("short_answer_options", None),
        include_unstructured_sources=kwargs.pop("include_unstructured_sources", None),
    )
    _verify_qna_id_and_question(options)
    return _handle_metadata_filter_conversion(options), kwargs


def _validate_text_records(records):
    if not records:
        raise ValueError("Input documents can not be empty or None")
    if isinstance(records, str):
        raise TypeError("Input documents cannot be a string.")
    if isinstance(records, dict):
        raise TypeError("Input documents cannot be a dict")
    if not all(isinstance(x, str) for x in records):
        if not all(isinstance(x, (dict, _models.TextDocument)) for x in records):
            raise TypeError("Mixing string and dictionary/object document input unsupported.")
    batch = []
    for idx, doc in enumerate(records):
        if isinstance(doc, str):
            batch.append({"id": str(idx), "text": doc})
        else:
            batch.append(doc)
    return batch


def _get_answers_from_text_prepare_options(
    *args: _models.AnswersFromTextOptions, **kwargs: Any
) -> Tuple[Union[JSON, _models.AnswersFromTextOptions], Any]:
    default_language = kwargs.pop("language", None)
    options = _get_positional_body(*args, **kwargs) or _models.AnswersFromTextOptions(
        question=kwargs.pop("question"),
        text_documents=kwargs.pop("text_documents"),
        language=default_language,
    )
    try:
        options = cast(JSON, options)
        options["records"] = _validate_text_records(options["records"])  # type: ignore[index]
        options["language"] = options.get("language", None) or default_language
    except TypeError:
        options = cast(_models.AnswersFromTextOptions, options)
        options.text_documents = _validate_text_records(options.text_documents)
        options.language = options.language or default_language
    return options, kwargs


class QuestionAnsweringOperations(QuestionAnsweringOperationsGenerated):  # type: ignore
    # ----- get_answers overloads (match base) -----
    @overload
    def get_answers(  # type: ignore[override]
        self,
        knowledge_base_query_options: _models.AnswersOptions,
        *,
        project_name: str,
        deployment_name: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.AnswersResult: ...

    @overload
    def get_answers(  # type: ignore[override]
        self,
        knowledge_base_query_options: JSON,
        *,
        project_name: str,
        deployment_name: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.AnswersResult: ...

    @overload
    def get_answers(  # type: ignore[override]
        self,
        knowledge_base_query_options: IO[bytes],
        *,
        project_name: str,
        deployment_name: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.AnswersResult: ...

    # ----- flattened convenience overload (extra) -----
    @overload
    def get_answers(  # pylint: disable=arguments-differ
        self,
        *,
        project_name: str,
        deployment_name: str,
        qna_id: Optional[int] = None,
        question: Optional[str] = None,
        top: Optional[int] = None,
        user_id: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        answer_context: Optional[_models.KnowledgeBaseAnswerContext] = None,
        ranker_kind: Optional[str] = None,
        filters: Optional[_models.QueryFilters] = None,
        short_answer_options: Optional[_models.ShortAnswerOptions] = None,
        include_unstructured_sources: Optional[bool] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.AnswersResult: ...
    # (Implementation below remains unchanged.)

    @distributed_trace
    def get_answers(  # type: ignore[override]
        self,
        *args: _models.AnswersOptions,
        **kwargs: Any,
    ) -> _models.AnswersResult:
        options, kwargs = _get_answers_prepare_options(*args, **kwargs)
        return super().get_answers(options, **kwargs)  # type: ignore

    # ----- get_answers_from_text overloads (match base) -----
    @overload
    def get_answers_from_text(  # type: ignore[override]
        self,
        text_query_options: _models.AnswersFromTextOptions,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.AnswersFromTextResult: ...

    @overload
    def get_answers_from_text(  # type: ignore[override]
        self,
        text_query_options: JSON,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.AnswersFromTextResult: ...

    @overload
    def get_answers_from_text(  # type: ignore[override]
        self,
        text_query_options: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.AnswersFromTextResult: ...

    # ----- flattened convenience overload (extra) -----
    @overload
    def get_answers_from_text(  # pylint: disable=arguments-differ
        self,
        *,
        question: str,
        text_documents: List[Union[str, _models.TextDocument]],
        language: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.AnswersFromTextResult: ...

    @distributed_trace
    def get_answers_from_text(  # type: ignore[override]
        self,
        *args: _models.AnswersFromTextOptions,
        **kwargs: Any,
    ) -> _models.AnswersFromTextResult:
        if args and (len(args) == 1) and not kwargs.get("question"):
            body = args[0]
            try:
                if isinstance(body, _models.AnswersFromTextOptions):
                    body.text_documents = _validate_text_records(body.text_documents)  # type: ignore[attr-defined]
            except (AttributeError, TypeError, ValueError):  # pragma: no cover
                pass
            return super().get_answers_from_text(body, **kwargs)  # type: ignore
        options, kwargs = _get_answers_from_text_prepare_options(*args, **kwargs)
        return super().get_answers_from_text(options, **kwargs)  # type: ignore

__all__: List[str] = ["QuestionAnsweringOperations"]

def patch_sdk():  # noqa: D401
    """Retained for compatibility; operations class already patched via subclassing."""
    return None

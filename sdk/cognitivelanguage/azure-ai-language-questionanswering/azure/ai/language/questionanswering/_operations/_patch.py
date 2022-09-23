# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, List, overload, Optional, Union, Dict, Tuple
import six
import copy
from azure.core.tracing.decorator import distributed_trace

from ._operations import QuestionAnsweringClientOperationsMixin as QuestionAnsweringClientOperationsMixinGenerated
from ..models import AnswersOptions, AnswersResult, TextDocument, AnswersFromTextOptions, AnswersFromTextResult


def _validate_text_records(records):
    if not records:
        raise ValueError("Input documents can not be empty or None")
    if isinstance(records, six.string_types):
        raise TypeError("Input documents cannot be a string.")
    if isinstance(records, dict):
        raise TypeError("Input documents cannot be a dict")
    if not all(isinstance(x, six.string_types) for x in records):
        if not all(isinstance(x, (dict, TextDocument)) for x in records):
            raise TypeError("Mixing string and dictionary/object document input unsupported.")
    request_batch = []
    for idx, doc in enumerate(records):
        if isinstance(doc, six.string_types):
            record = {"id": str(idx), "text": doc}
            request_batch.append(record)
        else:
            request_batch.append(doc)
    return request_batch


def _get_positional_body(*args, **kwargs):
    """Verify args and kwargs are valid, and then return the positional body, if users passed it in."""
    if len(args) > 1:
        raise TypeError("There can only be one positional argument, which is the POST body of this request.")
    if "options" in kwargs:
        raise TypeError("The 'options' parameter is positional only.")
    return args[0] if args else None


def _verify_qna_id_and_question(query_knowledgebase_options):
    """For query_knowledge_base we require either `question` or `qna_id`."""
    try:
        qna_id = query_knowledgebase_options.qna_id
        question = query_knowledgebase_options.question
    except AttributeError:
        qna_id = query_knowledgebase_options.get("qna_id") or query_knowledgebase_options.get("qnaId")
        question = query_knowledgebase_options.get("question")
    if not (qna_id or question):
        raise TypeError("You need to pass in either `qna_id` or `question`.")
    if qna_id and question:
        raise TypeError("You can not specify both `qna_id` and `question`.")


def _handle_metadata_filter_conversion(options_input):
    options = copy.deepcopy(options_input)
    filters = options.filters if hasattr(options, "filters") else options.get("filters", {})
    try:
        if filters and filters.metadata_filter and filters.metadata_filter.metadata:
            metadata_input = filters.metadata_filter.metadata
        else:
            metadata_input = None
        in_class = True
    except AttributeError:
        metadata_input = filters.get("metadataFilter", {}).get("metadata")
        in_class = False
    if not metadata_input:
        return options
    try:
        if any(t for t in metadata_input if len(t) != 2):
            raise ValueError("'metadata' must be a sequence of key-value tuples.")
    except TypeError:
        raise ValueError("'metadata' must be a sequence of key-value tuples.")
    metadata_modified = [{"key": m[0], "value": m[1]} for m in metadata_input]
    if in_class:
        filters.metadata_filter.metadata = metadata_modified
    else:
        filters["metadataFilter"]["metadata"] = metadata_modified
    return options


def _get_answers_prepare_options(*args: AnswersOptions, **kwargs: Any) -> Tuple[AnswersOptions, Any]:
    options = _get_positional_body(*args, **kwargs) or AnswersOptions(
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


def _get_answers_from_text_prepare_options(
    *args: AnswersFromTextOptions, **kwargs: Any
) -> Tuple[AnswersFromTextOptions, Any]:
    options = _get_positional_body(*args, **kwargs) or AnswersFromTextOptions(
        question=kwargs.pop("question"),
        text_documents=kwargs.pop("text_documents"),
        language=kwargs.pop("language"),
    )
    try:
        options["records"] = _validate_text_records(options["records"])
    except TypeError:
        options.text_documents = _validate_text_records(options.text_documents)
    kwargs.pop("language", None)
    return options, kwargs


class QuestionAnsweringClientOperationsMixin(QuestionAnsweringClientOperationsMixinGenerated):
    @overload
    def get_answers(self, options: AnswersOptions, **kwargs: Any) -> AnswersResult:
        pass

    @overload
    def get_answers(self, **kwargs: Any) -> AnswersResult:
        pass

    @distributed_trace
    def get_answers(self, *args: AnswersOptions, **kwargs: Any) -> AnswersResult:
        """Answers the specified question using your knowledge base.

        :param options: Positional only. POST body of the request. Provide either `options`, OR
         individual keyword arguments. If both are provided, only the options object will be used.
        :type options: ~azure.ai.language.questionanswering.AnswersOptions
        :keyword project_name: The name of the knowledge base project to use.
        :paramtype project_name: str
        :keyword deployment_name: The name of the specific deployment of the project to use.
        :paramtype deployment_name: str
        :keyword qna_id: Exact QnA ID to fetch from the knowledge base, this field takes priority over
         question.
        :paramtype qna_id: int
        :keyword question: User question to query against the knowledge base.
        :paramtype question: str
        :keyword top: Max number of answers to be returned for the question.
        :paramtype top: int
        :keyword user_id: Unique identifier for the user.
        :paramtype user_id: str
        :keyword confidence_threshold: Minimum threshold score for answers, value ranges from 0 to 1.
        :paramtype confidence_threshold: float
        :keyword answer_context: Context object with previous QnA's information.
        :paramtype answer_context: ~azure.ai.language.questionanswering.KnowledgeBaseAnswerContext
        :keyword ranker_kind: Type of ranker to be used. Possible
         values include: "Default", "QuestionOnly".
        :paramtype ranker_kind: str
        :keyword filters: Filter QnAs based on given metadata list and knowledge base sources.
        :paramtype filters: ~azure.ai.language.questionanswering.QueryFilters
        :keyword short_answer_options: To configure Answer span prediction feature.
        :paramtype short_answer_options: ~azure.ai.language.questionanswering.ShortAnswerOptions
        :keyword include_unstructured_sources: (Optional) Flag to enable Query over Unstructured
         Sources.
        :paramtype include_unstructured_sources: bool
        :return: AnswersResult
        :rtype: ~azure.ai.language.questionanswering.AnswersResult
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        options, kwargs = _get_answers_prepare_options(*args, **kwargs)
        return super().get_answers(options, **kwargs)

    @overload
    def get_answers_from_text(self, options: AnswersFromTextOptions, **kwargs: Any) -> AnswersFromTextResult:
        pass

    @overload
    def get_answers_from_text(self, **kwargs: Any) -> AnswersFromTextResult:
        pass

    @distributed_trace
    def get_answers_from_text(self, *args: AnswersFromTextOptions, **kwargs: Any) -> AnswersFromTextResult:
        """Answers the specified question using the provided text in the body.

        :param options: Positional only. POST body of the request. Provide either `options`, OR
         individual keyword arguments. If both are provided, only the options object will be used.
        :type options: ~azure.ai.language.questionanswering.models.AnswersFromTextOptions
        :keyword question: User question to query against the given text records.
        :paramtype question: str
        :keyword text_documents: Text records to be searched for given question.
        :paramtype text_documents: list[str or ~azure.ai.language.questionanswering.models.TextDocument]
        :keyword language: Language of the text records. This is BCP-47 representation of a language.
         For example, use "en" for English; "es" for Spanish etc. If not set, use "en" for English as
         default.
        :paramtype language: str
        :return: AnswersFromTextResult
        :rtype: ~azure.ai.language.questionanswering.models.AnswersFromTextResult
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        options, kwargs = _get_answers_from_text_prepare_options(
            *args, language=kwargs.pop("language", self._default_language), **kwargs
        )
        return super().get_answers_from_text(options, **kwargs)


__all__: List[str] = [
    "QuestionAnsweringClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

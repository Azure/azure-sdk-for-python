# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, List, overload, Optional, Union, Tuple, cast, MutableMapping
import copy
from azure.core.tracing.decorator import distributed_trace

from ._operations import QuestionAnsweringClientOperationsMixin as QuestionAnsweringClientOperationsMixinGenerated
from ..models import (
    AnswersOptions,
    AnswersFromTextOptions,
    AnswersResult,
    AnswersFromTextResult,
    KnowledgeBaseAnswerContext,
    QueryFilters,
    ShortAnswerOptions,
    TextDocument,
)

JSON = MutableMapping[str, Any]


def _validate_text_records(records):
    if not records:
        raise ValueError("Input documents can not be empty or None")
    if isinstance(records, str):
        raise TypeError("Input documents cannot be a string.")
    if isinstance(records, dict):
        raise TypeError("Input documents cannot be a dict")
    if not all(isinstance(x, str) for x in records):
        if not all(isinstance(x, (dict, TextDocument)) for x in records):
            raise TypeError("Mixing string and dictionary/object document input unsupported.")
    request_batch = []
    for idx, doc in enumerate(records):
        if isinstance(doc, str):
            record = {"id": str(idx), "text": doc}
            request_batch.append(record)
        else:
            request_batch.append(doc)
    return request_batch


def _get_positional_body(*args, **kwargs):
    """Verify args and kwargs are valid, and then return the positional body, if users passed it in.

    :param args: The arguments passed to the method.
    :type args: AnswersOptions or dict
    """
    if len(args) > 1:
        raise TypeError("There can only be one positional argument, which is the POST body of this request.")
    if "options" in kwargs:
        raise TypeError("The 'options' parameter is positional only.")
    return args[0] if args else None


def _verify_qna_id_and_question(query_knowledgebase_options):
    """For query_knowledge_base we require either `question` or `qna_id`.

    :param query_knowledgebase_options: The user-passed AnswersOptions or dict
    :type query_knowledgebase_options: AnswersOptions or dict
    """
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
    except TypeError as exc:
        raise ValueError("'metadata' must be a sequence of key-value tuples.") from exc
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
) -> Tuple[Union[JSON, AnswersFromTextOptions], Any]:
    default_language = kwargs.pop("language", None)
    options = _get_positional_body(*args, **kwargs) or AnswersFromTextOptions(
        question=kwargs.pop("question"),
        text_documents=kwargs.pop("text_documents"),
        language=default_language,
    )
    try:
        options = cast(JSON, options)
        # pylint: disable=unsubscriptable-object,unsupported-assignment-operation
        options["records"] = _validate_text_records(options["records"])
        # pylint: disable=no-member,unsupported-assignment-operation
        options["language"] = options.get("language", None) or default_language
    except TypeError:
        options = cast(AnswersFromTextOptions, options)
        options.text_documents = _validate_text_records(options.text_documents)
        options.language = options.language or default_language
    return options, kwargs


class QuestionAnsweringClientOperationsMixin(QuestionAnsweringClientOperationsMixinGenerated):
    @overload  # type: ignore # https://github.com/Azure/azure-sdk-for-python/issues/26621
    def get_answers(
        self, options: AnswersOptions, *, project_name: str, deployment_name: str, **kwargs: Any
    ) -> AnswersResult:
        """Answers the specified question using your knowledge base.

        :param options: Positional only. POST body of the request. Provide either `options`, OR
         individual keyword arguments. If both are provided, only the options object will be used.
        :type options: ~azure.ai.language.questionanswering.models.AnswersOptions
        :keyword project_name: The name of the knowledge base project to use.
        :paramtype project_name: str
        :keyword deployment_name: The name of the specific deployment of the project to use.
        :paramtype deployment_name: str
        :return: AnswersResult
        :rtype: ~azure.ai.language.questionanswering.models.AnswersResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

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
        answer_context: Optional[KnowledgeBaseAnswerContext] = None,
        ranker_kind: Optional[str] = None,
        filters: Optional[QueryFilters] = None,
        short_answer_options: Optional[ShortAnswerOptions] = None,
        include_unstructured_sources: Optional[bool] = None,
        **kwargs: Any
    ) -> AnswersResult:
        """Answers the specified question using your knowledge base.

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
        :paramtype answer_context: ~azure.ai.language.questionanswering.models.KnowledgeBaseAnswerContext
        :keyword ranker_kind: Type of ranker to be used. Possible
         values include: "Default", "QuestionOnly".
        :paramtype ranker_kind: str
        :keyword filters: Filter QnAs based on given metadata list and knowledge base sources.
        :paramtype filters: ~azure.ai.language.questionanswering.models.QueryFilters
        :keyword short_answer_options: To configure Answer span prediction feature.
        :paramtype short_answer_options: ~azure.ai.language.questionanswering.models.ShortAnswerOptions
        :keyword include_unstructured_sources: (Optional) Flag to enable Query over Unstructured
         Sources.
        :paramtype include_unstructured_sources: bool
        :return: AnswersResult
        :rtype: ~azure.ai.language.questionanswering.models.AnswersResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    # pylint ignore b/c with overloads we need to doc ALL the params in the impl for them to show up in docs
    # pylint: disable=docstring-keyword-should-match-keyword-only,docstring-missing-param,docstring-should-be-keyword
    @distributed_trace
    def get_answers(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        *args: AnswersOptions,
        **kwargs: Any
    ) -> AnswersResult:
        """Answers the specified question using your knowledge base.

        :param options: Positional only. POST body of the request. Provide either `options`, OR
         individual keyword arguments. If both are provided, only the options object will be used.
        :type options: ~azure.ai.language.questionanswering.models.AnswersOptions
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
        :paramtype answer_context: ~azure.ai.language.questionanswering.models.KnowledgeBaseAnswerContext
        :keyword ranker_kind: Type of ranker to be used. Possible
         values include: "Default", "QuestionOnly".
        :paramtype ranker_kind: str
        :keyword filters: Filter QnAs based on given metadata list and knowledge base sources.
        :paramtype filters: ~azure.ai.language.questionanswering.models.QueryFilters
        :keyword short_answer_options: To configure Answer span prediction feature.
        :paramtype short_answer_options: ~azure.ai.language.questionanswering.models.ShortAnswerOptions
        :keyword include_unstructured_sources: (Optional) Flag to enable Query over Unstructured
         Sources.
        :paramtype include_unstructured_sources: bool
        :return: AnswersResult
        :rtype: ~azure.ai.language.questionanswering.models.AnswersResult
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_query_knowledgebase.py
                :start-after: [START query_knowledgebase]
                :end-before: [END query_knowledgebase]
                :language: python
                :dedent: 4
                :caption: Answer the specified question using your knowledge base.
        """
        options, kwargs = _get_answers_prepare_options(*args, **kwargs)
        return super().get_answers(options, **kwargs)

    @overload  # type: ignore
    def get_answers_from_text(self, options: AnswersFromTextOptions, **kwargs: Any) -> AnswersFromTextResult:
        """Answers the specified question using the provided text in the body.

        :param options: Positional only. POST body of the request. Provide either `options`, OR
         individual keyword arguments. If both are provided, only the options object will be used.
        :type options: ~azure.ai.language.questionanswering.models.AnswersFromTextOptions
        :return: AnswersFromTextResult
        :rtype: ~azure.ai.language.questionanswering.models.AnswersFromTextResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def get_answers_from_text(  # pylint: disable=arguments-differ
        self,
        *,
        question: str,
        text_documents: List[Union[str, TextDocument]],
        language: Optional[str] = None,
        **kwargs: Any
    ) -> AnswersFromTextResult:
        """Answers the specified question using the provided text in the body.

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
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def get_answers_from_text(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        *args: AnswersFromTextOptions,
        **kwargs: Any
    ) -> AnswersFromTextResult:
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
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_query_text.py
                :start-after: [START query_text]
                :end-before: [END query_text]
                :language: python
                :dedent: 4
                :caption: Answers the specified question using the provided text.
        """
        options, kwargs = _get_answers_from_text_prepare_options(
            *args, language=kwargs.pop("language", self._default_language), **kwargs  # type: ignore
        )
        return super().get_answers_from_text(options, **kwargs)  # type: ignore


__all__: List[str] = [
    "QuestionAnsweringClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

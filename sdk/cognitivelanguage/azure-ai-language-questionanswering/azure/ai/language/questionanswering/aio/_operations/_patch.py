# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, List, overload, Optional, Union
from azure.core.tracing.decorator_async import distributed_trace_async

from ._operations import QuestionAnsweringClientOperationsMixin as QuestionAnsweringClientOperationsMixinGenerated
from ...models import (
    AnswersOptions,
    AnswersFromTextOptions,
    AnswersResult,
    AnswersFromTextResult,
    KnowledgeBaseAnswerContext,
    QueryFilters,
    ShortAnswerOptions,
    TextDocument,
)
from ..._operations._patch import _get_answers_from_text_prepare_options, _get_answers_prepare_options


class QuestionAnsweringClientOperationsMixin(QuestionAnsweringClientOperationsMixinGenerated):
    @overload  # type: ignore # https://github.com/Azure/azure-sdk-for-python/issues/26621
    async def get_answers(
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
    async def get_answers(  # pylint: disable=arguments-differ
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
    @distributed_trace_async
    async def get_answers(self, *args, **kwargs) -> AnswersResult:  # type: ignore
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

            .. literalinclude:: ../samples/async_samples/sample_query_knowledgebase_async.py
                :start-after: [START query_knowledgebase_async]
                :end-before: [END query_knowledgebase_async]
                :language: python
                :dedent: 4
                :caption: Answer the specified question using your knowledge base.
        """
        options, kwargs = _get_answers_prepare_options(*args, **kwargs)
        return await super().get_answers(options, **kwargs)  # type: ignore

    @overload  # type: ignore
    async def get_answers_from_text(self, options: AnswersFromTextOptions, **kwargs: Any) -> AnswersFromTextResult:
        """Answers the specified question using the provided text in the body.

        :param options: Positional only. POST body of the request. Provide either `options`, OR
         individual keyword arguments. If both are provided, only the options object will be used.
        :type options: ~azure.ai.language.questionanswering.models.AnswersFromTextOptions
        :return: AnswersFromTextResult
        :rtype: ~azure.ai.language.questionanswering.models.AnswersFromTextResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def get_answers_from_text(  # pylint: disable=arguments-differ
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

    @distributed_trace_async
    async def get_answers_from_text(self, *args, **kwargs) -> AnswersFromTextResult:  # type: ignore
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

            .. literalinclude:: ../samples/async_samples/sample_query_text_async.py
                :start-after: [START query_text_async]
                :end-before: [END query_text_async]
                :language: python
                :dedent: 4
                :caption: Answers the specified question using the provided text.
        """
        options, kwargs = _get_answers_from_text_prepare_options(
            *args, language=kwargs.pop("language", self._default_language), **kwargs  # type: ignore
        )
        return await super().get_answers_from_text(options, **kwargs)  # type: ignore


__all__: List[str] = [
    "QuestionAnsweringClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

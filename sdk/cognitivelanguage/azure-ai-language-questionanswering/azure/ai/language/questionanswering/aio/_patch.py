# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Union, Any, Optional, Mapping
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy, AsyncBearerTokenCredentialPolicy
from ._client import QuestionAnsweringClient as QuestionAnsweringClientGenerated
from .._normalization import (  # type: ignore  # noqa: F401
    _normalize_text_options,
    _normalize_answers_dict,
)  # shared helpers


def _apply_default_language(obj: Any, default_lang: Optional[str]) -> None:
    if default_lang and getattr(obj, "language", None) is None:
        setattr(obj, "language", default_lang)


def _authentication_policy(credential, **kwargs):
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(
            name="Ocp-Apim-Subscription-Key", credential=credential, **kwargs
        )
    elif hasattr(credential, "get_token"):
        authentication_policy = AsyncBearerTokenCredentialPolicy(
            credential, *kwargs.pop("credential_scopes", ["https://cognitiveservices.azure.com/.default"]), **kwargs
        )
    else:
        raise TypeError(
            "Unsupported credential: {}. Use an instance of AzureKeyCredential "
            "or a token credential from azure.identity".format(type(credential))
        )
    return authentication_policy


class QuestionAnsweringClient(QuestionAnsweringClientGenerated):
    """The language service API is a suite of natural language processing (NLP) skills built with best-in-class
    Microsoft machine learning algorithms.

    The API can be used to analyze unstructured text for tasks such as sentiment
    analysis, key phrase extraction, language detection and question answering.
    Further documentation can be found in https://learn.microsoft.com/azure/cognitive-services/language-service/overview

    :param endpoint: Supported Cognitive Services endpoint (e.g.,
     https://:code:`<resource-name>`.cognitiveservices.azure.com).
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
        This can be the an instance of AzureKeyCredential if using a Language API key
        or a token credential from :mod:`azure.identity`.
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials_async.AsyncTokenCredential
    :keyword str default_language: Sets the default language to use for all operations.
    :keyword api_version: Api Version. Default value is "2021-10-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self, endpoint: str, credential: Union[AzureKeyCredential, AsyncTokenCredential], **kwargs: Any
    ) -> None:
        try:
            endpoint = endpoint.rstrip("/")
        except AttributeError as exc:
            raise ValueError("Parameter 'endpoint' must be a string.") from exc
        # Extract and persist default language before base init (generated client does not keep it)
        self._default_language = kwargs.pop("default_language", None)
        super().__init__(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential)),
            **kwargs
        )

    # Async convenience wrappers adding the same normalization (aliases, span request, filters) as sync.
    # Placed in patch so regeneration does not remove user-friendly behaviors.
    async def get_answers_from_text(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        if "options" in kwargs:
            raise TypeError("'options' must be passed positionally, not as a keyword")
        if len(args) > 1:
            raise TypeError("Only a single positional 'options' argument is allowed")

        options = args[0] if len(args) > 0 else None
        question: Optional[str] = kwargs.pop("question", None)
        text_documents: Optional[list[Any]] = kwargs.pop("text_documents", None)
        language: Optional[str] = kwargs.pop("language", None)

        if options is not None and (question is not None or text_documents is not None or language is not None):
            raise TypeError("Pass either a positional 'options' argument or keyword params, not both")

        if options is None:
            if question is None or text_documents is None:
                raise TypeError("'question' and 'text_documents' are required when not providing an options object")
            from .. import models as _models
            effective_language = language if language is not None else self._default_language
            model = _models.AnswersFromTextOptions(
                question=question, text_documents=text_documents, language=effective_language
            )
            return await self.question_answering.get_answers_from_text(model, **kwargs)

        if isinstance(options, Mapping):
            # Normalize dict-style inputs (aliases, list[str] -> records, inject default language)
            opts = _normalize_text_options(options, self._default_language)
            return await self.question_answering.get_answers_from_text(opts, **kwargs)

        try:
            _apply_default_language(options, self._default_language)
        except AttributeError:
            pass
        return await self.question_answering.get_answers_from_text(options, **kwargs)

    async def get_answers(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        project_name: Optional[str] = kwargs.pop("project_name", None)
        deployment_name: Optional[str] = kwargs.pop("deployment_name", None)
        if project_name is None or deployment_name is None:
            raise TypeError("'project_name' and 'deployment_name' are required")

        if "options" in kwargs:
            raise TypeError("'options' must be passed positionally, not as a keyword")
        if len(args) > 1:
            raise TypeError("Only a single positional 'options' argument is allowed")

        options = args[0] if len(args) > 0 else None
        question: Optional[str] = kwargs.pop("question", None)
        qna_id: Optional[int] = kwargs.pop("qna_id", None)
        top: Optional[int] = kwargs.pop("top", None)
        user_id: Optional[str] = kwargs.pop("user_id", None)
        confidence_threshold: Optional[float] = kwargs.pop("confidence_threshold", None)
        answer_context: Optional[Any] = kwargs.pop("answer_context", None)
        ranker_kind: Optional[Union[str, Any]] = kwargs.pop("ranker_kind", None)
        filters: Optional[Any] = kwargs.pop("filters", None)
        short_answer_options: Optional[Any] = kwargs.pop("short_answer_options", None)
        include_unstructured_sources: Optional[bool] = kwargs.pop("include_unstructured_sources", None)
        query_preferences: Optional[Any] = kwargs.pop("query_preferences", None)

        if options is not None and any(
            param is not None
            for param in (
                question,
                qna_id,
                top,
                user_id,
                confidence_threshold,
                answer_context,
                ranker_kind,
                filters,
                short_answer_options,
                include_unstructured_sources,
                query_preferences,
            )
        ):
            raise TypeError("Pass either 'options' positional argument or keyword params, not both")

        if options is None:
            if not question and qna_id is None:
                raise TypeError("Either 'question' or 'qna_id' must be provided")
            from .. import models as _models
            model = _models.AnswersOptions(
                question=question,
                qna_id=qna_id,
                top=top,
                user_id=user_id,
                confidence_threshold=confidence_threshold,
                answer_context=answer_context,
                ranker_kind=ranker_kind,
                filters=filters,
                short_answer_options=short_answer_options,
                include_unstructured_sources=include_unstructured_sources,
                query_preferences=query_preferences,
            )
            return await self.question_answering.get_answers(
                model, project_name=project_name, deployment_name=deployment_name, **kwargs
            )

        if isinstance(options, Mapping):
            opts = _normalize_answers_dict(options)
            has_question = bool(opts.get("question"))
            has_qna = (opts.get("qnaId") is not None)
            if not has_question and not has_qna:
                raise TypeError("Either 'question' or 'qna_id' must be provided")
            return await self.question_answering.get_answers(
                opts, project_name=project_name, deployment_name=deployment_name, **kwargs
            )

        try:
            has_question = getattr(options, "question", None)
            has_qna_id = getattr(options, "qna_id", None) or getattr(options, "qnaId", None)
            if has_question in (None, "") and has_qna_id is None:
                raise TypeError("Either 'question' or 'qna_id' (or 'qnaId') must be provided")
        except AttributeError:
            pass

        return await self.question_answering.get_answers(
            options, project_name=project_name, deployment_name=deployment_name, **kwargs
        )


__all__: List[str] = [
    "QuestionAnsweringClient"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


# (Normalization helpers moved to shared module ../_normalization.py)

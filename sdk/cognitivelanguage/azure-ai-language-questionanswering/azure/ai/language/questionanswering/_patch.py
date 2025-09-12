# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from typing import Union, Any, Optional, Mapping
from io import IOBase
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy, BearerTokenCredentialPolicy
from azure.core.tracing.decorator import distributed_trace
from ._client import QuestionAnsweringClient as QuestionAnsweringClientGenerated
from ._normalization import (  # type: ignore  # noqa: F401
    _normalize_text_options,
    _normalize_answers_dict,
)  # internal shared helpers


def _apply_default_language(obj: Any, default_lang: Optional[str]) -> None:
    """Inject default language attribute if target lacks one.

    Swallows only AttributeError to avoid masking other issues.
    """
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
        authentication_policy = BearerTokenCredentialPolicy(
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
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.TokenCredential
    :keyword str default_language: Sets the default language to use for all operations.
    :keyword api_version: Api Version. Default value is "2021-10-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        try:
            endpoint = endpoint.rstrip("/")
        except AttributeError as exc:
            raise ValueError("Parameter 'endpoint' must be a string.") from exc
        # Extract default_language (generated client does not currently persist it)
        self._default_language = kwargs.pop("default_language", None)
        super().__init__(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential, **kwargs)),
            **kwargs
        )

    @distributed_trace
    def get_answers_from_text(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        """Get answers from ad-hoc text.

        Call patterns:
          - get_answers_from_text(options_model)
          - get_answers_from_text(question=..., text_documents=[...], language=..., **kwargs)
          - get_answers_from_text(dict_with_aliases)

        :param question: Question (required when an options object isn't provided).
        :param text_documents: List of texts (str or document objects) (required when an options object isn't provided).
        :keyword language: Language (falls back to the client's default_language if omitted).
        :return: AnswersFromTextResult
        """
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
            from . import models as _models
            effective_language = language if language is not None else getattr(self, "_default_language", None)
            model = _models.AnswersFromTextOptions(
                question=question, text_documents=text_documents, language=effective_language
            )
            return self.question_answering.get_answers_from_text(model, **kwargs)

        if isinstance(options, Mapping):
            # Normalize dict-style inputs (aliases, list[str] -> records, inject default language)
            opts = _normalize_text_options(options, self._default_language)
            return self.question_answering.get_answers_from_text(opts, **kwargs)

        try:
            # Inject default language into model instance if not already set
            _apply_default_language(options, self._default_language)
        except AttributeError:
            pass
        return self.question_answering.get_answers_from_text(options, **kwargs)

    @distributed_trace
    def get_answers(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        """Get answers from a knowledge base.

        Call patterns:
          - get_answers(options_model, project_name=..., deployment_name=...)
          - get_answers(question="...", project_name=..., deployment_name=..., [other keyword aliases])
          - get_answers({"question": "...", "filters": {...}}, project_name=..., deployment_name=...)

        :keyword project_name: Project name (required).
        :keyword deployment_name: Deployment name (required).
        :return: AnswersResult
        """
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
            from . import models as _models
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
            return self.question_answering.get_answers(
                model, project_name=project_name, deployment_name=deployment_name, **kwargs
            )

        if isinstance(options, Mapping):
            opts = _normalize_answers_dict(options)
            question_value = opts.get("question")
            qna_value = opts.get("qnaId")
            if (question_value in (None, "")) and qna_value is None:
                raise TypeError("Either 'question' or 'qna_id' must be provided")
            return self.question_answering.get_answers(
                opts, project_name=project_name, deployment_name=deployment_name, **kwargs
            )

        if not isinstance(options, (bytes, IOBase)):
            try:
                question_value = getattr(options, "question", None)
                qna_value = getattr(options, "qna_id", None) or getattr(options, "qnaId", None)
                if (question_value in (None, "")) and qna_value is None:
                    raise TypeError("Either 'question' or 'qna_id' (or 'qnaId') must be provided")
            except AttributeError:
                pass  # object lacks expected attributes; let service decide

        return self.question_answering.get_answers(
            options, project_name=project_name, deployment_name=deployment_name, **kwargs
        )


def patch_sdk():
    pass


__all__ = ["QuestionAnsweringClient"]


# (Normalization helpers moved to _normalization.py for reuse with async variant)

# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import (  # pylint: disable=unused-import
    Union,
    Optional,
    Any,
    List,
    TYPE_CHECKING,
)
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import HttpResponseError
from .._generated.aio._text_analytics_api_async import TextAnalyticsAPI
from ._base_client_async import AsyncTextAnalyticsClientBase
from .._models import Error
from .._response_handlers import (
    _validate_batch_input,
    process_batch_error,
    entities_result,
    linked_entities_result,
    key_phrases_result,
    sentiment_result,
    language_result,
)

if TYPE_CHECKING:
    from .._models import (
        LanguageInput,
        MultiLanguageInput,
        DocumentLanguage,
        DocumentEntities,
        DocumentLinkedEntities,
        DocumentKeyPhrases,
        DocumentSentiment,
        DocumentError,
    )

MAX_BATCH_SIZE = 1000


class TextAnalyticsClient(AsyncTextAnalyticsClientBase):
    """The Text Analytics API is a suite of text analytics web services built with best-in-class
    Microsoft machine learning algorithms. The API can be used to analyze unstructured text for
    tasks such as sentiment analysis, key phrase extraction and language detection. No training data
    is needed to use this API; just bring your text data. This API uses advanced natural language
    processing techniques to deliver best in class predictions.
    Further documentation can be found in
    https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the cognitive services subscription key or a token credential
        from azure.identity.
    :type credentials: str or token credential
    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, Any, Any) -> None
        super(TextAnalyticsClient, self).__init__(credentials=credential, **kwargs)
        self._client = TextAnalyticsAPI(
            endpoint=endpoint, credentials=credential, pipeline=self._pipeline
        )

    def _segment_batch(self, docs):  # pylint: disable=no-self-use
        """Internal method that segments input documents > 1000 items into
        batches < 1000 items.

        :param docs: The original input documents
        :type docs: list[dict] or list[(Multi)LanguageInput]
        :return: list[list]
        """
        segmented_batches = []
        num_batches = len(docs) // MAX_BATCH_SIZE
        for x in range(num_batches):
            segmented_batches.append(docs[x*MAX_BATCH_SIZE:(x+1)*MAX_BATCH_SIZE])
        segmented_batches.append(docs[num_batches*MAX_BATCH_SIZE:])
        return segmented_batches

    @distributed_trace_async
    async def detect_language(
        self,
        documents,  # type: List[str] or List[LanguageInput]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentLanguage, DocumentError]]
        """Detect Language for a batch of documents.

        The API returns the detected language and a numeric score between 0 and
        1. Scores close to 1 indicate 100% certainty that the identified
        language is true. See https://aka.ms/talangs for the list of enabled languages.

        :param documents: The set of documents to process as part of this
            batch.
        :type documents: list[str] or list[~azure.cognitiveservices.language.textanalytics.LanguageInput]
        :param model_version: (Optional) This value indicates which model will
            be used for scoring. If a model-version is not specified, the API
            will default to the latest, non-preview version.
        :type model_version: str
        :param show_stats: (Optional) if set to true, response will contain
            input and document level statistics.
        :type show_stats: bool
        :return: The combined list of DocumentLanguage and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.cognitiveservices.language.textanalytics.DocumentLanguage,
            ~azure.cognitiveservices.language.textanalytics.DocumentError]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        docs = _validate_batch_input(documents)
        if len(docs) < MAX_BATCH_SIZE:
            try:
                return await self._client.languages(
                    documents=docs,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=language_result,
                    **kwargs
                )
            except HttpResponseError as error:
                process_batch_error(error)

        result = []
        segmented_batches = self._segment_batch(docs)
        try:
            for batch in segmented_batches:
                response = await self._client.languages(
                    documents=batch,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=language_result,
                    **kwargs
                )
                if isinstance(response, Error):
                    for _ in batch:
                        result.append(response)
                else:
                    result.extend(response)
            return result
        except HttpResponseError as error:
            process_batch_error(error)

    @distributed_trace_async
    async def recognize_entities(
        self,
        documents,  # type: List[str] or List[MultiLanguageInput]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentEntities, DocumentError]]
        """Named Entity Recognition for a batch of documents.

        The API returns a list of general named entities in a given document.
        For the list of supported entity types, check:
        https://aka.ms/taner
        For the list of enabled languages, check:
        https://aka.ms/talangs

        :param documents: The set of documents to process as part of this
            batch.
        :type documents: list[str] or list[~azure.cognitiveservices.language.textanalytics.MultiLanguageInput]
        :param model_version: (Optional) This value indicates which model will
            be used for scoring. If a model-version is not specified, the API
            will default to the latest, non-preview version.
        :type model_version: str
        :param show_stats: (Optional) if set to true, response will contain
            input and document level statistics.
        :type show_stats: bool
        :return: The combined list of DocumentEntities and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.cognitiveservices.language.textanalytics.DocumentEntities,
            ~azure.cognitiveservices.language.textanalytics.DocumentError]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        docs = _validate_batch_input(documents)
        if len(docs) < MAX_BATCH_SIZE:
            try:
                return await self._client.entities_recognition_general(
                    documents=docs,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=entities_result,
                    **kwargs
                )
            except HttpResponseError as error:
                process_batch_error(error)

        result = []
        segmented_batches = self._segment_batch(docs)
        try:
            for batch in segmented_batches:
                response = await self._client.entities_recognition_general(
                    documents=batch,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=entities_result,
                    **kwargs
                )
                if isinstance(response, Error):
                    for _ in batch:
                        result.append(response)
                else:
                    result.extend(response)
            return result
        except HttpResponseError as error:
            process_batch_error(error)

    @distributed_trace_async
    async def recognize_pii_entities(
        self,
        documents,  # type: List[str] or List[MultiLanguageInput]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentEntities, DocumentError]]
        """Recognize entities containing personal information for a batch of documents.

        The API returns a list of personal information entities ("SSN",
        "Bank Account", etc) in the document.  For the list of supported entity types,
        check https://aka.ms/tanerpii. See https://aka.ms/talangs
        for the list of enabled languages.

        :param documents: The set of documents to process as part of this
            batch.
        :type documents: list[str] or list[~azure.cognitiveservices.language.textanalytics.MultiLanguageInput]
        :param model_version: (Optional) This value indicates which model will
            be used for scoring. If a model-version is not specified, the API
            will default to the latest, non-preview version.
        :type model_version: str
        :param show_stats: (Optional) if set to true, response will contain
            input and document level statistics.
        :type show_stats: bool
        :return: The combined list of DocumentEntities and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.cognitiveservices.language.textanalytics.DocumentEntities,
            ~azure.cognitiveservices.language.textanalytics.DocumentError]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        docs = _validate_batch_input(documents)
        if len(docs) < MAX_BATCH_SIZE:
            try:
                return await self._client.entities_recognition_pii(
                    documents=docs,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=entities_result,
                    **kwargs
                )
            except HttpResponseError as error:
                process_batch_error(error)

        result = []
        segmented_batches = self._segment_batch(docs)
        try:
            for batch in segmented_batches:
                response = await self._client.entities_recognition_pii(
                    documents=batch,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=entities_result,
                    **kwargs
                )
                if isinstance(response, Error):
                    for _ in batch:
                        result.append(response)
                else:
                    result.extend(response)
            return result
        except HttpResponseError as error:
            process_batch_error(error)

    @distributed_trace_async
    async def recognize_linked_entities(
        self,
        documents,  # type: List[str] or List[MultiLanguageInput]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentLinkedEntities, DocumentError]]
        """Recognize linked entities from a well-known knowledge base for a batch of documents.

        The API returns a list of recognized entities with links to a
        well-known knowledge base. See https://aka.ms/talangs for
        supported languages in Text Analytics API.

        :param documents: The set of documents to process as part of this
            batch.
        :type documents: list[str] or list[~azure.cognitiveservices.language.textanalytics.MultiLanguageInput]
        :param model_version: (Optional) This value indicates which model will
            be used for scoring. If a model-version is not specified, the API
            will default to the latest, non-preview version.
        :type model_version: str
        :param show_stats: (Optional) if set to true, response will contain
            input and document level statistics.
        :type show_stats: bool
        :return: The combined list of DocumentLinkedEntities and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.cognitiveservices.language.textanalytics.DocumentLinkedEntities,
            ~azure.cognitiveservices.language.textanalytics.DocumentError]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        docs = _validate_batch_input(documents)
        if len(docs) < MAX_BATCH_SIZE:
            try:
                return await self._client.entities_linking(
                    documents=docs,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=linked_entities_result,
                    **kwargs
                )
            except HttpResponseError as error:
                process_batch_error(error)

        result = []
        segmented_batches = self._segment_batch(docs)
        try:
            for batch in segmented_batches:
                response = await self._client.entities_linking(
                    documents=batch,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=linked_entities_result,
                    **kwargs
                )
                if isinstance(response, Error):
                    for _ in batch:
                        result.append(response)
                else:
                    result.extend(response)
            return result
        except HttpResponseError as error:
            process_batch_error(error)

    @distributed_trace_async
    async def extract_key_phrases(
        self,
        documents,  # type: List[str] or List[MultiLanguageInput]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentKeyPhrases, DocumentError]]
        """Extract Key Phrases from a batch of documents.

        The API returns a list of strings denoting the key phrases in the input
        text. See https://aka.ms/talangs for the list of enabled
        languages.

        :param documents: The set of documents to process as part of this
            batch.
        :type documents: list[str] or list[~azure.cognitiveservices.language.textanalytics.MultiLanguageInput]
        :param model_version: (Optional) This value indicates which model will
            be used for scoring. If a model-version is not specified, the API
            will default to the latest, non-preview version.
        :type model_version: str
        :param show_stats: (Optional) if set to true, response will contain
            input and document level statistics.
        :type show_stats: bool
        :return: The combined list of DocumentKeyPhrases and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.cognitiveservices.language.textanalytics.DocumentKeyPhrases,
            ~azure.cognitiveservices.language.textanalytics.DocumentError]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        docs = _validate_batch_input(documents)
        if len(docs) < MAX_BATCH_SIZE:
            try:
                return await self._client.key_phrases(
                    documents=docs,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=key_phrases_result,
                    **kwargs
                )
            except HttpResponseError as error:
                process_batch_error(error)

        result = []
        segmented_batches = self._segment_batch(docs)
        try:
            for batch in segmented_batches:
                response = await self._client.key_phrases(
                    documents=batch,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=key_phrases_result,
                    **kwargs
                )
                if isinstance(response, Error):
                    for _ in batch:
                        result.append(response)
                else:
                    result.extend(response)
            return result
        except HttpResponseError as error:
            process_batch_error(error)

    @distributed_trace_async
    async def analyze_sentiment(
        self,
        documents,  # type: List[str] or List[MultiLanguageInput]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentSentiment, DocumentError]]
        """Analyze sentiment for a batch of documents.

        The API returns a sentiment prediction, as well as sentiment scores for
        each sentiment class (Positive, Negative, and Neutral) for the document
        and each sentence within it. See https://aka.ms/talangs for the list
        of enabled languages.

        :param documents: The set of documents to process as part of this
            batch.
        :type documents: list[str] or list[~azure.cognitiveservices.language.textanalytics.MultiLanguageInput]
        :param model_version: (Optional) This value indicates which model will
            be used for scoring. If a model-version is not specified, the API
            will default to the latest, non-preview version.
        :type model_version: str
        :param show_stats: (Optional) if set to true, response will contain
            input and document level statistics.
        :type show_stats: bool
        :return: The combined list of DocumentSentiment and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.cognitiveservices.language.textanalytics.DocumentSentiment,
            ~azure.cognitiveservices.language.textanalytics.DocumentError]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        docs = _validate_batch_input(documents)
        if len(docs) < MAX_BATCH_SIZE:
            try:
                return await self._client.sentiment(
                    documents=docs,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=sentiment_result,
                    **kwargs
                )
            except HttpResponseError as error:
                process_batch_error(error)

        result = []
        segmented_batches = self._segment_batch(docs)
        try:
            for batch in segmented_batches:
                response = await self._client.sentiment(
                    documents=batch,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=sentiment_result,
                    **kwargs
                )
                if isinstance(response, Error):
                    for _ in batch:
                        result.append(response)
                else:
                    result.extend(response)
            return result
        except HttpResponseError as error:
            process_batch_error(error)

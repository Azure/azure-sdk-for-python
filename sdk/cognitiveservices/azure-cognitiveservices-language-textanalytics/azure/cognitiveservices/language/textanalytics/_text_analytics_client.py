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
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import HttpResponseError
from ._generated._text_analytics_api import TextAnalyticsAPI
from ._models import Error
from ._base_client import TextAnalyticsClientBase
from ._response_handlers import (
    _validate_batch_input,
    process_batch_error,
    entities_result,
    linked_entities_result,
    key_phrases_result,
    sentiment_result,
    language_result,
)

if TYPE_CHECKING:
    from ._models import (
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


class TextAnalyticsClient(TextAnalyticsClientBase):
    """The Text Analytics API is a suite of text analytics web services built with best-in-class Microsoft
    machine learning algorithms. The API can be used to analyze unstructured text for tasks such as sentiment analysis,
    key phrase and entity extraction as well as language detection.
    No training data is needed to use this API; just bring your text data.
    This API uses advanced natural language processing techniques to deliver best in class predictions.
    Further documentation can be found in
    https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/overview

    This API is currently available in:
    * Australia East - australiaeast.api.cognitive.microsoft.com
    * Brazil South - brazilsouth.api.cognitive.microsoft.com
    * Canada Central - canadacentral.api.cognitive.microsoft.com
    * Central India - centralindia.api.cognitive.microsoft.com
    * Central US - centralus.api.cognitive.microsoft.com
    * East Asia - eastasia.api.cognitive.microsoft.com
    * East US - eastus.api.cognitive.microsoft.com
    * East US 2 - eastus2.api.cognitive.microsoft.com
    * France Central - francecentral.api.cognitive.microsoft.com
    * Japan East - japaneast.api.cognitive.microsoft.com
    * Japan West - japanwest.api.cognitive.microsoft.com
    * Korea Central - koreacentral.api.cognitive.microsoft.com
    * North Central US - northcentralus.api.cognitive.microsoft.com
    * North Europe - northeurope.api.cognitive.microsoft.com
    * South Africa North - southafricanorth.api.cognitive.microsoft.com
    * South Central US - southcentralus.api.cognitive.microsoft.com
    * Southeast Asia - southeastasia.api.cognitive.microsoft.com
    * UK South - uksouth.api.cognitive.microsoft.com
    * West Central US - westcentralus.api.cognitive.microsoft.com
    * West Europe - westeurope.api.cognitive.microsoft.com
    * West US - westus.api.cognitive.microsoft.com
    * West US 2 - westus2.api.cognitive.microsoft.com

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the cognitive services subscription key or a token credential
        from azure.identity.
    :type credentials: str or token credential
    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, str, Any) -> None
        super(TextAnalyticsClient, self).__init__(credentials=credential, **kwargs)
        self._client = TextAnalyticsAPI(
            endpoint=endpoint, credentials=credential, pipeline=self._pipeline
        )

    def _segment_batch(self, docs):
        """Internal method that segments input documents > 1000 items into
        batches < 1000 items.

        :param docs: The original input documents
        :type docs: list[dict] or list[(Multi)LanguageInput]
        :return: list[list]
        """
        segmented_batches = []
        num_batches = len(docs) // MAX_BATCH_SIZE
        for x in range(num_batches):
            segmented_batches.append(
                docs[x*MAX_BATCH_SIZE:(x+1)*MAX_BATCH_SIZE]
            )
        segmented_batches.append(docs[num_batches*MAX_BATCH_SIZE:])
        return segmented_batches

    @distributed_trace
    def detect_language(
        self,
        documents,  # type: List[str] or List[LanguageInput]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentLanguage, DocumentError]]
        """Detect Language.

        The API returns the detected language and a numeric score between 0 and
        1. Scores close to 1 indicate 100% certainty that the identified
        language is true. See the &lt;a
        href="https://aka.ms/talangs"&gt;Supported languages in Text Analytics
        API&lt;/a&gt; for the list of enabled languages.

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
                return self._client.languages(
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
                response = self._client.languages(
                    documents=batch,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=language_result,
                    **kwargs
                )
                if isinstance(response, Error):
                    [result.append(response) for _ in batch]
                else:
                    result.extend(response)
            return result
        except HttpResponseError as error:
            process_batch_error(error)

    @distributed_trace
    def recognize_entities(
        self,
        documents,  # type: List[str] or List[MultiLanguageInput]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentEntities, DocumentError]]
        """Named Entity Recognition.

        The API returns a list of general named entities in a given document.
        For the list of supported entity types, check <a
        href="https://aka.ms/taner">Supported Entity Types in Text Analytics
        API</a>. For the list of enabled languages, check <a
        href="https://aka.ms/talangs">Supported languages in Text Analytics
        API</a>.

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
                return self._client.entities_recognition_general(
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
                response = self._client.entities_recognition_general(
                    documents=batch,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=entities_result,
                    **kwargs
                )
                if isinstance(response, Error):
                    [result.append(response) for _ in batch]
                else:
                    result.extend(response)
            return result
        except HttpResponseError as error:
            process_batch_error(error)

    @distributed_trace
    def recognize_pii_entities(
        self,
        documents,  # type: List[str] or List[MultiLanguageInput]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentEntities, DocumentError]]
        """Entities containing personal information.

        The API returns a list of personal information entities (\"SSN\",
        \"Bank Account\" etc) in the document. See the &lt;a
        href="https://aka.ms/talangs"&gt;Supported languages in Text Analytics
        API&lt;/a&gt; for the list of enabled languages.

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
                return self._client.entities_recognition_pii(
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
                response = self._client.entities_recognition_pii(
                    documents=batch,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=entities_result,
                    **kwargs
                )
                if isinstance(response, Error):
                    [result.append(response) for _ in batch]
                else:
                    result.extend(response)
            return result
        except HttpResponseError as error:
            process_batch_error(error)

    @distributed_trace
    def recognize_linked_entities(
        self,
        documents,  # type: List[str] or List[MultiLanguageInput]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentLinkedEntities, DocumentError]]
        """Linked entities from a well-known knowledge base.

        The API returns a list of recognized entities with links to a
        well-known knowledge base. See the &lt;a
        href="https://aka.ms/talangs"&gt;Supported languages in Text Analytics
        API.

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
                return self._client.entities_linking(
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
                response = self._client.entities_linking(
                    documents=batch,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=linked_entities_result,
                    **kwargs
                )
                if isinstance(response, Error):
                    [result.append(response) for _ in batch]
                else:
                    result.extend(response)
            return result
        except HttpResponseError as error:
            process_batch_error(error)

    @distributed_trace
    def extract_key_phrases(
        self,
        documents,  # type: List[str] or List[MultiLanguageInput]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentKeyPhrases, DocumentError]]
        """Key Phrases.

        The API returns a list of strings denoting the key phrases in the input
        text. See the &lt;a href="https://aka.ms/talangs"&gt;Supported
        languages in Text Analytics API&lt;/a&gt; for the list of enabled
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
                return self._client.key_phrases(
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
                response = self._client.key_phrases(
                    documents=batch,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=key_phrases_result,
                    **kwargs
                )
                if isinstance(response, Error):
                    [result.append(response) for _ in batch]
                else:
                    result.extend(response)
            return result
        except HttpResponseError as error:
            process_batch_error(error)

    @distributed_trace
    def analyze_sentiment(
        self,
        documents,  # type: List[str] or List[MultiLanguageInput]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentSentiment, DocumentError]]
        """Sentiment.

        The API returns a sentiment prediction, as well as sentiment scores for
        each sentiment class (Positive, Negative, and Neutral) for the document
        and each sentence within it. See the &lt;a
        href="https://aka.ms/talangs"&gt;Supported languages in Text Analytics
        API&lt;/a&gt; for the list of enabled languages.

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
                return self._client.sentiment(
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
                response = self._client.sentiment(
                    documents=batch,
                    model_version=model_version,
                    show_stats=show_stats,
                    cls=sentiment_result,
                    **kwargs
                )
                if isinstance(response, Error):
                    [result.append(response) for _ in batch]
                else:
                    result.extend(response)
            return result
        except HttpResponseError as error:
            process_batch_error(error)

# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._generated._text_analytics_api import TextAnalyticsAPI
from ._generated.models._models import LanguageInput
from ._base_client import TextAnalyticsClientBase
from ._deserialize import deserialize_entities_result

class TextAnalyticsClient(TextAnalyticsClientBase):
    """The Text Analytics API is a suite of text analytics web services built with best-in-class Microsoft machine learning algorithms.
    The API can be used to analyze unstructured text for tasks such as sentiment analysis, key phrase and entity extraction as well as language detection.
    No training data is needed to use this API; just bring your text data.
    This API uses advanced natural language processing techniques to deliver best in class predictions.
    Further documentation can be found in https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/overview
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


    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`
    :param endpoint: Supported Cognitive Services endpoints (protocol and
     hostname, for example: https://westus.api.cognitive.microsoft.com).
    :type endpoint: str
    """

    def __init__(self, endpoint, credential, **kwargs):
        super(TextAnalyticsClient, self).__init__(credentials=credential, **kwargs)
        self._client = TextAnalyticsAPI(endpoint=endpoint, credentials=credential, pipeline=self._pipeline)

    def _validate_input(self, documents):
        strings = False
        for idx, item in enumerate(documents):
            if type(item) == str:
                documents[idx] = {"id": idx, "text": item}
                strings = True
            if type(item) == dict or isinstance(item, LanguageInput):
                if strings:
                    raise TypeError("Mixing string and dictionary input unsupported.")
        return documents

    def detect_language(self, documents, model_version=None, show_stats=False, **kwargs):
        """Detect Language.

        The API returns the detected language and a numeric score between 0 and
        1. Scores close to 1 indicate 100% certainty that the identified
        language is true. See the &lt;a
        href="https://aka.ms/talangs"&gt;Supported languages in Text Analytics
        API&lt;/a&gt; for the list of enabled languages.

        :param documents:
        :type documents: list[~textanalytics.models.LanguageInput]
        :param model_version: (Optional) This value indicates which model will
         be used for scoring. If a model-version is not specified, the API
         should default to the latest, non-preview version.
        :type model_version: str
        :param show_stats: (Optional) if set to true, response will contain
         input and document level statistics.
        :type show_stats: bool
        :param callable cls: A custom type or function that will be passed the
         direct response
        :return: object or the result of cls(response)
        :rtype: object
        :raises: :class:`HttpResponseError<azure.core.HttpResponseError>`
        """
        docs = self._validate_input(documents)
        try:
            return self._client.languages(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                **kwargs
            )
        except Exception as error:
            raise error

    def detect_entities(self, documents, model_version=None, show_stats=False, **kwargs):
        """Named Entity Recognition.

        The API returns a list of general named entities in a given document.
        For the list of supported entity types, check <a
        href="https://aka.ms/taner">Supported Entity Types in Text Analytics
        API</a>. For the list of enabled languages, check <a
        href="https://aka.ms/talangs">Supported languages in Text Analytics
        API</a>.
        .

        :param documents: The set of documents to process as part of this
         batch.
        :type documents: list[~textanalytics.models.MultiLanguageInput]
        :param model_version: (Optional) This value indicates which model will
         be used for scoring. If a model-version is not specified, the API
         should default to the latest, non-preview version.
        :type model_version: str
        :param show_stats: (Optional) if set to true, response will contain
         input and document level statistics.
        :type show_stats: bool
        :param callable cls: A custom type or function that will be passed the
         direct response
        :return: object or the result of cls(response)
        :rtype: object
        :raises: :class:`HttpResponseError<azure.core.HttpResponseError>`
        """
        docs = self._validate_input(documents)
        try:
            return self._client.entitiesrecognitiongeneral(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=deserialize_entities_result,
                **kwargs
            )
        except Exception as error:
            raise error

    def detect_pii_entities(self, documents, model_version=None, show_stats=None, **kwargs):
        """Entities containing personal information.

        The API returns a list of personal information entities (\"SSN\",
        \"Bank Account\" etc) in the document. See the &lt;a
        href="https://aka.ms/talangs"&gt;Supported languages in Text Analytics
        API&lt;/a&gt; for the list of enabled languages.
        .

        :param documents: The set of documents to process as part of this
         batch.
        :type documents: list[~textanalytics.models.MultiLanguageInput]
        :param model_version: (Optional) This value indicates which model will
         be used for scoring. If a model-version is not specified, the API
         should default to the latest, non-preview version.
        :type model_version: str
        :param show_stats: (Optional) if set to true, response will contain
         input and document level statistics.
        :type show_stats: bool
        :param callable cls: A custom type or function that will be passed the
         direct response
        :return: object or the result of cls(response)
        :rtype: object
        :raises: :class:`HttpResponseError<azure.core.HttpResponseError>`
        """
        docs = self._validate_input(documents)
        try:
            return self._client.entitiesrecognitionpii(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                **kwargs
            )
        except Exception as error:
            raise error

    def detect_linked_entities(self, documents, model_version=None, show_stats=None, **kwargs):
        """Linked entities from a well-known knowledge base.

        The API returns a list of recognized entities with links to a
        well-known knowledge base. See the &lt;a
        href="https://aka.ms/talangs"&gt;Supported languages in Text Analytics
        API.
        .

        :param documents: The set of documents to process as part of this
         batch.
        :type documents: list[~textanalytics.models.MultiLanguageInput]
        :param model_version: (Optional) This value indicates which model will
         be used for scoring. If a model-version is not specified, the API
         should default to the latest, non-preview version.
        :type model_version: str
        :param show_stats: (Optional) if set to true, response will contain
         input and document level statistics.
        :type show_stats: bool
        :param callable cls: A custom type or function that will be passed the
         direct response
        :return: object or the result of cls(response)
        :rtype: object
        :raises: :class:`HttpResponseError<azure.core.HttpResponseError>`
        """
        docs = self._validate_input(documents)
        try:
            return self._client.entitieslinking(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                **kwargs
            )
        except Exception as error:
            raise error

    def key_phrases(self, documents, model_version=None, show_stats=None, **kwargs):
        """Key Phrases.

        The API returns a list of strings denoting the key phrases in the input
        text. See the &lt;a href="https://aka.ms/talangs"&gt;Supported
        languages in Text Analytics API&lt;/a&gt; for the list of enabled
        languages.

        :param documents: The set of documents to process as part of this
         batch.
        :type documents: list[~textanalytics.models.MultiLanguageInput]
        :param model_version: (Optional) This value indicates which model will
         be used for scoring. If a model-version is not specified, the API
         should default to the latest, non-preview version.
        :type model_version: str
        :param show_stats: (Optional) if set to true, response will contain
         input and document level statistics.
        :type show_stats: bool
        :param callable cls: A custom type or function that will be passed the
         direct response
        :return: object or the result of cls(response)
        :rtype: object
        :raises: :class:`HttpResponseError<azure.core.HttpResponseError>`
        """
        docs = self._validate_input(documents)
        try:
            return self._client.key_phrases(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                **kwargs
            )
        except Exception as error:
            raise error

    def detect_sentiment(self, documents, model_version=None, show_stats=None, **kwargs):
        """Sentiment.

        The API returns a sentiment prediction, as well as sentiment scores for
        each sentiment class (Positive, Negative, and Neutral) for the document
        and each sentence within it. See the &lt;a
        href="https://aka.ms/talangs"&gt;Supported languages in Text Analytics
        API&lt;/a&gt; for the list of enabled languages.

        :param documents: The set of documents to process as part of this
         batch.
        :type documents: list[~textanalytics.models.MultiLanguageInput]
        :param model_version: (Optional) This value indicates which model will
         be used for scoring. If a model-version is not specified, the API
         should default to the latest, non-preview version.
        :type model_version: str
        :param show_stats: (Optional) if set to true, response will contain
         input and document level statistics.
        :type show_stats: bool
        :param callable cls: A custom type or function that will be passed the
         direct response
        :return: object or the result of cls(response)
        :rtype: object
        :raises: :class:`HttpResponseError<azure.core.HttpResponseError>`
        """
        docs = self._validate_input(documents)
        try:
            return self._client.sentiment(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                **kwargs
            )
        except Exception as error:
            raise error

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=too-many-lines

from typing import (
    Union,
    Any,
    List,
    Dict,
    cast,
    Optional,
)
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials import TokenCredential
from ._base_client import TextAnalyticsClientBase, TextAnalyticsApiVersion
from ._lro import AnalyzeActionsLROPoller, AnalyzeHealthcareEntitiesLROPoller, TextAnalysisLROPoller
from ._request_handlers import (
    _validate_input,
    _determine_action_type,
)
from ._validate import validate_multiapi_args, check_for_unsupported_actions_types
from ._response_handlers import (
    process_http_response_error,
    entities_result,
    linked_entities_result,
    key_phrases_result,
    sentiment_result,
    language_result,
    pii_entities_result,
    healthcare_paged_result,
    analyze_paged_result,
    _get_result_from_continuation_token,
    dynamic_classification_result,
)

from ._lro import (
    TextAnalyticsOperationResourcePolling,
    AnalyzeActionsLROPollingMethod,
    AnalyzeHealthcareEntitiesLROPollingMethod,
)
from ._generated.models import HealthcareDocumentType, ClassificationType
from ._models import (
    DetectLanguageInput,
    TextDocumentInput,
    DetectLanguageResult,
    RecognizeEntitiesResult,
    RecognizeLinkedEntitiesResult,
    ExtractKeyPhrasesResult,
    AnalyzeSentimentResult,
    DocumentError,
    RecognizePiiEntitiesResult,
    RecognizeEntitiesAction,
    RecognizePiiEntitiesAction,
    RecognizeLinkedEntitiesAction,
    ExtractKeyPhrasesAction,
    AnalyzeSentimentAction,
    AnalyzeHealthcareEntitiesResult,
    RecognizeCustomEntitiesAction,
    RecognizeCustomEntitiesResult,
    SingleLabelClassifyAction,
    MultiLabelClassifyAction,
    ClassifyDocumentResult,
    AnalyzeHealthcareEntitiesAction,
    _AnalyzeActionsType,
    ExtractSummaryAction,
    ExtractSummaryResult,
    AbstractiveSummaryAction,
    AbstractiveSummaryResult,
    DynamicClassificationResult,
    PiiEntityDomain,
    PiiEntityCategory,
)
from ._check import is_language_api, string_index_type_compatibility


AnalyzeActionsResponse = TextAnalysisLROPoller[
    ItemPaged[
        List[
            Union[
                RecognizeEntitiesResult,
                RecognizeLinkedEntitiesResult,
                RecognizePiiEntitiesResult,
                ExtractKeyPhrasesResult,
                AnalyzeSentimentResult,
                RecognizeCustomEntitiesResult,
                ClassifyDocumentResult,
                AnalyzeHealthcareEntitiesResult,
                ExtractSummaryResult,
                AbstractiveSummaryResult,
                DocumentError,
            ]
        ]
    ]
]


class TextAnalyticsClient(TextAnalyticsClientBase):
    """The Language service API is a suite of natural language processing (NLP) skills built with the best-in-class
    Microsoft machine learning algorithms. The API can be used to analyze unstructured text for
    tasks such as sentiment analysis, key phrase extraction, entities recognition,
    and language detection, and more.

    Further documentation can be found in
    https://docs.microsoft.com/azure/cognitive-services/language-service/overview

    :param str endpoint: Supported Cognitive Services or Language resource
        endpoints (protocol and hostname, for example: 'https://<resource-name>.cognitiveservices.azure.com').
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the an instance of AzureKeyCredential if using a Cognitive Services/Language API key
        or a token credential from :mod:`azure.identity`.
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.TokenCredential
    :keyword str default_country_hint: Sets the default country_hint to use for all operations.
        Defaults to "US". If you don't want to use a country hint, pass the string "none".
    :keyword str default_language: Sets the default language to use for all operations.
        Defaults to "en".
    :keyword api_version: The API version of the service to use for requests. It defaults to the
        latest service version. Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str or ~azure.ai.textanalytics.TextAnalyticsApiVersion

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_ta_client_with_key]
            :end-before: [END create_ta_client_with_key]
            :language: python
            :dedent: 4
            :caption: Creating the TextAnalyticsClient with endpoint and API key.

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_ta_client_with_aad]
            :end-before: [END create_ta_client_with_aad]
            :language: python
            :dedent: 4
            :caption: Creating the TextAnalyticsClient with endpoint and token credential from Azure Active Directory.
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, TokenCredential],
        *,
        default_language: Optional[str] = None,
        default_country_hint: Optional[str] = None,
        api_version: Optional[Union[str, TextAnalyticsApiVersion]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            endpoint=endpoint, credential=credential, api_version=api_version, **kwargs
        )
        self._default_language = default_language if default_language is not None else "en"
        self._default_country_hint = default_country_hint if default_country_hint is not None else "US"
        self._string_index_type_default = (
            None if api_version == "v3.0" else "UnicodeCodePoint"
        )

    @distributed_trace
    @validate_multiapi_args(
        version_method_added="v3.0",
        args_mapping={"v3.1": ["disable_service_logs"]}
    )
    def detect_language(
        self,
        documents: Union[List[str], List[DetectLanguageInput], List[Dict[str, str]]],
        *,
        country_hint: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        model_version: Optional[str] = None,
        show_stats: Optional[bool] = None,
        **kwargs: Any,
    ) -> List[Union[DetectLanguageResult, DocumentError]]:
        """Detect language for a batch of documents.

        Returns the detected language and a numeric score between zero and
        one. Scores close to one indicate 100% certainty that the identified
        language is true. See https://aka.ms/talangs for the list of enabled languages.

        See https://aka.ms/azsdk/textanalytics/data-limits for service data limits.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and country_hint on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.DetectLanguageInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.DetectLanguageInput`, like
            `{"id": "1", "country_hint": "us", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.DetectLanguageInput] or list[dict[str, str]]
        :keyword str country_hint: Country of origin hint for the entire batch. Accepts two
            letter country codes specified by ISO 3166-1 alpha-2. Per-document
            country hints will take precedence over whole batch hints. Defaults to
            "US". If you don't want to use a country hint, pass the string "none".
        :keyword str model_version: Version of the model used on the service side for scoring,
            e.g. "latest", "2019-10-01". If a model version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, the Language service logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the service's natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :return: The combined list of :class:`~azure.ai.textanalytics.DetectLanguageResult` and
            :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents were
            passed in.
        :rtype: list[~azure.ai.textanalytics.DetectLanguageResult or ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. versionadded:: v3.1
            The *disable_service_logs* keyword argument.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_detect_language.py
                :start-after: [START detect_language]
                :end-before: [END detect_language]
                :language: python
                :dedent: 4
                :caption: Detecting language in a batch of documents.
        """

        country_hint_arg = (
            country_hint
            if country_hint is not None
            else self._default_country_hint
        )
        docs = _validate_input(documents, "country_hint", country_hint_arg)

        try:
            if is_language_api(self._api_version):
                models = self._client.models(api_version=self._api_version)
                return cast(
                    List[Union[DetectLanguageResult, DocumentError]],
                    self._client.analyze_text(
                        body=models.AnalyzeTextLanguageDetectionInput(
                            analysis_input={"documents": docs},
                            parameters=models.LanguageDetectionTaskParameters(
                                logging_opt_out=disable_service_logs,
                                model_version=model_version
                            )
                        ),
                        show_stats=show_stats,
                        cls=kwargs.pop("cls", language_result),
                        **kwargs
                    )
                )

            # api_versions 3.0, 3.1
            return cast(
                List[Union[DetectLanguageResult, DocumentError]],
                self._client.languages(
                    documents=docs,
                    model_version=model_version,
                    show_stats=show_stats,
                    logging_opt_out=disable_service_logs,
                    cls=kwargs.pop("cls", language_result),
                    **kwargs
                )
            )
        except HttpResponseError as error:
            return process_http_response_error(error)

    @distributed_trace
    @validate_multiapi_args(
        version_method_added="v3.0",
        args_mapping={"v3.1": ["string_index_type", "disable_service_logs"]}
    )
    def recognize_entities(
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        *,
        disable_service_logs: Optional[bool] = None,
        language: Optional[str] = None,
        model_version: Optional[str] = None,
        show_stats: Optional[bool] = None,
        string_index_type: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Union[RecognizeEntitiesResult, DocumentError]]:
        """Recognize entities for a batch of documents.

        Identifies and categorizes entities in your text as people, places,
        organizations, date/time, quantities, percentages, currencies, and more.
        For the list of supported entity types, check: https://aka.ms/taner

        See https://aka.ms/azsdk/textanalytics/data-limits for service data limits.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list
            of dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`,
            like `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or list[dict[str, str]]
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language. See https://aka.ms/talangs for
            supported languages in Language API.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :keyword str string_index_type: Specifies the method used to interpret string offsets.
            `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
            you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
            see https://aka.ms/text-analytics-offsets
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, the Language service logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the service's natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :return: The combined list of :class:`~azure.ai.textanalytics.RecognizeEntitiesResult` and
            :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents
            were passed in.
        :rtype: list[~azure.ai.textanalytics.RecognizeEntitiesResult or ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. versionadded:: v3.1
            The *disable_service_logs* and *string_index_type* keyword arguments.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_entities.py
                :start-after: [START recognize_entities]
                :end-before: [END recognize_entities]
                :language: python
                :dedent: 4
                :caption: Recognize entities in a batch of documents.
        """

        language_arg = language if language is not None else self._default_language
        docs = _validate_input(documents, "language", language_arg)
        string_index_type_arg = string_index_type if string_index_type is not None else self._string_index_type_default

        try:
            if is_language_api(self._api_version):
                models = self._client.models(api_version=self._api_version)
                return cast(
                    List[Union[RecognizeEntitiesResult, DocumentError]],
                    self._client.analyze_text(
                        body=models.AnalyzeTextEntityRecognitionInput(
                            analysis_input={"documents": docs},
                            parameters=models.EntitiesTaskParameters(
                                logging_opt_out=disable_service_logs,
                                model_version=model_version,
                                string_index_type=string_index_type_compatibility(string_index_type_arg)
                            )
                        ),
                        show_stats=show_stats,
                        cls=kwargs.pop("cls", entities_result),
                        **kwargs
                    )
                )

            # api_versions 3.0, 3.1
            return cast(
                List[Union[RecognizeEntitiesResult, DocumentError]],
                self._client.entities_recognition_general(
                    documents=docs,
                    model_version=model_version,
                    show_stats=show_stats,
                    string_index_type=string_index_type_arg,
                    logging_opt_out=disable_service_logs,
                    cls=kwargs.pop("cls", entities_result),
                    **kwargs,
                )
            )
        except HttpResponseError as error:
            return process_http_response_error(error)

    @distributed_trace
    @validate_multiapi_args(
        version_method_added="v3.1"
    )
    def recognize_pii_entities(
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        *,
        categories_filter: Optional[List[Union[str, PiiEntityCategory]]] = None,
        disable_service_logs: Optional[bool] = None,
        domain_filter: Optional[Union[str, PiiEntityDomain]] = None,
        language: Optional[str] = None,
        model_version: Optional[str] = None,
        show_stats: Optional[bool] = None,
        string_index_type: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Union[RecognizePiiEntitiesResult, DocumentError]]:
        """Recognize entities containing personal information for a batch of documents.

        Returns a list of personal information entities ("SSN",
        "Bank Account", etc) in the document.  For the list of supported entity types,
        check https://aka.ms/azsdk/language/pii

        See https://aka.ms/azsdk/textanalytics/data-limits for service data limits.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or list[dict[str, str]]
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language. See https://aka.ms/talangs for
            supported languages in Language API.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :keyword domain_filter: Filters the response entities to ones only included in the specified domain.
            I.e., if set to 'phi', will only return entities in the Protected Healthcare Information domain.
            See https://aka.ms/azsdk/language/pii for more information.
        :paramtype domain_filter: str or ~azure.ai.textanalytics.PiiEntityDomain
        :keyword categories_filter: Instead of filtering over all PII entity categories, you can pass in a list of
            the specific PII entity categories you want to filter out. For example, if you only want to filter out
            U.S. social security numbers in a document, you can pass in
            `[PiiEntityCategory.US_SOCIAL_SECURITY_NUMBER]` for this kwarg.
        :paramtype categories_filter: list[str or ~azure.ai.textanalytics.PiiEntityCategory]
        :keyword str string_index_type: Specifies the method used to interpret string offsets.
            `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
            you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
            see https://aka.ms/text-analytics-offsets
        :keyword bool disable_service_logs: Defaults to true, meaning that the Language service will not log your
            input text on the service side for troubleshooting. If set to False, the Language service logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the service's natural language processing functions. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :return: The combined list of :class:`~azure.ai.textanalytics.RecognizePiiEntitiesResult`
            and :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents
            were passed in.
        :rtype: list[~azure.ai.textanalytics.RecognizePiiEntitiesResult or ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. versionadded:: v3.1
            The *recognize_pii_entities* client method.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_pii_entities.py
                :start-after: [START recognize_pii_entities]
                :end-before: [END recognize_pii_entities]
                :language: python
                :dedent: 4
                :caption: Recognize personally identifiable information entities in a batch of documents.
        """
        language_arg = language if language is not None else self._default_language
        docs = _validate_input(documents, "language", language_arg)
        string_index_type_arg = string_index_type if string_index_type is not None else self._string_index_type_default

        try:
            if is_language_api(self._api_version):
                models = self._client.models(api_version=self._api_version)
                return cast(
                    List[Union[RecognizePiiEntitiesResult, DocumentError]],
                    self._client.analyze_text(
                        body=models.AnalyzeTextPiiEntitiesRecognitionInput(
                            analysis_input={"documents": docs},
                            parameters=models.PiiTaskParameters(
                                logging_opt_out=disable_service_logs,
                                model_version=model_version,
                                domain=domain_filter,
                                pii_categories=categories_filter,
                                string_index_type=string_index_type_compatibility(string_index_type_arg)
                            )
                        ),
                        show_stats=show_stats,
                        cls=kwargs.pop("cls", pii_entities_result),
                        **kwargs
                    )
                )

            # api_versions 3.0, 3.1
            return cast(
                List[Union[RecognizePiiEntitiesResult, DocumentError]],
                self._client.entities_recognition_pii(
                    documents=docs,
                    model_version=model_version,
                    show_stats=show_stats,
                    domain=domain_filter,
                    pii_categories=categories_filter,
                    logging_opt_out=disable_service_logs,
                    string_index_type=string_index_type_arg,
                    cls=kwargs.pop("cls", pii_entities_result),
                    **kwargs
                )
            )
        except HttpResponseError as error:
            return process_http_response_error(error)

    @distributed_trace
    @validate_multiapi_args(
        version_method_added="v3.0",
        args_mapping={"v3.1": ["string_index_type", "disable_service_logs"]}
    )
    def recognize_linked_entities(
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        *,
        disable_service_logs: Optional[bool] = None,
        language: Optional[str] = None,
        model_version: Optional[str] = None,
        show_stats: Optional[bool] = None,
        string_index_type: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Union[RecognizeLinkedEntitiesResult, DocumentError]]:
        """Recognize linked entities from a well-known knowledge base for a batch of documents.

        Identifies and disambiguates the identity of each entity found in text (for example,
        determining whether an occurrence of the word Mars refers to the planet, or to the
        Roman god of war). Recognized entities are associated with URLs to a well-known
        knowledge base, like Wikipedia.

        See https://aka.ms/azsdk/textanalytics/data-limits for service data limits.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or list[dict[str, str]]
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language. See https://aka.ms/talangs for
            supported languages in Language API.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :keyword str string_index_type: Specifies the method used to interpret string offsets.
            `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
            you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
            see https://aka.ms/text-analytics-offsets
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, the Language service logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the service's natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :return: The combined list of :class:`~azure.ai.textanalytics.RecognizeLinkedEntitiesResult`
            and :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents
            were passed in.
        :rtype: list[~azure.ai.textanalytics.RecognizeLinkedEntitiesResult or ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. versionadded:: v3.1
            The *disable_service_logs* and *string_index_type* keyword arguments.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_linked_entities.py
                :start-after: [START recognize_linked_entities]
                :end-before: [END recognize_linked_entities]
                :language: python
                :dedent: 4
                :caption: Recognize linked entities in a batch of documents.
        """

        language_arg = language if language is not None else self._default_language
        docs = _validate_input(documents, "language", language_arg)
        string_index_type_arg = string_index_type if string_index_type is not None else self._string_index_type_default

        try:
            if is_language_api(self._api_version):
                models = self._client.models(api_version=self._api_version)
                return cast(
                    List[Union[RecognizeLinkedEntitiesResult, DocumentError]],
                    self._client.analyze_text(
                        body=models.AnalyzeTextEntityLinkingInput(
                            analysis_input={"documents": docs},
                            parameters=models.EntityLinkingTaskParameters(
                                logging_opt_out=disable_service_logs,
                                model_version=model_version,
                                string_index_type=string_index_type_compatibility(string_index_type_arg)
                            )
                        ),
                        show_stats=show_stats,
                        cls=kwargs.pop("cls", linked_entities_result),
                        **kwargs
                    )
                )

            # api_versions 3.0, 3.1
            return cast(
                List[Union[RecognizeLinkedEntitiesResult, DocumentError]],
                self._client.entities_linking(
                    documents=docs,
                    logging_opt_out=disable_service_logs,
                    model_version=model_version,
                    string_index_type=string_index_type_arg,
                    show_stats=show_stats,
                    cls=kwargs.pop("cls", linked_entities_result),
                    **kwargs
                )
            )
        except HttpResponseError as error:
            return process_http_response_error(error)

    # pylint: disable=unused-argument
    def _healthcare_result_callback(
        self, raw_response, deserialized, doc_id_order, task_id_order=None, show_stats=False, bespoke=False
    ):
        if deserialized is None:
            models = self._client.models(api_version=self._api_version)
            response_cls = \
                models.AnalyzeTextJobState if is_language_api(self._api_version) else models.HealthcareJobState
            deserialized = response_cls.deserialize(raw_response)
        return healthcare_paged_result(
            doc_id_order,
            self._client.analyze_text_job_status if is_language_api(self._api_version) else self._client.health_status,
            raw_response,
            deserialized,
            show_stats=show_stats,
        )

    @distributed_trace
    @validate_multiapi_args(
        version_method_added="v3.1",
        args_mapping={
            "2022-10-01-preview": ["fhir_version", "document_type", "auto_detect_language"],
            "2022-05-01": ["display_name"]
        }
    )
    def begin_analyze_healthcare_entities(
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        *,
        auto_detect_language: Optional[bool] = None,
        continuation_token: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        display_name: Optional[str] = None,
        document_type: Optional[Union[str, HealthcareDocumentType]] = None,
        fhir_version: Optional[str] = None,
        language: Optional[str] = None,
        model_version: Optional[str] = None,
        polling_interval: Optional[int] = None,
        show_stats: Optional[bool] = None,
        string_index_type: Optional[str] = None,
        **kwargs: Any,
    ) -> AnalyzeHealthcareEntitiesLROPoller[ItemPaged[Union[AnalyzeHealthcareEntitiesResult, DocumentError]]]:
        """Analyze healthcare entities and identify relationships between these entities in a batch of documents.

        Entities are associated with references that can be found in existing knowledge bases,
        such as UMLS, CHV, MSH, etc.

        We also extract the relations found between entities, for example in "The subject took 100 mg of ibuprofen",
        we would extract the relationship between the "100 mg" dosage and the "ibuprofen" medication.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or list[dict[str, str]]
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default.
            Per-document language will take precedence over whole batch language.
            See https://aka.ms/talangs for supported languages in Language API.
        :keyword bool auto_detect_language: If True, the service will automatically detect the
            language of each text document (Only supported by API version 2022-10-01-preview and newer).
            Optionally use the `language` keyword argument to provide a default/fallback language
            to use for the batch in the event that the service is unable to detect the language.
        :keyword str display_name: An optional display name to set for the requested analysis.
        :keyword str string_index_type: Specifies the method used to interpret string offsets.
            `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
            you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
            see https://aka.ms/text-analytics-offsets
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token:
            Call `continuation_token()` on the poller object to save the long-running operation (LRO)
            state into an opaque token. Pass the value as the `continuation_token` keyword argument
            to restart the LRO from a saved state.
        :keyword bool disable_service_logs: Defaults to true, meaning that the Language service will not log your
            input text on the service side for troubleshooting. If set to False, the Language service logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the service's natural language processing functions. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :keyword str fhir_version: The FHIR Spec version that the result will use to format the fhir_bundle
            on the result object. For additional information see https://www.hl7.org/fhir/overview.html.
            The only acceptable values to pass in are None and "4.0.1". The default value is None.
        :keyword document_type: Document type that can be provided as input for Fhir Documents. Expect to
            have fhir_version provided when used. Behavior of using None enum is the same as not using the
            document_type parameter. Known values are: "None", "ClinicalTrial", "DischargeSummary",
            "ProgressNote", "HistoryAndPhysical", "Consult", "Imaging", "Pathology", and "ProcedureNote".
        :paramtype document_type: str or ~azure.ai.textanalytics.HealthcareDocumentType
        :return: An instance of an AnalyzeHealthcareEntitiesLROPoller. Call `result()` on the this
            object to return a heterogeneous pageable of
            :class:`~azure.ai.textanalytics.AnalyzeHealthcareEntitiesResult` and
            :class:`~azure.ai.textanalytics.DocumentError`.
        :rtype:
            ~azure.ai.textanalytics.AnalyzeHealthcareEntitiesLROPoller[~azure.core.paging.ItemPaged[
            ~azure.ai.textanalytics.AnalyzeHealthcareEntitiesResult or ~azure.ai.textanalytics.DocumentError]]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. versionadded:: v3.1
            The *begin_analyze_healthcare_entities* client method.
        .. versionadded:: 2022-05-01
            The *display_name* keyword argument.
        .. versionadded:: 2022-10-01-preview
            The *fhir_version*, *document_type*, and *auto_detect_language* keyword arguments.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_analyze_healthcare_entities.py
                :start-after: [START analyze_healthcare_entities]
                :end-before: [END analyze_healthcare_entities]
                :language: python
                :dedent: 4
                :caption: Recognize healthcare entities in a batch of documents.
        """

        language_arg = language if language is not None else self._default_language
        polling_interval_arg = polling_interval if polling_interval is not None else 5
        string_index_type_arg = string_index_type if string_index_type is not None else self._string_index_type_default

        if continuation_token:
            return cast(
                AnalyzeHealthcareEntitiesLROPoller[
                    ItemPaged[Union[AnalyzeHealthcareEntitiesResult, DocumentError]]
                ],
                _get_result_from_continuation_token(
                    self._client._client,  # pylint: disable=protected-access
                    continuation_token,
                    AnalyzeHealthcareEntitiesLROPoller,
                    AnalyzeHealthcareEntitiesLROPollingMethod(
                        text_analytics_client=self._client,
                        timeout=polling_interval_arg,
                        **kwargs
                    ),
                    self._healthcare_result_callback
                )
            )
        if auto_detect_language is True:
            docs = _validate_input(documents, "language", "auto")
        else:
            docs = _validate_input(documents, "language", language_arg)
        doc_id_order = [doc.get("id") for doc in docs]
        my_cls = kwargs.pop(
            "cls",
            lambda pipeline_response, deserialized, _: self._healthcare_result_callback(
                pipeline_response, deserialized, doc_id_order, show_stats=show_stats
            ),
        )
        models = self._client.models(api_version=self._api_version)

        try:
            if is_language_api(self._api_version):
                input_docs = models.MultiLanguageAnalysisInput(
                    documents=docs
                )
                return cast(
                    AnalyzeHealthcareEntitiesLROPoller[
                        ItemPaged[Union[AnalyzeHealthcareEntitiesResult, DocumentError]]
                    ],
                    self._client.begin_analyze_text_submit_job(  # type: ignore
                        body=models.AnalyzeTextJobsInput(
                            analysis_input=input_docs,
                            display_name=display_name,
                            default_language=language_arg if auto_detect_language is True else None,
                            tasks=[
                                models.HealthcareLROTask(
                                    task_name="0",
                                    parameters=models.HealthcareTaskParameters(
                                        model_version=model_version,
                                        logging_opt_out=disable_service_logs,
                                        string_index_type=string_index_type_compatibility(string_index_type_arg),
                                        fhir_version=fhir_version,
                                        document_type=document_type,
                                    )
                                )
                            ]
                        ),
                        cls=my_cls,
                        polling=AnalyzeHealthcareEntitiesLROPollingMethod(
                            text_analytics_client=self._client,
                            timeout=polling_interval_arg,
                            show_stats=show_stats,
                            doc_id_order=doc_id_order,
                            lro_algorithms=[
                                TextAnalyticsOperationResourcePolling(
                                    show_stats=show_stats,
                                )
                            ],
                            **kwargs
                        ),
                        continuation_token=continuation_token,
                        poller_cls=AnalyzeHealthcareEntitiesLROPoller,
                        **kwargs
                    )
                )

            # v3.1
            return cast(
                AnalyzeHealthcareEntitiesLROPoller[
                    ItemPaged[Union[AnalyzeHealthcareEntitiesResult, DocumentError]]
                ],
                self._client.begin_health(
                    docs,
                    model_version=model_version,
                    string_index_type=string_index_type_arg,
                    logging_opt_out=disable_service_logs,
                    cls=my_cls,
                    polling=AnalyzeHealthcareEntitiesLROPollingMethod(
                        text_analytics_client=self._client,
                        timeout=polling_interval_arg,
                        doc_id_order=doc_id_order,
                        show_stats=show_stats,
                        lro_algorithms=[
                            TextAnalyticsOperationResourcePolling(
                                show_stats=show_stats,
                            )
                        ],
                        **kwargs
                    ),
                    continuation_token=continuation_token,
                    **kwargs
                )
            )
        except HttpResponseError as error:
            return process_http_response_error(error)

    @distributed_trace
    @validate_multiapi_args(
        version_method_added="v3.0",
        args_mapping={"v3.1": ["disable_service_logs"]}
    )
    def extract_key_phrases(
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        *,
        disable_service_logs: Optional[bool] = None,
        language: Optional[str] = None,
        model_version: Optional[str] = None,
        show_stats: Optional[bool] = None,
        **kwargs: Any
    ) -> List[Union[ExtractKeyPhrasesResult, DocumentError]]:
        """Extract key phrases from a batch of documents.

        Returns a list of strings denoting the key phrases in the input
        text. For example, for the input text "The food was delicious and there
        were wonderful staff", the API returns the main talking points: "food"
        and "wonderful staff"

        See https://aka.ms/azsdk/textanalytics/data-limits for service data limits.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or list[dict[str, str]]
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language. See https://aka.ms/talangs for
            supported languages in Language API.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, the Language service logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the service's natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :return: The combined list of :class:`~azure.ai.textanalytics.ExtractKeyPhrasesResult` and
            :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents were
            passed in.
        :rtype: list[~azure.ai.textanalytics.ExtractKeyPhrasesResult or ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. versionadded:: v3.1
            The *disable_service_logs* keyword argument.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_extract_key_phrases.py
                :start-after: [START extract_key_phrases]
                :end-before: [END extract_key_phrases]
                :language: python
                :dedent: 4
                :caption: Extract the key phrases in a batch of documents.
        """

        language_arg = language if language is not None else self._default_language
        docs = _validate_input(documents, "language", language_arg)

        try:
            if is_language_api(self._api_version):
                models = self._client.models(api_version=self._api_version)
                return cast(
                    List[Union[ExtractKeyPhrasesResult, DocumentError]],
                    self._client.analyze_text(
                        body=models.AnalyzeTextKeyPhraseExtractionInput(
                            analysis_input={"documents": docs},
                            parameters=models.KeyPhraseTaskParameters(
                                logging_opt_out=disable_service_logs,
                                model_version=model_version,
                            )
                        ),
                        show_stats=show_stats,
                        cls=kwargs.pop("cls", key_phrases_result),
                        **kwargs
                    )
                )

            # api_versions 3.0, 3.1
            return cast(
                List[Union[ExtractKeyPhrasesResult, DocumentError]],
                self._client.key_phrases(
                    documents=docs,
                    model_version=model_version,
                    show_stats=show_stats,
                    logging_opt_out=disable_service_logs,
                    cls=kwargs.pop("cls", key_phrases_result),
                    **kwargs
                )
            )
        except HttpResponseError as error:
            return process_http_response_error(error)

    @distributed_trace
    @validate_multiapi_args(
        version_method_added="v3.0",
        args_mapping={"v3.1": ["show_opinion_mining", "disable_service_logs", "string_index_type"]}
    )
    def analyze_sentiment(
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        *,
        disable_service_logs: Optional[bool] = None,
        language: Optional[str] = None,
        model_version: Optional[str] = None,
        show_opinion_mining: Optional[bool] = None,
        show_stats: Optional[bool] = None,
        string_index_type: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Union[AnalyzeSentimentResult, DocumentError]]:
        """Analyze sentiment for a batch of documents. Turn on opinion mining with `show_opinion_mining`.

        Returns a sentiment prediction, as well as sentiment scores for
        each sentiment class (Positive, Negative, and Neutral) for the document
        and each sentence within it.

        See https://aka.ms/azsdk/textanalytics/data-limits for service data limits.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or list[dict[str, str]]
        :keyword bool show_opinion_mining: Whether to mine the opinions of a sentence and conduct more
            granular analysis around the aspects of a product or service (also known as
            aspect-based sentiment analysis). If set to true, the returned
            :class:`~azure.ai.textanalytics.SentenceSentiment` objects
            will have property `mined_opinions` containing the result of this analysis. Only available for
            API version v3.1 and up.
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language. See https://aka.ms/talangs for
            supported languages in Language API.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :keyword str string_index_type: Specifies the method used to interpret string offsets.
            `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
            you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
            see https://aka.ms/text-analytics-offsets
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, the Language service logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the service's natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :return: The combined list of :class:`~azure.ai.textanalytics.AnalyzeSentimentResult` and
            :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents were
            passed in.
        :rtype: list[~azure.ai.textanalytics.AnalyzeSentimentResult or ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. versionadded:: v3.1
            The *show_opinion_mining*, *disable_service_logs*, and *string_index_type* keyword arguments.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_analyze_sentiment.py
                :start-after: [START analyze_sentiment]
                :end-before: [END analyze_sentiment]
                :language: python
                :dedent: 4
                :caption: Analyze sentiment in a batch of documents.
        """

        language_arg = language if language is not None else self._default_language
        docs = _validate_input(documents, "language", language_arg)
        string_index_type_arg = string_index_type if string_index_type is not None else self._string_index_type_default

        try:
            if is_language_api(self._api_version):
                models = self._client.models(api_version=self._api_version)
                return cast(
                    List[Union[AnalyzeSentimentResult, DocumentError]],
                    self._client.analyze_text(
                        body=models.AnalyzeTextSentimentAnalysisInput(
                            analysis_input={"documents": docs},
                            parameters=models.SentimentAnalysisTaskParameters(
                                logging_opt_out=disable_service_logs,
                                model_version=model_version,
                                string_index_type=string_index_type_compatibility(string_index_type_arg),
                                opinion_mining=show_opinion_mining,
                            )
                        ),
                        show_stats=show_stats,
                        cls=kwargs.pop("cls", sentiment_result),
                        **kwargs
                    )
                )

            # api_versions 3.0, 3.1
            return cast(
                List[Union[AnalyzeSentimentResult, DocumentError]],
                self._client.sentiment(
                    documents=docs,
                    logging_opt_out=disable_service_logs,
                    model_version=model_version,
                    string_index_type=string_index_type_arg,
                    opinion_mining=show_opinion_mining,
                    show_stats=show_stats,
                    cls=kwargs.pop("cls", sentiment_result),
                    **kwargs
                )
            )
        except HttpResponseError as error:
            return process_http_response_error(error)

    def _analyze_result_callback(
        self, raw_response, deserialized, doc_id_order, task_id_order=None, show_stats=False, bespoke=False
    ):

        if deserialized is None:
            models = self._client.models(api_version=self._api_version)
            response_cls = models.AnalyzeTextJobState if is_language_api(self._api_version) else models.AnalyzeJobState
            deserialized = response_cls.deserialize(raw_response)
        return analyze_paged_result(
            doc_id_order,
            task_id_order,
            self._client.analyze_text_job_status if is_language_api(self._api_version) else self._client.analyze_status,
            raw_response,
            deserialized,
            show_stats=show_stats,
            bespoke=bespoke
        )

    @distributed_trace
    @validate_multiapi_args(
        version_method_added="v3.1",
        custom_wrapper=check_for_unsupported_actions_types,
        args_mapping={
            "2022-10-01-preview": ["auto_detect_language"],
        }
    )
    def begin_analyze_actions(
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        actions: List[
            Union[
                RecognizeEntitiesAction,
                RecognizeLinkedEntitiesAction,
                RecognizePiiEntitiesAction,
                ExtractKeyPhrasesAction,
                AnalyzeSentimentAction,
                RecognizeCustomEntitiesAction,
                SingleLabelClassifyAction,
                MultiLabelClassifyAction,
                AnalyzeHealthcareEntitiesAction,
                ExtractSummaryAction,
                AbstractiveSummaryAction,
            ]
        ],
        *,
        auto_detect_language: Optional[bool] = None,
        continuation_token: Optional[str] = None,
        display_name: Optional[str] = None,
        language: Optional[str] = None,
        polling_interval: Optional[int] = None,
        show_stats: Optional[bool] = None,
        **kwargs: Any,
    ) -> TextAnalysisLROPoller[
        ItemPaged[
            List[
                Union[
                    RecognizeEntitiesResult,
                    RecognizeLinkedEntitiesResult,
                    RecognizePiiEntitiesResult,
                    ExtractKeyPhrasesResult,
                    AnalyzeSentimentResult,
                    RecognizeCustomEntitiesResult,
                    ClassifyDocumentResult,
                    AnalyzeHealthcareEntitiesResult,
                    ExtractSummaryResult,
                    AbstractiveSummaryResult,
                    DocumentError,
                ]
            ]
        ]
    ]:
        """Start a long-running operation to perform a variety of text analysis actions over a batch of documents.

        We recommend you use this function if you're looking to analyze larger documents, and / or
        combine multiple text analysis actions into one call. Otherwise, we recommend you use
        the action specific endpoints, for example :func:`analyze_sentiment`.

        .. note:: The abstractive summarization feature is part of a gated preview. Request access here:
            https://aka.ms/applyforgatedsummarizationfeatures

        .. note:: See the service documentation for regional support of custom action features:
            https://aka.ms/azsdk/textanalytics/customfunctionalities

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or list[dict[str, str]]
        :param actions: A heterogeneous list of actions to perform on the input documents.
            Each action object encapsulates the parameters used for the particular action type.
            The action results will be in the same order of the input actions.
        :type actions:
            list[RecognizeEntitiesAction or RecognizePiiEntitiesAction or ExtractKeyPhrasesAction or
            RecognizeLinkedEntitiesAction or AnalyzeSentimentAction or
            RecognizeCustomEntitiesAction or SingleLabelClassifyAction or
            MultiLabelClassifyAction or AnalyzeHealthcareEntitiesAction or ExtractSummaryAction
            or AbstractiveSummaryAction]
        :keyword str display_name: An optional display name to set for the requested analysis.
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default.
            Per-document language will take precedence over whole batch language.
            See https://aka.ms/talangs for supported languages in Language API.
        :keyword bool auto_detect_language: If True, the service will automatically detect the
            language of each text document (Only supported by API version 2022-10-01-preview and newer).
            Optionally use the `language` keyword argument to provide a default/fallback language
            to use for the batch in the event that the service is unable to detect the language.
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token:
            Call `continuation_token()` on the poller object to save the long-running operation (LRO)
            state into an opaque token. Pass the value as the `continuation_token` keyword argument
            to restart the LRO from a saved state.
        :return: An instance of an TextAnalysisLROPoller. Call `result()` on the poller
            object to return a pageable heterogeneous list of lists. This list of lists is first ordered
            by the documents you input, then ordered by the actions you input. For example,
            if you have documents input ["Hello", "world"], and actions
            :class:`~azure.ai.textanalytics.RecognizeEntitiesAction` and
            :class:`~azure.ai.textanalytics.AnalyzeSentimentAction`, when iterating over the list of lists,
            you will first iterate over the action results for the "Hello" document, getting the
            :class:`~azure.ai.textanalytics.RecognizeEntitiesResult` of "Hello",
            then the :class:`~azure.ai.textanalytics.AnalyzeSentimentResult` of "Hello".
            Then, you will get the :class:`~azure.ai.textanalytics.RecognizeEntitiesResult` and
            :class:`~azure.ai.textanalytics.AnalyzeSentimentResult` of "world".
        :rtype:
            ~azure.ai.textanalytics.TextAnalysisLROPoller[~azure.core.paging.ItemPaged[
            list[RecognizeEntitiesResult or RecognizeLinkedEntitiesResult or RecognizePiiEntitiesResult or
            ExtractKeyPhrasesResult or AnalyzeSentimentResult or RecognizeCustomEntitiesResult
            or ClassifyDocumentResult or AnalyzeHealthcareEntitiesResult or ExtractSummaryResult
            or AbstractiveSummaryResult or DocumentError]]]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. versionadded:: v3.1
            The *begin_analyze_actions* client method.
        .. versionadded:: 2022-05-01
            The *RecognizeCustomEntitiesAction*, *SingleLabelClassifyAction*,
            *MultiLabelClassifyAction*, and *AnalyzeHealthcareEntitiesAction* input options and the
            corresponding *RecognizeCustomEntitiesResult*, *ClassifyDocumentResult*,
            and *AnalyzeHealthcareEntitiesResult* result objects
        .. versionadded:: 2022-10-01-preview
            The *ExtractSummaryAction* and *AbstractiveSummaryAction* input options and the corresponding
            *ExtractSummaryResult* and *AbstractiveSummaryResult* result objects.
            The *auto_detect_language* keyword argument.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_analyze_actions.py
                :start-after: [START analyze]
                :end-before: [END analyze]
                :language: python
                :dedent: 4
                :caption: Start a long-running operation to perform a variety of text analysis
                    actions over a batch of documents.
        """

        language_arg = language if language is not None else self._default_language
        polling_interval_arg = polling_interval if polling_interval is not None else 5
        bespoke = kwargs.pop("bespoke", False)

        if continuation_token:
            return cast(
                AnalyzeActionsResponse,
                _get_result_from_continuation_token(
                    self._client._client,  # pylint: disable=protected-access
                    continuation_token,
                    AnalyzeActionsLROPoller,
                    AnalyzeActionsLROPollingMethod(
                        text_analytics_client=self._client,
                        timeout=polling_interval_arg,
                        **kwargs
                    ),
                    self._analyze_result_callback,
                    bespoke
                )
            )

        models = self._client.models(api_version=self._api_version)

        input_model_cls = \
            models.MultiLanguageAnalysisInput if is_language_api(self._api_version) else models.MultiLanguageBatchInput
        if auto_detect_language is True:
            docs = input_model_cls(
                documents=_validate_input(documents, "language", "auto")
            )
        else:
            docs = input_model_cls(
                documents=_validate_input(documents, "language", language_arg)
            )
        doc_id_order = [doc.get("id") for doc in docs.documents]
        try:
            generated_tasks = [
                action._to_generated(self._api_version, str(idx))  # pylint: disable=protected-access
                for idx, action in enumerate(actions)
            ]
        except AttributeError as e:
            raise TypeError("Unsupported action type in list.") from e
        task_order = [(_determine_action_type(a), a.task_name) for a in generated_tasks]
        response_cls = kwargs.pop(
            "cls",
            lambda pipeline_response, deserialized, _:
                self._analyze_result_callback(
                    pipeline_response,
                    deserialized,
                    doc_id_order,
                    task_id_order=task_order,
                    show_stats=show_stats,
                    bespoke=bespoke
                ),
        )

        try:
            if is_language_api(self._api_version):
                return cast(
                    AnalyzeActionsResponse,
                    self._client.begin_analyze_text_submit_job(
                        body=models.AnalyzeTextJobsInput(
                            analysis_input=docs,
                            display_name=display_name,
                            default_language=language_arg if auto_detect_language is True else None,
                            tasks=generated_tasks
                        ),
                        cls=response_cls,
                        polling=AnalyzeActionsLROPollingMethod(
                            text_analytics_client=self._client,
                            timeout=polling_interval_arg,
                            show_stats=show_stats,
                            doc_id_order=doc_id_order,
                            task_id_order=task_order,
                            lro_algorithms=[
                                TextAnalyticsOperationResourcePolling(
                                    show_stats=show_stats,
                                )
                            ],
                            **kwargs
                        ),
                        continuation_token=continuation_token,
                        **kwargs
                    )
                )

            # v3.1
            analyze_tasks = models.JobManifestTasks(
                entity_recognition_tasks=[
                    a for a in generated_tasks
                    if _determine_action_type(a) == _AnalyzeActionsType.RECOGNIZE_ENTITIES
                ],
                entity_recognition_pii_tasks=[
                    a for a in generated_tasks
                    if _determine_action_type(a) == _AnalyzeActionsType.RECOGNIZE_PII_ENTITIES
                ],
                key_phrase_extraction_tasks=[
                    a for a in generated_tasks
                    if _determine_action_type(a) == _AnalyzeActionsType.EXTRACT_KEY_PHRASES
                ],
                entity_linking_tasks=[
                    a for a in generated_tasks
                    if _determine_action_type(a) == _AnalyzeActionsType.RECOGNIZE_LINKED_ENTITIES
                ],
                sentiment_analysis_tasks=[
                    a for a in generated_tasks
                    if _determine_action_type(a) == _AnalyzeActionsType.ANALYZE_SENTIMENT
                ],
            )
            analyze_body = models.AnalyzeBatchInput(
                display_name=display_name, tasks=analyze_tasks, analysis_input=docs
            )
            return cast(
                AnalyzeActionsResponse,
                self._client.begin_analyze(
                    body=analyze_body,
                    cls=response_cls,
                    polling=AnalyzeActionsLROPollingMethod(
                        text_analytics_client=self._client,
                        timeout=polling_interval_arg,
                        show_stats=show_stats,
                        doc_id_order=doc_id_order,
                        task_id_order=task_order,
                        lro_algorithms=[
                            TextAnalyticsOperationResourcePolling(
                                show_stats=show_stats,
                            )
                        ],
                        **kwargs
                    ),
                    continuation_token=continuation_token,
                    **kwargs
                )
            )
        except HttpResponseError as error:
            return process_http_response_error(error)

    @distributed_trace
    @validate_multiapi_args(
        version_method_added="2022-05-01",
        args_mapping={
            "2022-10-01-preview": ["auto_detect_language"],
        }
    )
    def begin_recognize_custom_entities(
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        project_name: str,
        deployment_name: str,
        *,
        auto_detect_language: Optional[bool] = None,
        continuation_token: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        display_name: Optional[str] = None,
        language: Optional[str] = None,
        polling_interval: Optional[int] = None,
        show_stats: Optional[bool] = None,
        string_index_type: Optional[str] = None,
        **kwargs: Any,
    ) -> TextAnalysisLROPoller[ItemPaged[Union[RecognizeCustomEntitiesResult, DocumentError]]]:
        """Start a long-running custom named entity recognition operation.

        For information on regional support of custom features and how to train a model to
        recognize custom entities, see https://aka.ms/azsdk/textanalytics/customentityrecognition

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or list[dict[str, str]]
        :param str project_name: Required. This field indicates the project name for the model.
        :param str deployment_name: This field indicates the deployment name for the model.
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default.
            Per-document language will take precedence over whole batch language.
            See https://aka.ms/talangs for supported languages in Language API.
        :keyword bool auto_detect_language: If True, the service will automatically detect the
            language of each text document (Only supported by API version 2022-10-01-preview and newer).
            Optionally use the `language` keyword argument to provide a default/fallback language
            to use for the batch in the event that the service is unable to detect the language.
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, the Language service logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the service's natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :keyword str string_index_type: Specifies the method used to interpret string offsets.
            `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
            you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
            see https://aka.ms/text-analytics-offsets
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token:
            Call `continuation_token()` on the poller object to save the long-running operation (LRO)
            state into an opaque token. Pass the value as the `continuation_token` keyword argument
            to restart the LRO from a saved state.
        :keyword str display_name: An optional display name to set for the requested analysis.
        :return: An instance of an TextAnalysisLROPoller. Call `result()` on the this
            object to return a heterogeneous pageable of
            :class:`~azure.ai.textanalytics.RecognizeCustomEntitiesResult` and
            :class:`~azure.ai.textanalytics.DocumentError`.
        :rtype:
            ~azure.ai.textanalytics.TextAnalysisLROPoller[~azure.core.paging.ItemPaged[
            ~azure.ai.textanalytics.RecognizeCustomEntitiesResult or ~azure.ai.textanalytics.DocumentError]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: 2022-05-01
            The *begin_recognize_custom_entities* client method.
        .. versionadded:: 2022-10-01-preview
            The *auto_detect_language* keyword argument.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_custom_entities.py
                :start-after: [START recognize_custom_entities]
                :end-before: [END recognize_custom_entities]
                :language: python
                :dedent: 4
                :caption: Recognize custom entities in a batch of documents.
        """

        polling_interval_arg = polling_interval if polling_interval is not None else 5
        string_index_type_arg = string_index_type if string_index_type is not None else self._string_index_type_default

        if continuation_token:
            return cast(
                TextAnalysisLROPoller[ItemPaged[Union[RecognizeCustomEntitiesResult, DocumentError]]],
                _get_result_from_continuation_token(
                    self._client._client,  # pylint: disable=protected-access
                    continuation_token,
                    AnalyzeActionsLROPoller,
                    AnalyzeActionsLROPollingMethod(
                        text_analytics_client=self._client,
                        timeout=polling_interval_arg,
                        **kwargs
                    ),
                    self._analyze_result_callback,
                    bespoke=True
                )
            )

        try:
            return cast(
                TextAnalysisLROPoller[
                    ItemPaged[Union[RecognizeCustomEntitiesResult, DocumentError]]
                ],
                self.begin_analyze_actions(
                    documents,
                    actions=[
                        RecognizeCustomEntitiesAction(
                            project_name=project_name,
                            deployment_name=deployment_name,
                            string_index_type=string_index_type_arg,
                            disable_service_logs=disable_service_logs
                        )
                    ],
                    auto_detect_language=auto_detect_language,
                    display_name=display_name,
                    show_stats=show_stats,
                    language=language,
                    polling_interval=polling_interval_arg,
                    bespoke=True,
                    **kwargs
                )
            )

        except HttpResponseError as error:
            return process_http_response_error(error)

    @distributed_trace
    @validate_multiapi_args(
        version_method_added="2022-05-01",
        args_mapping={
            "2022-10-01-preview": ["auto_detect_language"],
        }
    )
    def begin_single_label_classify(
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        project_name: str,
        deployment_name: str,
        *,
        auto_detect_language: Optional[bool] = None,
        continuation_token: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        display_name: Optional[str] = None,
        language: Optional[str] = None,
        polling_interval: Optional[int] = None,
        show_stats: Optional[bool] = None,
        **kwargs: Any,
    ) -> TextAnalysisLROPoller[ItemPaged[Union[ClassifyDocumentResult, DocumentError]]]:
        """Start a long-running custom single label classification operation.

        For information on regional support of custom features and how to train a model to
        classify your documents, see https://aka.ms/azsdk/textanalytics/customfunctionalities

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or list[dict[str, str]]
        :param str project_name: Required. This field indicates the project name for the model.
        :param str deployment_name: This field indicates the deployment name for the model.
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default.
            Per-document language will take precedence over whole batch language.
            See https://aka.ms/talangs for supported languages in Language API.
        :keyword bool auto_detect_language: If True, the service will automatically detect the
            language of each text document (Only supported by API version 2022-10-01-preview and newer).
            Optionally use the `language` keyword argument to provide a default/fallback language
            to use for the batch in the event that the service is unable to detect the language.
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, the Language service logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the service's natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token:
            Call `continuation_token()` on the poller object to save the long-running operation (LRO)
            state into an opaque token. Pass the value as the `continuation_token` keyword argument
            to restart the LRO from a saved state.
        :keyword str display_name: An optional display name to set for the requested analysis.
        :return: An instance of an TextAnalysisLROPoller. Call `result()` on the this
            object to return a heterogeneous pageable of
            :class:`~azure.ai.textanalytics.ClassifyDocumentResult` and
            :class:`~azure.ai.textanalytics.DocumentError`.
        :rtype:
            ~azure.ai.textanalytics.TextAnalysisLROPoller[~azure.core.paging.ItemPaged[
            ~azure.ai.textanalytics.ClassifyDocumentResult or ~azure.ai.textanalytics.DocumentError]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: 2022-05-01
            The *begin_single_label_classify* client method.
        .. versionadded:: 2022-10-01-preview
            The *auto_detect_language* keyword argument.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_single_label_classify.py
                :start-after: [START single_label_classify]
                :end-before: [END single_label_classify]
                :language: python
                :dedent: 4
                :caption: Perform single label classification on a batch of documents.
        """

        polling_interval_arg = polling_interval if polling_interval is not None else 5

        if continuation_token:
            return cast(
                TextAnalysisLROPoller[ItemPaged[Union[ClassifyDocumentResult, DocumentError]]],
                _get_result_from_continuation_token(
                    self._client._client,  # pylint: disable=protected-access
                    continuation_token,
                    AnalyzeActionsLROPoller,
                    AnalyzeActionsLROPollingMethod(
                        text_analytics_client=self._client,
                        timeout=polling_interval_arg,
                        **kwargs
                    ),
                    self._analyze_result_callback,
                    bespoke=True
                )
            )

        try:
            return cast(
                TextAnalysisLROPoller[
                    ItemPaged[Union[ClassifyDocumentResult, DocumentError]]
                ],
                self.begin_analyze_actions(
                    documents,
                    actions=[
                        SingleLabelClassifyAction(
                            project_name=project_name,
                            deployment_name=deployment_name,
                            disable_service_logs=disable_service_logs
                        )
                    ],
                    polling_interval=polling_interval_arg,
                    auto_detect_language=auto_detect_language,
                    display_name=display_name,
                    show_stats=show_stats,
                    language=language,
                    bespoke=True,
                    **kwargs
                )
            )

        except HttpResponseError as error:
            return process_http_response_error(error)

    @distributed_trace
    @validate_multiapi_args(
        version_method_added="2022-05-01",
        args_mapping={
            "2022-10-01-preview": ["auto_detect_language"],
        }
    )
    def begin_multi_label_classify(
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        project_name: str,
        deployment_name: str,
        *,
        auto_detect_language: Optional[bool] = None,
        continuation_token: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        display_name: Optional[str] = None,
        language: Optional[str] = None,
        polling_interval: Optional[int] = None,
        show_stats: Optional[bool] = None,
        **kwargs: Any,
    ) -> TextAnalysisLROPoller[ItemPaged[Union[ClassifyDocumentResult, DocumentError]]]:
        """Start a long-running custom multi label classification operation.

        For information on regional support of custom features and how to train a model to
        classify your documents, see https://aka.ms/azsdk/textanalytics/customfunctionalities

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or list[dict[str, str]]
        :param str project_name: Required. This field indicates the project name for the model.
        :param str deployment_name: This field indicates the deployment name for the model.
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default.
            Per-document language will take precedence over whole batch language.
            See https://aka.ms/talangs for supported languages in Language API.
        :keyword bool auto_detect_language: If True, the service will automatically detect the
            language of each text document (Only supported by API version 2022-10-01-preview and newer).
            Optionally use the `language` keyword argument to provide a default/fallback language
            to use for the batch in the event that the service is unable to detect the language.
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, the Language service logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the service's natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token:
            Call `continuation_token()` on the poller object to save the long-running operation (LRO)
            state into an opaque token. Pass the value as the `continuation_token` keyword argument
            to restart the LRO from a saved state.
        :keyword str display_name: An optional display name to set for the requested analysis.
        :return: An instance of an TextAnalysisLROPoller. Call `result()` on the this
            object to return a heterogeneous pageable of
            :class:`~azure.ai.textanalytics.ClassifyDocumentResult` and
            :class:`~azure.ai.textanalytics.DocumentError`.
        :rtype:
            ~azure.ai.textanalytics.TextAnalysisLROPoller[~azure.core.paging.ItemPaged[
            ~azure.ai.textanalytics.ClassifyDocumentResult or ~azure.ai.textanalytics.DocumentError]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: 2022-05-01
            The *begin_multi_label_classify* client method.
        .. versionadded:: 2022-10-01-preview
            The *auto_detect_language* keyword argument.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_multi_label_classify.py
                :start-after: [START multi_label_classify]
                :end-before: [END multi_label_classify]
                :language: python
                :dedent: 4
                :caption: Perform multi label classification on a batch of documents.
        """

        polling_interval_arg = polling_interval if polling_interval is not None else 5

        if continuation_token:
            return cast(
                TextAnalysisLROPoller[ItemPaged[Union[ClassifyDocumentResult, DocumentError]]],
                _get_result_from_continuation_token(
                    self._client._client,  # pylint: disable=protected-access
                    continuation_token,
                    AnalyzeActionsLROPoller,
                    AnalyzeActionsLROPollingMethod(
                        text_analytics_client=self._client,
                        timeout=polling_interval_arg,
                        **kwargs
                    ),
                    self._analyze_result_callback,
                    bespoke=True
                )
            )

        try:
            return cast(
                TextAnalysisLROPoller[
                    ItemPaged[Union[ClassifyDocumentResult, DocumentError]]
                ],
                self.begin_analyze_actions(
                    documents,
                    actions=[
                        MultiLabelClassifyAction(
                            project_name=project_name,
                            deployment_name=deployment_name,
                            disable_service_logs=disable_service_logs
                        )
                    ],
                    polling_interval=polling_interval_arg,
                    auto_detect_language=auto_detect_language,
                    display_name=display_name,
                    show_stats=show_stats,
                    language=language,
                    bespoke=True,
                    **kwargs
                )
            )

        except HttpResponseError as error:
            return process_http_response_error(error)

    @distributed_trace
    @validate_multiapi_args(
        version_method_added="2022-10-01-preview",
    )
    def dynamic_classification(
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        categories: List[str],
        *,
        classification_type: Optional[Union[str, ClassificationType]] = None,
        disable_service_logs: Optional[bool] = None,
        language: Optional[str] = None,
        model_version: Optional[str] = None,
        show_stats: Optional[bool] = None,
        **kwargs: Any,
    ) -> List[Union[DynamicClassificationResult, DocumentError]]:
        """Perform dynamic classification on a batch of documents.

        On the fly classification of the input documents into one or multiple categories.
        Assigns either one or multiple categories per document. This type of classification
        doesn't require model training.

        .. note:: The dynamic classification feature is part of a gated preview. Request access here:
            https://aka.ms/applyforgatedlanguagefeature

        See https://aka.ms/azsdk/textanalytics/data-limits for service data limits.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list
            of dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`,
            like `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or list[dict[str, str]]
        :param list[str] categories: A list of categories to which input is classified to.
        :keyword classification_type: Specifies either one or multiple categories per document. Defaults
            to multi classification which may return more than one class for each document. Known values
            are: "Single" and "Multi".
        :paramtype classification_type: str or ~azure.ai.textanalytics.ClassificationType
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language. See https://aka.ms/talangs for
            supported languages in Language API.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, the Language service logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the service's natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :return: The combined list of :class:`~azure.ai.textanalytics.DynamicClassificationResult` and
            :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents
            were passed in.
        :rtype: list[~azure.ai.textanalytics.DynamicClassificationResult or ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: 2022-10-01-preview
            The *dynamic_classification* client method.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_dynamic_classification.py
                :start-after: [START dynamic_classification]
                :end-before: [END dynamic_classification]
                :language: python
                :dedent: 4
                :caption: Perform dynamic classification on a batch of documents.
        """

        language_arg = language if language is not None else self._default_language
        docs = _validate_input(documents, "language", language_arg)

        try:
            models = self._client.models(api_version=self._api_version)
            return cast(
                List[Union[DynamicClassificationResult, DocumentError]],
                self._client.analyze_text(
                    body=models.AnalyzeTextDynamicClassificationInput(
                        analysis_input={"documents": docs},
                        parameters=models.DynamicClassificationTaskParameters(
                            categories=categories,
                            logging_opt_out=disable_service_logs,
                            model_version=model_version,
                            classification_type=classification_type,
                        )
                    ),
                    show_stats=show_stats,
                    cls=kwargs.pop("cls", dynamic_classification_result),
                    **kwargs
                )
            )
        except HttpResponseError as error:
            return process_http_response_error(error)

    @distributed_trace
    @validate_multiapi_args(
        version_method_added="2022-10-01-preview"
    )
    def begin_extract_summary(
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        *,
        auto_detect_language: Optional[bool] = None,
        continuation_token: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        display_name: Optional[str] = None,
        language: Optional[str] = None,
        polling_interval: Optional[int] = None,
        show_stats: Optional[bool] = None,
        model_version: Optional[str] = None,
        string_index_type: Optional[str] = None,
        max_sentence_count: Optional[int] = None,
        order_by: Optional[str] = None,
        **kwargs: Any,
    ) -> TextAnalysisLROPoller[ItemPaged[Union[ExtractSummaryResult, DocumentError]]]:
        """Start a long-running extractive summarization operation.

        For a conceptual discussion of extractive summarization, see the service documentation:
        https://learn.microsoft.com/azure/cognitive-services/language-service/summarization/overview

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or list[dict[str, str]]
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default.
            Per-document language will take precedence over whole batch language.
            See https://aka.ms/talangs for supported languages in Language API.
        :keyword bool auto_detect_language: If True, the service will automatically detect the
            language of each text document (Only supported by API version 2022-10-01-preview and newer).
            Optionally use the `language` keyword argument to provide a default/fallback language
            to use for the batch in the event that the service is unable to detect the language.
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :keyword Optional[int] max_sentence_count: Maximum number of sentences to return. Defaults to 3.
        :keyword Optional[str] order_by:  Possible values include: "Offset", "Rank". Default value: "Offset".
        :keyword Optional[str] model_version: The model version to use for the analysis.
        :keyword Optional[str] string_index_type: Specifies the method used to interpret string offsets.
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, the Language service logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the service's natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token:
            Call `continuation_token()` on the poller object to save the long-running operation (LRO)
            state into an opaque token. Pass the value as the `continuation_token` keyword argument
            to restart the LRO from a saved state.
        :keyword str display_name: An optional display name to set for the requested analysis.
        :return: An instance of an TextAnalysisLROPoller. Call `result()` on the this
            object to return a heterogeneous pageable of
            :class:`~azure.ai.textanalytics.ExtractSummaryResult` and
            :class:`~azure.ai.textanalytics.DocumentError`.
        :rtype:
            ~azure.ai.textanalytics.TextAnalysisLROPoller[~azure.core.paging.ItemPaged[
            ~azure.ai.textanalytics.ExtractSummaryResult or ~azure.ai.textanalytics.DocumentError]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: 2022-10-01-preview
            The *begin_extract_summary* client method.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_extract_summary.py
                :start-after: [START extract_summary]
                :end-before: [END extract_summary]
                :language: python
                :dedent: 4
                :caption: Perform extractive summarization on a batch of documents.
        """

        polling_interval_arg = polling_interval if polling_interval is not None else 5
        string_index_type_arg = string_index_type if string_index_type is not None else self._string_index_type_default

        if continuation_token:
            return cast(
                TextAnalysisLROPoller[ItemPaged[Union[ExtractSummaryResult, DocumentError]]],
                _get_result_from_continuation_token(
                    self._client._client,  # pylint: disable=protected-access
                    continuation_token,
                    AnalyzeActionsLROPoller,
                    AnalyzeActionsLROPollingMethod(
                        text_analytics_client=self._client,
                        timeout=polling_interval_arg,
                        **kwargs
                    ),
                    self._analyze_result_callback,
                    bespoke=True
                )
            )

        try:
            return cast(
                TextAnalysisLROPoller[
                    ItemPaged[Union[ExtractSummaryResult, DocumentError]]
                ],
                self.begin_analyze_actions(
                    documents,
                    actions=[
                        ExtractSummaryAction(
                            model_version=model_version,
                            string_index_type=string_index_type_arg,
                            max_sentence_count=max_sentence_count,
                            order_by=order_by,
                            disable_service_logs=disable_service_logs,
                        )
                    ],
                    polling_interval=polling_interval_arg,
                    auto_detect_language=auto_detect_language,
                    display_name=display_name,
                    show_stats=show_stats,
                    language=language,
                    bespoke=True,
                    **kwargs
                )
            )

        except HttpResponseError as error:
            return process_http_response_error(error)

    @distributed_trace
    @validate_multiapi_args(
        version_method_added="2022-10-01-preview"
    )
    def begin_abstractive_summary(
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        *,
        auto_detect_language: Optional[bool] = None,
        continuation_token: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        display_name: Optional[str] = None,
        language: Optional[str] = None,
        polling_interval: Optional[int] = None,
        show_stats: Optional[bool] = None,
        model_version: Optional[str] = None,
        string_index_type: Optional[str] = None,
        sentence_count: Optional[int] = None,
        **kwargs: Any,
    ) -> TextAnalysisLROPoller[ItemPaged[Union[AbstractiveSummaryResult, DocumentError]]]:
        """Start a long-running abstractive summarization operation.

        For a conceptual discussion of abstractive summarization, see the service documentation:
        https://learn.microsoft.com/azure/cognitive-services/language-service/summarization/overview

        .. note:: The abstractive summarization feature is part of a gated preview. Request access here:
            https://aka.ms/applyforgatedsummarizationfeatures

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or list[dict[str, str]]
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default.
            Per-document language will take precedence over whole batch language.
            See https://aka.ms/talangs for supported languages in Language API.
        :keyword bool auto_detect_language: If True, the service will automatically detect the
            language of each text document (Only supported by API version 2022-10-01-preview and newer).
            Optionally use the `language` keyword argument to provide a default/fallback language
            to use for the batch in the event that the service is unable to detect the language.
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :keyword Optional[int] sentence_count: It controls the approximate number of sentences in the output summaries.
        :keyword Optional[str] model_version: The model version to use for the analysis.
        :keyword Optional[str] string_index_type: Specifies the method used to interpret string offsets.
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, the Language service logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the service's natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token:
            Call `continuation_token()` on the poller object to save the long-running operation (LRO)
            state into an opaque token. Pass the value as the `continuation_token` keyword argument
            to restart the LRO from a saved state.
        :keyword str display_name: An optional display name to set for the requested analysis.
        :return: An instance of an TextAnalysisLROPoller. Call `result()` on the this
            object to return a heterogeneous pageable of
            :class:`~azure.ai.textanalytics.AbstractiveSummaryResult` and
            :class:`~azure.ai.textanalytics.DocumentError`.
        :rtype:
            ~azure.ai.textanalytics.TextAnalysisLROPoller[~azure.core.paging.ItemPaged[
            ~azure.ai.textanalytics.AbstractiveSummaryResult or ~azure.ai.textanalytics.DocumentError]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: 2022-10-01-preview
            The *begin_abstractive_summary* client method.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_abstractive_summary.py
                :start-after: [START abstractive_summary]
                :end-before: [END abstractive_summary]
                :language: python
                :dedent: 4
                :caption: Perform abstractive summarization on a batch of documents.
        """

        polling_interval_arg = polling_interval if polling_interval is not None else 5
        string_index_type_arg = string_index_type if string_index_type is not None else self._string_index_type_default

        if continuation_token:
            return cast(
                TextAnalysisLROPoller[ItemPaged[Union[AbstractiveSummaryResult, DocumentError]]],
                _get_result_from_continuation_token(
                    self._client._client,  # pylint: disable=protected-access
                    continuation_token,
                    AnalyzeActionsLROPoller,
                    AnalyzeActionsLROPollingMethod(
                        text_analytics_client=self._client,
                        timeout=polling_interval_arg,
                        **kwargs
                    ),
                    self._analyze_result_callback,
                    bespoke=True
                )
            )

        try:
            return cast(
                TextAnalysisLROPoller[
                    ItemPaged[Union[AbstractiveSummaryResult, DocumentError]]
                ],
                self.begin_analyze_actions(
                    documents,
                    actions=[
                        AbstractiveSummaryAction(
                            model_version=model_version,
                            string_index_type=string_index_type_arg,
                            sentence_count=sentence_count,
                            disable_service_logs=disable_service_logs,
                        )
                    ],
                    polling_interval=polling_interval_arg,
                    auto_detect_language=auto_detect_language,
                    display_name=display_name,
                    show_stats=show_stats,
                    language=language,
                    bespoke=True,
                    **kwargs
                )
            )

        except HttpResponseError as error:
            return process_http_response_error(error)

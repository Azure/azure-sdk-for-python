# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._generated.v3_0.models._models import LanguageInput
from ._generated.v3_0.models._models import MultiLanguageInput


class DictMixin(object):

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, key):
        self.__dict__[key] = None

    def __eq__(self, other):
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        """Compare objects by comparing all attributes."""
        return not self.__eq__(other)

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if not k.startswith('_')})

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return [k for k in self.__dict__ if not k.startswith('_')]

    def values(self):
        return [v for k, v in self.__dict__.items() if not k.startswith('_')]

    def items(self):
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith('_')]

    def get(self, key, default=None):
        if key in self.__dict__:
            return self.__dict__[key]
        return default


class DetectedLanguage(DictMixin):
    """DetectedLanguage contains the predicted language found in text,
    its confidence score, and ISO 639-1 representation.

    :ivar name: Long name of a detected language (e.g. English,
        French).
    :vartype name: str
    :ivar iso6391_name: A two letter representation of the detected
        language according to the ISO 639-1 standard (e.g. en, fr).
    :vartype iso6391_name: str
    :ivar confidence_score: A confidence score between 0 and 1. Scores close
        to 1 indicate 100% certainty that the identified language is true.
    :vartype confidence_score: float
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.iso6391_name = kwargs.get("iso6391_name", None)
        self.confidence_score = kwargs.get("confidence_score", None)

    @classmethod
    def _from_generated(cls, language):
        return cls(
            name=language.name, iso6391_name=language.iso6391_name, confidence_score=language.confidence_score
        )

    def __repr__(self):
        return "DetectedLanguage(name={}, iso6391_name={}, confidence_score={})" \
            .format(self.name, self.iso6391_name, self.confidence_score)[:1024]


class RecognizeEntitiesResult(DictMixin):
    """RecognizeEntitiesResult is a result object which contains
    the recognized entities from a particular document.

    :ivar id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :vartype id: str
    :ivar entities: Recognized entities in the document.
    :vartype entities:
        list[~azure.ai.textanalytics.CategorizedEntity]
    :ivar warnings: Warnings encountered while processing document. Results will still be returned
     if there are warnings, but they may not be fully accurate.
    :vartype warnings: list[~azure.ai.textanalytics.TextAnalyticsWarning]
    :ivar statistics: If show_stats=true was specified in the request this
        field will contain information about the document payload.
    :vartype statistics:
        ~azure.ai.textanalytics.TextDocumentStatistics
    :ivar bool is_error: Boolean check for error item when iterating over list of
        results. Always False for an instance of a RecognizeEntitiesResult.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.entities = kwargs.get("entities", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False

    def __repr__(self):
        return "RecognizeEntitiesResult(id={}, entities={}, warnings={}, statistics={}, is_error={})" \
            .format(self.id, repr(self.entities), repr(self.warnings), repr(self.statistics), self.is_error)[:1024]


class DetectLanguageResult(DictMixin):
    """DetectLanguageResult is a result object which contains
    the detected language of a particular document.

    :ivar id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :vartype id: str
    :ivar primary_language: The primary language detected in the document.
    :vartype primary_language: ~azure.ai.textanalytics.DetectedLanguage
    :ivar warnings: Warnings encountered while processing document. Results will still be returned
     if there are warnings, but they may not be fully accurate.
    :vartype warnings: list[~azure.ai.textanalytics.TextAnalyticsWarning]
    :ivar statistics: If show_stats=true was specified in the request this
        field will contain information about the document payload.
    :vartype statistics:
        ~azure.ai.textanalytics.TextDocumentStatistics
    :ivar bool is_error: Boolean check for error item when iterating over list of
        results. Always False for an instance of a DetectLanguageResult.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.primary_language = kwargs.get("primary_language", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False

    def __repr__(self):
        return "DetectLanguageResult(id={}, primary_language={}, warnings={}, statistics={}, "\
            "is_error={})".format(self.id, repr(self.primary_language), repr(self.warnings),
            repr(self.statistics), self.is_error)[:1024]


class CategorizedEntity(DictMixin):
    """CategorizedEntity contains information about a particular
    entity found in text.

    :ivar text: Entity text as appears in the request.
    :vartype text: str
    :ivar category: Entity category, such as Person/Location/Org/SSN etc
    :vartype category: str
    :ivar subcategory: Entity subcategory, such as Age/Year/TimeRange etc
    :vartype subcategory: str
    :ivar confidence_score: Confidence score between 0 and 1 of the extracted
        entity.
    :vartype confidence_score: float
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get('text', None)
        self.category = kwargs.get('category', None)
        self.subcategory = kwargs.get('subcategory', None)
        self.confidence_score = kwargs.get('confidence_score', None)

    @classmethod
    def _from_generated(cls, entity):
        return cls(
            text=entity.text,
            category=entity.category,
            subcategory=entity.subcategory,
            confidence_score=entity.confidence_score,
        )

    def __repr__(self):
        return "CategorizedEntity(text={}, category={}, subcategory={}, confidence_score={})".format(
            self.text, self.category, self.subcategory, self.confidence_score
        )[:1024]


class TextAnalyticsError(DictMixin):
    """TextAnalyticsError contains the error code, message, and
    other details that explain why the batch or individual document
    failed to be processed by the service.

    :ivar code: Error code. Possible values include:
     'invalidRequest', 'invalidArgument', 'internalServerError',
     'serviceUnavailable', 'invalidParameterValue', 'invalidRequestBodyFormat',
     'emptyRequest', 'missingInputRecords', 'invalidDocument', 'modelVersionIncorrect',
     'invalidDocumentBatch', 'unsupportedLanguageCode', 'invalidCountryHint'
    :vartype code: str
    :ivar message: Error message.
    :vartype message: str
    :ivar target: Error target.
    :vartype target: str
    """

    def __init__(self, **kwargs):
        self.code = kwargs.get('code', None)
        self.message = kwargs.get('message', None)
        self.target = kwargs.get('target', None)

    @classmethod
    def _from_generated(cls, err):
        if err.innererror:
            return cls(
                code=err.innererror.code,
                message=err.innererror.message,
                target=err.innererror.target
            )
        return cls(
            code=err.code,
            message=err.message,
            target=err.target
        )

    def __repr__(self):
        return "TextAnalyticsError(code={}, message={}, target={})" \
            .format(self.code, self.message, self.target)[:1024]

class TextAnalyticsWarning(DictMixin):
    """TextAnalyticsWarning contains the warning code and message that explains why
    the response has a warning.

    :ivar code: Warning code. Possible values include: 'LongWordsInDocument',
     'DocumentTruncated'.
    :vartype code: str
    :ivar message: Warning message.
    :vartype message: str
    """

    def __init__(self, **kwargs):
        self.code = kwargs.get('code', None)
        self.message = kwargs.get('message', None)

    @classmethod
    def _from_generated(cls, warning):
        return cls(
            code=warning.code,
            message=warning.message,
        )

    def __repr__(self):
        return "TextAnalyticsWarning(code={}, message={})" \
            .format(self.code, self.message)[:1024]


class ExtractKeyPhrasesResult(DictMixin):
    """ExtractKeyPhrasesResult is a result object which contains
    the key phrases found in a particular document.

    :ivar id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :vartype id: str
    :ivar key_phrases: A list of representative words or phrases.
        The number of key phrases returned is proportional to the number of words
        in the input document.
    :vartype key_phrases: list[str]
    :ivar warnings: Warnings encountered while processing document. Results will still be returned
     if there are warnings, but they may not be fully accurate.
    :vartype warnings: list[~azure.ai.textanalytics.TextAnalyticsWarning]
    :ivar statistics: If show_stats=true was specified in the request this
        field will contain information about the document payload.
    :vartype statistics:
        ~azure.ai.textanalytics.TextDocumentStatistics
    :ivar bool is_error: Boolean check for error item when iterating over list of
        results. Always False for an instance of a ExtractKeyPhrasesResult.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.key_phrases = kwargs.get("key_phrases", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False

    def __repr__(self):
        return "ExtractKeyPhrasesResult(id={}, key_phrases={}, warnings={}, statistics={}, is_error={})" \
            .format(self.id, self.key_phrases, repr(self.warnings), repr(self.statistics), self.is_error)[:1024]


class RecognizeLinkedEntitiesResult(DictMixin):
    """RecognizeLinkedEntitiesResult is a result object which contains
    links to a well-known knowledge base, like for example, Wikipedia or Bing.

    :ivar id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :vartype id: str
    :ivar entities: Recognized well-known entities in the document.
    :vartype entities:
        list[~azure.ai.textanalytics.LinkedEntity]
    :ivar warnings: Warnings encountered while processing document. Results will still be returned
     if there are warnings, but they may not be fully accurate.
    :vartype warnings: list[~azure.ai.textanalytics.TextAnalyticsWarning]
    :ivar statistics: If show_stats=true was specified in the request this
        field will contain information about the document payload.
    :vartype statistics:
        ~azure.ai.textanalytics.TextDocumentStatistics
    :ivar bool is_error: Boolean check for error item when iterating over list of
        results. Always False for an instance of a RecognizeLinkedEntitiesResult.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.entities = kwargs.get("entities", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False

    def __repr__(self):
        return "RecognizeLinkedEntitiesResult(id={}, entities={}, warnings={}, statistics={}, is_error={})" \
            .format(self.id, repr(self.entities), repr(self.warnings), repr(self.statistics), self.is_error)[:1024]


class AnalyzeSentimentResult(DictMixin):
    """AnalyzeSentimentResult is a result object which contains
    the overall predicted sentiment and confidence scores for your document
    and a per-sentence sentiment prediction with scores.

    :ivar id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :vartype id: str
    :ivar sentiment: Predicted sentiment for document (Negative,
        Neutral, Positive, or Mixed). Possible values include: 'positive',
        'neutral', 'negative', 'mixed'
    :vartype sentiment: str
    :ivar warnings: Warnings encountered while processing document. Results will still be returned
     if there are warnings, but they may not be fully accurate.
    :vartype warnings: list[~azure.ai.textanalytics.TextAnalyticsWarning]
    :ivar statistics: If show_stats=true was specified in the request this
        field will contain information about the document payload.
    :vartype statistics:
        ~azure.ai.textanalytics.TextDocumentStatistics
    :ivar confidence_scores: Document level sentiment confidence
        scores between 0 and 1 for each sentiment label.
    :vartype confidence_scores:
        ~azure.ai.textanalytics.SentimentConfidenceScores
    :ivar sentences: Sentence level sentiment analysis.
    :vartype sentences:
        list[~azure.ai.textanalytics.SentenceSentiment]
    :ivar bool is_error: Boolean check for error item when iterating over list of
        results. Always False for an instance of a AnalyzeSentimentResult.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.sentiment = kwargs.get("sentiment", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.confidence_scores = kwargs.get("confidence_scores", None)
        self.sentences = kwargs.get("sentences", None)
        self.is_error = False

    def __repr__(self):
        return "AnalyzeSentimentResult(id={}, sentiment={}, warnings={}, statistics={}, confidence_scores={}, "\
                 "sentences={}, is_error={})".format(
                 self.id, self.sentiment, repr(self.warnings), repr(self.statistics),
                 repr(self.confidence_scores), repr(self.sentences), self.is_error)[:1024]


class TextDocumentStatistics(DictMixin):
    """TextDocumentStatistics contains information about
    the document payload.

    :ivar character_count: Number of text elements recognized in
        the document.
    :vartype character_count: int
    :ivar transaction_count: Number of transactions for the
        document.
    :vartype transaction_count: int
    """

    def __init__(self, **kwargs):
        self.character_count = kwargs.get("character_count", None)
        self.transaction_count = kwargs.get("transaction_count", None)

    @classmethod
    def _from_generated(cls, stats):
        if stats is None:
            return None
        return cls(
            character_count=stats.characters_count,
            transaction_count=stats.transactions_count,
        )

    def __repr__(self):
        return "TextDocumentStatistics(character_count={}, transaction_count={})" \
            .format(self.character_count, self.transaction_count)[:1024]


class DocumentError(DictMixin):
    """DocumentError is an error object which represents an error on
    the individual document.

    :ivar id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :vartype id: str
    :ivar error: The document error.
    :vartype error: ~azure.ai.textanalytics.TextAnalyticsError
    :ivar bool is_error: Boolean check for error item when iterating over list of
        results. Always True for an instance of a DocumentError.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.error = kwargs.get("error", None)
        self.is_error = True

    def __getattr__(self, attr):
        result_set = set()
        result_set.update(
            RecognizeEntitiesResult().keys()
            + DetectLanguageResult().keys() + RecognizeLinkedEntitiesResult().keys()
            + AnalyzeSentimentResult().keys() + ExtractKeyPhrasesResult().keys()
        )
        result_attrs = result_set.difference(DocumentError().keys())
        if attr in result_attrs:
            raise AttributeError(
                "'DocumentError' object has no attribute '{}'. The service was unable to process this document:\n"
                "Document Id: {}\nError: {} - {}\n".
                format(attr, self.id, self.error.code, self.error.message)
            )
        raise AttributeError("'DocumentError' object has no attribute '{}'".format(attr))

    @classmethod
    def _from_generated(cls, doc_err):
        return cls(
            id=doc_err.id,
            error=TextAnalyticsError._from_generated(doc_err.error),  # pylint: disable=protected-access
            is_error=True
        )

    def __repr__(self):
        return "DocumentError(id={}, error={}, is_error={})" \
            .format(self.id, repr(self.error), self.is_error)[:1024]


class DetectLanguageInput(LanguageInput):
    """The input document to be analyzed for detecting language.

    :ivar id: Required. Unique, non-empty document identifier.
    :vartype id: str
    :ivar text: Required. The input text to process.
    :vartype text: str
    :ivar country_hint: A country hint to help better detect
     the language of the text. Accepts two letter country codes
     specified by ISO 3166-1 alpha-2. Defaults to "US". Pass
     in the string "none" to not use a country_hint.
    :vartype country_hint: str
    """

    def __init__(self, **kwargs):
        super(DetectLanguageInput, self).__init__(**kwargs)
        self.id = kwargs.get("id", None)
        self.text = kwargs.get("text", None)
        self.country_hint = kwargs.get("country_hint", None)

    def __repr__(self):
        return "DetectLanguageInput(id={}, text={}, country_hint={})" \
            .format(self.id, self.text, self.country_hint)[:1024]


class LinkedEntity(DictMixin):
    """LinkedEntity contains a link to the well-known recognized
    entity in text. The link comes from a data source like Wikipedia
    or Bing. It additionally includes all of the matches of this
    entity found in the document.

    :ivar name: Entity Linking formal name.
    :vartype name: str
    :ivar matches: List of instances this entity appears in the text.
    :vartype matches:
        list[~azure.ai.textanalytics.LinkedEntityMatch]
    :ivar language: Language used in the data source.
    :vartype language: str
    :ivar data_source_entity_id: Unique identifier of the recognized entity from the data
        source.
    :vartype data_source_entity_id: str
    :ivar url: URL to the entity's page from the data source.
    :vartype url: str
    :ivar data_source: Data source used to extract entity linking,
        such as Wiki/Bing etc.
    :vartype data_source: str
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.matches = kwargs.get("matches", None)
        self.language = kwargs.get("language", None)
        self.data_source_entity_id = kwargs.get("data_source_entity_id", None)
        self.url = kwargs.get("url", None)
        self.data_source = kwargs.get("data_source", None)

    @classmethod
    def _from_generated(cls, entity):
        return cls(
            name=entity.name,
            matches=[LinkedEntityMatch._from_generated(e) for e in entity.matches],  # pylint: disable=protected-access
            language=entity.language,
            data_source_entity_id=entity.id,
            url=entity.url,
            data_source=entity.data_source,
        )

    def __repr__(self):
        return "LinkedEntity(name={}, matches={}, language={}, data_source_entity_id={}, url={}, " \
               "data_source={})".format(self.name, repr(self.matches), self.language, self.data_source_entity_id,
                                        self.url, self.data_source)[:1024]


class LinkedEntityMatch(DictMixin):
    """A match for the linked entity found in text. Provides
    the confidence score of the prediction and where the entity
    was found in the text.

    :ivar confidence_score: If a well-known item is recognized, a
        decimal number denoting the confidence level between 0 and 1 will be
        returned.
    :vartype confidence_score: float
    :ivar text: Entity text as appears in the request.
    :vartype text: str
    """

    def __init__(self, **kwargs):
        self.confidence_score = kwargs.get("confidence_score", None)
        self.text = kwargs.get("text", None)

    @classmethod
    def _from_generated(cls, match):
        return cls(
            confidence_score=match.confidence_score,
            text=match.text
        )

    def __repr__(self):
        return "LinkedEntityMatch(confidence_score={}, text={})".format(
            self.confidence_score, self.text
        )[:1024]


class TextDocumentInput(MultiLanguageInput):
    """The input document to be analyzed by the service.

    :ivar id: Required. A unique, non-empty document identifier.
    :vartype id: str
    :ivar text: Required. The input text to process.
    :vartype text: str
    :ivar language: This is the 2 letter ISO 639-1 representation
     of a language. For example, use "en" for English; "es" for Spanish etc. If
     not set, uses "en" for English as default.
    :vartype language: str
    """

    def __init__(self, **kwargs):
        super(TextDocumentInput, self).__init__(**kwargs)
        self.id = kwargs.get("id", None)
        self.text = kwargs.get("text", None)
        self.language = kwargs.get("language", None)

    def __repr__(self):
        return "TextDocumentInput(id={}, text={}, language={})" \
            .format(self.id, self.text, self.language)[:1024]


class TextDocumentBatchStatistics(DictMixin):
    """TextDocumentBatchStatistics contains information about the
    request payload. Note: This object is not returned
    in the response and needs to be retrieved by a response hook.

    :ivar document_count: Number of documents submitted in the request.
    :vartype document_count: int
    :ivar valid_document_count: Number of valid documents. This
        excludes empty, over-size limit or non-supported languages documents.
    :vartype valid_document_count: int
    :ivar erroneous_document_count: Number of invalid documents.
        This includes empty, over-size limit or non-supported languages documents.
    :vartype erroneous_document_count: int
    :ivar transaction_count: Number of transactions for the request.
    :vartype transaction_count: long
    """

    def __init__(self, **kwargs):
        self.document_count = kwargs.get("document_count", None)
        self.valid_document_count = kwargs.get("valid_document_count", None)
        self.erroneous_document_count = kwargs.get("erroneous_document_count", None)
        self.transaction_count = kwargs.get("transaction_count", None)

    @classmethod
    def _from_generated(cls, statistics):
        if statistics is None:
            return None
        return cls(
            document_count=statistics["documentsCount"],
            valid_document_count=statistics["validDocumentsCount"],
            erroneous_document_count=statistics["erroneousDocumentsCount"],
            transaction_count=statistics["transactionsCount"],
        )

    def __repr__(self):
        return "TextDocumentBatchStatistics(document_count={}, valid_document_count={}, erroneous_document_count={}, " \
               "transaction_count={})".format(self.document_count, self.valid_document_count,
                                              self.erroneous_document_count, self.transaction_count)[:1024]


class SentenceSentiment(DictMixin):
    """SentenceSentiment contains the predicted sentiment and
    confidence scores for each individual sentence in the document.

    :ivar text: The sentence text.
    :vartype text: str
    :ivar sentiment: The predicted Sentiment for the sentence.
        Possible values include: 'positive', 'neutral', 'negative'
    :vartype sentiment: str
    :ivar confidence_scores: The sentiment confidence score between 0
        and 1 for the sentence for all labels.
    :vartype confidence_scores:
        ~azure.ai.textanalytics.SentimentConfidenceScores
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.sentiment = kwargs.get("sentiment", None)
        self.confidence_scores = kwargs.get("confidence_scores", None)

    @classmethod
    def _from_generated(cls, sentence):
        return cls(
            text=sentence.text,
            sentiment=sentence.sentiment,
            confidence_scores=SentimentConfidenceScores._from_generated(sentence.confidence_scores),  # pylint: disable=protected-access
        )

    def __repr__(self):
        return "SentenceSentiment(text={}, sentiment={}, confidence_scores={})".format(
            self.text,
            self.sentiment,
            repr(self.confidence_scores)
        )[:1024]


class SentimentConfidenceScores(DictMixin):
    """The confidence scores (Softmax scores) between 0 and 1.
    Higher values indicate higher confidence.

    :ivar positive: Positive score.
    :vartype positive: float
    :ivar neutral: Neutral score.
    :vartype neutral: float
    :ivar negative: Negative score.
    :vartype negative: float
    """

    def __init__(self, **kwargs):
        self.positive = kwargs.get('positive', None)
        self.neutral = kwargs.get('neutral', None)
        self.negative = kwargs.get('negative', None)

    @classmethod
    def _from_generated(cls, score):
        return cls(
            positive=score.positive,
            neutral=score.neutral,
            negative=score.negative
        )

    def __repr__(self):
        return "SentimentConfidenceScores(positive={}, neutral={}, negative={})" \
            .format(self.positive, self.neutral, self.negative)[:1024]

class HealthJobTaskResponse(DictMixin):
    """HealthJobTaskResponse.

    :param value: A wrapper class around a collection of results and errors.
    :type value: ~azure.ai.textanalytics.HealthcareBatchResult
    :param next_link:
    :type next_link: str
    :param expiration_time:
    :type expiration_time: str
    """

    def __init__(self, **kwargs):
        self.value = kwargs.get("value", None)
        self.next_link = kwargs.get("next_link", None)
        self.expiration_time = kwargs.get("expiration_time", None)

    @classmethod
    def _from_generated(cls, health_job_task_response):
        return cls(
            value=health_job_task_response.value,
            next_link=health_job_task_response.next_link,
            expiration_time=health_job_task_response.expiration_time
        )

class HealthcareBatchResult(DictMixin):
    """A wrapper class around a collection of results and errors.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar statistics: (Optional) if showStats=true was specified in the request this field will
     contain information about the request payload.
    :vartype statistics: ~azure.ai.textanalytics.TextDoccumentBatchStatistics
    :ivar documents: The set of successful results.
    :vartype documents:
     list[~azure.ai.textanalytics.HealthcareBatchResultItem]
    :ivar bool is_error: Boolean check for error item when iterating over list of
        results. Always False for an instance of a HealthcareBatchResult.
    :ivar model_version: The Model version.
    :vartype model_version: str
    """

    def __init__(
        self,
        **kwargs
    ):
        self.statistics = kwargs.get("statistics", None)
        self.documents = kwargs.get("documents", None)
        self.is_error = False
        self.model_version = kwargs.get("model_version", None)

    @classmethod
    def _from_generated(cls, healthcare_batch_result):
        return cls(
            statistics=TextDocumentBatchStatistics._from_generated(healthcare_batch_result.statistics),
            documents=HealthcareBatchResultItem._from_generated(healthcare_batch_result.documents),
            model_version=healthcare_batch_result.model_version
        )

class HealthcareBatchResultItem(DictMixin):
    """Contains all Health results for a given document.

    :param id: Unique, non-empty document identifier.
    :type id: str
    :param statistics: (Optional) if showStats=true was specified in the request this field will
     contain information about the document payload.
    :type statistics: ~azure.ai.textanalytics.TextDocumentStatistics
    :param entities: Gets or sets the list of recognized health entities in document.
    :type entities: list[~azure.ai.textanalytics.HealthcareEntity]
    :param relations:
    :type relations: list[~azure.ai.textanalytics.HealthcareRelation]
    """

    def __init__(
        self,
        **kwargs
    ):
        self.id = kwargs.get('id', None)
        self.statistics = kwargs.get('statistics', None)
        self.entities = kwargs.get('entities', None)
        self.relations = kwargs.get('relations', None)

    @classmethod
    def _from_generated(cls, healthcare_batch_result_item):
        return cls(
            id=healthcare_batch_result_item.id,
            statistics=TextDocumentStatistics._from_generated(healthcare_batch_result_item.statistics),
            entities=[
                HealthcareEntity._from_generated(entity) for entity in healthcare_batch_result_item.entities
            ],
            relations=[
                HealthcareRelation._from_generated(relation) for relation in healthcare_batch_result_item.relations
            ]
        )

class HealthcareEntity(DictMixin):
    """Contains information about an individual entity.

    :param id: Gets or sets the unique Id of the entity (used for matching betweent relation and
     entity results).
    :type id: str
    :param offset: Gets or sets the start index of the given entity in the document.
    :type offset: int
    :param length: Gets or sets the character length of the given entity in the document.
    :type length: int
    :param text: Gets or sets the text of the given entity.
    :type text: str
    :param category: Gets or sets the category of the given entity.
    :type category: str
    :param confidence_score: Gets or sets the confidence score of the given entity.
    :type confidence_score: float
    :param links: Entity links. For example UMLS ID's, ICD9/10 codes, etc.
    :type links: list[~azure.ai.textanalytics.HealthcareEntityLink]
    """

    def __init__(
        self,
        **kwargs
    ):
        self.id = kwargs.get('id', None)
        self.offset = kwargs.get('offset', None)
        self.length = kwargs.get('length', None)
        self.text = kwargs.get('text', None)
        self.category = kwargs.get('category', None)
        self.confidence_score = kwargs.get('confidence_score', None)
        self.links = kwargs.get('links', None)

    @classmethod
    def _from_generated(cls, healthcare_entity):
        return cls(
            id=healthcare_entity.id,
            offset=healthcare_entity.offset,
            length=healthcare_entity.length,
            text=healthcare_entity.text,
            category=healthcare_entity.category.
            confidence_score=healthcare_entity.confidence_score,
            links=[HealthcareEntityLink._from_generated(link) for link in healthcare_entity.links]
        )

class HealthcareRelation(DictMixin):
    """Contains entity pairs that are related Ex: Prescribed 100mg ibuprofen '100mg' is a dosage amount of 'ibuoprofen'.

    :param relation_type: Gets or sets type.
    :type relation_type: str
    :param bidirectional: Gets or sets the directionality flag for the relationship. If true the
     relation between the entities is bidirectional, otherwise directionality is source to target.
    :type bidirectional: bool
    :param source: Gets or sets the reference to the source entity.
    :type source: str
    :param target: Gets or sets reference to the target entity.
    :type target: str
    """

    def __init__(
        self,
        **kwargs
    ):
        self.relation_type = kwargs.get('relation_type', None)
        self.bidirectional = kwargs.get('bidirectional', None)
        self.source = kwargs.get('source', None)
        self.target = kwargs.get('target', None)

    @classmethod
    def _from_generated(cls, healthcare_relation):
        return cls(
            relation_type=healthcare_relation.relation_type,
            bidirectional=healthcare_relation.bidirectional,
            source=healthcare_relation.source,
            target=healthcare_relation.target
        )

class HealthcareEntityLink(DictMixin):
    """Entity Link in Healthcare Domain.

    :param data_source: Entity Link Data Source.This is the catalog/list the entity link ID belongs
     to.  Sources include: UMLS, CHV, MSH, etc.
    :type data_source: str
    :param id: Entity Link Concept Id. This is the specific id in the given source catalog.
     Example: blood pressure - source: umls, concept_id: C1272641.
    :type id: str
    """

    _attribute_map = {
        'data_source': {'key': 'dataSource', 'type': 'str'},
        'id': {'key': 'id', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(HealthcareEntityLink, self).__init__(**kwargs)
        self.data_source = kwargs.get('data_source', None)
        self.id = kwargs.get('id', None)

    @classmethod
    def _from_generated(cls, healthcare_entity_link):
        return cls(
            data_source=healthcare_entity_link.data_source,
            id=healthcare_entity_link.id
        )

class JobResponse(DictMixin):
    """JobResponse.

    All required parameters must be populated in order to send to Azure.

    :param job_id: Required.
    :type job_id: str
    :param last_updated_time: Required.
    :type last_updated_time: str
    :param created_datetime: Required.
    :type created_datetime: str
    :param status: Required.
    :type status: str
    :param results_location: Required.
    :type results_location: str
    """

    def __init__(
        self,
        **kwargs
    ):
        self.job_id = kwargs['job_id']
        self.last_updated_time = kwargs['last_updated_time']
        self.created_datetime = kwargs['created_datetime']
        self.status = kwargs['status']
        self.results_location = kwargs['results_location']

    @classmethod
    def _from_generated(cls, job_response):
        return cls(
            job_id=job_response.job_id,
            last_updated_time=job_response.last_updated_time,
            created_datetime=job_response.created_datetime,
            status=job_response.status,
            results_location=job_response.results_location
        )

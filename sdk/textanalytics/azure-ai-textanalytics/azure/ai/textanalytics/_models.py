# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._generated.models._models import LanguageInput
from ._generated.models._models import MultiLanguageInput


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

    :param name: Long name of a detected language (e.g. English,
        French).
    :type name: str
    :param iso6391_name: A two letter representation of the detected
        language according to the ISO 639-1 standard (e.g. en, fr).
    :type iso6391_name: str
    :param score: A confidence score between 0 and 1. Scores close
        to 1 indicate 100% certainty that the identified language is true.
    :type score: float
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.iso6391_name = kwargs.get("iso6391_name", None)
        self.score = kwargs.get("score", None)

    @classmethod
    def _from_generated(cls, language):
        return cls(
            name=language.name, iso6391_name=language.iso6391_name, score=language.score
        )

    def __repr__(self):
        return "DetectedLanguage(name={}, iso6391_name={}, score={})" \
            .format(self.name, self.iso6391_name, self.score)[:1024]


class RecognizeEntitiesResult(DictMixin):
    """RecognizeEntitiesResult is a result object which contains
    the recognized entities from a particular document.

    :param id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :type id: str
    :param entities: Recognized entities in the document.
    :type entities:
        list[~azure.ai.textanalytics.CategorizedEntity]
    :param statistics: If show_stats=true was specified in the request this
        field will contain information about the document payload.
    :type statistics:
        ~azure.ai.textanalytics.TextDocumentStatistics
    :param bool is_error: Boolean check for error item when iterating over list of
        results. Always False for an instance of a RecognizeEntitiesResult.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.entities = kwargs.get("entities", None)
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False

    def __repr__(self):
        return "RecognizeEntitiesResult(id={}, entities={}, statistics={}, is_error={})" \
            .format(self.id, repr(self.entities), repr(self.statistics), self.is_error)[:1024]


class RecognizePiiEntitiesResult(DictMixin):
    """RecognizePiiEntitiesResult is a result object which contains
    the recognized Personally Identifiable Information (PII) entities
    from a particular document.

    :param id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :type id: str
    :param entities: Recognized PII entities in the document.
    :type entities:
        list[~azure.ai.textanalytics.PiiEntity]
    :param statistics: If show_stats=true was specified in the request this
        field will contain information about the document payload.
    :type statistics:
        ~azure.ai.textanalytics.TextDocumentStatistics
    :param bool is_error: Boolean check for error item when iterating over list of
        results. Always False for an instance of a RecognizePiiEntitiesResult.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.entities = kwargs.get("entities", None)
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False

    def __repr__(self):
        return "RecognizePiiEntitiesResult(id={}, entities={}, statistics={}, is_error={})" \
            .format(self.id, repr(self.entities), repr(self.statistics), self.is_error)[:1024]


class DetectLanguageResult(DictMixin):
    """DetectLanguageResult is a result object which contains
    the detected language of a particular document.

    :param id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :type id: str
    :param primary_language: The primary language detected in the document.
    :type primary_language: ~azure.ai.textanalytics.DetectedLanguage
    :param statistics: If show_stats=true was specified in the request this
        field will contain information about the document payload.
    :type statistics:
        ~azure.ai.textanalytics.TextDocumentStatistics
    :param bool is_error: Boolean check for error item when iterating over list of
        results. Always False for an instance of a DetectLanguageResult.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.primary_language = kwargs.get("primary_language", None)
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False

    def __repr__(self):
        return "DetectLanguageResult(id={}, primary_language={}, statistics={}, is_error={})" \
            .format(self.id, repr(self.primary_language), repr(self.statistics), self.is_error)[:1024]


class CategorizedEntity(DictMixin):
    """CategorizedEntity contains information about a particular
    entity found in text.

    :param text: Entity text as appears in the request.
    :type text: str
    :param category: Entity category, such as Person/Location/Org/SSN etc
    :type category: str
    :param subcategory: Entity subcategory, such as Age/Year/TimeRange etc
    :type subcategory: str
    :param offset: Start position (in Unicode characters) for the
        entity text.
    :type offset: int
    :param length: Length (in Unicode characters) for the entity
        text.
    :type length: int
    :param score: Confidence score between 0 and 1 of the extracted
        entity.
    :type score: float
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get('text', None)
        self.category = kwargs.get('category', None)
        self.subcategory = kwargs.get('subcategory', None)
        self.offset = kwargs.get('offset', None)
        self.length = kwargs.get('length', None)
        self.score = kwargs.get('score', None)

    @classmethod
    def _from_generated(cls, entity):
        return cls(
            text=entity.text,
            category=entity.type,
            subcategory=entity.subtype,
            offset=entity.offset,
            length=entity.length,
            score=entity.score,
        )

    def __repr__(self):
        return "CategorizedEntity(text={}, category={}, subcategory={}, offset={}, length={}, score={})" \
            .format(self.text, self.category, self.subcategory, self.offset, self.length, self.score)[:1024]


class PiiEntity(DictMixin):
    """PiiEntity contains information about a Personally Identifiable
    Information (PII) entity found in text.

    :param text: Entity text as appears in the request.
    :type text: str
    :param category: Entity category, such as Financial Account
        Identification/Social Security Number/Phone Number, etc.
    :type category: str
    :param subcategory: Entity subcategory, such as Credit Card/EU
        Phone number/ABA Routing Numbers, etc.
    :type subcategory: str
    :param offset: Start position (in Unicode characters) for the
        entity text.
    :type offset: int
    :param length: Length (in Unicode characters) for the entity
        text.
    :type length: int
    :param score: Confidence score between 0 and 1 of the extracted
        entity.
    :type score: float
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get('text', None)
        self.category = kwargs.get('category', None)
        self.subcategory = kwargs.get('subcategory', None)
        self.offset = kwargs.get('offset', None)
        self.length = kwargs.get('length', None)
        self.score = kwargs.get('score', None)

    @classmethod
    def _from_generated(cls, entity):
        return cls(
            text=entity.text,
            category=entity.type,
            subcategory=entity.subtype,
            offset=entity.offset,
            length=entity.length,
            score=entity.score,
        )

    def __repr__(self):
        return "PiiEntity(text={}, category={}, subcategory={}, offset={}, length={}, score={})" \
            .format(self.text, self.category, self.subcategory, self.offset, self.length, self.score)[:1024]


class TextAnalyticsError(DictMixin):
    """TextAnalyticsError contains the error code, message, and
    other details that explain why the batch or individual document
    failed to be processed by the service.

    :param code: Error code. Possible values include:
     'invalidRequest', 'invalidArgument', 'internalServerError',
     'serviceUnavailable', 'invalidParameterValue', 'invalidRequestBodyFormat',
     'emptyRequest', 'missingInputRecords', 'invalidDocument', 'modelVersionIncorrect',
     'invalidDocumentBatch', 'unsupportedLanguageCode', 'invalidCountryHint'
    :type code: str
    :param message: Error message.
    :type message: str
    :param target: Error target.
    :type target: str
    """

    def __init__(self, **kwargs):
        self.code = kwargs.get('code', None)
        self.message = kwargs.get('message', None)
        self.target = kwargs.get('target', None)

    @classmethod
    def _from_generated(cls, err):
        if err.inner_error:
            return cls(
                code=err.inner_error.code.value,
                message=err.inner_error.message,
                target=err.inner_error.target
            )
        return cls(
            code=err.code.value,
            message=err.message,
            target=err.target
        )

    def __repr__(self):
        return "TextAnalyticsError(code={}, message={}, target={})" \
            .format(self.code, self.message, self.target)[:1024]


class ExtractKeyPhrasesResult(DictMixin):
    """ExtractKeyPhrasesResult is a result object which contains
    the key phrases found in a particular document.

    :param id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :type id: str
    :param key_phrases: A list of representative words or phrases.
        The number of key phrases returned is proportional to the number of words
        in the input document.
    :type key_phrases: list[str]
    :param statistics: If show_stats=true was specified in the request this
        field will contain information about the document payload.
    :type statistics:
        ~azure.ai.textanalytics.TextDocumentStatistics
    :param bool is_error: Boolean check for error item when iterating over list of
        results. Always False for an instance of a ExtractKeyPhrasesResult.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.key_phrases = kwargs.get("key_phrases", None)
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False

    def __repr__(self):
        return "ExtractKeyPhrasesResult(id={}, key_phrases={}, statistics={}, is_error={})" \
            .format(self.id, self.key_phrases, repr(self.statistics), self.is_error)[:1024]


class RecognizeLinkedEntitiesResult(DictMixin):
    """RecognizeLinkedEntitiesResult is a result object which contains
    links to a well-known knowledge base, like for example, Wikipedia or Bing.

    :param id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :type id: str
    :param entities: Recognized well-known entities in the document.
    :type entities:
        list[~azure.ai.textanalytics.LinkedEntity]
    :param statistics: If show_stats=true was specified in the request this
        field will contain information about the document payload.
    :type statistics:
        ~azure.ai.textanalytics.TextDocumentStatistics
    :param bool is_error: Boolean check for error item when iterating over list of
        results. Always False for an instance of a RecognizeLinkedEntitiesResult.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.entities = kwargs.get("entities", None)
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False

    def __repr__(self):
        return "RecognizeLinkedEntitiesResult(id={}, entities={}, statistics={}, is_error={})" \
            .format(self.id, repr(self.entities), repr(self.statistics), self.is_error)[:1024]


class AnalyzeSentimentResult(DictMixin):
    """AnalyzeSentimentResult is a result object which contains
    the overall predicted sentiment and confidence scores for your document
    and a per-sentence sentiment prediction with scores.

    :param id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :type id: str
    :param sentiment: Predicted sentiment for document (Negative,
        Neutral, Positive, or Mixed). Possible values include: 'positive',
        'neutral', 'negative', 'mixed'
    :type sentiment: str
    :param statistics: If show_stats=true was specified in the request this
        field will contain information about the document payload.
    :type statistics:
        ~azure.ai.textanalytics.TextDocumentStatistics
    :param sentiment_scores: Document level sentiment confidence
        scores between 0 and 1 for each sentiment class.
    :type sentiment_scores:
        ~azure.ai.textanalytics.SentimentScorePerLabel
    :param sentences: Sentence level sentiment analysis.
    :type sentences:
        list[~azure.ai.textanalytics.SentenceSentiment]
    :param bool is_error: Boolean check for error item when iterating over list of
        results. Always False for an instance of a AnalyzeSentimentResult.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.sentiment = kwargs.get("sentiment", None)
        self.statistics = kwargs.get("statistics", None)
        self.sentiment_scores = kwargs.get("sentiment_scores", None)
        self.sentences = kwargs.get("sentences", None)
        self.is_error = False

    def __repr__(self):
        return "AnalyzeSentimentResult(id={}, sentiment={}, statistics={}, sentiment_scores={}, sentences={}, " \
               "is_error={})".format(self.id, self.sentiment, repr(self.statistics), repr(self.sentiment_scores),
                                     repr(self.sentences), self.is_error)[:1024]


class TextDocumentStatistics(DictMixin):
    """TextDocumentStatistics contains information about
    the document payload.

    :param character_count: Number of text elements recognized in
        the document.
    :type character_count: int
    :param transaction_count: Number of transactions for the
        document.
    :type transaction_count: int
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

    :param id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :type id: str
    :param error: The document error.
    :type error: ~azure.ai.textanalytics.TextAnalyticsError
    :param bool is_error: Boolean check for error item when iterating over list of
        results. Always True for an instance of a DocumentError.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.error = kwargs.get("error", None)
        self.is_error = True

    def __getattr__(self, attr):
        result_set = set()
        result_set.update(
            RecognizeEntitiesResult().keys() + RecognizePiiEntitiesResult().keys()
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

    :param id: Required. Unique, non-empty document identifier.
    :type id: str
    :param text: Required. The input text to process.
    :type text: str
    :param country_hint: A country hint to help better detect
     the language of the text. Accepts two letter country codes
     specified by ISO 3166-1 alpha-2. Defaults to "US". Pass
     in the empty string "" to not use a country_hint.
    :type country_hint: str
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

    :param name: Entity Linking formal name.
    :type name: str
    :param matches: List of instances this entity appears in the text.
    :type matches:
        list[~azure.ai.textanalytics.LinkedEntityMatch]
    :param language: Language used in the data source.
    :type language: str
    :param id: Unique identifier of the recognized entity from the data
        source.
    :type id: str
    :param url: URL to the entity's page from the data source.
    :type url: str
    :param data_source: Data source used to extract entity linking,
        such as Wiki/Bing etc.
    :type data_source: str
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.matches = kwargs.get("matches", None)
        self.language = kwargs.get("language", None)
        self.id = kwargs.get("id", None)
        self.url = kwargs.get("url", None)
        self.data_source = kwargs.get("data_source", None)

    @classmethod
    def _from_generated(cls, entity):
        return cls(
            name=entity.name,
            matches=[LinkedEntityMatch._from_generated(e) for e in entity.matches],  # pylint: disable=protected-access
            language=entity.language,
            id=entity.id,
            url=entity.url,
            data_source=entity.data_source,
        )

    def __repr__(self):
        return "LinkedEntity(name={}, matches={}, language={}, id={}, url={}, " \
               "data_source={})".format(self.name, repr(self.matches), self.language, self.id, self.url,
                                        self.data_source)[:1024]


class LinkedEntityMatch(DictMixin):
    """A match for the linked entity found in text. Provides
    the confidence score of the prediction and where the entity
    was found in the text.

    :param score: If a well-known item is recognized, a
        decimal number denoting the confidence level between 0 and 1 will be
        returned.
    :type score: float
    :param text: Entity text as appears in the request.
    :type text: str
    :param offset: Start position (in Unicode characters) for the
        entity match text.
    :type offset: int
    :param length: Length (in Unicode characters) for the entity
        match text.
    :type length: int
    """

    def __init__(self, **kwargs):
        self.score = kwargs.get("score", None)
        self.text = kwargs.get("text", None)
        self.offset = kwargs.get("offset", None)
        self.length = kwargs.get("length", None)

    @classmethod
    def _from_generated(cls, match):
        return cls(
            score=match.score, text=match.text, offset=match.offset, length=match.length
        )

    def __repr__(self):
        return "LinkedEntityMatch(score={}, text={}, offset={}, length={})" \
            .format(self.score, self.text, self.offset, self.length)[:1024]


class TextDocumentInput(MultiLanguageInput):
    """The input document to be analyzed by the service.

    :param id: Required. A unique, non-empty document identifier.
    :type id: str
    :param text: Required. The input text to process.
    :type text: str
    :param language: This is the 2 letter ISO 639-1 representation
     of a language. For example, use "en" for English; "es" for Spanish etc. If
     not set, uses "en" for English as default.
    :type language: str
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

    :param document_count: Number of documents submitted in the request.
    :type document_count: int
    :param valid_document_count: Number of valid documents. This
        excludes empty, over-size limit or non-supported languages documents.
    :type valid_document_count: int
    :param erroneous_document_count: Number of invalid documents.
        This includes empty, over-size limit or non-supported languages documents.
    :type erroneous_document_count: int
    :param transaction_count: Number of transactions for the request.
    :type transaction_count: long
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

    :param sentiment: The predicted Sentiment for the sentence.
        Possible values include: 'positive', 'neutral', 'negative'
    :type sentiment: str
    :param sentiment_scores: The sentiment confidence score between 0
        and 1 for the sentence for all labels.
    :type sentiment_scores:
        ~azure.ai.textanalytics.SentimentScorePerLabel
    :param offset: The sentence offset from the start of the
        document.
    :type offset: int
    :param length: The length of the sentence by Unicode standard.
    :type length: int
    :param warnings: The warnings generated for the sentence.
    :type warnings: list[str]
    """

    def __init__(self, **kwargs):
        self.sentiment = kwargs.get("sentiment", None)
        self.sentiment_scores = kwargs.get("sentiment_scores", None)
        self.offset = kwargs.get("offset", None)
        self.length = kwargs.get("length", None)
        self.warnings = kwargs.get("warnings", None)

    @classmethod
    def _from_generated(cls, sentence):
        return cls(
            sentiment=sentence.sentiment.value,
            sentiment_scores=SentimentScorePerLabel._from_generated(sentence.sentence_scores),  # pylint: disable=protected-access
            offset=sentence.offset,
            length=sentence.length,
            warnings=sentence.warnings,
        )

    def __repr__(self):
        return "SentenceSentiment(sentiment={}, sentiment_scores={}, offset={}, length={}, warnings={})" \
            .format(self.sentiment, repr(self.sentiment_scores), self.offset, self.length, self.warnings)[:1024]


class SentimentScorePerLabel(DictMixin):
    """Represents the confidence scores between 0 and 1 across all sentiment
    labels: positive, neutral, negative.

    :param positive: Positive score.
    :type positive: float
    :param neutral: Neutral score.
    :type neutral: float
    :param negative: Negative score.
    :type negative: float
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
        return "SentimentScorePerLabel(positive={}, neutral={}, negative={})" \
            .format(self.positive, self.neutral, self.negative)[:1024]

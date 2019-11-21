# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._generated.models._models import LanguageInput as GeneratedLanguageInput
from ._generated.models._models import MultiLanguageInput as GeneratedMultiLanguageInput


class DetectedLanguage(object):
    """DetectedLanguage.

    All required parameters must be populated in order to send to Azure.

    :param name: Required. Long name of a detected language (e.g. English,
     French).
    :type name: str
    :param iso6391_name: Required. A two letter representation of the detected
     language according to the ISO 639-1 standard (e.g. en, fr).
    :type iso6391_name: str
    :param score: Required. A confidence score between 0 and 1. Scores close
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


class DocumentEntities(object):
    """DocumentEntities.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. Unique, non-empty document identifier.
    :type id: str
    :param entities: Required. Recognized entities in the document.
    :type entities:
     list[~azure.cognitiveservices.language.textanalytics.models.Entity]
    :param statistics: if showStats=true was specified in the request this
     field will contain information about the document payload.
    :type statistics:
     ~azure.cognitiveservices.language.textanalytics.models.DocumentStatistics
    :param bool is_error: Boolean check for error item when iterating over list of
     results. Always False for an instance of a DocumentEntities.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.entities = kwargs.get("entities", None)
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False


class DocumentLanguage(object):
    """DocumentLanguage.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. Unique, non-empty document identifier.
    :type id: str
    :param detected_language: Required. The extracted language.
    :type detected_language:
     ~azure.cognitiveservices.language.textanalytics.models.DetectedLanguage
    :param statistics: if showStats=true was specified in the request this
     field will contain information about the document payload.
    :type statistics:
     ~azure.cognitiveservices.language.textanalytics.models.DocumentStatistics
    :param bool is_error: Boolean check for error item when iterating over list of
     results. Always False for an instance of a DocumentLanguage.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.detected_language = kwargs.get("detected_language", None)
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False


class Entity(object):
    """Entity.

    All required parameters must be populated in order to send to Azure.

    :param text: Required. Entity text as appears in the request.
    :type text: str
    :param type: Required. Entity type, such as Person/Location/Org/SSN etc
    :type type: str
    :param subtype: Entity sub type, such as Age/Year/TimeRange etc
    :type subtype: str
    :param offset: Required. Start position (in Unicode characters) for the
     entity text.
    :type offset: int
    :param length: Required. Length (in Unicode characters) for the entity
     text.
    :type length: int
    :param score: Required. Confidence score between 0 and 1 of the extracted
     entity.
    :type score: float
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get('text', None)
        self.type = kwargs.get('type', None)
        self.subtype = kwargs.get('subtype', None)
        self.offset = kwargs.get('offset', None)
        self.length = kwargs.get('length', None)
        self.score = kwargs.get('score', None)

    @classmethod
    def _from_generated(cls, entity):
        return cls(
            text=entity.text,
            type=entity.type,
            subtype=entity.subtype,
            offset=entity.offset,
            length=entity.length,
            score=entity.score,
        )


class Error(object):
    """Error.

    All required parameters must be populated in order to send to Azure.

    :param code: Required. Error code. Possible values include:
     'invalidRequest', 'invalidArgument', 'internalServerError',
     'serviceUnavailable'
    :type code: str or
     ~azure.cognitiveservices.language.textanalytics.models.enum
    :param message: Required. Error message.
    :type message: str
    :param target: Error target.
    :type target: str
    :param innererror: Inner error contains more specific information.
    :type innererror:
     ~azure.cognitiveservices.language.textanalytics.models.InnerError
    :param details: Details about specific errors that led to this reported
     error.
    :type details:
     list[~azure.cognitiveservices.language.textanalytics.models.Error]
    :param is_error: Boolean check for error item when iterating over list of
     results. Always True for an instance of a Error.
    """

    def __init__(self, **kwargs):
        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)
        self.target = kwargs.get("target", None)
        self.innererror = kwargs.get("innererror", None)
        self.details = kwargs.get("details", None)
        self.is_error = True


class InnerError(object):
    """InnerError.

    All required parameters must be populated in order to send to Azure.

    :param code: Required. Error code. Possible values include:
     'invalidParameterValue', 'invalidRequestBodyFormat', 'emptyRequest',
     'missingInputRecords', 'invalidDocument', 'modelVersionIncorrect',
     'invalidDocumentBatch', 'unsupportedLanguageCode', 'invalidCountryHint'
    :type code: str or
     ~azure.cognitiveservices.language.textanalytics.models.enum
    :param message: Required. Error message.
    :type message: str
    :param target: Error target.
    :type target: str
    :param innererror: Inner error contains more specific information.
    :type innererror:
     ~azure.cognitiveservices.language.textanalytics.models.InnerError
    """

    def __init__(self, **kwargs):
        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)
        self.target = kwargs.get("target", None)
        self.innererror = kwargs.get("innererror", None)


class DocumentKeyPhrases(object):
    """DocumentKeyPhrases.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. Unique, non-empty document identifier.
    :type id: str
    :param key_phrases: Required. A list of representative words or phrases.
     The number of key phrases returned is proportional to the number of words
     in the input document.
    :type key_phrases: list[str]
    :param statistics: if showStats=true was specified in the request this
     field will contain information about the document payload.
    :type statistics:
     ~azure.cognitiveservices.language.textanalytics.models.DocumentStatistics
    :param bool is_error: Boolean check for error item when iterating over list of
     results. Always False for an instance of a DocumentKeyPhrases.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.key_phrases = kwargs.get("key_phrases", None)
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False


class DocumentLinkedEntities(object):
    """DocumentLinkedEntities.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. Unique, non-empty document identifier.
    :type id: str
    :param entities: Required. Recognized well-known entities in the document.
    :type entities:
     list[~azure.cognitiveservices.language.textanalytics.models.LinkedEntity]
    :param statistics: if showStats=true was specified in the request this
     field will contain information about the document payload.
    :type statistics:
     ~azure.cognitiveservices.language.textanalytics.models.DocumentStatistics
    :param bool is_error: Boolean check for error item when iterating over list of
     results. Always False for an instance of a DocumentLinkedEntities.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.entities = kwargs.get("entities", None)
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False


class DocumentSentiment(object):
    """DocumentSentiment.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. Unique, non-empty document identifier.
    :type id: str
    :param sentiment: Required. Predicted sentiment for document (Negative,
     Neutral, Positive, or Mixed). Possible values include: 'positive',
     'neutral', 'negative', 'mixed'
    :type sentiment: str or
     ~azure.cognitiveservices.language.textanalytics.models.enum
    :param statistics: The document statistics.
    :type statistics:
     ~azure.cognitiveservices.language.textanalytics.models.DocumentStatistics
    :param document_scores: Required. Document level sentiment confidence
     scores between 0 and 1 for each sentiment class.
    :type document_scores: object
    :param sentences: Required. Sentence level sentiment analysis.
    :type sentences:
     list[~azure.cognitiveservices.language.textanalytics.models.SentenceSentiment]
    :param bool is_error: Boolean check for error item when iterating over list of
     results. Always False for an instance of a DocumentSentiment.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.sentiment = kwargs.get("sentiment", None)
        self.statistics = kwargs.get("statistics", None)
        self.document_scores = kwargs.get("document_scores", None)
        self.sentences = kwargs.get("sentences", None)
        self.is_error = False


class DocumentStatistics(object):
    """if showStats=true was specified in the request this field will contain
    information about the document payload.

    All required parameters must be populated in order to send to Azure.

    :param characters_count: Required. Number of text elements recognized in
     the document.
    :type characters_count: int
    :param transactions_count: Required. Number of transactions for the
     document.
    :type transactions_count: int
    """

    def __init__(self, **kwargs):
        self.characters_count = kwargs.get("characters_count", None)
        self.transactions_count = kwargs.get("transactions_count", None)

    @classmethod
    def _from_generated(cls, stats):
        if stats is None:
            return None
        return cls(
            characters_count=stats.characters_count,
            transactions_count=stats.transactions_count,
        )


class DocumentError(object):
    """DocumentError.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. Document Id.
    :type id: str
    :param error: Required. Document Error.
    :type error: object
    :param bool is_error: Boolean check for error item when iterating over list of
     results. Always True for an instance of a DocumentError.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.error = kwargs.get("error", None)
        self.is_error = True


class LanguageInput(GeneratedLanguageInput):
    """LanguageInput.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. Unique, non-empty document identifier.
    :type id: str
    :param text: Required.
    :type text: str
    :param country_hint:
    :type country_hint: str
    """

    def __init__(self, **kwargs):
        super(LanguageInput, self).__init__(**kwargs)
        self.id = kwargs.get("id", None)
        self.text = kwargs.get("text", None)
        self.country_hint = kwargs.get("country_hint", None)


class LinkedEntity(object):
    """LinkedEntity.

    All required parameters must be populated in order to send to Azure.

    :param name: Required. Entity Linking formal name.
    :type name: str
    :param matches: Required. List of instances this entity appears in the
     text.
    :type matches:
     list[~azure.cognitiveservices.language.textanalytics.models.Match]
    :param language: Required. Language used in the data source.
    :type language: str
    :param id: Unique identifier of the recognized entity from the data
     source.
    :type id: str
    :param url: Required. URL for the entity's page from the data source.
    :type url: str
    :param data_source: Required. Data source used to extract entity linking,
     such as Wiki/Bing etc.
    :type data_source: str
    :param bool is_error: Boolean check for error item when iterating over list of
     results. Always False for an instance of a LinkedEntity.
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.matches = kwargs.get("matches", None)
        self.language = kwargs.get("language", None)
        self.id = kwargs.get("id", None)
        self.url = kwargs.get("url", None)
        self.data_source = kwargs.get("data_source", None)
        self.is_error = False

    @classmethod
    def _from_generated(cls, entity):
        return cls(
            name=entity.name,
            matches=[Match._from_generated(e) for e in entity.matches],  # pylint: disable=protected-access
            language=entity.language,
            id=entity.id,
            url=entity.url,
            data_source=entity.data_source,
        )


class Match(object):
    """Match.

    All required parameters must be populated in order to send to Azure.

    :param score: Required. (Optional) If a well-known item is recognized, a
     decimal number denoting the confidence level between 0 and 1 will be
     returned.
    :type score: float
    :param text: Required. Entity text as appears in the request.
    :type text: str
    :param offset: Required. Start position (in Unicode characters) for the
     entity match text.
    :type offset: int
    :param length: Required. Length (in Unicode characters) for the entity
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


class MultiLanguageInput(GeneratedMultiLanguageInput):
    """Contains an input document to be analyzed by the service.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. A unique, non-empty document identifier.
    :type id: str
    :param text: Required. The input text to process.
    :type text: str
    :param language: (Optional) This is the 2 letter ISO 639-1 representation
     of a language. For example, use "en" for English; "es" for Spanish etc. If
     not set, use "en" for English as default.
    :type language: str
    """

    def __init__(self, **kwargs):
        super(MultiLanguageInput, self).__init__(**kwargs)
        self.id = kwargs.get("id", None)
        self.text = kwargs.get("text", None)
        self.language = kwargs.get("language", None)


class RequestStatistics(object):
    """if showStats=true was specified in the request this field will contain
    information about the request payload.

    All required parameters must be populated in order to send to Azure.

    :param documents_count: Required. Number of documents submitted in the
     request.
    :type documents_count: int
    :param valid_documents_count: Required. Number of valid documents. This
     excludes empty, over-size limit or non-supported languages documents.
    :type valid_documents_count: int
    :param erroneous_documents_count: Required. Number of invalid documents.
     This includes empty, over-size limit or non-supported languages documents.
    :type erroneous_documents_count: int
    :param transactions_count: Required. Number of transactions for the
     request.
    :type transactions_count: long
    """

    def __init__(self, **kwargs):
        self.documents_count = kwargs.get("documents_count", None)
        self.valid_documents_count = kwargs.get("valid_documents_count", None)
        self.erroneous_documents_count = kwargs.get("erroneous_documents_count", None)
        self.transactions_count = kwargs.get("transactions_count", None)

    @classmethod
    def _from_generated(cls, statistics):
        if statistics is None:
            return None
        return cls(
            documents_count=statistics["documentsCount"],
            valid_documents_count=statistics["validDocumentsCount"],
            erroneous_documents_count=statistics["erroneousDocumentsCount"],
            transactions_count=statistics["transactionsCount"],
        )


class SentenceSentiment(object):
    """SentenceSentiment.

    All required parameters must be populated in order to send to Azure.

    :param sentiment: Required. The predicted Sentiment for the sentence.
     Possible values include: 'positive', 'neutral', 'negative'
    :type sentiment: str or
     ~azure.cognitiveservices.language.textanalytics.models.enum
    :param sentence_scores: Required. The sentiment confidence score between 0
     and 1 for the sentence for all classes.
    :type sentence_scores: object
    :param offset: Required. The sentence offset from the start of the
     document.
    :type offset: int
    :param length: Required. The length of the sentence by Unicode standard.
    :type length: int
    :param warnings: The warnings generated for the sentence.
    :type warnings: list[str]
    """

    def __init__(self, **kwargs):
        self.sentiment = kwargs.get("sentiment", None)
        self.sentence_scores = kwargs.get("sentence_scores", None)
        self.offset = kwargs.get("offset", None)
        self.length = kwargs.get("length", None)
        self.warnings = kwargs.get("warnings", None)

    @classmethod
    def _from_generated(cls, sentence):
        return cls(
            sentiment=sentence.sentiment,
            sentence_scores=sentence.sentence_scores,
            offset=sentence.offset,
            length=sentence.length,
            warnings=sentence.warnings,
        )

# coding=utf-8  pylint: disable=too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import re
from enum import Enum
from ._generated.models import (
    LanguageInput,
    MultiLanguageInput,
)

from ._generated.v3_0 import models as _v3_0_models
from ._generated.v3_1_preview_3 import models as _v3_1_preview_3_models

def _get_indices(relation):
    return [int(s) for s in re.findall(r"\d+", relation)]

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

class PiiEntityDomainType(str, Enum):
    """The different domains of PII entities that users can filter by"""
    PROTECTED_HEALTH_INFORMATION = "PHI"  # See https://aka.ms/tanerpii for more information.


class DetectedLanguage(DictMixin):
    """DetectedLanguage contains the predicted language found in text,
    its confidence score, and its ISO 639-1 representation.

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
    :ivar statistics: If `show_stats=True` was specified in the request this
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


class RecognizePiiEntitiesResult(DictMixin):
    """RecognizePiiEntitiesResult is a result object which contains
    the recognized Personally Identifiable Information (PII) entities
    from a particular document.

    :ivar str id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :ivar entities: Recognized PII entities in the document.
    :vartype entities:
        list[~azure.ai.textanalytics.PiiEntity]
    :ivar str redacted_text: Returns the text of the input document with all of the PII information
        redacted out. Only returned for API versions v3.1-preview and up.
    :ivar warnings: Warnings encountered while processing document. Results will still be returned
        if there are warnings, but they may not be fully accurate.
    :vartype warnings: list[~azure.ai.textanalytics.TextAnalyticsWarning]
    :ivar statistics: If `show_stats=True` was specified in the request this
        field will contain information about the document payload.
    :vartype statistics:
        ~azure.ai.textanalytics.TextDocumentStatistics
    :ivar bool is_error: Boolean check for error item when iterating over list of
        results. Always False for an instance of a RecognizePiiEntitiesResult.
    .. versionadded:: v3.1-preview
        The *redacted_text* parameter.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.entities = kwargs.get("entities", None)
        self.redacted_text = kwargs.get("redacted_text", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False

    def __repr__(self):
        return "RecognizePiiEntitiesResult(id={}, entities={}, redacted_text={}, warnings={}, " \
            "statistics={}, is_error={})" .format(
                self.id,
                repr(self.entities),
                self.redacted_text,
                repr(self.warnings),
                repr(self.statistics),
                self.is_error
            )[:1024]


class AnalyzeHealthcareResultItem(DictMixin):
    """
    AnalyzeHealthcareResultItem contains the Healthcare entities and relations from a
    particular document.

    :ivar str id: Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document.
    :ivar entities: Identified Healthcare entities in the document.
    :vartype entities:
        list[~azure.ai.textanalytics.HealthcareEntity]
    :ivar relations: A list of detected relations between recognized entities.
    :vartype relations:
        list[~azure.ai.textanalytics.HealthcareRelation]
    :ivar warnings: Warnings encountered while processing document. Results will still be returned
        if there are warnings, but they may not be fully accurate.
    :vartype warnings: list[~azure.ai.textanalytics.TextAnalyticsWarning]
    :ivar statistics: If show_stats=true was specified in the request this
        field will contain information about the document payload.
    :vartype statistics:
        ~azure.ai.textanalytics.TextDocumentStatistics
    :ivar bool is_error: Boolean check for error item when iterating over list of
        results. Always False for an instance of a AnalyzeHealthcareResult.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.entities = kwargs.get("entities", None)
        self.relations = kwargs.get("relations", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.is_error = False

    @classmethod
    def _from_generated(cls, healthcare_result):
        entities = [HealthcareEntity._from_generated(e) for e in healthcare_result.entities] # pylint: disable=protected-access
        relations = []
        if healthcare_result.relations:
            for r in healthcare_result.relations:
                _, source_idx = _get_indices(r.source)
                _, target_idx = _get_indices(r.target)
                relations.append(HealthcareRelation._from_generated(r, entities[source_idx], entities[target_idx])) # pylint: disable=protected-access

        return cls(
            id=healthcare_result.id,
            entities=entities,
            relations=relations,
            warnings=healthcare_result.warnings,
            statistics=healthcare_result.statistics
        )

    def __repr__(self):
        return "AnalyzeHealthcareResultItem(id={}, entities={}, relations={}, warnings={}, statistics={}, \
        is_error={})".format(
            self.id,
            self.entities,
            self.relations,
            self.warnings,
            self.statistics,
            self.is_error
        )[:1024]


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
    :ivar statistics: If `show_stats=True` was specified in the request this
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
    :ivar int offset: The entity text offset from the start of the document.
        Returned in unicode code points. Only returned for API versions v3.1-preview and up.
    :ivar confidence_score: Confidence score between 0 and 1 of the extracted
        entity.
    :vartype confidence_score: float
    .. versionadded:: v3.1-preview
        The *offset* property.
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get('text', None)
        self.category = kwargs.get('category', None)
        self.subcategory = kwargs.get('subcategory', None)
        self.offset = kwargs.get('offset', None)
        self.confidence_score = kwargs.get('confidence_score', None)

    @classmethod
    def _from_generated(cls, entity):
        offset = entity.offset
        if isinstance(entity, _v3_0_models.Entity):
            # we do not return offset for v3.0 since
            # the correct encoding was not introduced for v3.0
            offset = None
        return cls(
            text=entity.text,
            category=entity.category,
            subcategory=entity.subcategory,
            offset=offset,
            confidence_score=entity.confidence_score,
        )

    def __repr__(self):
        return "CategorizedEntity(text={}, category={}, subcategory={}, "\
            "offset={}, confidence_score={})".format(
            self.text,
            self.category,
            self.subcategory,
            self.offset,
            self.confidence_score
        )[:1024]


class PiiEntity(DictMixin):
    """PiiEntity contains information about a Personally Identifiable
    Information (PII) entity found in text.

    :ivar str text: Entity text as appears in the request.
    :ivar str category: Entity category, such as Financial Account
        Identification/Social Security Number/Phone Number, etc.
    :ivar str subcategory: Entity subcategory, such as Credit Card/EU
        Phone number/ABA Routing Numbers, etc.
    :ivar int offset: The PII entity text offset from the start of the document.
        Returned in unicode code points.
    :ivar float confidence_score: Confidence score between 0 and 1 of the extracted
        entity.
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get('text', None)
        self.category = kwargs.get('category', None)
        self.subcategory = kwargs.get('subcategory', None)
        self.offset = kwargs.get('offset', None)
        self.confidence_score = kwargs.get('confidence_score', None)

    @classmethod
    def _from_generated(cls, entity):
        return cls(
            text=entity.text,
            category=entity.category,
            subcategory=entity.subcategory,
            offset=entity.offset,
            confidence_score=entity.confidence_score,
        )

    def __repr__(self):
        return (
            "PiiEntity(text={}, category={}, subcategory={}, offset={}, "\
            "confidence_score={})".format(
                self.text,
                self.category,
                self.subcategory,
                self.offset,
                self.confidence_score
            )[:1024]
        )


class HealthcareEntity(DictMixin):
    """HealthcareEntity contains information about a Healthcare entity found in text.

        :ivar str text: Entity text as appears in the request.
        :ivar str category: Entity category, such as Dosage or MedicationName, etc.
        :ivar str subcategory: Entity subcategory.  # TODO: add subcategory examples
        :ivar int offset: The Healthcare entity text offset from the start of the document.
        :ivar float confidence_score: Confidence score between 0 and 1 of the extracted
            entity.
        :ivar links: A collection of entity references in known data sources.
        :vartype links: list[~azure.ai.textanalytics.HealthcareEntityLink]
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.category = kwargs.get("category", None)
        self.subcategory = kwargs.get("subcategory", None)
        self.offset = kwargs.get("offset", None)
        self.confidence_score = kwargs.get("confidence_score", None)
        self.links = kwargs.get("links", [])

    @classmethod
    def _from_generated(cls, healthcare_entity):
        return cls(
            text=healthcare_entity.text,
            category=healthcare_entity.category,
            subcategory=healthcare_entity.subcategory,
            offset=healthcare_entity.offset,
            confidence_score=healthcare_entity.confidence_score,
            links=[
                HealthcareEntityLink(id=l.id, data_source=l.data_source) for l in healthcare_entity.links
            ] if healthcare_entity.links else None
        )

    def __repr__(self):
        return "HealthcareEntity(text={}, category={}, subcategory={}, offset={}, confidence_score={},\
        links={})".format(
            self.text,
            self.category,
            self.subcategory,
            self.offset,
            self.confidence_score,
            repr(self.links)
        )[:1024]


class HealthcareRelation(DictMixin):
    """
    HealthcareRelation contains information describing a relationship between two entities found in text.

    :ivar str type: The type of relation, such as DosageOfMedication or FrequencyOfMedication, etc.
    :ivar bool is_bidirectional: Boolean value indicating that the relationship between the two entities is
        bidirectional.  If true the relation between the entities is bidirectional, otherwise directionality
        is source to target.
    :ivar source: A reference to an extracted Healthcare entity representing the source of the relation.
    :vartype source: ~azure.ai.textanalytics.HealthcareEntity
    :ivar target: A reference to an extracted Healthcare entity representing the target of the relation.
    :vartype target: ~azure.ai.textanalytics.HealthcareEntity
    """

    def __init__(self, **kwargs):
        self.relation_type = kwargs.get("relation_type", None)
        self.is_bidirectional = kwargs.get("is_bidirectional", None)
        self.source = kwargs.get("source", None)
        self.target = kwargs.get("target", None)

    @classmethod
    def _from_generated(cls, healthcare_relation, source_entity, target_entity):
        return cls(
            relation_type=healthcare_relation.relation_type,
            is_bidirectional=healthcare_relation.bidirectional,
            source=source_entity,
            target=target_entity
        )

    def __repr__(self):
        return "HealthcareRelation(relation_type={}, is_bidirectional={}, source={}, target={})".format(
            self.relation_type,
            self.is_bidirectional,
            repr(self.source),
            repr(self.target)
        )[:1024]


class HealthcareEntityLink(DictMixin):
    """
    HealthcareEntityLink contains information representing an entity reference in a known data source.

    :ivar str id: ID of the entity in the given source catalog.
    :ivar str data_source: The entity catalog from where the entity was identified, such as UMLS, CHV, MSH, etc.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.data_source = kwargs.get("data_source", None)

    def __repr__(self):
        return "HealthcareEntityLink(id={}, data_source={})".format(self.id, self.data_source)[:1024]


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
    :ivar statistics: If `show_stats=True` was specified in the request this
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
    :ivar statistics: If `show_stats=True` was specified in the request this
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
    :ivar statistics: If `show_stats=True` was specified in the request this
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
    :ivar str bing_entity_search_api_id: Bing Entity Search unique identifier of the recognized entity.
        Use in conjunction with the Bing Entity Search SDK to fetch additional relevant information.
        Only available for API version v3.1-preview and up.
    .. versionadded:: v3.1-preview
        The *bing_entity_search_api_id* property.
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.matches = kwargs.get("matches", None)
        self.language = kwargs.get("language", None)
        self.data_source_entity_id = kwargs.get("data_source_entity_id", None)
        self.url = kwargs.get("url", None)
        self.data_source = kwargs.get("data_source", None)
        self.bing_entity_search_api_id = kwargs.get("bing_entity_search_api_id", None)

    @classmethod
    def _from_generated(cls, entity):
        bing_entity_search_api_id = entity.bing_id if hasattr(entity, "bing_id") else None
        return cls(
            name=entity.name,
            matches=[LinkedEntityMatch._from_generated(e) for e in entity.matches],  # pylint: disable=protected-access
            language=entity.language,
            data_source_entity_id=entity.id,
            url=entity.url,
            data_source=entity.data_source,
            bing_entity_search_api_id=bing_entity_search_api_id,
        )

    def __repr__(self):
        return "LinkedEntity(name={}, matches={}, language={}, data_source_entity_id={}, url={}, " \
            "data_source={}, bing_entity_search_api_id={})".format(
                self.name,
                repr(self.matches),
                self.language,
                self.data_source_entity_id,
                self.url,
                self.data_source,
                self.bing_entity_search_api_id,
        )[:1024]


class LinkedEntityMatch(DictMixin):
    """A match for the linked entity found in text. Provides
    the confidence score of the prediction and where the entity
    was found in the text.

    :ivar confidence_score: If a well-known item is recognized, a
        decimal number denoting the confidence level between 0 and 1 will be
        returned.
    :vartype confidence_score: float
    :ivar text: Entity text as appears in the request.
    :ivar int offset: The linked entity match text offset from the start of the document.
        Returned in unicode code points. Only returned for API versions v3.1-preview and up.
    :vartype text: str
    .. versionadded:: v3.1-preview
        The *offset* property.
    """

    def __init__(self, **kwargs):
        self.confidence_score = kwargs.get("confidence_score", None)
        self.text = kwargs.get("text", None)
        self.offset = kwargs.get("offset", None)

    @classmethod
    def _from_generated(cls, match):
        offset = match.offset
        if isinstance(match, _v3_0_models.Match):
            # we do not return offset for v3.0 since
            # the correct encoding was not introduced for v3.0
            offset = None
        return cls(
            confidence_score=match.confidence_score,
            text=match.text,
            offset=offset,
        )

    def __repr__(self):
        return "LinkedEntityMatch(confidence_score={}, text={}, offset={})".format(
            self.confidence_score, self.text, self.offset
        )[:1024]


class TextDocumentInput(DictMixin, MultiLanguageInput):
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
    :ivar int offset: The sentence offset from the start of the document. Returned
        in unicode code points. Only returned for API versions v3.1-preview and up.
    :ivar mined_opinions: The list of opinions mined from this sentence.
        For example in the sentence "The food is good, but the service is bad", we would
        mine the two opinions "food is good" and "service is bad". Only returned
        if `show_opinion_mining` is set to True in the call to `analyze_sentiment` and
        api version is v3.1-preview and up.
    :vartype mined_opinions:
        list[~azure.ai.textanalytics.MinedOpinion]
    .. versionadded:: v3.1-preview
        The *offset* and *mined_opinions* properties.
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.sentiment = kwargs.get("sentiment", None)
        self.confidence_scores = kwargs.get("confidence_scores", None)
        self.offset = kwargs.get("offset", None)
        self.mined_opinions = kwargs.get("mined_opinions", None)

    @classmethod
    def _from_generated(cls, sentence, results, sentiment):
        offset = sentence.offset
        if isinstance(sentence, _v3_0_models.SentenceSentiment):
            # we do not return offset for v3.0 since
            # the correct encoding was not introduced for v3.0
            offset = None
        if hasattr(sentence, "aspects"):
            mined_opinions = (
                [MinedOpinion._from_generated(aspect, results, sentiment) for aspect in sentence.aspects]  # pylint: disable=protected-access
                if sentence.aspects else []
            )
        else:
            mined_opinions = None
        return cls(
            text=sentence.text,
            sentiment=sentence.sentiment,
            confidence_scores=SentimentConfidenceScores._from_generated(sentence.confidence_scores),  # pylint: disable=protected-access
            offset=offset,
            mined_opinions=mined_opinions
        )

    def __repr__(self):
        return "SentenceSentiment(text={}, sentiment={}, confidence_scores={}, "\
            "offset={}, mined_opinions={})".format(
            self.text,
            self.sentiment,
            repr(self.confidence_scores),
            self.offset,
            repr(self.mined_opinions)
        )[:1024]

class MinedOpinion(DictMixin):
    """A mined opinion object represents an opinion we've extracted from a sentence.
    It consists of both an aspect that these opinions are about, and the actual
    opinions themselves.

    :ivar aspect: The aspect of a product/service that this opinion is about
    :vartype aspect: ~azure.ai.textanalytics.AspectSentiment
    :ivar opinions: The actual opinions of the aspect
    :vartype opinions: list[~azure.ai.textanalytics.OpinionSentiment]
    """

    def __init__(self, **kwargs):
        self.aspect = kwargs.get("aspect", None)
        self.opinions = kwargs.get("opinions", None)

    @staticmethod
    def _get_opinions(relations, results, sentiment):  # pylint: disable=unused-argument
        if not relations:
            return []
        opinion_relations = [r.ref for r in relations if r.relation_type == "opinion"]
        opinions = []
        for opinion_relation in opinion_relations:
            nums = _get_indices(opinion_relation)
            sentence_index = nums[1]
            opinion_index = nums[2]
            opinions.append(
                sentiment.sentences[sentence_index].opinions[opinion_index]
            )
        return opinions

    @classmethod
    def _from_generated(cls, aspect, results, sentiment):
        return cls(
            aspect=AspectSentiment._from_generated(aspect),  # pylint: disable=protected-access
            opinions=[
                OpinionSentiment._from_generated(opinion)  # pylint: disable=protected-access
                for opinion in cls._get_opinions(aspect.relations, results, sentiment)
            ],
        )

    def __repr__(self):
        return "MinedOpinion(aspect={}, opinions={})".format(
            repr(self.aspect),
            repr(self.opinions)
        )[:1024]


class AspectSentiment(DictMixin):
    """AspectSentiment contains the related opinions, predicted sentiment,
    confidence scores and other information about an aspect of a product.
    An aspect of a product/service is a key component of that product/service.
    For example in "The food at Hotel Foo is good", "food" is an aspect of
    "Hotel Foo".

    :ivar str text: The aspect text.
    :ivar str sentiment: The predicted Sentiment for the aspect. Possible values
        include 'positive', 'mixed', and 'negative'.
    :ivar confidence_scores: The sentiment confidence score between 0
        and 1 for the aspect for 'positive' and 'negative' labels. It's score
        for 'neutral' will always be 0
    :vartype confidence_scores:
        ~azure.ai.textanalytics.SentimentConfidenceScores
    :ivar int offset: The aspect offset from the start of the document. Returned
        in unicode code points.
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.sentiment = kwargs.get("sentiment", None)
        self.confidence_scores = kwargs.get("confidence_scores", None)
        self.offset = kwargs.get("offset", None)

    @classmethod
    def _from_generated(cls, aspect):
        return cls(
            text=aspect.text,
            sentiment=aspect.sentiment,
            confidence_scores=SentimentConfidenceScores._from_generated(aspect.confidence_scores),  # pylint: disable=protected-access
            offset=aspect.offset,
        )

    def __repr__(self):
        return "AspectSentiment(text={}, sentiment={}, confidence_scores={}, offset={})".format(
            self.text,
            self.sentiment,
            repr(self.confidence_scores),
            self.offset,
        )[:1024]


class OpinionSentiment(DictMixin):
    """OpinionSentiment contains the predicted sentiment,
    confidence scores and other information about an opinion of an aspect.
    For example, in the sentence "The food is good", the opinion of the
    aspect 'food' is 'good'.

    :ivar str text: The opinion text.
    :ivar str sentiment: The predicted Sentiment for the opinion. Possible values
        include 'positive', 'mixed', and 'negative'.
    :ivar confidence_scores: The sentiment confidence score between 0
        and 1 for the opinion for 'positive' and 'negative' labels. It's score
        for 'neutral' will always be 0
    :vartype confidence_scores:
        ~azure.ai.textanalytics.SentimentConfidenceScores
    :ivar int offset: The opinion offset from the start of the document. Returned
        in unicode code points.
    :ivar bool is_negated: Whether the opinion is negated. For example, in
        "The food is not good", the opinion "good" is negated.
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.sentiment = kwargs.get("sentiment", None)
        self.confidence_scores = kwargs.get("confidence_scores", None)
        self.offset = kwargs.get("offset", None)
        self.is_negated = kwargs.get("is_negated", None)

    @classmethod
    def _from_generated(cls, opinion):
        return cls(
            text=opinion.text,
            sentiment=opinion.sentiment,
            confidence_scores=SentimentConfidenceScores._from_generated(opinion.confidence_scores),  # pylint: disable=protected-access
            offset=opinion.offset,
            is_negated=opinion.is_negated
        )

    def __repr__(self):
        return (
            "OpinionSentiment(text={}, sentiment={}, confidence_scores={}, offset={}, is_negated={})".format(
                self.text,
                self.sentiment,
                repr(self.confidence_scores),
                self.offset,
                self.is_negated
            )[:1024]
        )


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
        self.positive = kwargs.get('positive', 0.0)
        self.neutral = kwargs.get('neutral', 0.0)
        self.negative = kwargs.get('negative', 0.0)

    @classmethod
    def _from_generated(cls, score):
        return cls(
            positive=score.positive,
            neutral=score.neutral if hasattr(score, "neutral") else 0.0,
            negative=score.negative
        )

    def __repr__(self):
        return "SentimentConfidenceScores(positive={}, neutral={}, negative={})" \
            .format(self.positive, self.neutral, self.negative)[:1024]


class EntitiesRecognitionTask(DictMixin):
    """EntitiesRecognitionTask encapsulates the parameters for starting a long-running Entities Recognition operation.

    :ivar str model_version: The model version to use for the analysis.
    """

    def __init__(self, **kwargs):
        self.model_version = kwargs.get("model_version", "latest")

    def __repr__(self, **kwargs):
        return "EntitiesRecognitionTask(model_version={})" \
            .format(self.model_version)[:1024]

    def to_generated(self):
        return _v3_1_preview_3_models.EntitiesTask(
            parameters=_v3_1_preview_3_models.EntitiesTaskParameters(
                model_version=self.model_version
            )
        )


class EntitiesRecognitionTaskResult(DictMixin):
    """EntitiesRecognitionTaskResult contains the results of a single Entities Recognition task,
        including additional task metadata.

    :ivar str name: The name of the task.
    :ivar results: The results of the analysis.
    :vartype results: list[~azure.ai.textanalytics.RecognizeEntitiesResult]
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.results = kwargs.get("results", [])

    def __repr__(self, **kwargs):
        return "EntitiesRecognitionTaskResult(name={}, results={})" \
            .format(self.name, repr(self.results))[:1024]


class PiiEntitiesRecognitionTask(DictMixin):
    """PiiEntitiesRecognitionTask encapsulates the parameters for starting a
    long-running PII Entities Recognition operation.

    :ivar str model_version: The model version to use for the analysis.
    :ivar str domain: An optional string to set the PII domain to include only a
    subset of the entity categories. Possible values include 'PHI' or None.
    """

    def __init__(self, **kwargs):
        self.model_version = kwargs.get("model_version", "latest")
        self.domain = kwargs.get("domain", None)

    def __repr__(self, **kwargs):
        return "PiiEntitiesRecognitionTask(model_version={}, domain={})" \
            .format(self.model_version, self.domain)[:1024]

    def to_generated(self):
        return _v3_1_preview_3_models.PiiTask(
            parameters=_v3_1_preview_3_models.PiiTaskParameters(
                model_version=self.model_version,
                domain=self.domain
            )
        )


class PiiEntitiesRecognitionTaskResult(DictMixin):
    """PiiEntitiesRecognitionTaskResult contains the results of a single PII Entities Recognition task,
        including additional task metadata.

    :ivar str name: The name of the task.
    :ivar results: The results of the analysis.
    :vartype results: list[~azure.ai.textanalytics.RecognizePiiEntitiesResult]
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.results = kwargs.get("results", [])

    def __repr__(self, **kwargs):
        return "PiiEntitiesRecognitionTaskResult(name={}, results={})" \
            .format(self.name, repr(self.results))[:1024]


class KeyPhraseExtractionTask(DictMixin):
    """KeyPhraseExtractionTask encapsulates the parameters for starting a long-running Key Phrase Extraction operation.

    :ivar str model_version: The model version to use for the analysis.
    """

    def __init__(self, **kwargs):
        self.model_version = kwargs.get("model_version", "latest")

    def __repr__(self, **kwargs):
        return "KeyPhraseExtractionTask(model_version={})" \
            .format(self.model_version)[:1024]

    def to_generated(self):
        return _v3_1_preview_3_models.KeyPhrasesTask(
            parameters=_v3_1_preview_3_models.KeyPhrasesTaskParameters(
                model_version=self.model_version
            )
        )


class KeyPhraseExtractionTaskResult(DictMixin):
    """KeyPhraseExtractionTaskResult contains the results of a single Key Phrase Extraction task, including additional
        task metadata.

    :ivar str name: The name of the task.
    :ivar results: The results of the analysis.
    :vartype results: list[~azure.ai.textanalytics.ExtractKeyPhrasesResult]
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.results = kwargs.get("results", [])

    def __repr__(self, **kwargs):
        return "KeyPhraseExtractionTaskResult(name={}, results={})" \
            .format(self.name, repr(self.results))[:1024]


class TextAnalysisResult(DictMixin):
    """TextAnalysisResult contains the results of multiple text analyses performed on a batch of documents.

    :ivar entities_recognition_results: A list of objects containing results for all Entity Recognition tasks
        included in the analysis.
    :vartype entities_recognition_results: list[~azure.ai.textanalytics.EntitiesRecognitionTaskResult]
    :ivar pii_entities_recognition_results: A list of objects containing results for all PII Entity Recognition
        tasks included in the analysis.
    :vartype pii_entities_recogition_results: list[~azure.ai.textanalytics.PiiEntitiesRecognitionTaskResult]
    :ivar key_phrase_extraction_results: A list of objects containing results for all Key Phrase Extraction tasks
        included in the analysis.
    :vartype key_phrase_extraction_results: list[~azure.ai.textanalytics.KeyPhraseExtractionTaskResult]
    """
    def __init__(self, **kwargs):
        self.entities_recognition_results = kwargs.get("entities_recognition_results", [])
        self.pii_entities_recognition_results = kwargs.get("pii_entities_recognition_results", [])
        self.key_phrase_extraction_results = kwargs.get("key_phrase_extraction_results", [])

    def __repr__(self):
        return "TextAnalysisResult(entities_recognition_results={}, pii_entities_recognition_results={}, \
            key_phrase_extraction_results={})" \
            .format(
                repr(self.entities_recognition_results),
                repr(self.pii_entities_recognition_results),
                repr(self.key_phrase_extraction_results)
            )[:1024]


class RequestStatistics(DictMixin):
    def __init__(self, **kwargs):
        self.documents_count = kwargs.get("documents_count")
        self.valid_documents_count = kwargs.get("valid_documents_count")
        self.erroneous_documents_count = kwargs.get("erroneous_documents_count")
        self.transactions_count = kwargs.get("transactions_count")

    @classmethod
    def _from_generated(cls, request_statistics):
        return cls(
            documents_count=request_statistics.documents_count,
            valid_documents_count=request_statistics.valid_documents_count,
            erroneous_documents_count=request_statistics.erroneous_documents_count,
            transactions_count=request_statistics.transactions_count
        )

    def __repr__(self, **kwargs):
        return "RequestStatistics(documents_count={}, valid_documents_count={}, erroneous_documents_count={}, \
            transactions_count={}".format(
                self.documents_count,
                self.valid_documents_count,
                self.erroneous_documents_count,
                self.transactions_count
            )[:1024]

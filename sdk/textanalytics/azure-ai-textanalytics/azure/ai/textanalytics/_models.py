# pylint: disable=too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=unused-argument
import re
from enum import Enum
from typing import Optional, List, Any, Union
from typing_extensions import Literal
from azure.core import CaseInsensitiveEnumMeta
from ._generated.models import (
    LanguageInput,
    MultiLanguageInput,
    PiiEntityCategory,
)
from ._generated.v3_0 import models as _v3_0_models
from ._generated.v3_1 import models as _v3_1_models
from ._generated.v2023_04_01 import models as _v2023_04_01_models
from ._check import is_language_api, string_index_type_compatibility
from ._dict_mixin import DictMixin

STRING_INDEX_TYPE_DEFAULT = "UnicodeCodePoint"

def _get_indices(relation):
    return [int(s) for s in re.findall(r"\d+", relation)]


class TextAnalysisKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Enumeration of supported Text Analysis kinds.

    .. versionadded:: 2022-05-01
        The *TextAnalysisKind* enum.
    """

    SENTIMENT_ANALYSIS = "SentimentAnalysis"
    ENTITY_RECOGNITION = "EntityRecognition"
    PII_ENTITY_RECOGNITION = "PiiEntityRecognition"
    KEY_PHRASE_EXTRACTION = "KeyPhraseExtraction"
    ENTITY_LINKING = "EntityLinking"
    HEALTHCARE = "Healthcare"
    CUSTOM_ENTITY_RECOGNITION = "CustomEntityRecognition"
    CUSTOM_DOCUMENT_CLASSIFICATION = "CustomDocumentClassification"
    LANGUAGE_DETECTION = "LanguageDetection"
    EXTRACTIVE_SUMMARIZATION = "ExtractiveSummarization"
    ABSTRACTIVE_SUMMARIZATION = "AbstractiveSummarization"


class PiiEntityDomain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The different domains of PII entities that users can filter by"""

    PROTECTED_HEALTH_INFORMATION = (
        "phi"  # See https://aka.ms/azsdk/language/pii for more information.
    )


class DetectedLanguage(DictMixin):
    """DetectedLanguage contains the predicted language found in text,
    its confidence score, and its ISO 639-1 representation.
    """

    name: str
    """Long name of a detected language (e.g. English,
        French)."""
    iso6391_name: str
    """A two letter representation of the detected
        language according to the ISO 639-1 standard (e.g. en, fr)."""
    confidence_score: float
    """A confidence score between 0 and 1. Scores close
        to 1 indicate 100% certainty that the identified language is true."""

    def __init__(self, **kwargs: Any) -> None:
        self.name = kwargs.get("name", None)
        self.iso6391_name = kwargs.get("iso6391_name", None)
        self.confidence_score = kwargs.get("confidence_score", None)

    @classmethod
    def _from_generated(cls, language):
        return cls(
            name=language.name,
            iso6391_name=language.iso6391_name,
            confidence_score=language.confidence_score,
        )

    def __repr__(self) -> str:
        return (
            f"DetectedLanguage(name={self.name}, iso6391_name={self.iso6391_name}, "
            f"confidence_score={self.confidence_score})"[:1024]
        )


class RecognizeEntitiesResult(DictMixin):
    """RecognizeEntitiesResult is a result object which contains
    the recognized entities from a particular document.
    """

    id: str  # pylint: disable=redefined-builtin
    """Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document."""
    entities: List["CategorizedEntity"]
    """Recognized entities in the document."""
    warnings: List["TextAnalyticsWarning"]
    """Warnings encountered while processing document. Results will still be returned
        if there are warnings, but they may not be fully accurate."""
    statistics: Optional["TextDocumentStatistics"] = None
    """If `show_stats=True` was specified in the request this
        field will contain information about the document payload."""
    is_error: Literal[False] = False
    """Boolean check for error item when iterating over list of
        results. Always False for an instance of a RecognizeEntitiesResult."""
    kind: Literal["EntityRecognition"] = "EntityRecognition"
    """The text analysis kind - "EntityRecognition"."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", None)
        self.entities = kwargs.get("entities", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.is_error: Literal[False] = False
        self.kind: Literal["EntityRecognition"] = "EntityRecognition"

    def __repr__(self) -> str:
        return (
            f"RecognizeEntitiesResult(id={self.id}, entities={repr(self.entities)}, "
            f"warnings={repr(self.warnings)}, statistics={repr(self.statistics)}, "
            f"is_error={self.is_error}, kind={self.kind})"[:1024]
        )


class RecognizePiiEntitiesResult(DictMixin):
    """RecognizePiiEntitiesResult is a result object which contains
    the recognized Personally Identifiable Information (PII) entities
    from a particular document.
    """

    id: str  # pylint: disable=redefined-builtin
    """Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document."""
    entities: List["PiiEntity"]
    """Recognized PII entities in the document."""
    redacted_text: str
    """Returns the text of the input document with all of the PII information
        redacted out."""
    warnings: List["TextAnalyticsWarning"]
    """Warnings encountered while processing document. Results will still be returned
        if there are warnings, but they may not be fully accurate."""
    statistics: Optional["TextDocumentStatistics"] = None
    """If `show_stats=True` was specified in the request this
        field will contain information about the document payload."""
    is_error: Literal[False] = False
    """Boolean check for error item when iterating over list of
        results. Always False for an instance of a RecognizePiiEntitiesResult."""
    kind: Literal["PiiEntityRecognition"] = "PiiEntityRecognition"
    """The text analysis kind - "PiiEntityRecognition"."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", None)
        self.entities = kwargs.get("entities", None)
        self.redacted_text = kwargs.get("redacted_text", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.is_error: Literal[False] = False
        self.kind: Literal["PiiEntityRecognition"] = "PiiEntityRecognition"

    def __repr__(self) -> str:
        return (
            f"RecognizePiiEntitiesResult(id={self.id}, entities={repr(self.entities)}, "
            f"redacted_text={self.redacted_text}, warnings={repr(self.warnings)}, "
            f"statistics={repr(self.statistics)}, "
            f"is_error={self.is_error}, kind={self.kind})"[:1024]
        )


class AnalyzeHealthcareEntitiesResult(DictMixin):
    """
    AnalyzeHealthcareEntitiesResult contains the Healthcare entities from a
    particular document.
    """

    id: str  # pylint: disable=redefined-builtin
    """Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document."""
    entities: List["HealthcareEntity"]
    """Identified Healthcare entities in the document, i.e. in
        the document "The subject took ibuprofen", "ibuprofen" is an identified entity
        from the document."""
    entity_relations: List["HealthcareRelation"]
    """Identified Healthcare relations between entities. For example, in the
        document "The subject took 100mg of ibuprofen", we would identify the relationship
        between the dosage of 100mg and the medication ibuprofen."""
    warnings: List["TextAnalyticsWarning"]
    """Warnings encountered while processing document. Results will still be returned
        if there are warnings, but they may not be fully accurate."""
    statistics: Optional["TextDocumentStatistics"] = None
    """If show_stats=true was specified in the request this
        field will contain information about the document payload."""
    is_error: Literal[False] = False
    """Boolean check for error item when iterating over list of
        results. Always False for an instance of a AnalyzeHealthcareEntitiesResult."""
    kind: Literal["Healthcare"] = "Healthcare"
    """The text analysis kind - "Healthcare"."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", None)
        self.entities = kwargs.get("entities", None)
        self.entity_relations = kwargs.get("entity_relations", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.is_error: Literal[False] = False
        self.kind: Literal["Healthcare"] = "Healthcare"

    @classmethod
    def _from_generated(cls, healthcare_result):
        entities = [
            HealthcareEntity._from_generated(e)  # pylint: disable=protected-access
            for e in healthcare_result.entities
        ]
        relations = [
            HealthcareRelation._from_generated(  # pylint: disable=protected-access
                r, entities
            )
            for r in healthcare_result.relations
        ]
        return cls(
            id=healthcare_result.id,
            entities=entities,
            entity_relations=relations,
            warnings=[
                TextAnalyticsWarning._from_generated(  # pylint: disable=protected-access
                    w
                )
                for w in healthcare_result.warnings
            ],
            statistics=TextDocumentStatistics._from_generated(  # pylint: disable=protected-access
                healthcare_result.statistics
            ),
        )

    def __repr__(self) -> str:
        return (
            f"AnalyzeHealthcareEntitiesResult(id={self.id}, entities={repr(self.entities)}, "
            f"entity_relations={repr(self.entity_relations)}, warnings={repr(self.warnings)}, "
            f"statistics={repr(self.statistics)}, is_error={self.is_error}, kind={self.kind})"[:1024]
        )


class HealthcareRelation(DictMixin):
    """HealthcareRelation is a result object which represents a relation detected in a document.

    Every HealthcareRelation is an entity graph of a certain relation type,
    where all entities are connected and have specific roles within the relation context.

    .. versionadded:: 2023-04-01
        The *confidence_score* property.
    """

    relation_type: str
    """The type of relation, i.e. the relationship between "100mg" and
        "ibuprofen" in the document "The subject took 100 mg of ibuprofen" is "DosageOfMedication".
        Possible values found in :class:`~azure.ai.textanalytics.HealthcareEntityRelation`"""
    roles: List["HealthcareRelationRole"]
    """The roles present in this relation. I.e., in the document
        "The subject took 100 mg of ibuprofen", the present roles are "Dosage" and "Medication"."""
    confidence_score: Optional[float] = None
    """Confidence score between 0 and 1 of the extracted relation."""

    def __init__(self, **kwargs: Any) -> None:
        self.relation_type = kwargs.get("relation_type", None)
        self.roles = kwargs.get("roles", None)
        self.confidence_score = kwargs.get("confidence_score", None)

    @classmethod
    def _from_generated(cls, healthcare_relation_result, entities):
        roles = [
            HealthcareRelationRole._from_generated(  # pylint: disable=protected-access
                r, entities
            )
            for r in healthcare_relation_result.entities
        ]
        confidence_score = healthcare_relation_result.confidence_score \
            if hasattr(healthcare_relation_result, "confidence_score") else None
        return cls(
            relation_type=healthcare_relation_result.relation_type,
            roles=roles,
            confidence_score=confidence_score,
        )

    def __repr__(self) -> str:
        return f"HealthcareRelation(relation_type={self.relation_type}, roles={repr(self.roles)}, " \
               f"confidence_score={self.confidence_score})"[:1024]


class HealthcareRelationRole(DictMixin):
    """A model representing a role in a relation.

    For example, in "The subject took 100 mg of ibuprofen",
    "100 mg" is a dosage entity fulfilling the role "Dosage"
    in the extracted relation "DosageOfMedication".
    """

    name: str
    """The role of the entity in the relationship. I.e., in the relation
        "The subject took 100 mg of ibuprofen", the dosage entity "100 mg" has role
        "Dosage"."""
    entity: "HealthcareEntity"
    """The entity that is present in the relationship. For example, in
        "The subject took 100 mg of ibuprofen", this property holds the dosage entity
        of "100 mg"."""

    def __init__(self, **kwargs: Any) -> None:
        self.name = kwargs.get("name", None)
        self.entity = kwargs.get("entity", None)

    @staticmethod
    def _get_entity(healthcare_role_result, entities):
        numbers = _get_indices(healthcare_role_result.ref)
        entity_index = numbers[
            1
        ]  # first number parsed from index is document #, second is entity index
        return entities[entity_index]

    @classmethod
    def _from_generated(cls, healthcare_role_result, entities):
        return cls(
            name=healthcare_role_result.role,
            entity=HealthcareRelationRole._get_entity(healthcare_role_result, entities),
        )

    def __repr__(self) -> str:
        return f"HealthcareRelationRole(name={self.name}, entity={repr(self.entity)})"[:1024]


class DetectLanguageResult(DictMixin):
    """DetectLanguageResult is a result object which contains
    the detected language of a particular document.
    """

    id: str  # pylint: disable=redefined-builtin
    """Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document."""
    primary_language: DetectedLanguage
    """The primary language detected in the document."""
    warnings: List["TextAnalyticsWarning"]
    """Warnings encountered while processing document. Results will still be returned
        if there are warnings, but they may not be fully accurate."""
    statistics: Optional["TextDocumentStatistics"] = None
    """If `show_stats=True` was specified in the request this
        field will contain information about the document payload."""
    is_error: Literal[False] = False
    """Boolean check for error item when iterating over list of
        results. Always False for an instance of a DetectLanguageResult."""
    kind: Literal["LanguageDetection"] = "LanguageDetection"
    """The text analysis kind - "LanguageDetection"."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", None)
        self.primary_language = kwargs.get("primary_language", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.is_error: Literal[False] = False
        self.kind: Literal["LanguageDetection"] = "LanguageDetection"

    def __repr__(self) -> str:
        return (
            f"DetectLanguageResult(id={self.id}, primary_language={repr(self.primary_language)}, "
            f"warnings={repr(self.warnings)}, statistics={repr(self.statistics)}, is_error={self.is_error}, "
            f"kind={self.kind})"[:1024]
        )


class CategorizedEntity(DictMixin):
    """CategorizedEntity contains information about a particular
    entity found in text.

    .. versionadded:: v3.1
        The *offset* and *length* properties.
    """

    text: str
    """Entity text as appears in the request."""
    category: str
    """Entity category, such as Person/Location/Org/SSN etc"""
    length: int
    """The entity text length.  This value depends on the value of the
        `string_index_type` parameter set in the original request, which is UnicodeCodePoints
        by default."""
    offset: int
    """The entity text offset from the start of the document.
        The value depends on the value of the `string_index_type` parameter
        set in the original request, which is UnicodeCodePoints by default."""
    confidence_score: float
    """Confidence score between 0 and 1 of the extracted
        entity."""
    subcategory: Optional[str] = None
    """Entity subcategory, such as Age/Year/TimeRange etc"""

    def __init__(self, **kwargs: Any) -> None:
        self.text = kwargs.get("text", None)
        self.category = kwargs.get("category", None)
        self.subcategory = kwargs.get("subcategory", None)
        self.length = kwargs.get("length", None)
        self.offset = kwargs.get("offset", None)
        self.confidence_score = kwargs.get("confidence_score", None)

    @classmethod
    def _from_generated(cls, entity):
        offset = entity.offset
        length = entity.length
        if isinstance(entity, _v3_0_models.Entity):
            # we do not return offset for v3.0 since
            # the correct encoding was not introduced for v3.0
            offset = None
            length = None

        return cls(
            text=entity.text,
            category=entity.category,
            subcategory=entity.subcategory,
            length=length,
            offset=offset,
            confidence_score=entity.confidence_score,
        )

    def __repr__(self) -> str:
        return (
            f"CategorizedEntity(text={self.text}, category={self.category}, subcategory={self.subcategory}, "
            f"length={self.length}, offset={self.offset}, confidence_score={self.confidence_score})"[:1024]
        )


class PiiEntity(DictMixin):
    """PiiEntity contains information about a Personally Identifiable
    Information (PII) entity found in text.
    """

    text: str
    """Entity text as appears in the request."""
    category: str
    """Entity category, such as Financial Account
        Identification/Social Security Number/Phone Number, etc."""
    length: int
    """The PII entity text length.  This value depends on the value
        of the `string_index_type` parameter specified in the original request, which
        is UnicodeCodePoints by default."""
    offset: int
    """The PII entity text offset from the start of the document.
        This value depends on the value of the `string_index_type` parameter specified
        in the original request, which is UnicodeCodePoints by default."""
    confidence_score: float
    """Confidence score between 0 and 1 of the extracted entity."""
    subcategory: Optional[str] = None
    """Entity subcategory, such as Credit Card/EU
        Phone number/ABA Routing Numbers, etc."""

    def __init__(self, **kwargs: Any) -> None:
        self.text = kwargs.get("text", None)
        self.category = kwargs.get("category", None)
        self.subcategory = kwargs.get("subcategory", None)
        self.length = kwargs.get("length", None)
        self.offset = kwargs.get("offset", None)
        self.confidence_score = kwargs.get("confidence_score", None)

    @classmethod
    def _from_generated(cls, entity):
        return cls(
            text=entity.text,
            category=entity.category,
            subcategory=entity.subcategory,
            length=entity.length,
            offset=entity.offset,
            confidence_score=entity.confidence_score,
        )

    def __repr__(self) -> str:
        return (
            f"PiiEntity(text={self.text}, category={self.category}, subcategory={self.subcategory}, "
            f"length={self.length}, offset={self.offset}, confidence_score={self.confidence_score})"[:1024]
        )


class HealthcareEntity(DictMixin):
    """HealthcareEntity contains information about a Healthcare entity found in text.
    """

    text: str
    """Entity text as appears in the document."""
    category: str
    """Entity category, see the :class:`~azure.ai.textanalytics.HealthcareEntityCategory`
        type for possible healthcare entity categories."""
    length: int
    """The entity text length.  This value depends on the value
        of the `string_index_type` parameter specified in the original request, which is
        UnicodeCodePoints by default."""
    offset: int
    """The entity text offset from the start of the document.
        This value depends on the value of the `string_index_type` parameter specified
        in the original request, which is UnicodeCodePoints by default."""
    confidence_score: float
    """Confidence score between 0 and 1 of the extracted entity."""
    subcategory: Optional[str] = None
    """Entity subcategory."""
    assertion: Optional["HealthcareEntityAssertion"] = None
    """Contains various assertions about this entity. For example, if
        an entity is a diagnosis, is this diagnosis 'conditional' on a symptom?
        Are the doctors 'certain' about this diagnosis? Is this diagnosis 'associated'
        with another diagnosis?"""
    normalized_text: Optional[str] = None
    """Normalized version of the raw `text` we extract
        from the document. Not all `text` will have a normalized version."""
    data_sources: Optional[List["HealthcareEntityDataSource"]]
    """A collection of entity references in known data sources."""

    def __init__(self, **kwargs: Any) -> None:
        self.text = kwargs.get("text", None)
        self.normalized_text = kwargs.get("normalized_text", None)
        self.category = kwargs.get("category", None)
        self.subcategory = kwargs.get("subcategory", None)
        self.assertion = kwargs.get("assertion", None)
        self.length = kwargs.get("length", None)
        self.offset = kwargs.get("offset", None)
        self.confidence_score = kwargs.get("confidence_score", None)
        self.data_sources = kwargs.get("data_sources", [])

    @classmethod
    def _from_generated(cls, healthcare_entity):
        assertion = None
        try:
            if healthcare_entity.assertion:
                assertion = HealthcareEntityAssertion._from_generated(  # pylint: disable=protected-access
                    healthcare_entity.assertion
                )
        except AttributeError:
            assertion = None

        return cls(
            text=healthcare_entity.text,
            normalized_text=healthcare_entity.name,
            category=healthcare_entity.category,
            subcategory=healthcare_entity.subcategory,
            assertion=assertion,
            length=healthcare_entity.length,
            offset=healthcare_entity.offset,
            confidence_score=healthcare_entity.confidence_score,
            data_sources=[
                HealthcareEntityDataSource(entity_id=l.id, name=l.data_source)
                for l in healthcare_entity.links
            ]
            if healthcare_entity.links
            else None,
        )

    def __hash__(self) -> int:
        return hash(repr(self))

    def __repr__(self) -> str:
        return (
            f"HealthcareEntity(text={self.text}, normalized_text={self.normalized_text}, "
            f"category={self.category}, subcategory={self.subcategory}, assertion={repr(self.assertion)}, "
            f"length={self.length}, offset={self.offset}, confidence_score={self.confidence_score}, "
            f"data_sources={repr(self.data_sources)})"[:1024]
        )


class HealthcareEntityAssertion(DictMixin):
    """Contains various assertions about a `HealthcareEntity`.

    For example, if an entity is a diagnosis, is this diagnosis 'conditional' on a symptom?
    Are the doctors 'certain' about this diagnosis? Is this diagnosis 'associated'
    with another diagnosis?
    """

    conditionality: Optional[str] = None
    """Describes whether the healthcare entity it's on is conditional
        on another entity. For example, "If the patient has a fever, he has pneumonia", the diagnosis of pneumonia
        is 'conditional' on whether the patient has a fever. Possible values are "hypothetical" and
        "conditional"."""
    certainty: Optional[str] = None
    """Describes how certain the healthcare entity it's on is. For example,
        in "The patient may have a fever", the fever entity is not 100% certain, but is instead
        "positivePossible". Possible values are "positive", "positivePossible", "neutralPossible",
        "negativePossible", and "negative"."""
    association: Optional[str] = None
    """Describes whether the healthcare entity it's on is the subject of the document, or
        if this entity describes someone else in the document. For example, in "The subject's mother has
        a fever", the "fever" entity is not associated with the subject themselves, but with the subject's
        mother. Possible values are "subject" and "other"."""

    def __init__(self, **kwargs: Any) -> None:
        self.conditionality = kwargs.get("conditionality", None)
        self.certainty = kwargs.get("certainty", None)
        self.association = kwargs.get("association", None)

    @classmethod
    def _from_generated(cls, healthcare_assertion):
        return cls(
            conditionality=healthcare_assertion.conditionality,
            certainty=healthcare_assertion.certainty,
            association=healthcare_assertion.association,
        )

    def __repr__(self) -> str:
        return f"HealthcareEntityAssertion(conditionality={self.conditionality}, certainty={self.certainty}, " \
               f"association={self.association})"[:1024]


class HealthcareEntityDataSource(DictMixin):
    """
    HealthcareEntityDataSource contains information representing an entity reference in a known data source.
    """

    entity_id: str
    """ID of the entity in the given source catalog."""
    name: str
    """The name of the entity catalog from where the entity was identified, such as UMLS, CHV, MSH, etc."""

    def __init__(self, **kwargs: Any) -> None:
        self.entity_id = kwargs.get("entity_id", None)
        self.name = kwargs.get("name", None)

    def __repr__(self) -> str:
        return (
            f"HealthcareEntityDataSource(entity_id={self.entity_id}, name={self.name})"[:1024]
        )


class TextAnalyticsError(DictMixin):
    """TextAnalyticsError contains the error code, message, and
    other details that explain why the batch or individual document
    failed to be processed by the service.
    """

    code: str
    """Error code. Possible values include
     'invalidRequest', 'invalidArgument', 'internalServerError',
     'serviceUnavailable', 'invalidParameterValue', 'invalidRequestBodyFormat',
     'emptyRequest', 'missingInputRecords', 'invalidDocument', 'modelVersionIncorrect',
     'invalidDocumentBatch', 'unsupportedLanguageCode', 'invalidCountryHint'"""
    message: str
    """Error message."""
    target: Optional[str] = None
    """Error target."""

    def __init__(self, **kwargs: Any) -> None:
        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)
        self.target = kwargs.get("target", None)

    @classmethod
    def _from_generated(cls, err):
        if err.innererror:
            return cls(
                code=err.innererror.code,
                message=err.innererror.message,
                target=err.innererror.target,
            )
        return cls(code=err.code, message=err.message, target=err.target)

    def __repr__(self) -> str:
        return f"TextAnalyticsError(code={self.code}, message={self.message}, target={self.target})"[:1024]


class TextAnalyticsWarning(DictMixin):
    """TextAnalyticsWarning contains the warning code and message that explains why
    the response has a warning.
    """

    code: str
    """Warning code. Possible values include 'LongWordsInDocument',
     'DocumentTruncated'."""
    message: str
    """Warning message."""

    def __init__(self, **kwargs: Any) -> None:
        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)

    @classmethod
    def _from_generated(cls, warning):
        return cls(
            code=warning.code,
            message=warning.message,
        )

    def __repr__(self) -> str:
        return f"TextAnalyticsWarning(code={self.code}, message={self.message})"[:1024]


class ExtractKeyPhrasesResult(DictMixin):
    """ExtractKeyPhrasesResult is a result object which contains
    the key phrases found in a particular document.
    """

    id: str  # pylint: disable=redefined-builtin
    """Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document."""
    key_phrases: List[str]
    """A list of representative words or phrases.
        The number of key phrases returned is proportional to the number of words
        in the input document."""
    warnings: List[TextAnalyticsWarning]
    """Warnings encountered while processing document. Results will still be returned
        if there are warnings, but they may not be fully accurate."""
    statistics: Optional["TextDocumentStatistics"] = None
    """If `show_stats=True` was specified in the request this
        field will contain information about the document payload."""
    is_error: Literal[False] = False
    """Boolean check for error item when iterating over list of
        results. Always False for an instance of a ExtractKeyPhrasesResult."""
    kind: Literal["KeyPhraseExtraction"] = "KeyPhraseExtraction"
    """The text analysis kind - "KeyPhraseExtraction"."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", None)
        self.key_phrases = kwargs.get("key_phrases", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.is_error: Literal[False] = False
        self.kind: Literal["KeyPhraseExtraction"] = "KeyPhraseExtraction"

    def __repr__(self) -> str:
        return (
            f"ExtractKeyPhrasesResult(id={self.id}, key_phrases={self.key_phrases}, "
            f"warnings={repr(self.warnings)}, statistics={repr(self.statistics)}, "
            f"is_error={self.is_error}, kind={self.kind})"[:1024]
        )


class RecognizeLinkedEntitiesResult(DictMixin):
    """RecognizeLinkedEntitiesResult is a result object which contains
    links to a well-known knowledge base, like for example, Wikipedia or Bing.
    """

    id: str  # pylint: disable=redefined-builtin
    """Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document."""
    entities: List["LinkedEntity"]
    """Recognized well-known entities in the document."""
    warnings: List[TextAnalyticsWarning]
    """Warnings encountered while processing document. Results will still be returned
        if there are warnings, but they may not be fully accurate."""
    statistics: Optional["TextDocumentStatistics"] = None
    """If `show_stats=True` was specified in the request this
        field will contain information about the document payload."""
    is_error: Literal[False] = False
    """Boolean check for error item when iterating over list of
        results. Always False for an instance of a RecognizeLinkedEntitiesResult."""
    kind: Literal["EntityLinking"] = "EntityLinking"
    """The text analysis kind - "EntityLinking"."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", None)
        self.entities = kwargs.get("entities", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.is_error: Literal[False] = False
        self.kind: Literal["EntityLinking"] = "EntityLinking"

    def __repr__(self) -> str:
        return (
            f"RecognizeLinkedEntitiesResult(id={self.id}, entities={repr(self.entities)}, "
            f"warnings={repr(self.warnings)}, statistics={repr(self.statistics)}, "
            f"is_error={self.is_error}, kind={self.kind})"[:1024]
        )


class AnalyzeSentimentResult(DictMixin):
    """AnalyzeSentimentResult is a result object which contains
    the overall predicted sentiment and confidence scores for your document
    and a per-sentence sentiment prediction with scores.
    """

    id: str  # pylint: disable=redefined-builtin
    """Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document."""
    sentiment: str
    """Predicted sentiment for document (Negative,
        Neutral, Positive, or Mixed). Possible values include 'positive',
        'neutral', 'negative', 'mixed'"""
    confidence_scores: "SentimentConfidenceScores"
    """Document level sentiment confidence
        scores between 0 and 1 for each sentiment label."""
    sentences: List["SentenceSentiment"]
    """Sentence level sentiment analysis."""
    warnings: List[TextAnalyticsWarning]
    """Warnings encountered while processing document. Results will still be returned
        if there are warnings, but they may not be fully accurate."""
    statistics: Optional["TextDocumentStatistics"] = None
    """If `show_stats=True` was specified in the request this
        field will contain information about the document payload."""
    is_error: Literal[False] = False
    """Boolean check for error item when iterating over list of
        results. Always False for an instance of a AnalyzeSentimentResult."""
    kind: Literal["SentimentAnalysis"] = "SentimentAnalysis"
    """The text analysis kind - "SentimentAnalysis"."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", None)
        self.sentiment = kwargs.get("sentiment", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.confidence_scores = kwargs.get("confidence_scores", None)
        self.sentences = kwargs.get("sentences", None)
        self.is_error: Literal[False] = False
        self.kind: Literal["SentimentAnalysis"] = "SentimentAnalysis"

    def __repr__(self) -> str:
        return (
            f"AnalyzeSentimentResult(id={self.id}, sentiment={self.sentiment}, warnings={repr(self.warnings)}, "
            f"statistics={repr(self.statistics)}, confidence_scores={repr(self.confidence_scores)}, "
            f"sentences={repr(self.sentences)}, "
            f"is_error={self.is_error}, kind={self.kind})"[:1024]
        )


class TextDocumentStatistics(DictMixin):
    """TextDocumentStatistics contains information about
    the document payload.
    """

    character_count: int
    """Number of text elements recognized in
        the document."""
    transaction_count: int
    """Number of transactions for the document."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return f"TextDocumentStatistics(character_count={self.character_count}, " \
               f"transaction_count={self.transaction_count})"[:1024]


class DocumentError(DictMixin):
    """DocumentError is an error object which represents an error on
    the individual document.
    """

    id: str  # pylint: disable=redefined-builtin
    """Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document."""
    error: TextAnalyticsError
    """The document error."""
    is_error: Literal[True] = True
    """Boolean check for error item when iterating over list of
        results. Always True for an instance of a DocumentError."""
    kind: Literal["DocumentError"] = "DocumentError"
    """Error kind - "DocumentError"."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", None)
        self.error = kwargs.get("error", None)
        self.is_error: Literal[True] = True
        self.kind: Literal["DocumentError"] = "DocumentError"

    def __getattr__(self, attr: str) -> Any:
        result_set = set()
        result_set.update(
            RecognizeEntitiesResult().keys()  # type: ignore[operator]
            + RecognizePiiEntitiesResult().keys()
            + DetectLanguageResult().keys()
            + RecognizeLinkedEntitiesResult().keys()
            + AnalyzeSentimentResult().keys()
            + ExtractKeyPhrasesResult().keys()
            + AnalyzeHealthcareEntitiesResult().keys()
            + RecognizeCustomEntitiesResult().keys()
            + ClassifyDocumentResult().keys()
            + ExtractiveSummaryResult().keys()
            + AbstractiveSummaryResult().keys()
        )
        result_attrs = result_set.difference(DocumentError().keys())
        if attr in result_attrs:
            raise AttributeError(
                "'DocumentError' object has no attribute '{}'. The service was unable to process this document:\n"
                "Document Id: {}\nError: {} - {}\n".format(
                    attr, self.id, self.error.code, self.error.message
                )
            )
        raise AttributeError(
            f"'DocumentError' object has no attribute '{attr}'"
        )

    @classmethod
    def _from_generated(cls, doc_err):
        return cls(
            id=doc_err.id,
            error=TextAnalyticsError._from_generated(  # pylint: disable=protected-access
                doc_err.error
            ),
        )

    def __repr__(self) -> str:
        return f"DocumentError(id={self.id}, error={repr(self.error)}, " \
               f"is_error={self.is_error}, kind={self.kind})"[:1024]


class DetectLanguageInput(LanguageInput):
    """The input document to be analyzed for detecting language.

    :keyword str id: Required. Unique, non-empty document identifier.
    :keyword str text: Required. The input text to process.
    :keyword Optional[str] country_hint: A country hint to help better detect
     the language of the text. Accepts two letter country codes
     specified by ISO 3166-1 alpha-2. Defaults to "US". Pass
     in the string "none" to not use a country_hint.
    """

    id: str  # pylint: disable=redefined-builtin
    """Required. Unique, non-empty document identifier."""
    text: str
    """Required. The input text to process."""
    country_hint: Optional[str] = None
    """A country hint to help better detect
        the language of the text. Accepts two letter country codes
        specified by ISO 3166-1 alpha-2. Defaults to "US". Pass
        in the string "none" to not use a country_hint."""

    def __init__(
        self,
        *,
        id: str,  # pylint: disable=redefined-builtin
        text: str,
        country_hint: Optional[str] = None,
        **kwargs: Any  # pylint: disable=unused-argument
    ) -> None:
        super().__init__(id=id, text=text, country_hint=country_hint)
        self.id = id
        self.text = text
        self.country_hint = country_hint

    def __repr__(self) -> str:
        return f"DetectLanguageInput(id={self.id}, text={self.text}, country_hint={self.country_hint})"[:1024]


class LinkedEntity(DictMixin):
    """LinkedEntity contains a link to the well-known recognized
    entity in text. The link comes from a data source like Wikipedia
    or Bing. It additionally includes all of the matches of this
    entity found in the document.

    .. versionadded:: v3.1
        The *bing_entity_search_api_id* property.
    """

    name: str
    """Entity Linking formal name."""
    matches: List["LinkedEntityMatch"]
    """List of instances this entity appears in the text."""
    language: str
    """Language used in the data source."""
    url: str
    """URL to the entity's page from the data source."""
    data_source: str
    """Data source used to extract entity linking,
        such as Wiki/Bing etc."""
    data_source_entity_id: Optional[str] = None
    """Unique identifier of the recognized entity from the data
        source."""
    bing_entity_search_api_id: Optional[str] = None
    """Bing Entity Search unique identifier of the recognized entity.
        Use in conjunction with the Bing Entity Search SDK to fetch additional relevant information."""

    def __init__(self, **kwargs: Any) -> None:
        self.name = kwargs.get("name", None)
        self.matches = kwargs.get("matches", None)
        self.language = kwargs.get("language", None)
        self.data_source_entity_id = kwargs.get("data_source_entity_id", None)
        self.url = kwargs.get("url", None)
        self.data_source = kwargs.get("data_source", None)
        self.bing_entity_search_api_id = kwargs.get("bing_entity_search_api_id", None)

    @classmethod
    def _from_generated(cls, entity):
        bing_entity_search_api_id = (
            entity.bing_id if hasattr(entity, "bing_id") else None
        )
        return cls(
            name=entity.name,
            matches=[
                LinkedEntityMatch._from_generated(e)  # pylint: disable=protected-access
                for e in entity.matches
            ],
            language=entity.language,
            data_source_entity_id=entity.id,
            url=entity.url,
            data_source=entity.data_source,
            bing_entity_search_api_id=bing_entity_search_api_id,
        )

    def __repr__(self) -> str:
        return (
            f"LinkedEntity(name={self.name}, matches={repr(self.matches)}, language={self.language}, "
            f"data_source_entity_id={self.data_source_entity_id}, url={self.url}, "
            f"data_source={self.data_source}, bing_entity_search_api_id={self.bing_entity_search_api_id})"[:1024]
        )


class LinkedEntityMatch(DictMixin):
    """A match for the linked entity found in text. Provides
    the confidence score of the prediction and where the entity
    was found in the text.

    .. versionadded:: v3.1
        The *offset* and *length* properties.
    """

    confidence_score: float
    """If a well-known item is recognized, a
        decimal number denoting the confidence level between 0 and 1 will be
        returned."""
    text: str
    """Entity text as appears in the request."""
    length: int
    """The linked entity match text length.  This value depends on the value of the
        `string_index_type` parameter set in the original request, which is UnicodeCodePoints by default."""
    offset: int
    """The linked entity match text offset from the start of the document.
        The value depends on the value of the `string_index_type` parameter
        set in the original request, which is UnicodeCodePoints by default."""

    def __init__(self, **kwargs: Any) -> None:
        self.confidence_score = kwargs.get("confidence_score", None)
        self.text = kwargs.get("text", None)
        self.length = kwargs.get("length", None)
        self.offset = kwargs.get("offset", None)

    @classmethod
    def _from_generated(cls, match):
        offset = match.offset
        length = match.length
        if isinstance(match, _v3_0_models.Match):
            # we do not return offset for v3.0 since
            # the correct encoding was not introduced for v3.0
            offset = None
            length = None
        return cls(
            confidence_score=match.confidence_score,
            text=match.text,
            length=length,
            offset=offset,
        )

    def __repr__(self) -> str:
        return f"LinkedEntityMatch(confidence_score={self.confidence_score}, text={self.text}, " \
               f"length={self.length}, offset={self.offset})"[:1024]


class TextDocumentInput(DictMixin, MultiLanguageInput):
    """The input document to be analyzed by the service.

    :keyword str id: Required. Unique, non-empty document identifier.
    :keyword str text: Required. The input text to process.
    :keyword str language: This is the 2 letter ISO 639-1 representation
     of a language. For example, use "en" for English; "es" for Spanish etc.
     If not set, uses "en" for English as default.
    """

    id: str  # pylint: disable=redefined-builtin
    """Required. Unique, non-empty document identifier."""
    text: str
    """Required. The input text to process."""
    language: Optional[str] = None
    """This is the 2 letter ISO 639-1 representation
     of a language. For example, use "en" for English; "es" for Spanish etc.
     If not set, uses "en" for English as default."""

    def __init__(
        self,
        *,
        id: str,  # pylint: disable=redefined-builtin
        text: str,
        language: Optional[str] = None,
        **kwargs: Any  # pylint: disable=unused-argument
    ) -> None:
        super().__init__(id=id, text=text, language=language)
        self.id = id
        self.text = text
        self.language = language

    def __repr__(self) -> str:
        return f"TextDocumentInput(id={self.id}, text={self.text}, language={self.language})"[:1024]


class TextDocumentBatchStatistics(DictMixin):
    """TextDocumentBatchStatistics contains information about the
    request payload. Note: This object is not returned
    in the response and needs to be retrieved by a response hook.
    """

    document_count: int
    """Number of documents submitted in the request"""
    valid_document_count: int
    """Number of valid documents. This
        excludes empty, over-size limit or non-supported languages documents."""
    erroneous_document_count: int
    """Number of invalid documents.
        This includes empty, over-size limit or non-supported languages documents."""
    transaction_count: int
    """Number of transactions for the request."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"TextDocumentBatchStatistics(document_count={self.document_count}, "
            f"valid_document_count={self.valid_document_count}, "
            f"erroneous_document_count={self.erroneous_document_count}, "
            f"transaction_count={self.transaction_count})"[:1024]
        )


class SentenceSentiment(DictMixin):
    """SentenceSentiment contains the predicted sentiment and
    confidence scores for each individual sentence in the document.

    .. versionadded:: v3.1
        The *offset*, *length*, and *mined_opinions* properties.
    """

    text: str
    """The sentence text."""
    sentiment: str
    """The predicted Sentiment for the sentence.
        Possible values include 'positive', 'neutral', 'negative'"""
    confidence_scores: "SentimentConfidenceScores"
    """The sentiment confidence score between 0
        and 1 for the sentence for all labels."""
    length: int
    """The sentence text length.  This value depends on the value of the
        `string_index_type` parameter set in the original request, which is UnicodeCodePoints
        by default."""
    offset: int
    """The sentence text offset from the start of the document.
        The value depends on the value of the `string_index_type` parameter
        set in the original request, which is UnicodeCodePoints by default."""
    mined_opinions: Optional[List["MinedOpinion"]] = None
    """The list of opinions mined from this sentence.
        For example in the sentence "The food is good, but the service is bad", we would
        mine the two opinions "food is good" and "service is bad". Only returned
        if `show_opinion_mining` is set to True in the call to `analyze_sentiment` and
        api version is v3.1 and up."""

    def __init__(self, **kwargs: Any) -> None:
        self.text = kwargs.get("text", None)
        self.sentiment = kwargs.get("sentiment", None)
        self.confidence_scores = kwargs.get("confidence_scores", None)
        self.length = kwargs.get("length", None)
        self.offset = kwargs.get("offset", None)
        self.mined_opinions = kwargs.get("mined_opinions", None)

    @classmethod
    def _from_generated(cls, sentence, results, sentiment):
        offset = sentence.offset
        length = sentence.length
        if isinstance(sentence, _v3_0_models.SentenceSentiment):
            # we do not return offset for v3.0 since
            # the correct encoding was not introduced for v3.0
            offset = None
            length = None
        if hasattr(sentence, "targets"):
            mined_opinions = (
                [
                    MinedOpinion._from_generated(  # pylint: disable=protected-access
                        target, results, sentiment
                    )
                    for target in sentence.targets
                ]
                if sentence.targets
                else []
            )
        else:
            mined_opinions = None
        return cls(
            text=sentence.text,
            sentiment=sentence.sentiment,
            confidence_scores=SentimentConfidenceScores._from_generated(  # pylint: disable=protected-access
                sentence.confidence_scores
            ),
            length=length,
            offset=offset,
            mined_opinions=mined_opinions,
        )

    def __repr__(self) -> str:
        return (
            f"SentenceSentiment(text={self.text}, sentiment={self.sentiment}, "
            f"confidence_scores={repr(self.confidence_scores)}, length={self.length}, "
            f"offset={self.offset}, mined_opinions={repr(self.mined_opinions)})"[:1024]
        )


class MinedOpinion(DictMixin):
    """A mined opinion object represents an opinion we've extracted from a sentence.
    It consists of both a target that these opinions are about, and the assessments
    representing the opinion.
    """

    target: "TargetSentiment"
    """The target of an opinion about a product/service."""
    assessments: List["AssessmentSentiment"]
    """The assessments representing the opinion of the target."""

    def __init__(self, **kwargs: Any) -> None:
        self.target = kwargs.get("target", None)
        self.assessments = kwargs.get("assessments", None)

    @staticmethod
    def _get_assessments(
        relations, results, sentiment
    ):  # pylint: disable=unused-argument
        if not relations:
            return []
        assessment_relations = [
            r.ref for r in relations if r.relation_type == "assessment"
        ]
        assessments = []
        for assessment_relation in assessment_relations:
            numbers = _get_indices(assessment_relation)
            sentence_index = numbers[1]
            assessment_index = numbers[2]
            assessments.append(
                sentiment.sentences[sentence_index].assessments[assessment_index]
            )
        return assessments

    @classmethod
    def _from_generated(cls, target, results, sentiment):
        return cls(
            target=TargetSentiment._from_generated(  # pylint: disable=protected-access
                target
            ),
            assessments=[
                AssessmentSentiment._from_generated(  # pylint: disable=protected-access
                    assessment
                )
                for assessment in cls._get_assessments(
                    target.relations, results, sentiment
                )
            ],
        )

    def __repr__(self) -> str:
        return f"MinedOpinion(target={repr(self.target)}, assessments={repr(self.assessments)})"[:1024]


class TargetSentiment(DictMixin):
    """TargetSentiment contains the predicted sentiment,
    confidence scores and other information about a key component of a product/service.
    For example in "The food at Hotel Foo is good", "food" is an key component of
    "Hotel Foo".
    """

    text: str
    """The text value of the target."""
    sentiment: str
    """The predicted Sentiment for the target. Possible values
        include 'positive', 'mixed', and 'negative'."""
    confidence_scores: "SentimentConfidenceScores"
    """The sentiment confidence score between 0
        and 1 for the target for 'positive' and 'negative' labels. It's score
        for 'neutral' will always be 0"""
    length: int
    """The target text length.  This value depends on the value of the
        `string_index_type` parameter set in the original request, which is UnicodeCodePoints
        by default."""
    offset: int
    """The target text offset from the start of the document.
        The value depends on the value of the `string_index_type` parameter
        set in the original request, which is UnicodeCodePoints by default."""

    def __init__(self, **kwargs: Any) -> None:
        self.text = kwargs.get("text", None)
        self.sentiment = kwargs.get("sentiment", None)
        self.confidence_scores = kwargs.get("confidence_scores", None)
        self.length = kwargs.get("length", None)
        self.offset = kwargs.get("offset", None)

    @classmethod
    def _from_generated(cls, target):
        return cls(
            text=target.text,
            sentiment=target.sentiment,
            confidence_scores=SentimentConfidenceScores._from_generated(  # pylint: disable=protected-access
                target.confidence_scores
            ),
            length=target.length,
            offset=target.offset,
        )

    def __repr__(self) -> str:
        return (
            f"TargetSentiment(text={self.text}, sentiment={self.sentiment}, "
            f"confidence_scores={repr(self.confidence_scores)}, "
            f"length={self.length}, offset={self.offset})"[:1024]
        )


class AssessmentSentiment(DictMixin):
    """AssessmentSentiment contains the predicted sentiment,
    confidence scores and other information about an assessment given about
    a particular target.  For example, in the sentence "The food is good", the assessment
    of the target 'food' is 'good'.
    """

    text: str
    """The assessment text."""
    sentiment: str
    """The predicted Sentiment for the assessment. Possible values
        include 'positive', 'mixed', and 'negative'."""
    confidence_scores: "SentimentConfidenceScores"
    """The sentiment confidence score between 0
        and 1 for the assessment for 'positive' and 'negative' labels. It's score
        for 'neutral' will always be 0"""
    length: int
    """The assessment text length.  This value depends on the value of the
        `string_index_type` parameter set in the original request, which is UnicodeCodePoints
        by default."""
    offset: int
    """The assessment text offset from the start of the document.
        The value depends on the value of the `string_index_type` parameter
        set in the original request, which is UnicodeCodePoints by default."""
    is_negated: bool
    """Whether the value of the assessment is negated. For example, in
        "The food is not good", the assessment "good" is negated."""

    def __init__(self, **kwargs: Any) -> None:
        self.text = kwargs.get("text", None)
        self.sentiment = kwargs.get("sentiment", None)
        self.confidence_scores = kwargs.get("confidence_scores", None)
        self.length = kwargs.get("length", None)
        self.offset = kwargs.get("offset", None)
        self.is_negated = kwargs.get("is_negated", None)

    @classmethod
    def _from_generated(cls, assessment):
        return cls(
            text=assessment.text,
            sentiment=assessment.sentiment,
            confidence_scores=SentimentConfidenceScores._from_generated(  # pylint: disable=protected-access
                assessment.confidence_scores
            ),
            length=assessment.length,
            offset=assessment.offset,
            is_negated=assessment.is_negated,
        )

    def __repr__(self) -> str:
        return (
            f"AssessmentSentiment(text={self.text}, sentiment={self.sentiment}, "
            f"confidence_scores={repr(self.confidence_scores)}, length={self.length}, "
            f"offset={self.offset}, is_negated={self.is_negated})"[:1024]
        )


class SentimentConfidenceScores(DictMixin):
    """The confidence scores (Softmax scores) between 0 and 1.
    Higher values indicate higher confidence.
    """

    positive: float
    """Positive score."""
    neutral: float
    """Neutral score."""
    negative: float
    """Negative score."""

    def __init__(self, **kwargs: Any) -> None:
        self.positive = kwargs.get("positive", 0.0)
        self.neutral = kwargs.get("neutral", 0.0)
        self.negative = kwargs.get("negative", 0.0)

    @classmethod
    def _from_generated(cls, score):
        return cls(
            positive=score.positive,
            neutral=score.neutral if hasattr(score, "neutral") else 0.0,
            negative=score.negative,
        )

    def __repr__(self) -> str:
        return f"SentimentConfidenceScores(positive={self.positive}, " \
               f"neutral={self.neutral}, negative={self.negative})"[:1024]


class _AnalyzeActionsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of action that was applied to the documents"""

    RECOGNIZE_ENTITIES = "recognize_entities"  #: Entities Recognition action.
    RECOGNIZE_PII_ENTITIES = (
        "recognize_pii_entities"  #: PII Entities Recognition action.
    )
    EXTRACT_KEY_PHRASES = "extract_key_phrases"  #: Key Phrase Extraction action.
    RECOGNIZE_LINKED_ENTITIES = (
        "recognize_linked_entities"  #: Linked Entities Recognition action.
    )
    ANALYZE_SENTIMENT = "analyze_sentiment"  #: Sentiment Analysis action.
    RECOGNIZE_CUSTOM_ENTITIES = "recognize_custom_entities"
    SINGLE_LABEL_CLASSIFY = "single_label_classify"
    MULTI_LABEL_CLASSIFY = "multi_label_classify"
    ANALYZE_HEALTHCARE_ENTITIES = "analyze_healthcare_entities"
    EXTRACT_SUMMARY = "extract_summary"
    ABSTRACT_SUMMARY = "abstract_summary"


class ActionPointerKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """v3.1 only"""
    RECOGNIZE_ENTITIES = "entityRecognitionTasks"
    RECOGNIZE_PII_ENTITIES = "piiEntityRecognitionTasks"
    EXTRACT_KEY_PHRASES = "keyPhraseExtractionTasks"
    RECOGNIZE_LINKED_ENTITIES = "entityLinkingTasks"
    ANALYZE_SENTIMENT = "sentimentAnalysisTasks"


class RecognizeEntitiesAction(DictMixin):
    """RecognizeEntitiesAction encapsulates the parameters for starting a long-running Entities Recognition operation.

    If you just want to recognize entities in a list of documents, and not perform multiple
    long running actions on the input of documents, call method `recognize_entities` instead
    of interfacing with this model.

    :keyword Optional[str] model_version: The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning
    :keyword Optional[str] string_index_type: Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets
    :keyword Optional[bool] disable_service_logs: If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai.
    """

    model_version: Optional[str] = None
    """The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning"""
    string_index_type: Optional[str] = None
    """Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets"""
    disable_service_logs: Optional[bool] = None
    """If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai."""

    def __init__(
        self,
        *,
        model_version: Optional[str] = None,
        string_index_type: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        self.model_version = model_version
        self.string_index_type: str = string_index_type if string_index_type is not None else STRING_INDEX_TYPE_DEFAULT
        self.disable_service_logs = disable_service_logs

    def __repr__(self) -> str:
        return f"RecognizeEntitiesAction(model_version={self.model_version}, " \
               f"string_index_type={self.string_index_type}, " \
               f"disable_service_logs={self.disable_service_logs})"[:1024]

    def _to_generated(self, api_version, task_id):
        if is_language_api(api_version):
            return _v2023_04_01_models.EntitiesLROTask(
                task_name=task_id,
                parameters=_v2023_04_01_models.EntitiesTaskParameters(
                    model_version=self.model_version,
                    string_index_type=string_index_type_compatibility(self.string_index_type),
                    logging_opt_out=self.disable_service_logs,
                )
            )

        return _v3_1_models.EntitiesTask(
            parameters=_v3_1_models.EntitiesTaskParameters(
                model_version=self.model_version,
                string_index_type=self.string_index_type,
                logging_opt_out=self.disable_service_logs,
            ),
            task_name=task_id
        )


class AnalyzeSentimentAction(DictMixin):
    """AnalyzeSentimentAction encapsulates the parameters for starting a long-running
    Sentiment Analysis operation.

    If you just want to analyze sentiment in a list of documents, and not perform multiple
    long running actions on the input of documents, call method `analyze_sentiment` instead
    of interfacing with this model.

    :keyword Optional[str] model_version: The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning
    :keyword Optional[bool] show_opinion_mining: Whether to mine the opinions of a sentence and conduct more
        granular analysis around the aspects of a product or service (also known as
        aspect-based sentiment analysis). If set to true, the returned
        :class:`~azure.ai.textanalytics.SentenceSentiment` objects
        will have property `mined_opinions` containing the result of this analysis.
    :keyword Optional[str] string_index_type: Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets
    :keyword Optional[bool] disable_service_logs: If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai.
    """

    show_opinion_mining: Optional[bool] = None
    """Whether to mine the opinions of a sentence and conduct more
        granular analysis around the aspects of a product or service (also known as
        aspect-based sentiment analysis). If set to true, the returned
        :class:`~azure.ai.textanalytics.SentenceSentiment` objects
        will have property `mined_opinions` containing the result of this analysis."""
    model_version: Optional[str] = None
    """The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning."""
    string_index_type: Optional[str] = None
    """Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets"""
    disable_service_logs: Optional[bool] = None
    """If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai."""

    def __init__(
        self,
        *,
        show_opinion_mining: Optional[bool] = None,
        model_version: Optional[str] = None,
        string_index_type: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        self.model_version = model_version
        self.show_opinion_mining = show_opinion_mining
        self.string_index_type: str = string_index_type if string_index_type is not None else STRING_INDEX_TYPE_DEFAULT
        self.disable_service_logs = disable_service_logs

    def __repr__(self) -> str:
        return (
            f"AnalyzeSentimentAction(model_version={self.model_version}, "
            f"show_opinion_mining={self.show_opinion_mining}, "
            f"string_index_type={self.string_index_type}, "
            f"disable_service_logs={self.disable_service_logs}"[:1024]
        )

    def _to_generated(self, api_version, task_id):
        if is_language_api(api_version):
            return _v2023_04_01_models.SentimentAnalysisLROTask(
                task_name=task_id,
                parameters=_v2023_04_01_models.SentimentAnalysisTaskParameters(
                    model_version=self.model_version,
                    opinion_mining=self.show_opinion_mining,
                    string_index_type=string_index_type_compatibility(self.string_index_type),
                    logging_opt_out=self.disable_service_logs,
                )
            )
        return _v3_1_models.SentimentAnalysisTask(
            parameters=_v3_1_models.SentimentAnalysisTaskParameters(
                model_version=self.model_version,
                opinion_mining=self.show_opinion_mining,
                string_index_type=self.string_index_type,
                logging_opt_out=self.disable_service_logs,
            ),
            task_name=task_id
        )


class RecognizePiiEntitiesAction(DictMixin):
    """RecognizePiiEntitiesAction encapsulates the parameters for starting a long-running PII
    Entities Recognition operation. See more information in the service docs: https://aka.ms/azsdk/language/pii

    If you just want to recognize pii entities in a list of documents, and not perform multiple
    long running actions on the input of documents, call method `recognize_pii_entities` instead
    of interfacing with this model.

    :keyword Optional[str] model_version: The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning
    :keyword Optional[str] domain_filter: An optional string to set the PII domain to include only a
        subset of the PII entity categories. Possible values include 'phi' or None.
    :keyword categories_filter: Instead of filtering over all PII entity categories, you can pass in a list of
        the specific PII entity categories you want to filter out. For example, if you only want to filter out
        U.S. social security numbers in a document, you can pass in
        `[PiiEntityCategory.US_SOCIAL_SECURITY_NUMBER]` for this kwarg.
    :paramtype categories_filter: Optional[list[str or ~azure.ai.textanalytics.PiiEntityCategory]]
    :keyword Optional[str] string_index_type: Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets
    :keyword Optional[bool] disable_service_logs: Defaults to true, meaning that the Language service will not log your
        input text on the service side for troubleshooting. If set to False, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai.
    """

    categories_filter: Optional[List[Union[str, PiiEntityCategory]]] = None
    """Instead of filtering over all PII entity categories, you can pass in a list of
        the specific PII entity categories you want to filter out. For example, if you only want to filter out
        U.S. social security numbers in a document, you can pass in
        `[PiiEntityCategory.US_SOCIAL_SECURITY_NUMBER]` for this kwarg."""
    domain_filter: Optional[str] = None
    """An optional string to set the PII domain to include only a
        subset of the PII entity categories. Possible values include 'phi' or None."""
    model_version: Optional[str] = None
    """The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning"""
    string_index_type: Optional[str] = None
    """Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets"""
    disable_service_logs: Optional[bool] = None
    """Defaults to true, meaning that the Language service will not log your
        input text on the service side for troubleshooting. If set to False, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai."""

    def __init__(
        self,
        *,
        categories_filter: Optional[List[Union[str, PiiEntityCategory]]] = None,
        domain_filter: Optional[str] = None,
        model_version: Optional[str] = None,
        string_index_type: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        self.model_version = model_version
        self.domain_filter = domain_filter
        self.categories_filter = categories_filter
        self.string_index_type: str = string_index_type if string_index_type is not None else STRING_INDEX_TYPE_DEFAULT
        self.disable_service_logs = disable_service_logs

    def __repr__(self) -> str:
        return (
            f"RecognizePiiEntitiesAction(model_version={self.model_version}, "
            f"domain_filter={self.domain_filter}, categories_filter={self.categories_filter}, "
            f"string_index_type={self.string_index_type}, "
            f"disable_service_logs={self.disable_service_logs}"[:1024]
        )

    def _to_generated(self, api_version, task_id):
        if is_language_api(api_version):
            return _v2023_04_01_models.PiiLROTask(
                task_name=task_id,
                parameters=_v2023_04_01_models.PiiTaskParameters(
                    model_version=self.model_version,
                    domain=self.domain_filter,
                    pii_categories=self.categories_filter,
                    string_index_type=string_index_type_compatibility(self.string_index_type),
                    logging_opt_out=self.disable_service_logs,
                )
            )

        return _v3_1_models.PiiTask(
            parameters=_v3_1_models.PiiTaskParameters(
                model_version=self.model_version,
                domain=self.domain_filter,
                pii_categories=self.categories_filter,
                string_index_type=self.string_index_type,
                logging_opt_out=self.disable_service_logs,
            ),
            task_name=task_id
        )


class ExtractKeyPhrasesAction(DictMixin):
    """ExtractKeyPhrasesAction encapsulates the parameters for starting a long-running key phrase
    extraction operation

    If you just want to extract key phrases from a list of documents, and not perform multiple
    long running actions on the input of documents, call method `extract_key_phrases` instead
    of interfacing with this model.

    :keyword Optional[str] model_version: The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning
    :keyword Optional[bool] disable_service_logs: If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai.
    """

    model_version: Optional[str] = None
    """The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning"""
    disable_service_logs: Optional[bool] = None
    """If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai."""

    def __init__(
        self,
        *,
        model_version: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        self.model_version = model_version
        self.disable_service_logs = disable_service_logs

    def __repr__(self) -> str:
        return f"ExtractKeyPhrasesAction(model_version={self.model_version}, " \
               f"disable_service_logs={self.disable_service_logs})"[:1024]

    def _to_generated(self, api_version, task_id):
        if is_language_api(api_version):
            return _v2023_04_01_models.KeyPhraseLROTask(
                task_name=task_id,
                parameters=_v2023_04_01_models.KeyPhraseTaskParameters(
                    model_version=self.model_version,
                    logging_opt_out=self.disable_service_logs,
                )
            )

        return _v3_1_models.KeyPhrasesTask(
            parameters=_v3_1_models.KeyPhrasesTaskParameters(
                model_version=self.model_version,
                logging_opt_out=self.disable_service_logs,
            ),
            task_name=task_id
        )


class RecognizeLinkedEntitiesAction(DictMixin):
    """RecognizeLinkedEntitiesAction encapsulates the parameters for starting a long-running Linked Entities
    Recognition operation.

    If you just want to recognize linked entities in a list of documents, and not perform multiple
    long running actions on the input of documents, call method `recognize_linked_entities` instead
    of interfacing with this model.

    :keyword Optional[str] model_version: The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning
    :keyword Optional[str] string_index_type: Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets
    :keyword Optional[bool] disable_service_logs: If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai.
    """

    model_version: Optional[str] = None
    """The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning"""
    string_index_type: Optional[str] = None
    """Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets"""
    disable_service_logs: Optional[bool] = None
    """If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai."""

    def __init__(
        self,
        *,
        model_version: Optional[str] = None,
        string_index_type: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        self.model_version = model_version
        self.string_index_type: str = string_index_type if string_index_type is not None else STRING_INDEX_TYPE_DEFAULT
        self.disable_service_logs = disable_service_logs

    def __repr__(self) -> str:
        return (
            f"RecognizeLinkedEntitiesAction(model_version={self.model_version}, "
            f"string_index_type={self.string_index_type}), "
            f"disable_service_logs={self.disable_service_logs}"[:1024]
        )

    def _to_generated(self, api_version, task_id):
        if is_language_api(api_version):
            return _v2023_04_01_models.EntityLinkingLROTask(
                task_name=task_id,
                parameters=_v2023_04_01_models.EntityLinkingTaskParameters(
                    model_version=self.model_version,
                    string_index_type=string_index_type_compatibility(self.string_index_type),
                    logging_opt_out=self.disable_service_logs,
                )
            )

        return _v3_1_models.EntityLinkingTask(
            parameters=_v3_1_models.EntityLinkingTaskParameters(
                model_version=self.model_version,
                string_index_type=self.string_index_type,
                logging_opt_out=self.disable_service_logs,
            ),
            task_name=task_id
        )


class RecognizeCustomEntitiesAction(DictMixin):
    """RecognizeCustomEntitiesAction encapsulates the parameters for starting a long-running custom entity
    recognition operation. For information on regional support of custom features and how to train a model to
    recognize custom entities, see https://aka.ms/azsdk/textanalytics/customentityrecognition

    :param str project_name: Required. This field indicates the project name for the model.
    :param str deployment_name: This field indicates the deployment name for the model.
    :keyword Optional[str] string_index_type: Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets
    :keyword Optional[bool] disable_service_logs: If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai.

    .. versionadded:: 2022-05-01
        The *RecognizeCustomEntitiesAction* model.
    """

    project_name: str
    """This field indicates the project name for the model."""
    deployment_name: str
    """This field indicates the deployment name for the model."""
    string_index_type: Optional[str] = None
    """Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets"""
    disable_service_logs: Optional[bool] = None
    """If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai."""

    def __init__(
        self,
        project_name: str,
        deployment_name: str,
        *,
        string_index_type: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        self.project_name = project_name
        self.deployment_name = deployment_name
        self.disable_service_logs = disable_service_logs
        self.string_index_type: str = string_index_type if string_index_type is not None else STRING_INDEX_TYPE_DEFAULT

    def __repr__(self) -> str:
        return (
            f"RecognizeCustomEntitiesAction(project_name={self.project_name}, "
            f"deployment_name={self.deployment_name}, disable_service_logs={self.disable_service_logs}, "
            f"string_index_type={self.string_index_type})"[:1024]
        )

    def _to_generated(self, api_version, task_id):  # pylint: disable=unused-argument
        return _v2023_04_01_models.CustomEntitiesLROTask(
            task_name=task_id,
            parameters=_v2023_04_01_models.CustomEntitiesTaskParameters(
                project_name=self.project_name,
                deployment_name=self.deployment_name,
                string_index_type=string_index_type_compatibility(self.string_index_type),
                logging_opt_out=self.disable_service_logs,
            )
        )


class RecognizeCustomEntitiesResult(DictMixin):
    """RecognizeCustomEntitiesResult is a result object which contains
    the custom recognized entities from a particular document.
    """

    id: str  # pylint: disable=redefined-builtin
    """Unique, non-empty document identifier that matches the
        document id that was passed in with the request. If not specified
        in the request, an id is assigned for the document."""
    entities: List[CategorizedEntity]
    """Recognized custom entities in the document."""
    warnings: List[TextAnalyticsWarning]
    """Warnings encountered while processing document."""
    statistics: Optional[TextDocumentStatistics] = None
    """If `show_stats=True` was specified in the request this
        field will contain information about the document payload."""
    is_error: Literal[False] = False
    """Boolean check for error item when iterating over list of
        results. Always False for an instance of a RecognizeCustomEntitiesResult."""
    kind: Literal["CustomEntityRecognition"] = "CustomEntityRecognition"
    """The text analysis kind - "CustomEntityRecognition"."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", None)
        self.entities = kwargs.get("entities", None)
        self.warnings = kwargs.get("warnings", [])
        self.statistics = kwargs.get("statistics", None)
        self.is_error: Literal[False] = False
        self.kind: Literal["CustomEntityRecognition"] = "CustomEntityRecognition"

    def __repr__(self) -> str:
        return (
            f"RecognizeCustomEntitiesResult(id={self.id}, entities={repr(self.entities)}, "
            f"warnings={repr(self.warnings)}, statistics={repr(self.statistics)}, "
            f"is_error={self.is_error}, kind={self.kind})"[:1024]
        )

    @classmethod
    def _from_generated(cls, result):
        return cls(
            id=result.id,
            entities=[
                CategorizedEntity._from_generated(e)  # pylint: disable=protected-access
                for e in result.entities
            ],
            warnings=[
                TextAnalyticsWarning._from_generated(  # pylint: disable=protected-access
                    w
                )
                for w in result.warnings
            ],
            statistics=TextDocumentStatistics._from_generated(  # pylint: disable=protected-access
                result.statistics
            ),
        )


class MultiLabelClassifyAction(DictMixin):
    """MultiLabelClassifyAction encapsulates the parameters for starting a long-running custom multi label
    classification operation. For information on regional support of custom features and how to train a model to
    classify your documents, see https://aka.ms/azsdk/textanalytics/customfunctionalities

    :param str project_name: Required. This field indicates the project name for the model.
    :param str deployment_name: Required. This field indicates the deployment name for the model.
    :keyword Optional[bool] disable_service_logs: If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai.

    .. versionadded:: 2022-05-01
        The *MultiLabelClassifyAction* model.
    """

    project_name: str
    """This field indicates the project name for the model."""
    deployment_name: str
    """This field indicates the deployment name for the model."""
    disable_service_logs: Optional[bool] = None
    """If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai."""

    def __init__(
        self,
        project_name: str,
        deployment_name: str,
        *,
        disable_service_logs: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        self.project_name = project_name
        self.deployment_name = deployment_name
        self.disable_service_logs = disable_service_logs

    def __repr__(self) -> str:
        return (
            f"MultiLabelClassifyAction(project_name={self.project_name}, deployment_name={self.deployment_name}, "
            f"disable_service_logs={self.disable_service_logs})"[:1024]
        )

    def _to_generated(self, api_version, task_id):  # pylint: disable=unused-argument
        return _v2023_04_01_models.CustomMultiLabelClassificationLROTask(
            task_name=task_id,
            parameters=_v2023_04_01_models.CustomMultiLabelClassificationTaskParameters(
                project_name=self.project_name,
                deployment_name=self.deployment_name,
                logging_opt_out=self.disable_service_logs,
            )
        )


class ClassifyDocumentResult(DictMixin):
    """ClassifyDocumentResult is a result object which contains
    the classifications for a particular document.
    """

    id: str  # pylint: disable=redefined-builtin
    """Unique, non-empty document identifier."""
    classifications: List["ClassificationCategory"]
    """Recognized classification results in the document."""
    warnings: List[TextAnalyticsWarning]
    """Warnings encountered while processing document."""
    statistics: Optional[TextDocumentStatistics] = None
    """If `show_stats=True` was specified in the request this
        field will contain information about the document payload."""
    is_error: Literal[False] = False
    """Boolean check for error item when iterating over list of
        results. Always False for an instance of a ClassifyDocumentResult."""
    kind: Literal["CustomDocumentClassification"] = "CustomDocumentClassification"
    """The text analysis kind - "CustomDocumentClassification"."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get('id', None)
        self.classifications = kwargs.get('classifications', None)
        self.warnings = kwargs.get('warnings', [])
        self.statistics = kwargs.get('statistics', None)
        self.is_error: Literal[False] = False
        self.kind: Literal["CustomDocumentClassification"] = "CustomDocumentClassification"

    def __repr__(self) -> str:
        return (
            f"ClassifyDocumentResult(id={self.id}, classifications={repr(self.classifications)}, "
            f"warnings={repr(self.warnings)}, statistics={repr(self.statistics)}, "
            f"is_error={self.is_error}, kind={self.kind})"[:1024]
        )

    @classmethod
    def _from_generated(cls, result):
        return cls(
            id=result.id,
            classifications=[
                ClassificationCategory._from_generated(e)  # pylint: disable=protected-access
                for e in result.class_property
            ],
            warnings=[
                TextAnalyticsWarning._from_generated(  # pylint: disable=protected-access
                    w
                )
                for w in result.warnings
            ],
            statistics=TextDocumentStatistics._from_generated(  # pylint: disable=protected-access
                result.statistics
            ),
        )


class SingleLabelClassifyAction(DictMixin):
    """SingleLabelClassifyAction encapsulates the parameters for starting a long-running custom single label
    classification operation. For information on regional support of custom features and how to train a model to
    classify your documents, see https://aka.ms/azsdk/textanalytics/customfunctionalities

    :param str project_name: Required. This field indicates the project name for the model.
    :param str deployment_name: Required. This field indicates the deployment name for the model.
    :keyword Optional[bool] disable_service_logs: If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai.

    .. versionadded:: 2022-05-01
        The *SingleLabelClassifyAction* model.
    """

    project_name: str
    """This field indicates the project name for the model."""
    deployment_name: str
    """This field indicates the deployment name for the model."""
    disable_service_logs: Optional[bool] = None
    """If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai."""

    def __init__(
        self,
        project_name: str,
        deployment_name: str,
        *,
        disable_service_logs: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        self.project_name = project_name
        self.deployment_name = deployment_name
        self.disable_service_logs = disable_service_logs

    def __repr__(self) -> str:
        return (
            f"SingleLabelClassifyAction(project_name={self.project_name}, deployment_name={self.deployment_name}, "
            f"disable_service_logs={self.disable_service_logs})"[:1024]
        )

    def _to_generated(self, api_version, task_id):  # pylint: disable=unused-argument
        return _v2023_04_01_models.CustomSingleLabelClassificationLROTask(
            task_name=task_id,
            parameters=_v2023_04_01_models.CustomSingleLabelClassificationTaskParameters(
                project_name=self.project_name,
                deployment_name=self.deployment_name,
                logging_opt_out=self.disable_service_logs,
            )
        )


class ClassificationCategory(DictMixin):
    """ClassificationCategory represents a classification of the input document.
    """

    category: str
    """Classification category for the document."""
    confidence_score: float
    """Confidence score between 0 and 1 of the recognized classification."""

    def __init__(self, **kwargs: Any) -> None:
        self.category = kwargs.get('category', None)
        self.confidence_score = kwargs.get('confidence_score', None)

    def __repr__(self) -> str:
        return f"ClassificationCategory(category={self.category}, " \
               f"confidence_score={self.confidence_score})"[:1024]

    @classmethod
    def _from_generated(cls, result):
        return cls(
            category=result.category,
            confidence_score=result.confidence_score
        )


class AnalyzeHealthcareEntitiesAction(DictMixin):
    """AnalyzeHealthcareEntitiesAction encapsulates the parameters for starting a long-running
    healthcare entities analysis operation.

    If you just want to analyze healthcare entities in a list of documents, and not perform multiple
    long running actions on the input of documents, call method `begin_analyze_healthcare_entities` instead
    of interfacing with this model.

    :keyword Optional[str] model_version: The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning
    :keyword Optional[str] string_index_type: Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets
    :keyword Optional[bool] disable_service_logs: If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai.

    .. versionadded:: 2022-05-01
        The *AnalyzeHealthcareEntitiesAction* model.
    """

    model_version: Optional[str] = None
    """The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning"""
    string_index_type: Optional[str] = None
    """Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets"""
    disable_service_logs: Optional[bool] = None
    """If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai."""

    def __init__(
        self,
        *,
        model_version: Optional[str] = None,
        string_index_type: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        self.model_version = model_version
        self.string_index_type: str = string_index_type if string_index_type is not None else STRING_INDEX_TYPE_DEFAULT
        self.disable_service_logs = disable_service_logs

    def __repr__(self) -> str:
        return (
            f"AnalyzeHealthcareEntitiesAction(model_version={self.model_version}, "
            f"string_index_type={self.string_index_type}, "
            f"disable_service_logs={self.disable_service_logs})"[:1024]
        )

    def _to_generated(self, api_version, task_id):  # pylint: disable=unused-argument
        return _v2023_04_01_models.HealthcareLROTask(
            task_name=task_id,
            parameters=_v2023_04_01_models.HealthcareTaskParameters(
                model_version=self.model_version,
                string_index_type=string_index_type_compatibility(self.string_index_type),
                logging_opt_out=self.disable_service_logs,
            )
        )


class ExtractiveSummaryAction(DictMixin):
    """ExtractiveSummaryAction encapsulates the parameters for starting a long-running Extractive Text
    Summarization operation. For a conceptual discussion of extractive summarization, see the service documentation:
    https://learn.microsoft.com/azure/cognitive-services/language-service/summarization/overview

    :keyword Optional[str] model_version: The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning
    :keyword Optional[str] string_index_type: Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets
    :keyword Optional[bool] disable_service_logs: If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai.
    :keyword Optional[int] max_sentence_count: Maximum number of sentences to return. Defaults to 3.
    :keyword Optional[str] order_by:  Possible values include: "Offset", "Rank". Default value: "Offset".

    .. versionadded:: 2023-04-01
        The *ExtractiveSummaryAction* model.
    """

    model_version: Optional[str] = None
    """The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning"""
    string_index_type: Optional[str] = None
    """Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets"""
    disable_service_logs: Optional[bool] = None
    """If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai."""
    max_sentence_count: Optional[int] = None
    """Number of sentences to return. Defaults to 3."""
    order_by: Optional[Literal["Rank", "Offset"]] = None
    """Possible values include "Offset", "Rank". Default value is "Offset"."""

    def __init__(
        self,
        *,
        model_version: Optional[str] = None,
        string_index_type: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        max_sentence_count: Optional[int] = None,
        order_by: Optional[Literal["Rank", "Offset"]] = None,
        **kwargs: Any
    ) -> None:
        self.model_version = model_version
        self.string_index_type: str = string_index_type if string_index_type is not None else STRING_INDEX_TYPE_DEFAULT
        self.disable_service_logs = disable_service_logs
        self.max_sentence_count = max_sentence_count
        self.order_by = order_by

    def __repr__(self) -> str:
        return (
            f"ExtractiveSummaryAction(model_version={self.model_version}, "
            f"string_index_type={self.string_index_type}, disable_service_logs={self.disable_service_logs}, "
            f"max_sentence_count={self.max_sentence_count}, order_by={self.order_by})"[:1024]
        )

    def _to_generated(self, api_version, task_id):  # pylint: disable=unused-argument
        return _v2023_04_01_models.ExtractiveSummarizationLROTask(  # pylint: disable=no-member
            task_name=task_id,
            parameters=_v2023_04_01_models.ExtractiveSummarizationTaskParameters(  # pylint: disable=no-member
                model_version=self.model_version,
                string_index_type=string_index_type_compatibility(self.string_index_type),
                logging_opt_out=self.disable_service_logs,
                sentence_count=self.max_sentence_count,
                sort_by=self.order_by,
            )
        )


class ExtractiveSummaryResult(DictMixin):
    """ExtractiveSummaryResult is a result object which contains
    the extractive text summarization from a particular document.
    """

    id: str  # pylint: disable=redefined-builtin
    """Unique, non-empty document identifier."""
    sentences: List["SummarySentence"]
    """A ranked list of sentences representing the extracted summary."""
    warnings: List[TextAnalyticsWarning]
    """Warnings encountered while processing document."""
    statistics: Optional[TextDocumentStatistics] = None
    """If `show_stats=True` was specified in the request this
        field will contain information about the document payload."""
    is_error: Literal[False] = False
    """Boolean check for error item when iterating over list of
        results. Always False for an instance of an ExtractiveSummaryResult."""
    kind: Literal["ExtractiveSummarization"] = "ExtractiveSummarization"
    """The text analysis kind - "ExtractiveSummarization"."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", None)
        self.sentences = kwargs.get("sentences", None)
        self.warnings = kwargs.get("warnings", None)
        self.statistics = kwargs.get("statistics", None)
        self.is_error: Literal[False] = False
        self.kind: Literal["ExtractiveSummarization"] = "ExtractiveSummarization"

    def __repr__(self) -> str:
        return (
            f"ExtractiveSummaryResult(id={self.id}, sentences={repr(self.sentences)}, "
            f"warnings={repr(self.warnings)}, statistics={repr(self.statistics)}, "
            f" is_error={self.is_error}, kind={self.kind})"[:1024]
        )

    @classmethod
    def _from_generated(cls, summary):
        return cls(
            id=summary.id,
            sentences=[
                SummarySentence._from_generated(  # pylint: disable=protected-access
                    sentence
                )
                for sentence in summary.sentences
            ],
            warnings=[
                TextAnalyticsWarning._from_generated(  # pylint: disable=protected-access
                    w
                )
                for w in summary.warnings
            ],
            statistics=TextDocumentStatistics._from_generated(  # pylint: disable=protected-access
                summary.statistics
            ),
        )


class SummarySentence(DictMixin):
    """Represents a single sentence from the extractive text summarization.

    .. versionadded:: 2023-04-01
        The *SummarySentence* model.
    """

    text: str
    """The extracted sentence text."""
    rank_score: float
    """A float value representing the relevance of the sentence within
        the summary. Higher values indicate higher importance."""
    offset: int
    """The sentence offset from the start of the document.
        The value depends on the value of the `string_index_type` parameter
        set in the original request, which is UnicodeCodePoint by default."""
    length: int
    """The length of the sentence. This value depends on the value of the
        `string_index_type` parameter set in the original request, which is UnicodeCodePoint
        by default."""

    def __init__(self, **kwargs: Any) -> None:
        self.text = kwargs.get("text", None)
        self.rank_score = kwargs.get("rank_score", None)
        self.offset = kwargs.get("offset", None)
        self.length = kwargs.get("length", None)

    def __repr__(self) -> str:
        return f"SummarySentence(text={self.text}, rank_score={self.rank_score}, " \
               f"offset={self.offset}, length={self.length})"[:1024]

    @classmethod
    def _from_generated(cls, sentence):
        return cls(
            text=sentence.text,
            rank_score=sentence.rank_score,
            offset=sentence.offset,
            length=sentence.length,
        )


class AbstractiveSummaryResult(DictMixin):
    """AbstractiveSummaryResult is a result object which contains
    the summary generated for a particular document.

    .. versionadded:: 2023-04-01
        The *AbstractiveSummaryResult* model.
    """

    id: str  # pylint: disable=redefined-builtin
    """Unique, non-empty document identifier. Required."""
    summaries: List["AbstractiveSummary"]
    """A list of abstractive summaries. Required."""
    warnings: List[TextAnalyticsWarning]
    """Warnings encountered while processing document. Results will still be returned
        if there are warnings, but they may not be fully accurate."""
    statistics: Optional[TextDocumentStatistics] = None
    """If `show_stats=True` was specified in the request this
        field will contain information about the document payload."""
    is_error: Literal[False] = False
    """Boolean check for error item when iterating over list of
        results. Always False for an instance of a AbstractiveSummaryResult."""
    kind: Literal["AbstractiveSummarization"] = "AbstractiveSummarization"
    """The text analysis kind - "AbstractiveSummarization"."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", None)
        self.warnings = kwargs.get("warnings", None)
        self.statistics = kwargs.get("statistics", None)
        self.summaries = kwargs.get("summaries", None)
        self.is_error: Literal[False] = False
        self.kind: Literal["AbstractiveSummarization"] = "AbstractiveSummarization"

    def __repr__(self) -> str:
        return (
            f"AbstractiveSummaryResult(id={self.id}, "
            f"warnings={repr(self.warnings)}, statistics={repr(self.statistics)}, "
            f"summaries={repr(self.summaries)}, is_error={self.is_error}, kind={self.kind})"[:1024]
        )

    @classmethod
    def _from_generated(cls, result):
        return cls(
            id=result.id,
            warnings=[
                TextAnalyticsWarning._from_generated(  # pylint: disable=protected-access
                    w
                )
                for w in result.warnings
            ],
            statistics=TextDocumentStatistics._from_generated(  # pylint: disable=protected-access
                result.statistics
            ),
            summaries=[
                AbstractiveSummary._from_generated(summary)  # pylint: disable=protected-access
                for summary in result.summaries
            ],
        )


class AbstractiveSummary(DictMixin):
    """An object representing a single summary with context for given document.

    .. versionadded:: 2023-04-01
        The *AbstractiveSummary* model.
    """

    text: str
    """The text of the summary. Required."""
    contexts: List["SummaryContext"]
    """The context list of the summary."""

    def __init__(self, **kwargs: Any) -> None:
        self.text = kwargs.get("text", None)
        self.contexts = kwargs.get("contexts", None)

    def __repr__(self) -> str:
        return f"AbstractiveSummary(text={self.text}, contexts={repr(self.contexts)})"[:1024]

    @classmethod
    def _from_generated(cls, result):
        return cls(
            text=result.text,
            contexts=[
                SummaryContext._from_generated(context)  # pylint: disable=protected-access
                for context in result.contexts
            ] if result.contexts else []
        )


class SummaryContext(DictMixin):
    """The context of the summary.

    .. versionadded:: 2023-04-01
        The *SummaryContext* model.
    """

    offset: int
    """Start position for the context. Use of different 'string_index_type' values can
     affect the offset returned. Required."""
    length: int
    """The length of the context. Use of different 'string_index_type' values can affect
     the length returned. Required."""

    def __init__(self, **kwargs: Any) -> None:
        self.offset = kwargs.get("offset", None)
        self.length = kwargs.get("length", None)

    def __repr__(self) -> str:
        return f"SummaryContext(offset={self.offset}, length={self.length})"[:1024]

    @classmethod
    def _from_generated(cls, summary):
        return cls(
            offset=summary.offset,
            length=summary.length
        )


class AbstractiveSummaryAction(DictMixin):
    """AbstractiveSummaryAction encapsulates the parameters for starting a long-running
    abstractive summarization operation. For a conceptual discussion of extractive summarization,
    see the service documentation:
    https://learn.microsoft.com/azure/cognitive-services/language-service/summarization/overview

    Abstractive summarization generates a summary for the input documents. Abstractive summarization
    is different from extractive summarization in that extractive summarization is the strategy of
    concatenating extracted sentences from the input document into a summary, while abstractive
    summarization involves paraphrasing the document using novel sentences.

    :keyword Optional[int] sentence_count: It controls the approximate number of sentences in the output summaries.
    :keyword Optional[str] model_version: The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning
    :keyword Optional[str] string_index_type: Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets
    :keyword Optional[bool] disable_service_logs: If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai.

    .. versionadded:: 2023-04-01
        The *AbstractiveSummaryAction* model.
    """

    sentence_count: Optional[int] = None
    """It controls the approximate number of sentences in the output summaries."""
    model_version: Optional[str] = None
    """The model version to use for the analysis, e.g. "latest".
        If a model version is not specified, the API will default to the latest, non-preview version.
        See here for more info: https://aka.ms/text-analytics-model-versioning"""
    string_index_type: Optional[str] = None
    """Specifies the method used to interpret string offsets.
        `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
        you can also pass in `Utf16CodeUnit` or `TextElement_v8`. For additional information
        see https://aka.ms/text-analytics-offsets"""
    disable_service_logs: Optional[bool] = None
    """If set to true, you opt-out of having your text input
        logged on the service side for troubleshooting. By default, the Language service logs your
        input text for 48 hours, solely to allow for troubleshooting issues in providing you with
        the service's natural language processing functions. Setting this parameter to true,
        disables input logging and may limit our ability to remediate issues that occur. Please see
        Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
        additional details, and Microsoft Responsible AI principles at
        https://www.microsoft.com/ai/responsible-ai."""

    def __init__(
        self,
        *,
        sentence_count: Optional[int] = None,
        model_version: Optional[str] = None,
        string_index_type: Optional[str] = None,
        disable_service_logs: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        self.sentence_count = sentence_count
        self.model_version = model_version
        self.string_index_type: str = string_index_type if string_index_type is not None else STRING_INDEX_TYPE_DEFAULT
        self.disable_service_logs = disable_service_logs

    def __repr__(self) -> str:
        return (
            f"AbstractiveSummaryAction(model_version={self.model_version}, "
            f"string_index_type={self.string_index_type}, disable_service_logs={self.disable_service_logs}, "
            f"sentence_count={self.sentence_count})"[:1024]
        )

    def _to_generated(self, api_version, task_id):  # pylint: disable=unused-argument
        return _v2023_04_01_models.AbstractiveSummarizationLROTask(
            task_name=task_id,
            parameters=_v2023_04_01_models.AbstractiveSummarizationTaskParameters(
                model_version=self.model_version,
                string_index_type=string_index_type_compatibility(self.string_index_type),
                logging_opt_out=self.disable_service_logs,
                sentence_count=self.sentence_count,
            )
        )

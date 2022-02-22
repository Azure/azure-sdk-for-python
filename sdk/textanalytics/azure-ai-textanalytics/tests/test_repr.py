# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import datetime
from azure.ai.textanalytics import _models
from azure.ai.textanalytics._generated.v3_1 import models as _generated_models

# All features return a tuple of the object and the repr of the obejct

# Adding in assert for each pytest fixture so it's easier to narrow down where the problem is

"""general"""
@pytest.fixture
def text_document_statistics():
    model = _models.TextDocumentStatistics(
        character_count=14,
        transaction_count=18
    )
    model_repr = "TextDocumentStatistics(character_count=14, transaction_count=18)"
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def text_analytics_warning():
    model = _models.TextAnalyticsWarning(
        code="LongWordsInDocument",
        message="The document contains very long words (longer than 64 characters). These words will be truncated and may result in unreliable model predictions."
    )
    model_repr = (
        "TextAnalyticsWarning(code=LongWordsInDocument, message=The document contains very long words (longer than 64 characters). "
        "These words will be truncated and may result in unreliable model predictions.)"
    )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def text_analytics_error():
    model = _models.TextAnalyticsError(
        code="invalidRequest",
        message="The request is invalid",
        target="request",
    )
    model_repr = "TextAnalyticsError(code=invalidRequest, message=The request is invalid, target=request)"
    assert repr(model) == model_repr
    return model, model_repr


"""detect language models"""

@pytest.fixture
def detected_language():
    model = _models.DetectedLanguage(
        name="English",
        iso6391_name="en",
        confidence_score=1.0
    )
    model_repr = "DetectedLanguage(name=English, iso6391_name=en, confidence_score=1.0)"
    assert repr(model) == model_repr
    return model, model_repr

"""recognize entities models"""
@pytest.fixture
def categorized_entity():
    model = _models.CategorizedEntity(
        text="Bill Gates",
        category="Person",
        subcategory="Age",
        length=10,
        offset=0,
        confidence_score=0.899
    )
    model_repr = (
        "CategorizedEntity(text=Bill Gates, category=Person, subcategory=Age, "
        "length=10, offset=0, confidence_score=0.899)"
    )
    assert repr(model) == model_repr
    return model, model_repr

"""recognize PII entities models"""
@pytest.fixture
def pii_entity():
    model = _models.PiiEntity(
        text="859-98-0987",
        category="SSN",
        subcategory=None,
        length=11,
        offset=0,
        confidence_score=0.899
    )
    model_repr = "PiiEntity(text=859-98-0987, category=SSN, subcategory=None, length=11, offset=0, confidence_score=0.899)"
    assert repr(model) == model_repr
    return model, model_repr

"""recognize linked entity models"""
@pytest.fixture
def linked_entity_match():
    model = _models.LinkedEntityMatch(
        confidence_score=0.999,
        text="Bill Gates",
        offset=0,
        length=10
    )
    model_repr = "LinkedEntityMatch(confidence_score=0.999, text=Bill Gates, length=10, offset=0)"
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def linked_entity(linked_entity_match):
    model = _models.LinkedEntity(
        name="Bill Gates",
        matches=[linked_entity_match[0], linked_entity_match[0]],
        language="English",
        data_source_entity_id="Bill Gates",
        url="https://en.wikipedia.org/wiki/Bill_Gates",
        data_source="wikipedia",
        bing_entity_search_api_id="12345678"
    )
    model_repr = (
        "LinkedEntity(name=Bill Gates, matches=[{}, {}], "\
        "language=English, data_source_entity_id=Bill Gates, "\
        "url=https://en.wikipedia.org/wiki/Bill_Gates, data_source=wikipedia, bing_entity_search_api_id=12345678)".format(
            linked_entity_match[1], linked_entity_match[1]
        )
    )
    assert repr(model) == model_repr
    return model, model_repr

"""analyze sentiment models"""

@pytest.fixture
def sentiment_confidence_scores():
    model = _models.SentimentConfidenceScores(
        positive=0.99,
        neutral=0.05,
        negative=0.02
    )
    model_repr = "SentimentConfidenceScores(positive=0.99, neutral=0.05, negative=0.02)"
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def target_assessment_confidence_score():
    model = _models.SentimentConfidenceScores(
        positive=0.5,
        negative=0.5
    )
    model_repr = "SentimentConfidenceScores(positive=0.5, neutral=0.0, negative=0.5)"
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def target_sentiment(target_assessment_confidence_score):
    model = _models.TargetSentiment(
        text="aspect",
        sentiment="positive",
        confidence_scores=target_assessment_confidence_score[0],
        length=6,
        offset=10,
    )
    model_repr = "TargetSentiment(text=aspect, sentiment=positive, confidence_scores={}, length=6, offset=10)".format(
        target_assessment_confidence_score[1]
    )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def assessment_sentiment(target_assessment_confidence_score):
    model = _models.AssessmentSentiment(
        text="opinion",
        sentiment="positive",
        confidence_scores=target_assessment_confidence_score[0],
        length=7,
        offset=3,
        is_negated=False
    )
    model_repr = "AssessmentSentiment(text=opinion, sentiment=positive, confidence_scores={}, length=7, offset=3, is_negated=False)".format(
        target_assessment_confidence_score[1]
    )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def mined_opinion(target_sentiment, assessment_sentiment):
    model = _models.MinedOpinion(
        target=target_sentiment[0],
        assessments=[assessment_sentiment[0]]
    )
    model_repr = f"MinedOpinion(target={target_sentiment[1]}, assessments=[{assessment_sentiment[1]}])"
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def sentence_sentiment(sentiment_confidence_scores, mined_opinion):
    model = _models.SentenceSentiment(
        text="This is a sentence.",
        sentiment="neutral",
        confidence_scores=sentiment_confidence_scores[0],
        length=19,
        offset=0,
        mined_opinions=[mined_opinion[0]]
    )
    model_repr = (
        "SentenceSentiment(text=This is a sentence., sentiment=neutral, confidence_scores={}, "\
        "length=19, offset=0, mined_opinions=[{}])".format(
            sentiment_confidence_scores[1], mined_opinion[1]
        )
    )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def recognize_pii_entities_result(pii_entity, text_analytics_warning, text_document_statistics):
    model = _models.RecognizePiiEntitiesResult(
        id="1",
        entities=[pii_entity[0]],
        redacted_text="***********",
        warnings=[text_analytics_warning[0]],
        statistics=text_document_statistics[0],
        is_error=False
    )
    model_repr = "RecognizePiiEntitiesResult(id=1, entities=[{}], redacted_text=***********, warnings=[{}], " \
    "statistics={}, is_error=False)".format(
        pii_entity[1], text_analytics_warning[1], text_document_statistics[1]
    )

    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def recognize_entities_result(categorized_entity, text_analytics_warning, text_document_statistics):
    model = _models.RecognizeEntitiesResult(
        id="1",
        entities=[categorized_entity[0]],
        warnings=[text_analytics_warning[0]],
        statistics=text_document_statistics[0],
        is_error=False
    )
    model_repr = "RecognizeEntitiesResult(id=1, entities=[{}], warnings=[{}], statistics={}, is_error=False)".format(
        categorized_entity[1], text_analytics_warning[1], text_document_statistics[1]
    )

    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def extract_key_phrases_result(text_analytics_warning, text_document_statistics):
    model = _models.ExtractKeyPhrasesResult(
        id="1",
        key_phrases=["dog", "cat", "bird"],
        warnings=[text_analytics_warning[0]],
        statistics=text_document_statistics[0],
        is_error=False
    )
    model_repr = "ExtractKeyPhrasesResult(id=1, key_phrases=['dog', 'cat', 'bird'], warnings=[{}], statistics={}, is_error=False)".format(
        text_analytics_warning[1], text_document_statistics[1]
    )

    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def data_source():
    model = _models.HealthcareEntityDataSource(
        entity_id="BONJOUR",
        name="UMLS",
    )
    model_repr = "HealthcareEntityDataSource(entity_id=BONJOUR, name=UMLS)"

    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def healthcare_entity_assertion():
    model = _models.HealthcareEntityAssertion(
        conditionality="conditionality",
        certainty="certainty",
        association="association",
    )
    model_repr = "HealthcareEntityAssertion(conditionality=conditionality, certainty=certainty, association=association)"

    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def healthcare_entity(data_source, healthcare_entity_assertion):
    model = _models.HealthcareEntity(
        text="Bonjour",
        normalized_text="Bonjour",
        category="MyCategory",
        subcategory="MySubcategory",
        assertion=healthcare_entity_assertion[0],
        length=7,
        offset=12,
        confidence_score=0.95,
        data_sources=[data_source[0]],
    )
    model_repr = (
        "HealthcareEntity(text=Bonjour, normalized_text=Bonjour, category=MyCategory, subcategory=MySubcategory, assertion={}, length=7, offset=12, "\
        "confidence_score=0.95, data_sources=[{}])".format(healthcare_entity_assertion[1], data_source[1])
    )

    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def healthcare_relation_role(healthcare_entity):
    model = _models.HealthcareRelationRole(
        name="ROLE",
        entity=healthcare_entity[0]
    )

    model_repr = f"HealthcareRelationRole(name=ROLE, entity={healthcare_entity[1]})"

    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def healthcare_relation(healthcare_relation_role):
    model = _models.HealthcareRelation(
        relation_type="DOSAGE",
        roles=[healthcare_relation_role[0]]
    )

    model_repr = f"HealthcareRelation(relation_type=DOSAGE, roles=[{healthcare_relation_role[1]}])"

    assert repr(model) == model_repr
    return model, model_repr

class TestRepr():
    def test_text_document_input(self):
        model = _models.TextDocumentInput(
            id="1",
            text="hello world",
            language="en"
        )
        model_repr = "TextDocumentInput(id=1, text=hello world, language=en)"

        assert repr(model) == model_repr

    def test_detect_language_input(self):
        model = _models.DetectLanguageInput(
            id="1",
            text="hello world",
            country_hint="US"
        )
        model_repr = "DetectLanguageInput(id=1, text=hello world, country_hint=US)"

        assert repr(model) == model_repr

    def test_document_error(self, text_analytics_error):
        model = _models.DocumentError(
            id="1",
            error=text_analytics_error[0],
            is_error=True
        )
        model_repr = f"DocumentError(id=1, error={text_analytics_error[1]}, is_error=True)"

        assert repr(model) == model_repr

    def test_text_document_batch_statistics(self):
        model = _models.TextDocumentBatchStatistics(
            document_count=1,
            valid_document_count=2,
            erroneous_document_count=3,
            transaction_count=4
        )
        model_repr = (
            "TextDocumentBatchStatistics(document_count=1, valid_document_count=2, "
            "erroneous_document_count=3, transaction_count=4)"
        )

        assert repr(model) == model_repr

    def test_detect_language_result(self, detected_language, text_analytics_warning, text_document_statistics):
        model = _models.DetectLanguageResult(
            id="1",
            primary_language=detected_language[0],
            warnings=[text_analytics_warning[0]],
            statistics=text_document_statistics[0],
            is_error=False
        )
        model_repr = "DetectLanguageResult(id=1, primary_language={}, warnings=[{}], statistics={}, is_error=False)".format(
            detected_language[1], text_analytics_warning[1], text_document_statistics[1]
        )

        assert repr(model) == model_repr

    def test_recognized_linked_entities_result(self, linked_entity, text_analytics_warning, text_document_statistics):
        model = _models.RecognizeLinkedEntitiesResult(
            id="1",
            entities=[linked_entity[0]],
            warnings=[text_analytics_warning[0]],
            statistics=text_document_statistics[0],
            is_error=False
        )
        model_repr = "RecognizeLinkedEntitiesResult(id=1, entities=[{}], warnings=[{}], statistics={}, is_error=False)".format(
            linked_entity[1], text_analytics_warning[1], text_document_statistics[1]
        )

        assert repr(model) == model_repr

    def test_analyze_sentiment_result(
        self, text_analytics_warning, text_document_statistics, sentiment_confidence_scores, sentence_sentiment
    ):
        model = _models.AnalyzeSentimentResult(
            id="1",
            sentiment="positive",
            warnings=[text_analytics_warning[0]],
            statistics=text_document_statistics[0],
            confidence_scores=sentiment_confidence_scores[0],
            sentences=[sentence_sentiment[0]],
            is_error=False
        )
        model_repr = (
            "AnalyzeSentimentResult(id=1, sentiment=positive, warnings=[{}], statistics={}, confidence_scores={}, "\
            "sentences=[{}], is_error=False)".format(
                text_analytics_warning[1], text_document_statistics[1], sentiment_confidence_scores[1], sentence_sentiment[1]
            )
        )

        assert repr(model) == model_repr

    def test_inner_error_takes_precedence(self):
        generated_innererror = _generated_models.InnerError(
            code="UnsupportedLanguageCode",
            message="Supplied language not supported. Pass in one of: de,en,es,fr,it,ja,ko,nl,pt-PT,zh-Hans,zh-Hant",

        )
        generated_error = _generated_models.TextAnalyticsError(
            code="InvalidArgument",
            message="Invalid Language Code.",
            innererror=generated_innererror
        )

        error = _models.TextAnalyticsError._from_generated(generated_error)
        assert error.code == "UnsupportedLanguageCode"
        assert error.message == "Supplied language not supported. Pass in one of: de,en,es,fr,it,ja,ko,nl,pt-PT,zh-Hans,zh-Hant"

    def test_analyze_healthcare_entities_result_item(
        self, healthcare_entity, healthcare_relation, text_analytics_warning, text_document_statistics
    ):
        model = _models.AnalyzeHealthcareEntitiesResult(
            id=1,
            entities=[healthcare_entity[0]],
            entity_relations=[healthcare_relation[0]],
            warnings=[text_analytics_warning[0]],
            statistics=text_document_statistics[0],
            is_error=False
        )

        model_repr = (
            "AnalyzeHealthcareEntitiesResult(id=1, entities=[{}], entity_relations=[{}], warnings=[{}], statistics={}, is_error=False)".format(
                healthcare_entity[1], healthcare_relation[1], text_analytics_warning[1], text_document_statistics[1]
            )
        )

        assert repr(model) == model_repr[:1024]
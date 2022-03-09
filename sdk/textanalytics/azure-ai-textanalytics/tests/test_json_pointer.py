# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.ai.textanalytics._models import (
    AnalyzeSentimentResult,
    TargetSentiment,
    AssessmentSentiment,
    SentenceSentiment,
    _get_indices,
)

from azure.ai.textanalytics._response_handlers import sentiment_result

from azure.ai.textanalytics._generated.v3_1 import models as _generated_models


@pytest.fixture
def generated_target_assessment_confidence_scores():
    return _generated_models.TargetConfidenceScoreLabel(
        positive=1.0,
        neutral=0.0,
        negative=0.0,
    )

@pytest.fixture
def generated_sentiment_confidence_score():
    return _generated_models.SentimentConfidenceScorePerLabel(
        positive=1.0,
        neutral=0.0,
        negative=0.0,
    )

@pytest.fixture
def generated_target_relation():
    return _generated_models.TargetRelation(
        relation_type="assessment",
        ref="#/documents/0/sentences/1/assessments/0"
    )

@pytest.fixture
def generated_target(generated_target_assessment_confidence_scores, generated_target_relation):
    return _generated_models.SentenceTarget(
        text="aspect",
        sentiment="positive",
        confidence_scores=generated_target_assessment_confidence_scores,
        offset=0,
        length=6,
        relations=[generated_target_relation],
    )

@pytest.fixture
def generated_assessment(generated_target_assessment_confidence_scores):
    return _generated_models.SentenceAssessment(
        text="good",
        sentiment="positive",
        confidence_scores=generated_target_assessment_confidence_scores,
        offset=0,
        length=4,
        is_negated=False,
    )

def generated_sentence_sentiment(generated_sentiment_confidence_score, index, targets=[], assessments=[]):
    return _generated_models.SentenceSentiment(
        text="not relevant",
        sentiment="positive",
        confidence_scores=generated_sentiment_confidence_score,
        offset=0,
        length=12,
        targets=targets,
        assessments=assessments,
    )

@pytest.fixture
def generated_document_sentiment(generated_target, generated_assessment, generated_sentiment_confidence_score):
    target_sentence = generated_sentence_sentiment(generated_sentiment_confidence_score, index=0, targets=[generated_target])
    assessment_sentence = generated_sentence_sentiment(generated_sentiment_confidence_score, index=1, assessments=[generated_assessment])

    return _generated_models.DocumentSentiment(
        id=1,
        sentiment="positive",
        confidence_scores=generated_sentiment_confidence_score,
        sentences=[target_sentence, assessment_sentence],
        warnings=[],
    )

@pytest.fixture
def generated_sentiment_response(generated_document_sentiment):
    return _generated_models.SentimentResponse(
        documents=[generated_document_sentiment],
        errors=[],
        model_version="0000-00-00",
    )


class TestJsonPointer():

    def test_json_pointer_parsing(self):
        assert [1, 0, 15] == _get_indices("#/documents/1/sentences/0/assessments/15")

    def test_opinion_different_sentence_target(self, generated_sentiment_response):
        # the first sentence has the target, and the second sentence has the assessment
        # the desired behavior is the first wrapped sentence object has a target, and it's assessment
        # is in the second sentence.
        # the second sentence will have no mined opinions, since we define that as a target and assessment duo
        wrapped_sentiment = sentiment_result("not relevant", generated_sentiment_response, {})[0]
        assert wrapped_sentiment.sentences[0].mined_opinions[0].assessments[0].text == "good"
        assert not wrapped_sentiment.sentences[1].mined_opinions

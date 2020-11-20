# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.ai.textanalytics._models import (
    AnalyzeSentimentResult,
    AspectSentiment,
    OpinionSentiment,
    SentenceSentiment,
    _get_indices,
)

from azure.ai.textanalytics._response_handlers import sentiment_result

from azure.ai.textanalytics._generated.v3_1_preview_2 import models as _generated_models


@pytest.fixture
def generated_aspect_opinion_confidence_scores():
    return _generated_models.AspectConfidenceScoreLabel(
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
def generated_aspect_relation():
    return _generated_models.AspectRelation(
        relation_type="opinion",
        ref="#/documents/0/sentences/1/opinions/0"
    )

@pytest.fixture
def generated_aspect(generated_aspect_opinion_confidence_scores, generated_aspect_relation):
    return _generated_models.SentenceAspect(
        text="aspect",
        sentiment="positive",
        confidence_scores=generated_aspect_opinion_confidence_scores,
        offset=0,
        length=6,
        relations=[generated_aspect_relation],
    )

@pytest.fixture
def generated_opinion(generated_aspect_opinion_confidence_scores):
    return _generated_models.SentenceOpinion(
        text="good",
        sentiment="positive",
        confidence_scores=generated_aspect_opinion_confidence_scores,
        offset=0,
        length=4,
        is_negated=False,
    )

def generated_sentence_sentiment(generated_sentiment_confidence_score, index, aspects=[], opinions=[]):
    return _generated_models.SentenceSentiment(
        text="not relevant",
        sentiment="positive",
        confidence_scores=generated_sentiment_confidence_score,
        offset=0,
        length=12,
        aspects=aspects,
        opinions=opinions,
    )

@pytest.fixture
def generated_document_sentiment(generated_aspect, generated_opinion, generated_sentiment_confidence_score):
    aspect_sentence = generated_sentence_sentiment(generated_sentiment_confidence_score, index=0, aspects=[generated_aspect])
    opinion_sentence = generated_sentence_sentiment(generated_sentiment_confidence_score, index=1, opinions=[generated_opinion])

    return _generated_models.DocumentSentiment(
        id=1,
        sentiment="positive",
        confidence_scores=generated_sentiment_confidence_score,
        sentences=[aspect_sentence, opinion_sentence],
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
        assert [1, 0, 15] == _get_indices("#/documents/1/sentences/0/opinions/15")

    def test_opinion_different_sentence_aspect(self, generated_sentiment_response):
        # the first sentence has the aspect, and the second sentence has the opinion
        # the desired behavior is the first wrapped sentence object has an aspect, and it's opinion
        # is in the second sentence.
        # the second sentence will have no mined opinions, since we define that as an aspect and opinion duo
        wrapped_sentiment = sentiment_result("not relevant", generated_sentiment_response, {})[0]
        assert wrapped_sentiment.sentences[0].mined_opinions[0].opinions[0].text == "good"
        assert not wrapped_sentiment.sentences[1].mined_opinions

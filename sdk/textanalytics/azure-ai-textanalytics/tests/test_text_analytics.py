# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential
from azure.ai.textanalytics import _models
from testcase import GlobalTextAnalyticsAccountPreparer
from testcase import TextAnalyticsTest as TestAnalyticsTestCase


class TextAnalyticsTest(TestAnalyticsTestCase):

    @GlobalTextAnalyticsAccountPreparer()
    def test_detect_language(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        response = text_analytics.detect_languages(
            inputs=[{
                'id': 1,
                'text': 'I had a wonderful experience! The rooms were wonderful and the staff was helpful.'
            }]
        )

        self.assertEqual(response[0].primary_language.name, "English")

    def test_repr(self):
        detected_language = _models.DetectedLanguage(name="English", iso6391_name="en", score=1.0)

        named_entity = _models.NamedEntity(text="Bill Gates", type="Person", subtype="Age", offset=0, length=8,
                                           score=0.899)

        text_document_statistics = _models.TextDocumentStatistics(character_count=14, transaction_count=18)

        recognize_entities_result = _models.RecognizeEntitiesResult(
            id="1",
            entities=[named_entity],
            statistics=text_document_statistics,
            is_error=False
        )

        recognize_pii_entities_result = _models.RecognizePiiEntitiesResult(
            id="1",
            entities=[named_entity],
            statistics=text_document_statistics,
            is_error=False
        )

        detect_language_result = _models.DetectLanguageResult(
            id="1",
            detected_languages=[detected_language],
            primary_language=detected_language,
            statistics=text_document_statistics,
            is_error=False
        )

        inner_error = _models.InnerError(
            code="invalidParameterValue",
            message="The parameter is invalid",
            details={"parameter": "invalid"},
            target="parameter",
            inner_error=_models.InnerError(
                code="invalidParameterValue2",
                message="The parameter is invalid2",
                details={"parameter2": "invalid2"},
                target="parameter2",
                inner_error=None
            )
        )

        text_analytics_error = _models.TextAnalyticsError(
            code="invalidRequest",
            message="The request is invalid",
            target="request",
            inner_error=inner_error,
            details=[_models.TextAnalyticsError(
                code="invalidRequest2",
                message="The request is invalid2",
                target="request2",
                inner_error=None,
                details=None
            )]
        )

        extract_key_phrases_result = \
            _models.ExtractKeyPhrasesResult(
                id="1", key_phrases=["dog", "cat", "bird"], statistics=text_document_statistics, is_error=False
            )

        linked_entity_match = _models.LinkedEntityMatch(score=0.999, text="Bill Gates", offset=0, length=8)

        linked_entity = _models.LinkedEntity(
            name="Bill Gates",
            matches=[linked_entity_match, linked_entity_match],
            language="English",
            id="Bill Gates",
            url="https://en.wikipedia.org/wiki/Bill_Gates",
            data_source="wikipedia"
        )
        recognize_linked_entities_result = \
            _models.RecognizeLinkedEntitiesResult(
                id="1", entities=[linked_entity], statistics=text_document_statistics, is_error=False
            )

        sentiment_confidence_score_per_label = \
            _models.SentimentConfidenceScorePerLabel(positive=0.99, neutral=0.05, negative=0.02)

        sentence_sentiment = _models.SentenceSentiment(
            sentiment="neutral",
            sentence_scores=sentiment_confidence_score_per_label,
            offset=0,
            length=10,
            warnings=["sentence was too short to find sentiment"]
        )

        analyze_sentiment_result = _models.AnalyzeSentimentResult(
            id="1",
            sentiment="positive",
            statistics=text_document_statistics,
            document_scores=sentiment_confidence_score_per_label,
            sentences=[sentence_sentiment],
            is_error=False
        )

        document_error = _models.DocumentError(id="1", error=text_analytics_error, is_error=True)

        detect_language_input = _models.DetectLanguageInput(id="1", text="hello world", country_hint="US")

        text_document_input = _models.TextDocumentInput(id="1", text="hello world", language="en")

        text_document_batch_statistics = _models.TextDocumentBatchStatistics(
            document_count=1,
            valid_document_count=2,
            erroneous_document_count=3,
            transaction_count=4
        )

        self.assertEqual("DetectedLanguage(name=English, iso6391_name=en, score=1.0)", repr(detected_language))
        self.assertEqual("NamedEntity(text=Bill Gates, type=Person, subtype=Age, offset=0, length=8, score=0.899)",
                         repr(named_entity))
        self.assertEqual("TextDocumentStatistics(character_count=14, transaction_count=18)",
                         repr(text_document_statistics))
        self.assertEqual("RecognizeEntitiesResult(id=1, entities=[NamedEntity(text=Bill Gates, type=Person, "
                         "subtype=Age, offset=0, length=8, score=0.899)], "
                         "statistics=TextDocumentStatistics(character_count=14, transaction_count=18), "
                         "is_error=False)", repr(recognize_entities_result))
        self.assertEqual("RecognizePiiEntitiesResult(id=1, entities=[NamedEntity(text=Bill Gates, type=Person, "
                         "subtype=Age, offset=0, length=8, score=0.899)], "
                         "statistics=TextDocumentStatistics(character_count=14, transaction_count=18), "
                         "is_error=False)", repr(recognize_pii_entities_result))
        self.assertEqual("DetectLanguageResult(id=1, detected_languages=[DetectedLanguage(name=English, "
                         "iso6391_name=en, score=1.0)], primary_language=DetectedLanguage(name=English, "
                         "iso6391_name=en, score=1.0), statistics=TextDocumentStatistics(character_count=14, "
                         "transaction_count=18), is_error=False)", repr(detect_language_result))
        self.assertEqual("InnerError(code=invalidParameterValue, message=The parameter is invalid, "
                         "details={'parameter': 'invalid'}, target=parameter, inner_error=InnerError(code="
                         "invalidParameterValue2, message=The parameter is invalid2, "
                         "details={'parameter2': 'invalid2'}, target=parameter2, inner_error=None))", repr(inner_error))
        self.assertEqual("TextAnalyticsError(code=invalidRequest, message=The request is invalid, target=request, "
                         "inner_error=InnerError(code=invalidParameterValue, message=The parameter is invalid, "
                         "details={'parameter': 'invalid'}, target=parameter, inner_error=InnerError(code="
                         "invalidParameterValue2, message=The parameter is invalid2, "
                         "details={'parameter2': 'invalid2'}, target=parameter2, inner_error=None)), details=["
                         "TextAnalyticsError(code=invalidRequest2, message=The request is invalid2, target=request2, "
                         "inner_error=None, details=None)])", repr(text_analytics_error))
        self.assertEqual("ExtractKeyPhrasesResult(id=1, key_phrases=['dog', 'cat', 'bird'], statistics="
                         "TextDocumentStatistics(character_count=14, transaction_count=18), is_error=False)",
                         repr(extract_key_phrases_result))
        self.assertEqual("LinkedEntityMatch(score=0.999, text=Bill Gates, offset=0, length=8)", repr(linked_entity_match))
        self.assertEqual("LinkedEntity(name=Bill Gates, matches=[LinkedEntityMatch(score=0.999, text=Bill Gates, "
                         "offset=0, length=8), LinkedEntityMatch(score=0.999, text=Bill Gates, offset=0, length=8)], "
                         "language=English, id=Bill Gates, url=https://en.wikipedia.org/wiki/Bill_Gates, data_source="
                         "wikipedia)", repr(linked_entity))
        self.assertEqual("RecognizeLinkedEntitiesResult(id=1, entities=[LinkedEntity(name=Bill Gates, "
                         "matches=[LinkedEntityMatch(score=0.999, text=Bill Gates, offset=0, length=8), "
                         "LinkedEntityMatch(score=0.999, text=Bill Gates, offset=0, length=8)], language=English, "
                         "id=Bill Gates, url=https://en.wikipedia.org/wiki/Bill_Gates, data_source=wikipedia)], "
                         "statistics=TextDocumentStatistics(character_count=14, "
                         "transaction_count=18), is_error=False)", repr(recognize_linked_entities_result))
        self.assertEqual("SentimentConfidenceScorePerLabel(positive=0.99, neutral=0.05, negative=0.02)",
                         repr(sentiment_confidence_score_per_label))
        self.assertEqual("SentenceSentiment(sentiment=neutral, sentence_scores=SentimentConfidenceScorePerLabel("
                         "positive=0.99, neutral=0.05, negative=0.02), offset=0, length=10, warnings="
                         "['sentence was too short to find sentiment'])", repr(sentence_sentiment))
        self.assertEqual("AnalyzeSentimentResult(id=1, sentiment=positive, statistics=TextDocumentStatistics("
                         "character_count=14, transaction_count=18), document_scores=SentimentConfidenceScorePerLabel"
                         "(positive=0.99, neutral=0.05, negative=0.02), sentences=[SentenceSentiment(sentiment=neutral, "
                         "sentence_scores=SentimentConfidenceScorePerLabel(positive=0.99, neutral=0.05, negative=0.02), "
                         "offset=0, length=10, warnings=['sentence was too short to find sentiment'])], is_error=False)",
                         repr(analyze_sentiment_result))
        self.assertEqual("DocumentError(id=1, error=TextAnalyticsError(code=invalidRequest, "
                         "message=The request is invalid, target=request, "
                         "inner_error=InnerError(code=invalidParameterValue, message=The parameter is invalid, "
                         "details={'parameter': 'invalid'}, target=parameter, inner_error=InnerError(code="
                         "invalidParameterValue2, message=The parameter is invalid2, "
                         "details={'parameter2': 'invalid2'}, target=parameter2, inner_error=None)), details=["
                         "TextAnalyticsError(code=invalidRequest2, message=The request is invalid2, target=request2, "
                         "inner_error=None, details=None)]), is_error=True)", repr(document_error))
        self.assertEqual("DetectLanguageInput(id=1, text=hello world, country_hint=US)", repr(detect_language_input))
        self.assertEqual("TextDocumentInput(id=1, text=hello world, language=en)", repr(text_document_input))
        self.assertEqual("TextDocumentBatchStatistics(document_count=1, valid_document_count=2, "
                         "erroneous_document_count=3, transaction_count=4)", repr(text_document_batch_statistics))

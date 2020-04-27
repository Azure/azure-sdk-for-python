# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.textanalytics import _models
from testcase import GlobalTextAnalyticsAccountPreparer
from testcase import TextAnalyticsTest as TestAnalyticsTestCase


class TextAnalyticsTest(TestAnalyticsTestCase):

    @GlobalTextAnalyticsAccountPreparer()
    def test_detect_language(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, AzureKeyCredential(text_analytics_account_key))

        response = text_analytics.detect_language(
            documents=[{
                'id': 1,
                'text': 'I had a wonderful experience! The rooms were wonderful and the staff was helpful.'
            }]
        )

        self.assertEqual(response[0].primary_language.name, "English")

    def test_repr(self):
        detected_language = _models.DetectedLanguage(name="English", iso6391_name="en", confidence_score=1.0)

        categorized_entity = _models.CategorizedEntity(text="Bill Gates", category="Person", subcategory="Age",
                                                       grapheme_offset=0, grapheme_length=8, confidence_score=0.899)

        text_document_statistics = _models.TextDocumentStatistics(grapheme_count=14, transaction_count=18)

        warnings = [_models.TextAnalyticsWarning(code="LongWordsInDocument", message="The document contains very long words (longer than 64 characters). These words will be truncated and may result in unreliable model predictions.")]

        recognize_entities_result = _models.RecognizeEntitiesResult(
            id="1",
            entities=[categorized_entity],
            warnings=warnings,
            statistics=text_document_statistics,
            is_error=False
        )

        detect_language_result = _models.DetectLanguageResult(
            id="1",
            primary_language=detected_language,
            warnings=warnings,
            statistics=text_document_statistics,
            is_error=False
        )

        text_analytics_error = _models.TextAnalyticsError(
            code="invalidRequest",
            message="The request is invalid",
            target="request",
        )

        extract_key_phrases_result = \
            _models.ExtractKeyPhrasesResult(
                id="1", key_phrases=["dog", "cat", "bird"], warnings=warnings, statistics=text_document_statistics, is_error=False
            )

        linked_entity_match = _models.LinkedEntityMatch(confidence_score=0.999, text="Bill Gates", grapheme_offset=0,
                                                        grapheme_length=8)

        linked_entity = _models.LinkedEntity(
            name="Bill Gates",
            matches=[linked_entity_match, linked_entity_match],
            language="English",
            data_source_entity_id="Bill Gates",
            url="https://en.wikipedia.org/wiki/Bill_Gates",
            data_source="wikipedia"
        )
        recognize_linked_entities_result = \
            _models.RecognizeLinkedEntitiesResult(
                id="1", entities=[linked_entity], warnings=warnings, statistics=text_document_statistics, is_error=False
            )

        sentiment_confidence_score_per_label = \
            _models.SentimentConfidenceScores(positive=0.99, neutral=0.05, negative=0.02)

        sentence_sentiment = _models.SentenceSentiment(
            text="This is a sentence.",
            sentiment="neutral",
            confidence_scores=sentiment_confidence_score_per_label,
            grapheme_offset=0,
            grapheme_length=10
        )

        analyze_sentiment_result = _models.AnalyzeSentimentResult(
            id="1",
            sentiment="positive",
            warnings=warnings,
            statistics=text_document_statistics,
            confidence_scores=sentiment_confidence_score_per_label,
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

        self.assertEqual("DetectedLanguage(name=English, iso6391_name=en, confidence_score=1.0)", repr(detected_language))
        self.assertEqual("CategorizedEntity(text=Bill Gates, category=Person, subcategory=Age, grapheme_offset=0, "
                         "grapheme_length=8, confidence_score=0.899)",
                         repr(categorized_entity))
        self.assertEqual("TextDocumentStatistics(grapheme_count=14, transaction_count=18)",
                         repr(text_document_statistics))
        self.assertEqual("RecognizeEntitiesResult(id=1, entities=[CategorizedEntity(text=Bill Gates, category=Person, "
                         "subcategory=Age, grapheme_offset=0, grapheme_length=8, confidence_score=0.899)], "
                         "warnings=[TextAnalyticsWarning(code=LongWordsInDocument, message=The document contains very long words (longer than 64 characters). "
                         "These words will be truncated and may result in unreliable model predictions.)], "
                         "statistics=TextDocumentStatistics(grapheme_count=14, transaction_count=18), "
                         "is_error=False)", repr(recognize_entities_result))
        self.assertEqual("DetectLanguageResult(id=1, primary_language=DetectedLanguage(name=English, "
                         "iso6391_name=en, confidence_score=1.0), "
                         "warnings=[TextAnalyticsWarning(code=LongWordsInDocument, message=The document contains very long words (longer than 64 characters). "
                         "These words will be truncated and may result in unreliable model predictions.)], "
                         "statistics=TextDocumentStatistics(grapheme_count=14, "
                         "transaction_count=18), is_error=False)", repr(detect_language_result))
        self.assertEqual("TextAnalyticsError(code=invalidRequest, message=The request is invalid, target=request)",
                         repr(text_analytics_error))
        self.assertEqual("ExtractKeyPhrasesResult(id=1, key_phrases=['dog', 'cat', 'bird'], "
                         "warnings=[TextAnalyticsWarning(code=LongWordsInDocument, message=The document contains very long words (longer than 64 characters). "
                         "These words will be truncated and may result in unreliable model predictions.)], "
                         "statistics=TextDocumentStatistics(grapheme_count=14, transaction_count=18), is_error=False)",
                         repr(extract_key_phrases_result))
        self.assertEqual("LinkedEntityMatch(confidence_score=0.999, text=Bill Gates, grapheme_offset=0, grapheme_length=8)",
                         repr(linked_entity_match))
        self.assertEqual("LinkedEntity(name=Bill Gates, matches=[LinkedEntityMatch(confidence_score=0.999, text=Bill Gates, "
                         "grapheme_offset=0, grapheme_length=8), LinkedEntityMatch(confidence_score=0.999, text=Bill Gates, "
                         "grapheme_offset=0, grapheme_length=8)], language=English, data_source_entity_id=Bill Gates, "
                         "url=https://en.wikipedia.org/wiki/Bill_Gates, data_source=wikipedia)", repr(linked_entity))
        self.assertEqual("RecognizeLinkedEntitiesResult(id=1, entities=[LinkedEntity(name=Bill Gates, "
                         "matches=[LinkedEntityMatch(confidence_score=0.999, text=Bill Gates, grapheme_offset=0, "
                         "grapheme_length=8), LinkedEntityMatch(confidence_score=0.999, text=Bill Gates, grapheme_offset=0, "
                         "grapheme_length=8)], language=English, data_source_entity_id=Bill Gates, "
                         "url=https://en.wikipedia.org/wiki/Bill_Gates, data_source=wikipedia)], "
                         "warnings=[TextAnalyticsWarning(code=LongWordsInDocument, message=The document contains very long words (longer than 64 characters). "
                         "These words will be truncated and may result in unreliable model predictions.)], "
                         "statistics=TextDocumentStatistics(grapheme_count=14, "
                         "transaction_count=18), is_error=False)", repr(recognize_linked_entities_result))
        self.assertEqual("SentimentConfidenceScores(positive=0.99, neutral=0.05, negative=0.02)",
                         repr(sentiment_confidence_score_per_label))
        self.assertEqual("SentenceSentiment(text=This is a sentence., sentiment=neutral, confidence_scores=SentimentConfidenceScores("
                         "positive=0.99, neutral=0.05, negative=0.02), grapheme_offset=0, grapheme_length=10)",
                         repr(sentence_sentiment))
        self.assertEqual("AnalyzeSentimentResult(id=1, sentiment=positive, "
                         "warnings=[TextAnalyticsWarning(code=LongWordsInDocument, message=The document contains very long words (longer than 64 characters). "
                         "These words will be truncated and may result in unreliable model predictions.)], "
                         "statistics=TextDocumentStatistics("
                         "grapheme_count=14, transaction_count=18), confidence_scores=SentimentConfidenceScores"
                         "(positive=0.99, neutral=0.05, negative=0.02), "
                         "sentences=[SentenceSentiment(text=This is a sentence., sentiment=neutral, confidence_scores="
                         "SentimentConfidenceScores(positive=0.99, neutral=0.05, negative=0.02), "
                         "grapheme_offset=0, grapheme_length=10)], "
                         "is_error=False)",
                         repr(analyze_sentiment_result))
        self.assertEqual("DocumentError(id=1, error=TextAnalyticsError(code=invalidRequest, "
                         "message=The request is invalid, target=request), is_error=True)", repr(document_error))
        self.assertEqual("DetectLanguageInput(id=1, text=hello world, country_hint=US)", repr(detect_language_input))
        self.assertEqual("TextDocumentInput(id=1, text=hello world, language=en)", repr(text_document_input))
        self.assertEqual("TextDocumentBatchStatistics(document_count=1, valid_document_count=2, "
                         "erroneous_document_count=3, transaction_count=4)", repr(text_document_batch_statistics))

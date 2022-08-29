# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import pytest
import platform
import functools
import json
from unittest import mock
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from testcase import TextAnalyticsTest, TextAnalyticsPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from devtools_testutils import recorded_by_proxy
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    TextDocumentInput,
    VERSION,
    TextAnalyticsApiVersion,
)

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)

class TestAnalyzeSentiment(TextAnalyticsTest):

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_no_single_input(self, client):
        with pytest.raises(TypeError):
            response = client.analyze_sentiment("hello world")

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_all_successful_passing_dict(self, client):
        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
                {"id": "2", "language": "en", "text": "I did not like the hotel we stayed at. It was too expensive."},
                {"id": "3", "language": "en", "text": "The restaurant had really good food. I recommend you try it."}]

        response = client.analyze_sentiment(docs, show_stats=True)
        assert response[0].sentiment == "neutral"
        assert response[1].sentiment == "negative"
        assert response[2].sentiment == "positive"

        for doc in response:
            assert doc.id is not None
            assert doc.statistics is not None
            self.validateConfidenceScores(doc.confidence_scores)
            assert doc.sentences is not None

        assert len(response[0].sentences) == 1
        assert response[0].sentences[0].text == "Microsoft was founded by Bill Gates and Paul Allen."
        assert len(response[1].sentences) == 2
        # assert response[1].sentences[0].text == "I did not like the hotel we stayed at." FIXME https://msazure.visualstudio.com/Cognitive%20Services/_workitems/edit/13848227
        assert response[1].sentences[1].text == "It was too expensive."
        assert len(response[2].sentences) == 2
        # assert response[2].sentences[0].text == "The restaurant had really good food." FIXME https://msazure.visualstudio.com/Cognitive%20Services/_workitems/edit/13848227
        assert response[2].sentences[1].text == "I recommend you try it."

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_all_successful_passing_text_document_input(self, client):
        docs = [
            TextDocumentInput(id="1", text="Microsoft was founded by Bill Gates and Paul Allen."),
            TextDocumentInput(id="2", text="I did not like the hotel we stayed at. It was too expensive."),
            TextDocumentInput(id="3", text="The restaurant had really good food. I recommend you try it."),
        ]

        response = client.analyze_sentiment(docs)
        assert response[0].sentiment == "neutral"
        assert response[1].sentiment == "negative"
        assert response[2].sentiment == "positive"

        for doc in response:
            self.validateConfidenceScores(doc.confidence_scores)
            assert doc.sentences is not None

        assert len(response[0].sentences) == 1
        assert response[0].sentences[0].text == "Microsoft was founded by Bill Gates and Paul Allen."
        assert len(response[1].sentences) == 2
        # assert response[1].sentences[0].text == "I did not like the hotel we stayed at."  FIXME https://msazure.visualstudio.com/Cognitive%20Services/_workitems/edit/13848227
        assert response[1].sentences[1].text == "It was too expensive."
        assert len(response[2].sentences) == 2
        # assert response[2].sentences[0].text == "The restaurant had really good food." FIXME https://msazure.visualstudio.com/Cognitive%20Services/_workitems/edit/13848227
        assert response[2].sentences[1].text == "I recommend you try it."

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_passing_only_string(self, client):
        docs = [
            "Microsoft was founded by Bill Gates and Paul Allen.",
            "I did not like the hotel we stayed at. It was too expensive.",
            "The restaurant had really good food. I recommend you try it.",
            ""
        ]

        response = client.analyze_sentiment(docs)
        assert response[0].sentiment == "neutral"
        assert response[1].sentiment == "negative"
        assert response[2].sentiment == "positive"
        assert response[3].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_input_with_some_errors(self, client):
        docs = [{"id": "1", "language": "en", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed at. It was too expensive."},
                {"id": "3", "language": "en", "text": "The restaurant had really good food. I recommend you try it."}]

        response = client.analyze_sentiment(docs)
        assert response[0].is_error
        assert response[1].is_error
        assert not response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_input_with_all_errors(self, client):
        docs = [{"id": "1", "language": "en", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed at. It was too expensive."},
                {"id": "3", "language": "en", "text": ""}]

        response = client.analyze_sentiment(docs)
        assert response[0].is_error
        assert response[1].is_error
        assert response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_too_many_documents(self, client):
        docs = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven"]

        with pytest.raises(HttpResponseError) as excinfo:
            client.analyze_sentiment(docs)
        assert excinfo.value.status_code == 400
        assert excinfo.value.error.code == "InvalidDocumentBatch"
        assert "Batch request contains too many records" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_document_warnings(self, client):
        # No warnings actually returned for analyze_sentiment. Will update when they add
        docs = [
            {"id": "1", "text": "This won't actually create a warning :'("},
        ]

        result = client.analyze_sentiment(docs)
        for doc in result:
            doc_warnings = doc.warnings
            assert len(doc_warnings) == 0

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_output_same_order_as_input(self, client):
        docs = [
            TextDocumentInput(id="1", text="one"),
            TextDocumentInput(id="2", text="two"),
            TextDocumentInput(id="3", text="three"),
            TextDocumentInput(id="4", text="four"),
            TextDocumentInput(id="5", text="five")
        ]

        response = client.analyze_sentiment(docs)

        for idx, doc in enumerate(response):
            assert str(idx + 1) == doc.id

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"textanalytics_test_api_key": ""})
    @recorded_by_proxy
    def test_empty_credential_class(self, client):
        with pytest.raises(ClientAuthenticationError):
            response = client.analyze_sentiment(
                ["This is written in English."]
            )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"textanalytics_test_api_key": "xxxxxxxxxxxx"})
    @recorded_by_proxy
    def test_bad_credentials(self, client):
        with pytest.raises(ClientAuthenticationError):
            response = client.analyze_sentiment(
                ["This is written in English."]
            )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_bad_document_input(self, client):
        docs = "This is the wrong type"

        with pytest.raises(TypeError):
            response = client.analyze_sentiment(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_mixing_inputs(self, client):
        docs = [
            {"id": "1", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
            TextDocumentInput(id="2", text="I did not like the hotel we stayed at. It was too expensive."),
            "You cannot mix string input with the above inputs"
        ]
        with pytest.raises(TypeError):
            response = client.analyze_sentiment(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_out_of_order_ids(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = client.analyze_sentiment(docs)
        in_order = ["56", "0", "22", "19", "1"]
        for idx, resp in enumerate(response):
            assert resp.id == in_order[idx]

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_show_stats_and_model_version(self, client):
        def callback(response):
            assert response is not None
            assert response.model_version
            assert response.raw_response is not None
            assert response.statistics.document_count == 5
            assert response.statistics.transaction_count == 4
            assert response.statistics.valid_document_count == 4
            assert response.statistics.erroneous_document_count == 1

        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = client.analyze_sentiment(
            docs,
            show_stats=True,
            model_version="latest",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_batch_size_over_limit(self, client):
        docs = ["hello world"] * 1050
        with pytest.raises(HttpResponseError):
            response = client.analyze_sentiment(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_whole_batch_language_hint(self, client):
        def callback(resp):
            language_str = "\"language\": \"fr\""
            language = resp.http_request.body.count(language_str)
            assert language == 3

        docs = [
            "This was the best day of my life.",
            "I did not like the hotel we stayed at. It was too expensive.",
            "The restaurant was not as good as I hoped."
        ]

        response = client.analyze_sentiment(docs, language="fr", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_whole_batch_dont_use_language_hint(self, client):
        def callback(resp):
            language_str = "\"language\": \"\""
            language = resp.http_request.body.count(language_str)
            assert language == 3

        docs = [
            "This was the best day of my life.",
            "I did not like the hotel we stayed at. It was too expensive.",
            "The restaurant was not as good as I hoped."
        ]

        response = client.analyze_sentiment(docs, language="", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_per_item_dont_use_language_hint(self, client):
        def callback(resp):
            language_str = "\"language\": \"\""
            language = resp.http_request.body.count(language_str)
            assert language == 2
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            assert language == 1


        docs = [{"id": "1", "language": "", "text": "I will go to the park."},
                {"id": "2", "language": "", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.analyze_sentiment(docs, raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_whole_batch_language_hint_and_obj_input(self, client):
        def callback(resp):
            language_str = "\"language\": \"de\""
            language = resp.http_request.body.count(language_str)
            assert language == 3

        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian."),
            TextDocumentInput(id="4", text="Este es un document escrito en Español."),
            TextDocumentInput(id="3", text="猫は幸せ"),
        ]

        response = client.analyze_sentiment(docs, language="de", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_whole_batch_language_hint_and_dict_input(self, client):
        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            assert language == 3

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.analyze_sentiment(docs, language="es", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_whole_batch_language_hint_and_obj_per_item_hints(self, client):
        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            assert language == 2
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            assert language == 1

        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian.", language="es"),
            TextDocumentInput(id="2", text="Este es un document escrito en Español.", language="es"),
            TextDocumentInput(id="3", text="猫は幸せ"),
        ]

        response = client.analyze_sentiment(docs, language="en", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_whole_batch_language_hint_and_dict_per_item_hints(self, client):
        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            assert language == 2
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            assert language == 1


        docs = [{"id": "1", "language": "es", "text": "I will go to the park."},
                {"id": "2", "language": "es", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.analyze_sentiment(docs, language="en", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"default_language": "es"})
    @recorded_by_proxy
    def test_client_passed_default_language_hint(self, client):
        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            assert language == 3

        def callback_2(resp):
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            assert language == 3

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.analyze_sentiment(docs, raw_response_hook=callback)
        response = client.analyze_sentiment(docs, language="en", raw_response_hook=callback_2)
        response = client.analyze_sentiment(docs, raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_invalid_language_hint_method(self, client):
        response = client.analyze_sentiment(
            ["This should fail because we're passing in an invalid language hint"], language="notalanguage"
        )
        assert response[0].error.code == 'UnsupportedLanguageCode'

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_invalid_language_hint_docs(self, client):
        response = client.analyze_sentiment(
            [{"id": "1", "language": "notalanguage", "text": "This should fail because we're passing in an invalid language hint"}]
        )
        assert response[0].error.code == 'UnsupportedLanguageCode'

    @TextAnalyticsPreparer()
    @recorded_by_proxy
    def test_rotate_subscription_key(self, textanalytics_test_endpoint, textanalytics_test_api_key):
        credential = AzureKeyCredential(textanalytics_test_api_key)
        client = TextAnalyticsClient(textanalytics_test_endpoint, credential)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.analyze_sentiment(docs)
        assert response is not None

        credential.update("xxx")  # Make authentication fail
        with pytest.raises(ClientAuthenticationError):
            response = client.analyze_sentiment(docs)

        credential.update(textanalytics_test_api_key)  # Authenticate successfully again
        response = client.analyze_sentiment(docs)
        assert response is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_user_agent(self, client):
        def callback(resp):
            assert "azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                VERSION, platform.python_version(), platform.platform()) in \
                resp.http_request.headers["User-Agent"]

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.analyze_sentiment(docs, raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_document_attribute_error_no_result_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        response = client.analyze_sentiment(docs)

        # Attributes on DocumentError
        assert response[0].is_error
        assert response[0].id == "1"
        assert response[0].error is not None

        # Result attribute not on DocumentError, custom error message
        try:
            sentiment = response[0].sentiment
        except AttributeError as custom_error:
            assert custom_error.args[0] == \
                '\'DocumentError\' object has no attribute \'sentiment\'. ' \
                'The service was unable to process this document:\nDocument Id: 1\nError: ' \
                'InvalidDocument - Document text is empty.\n'

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_document_attribute_error_nonexistent_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        response = client.analyze_sentiment(docs)

        # Attribute not found on DocumentError or result obj, default behavior/message
        try:
            sentiment = response[0].attribute_not_on_result_or_error
        except AttributeError as default_behavior:
            assert default_behavior.args[0] == '\'DocumentError\' object has no attribute \'attribute_not_on_result_or_error\''

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_bad_model_version_error(self, client):
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        try:
            result = client.analyze_sentiment(docs, model_version="bad")
        except HttpResponseError as err:
            assert err.error.code == "ModelVersionIncorrect"
            assert err.error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_document_errors(self, client):
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": text}]

        doc_errors = client.analyze_sentiment(docs)
        assert doc_errors[0].error.code == "InvalidDocument"
        assert doc_errors[0].error.message is not None
        assert doc_errors[1].error.code == "UnsupportedLanguageCode"
        assert doc_errors[1].error.message is not None
        assert doc_errors[2].error.code == "InvalidDocument"
        assert doc_errors[2].error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_not_passing_list_for_docs(self, client):
        docs = {"id": "1", "text": "hello world"}
        with pytest.raises(TypeError) as excinfo:
            client.analyze_sentiment(docs)
        assert "Input documents cannot be a dict" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_missing_input_records_error(self, client):
        docs = []
        with pytest.raises(ValueError) as excinfo:
            client.analyze_sentiment(docs)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_passing_none_docs(self, client):
        with pytest.raises(ValueError) as excinfo:
            client.analyze_sentiment(None)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_duplicate_ids_error(self, client):
        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed at."}]
        try:
            result = client.analyze_sentiment(docs)
        except HttpResponseError as err:
            assert err.error.code == "InvalidDocument"
            assert err.error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_batch_size_over_limit_error(self, client):
        # Batch size over limit
        docs = ["hello world"] * 1001
        try:
            response = client.analyze_sentiment(docs)
        except HttpResponseError as err:
            assert err.error.code == "InvalidDocumentBatch"
            assert err.error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_language_kwarg_spanish(self, client):
        def callback(response):
            language_str = "\"language\": \"es\""
            assert response.http_request.body.count(language_str) == 1
            assert response.model_version is not None
            assert response.statistics is not None

        res = client.analyze_sentiment(
            documents=["Bill Gates is the CEO of Microsoft."],
            model_version="latest",
            show_stats=True,
            language="es",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_pass_cls(self, client):
        def callback(pipeline_response, deserialized, _):
            return "cls result"
        res = client.analyze_sentiment(
            documents=["Test passing cls to endpoint"],
            cls=callback
        )
        assert res == "cls result"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_opinion_mining(self, client):
        documents = [
            "It has a sleek premium aluminum design that makes it beautiful to look at."
        ]

        document = client.analyze_sentiment(documents=documents, show_opinion_mining=True)[0]

        for sentence in document.sentences:
            for mined_opinion in sentence.mined_opinions:
                target = mined_opinion.target
                assert 'design' == target.text
                assert 'positive' == target.sentiment
                assert 0.0 == target.confidence_scores.neutral
                self.validateConfidenceScores(target.confidence_scores)
                assert 32 == target.offset

                sleek_opinion = mined_opinion.assessments[0]
                assert 'sleek' == sleek_opinion.text
                assert 'positive' == sleek_opinion.sentiment
                assert 0.0 == sleek_opinion.confidence_scores.neutral
                self.validateConfidenceScores(sleek_opinion.confidence_scores)
                assert 9 == sleek_opinion.offset
                assert not sleek_opinion.is_negated

                # FIXME https://msazure.visualstudio.com/Cognitive%20Services/_workitems/edit/13848227
                # premium_opinion = mined_opinion.assessments[1]
                # assert 'premium' == premium_opinion.text
                # assert 'positive' == premium_opinion.sentiment
                # assert 0.0 == premium_opinion.confidence_scores.neutral
                # self.validateConfidenceScores(premium_opinion.confidence_scores)
                # assert 15 == premium_opinion.offset
                # assert not premium_opinion.is_negated

                beautiful_opinion = mined_opinion.assessments[1]
                assert 'beautiful' == beautiful_opinion.text
                assert 'positive' == beautiful_opinion.sentiment
                assert 1.0 == beautiful_opinion.confidence_scores.positive
                self.validateConfidenceScores(beautiful_opinion.confidence_scores)
                assert 53 == beautiful_opinion.offset
                assert not beautiful_opinion.is_negated

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_opinion_mining_with_negated_opinion(self, client):
        documents = [
            "The food and service is not good"
        ]

        document = client.analyze_sentiment(documents=documents, show_opinion_mining=True)[0]

        for sentence in document.sentences:
            food_target = sentence.mined_opinions[0].target
            service_target = sentence.mined_opinions[1].target

            assert 'food' == food_target.text
            assert 'negative' == food_target.sentiment
            assert 0.0 == food_target.confidence_scores.neutral
            self.validateConfidenceScores(food_target.confidence_scores)
            assert 4 == food_target.offset

            assert 'service' == service_target.text
            # assert 'negative' == service_target.sentiment  FIXME https://msazure.visualstudio.com/Cognitive%20Services/_workitems/edit/13848227
            assert 0.0 == service_target.confidence_scores.neutral
            self.validateConfidenceScores(service_target.confidence_scores)
            assert 13 == service_target.offset

            food_opinion = sentence.mined_opinions[0].assessments[0]
            service_opinion = sentence.mined_opinions[1].assessments[0]
            self.assertOpinionsEqual(food_opinion, service_opinion)

            assert 'good' == food_opinion.text
            assert 'negative' == food_opinion.sentiment
            assert 0.0 == food_opinion.confidence_scores.neutral
            self.validateConfidenceScores(food_opinion.confidence_scores)
            assert 28 == food_opinion.offset
            assert food_opinion.is_negated


    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_opinion_mining_more_than_5_documents(self, client):
        documents = [
            "The food was unacceptable",
            "The rooms were beautiful. The AC was good and quiet.",
            "The breakfast was good, but the toilet was smelly.",
            "Loved this hotel - good breakfast - nice shuttle service - clean rooms.",
            "I had a great unobstructed view of the Microsoft campus.",
            "Nice rooms but bathrooms were old and the toilet was dirty when we arrived.",
            "The toilet smelled."
        ]

        analyzed_documents = client.analyze_sentiment(documents, show_opinion_mining=True)
        doc_5 = analyzed_documents[5]
        doc_6 = analyzed_documents[6]

        doc_5_opinions = [
            opinion.text
            for sentence in doc_5.sentences
            for mined_opinion in sentence.mined_opinions
            for opinion in mined_opinion.assessments
        ]

        doc_6_opinions = [
            opinion.text
            for sentence in doc_6.sentences
            for mined_opinion in sentence.mined_opinions
            for opinion in mined_opinion.assessments
        ]

        assert doc_5_opinions == ["Nice", "old", "dirty"]
        assert doc_6_opinions == ["smelled"]

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_opinion_mining_no_mined_opinions(self, client):
        document = client.analyze_sentiment(documents=["today is a hot day"], show_opinion_mining=True)[0]

        assert not document.sentences[0].mined_opinions

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    def test_opinion_mining_v3(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as excinfo:
            client.analyze_sentiment(["will fail"], show_opinion_mining=True)

        assert "'show_opinion_mining' is only available for API version v3.1 and up" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_offset(self, client):
        result = client.analyze_sentiment(["I like nature. I do not like being inside"])
        sentences = result[0].sentences
        assert sentences[0].offset == 0
        assert sentences[1].offset == 15

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    @recorded_by_proxy
    def test_no_offset_v3_sentence_sentiment(self, client):
        result = client.analyze_sentiment(["I like nature. I do not like being inside"])
        sentences = result[0].sentences
        assert sentences[0].offset is None
        assert sentences[1].offset is None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy
    def test_default_string_index_type_is_UnicodeCodePoint(self, client):
        def callback(response):
            assert response.http_request.query["stringIndexType"] == "UnicodeCodePoint"

        res = client.analyze_sentiment(
            documents=["Hello world"],
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V2022_05_01})
    @recorded_by_proxy
    def test_default_string_index_type_UnicodeCodePoint_body_param(self, client):
        def callback(response):
            assert json.loads(response.http_request.body)['parameters']["stringIndexType"] == "UnicodeCodePoint"

        res = client.analyze_sentiment(
            documents=["Hello world"],
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy
    def test_explicit_set_string_index_type(self, client):
        def callback(response):
            assert response.http_request.query["stringIndexType"] == "TextElement_v8"

        res = client.analyze_sentiment(
            documents=["Hello world"],
            string_index_type="TextElement_v8",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V2022_05_01})
    @recorded_by_proxy
    def test_explicit_set_string_index_type_body_param(self, client):
        def callback(response):
            assert json.loads(response.http_request.body)['parameters']["stringIndexType"] == "TextElements_v8"

        res = client.analyze_sentiment(
            documents=["Hello world"],
            string_index_type="TextElement_v8",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy
    def test_disable_service_logs(self, client):
        def callback(resp):
            assert resp.http_request.query['loggingOptOut']
        client.analyze_sentiment(
            documents=["Test for logging disable"],
            disable_service_logs=True,
            raw_response_hook=callback,
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V2022_05_01})
    @recorded_by_proxy
    def test_disable_service_logs_body_param(self, client):
        def callback(resp):
            assert json.loads(resp.http_request.body)['parameters']['loggingOptOut']
        client.analyze_sentiment(
            documents=["Test for logging disable"],
            disable_service_logs=True,
            raw_response_hook=callback,
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": "v3.0"})
    def test_sentiment_multiapi_validate_args_v3_0(self, **kwargs):
        client = kwargs.pop("client")

        with pytest.raises(ValueError) as e:
            res = client.analyze_sentiment(["I'm tired"], string_index_type="UnicodeCodePoint")
        assert str(e.value) == "'string_index_type' is only available for API version v3.1 and up.\n"

        with pytest.raises(ValueError) as e:
            res = client.analyze_sentiment(["I'm tired"], show_opinion_mining=True)
        assert str(e.value) == "'show_opinion_mining' is only available for API version v3.1 and up.\n"

        with pytest.raises(ValueError) as e:
            res = client.analyze_sentiment(["I'm tired"], disable_service_logs=True)
        assert str(e.value) == "'disable_service_logs' is only available for API version v3.1 and up.\n"

        with pytest.raises(ValueError) as e:
            res = client.analyze_sentiment(["I'm tired"], show_opinion_mining=True, disable_service_logs=True, string_index_type="UnicodeCodePoint")
        assert str(e.value) == "'show_opinion_mining' is only available for API version v3.1 and up.\n'disable_service_logs' is only available for API version v3.1 and up.\n'string_index_type' is only available for API version v3.1 and up.\n"

    @TextAnalyticsPreparer()
    def test_mock_quota_exceeded(self, **kwargs):
        textanalytics_test_endpoint = kwargs.pop("textanalytics_test_endpoint")
        textanalytics_test_api_key = kwargs.pop("textanalytics_test_api_key")
        response = mock.Mock(
            status_code=403,
            headers={"Retry-After": 186688, "Content-Type": "application/json"},
            reason="Bad Request"
        )
        response.text = lambda encoding=None: json.dumps(
            {"error": {"code": "403", "message": "Out of call volume quota for TextAnalytics F0 pricing tier. Please retry after 15 days. To increase your call volume switch to a paid tier."}}
        )
        response.content_type = "application/json"
        transport = mock.Mock(send=lambda request, **kwargs: response)

        client = TextAnalyticsClient(textanalytics_test_endpoint, AzureKeyCredential(textanalytics_test_api_key), transport=transport)

        with pytest.raises(HttpResponseError) as e:
            result = client.analyze_sentiment(["I'm tired"])
        assert e.value.status_code == 403
        assert e.value.error.message == 'Out of call volume quota for TextAnalytics F0 pricing tier. Please retry after 15 days. To increase your call volume switch to a paid tier.'

# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import pytest
import platform
import functools

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.pipeline.transport import AioHttpTransport
from azure.core.credentials import AzureKeyCredential
from multidict import CIMultiDict, CIMultiDictProxy
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.ai.textanalytics import (
    VERSION,
    DetectLanguageInput,
    TextDocumentInput,
    TextAnalyticsApiVersion,
)

from testcase import GlobalTextAnalyticsAccountPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from asynctestcase import AsyncTextAnalyticsTest

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)

class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class TestAnalyzeSentiment(AsyncTextAnalyticsTest):

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_no_single_input(self, client):
        with self.assertRaises(TypeError):
            response = await client.analyze_sentiment("hello world")

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_all_successful_passing_dict(self, client):
        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
                {"id": "2", "language": "en", "text": "I did not like the hotel we stayed at. It was too expensive."},
                {"id": "3", "language": "en", "text": "The restaurant had really good food. I recommend you try it."}]

        response = await client.analyze_sentiment(docs, show_stats=True)
        self.assertEqual(response[0].sentiment, "neutral")
        self.assertEqual(response[1].sentiment, "negative")
        self.assertEqual(response[2].sentiment, "positive")

        for doc in response:
            self.assertIsNotNone(doc.id)
            self.assertIsNotNone(doc.statistics)
            self.validateConfidenceScores(doc.confidence_scores)
            self.assertIsNotNone(doc.sentences)

        self.assertEqual(len(response[0].sentences), 1)
        self.assertEqual(response[0].sentences[0].text, "Microsoft was founded by Bill Gates and Paul Allen.")
        self.assertEqual(len(response[1].sentences), 2)
        self.assertEqual(response[1].sentences[0].text, "I did not like the hotel we stayed at.")
        self.assertEqual(response[1].sentences[1].text, "It was too expensive.")
        self.assertEqual(len(response[2].sentences), 2)
        self.assertEqual(response[2].sentences[0].text, "The restaurant had really good food.")
        self.assertEqual(response[2].sentences[1].text, "I recommend you try it.")

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_all_successful_passing_text_document_input(self, client):
        docs = [
            TextDocumentInput(id="1", text="Microsoft was founded by Bill Gates and Paul Allen."),
            TextDocumentInput(id="2", text="I did not like the hotel we stayed at. It was too expensive."),
            TextDocumentInput(id="3", text="The restaurant had really good food. I recommend you try it."),
        ]

        response = await client.analyze_sentiment(docs)
        self.assertEqual(response[0].sentiment, "neutral")
        self.assertEqual(response[1].sentiment, "negative")
        self.assertEqual(response[2].sentiment, "positive")

        for doc in response:
            self.validateConfidenceScores(doc.confidence_scores)
            self.assertIsNotNone(doc.sentences)

        self.assertEqual(len(response[0].sentences), 1)
        self.assertEqual(response[0].sentences[0].text, "Microsoft was founded by Bill Gates and Paul Allen.")
        self.assertEqual(len(response[1].sentences), 2)
        self.assertEqual(response[1].sentences[0].text, "I did not like the hotel we stayed at.")
        self.assertEqual(response[1].sentences[1].text, "It was too expensive.")
        self.assertEqual(len(response[2].sentences), 2)
        self.assertEqual(response[2].sentences[0].text, "The restaurant had really good food.")
        self.assertEqual(response[2].sentences[1].text, "I recommend you try it.")

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_passing_only_string(self, client):
        docs = [
            u"Microsoft was founded by Bill Gates and Paul Allen.",
            u"I did not like the hotel we stayed at. It was too expensive.",
            u"The restaurant had really good food. I recommend you try it.",
            u""
        ]

        response = await client.analyze_sentiment(docs)
        self.assertEqual(response[0].sentiment, "neutral")
        self.assertEqual(response[1].sentiment, "negative")
        self.assertEqual(response[2].sentiment, "positive")
        self.assertTrue(response[3].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_input_with_some_errors(self, client):
        docs = [{"id": "1", "language": "en", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed at. It was too expensive."},
                {"id": "3", "language": "en", "text": "The restaurant had really good food. I recommend you try it."}]

        response = await client.analyze_sentiment(docs)
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_input_with_all_errors(self, client):
        docs = [{"id": "1", "language": "en", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed at. It was too expensive."},
                {"id": "3", "language": "en", "text": ""}]

        response = await client.analyze_sentiment(docs)
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)
        self.assertTrue(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_too_many_documents(self, client):
        docs = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven"]

        with pytest.raises(HttpResponseError) as excinfo:
            await client.analyze_sentiment(docs)
        assert excinfo.value.status_code == 400
        assert excinfo.value.error.code == "InvalidDocumentBatch"
        assert "Batch request contains too many records" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_output_same_order_as_input(self, client):
        docs = [
            TextDocumentInput(id="1", text="one"),
            TextDocumentInput(id="2", text="two"),
            TextDocumentInput(id="3", text="three"),
            TextDocumentInput(id="4", text="four"),
            TextDocumentInput(id="5", text="five")
        ]

        response = await client.analyze_sentiment(docs)

        for idx, doc in enumerate(response):
            self.assertEqual(str(idx + 1), doc.id)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"text_analytics_account_key": ""})
    async def test_empty_credential_class(self, client):
        with self.assertRaises(ClientAuthenticationError):
            response = await client.analyze_sentiment(
                ["This is written in English."]
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"text_analytics_account_key": "xxxxxxxxxxxx"})
    async def test_bad_credentials(self, client):
        with self.assertRaises(ClientAuthenticationError):
            response = await client.analyze_sentiment(
                ["This is written in English."]
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_bad_document_input(self, client):
        docs = "This is the wrong type"

        with self.assertRaises(TypeError):
            response = await client.analyze_sentiment(docs)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_mixing_inputs(self, client):
        docs = [
            {"id": "1", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
            TextDocumentInput(id="2", text="I did not like the hotel we stayed at. It was too expensive."),
            u"You cannot mix string input with the above inputs"
        ]
        with self.assertRaises(TypeError):
            response = await client.analyze_sentiment(docs)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_out_of_order_ids(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = await client.analyze_sentiment(docs)
        in_order = ["56", "0", "22", "19", "1"]
        for idx, resp in enumerate(response):
            self.assertEqual(resp.id, in_order[idx])

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_show_stats_and_model_version(self, client):
        def callback(response):
            self.assertIsNotNone(response)
            self.assertIsNotNone(response.model_version, msg=response.raw_response)
            self.assertIsNotNone(response.raw_response)
            self.assertEqual(response.statistics.document_count, 5)
            self.assertEqual(response.statistics.transaction_count, 4)
            self.assertEqual(response.statistics.valid_document_count, 4)
            self.assertEqual(response.statistics.erroneous_document_count, 1)

        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = await client.analyze_sentiment(
            docs,
            show_stats=True,
            model_version="latest",
            raw_response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_batch_size_over_limit(self, client):
        docs = [u"hello world"] * 1050
        with self.assertRaises(HttpResponseError):
            response = await client.analyze_sentiment(docs)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_whole_batch_language_hint(self, client):
        def callback(resp):
            language_str = "\"language\": \"fr\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed at. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        response = await client.analyze_sentiment(docs, language="fr", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_whole_batch_dont_use_language_hint(self, client):
        def callback(resp):
            language_str = "\"language\": \"\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed at. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        response = await client.analyze_sentiment(docs, language="", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_per_item_dont_use_language_hint(self, client):
        def callback(resp):
            language_str = "\"language\": \"\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 2)
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 1)


        docs = [{"id": "1", "language": "", "text": "I will go to the park."},
                {"id": "2", "language": "", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.analyze_sentiment(docs, raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_whole_batch_language_hint_and_obj_input(self, client):
        def callback(resp):
            language_str = "\"language\": \"de\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian."),
            TextDocumentInput(id="4", text="Este es un document escrito en Español."),
            TextDocumentInput(id="3", text="猫は幸せ"),
        ]

        response = await client.analyze_sentiment(docs, language="de", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_whole_batch_language_hint_and_dict_input(self, client):
        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.analyze_sentiment(docs, language="es", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_whole_batch_language_hint_and_obj_per_item_hints(self, client):
        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 2)
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 1)

        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian.", language="es"),
            TextDocumentInput(id="2", text="Este es un document escrito en Español.", language="es"),
            TextDocumentInput(id="3", text="猫は幸せ"),
        ]

        response = await client.analyze_sentiment(docs, language="en", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_whole_batch_language_hint_and_dict_per_item_hints(self, client):
        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 2)
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 1)


        docs = [{"id": "1", "language": "es", "text": "I will go to the park."},
                {"id": "2", "language": "es", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.analyze_sentiment(docs, language="en", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"default_language": "es"})
    async def test_client_passed_default_language_hint(self, client):
        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        def callback_2(resp):
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.analyze_sentiment(docs, raw_response_hook=callback)
        response = await client.analyze_sentiment(docs, language="en", raw_response_hook=callback_2)
        response = await client.analyze_sentiment(docs, raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_invalid_language_hint_method(self, client):
        response = await client.analyze_sentiment(
            ["This should fail because we're passing in an invalid language hint"], language="notalanguage"
        )
        self.assertEqual(response[0].error.code, 'UnsupportedLanguageCode')

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_invalid_language_hint_docs(self, client):
        response = await client.analyze_sentiment(
            [{"id": "1", "language": "notalanguage", "text": "This should fail because we're passing in an invalid language hint"}]
        )
        self.assertEqual(response[0].error.code, 'UnsupportedLanguageCode')

    @GlobalTextAnalyticsAccountPreparer()
    async def test_rotate_subscription_key(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        credential = AzureKeyCredential(text_analytics_account_key)
        client = TextAnalyticsClient(text_analytics_account, credential)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.analyze_sentiment(docs)
        self.assertIsNotNone(response)

        credential.update("xxx")  # Make authentication fail
        with self.assertRaises(ClientAuthenticationError):
            response = await client.analyze_sentiment(docs)

        credential.update(text_analytics_account_key)  # Authenticate successfully again
        response = await client.analyze_sentiment(docs)
        self.assertIsNotNone(response)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_user_agent(self, client):
        def callback(resp):
            self.assertIn("azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                VERSION, platform.python_version(), platform.platform()),
                resp.http_request.headers["User-Agent"]
            )

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.analyze_sentiment(docs, raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_document_attribute_error_no_result_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        response = await client.analyze_sentiment(docs)

        # Attributes on DocumentError
        self.assertTrue(response[0].is_error)
        self.assertEqual(response[0].id, "1")
        self.assertIsNotNone(response[0].error)

        # Result attribute not on DocumentError, custom error message
        try:
            sentiment = response[0].sentiment
        except AttributeError as custom_error:
            self.assertEqual(
                custom_error.args[0],
                '\'DocumentError\' object has no attribute \'sentiment\'. '
                'The service was unable to process this document:\nDocument Id: 1\nError: '
                'InvalidDocument - Document text is empty.\n'
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_document_attribute_error_nonexistent_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        response = await client.analyze_sentiment(docs)

        # Attribute not found on DocumentError or result obj, default behavior/message
        try:
            sentiment = response[0].attribute_not_on_result_or_error
        except AttributeError as default_behavior:
            self.assertEqual(
                default_behavior.args[0],
                '\'DocumentError\' object has no attribute \'attribute_not_on_result_or_error\''
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_bad_model_version_error(self, client):
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        try:
            result = await client.analyze_sentiment(docs, model_version="bad")
        except HttpResponseError as err:
            self.assertEqual(err.error.code, "ModelVersionIncorrect")
            self.assertIsNotNone(err.error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_document_errors(self, client):
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": text}]

        doc_errors = await client.analyze_sentiment(docs)
        self.assertEqual(doc_errors[0].error.code, "InvalidDocument")
        self.assertIsNotNone(doc_errors[0].error.message)
        self.assertEqual(doc_errors[1].error.code, "UnsupportedLanguageCode")
        self.assertIsNotNone(doc_errors[1].error.message)
        self.assertEqual(doc_errors[2].error.code, "InvalidDocument")
        self.assertIsNotNone(doc_errors[2].error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_document_warnings(self, client):
        # No warnings actually returned for analyze_sentiment. Will update when they add
        docs = [
            {"id": "1", "text": "This won't actually create a warning :'("},
        ]

        result = await client.analyze_sentiment(docs)
        for doc in result:
            doc_warnings = doc.warnings
            self.assertEqual(len(doc_warnings), 0)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_not_passing_list_for_docs(self, client):
        docs = {"id": "1", "text": "hello world"}
        with pytest.raises(TypeError) as excinfo:
            await client.analyze_sentiment(docs)
        assert "Input documents cannot be a dict" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_missing_input_records_error(self, client):
        docs = []
        with pytest.raises(ValueError) as excinfo:
            await client.analyze_sentiment(docs)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_passing_none_docs(self, client):
        with pytest.raises(ValueError) as excinfo:
            await client.analyze_sentiment(None)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_duplicate_ids_error(self, client):
        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed at."}]
        try:
            result = await client.analyze_sentiment(docs)
        except HttpResponseError as err:
            self.assertEqual(err.error.code, "InvalidDocument")
            self.assertIsNotNone(err.error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_batch_size_over_limit_error(self, client):
        # Batch size over limit
        docs = [u"hello world"] * 1001
        try:
            response = await client.analyze_sentiment(docs)
        except HttpResponseError as err:
            self.assertEqual(err.error.code, "InvalidDocumentBatch")
            self.assertIsNotNone(err.error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_language_kwarg_spanish(self, client):
        def callback(response):
            language_str = "\"language\": \"es\""
            self.assertEqual(response.http_request.body.count(language_str), 1)
            self.assertIsNotNone(response.model_version)
            self.assertIsNotNone(response.statistics)

        res = await client.analyze_sentiment(
            documents=["Bill Gates is the CEO of Microsoft."],
            model_version="latest",
            show_stats=True,
            language="es",
            raw_response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_pass_cls(self, client):
        def callback(pipeline_response, deserialized, _):
            return "cls result"
        res = await client.analyze_sentiment(
            documents=["Test passing cls to endpoint"],
            cls=callback
        )
        assert res == "cls result"

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_opinion_mining(self, client):
        documents = [
            "It has a sleek premium aluminum design that makes it beautiful to look at."
        ]

        document = (await client.analyze_sentiment(documents=documents, show_opinion_mining=True))[0]

        for sentence in document.sentences:
            for mined_opinion in sentence.mined_opinions:
                target = mined_opinion.target
                self.assertEqual('design', target.text)
                self.assertEqual('positive', target.sentiment)
                self.assertEqual(0.0, target.confidence_scores.neutral)
                self.validateConfidenceScores(target.confidence_scores)
                self.assertEqual(32, target.offset)

                sleek_opinion = mined_opinion.assessments[0]
                self.assertEqual('sleek', sleek_opinion.text)
                self.assertEqual('positive', sleek_opinion.sentiment)
                self.assertEqual(0.0, sleek_opinion.confidence_scores.neutral)
                self.validateConfidenceScores(sleek_opinion.confidence_scores)
                self.assertEqual(9, sleek_opinion.offset)
                self.assertFalse(sleek_opinion.is_negated)

                premium_opinion = mined_opinion.assessments[1]
                self.assertEqual('premium', premium_opinion.text)
                self.assertEqual('positive', premium_opinion.sentiment)
                self.assertEqual(0.0, premium_opinion.confidence_scores.neutral)
                self.validateConfidenceScores(premium_opinion.confidence_scores)
                self.assertEqual(15, premium_opinion.offset)
                self.assertFalse(premium_opinion.is_negated)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_opinion_mining_with_negated_opinion(self, client):
        documents = [
            "The food and service is not good"
        ]

        document = (await client.analyze_sentiment(documents=documents, show_opinion_mining=True))[0]

        for sentence in document.sentences:
            food_target = sentence.mined_opinions[0].target
            service_target = sentence.mined_opinions[1].target

            self.assertEqual('food', food_target.text)
            self.assertEqual('negative', food_target.sentiment)
            self.assertEqual(0.0, food_target.confidence_scores.neutral)
            self.validateConfidenceScores(food_target.confidence_scores)
            self.assertEqual(4, food_target.offset)

            self.assertEqual('service', service_target.text)
            self.assertEqual('negative', service_target.sentiment)
            self.assertEqual(0.0, service_target.confidence_scores.neutral)
            self.validateConfidenceScores(service_target.confidence_scores)
            self.assertEqual(13, service_target.offset)

            food_opinion = sentence.mined_opinions[0].assessments[0]
            service_opinion = sentence.mined_opinions[1].assessments[0]
            self.assertOpinionsEqual(food_opinion, service_opinion)

            self.assertEqual('good', food_opinion.text)
            self.assertEqual('negative', food_opinion.sentiment)
            self.assertEqual(0.0, food_opinion.confidence_scores.neutral)
            self.validateConfidenceScores(food_opinion.confidence_scores)
            self.assertEqual(28, food_opinion.offset)
            self.assertTrue(food_opinion.is_negated)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_opinion_mining_more_than_5_documents(self, client):
        documents = [
            "The food was unacceptable",
            "The rooms were beautiful. The AC was good and quiet.",
            "The breakfast was good, but the toilet was smelly.",
            "Loved this hotel - good breakfast - nice shuttle service - clean rooms.",
            "I had a great unobstructed view of the Microsoft campus.",
            "Nice rooms but bathrooms were old and the toilet was dirty when we arrived.",
            "The toilet smelled."
        ]

        analyzed_documents = await client.analyze_sentiment(documents, show_opinion_mining=True)
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

        assert doc_5_opinions == ["nice", "old", "dirty"]
        assert doc_6_opinions == ["smelled"]

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_opinion_mining_no_mined_opinions(self, client):
        document = (await client.analyze_sentiment(documents=["today is a hot day"], show_opinion_mining=True))[0]

        assert not document.sentences[0].mined_opinions

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    async def test_opinion_mining_v3(self, client):
        with pytest.raises(ValueError) as excinfo:
            await client.analyze_sentiment(["will fail"], show_opinion_mining=True)

        assert "'show_opinion_mining' is only available for API version v3.1-preview and up" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_offset(self, client):
        result = await client.analyze_sentiment(["I like nature. I do not like being inside"])
        sentences = result[0].sentences
        self.assertEqual(sentences[0].offset, 0)
        self.assertEqual(sentences[1].offset, 15)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    async def test_no_offset_v3_sentence_sentiment(self, client):
        result = await client.analyze_sentiment(["I like nature. I do not like being inside"])
        sentences = result[0].sentences
        self.assertIsNone(sentences[0].offset)
        self.assertIsNone(sentences[1].offset)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    async def test_string_index_type_not_fail_v3(self, client):
        # make sure that the addition of the string_index_type kwarg for v3.1-preview.1 doesn't
        # cause v3.0 calls to fail
        await client.analyze_sentiment(["please don't fail"])

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    async def test_string_index_type_explicit_fails_v3(self, client):
        with pytest.raises(ValueError) as excinfo:
            await client.analyze_sentiment(["this should fail"], string_index_type="UnicodeCodePoint")
        assert "'string_index_type' is only available for API version V3_1_PREVIEW and up" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_default_string_index_type_is_UnicodeCodePoint(self, client):
        def callback(response):
            self.assertEqual(response.http_request.query["stringIndexType"], "UnicodeCodePoint")

        res = await client.analyze_sentiment(
            documents=["Hello world"],
            raw_response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_explicit_set_string_index_type(self, client):
        def callback(response):
            self.assertEqual(response.http_request.query["stringIndexType"], "TextElements_v8")

        res = await client.analyze_sentiment(
            documents=["Hello world"],
            string_index_type="TextElements_v8",
            raw_response_hook=callback
        )

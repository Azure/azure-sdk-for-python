# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import platform

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from testcase import TextAnalyticsTest, GlobalTextAnalyticsAccountPreparer
from azure.ai.textanalytics import (
    TextAnalyticsApiKeyCredential,
    TextAnalyticsClient,
    TextDocumentInput,
    VERSION
)


class TestRecognizePIIEntities(TextAnalyticsTest):

    @GlobalTextAnalyticsAccountPreparer()
    def test_no_single_input(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))
        with self.assertRaises(TypeError):
            response = text_analytics.recognize_pii_entities("hello world")

    @GlobalTextAnalyticsAccountPreparer()
    def test_all_successful_passing_dict(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        docs = [{"id": "1", "text": "My SSN is 555-55-5555."},
                {"id": "2", "text": "Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check."},
                {"id": "3", "text": "Is 998.214.865-68 your Brazilian CPF number?"}]

        response = text_analytics.recognize_pii_entities(docs, show_stats=True)
        self.assertEqual(response[0].entities[0].text, "555-55-5555")
        self.assertEqual(response[0].entities[0].category, "U.S. Social Security Number (SSN)")
        self.assertEqual(response[1].entities[0].text, "111000025")
        # self.assertEqual(response[1].entities[0].category, "ABA Routing Number")  # Service is currently returning PhoneNumber here
        self.assertEqual(response[2].entities[0].text, "998.214.865-68")
        self.assertEqual(response[2].entities[0].category, "Brazil CPF Number")
        for doc in response:
            self.assertIsNotNone(doc.id)
            self.assertIsNotNone(doc.statistics)
            for entity in doc.entities:
                self.assertIsNotNone(entity.text)
                self.assertIsNotNone(entity.category)
                self.assertIsNotNone(entity.offset)
                self.assertIsNotNone(entity.length)
                self.assertIsNotNone(entity.score)

    @GlobalTextAnalyticsAccountPreparer()
    def test_all_successful_passing_text_document_input(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        docs = [
            TextDocumentInput(id="1", text="My SSN is 555-55-5555."),
            TextDocumentInput(id="2", text="Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check."),
            TextDocumentInput(id="3", text="Is 998.214.865-68 your Brazilian CPF number?")
        ]

        response = text_analytics.recognize_pii_entities(docs, show_stats=True)
        self.assertEqual(response[0].entities[0].text, "555-55-5555")
        self.assertEqual(response[0].entities[0].category, "U.S. Social Security Number (SSN)")
        self.assertEqual(response[1].entities[0].text, "111000025")
        # self.assertEqual(response[1].entities[0].category, "ABA Routing Number")  # Service is currently returning PhoneNumber here
        self.assertEqual(response[2].entities[0].text, "998.214.865-68")
        self.assertEqual(response[2].entities[0].category, "Brazil CPF Number")
        for doc in response:
            self.assertIsNotNone(doc.id)
            self.assertIsNotNone(doc.statistics)
            for entity in doc.entities:
                self.assertIsNotNone(entity.text)
                self.assertIsNotNone(entity.category)
                self.assertIsNotNone(entity.offset)
                self.assertIsNotNone(entity.length)
                self.assertIsNotNone(entity.score)

    @GlobalTextAnalyticsAccountPreparer()
    def test_passing_only_string(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        docs = [
            u"My SSN is 555-55-5555.",
            u"Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check.",
            u"Is 998.214.865-68 your Brazilian CPF number?",
            u""
        ]

        response = text_analytics.recognize_pii_entities(docs, show_stats=True)
        self.assertEqual(response[0].entities[0].text, "555-55-5555")
        self.assertEqual(response[0].entities[0].category, "U.S. Social Security Number (SSN)")
        self.assertEqual(response[1].entities[0].text, "111000025")
        # self.assertEqual(response[1].entities[0].category, "ABA Routing Number")  # Service is currently returning PhoneNumber here
        self.assertEqual(response[2].entities[0].text, "998.214.865-68")
        self.assertEqual(response[2].entities[0].category, "Brazil CPF Number")
        self.assertTrue(response[3].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    def test_some_errors(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        docs = [{"id": "1", "language": "es", "text": "hola"},
                {"id": "2", "text": ""},
                {"id": "3", "text": "Is 998.214.865-68 your Brazilian CPF number?"}]

        response = text_analytics.recognize_pii_entities(docs)
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    def test_all_errors(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        docs = [{"id": "1", "language": "es", "text": "hola"},
                {"id": "2", "text": ""}]

        response = text_analytics.recognize_pii_entities(docs)
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    def test_empty_credential_class(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(""))
        with self.assertRaises(ClientAuthenticationError):
            response = text_analytics.recognize_pii_entities(
                ["This is written in English."]
            )

    @GlobalTextAnalyticsAccountPreparer()
    def test_bad_credentials(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential("xxxxxxxxxxxx"))
        with self.assertRaises(ClientAuthenticationError):
            response = text_analytics.recognize_pii_entities(
                ["This is written in English."]
            )

    @GlobalTextAnalyticsAccountPreparer()
    def test_bad_model_version(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))
        with self.assertRaises(HttpResponseError):
            response = text_analytics.recognize_pii_entities(
                inputs=["Microsoft was founded by Bill Gates."],
                model_version="old"
            )

    @GlobalTextAnalyticsAccountPreparer()
    def test_bad_document_input(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        docs = "This is the wrong type"

        with self.assertRaises(TypeError):
            response = text_analytics.recognize_pii_entities(docs)

    @GlobalTextAnalyticsAccountPreparer()
    def test_mixing_inputs(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))
        docs = [
            {"id": "1", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
            TextDocumentInput(id="2", text="I did not like the hotel we stayed it. It was too expensive."),
            u"You cannot mix string input with the above inputs"
        ]
        with self.assertRaises(TypeError):
            response = text_analytics.recognize_pii_entities(docs)

    @GlobalTextAnalyticsAccountPreparer()
    def test_show_stats_and_model_version(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        def callback(response):
            self.assertIsNotNone(response.model_version)
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

        response = text_analytics.recognize_pii_entities(
            docs,
            show_stats=True,
            model_version="latest",
            raw_response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    def test_batch_size_over_limit(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        docs = [u"hello world"] * 1050
        with self.assertRaises(HttpResponseError):
            response = text_analytics.recognize_pii_entities(docs)

    @GlobalTextAnalyticsAccountPreparer()
    def test_whole_batch_language_hint(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        def callback(resp):
            language_str = "\"language\": \"fr\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed it. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        response = text_analytics.recognize_pii_entities(docs, language="fr", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    def test_whole_batch_dont_use_language_hint(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        def callback(resp):
            language_str = "\"language\": \"\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed it. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        response = text_analytics.recognize_pii_entities(docs, language="", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    def test_per_item_dont_use_language_hint(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        def callback(resp):
            language_str = "\"language\": \"\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 2)
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 1)


        docs = [{"id": "1", "language": "", "text": "I will go to the park."},
                {"id": "2", "language": "", "text": "I did not like the hotel we stayed it."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = text_analytics.recognize_pii_entities(docs, raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    def test_whole_batch_language_hint_and_obj_input(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        def callback(resp):
            language_str = "\"language\": \"de\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian."),
            TextDocumentInput(id="4", text="Este es un document escrito en Español."),
            TextDocumentInput(id="3", text="猫は幸せ"),
        ]

        response = text_analytics.recognize_pii_entities(docs, language="de", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    def test_whole_batch_language_hint_and_obj_per_item_hints(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

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

        response = text_analytics.recognize_pii_entities(docs, language="en", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    def test_whole_batch_language_hint_and_dict_per_item_hints(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 2)
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 1)


        docs = [{"id": "1", "language": "es", "text": "I will go to the park."},
                {"id": "2", "language": "es", "text": "I did not like the hotel we stayed it."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = text_analytics.recognize_pii_entities(docs, language="en", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    def test_client_passed_default_language_hint(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key), default_language="es")

        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        def callback_2(resp):
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed it."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = text_analytics.recognize_pii_entities(docs, raw_response_hook=callback)
        response = text_analytics.recognize_pii_entities(docs, language="en", raw_response_hook=callback_2)
        response = text_analytics.recognize_pii_entities(docs, raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    def test_rotate_subscription_key(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        credential = TextAnalyticsApiKeyCredential(text_analytics_account_key)
        text_analytics = TextAnalyticsClient(text_analytics_account, credential)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed it."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = text_analytics.recognize_pii_entities(docs)
        self.assertIsNotNone(response)

        credential.update_key("xxx")  # Make authentication fail
        with self.assertRaises(ClientAuthenticationError):
            response = text_analytics.recognize_pii_entities(docs)

        credential.update_key(text_analytics_account_key)  # Authenticate successfully again
        response = text_analytics.recognize_pii_entities(docs)
        self.assertIsNotNone(response)

    @GlobalTextAnalyticsAccountPreparer()
    def test_user_agent(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        def callback(resp):
            self.assertIn("azsdk-python-azure-ai-textanalytics/{} Python/{} ({})".format(
                VERSION, platform.python_version(), platform.platform()),
                resp.http_request.headers["User-Agent"]
            )

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed it."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = text_analytics.recognize_pii_entities(docs, raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    def test_document_attribute_error_no_result_attribute(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        docs = [{"id": "1", "text": ""}]
        response = text_analytics.recognize_pii_entities(docs)

        # Attributes on DocumentError
        self.assertTrue(response[0].is_error)
        self.assertEqual(response[0].id, "1")
        self.assertIsNotNone(response[0].error)

        # Result attribute not on DocumentError, custom error message
        try:
            entities = response[0].entities
        except AttributeError as custom_error:
            self.assertEqual(
                custom_error.args[0],
                '\'DocumentError\' object has no attribute \'entities\'. '
                'The service was unable to process this document:\nDocument Id: 1\nError: '
                'invalidDocument - Document text is empty.\n'
            )

    @GlobalTextAnalyticsAccountPreparer()
    def test_document_attribute_error_nonexistent_attribute(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        docs = [{"id": "1", "text": ""}]
        response = text_analytics.recognize_pii_entities(docs)

        # Attribute not found on DocumentError or result obj, default behavior/message
        try:
            entities = response[0].attribute_not_on_result_or_error
        except AttributeError as default_behavior:
            self.assertEqual(
                default_behavior.args[0],
                '\'DocumentError\' object has no attribute \'attribute_not_on_result_or_error\''
            )

    @GlobalTextAnalyticsAccountPreparer()
    def test_text_analytics_error_bad_model_version(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed it."},
                {"id": "3", "text": text}]

        try:
            result = text_analytics.recognize_pii_entities(docs, model_version="bad")
        except HttpResponseError as err:
            self.assertEqual(err.error_code, "InvalidRequest")
            self.assertIsNotNone(err.message)

    @GlobalTextAnalyticsAccountPreparer()
    def test_text_analytics_error_document_errors(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed it."},
                {"id": "3", "text": text}]

        doc_errors = text_analytics.recognize_pii_entities(docs)
        self.assertEqual(doc_errors[0].error.code, "invalidDocument")
        self.assertIsNotNone(doc_errors[0].error.message)
        self.assertEqual(doc_errors[1].error.code, "unsupportedLanguageCode")
        self.assertIsNotNone(doc_errors[1].error.message)
        self.assertEqual(doc_errors[2].error.code, "invalidDocument")
        self.assertIsNotNone(doc_errors[2].error.message)

    @GlobalTextAnalyticsAccountPreparer()
    def test_text_analytics_error_missing_input_records(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed it."},
                {"id": "3", "text": text}]

        docs = []
        try:
            result = text_analytics.recognize_pii_entities(docs)
        except HttpResponseError as err:
            self.assertEqual(err.error_code, "MissingInputRecords")
            self.assertIsNotNone(err.message)

    @GlobalTextAnalyticsAccountPreparer()
    def test_text_analytics_error_duplicate_ids(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed it."},
                {"id": "3", "text": text}]

        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed it."}]
        try:
            result = text_analytics.recognize_pii_entities(docs)
        except HttpResponseError as err:
            self.assertEqual(err.error_code, "InvalidDocument")
            self.assertIsNotNone(err.message)

    @GlobalTextAnalyticsAccountPreparer()
    def test_text_analytics_error_batch_size_over_limit(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed it."},
                {"id": "3", "text": text}]

        # Batch size over limit
        docs = [u"hello world"] * 1001
        try:
            response = text_analytics.recognize_pii_entities(docs)
        except HttpResponseError as err:
            self.assertEqual(err.error_code, "InvalidDocumentBatch")
            self.assertIsNotNone(err.message)

    @GlobalTextAnalyticsAccountPreparer()
    @pytest.mark.skip(reason="Service bug returns invalidDocument here. Unskip after v3.0-preview.2")
    def test_text_analytics_error_bad_model_version(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        docs = [{"id": "1", "country_hint": "United States", "text": "hello world"}]

        response = text_analytics.recognize_pii_entities(docs)
        self.assertEqual(response[0].error.code, "invalidCountryHint")
        self.assertIsNotNone(response[0].error.message)

    @GlobalTextAnalyticsAccountPreparer()
    def test_language_kwarg_spanish(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        def callback(response):
            language_str = "\"language\": \"es\""
            self.assertEqual(response.http_request.body.count(language_str), 1)
            self.assertIsNotNone(response.model_version)
            self.assertIsNotNone(response.statistics)

        res = text_analytics.recognize_pii_entities(
            inputs=["Bill Gates is the CEO of Microsoft."],
            model_version="latest",
            show_stats=True,
            language="es",
            raw_response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    def test_language_kwarg_spanish(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, TextAnalyticsApiKeyCredential(text_analytics_account_key))

        def callback(response):
            language_str = "\"language\": \"en\""
            self.assertEqual(response.http_request.body.count(language_str), 1)
            self.assertIsNotNone(response.model_version)
            self.assertIsNotNone(response.statistics)

        res = text_analytics.recognize_pii_entities(
            inputs=["Bill Gates is the CEO of Microsoft."],
            model_version="latest",
            show_stats=True,
            language="en",
            raw_response_hook=callback
        )

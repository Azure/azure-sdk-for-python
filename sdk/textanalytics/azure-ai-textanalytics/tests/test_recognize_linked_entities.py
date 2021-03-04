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
from azure.core.credentials import AzureKeyCredential
from testcase import TextAnalyticsTest, GlobalTextAnalyticsAccountPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    TextDocumentInput,
    VERSION,
    TextAnalyticsApiVersion,
)

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)

class TestRecognizeLinkedEntities(TextAnalyticsTest):

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_no_single_input(self, client):
        with self.assertRaises(TypeError):
            response = client.recognize_linked_entities("hello world")

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_all_successful_passing_dict(self, client):
        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen"},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        response = client.recognize_linked_entities(docs, show_stats=True)
        for doc in response:
            self.assertEqual(len(doc.entities), 3)
            self.assertIsNotNone(doc.id)
            self.assertIsNotNone(doc.statistics)
            for entity in doc.entities:
                self.assertIsNotNone(entity.name)
                self.assertIsNotNone(entity.language)
                self.assertIsNotNone(entity.data_source_entity_id)
                self.assertIsNotNone(entity.url)
                self.assertIsNotNone(entity.data_source)
                self.assertIsNotNone(entity.matches)
                for match in entity.matches:
                    self.assertIsNotNone(match.offset)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_all_successful_passing_text_document_input(self, client):
        docs = [
            TextDocumentInput(id="1", text="Microsoft was founded by Bill Gates and Paul Allen"),
            TextDocumentInput(id="2", text="Microsoft fue fundado por Bill Gates y Paul Allen")
        ]

        response = client.recognize_linked_entities(docs)
        for doc in response:
            self.assertEqual(len(doc.entities), 3)
            for entity in doc.entities:
                self.assertIsNotNone(entity.name)
                self.assertIsNotNone(entity.language)
                self.assertIsNotNone(entity.data_source_entity_id)
                self.assertIsNotNone(entity.url)
                self.assertIsNotNone(entity.data_source)
                self.assertIsNotNone(entity.matches)
                for match in entity.matches:
                    self.assertIsNotNone(match.offset)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_passing_only_string(self, client):
        docs = [
            u"Microsoft was founded by Bill Gates and Paul Allen",
            u"Microsoft fue fundado por Bill Gates y Paul Allen",
            u""
        ]

        response = client.recognize_linked_entities(docs)
        self.assertEqual(len(response[0].entities), 3)
        self.assertEqual(len(response[1].entities), 3)
        self.assertTrue(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_input_with_some_errors(self, client):
        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        response = client.recognize_linked_entities(docs)
        self.assertTrue(response[0].is_error)
        self.assertFalse(response[1].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_input_with_all_errors(self, client):
        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "Spanish", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        response = client.recognize_linked_entities(docs)
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_too_many_documents(self, client):
        docs = ["One", "Two", "Three", "Four", "Five", "Six"]

        with pytest.raises(HttpResponseError) as excinfo:
            client.recognize_linked_entities(docs)
        assert excinfo.value.status_code == 400
        assert excinfo.value.error.code == "InvalidDocumentBatch"
        assert "Batch request contains too many records" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_output_same_order_as_input(self, client):
        docs = [
            TextDocumentInput(id="1", text="one"),
            TextDocumentInput(id="2", text="two"),
            TextDocumentInput(id="3", text="three"),
            TextDocumentInput(id="4", text="four"),
            TextDocumentInput(id="5", text="five")
        ]

        response = client.recognize_linked_entities(docs)

        for idx, doc in enumerate(response):
            self.assertEqual(str(idx + 1), doc.id)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"text_analytics_account_key": ""})
    def test_empty_credential_class(self, client):
        with self.assertRaises(ClientAuthenticationError):
            response = client.recognize_linked_entities(
                ["This is written in English."]
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"text_analytics_account_key": "xxxxxxxxxxxx"})
    def test_bad_credentials(self, client):
        with self.assertRaises(ClientAuthenticationError):
            response = client.recognize_linked_entities(
                ["This is written in English."]
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_bad_document_input(self, client):
        docs = "This is the wrong type"

        with self.assertRaises(TypeError):
            response = client.recognize_linked_entities(docs)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_mixing_inputs(self, client):
        docs = [
            {"id": "1", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
            TextDocumentInput(id="2", text="I did not like the hotel we stayed at. It was too expensive."),
            u"You cannot mix string input with the above inputs"
        ]
        with self.assertRaises(TypeError):
            response = client.recognize_linked_entities(docs)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_out_of_order_ids(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = client.recognize_linked_entities(docs)
        in_order = ["56", "0", "22", "19", "1"]
        for idx, resp in enumerate(response):
            self.assertEqual(resp.id, in_order[idx])

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_show_stats_and_model_version(self, client):
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

        response = client.recognize_linked_entities(
            docs,
            show_stats=True,
            model_version="latest",
            raw_response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_batch_size_over_limit(self, client):
        docs = [u"hello world"] * 1050
        with self.assertRaises(HttpResponseError):
            response = client.recognize_linked_entities(docs)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_whole_batch_language_hint(self, client):
        def callback(resp):
            language_str = "\"language\": \"fr\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed at. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        response = client.recognize_linked_entities(docs, language="fr", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_whole_batch_dont_use_language_hint(self, client):
        def callback(resp):
            language_str = "\"language\": \"\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed at. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        response = client.recognize_linked_entities(docs, language="", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_per_item_dont_use_language_hint(self, client):
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

        response = client.recognize_linked_entities(docs, raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_whole_batch_language_hint_and_obj_input(self, client):
        def callback(resp):
            language_str = "\"language\": \"de\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian."),
            TextDocumentInput(id="4", text="Este es un document escrito en Español."),
            TextDocumentInput(id="3", text="猫は幸せ"),
        ]

        response = client.recognize_linked_entities(docs, language="de", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_whole_batch_language_hint_and_obj_per_item_hints(self, client):
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

        response = client.recognize_linked_entities(docs, language="en", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_whole_batch_language_hint_and_dict_per_item_hints(self, client):
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

        response = client.recognize_linked_entities(docs, language="en", raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"default_language": "es"})
    def test_client_passed_default_language_hint(self, client):
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

        response = client.recognize_linked_entities(docs, raw_response_hook=callback)
        response = client.recognize_linked_entities(docs, language="en", raw_response_hook=callback_2)
        response = client.recognize_linked_entities(docs, raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_invalid_language_hint_method(self, client):
        response = client.recognize_linked_entities(
            ["This should fail because we're passing in an invalid language hint"], language="notalanguage"
        )
        self.assertEqual(response[0].error.code, 'UnsupportedLanguageCode')

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_invalid_language_hint_docs(self, client):
        response = client.recognize_linked_entities(
            [{"id": "1", "language": "notalanguage", "text": "This should fail because we're passing in an invalid language hint"}]
        )
        self.assertEqual(response[0].error.code, 'UnsupportedLanguageCode')

    @GlobalTextAnalyticsAccountPreparer()
    def test_rotate_subscription_key(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        credential = AzureKeyCredential(text_analytics_account_key)
        client = TextAnalyticsClient(text_analytics_account, credential)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.recognize_linked_entities(docs)
        self.assertIsNotNone(response)

        credential.update("xxx")  # Make authentication fail
        with self.assertRaises(ClientAuthenticationError):
            response = client.recognize_linked_entities(docs)

        credential.update(text_analytics_account_key)  # Authenticate successfully again
        response = client.recognize_linked_entities(docs)
        self.assertIsNotNone(response)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_user_agent(self, client):
        def callback(resp):
            self.assertIn("azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                VERSION, platform.python_version(), platform.platform()),
                resp.http_request.headers["User-Agent"]
            )

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.recognize_linked_entities(docs, raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_document_attribute_error_no_result_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        response = client.recognize_linked_entities(docs)

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
                'InvalidDocument - Document text is empty.\n'
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_document_attribute_error_nonexistent_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        response = client.recognize_linked_entities(docs)

        # Attribute not found on DocumentError or result obj, default behavior/message
        try:
            entities = response[0].attribute_not_on_result_or_error
        except AttributeError as default_behavior:
            self.assertEqual(
                default_behavior.args[0],
                '\'DocumentError\' object has no attribute \'attribute_not_on_result_or_error\''
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_bad_model_version_error(self, client):
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        try:
            result = client.recognize_linked_entities(docs, model_version="bad")
        except HttpResponseError as err:
            self.assertEqual(err.error.code, "ModelVersionIncorrect")
            self.assertIsNotNone(err.error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_document_errors(self, client):
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": text}]

        doc_errors = client.recognize_linked_entities(docs)
        self.assertEqual(doc_errors[0].error.code, "InvalidDocument")
        self.assertIsNotNone(doc_errors[0].error.message)
        self.assertEqual(doc_errors[1].error.code, "UnsupportedLanguageCode")
        self.assertIsNotNone(doc_errors[1].error.message)
        self.assertEqual(doc_errors[2].error.code, "InvalidDocument")
        self.assertIsNotNone(doc_errors[2].error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_document_warnings(self, client):
        # No warnings actually returned for recognize_linked_entities. Will update when they add
        docs = [
            {"id": "1", "text": "This won't actually create a warning :'("},
        ]

        result = client.recognize_linked_entities(docs)
        for doc in result:
            doc_warnings = doc.warnings
            self.assertEqual(len(doc_warnings), 0)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_not_passing_list_for_docs(self, client):
        docs = {"id": "1", "text": "hello world"}
        with pytest.raises(TypeError) as excinfo:
            client.recognize_linked_entities(docs)
        assert "Input documents cannot be a dict" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_missing_input_records_error(self, client):
        docs = []
        with pytest.raises(ValueError) as excinfo:
            client.recognize_linked_entities(docs)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_passing_none_docs(self, client):
        with pytest.raises(ValueError) as excinfo:
            client.recognize_linked_entities(None)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_duplicate_ids_error(self, client):
        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed at."}]
        try:
            result = client.recognize_linked_entities(docs)
        except HttpResponseError as err:
            self.assertEqual(err.error.code, "InvalidDocument")
            self.assertIsNotNone(err.error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_batch_size_over_limit_error(self, client):
        # Batch size over limit
        docs = [u"hello world"] * 1001
        try:
            response = client.recognize_linked_entities(docs)
        except HttpResponseError as err:
            self.assertEqual(err.error.code, "InvalidDocumentBatch")
            self.assertIsNotNone(err.error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_language_kwarg_spanish(self, client):
        def callback(response):
            language_str = "\"language\": \"es\""
            self.assertEqual(response.http_request.body.count(language_str), 1)
            self.assertIsNotNone(response.model_version)
            self.assertIsNotNone(response.statistics)

        res = client.recognize_linked_entities(
            documents=["Bill Gates is the CEO of Microsoft."],
            model_version="latest",
            show_stats=True,
            language="es",
            raw_response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_pass_cls(self, client):
        def callback(pipeline_response, deserialized, _):
            return "cls result"
        res = client.recognize_linked_entities(
            documents=["Test passing cls to endpoint"],
            cls=callback
        )
        assert res == "cls result"

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_offset(self, client):
        result = client.recognize_linked_entities(["Microsoft was founded by Bill Gates and Paul Allen"])
        entities = result[0].entities

        # the entities are being returned in a non-sequential order by the service
        microsoft_entity = [entity for entity in entities if entity.name == "Microsoft"][0]
        bill_gates_entity = [entity for entity in entities if entity.name == "Bill Gates"][0]
        paul_allen_entity = [entity for entity in entities if entity.name == "Paul Allen"][0]

        self.assertEqual(microsoft_entity.matches[0].offset, 0)

        self.assertEqual(bill_gates_entity.matches[0].offset, 25)

        self.assertEqual(paul_allen_entity.matches[0].offset, 40)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    def test_no_offset_v3_linked_entity_match(self, client):
        result = client.recognize_linked_entities(["Microsoft was founded by Bill Gates and Paul Allen"])
        entities = result[0].entities

        self.assertIsNone(entities[0].matches[0].offset)
        self.assertIsNone(entities[1].matches[0].offset)
        self.assertIsNone(entities[2].matches[0].offset)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    def test_string_index_type_not_fail_v3(self, client):
        # make sure that the addition of the string_index_type kwarg for v3.1-preview doesn't
        # cause v3.0 calls to fail
        client.recognize_linked_entities(["please don't fail"])

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_bing_id(self, client):
        result = client.recognize_linked_entities(["Microsoft was founded by Bill Gates and Paul Allen"])
        for doc in result:
            for entity in doc.entities:
                assert entity.bing_entity_search_api_id  # this checks if it's None and if it's empty

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    def test_string_index_type_explicit_fails_v3(self, client):
        with pytest.raises(ValueError) as excinfo:
            client.recognize_linked_entities(["this should fail"], string_index_type="UnicodeCodePoint")
        assert "'string_index_type' is only available for API version V3_1_PREVIEW and up" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_default_string_index_type_is_UnicodeCodePoint(self, client):
        def callback(response):
            self.assertEqual(response.http_request.query["stringIndexType"], "UnicodeCodePoint")

        res = client.recognize_linked_entities(
            documents=["Hello world"],
            raw_response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_explicit_set_string_index_type(self, client):
        def callback(response):
            self.assertEqual(response.http_request.query["stringIndexType"], "TextElements_v8")

        res = client.recognize_linked_entities(
            documents=["Hello world"],
            string_index_type="TextElements_v8",
            raw_response_hook=callback
        )
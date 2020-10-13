# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import platform
import functools
import itertools

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

class TestHealth(TextAnalyticsTest):

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_no_single_input(self, client):
        with self.assertRaises(TypeError):
            response = client.begin_health("hello world").result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_all_successful_passing_dict(self, client):
        docs = [{"id": "1", "language": "en", "text": "Patient does not suffer from high blood pressure."},
                {"id": "2", "language": "en", "text": "Prescribed 100mg ibuprofen, taken twice daily."}]

        response = client.begin_health(docs, show_stats=True).result()

        for doc in response:
            self.assertIsNotNone(doc.id)
            self.assertIsNotNone(doc.statistics)
            self.assertIsNotNone(doc.entities)
            self.assertIsNotNone(doc.relations)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_all_successful_passing_text_document_input(self, client):
        docs = [
            TextDocumentInput(id="1", text="Patient does not suffer from high blood pressure."),
            TextDocumentInput(id="2", text="Prescribed 100mg ibuprofen, taken twice daily."),
        ]

        response = client.begin_health(docs).result()

        for doc in response:
            self.assertIsNotNone(doc.id)
            self.assertIsNotNone(doc.statistics)
            self.assertIsNotNone(doc.entities)
            self.assertIsNotNone(doc.relations)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_passing_only_string(self, client):
        docs = [
            u"Patient does not suffer from high blood pressure.",
            u"Prescribed 100mg ibuprofen, taken twice daily.",
            u""
        ]

        response = client.begin_health(docs).result()

        for i in range(2):
            self.assertIsNotNone(response[i].id)
            self.assertIsNotNone(response[i].statistics)
            self.assertIsNotNone(response[i].entities)
            self.assertIsNotNone(response[i].relations)

        self.assertTrue(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_input_with_some_errors(self, client):
        docs = [{"id": "1", "language": "en", "text": ""},
                {"id": "2", "language": "english", "text": "Patient does not suffer from high blood pressure."},
                {"id": "3", "language": "en", "text": "Prescribed 100mg ibuprofen, taken twice daily."}]

        response = client.begin_health(docs).result()
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_input_with_all_errors(self, client):
        docs = [{"id": "1", "language": "en", "text": ""},
                {"id": "2", "language": "english", "text": "Patient does not suffer from high blood pressure."},
                {"id": "3", "language": "en", "text": ""}]

        response = client.begin_health(docs).result()
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)
        self.assertTrue(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_too_many_documents(self, client):
        docs = list(itertools.repeat("input document", 1001))  # Maximum number of documents per request is 1000

        with pytest.raises(HttpResponseError) as excinfo:
            client.begin_health(docs)
        assert excinfo.value.status_code == 400
        assert excinfo.value.error.code == "InvalidDocumentBatch"
        assert "Batch request contains too many records" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_payload_too_large(self, client):
        large_doc = "RECORD #333582770390100 | MH | 85986313 | | 054351 | 2/14/2001 12:00:00 AM | \
            CORONARY ARTERY DISEASE | Signed | DIS | Admission Date: 5/22/2001 \
            Report Status: Signed Discharge Date: 4/24/2001 ADMISSION DIAGNOSIS: \
            CORONARY ARTERY DISEASE. HISTORY OF PRESENT ILLNESS: \
            The patient is a 54-year-old gentleman with a history of progressive angina over the past several months. \
            The patient had a cardiac catheterization in July of this year revealing total occlusion of the RCA and \
            50% left main disease , with a strong family history of coronary artery disease with a brother dying at \
            the age of 52 from a myocardial infarction and another brother who is status post coronary artery bypass grafting. \
            The patient had a stress echocardiogram done on July , 2001 , which showed no wall motion abnormalities ,\
            but this was a difficult study due to body habitus. The patient went for six minutes with minimal ST depressions \
            in the anterior lateral leads , thought due to fatigue and wrist pain , his anginal equivalent. Due to the patient's \
            increased symptoms and family history and history left main disease with total occasional of his RCA was referred \
            for revascularization with open heart surgery."
        docs = list(itertools.repeat(large_doc, 500))

        with pytest.raises(HttpResponseError) as excinfo:
            client.begin_health(docs)
        assert excinfo.value.status_code == 413
        assert excinfo.value.error.code == "BodyTooLarge"
        assert "Request Payload sent is too large to be processed. Limit request size to: 524288" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_document_warnings(self, client):
        # TODO: reproduce a warnings scenario for implementation
        docs = [
            {"id": "1", "text": "This won't actually create a warning :'("},
        ]

        result = client.analyze_sentiment(docs)
        for doc in result:
            doc_warnings = doc.warnings
            self.assertEqual(len(doc_warnings), 0)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_output_same_order_as_input(self, client):
        docs = [
            TextDocumentInput(id="1", text="one"),
            TextDocumentInput(id="2", text="two"),
            TextDocumentInput(id="3", text="three"),
            TextDocumentInput(id="4", text="four"),
            TextDocumentInput(id="5", text="five")
        ]

        response = client.begin_health(docs).result()

        for idx, doc in enumerate(response):
            self.assertEqual(str(idx + 1), doc.id)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"text_analytics_account_key": ""})
    def test_empty_credential_class(self, client):
        with self.assertRaises(ClientAuthenticationError):
            response = client.begin_health(
                ["This is written in English."]
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"text_analytics_account_key": "xxxxxxxxxxxx"})
    def test_bad_credentials(self, client):
        with self.assertRaises(ClientAuthenticationError):
            response = client.begin_health(
                ["This is written in English."]
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_bad_document_input(self, client):
        docs = "This is the wrong type"

        with self.assertRaises(TypeError):
            response = client.begin_health(docs)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_mixing_inputs(self, client):
        docs = [
            {"id": "1", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
            TextDocumentInput(id="2", text="I did not like the hotel we stayed at. It was too expensive."),
            u"You cannot mix string input with the above inputs"
        ]
        with self.assertRaises(TypeError):
            response = client.begin_health(docs)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_out_of_order_ids(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = client.begin_health(docs).result()
        in_order = ["56", "0", "22", "19", "1"]
        for idx, resp in enumerate(response):
            self.assertEqual(resp.id, in_order[idx])

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
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

        response = client.begin_health(
            docs,
            show_stats=True,
            model_version="latest",
            raw_response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_whole_batch_language_hint(self, client):
        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed at. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        response = client.begin_health(docs, language="en").result()
        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_whole_batch_dont_use_language_hint(self, client):
        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed at. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        response = client.begin_health(docs, language="").result()
        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_per_item_dont_use_language_hint(self, client):
        docs = [{"id": "1", "language": "", "text": "I will go to the park."},
                {"id": "2", "language": "", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.begin_health(docs).result()
        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_whole_batch_language_hint_and_obj_input(self, client):
        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian."),
            TextDocumentInput(id="4", text="Este es un document escrito en Español."),
            TextDocumentInput(id="3", text="猫は幸せ"),
        ]

        response = client.begin_health(docs, language="en").result()
        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_whole_batch_language_hint_and_dict_input(self, client):
        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.begin_health(docs, language="en").result()
        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_whole_batch_language_hint_and_obj_per_item_hints(self, client):
        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian.", language="en"),
            TextDocumentInput(id="2", text="猫は幸せ"),
        ]

        response = client.begin_health(docs, language="en").result()
        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_whole_batch_language_hint_and_dict_per_item_hints(self, client):
        docs = [{"id": "1", "language": "", "text": "I will go to the park."},
                {"id": "2", "language": "", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.begin_health(docs, language="en").result()
        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"default_language": "en"})
    def test_client_passed_default_language_hint(self, client):
        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.begin_health(docs).result()
        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_invalid_language_hint_method(self, client):
        response = client.begin_health(
            ["This should fail because we're passing in an invalid language hint"], language="notalanguage"
        ).result()
        self.assertEqual(response[0].error.code, 'UnsupportedLanguageCode')

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_invalid_language_hint_docs(self, client):
        response = client.begin_health(
            [{"id": "1", "language": "notalanguage", "text": "This should fail because we're passing in an invalid language hint"}]
        ).result()
        self.assertEqual(response[0].error.code, 'UnsupportedLanguageCode')

    @GlobalTextAnalyticsAccountPreparer()
    def test_rotate_subscription_key(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        credential = AzureKeyCredential(text_analytics_account_key)
        client = TextAnalyticsClient(text_analytics_account, credential)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.begin_health(docs)
        self.assertIsNotNone(response)

        credential.update("xxx")  # Make authentication fail
        with self.assertRaises(ClientAuthenticationError):
            response = client.begin_health(docs)

        credential.update(text_analytics_account_key)  # Authenticate successfully again
        response = client.begin_health(docs)
        self.assertIsNotNone(response)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_user_agent(self, client):  # TODO: verify
        def callback(resp):
            self.assertIn("azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                VERSION, platform.python_version(), platform.platform()),
                resp.http_request.headers["User-Agent"]
            )

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.begin_health(docs, raw_response_hook=callback)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_document_attribute_error_no_result_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        response = client.begin_health(docs).result()

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
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_document_attribute_error_nonexistent_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        response = client.begin_health(docs).result()

        # Attribute not found on DocumentError or result obj, default behavior/message
        try:
            health = response[0].attribute_not_on_result_or_error
        except AttributeError as default_behavior:
            self.assertEqual(
                default_behavior.args[0],
                '\'DocumentError\' object has no attribute \'attribute_not_on_result_or_error\''
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_bad_model_version_error(self, client):
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        try:
            result = client.begin_health(docs, model_version="bad").result()
        except HttpResponseError as err:
            self.assertEqual(err.error.code, "ModelVersionIncorrect")
            self.assertIsNotNone(err.error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_document_errors(self, client):
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": text}]

        doc_errors = client.begin_health(docs).result()
        self.assertEqual(doc_errors[0].error.code, "InvalidDocument")
        self.assertIsNotNone(doc_errors[0].error.message)
        self.assertEqual(doc_errors[1].error.code, "UnsupportedLanguageCode")
        self.assertIsNotNone(doc_errors[1].error.message)
        self.assertEqual(doc_errors[2].error.code, "InvalidDocument")
        self.assertIsNotNone(doc_errors[2].error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_not_passing_list_for_docs(self, client):
        docs = {"id": "1", "text": "hello world"}
        with pytest.raises(TypeError) as excinfo:
            client.begin_health(docs)
        assert "Input documents cannot be a dict" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_missing_input_records_error(self, client):
        docs = []
        with pytest.raises(ValueError) as excinfo:
            client.begin_health(docs)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_passing_none_docs(self, client):
        with pytest.raises(ValueError) as excinfo:
            client.begin_health(None)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_duplicate_ids_error(self, client):
        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed at."}]
        try:
            result = client.begin_health(docs)
        except HttpResponseError as err:
            self.assertEqual(err.error.code, "InvalidDocument")
            self.assertIsNotNone(err.error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_2_PREVIEW,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "text_analytics_account": "https://cognitiveusw2dev.azure-api.net"
    })
    def test_pass_cls(self, client):
        def callback(pipeline_response, deserialized, _):
            return "cls result"
        res = client.begin_health(
            documents=["Test passing cls to endpoint"],
            cls=callback
        ).result()
        assert res == "cls result"

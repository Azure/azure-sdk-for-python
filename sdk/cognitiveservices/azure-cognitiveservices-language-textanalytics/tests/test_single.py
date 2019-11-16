# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from devtools_testutils import ResourceGroupPreparer
from devtools_testutils.cognitiveservices_testcase import CognitiveServiceTest, CognitiveServicesAccountPreparer
from azure.cognitiveservices.language.textanalytics import (
    single_detect_language,
    single_recognize_entities,
    single_recognize_pii_entities,
    single_recognize_linked_entities,
    single_analyze_sentiment,
    single_extract_key_phrases
)


class TextAnalyticsTest(CognitiveServiceTest):

    # single_detect_language ------------------------------------------------------

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_successful_single_language_detection(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        response = single_detect_language(
            endpoint=cognitiveservices_account,
            credential=cognitiveservices_account_key,
            text="This is written in English.",
            country_hint="US"
        )

        self.assertEqual(response.name, "English")
        self.assertEqual(response.iso6391_name, "en")
        self.assertEqual(response.score, 1.0)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_language_detection_bad_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = single_detect_language(
                endpoint=cognitiveservices_account,
                credential="xxxxxxxxxxxx",
                text="This is written in English.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_language_detection_empty_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = single_detect_language(
                endpoint=cognitiveservices_account,
                credential="",
                text="This is written in English.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_language_detection_bad_type_for_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(TypeError):
            response = single_detect_language(
                endpoint=cognitiveservices_account,
                credential=[],
                text="This is written in English.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_language_detection_none_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ValueError):
            response = single_detect_language(
                endpoint=cognitiveservices_account,
                credential=None,
                text="This is written in English.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_language_detection_too_many_chars(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text = ""
        for _ in range(5121):
            text += "x"
        with self.assertRaises(HttpResponseError) as err:
            response = single_detect_language(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text=text,
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_language_detection_empty_text_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(HttpResponseError):
            response = single_detect_language(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text="",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_language_detection_non_text_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(TypeError):
            response = single_detect_language(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text={"id": "1", "text": "hello world"}
            )

    # TODO: Will fail with "At least one document missing an Id" until service bug is fixed
    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_language_detection_bad_country_hint(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        pytest.skip("waiting on service bug")
        with self.assertRaises(HttpResponseError):
            response = single_detect_language(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text="This is written in English.",
                country_hint="United States"
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_language_detection_get_stats_and_model_version(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        def callback(resp):
            self.assertIsNotNone(resp.statistics)
            self.assertEqual(resp.model_version, "latest")

        response = single_detect_language(
            endpoint=cognitiveservices_account,
            credential=cognitiveservices_account_key,
            text="Este es un document escrito en Español.",
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )

    # single_recognize_entities ------------------------------------------------------

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_successful_single_recognize_entities(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        response = single_recognize_entities(
            endpoint=cognitiveservices_account,
            credential=cognitiveservices_account_key,
            text="Microsoft was founded by Bill Gates.",
            language="en"
        )

        self.assertEqual(response[0].text, "Microsoft")
        self.assertEqual(response[1].text, "Bill Gates")
        for entity in response:
            self.assertIsNotNone(entity.type)
            self.assertIsNotNone(entity.offset)
            self.assertIsNotNone(entity.length)
            self.assertIsNotNone(entity.score)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_entities_bad_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = single_recognize_entities(
                endpoint=cognitiveservices_account,
                credential="xxxxxxxxxxxx",
                text="Microsoft was founded by Bill Gates.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_entities_empty_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = single_recognize_entities(
                endpoint=cognitiveservices_account,
                credential="",
                text="Microsoft was founded by Bill Gates.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_entities_bad_type_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(TypeError):
            response = single_recognize_entities(
                endpoint=cognitiveservices_account,
                credential=[],
                text="Microsoft was founded by Bill Gates.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_entities_none_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ValueError):
            response = single_recognize_entities(
                endpoint=cognitiveservices_account,
                credential=None,
                text="Microsoft was founded by Bill Gates.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_entities_too_many_chars(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text = ""
        for _ in range(5121):
            text += "x"
        with self.assertRaises(HttpResponseError):
            response = single_recognize_entities(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text=text,
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_entities_empty_text_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(HttpResponseError):
            response = single_recognize_entities(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text="",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_entities_non_text_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(TypeError):
            response = single_recognize_entities(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text={"id": "1", "text": "hello world"}
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_entities_bad_language_hint(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(HttpResponseError):
            response = single_recognize_entities(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text="Microsoft was founded by Bill Gates.",
                language="English"
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_entities_get_stats_and_model_version(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        def callback(resp):
            self.assertIsNotNone(resp.statistics)
            self.assertEqual(resp.model_version, "latest")

        response = single_recognize_entities(
            endpoint=cognitiveservices_account,
            credential=cognitiveservices_account_key,
            text="Microsoft was founded by Bill Gates.",
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )

    # single_recognize_pii_entities ------------------------------------------------------

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_successful_single_recognize_pii_entities(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        response = single_recognize_pii_entities(
            endpoint=cognitiveservices_account,
            credential=cognitiveservices_account_key,
            text="My SSN is 555-55-5555",
            language="en"
        )

        self.assertEqual(response[0].text, "555-55-5555")
        for entity in response:
            self.assertIsNotNone(entity.type)
            self.assertIsNotNone(entity.offset)
            self.assertIsNotNone(entity.length)
            self.assertIsNotNone(entity.score)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_pii_entities_bad_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = single_recognize_pii_entities(
                endpoint=cognitiveservices_account,
                credential="xxxxxxxxxxxx",
                text="My SSN is 555-55-5555",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_pii_entities_empty_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = single_recognize_pii_entities(
                endpoint=cognitiveservices_account,
                credential="",
                text="My SSN is 555-55-5555",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_pii_entities_bad_type_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(TypeError):
            response = single_recognize_pii_entities(
                endpoint=cognitiveservices_account,
                credential=[],
                text="My SSN is 555-55-5555",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_pii_entities_none_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ValueError):
            response = single_recognize_pii_entities(
                endpoint=cognitiveservices_account,
                credential=None,
                text="My SSN is 555-55-5555",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_pii_entities_too_many_chars(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text = ""
        for _ in range(5121):
            text += "x"
        with self.assertRaises(HttpResponseError):
            response = single_recognize_pii_entities(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text=text,
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_pii_entities_empty_text_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(HttpResponseError):
            response = single_recognize_pii_entities(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text="",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_pii_entities_non_text_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(TypeError):
            response = single_recognize_pii_entities(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text={"id": "1", "text": "hello world"}
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_pii_entities_bad_language_hint(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(HttpResponseError):
            response = single_recognize_pii_entities(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text="My SSN is 555-55-5555",
                language="English"
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_pii_entities_get_stats_and_model_version(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        def callback(resp):
            self.assertIsNotNone(resp.statistics)
            self.assertEqual(resp.model_version, "latest")

        response = single_recognize_pii_entities(
            endpoint=cognitiveservices_account,
            credential=cognitiveservices_account_key,
            text="My SSN is 555-55-5555",
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )

    # single_recognize_linked_entities ------------------------------------------------------

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_successful_single_recognize_linked_entities(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        response = single_recognize_linked_entities(
            endpoint=cognitiveservices_account,
            credential=cognitiveservices_account_key,
            text="Microsoft was founded by Bill Gates.",
            language="en"
        )

        self.assertEqual(response[0].name, "Bill Gates")
        self.assertEqual(response[1].name, "Microsoft")
        for entity in response:
            self.assertIsNotNone(entity.matches)
            self.assertIsNotNone(entity.language)
            self.assertIsNotNone(entity.id)
            self.assertIsNotNone(entity.url)
            self.assertIsNotNone(entity.data_source)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_linked_entities_bad_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = single_recognize_linked_entities(
                endpoint=cognitiveservices_account,
                credential="xxxxxxxxxxxx",
                text="Microsoft was founded by Bill Gates.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_linked_entities_empty_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = single_recognize_linked_entities(
                endpoint=cognitiveservices_account,
                credential="",
                text="Microsoft was founded by Bill Gates.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_linked_entities_bad_type_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(TypeError):
            response = single_recognize_linked_entities(
                endpoint=cognitiveservices_account,
                credential=[],
                text="Microsoft was founded by Bill Gates.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_linked_entities_none_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ValueError):
            response = single_recognize_linked_entities(
                endpoint=cognitiveservices_account,
                credential=None,
                text="Microsoft was founded by Bill Gates.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_linked_entities_too_many_chars(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text = ""
        for _ in range(5121):
            text += "x"
        with self.assertRaises(HttpResponseError):
            response = single_recognize_linked_entities(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text=text,
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_linked_entities_empty_text_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(HttpResponseError):
            response = single_recognize_linked_entities(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text="",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_linked_entities_non_text_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(TypeError):
            response = single_recognize_linked_entities(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text={"id": "1", "text": "hello world"}
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_linked_entities_bad_language_hint(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(HttpResponseError):
            response = single_recognize_linked_entities(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text="Microsoft was founded by Bill Gates.",
                language="English"
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_recognize_linked_entities_get_stats_and_model_version(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        def callback(resp):
            self.assertIsNotNone(resp.statistics)
            self.assertEqual(resp.model_version, "latest")

        response = single_recognize_linked_entities(
            endpoint=cognitiveservices_account,
            credential=cognitiveservices_account_key,
            text="Microsoft was founded by Bill Gates.",
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )

    # single_extract_key_phrases ------------------------------------------------------

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_successful_single_extract_key_phrases(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        response = single_extract_key_phrases(
            endpoint=cognitiveservices_account,
            credential=cognitiveservices_account_key,
            text="Microsoft was founded by Bill Gates.",
            language="en"
        )

        self.assertIn("Microsoft", response)
        self.assertIn("Bill Gates", response)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_extract_key_phrases_bad_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = single_extract_key_phrases(
                endpoint=cognitiveservices_account,
                credential="xxxxxxxxxxxx",
                text="Microsoft was founded by Bill Gates.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_extract_key_phrases_empty_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = single_extract_key_phrases(
                endpoint=cognitiveservices_account,
                credential="",
                text="Microsoft was founded by Bill Gates.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_extract_key_phrases_bad_type_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(TypeError):
            response = single_extract_key_phrases(
                endpoint=cognitiveservices_account,
                credential=[],
                text="Microsoft was founded by Bill Gates.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_extract_key_phrases_none_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ValueError):
            response = single_extract_key_phrases(
                endpoint=cognitiveservices_account,
                credential=None,
                text="Microsoft was founded by Bill Gates.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_extract_key_phrases_too_many_chars(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text = ""
        for _ in range(5121):
            text += "x"
        with self.assertRaises(HttpResponseError):
            response = single_extract_key_phrases(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text=text,
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_extract_key_phrases_empty_text_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(HttpResponseError):
            response = single_extract_key_phrases(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text="",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_extract_key_phrases_non_text_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(TypeError):
            response = single_extract_key_phrases(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text={"id": "1", "text": "hello world"}
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_extract_key_phrases_bad_language_hint(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(HttpResponseError):
            response = single_extract_key_phrases(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text="Microsoft was founded by Bill Gates.",
                language="English"
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_extract_key_phrases_get_stats_and_model_version(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        def callback(resp):
            self.assertIsNotNone(resp.statistics)
            self.assertEqual(resp.model_version, "latest")

        response = single_extract_key_phrases(
            endpoint=cognitiveservices_account,
            credential=cognitiveservices_account_key,
            text="Microsoft was founded by Bill Gates.",
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )

    # single_analyze_sentiment ------------------------------------------------------

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_successful_single_analyze_sentiment(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        response = single_analyze_sentiment(
            endpoint=cognitiveservices_account,
            credential=cognitiveservices_account_key,
            text="I was unhappy with the food at the restaurant.",
            language="en"
        )

        self.assertIsNotNone(response.id)
        self.assertEqual(response.sentiment, "negative")
        self.assertIsNotNone(response.document_scores)
        self.assertIsNotNone(response.sentences)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_analyze_sentiment_bad_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = single_analyze_sentiment(
                endpoint=cognitiveservices_account,
                credential="xxxxxxxxxxxx",
                text="I was unhappy with the food at the restaurant.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_analyze_sentiment_empty_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = single_analyze_sentiment(
                endpoint=cognitiveservices_account,
                credential="",
                text="I was unhappy with the food at the restaurant.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_analyze_sentiment_bad_type_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(TypeError):
            response = single_analyze_sentiment(
                endpoint=cognitiveservices_account,
                credential=[],
                text="I was unhappy with the food at the restaurant.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_analyze_sentiment_none_credentials(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(ValueError):
            response = single_analyze_sentiment(
                endpoint=cognitiveservices_account,
                credential=None,
                text="I was unhappy with the food at the restaurant.",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_analyze_sentiment_too_many_chars(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text = ""
        for _ in range(5121):
            text += "x"
        with self.assertRaises(HttpResponseError):
            response = single_analyze_sentiment(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text=text,
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_analyze_sentiment_empty_text_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(HttpResponseError):
            response = single_analyze_sentiment(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text="",
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_analyze_sentiment_non_text_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(TypeError):
            response = single_analyze_sentiment(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text={"id": "1", "text": "hello world"}
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_analyze_sentiment_bad_language_hint(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        with self.assertRaises(HttpResponseError):
            response = single_analyze_sentiment(
                endpoint=cognitiveservices_account,
                credential=cognitiveservices_account_key,
                text="I was unhappy with the food at the restaurant.",
                language="English"
            )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_single_analyze_sentiment_get_stats_and_model_version(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        def callback(resp):
            self.assertIsNotNone(resp.statistics)
            self.assertEqual(resp.model_version, "latest")

        response = single_analyze_sentiment(
            endpoint=cognitiveservices_account,
            credential=cognitiveservices_account_key,
            text="I was unhappy with the food at the restaurant.",
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )

# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from azure.core.exceptions import HttpResponseError
from devtools_testutils import ResourceGroupPreparer
from devtools_testutils.cognitiveservices_testcase import CognitiveServiceTest, CognitiveServicesAccountPreparer
from azure.cognitiveservices.language.textanalytics import (
    TextAnalyticsClient,
    LanguageInput,
    MultiLanguageInput
)


class BatchTextAnalyticsTest(CognitiveServiceTest):

    @pytest.mark.live_test_only
    def test_active_directory_auth(self):
        token = self.generate_oauth_token()
        endpoint = self.get_oauth_endpoint()
        text_analytics = TextAnalyticsClient(endpoint, token)

        docs = [{"id": "1", "text": "I should take my cat to the veterinarian."},
                {"id": "2", "text": "Este es un document escrito en Español."},
                {"id": "3", "text": "猫は幸せ"},
                {"id": "4", "text": "Fahrt nach Stuttgart und dann zum Hotel zu Fu."}]

        response = text_analytics.detect_language(docs)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_successful_detect_language(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "text": "I should take my cat to the veterinarian."},
                {"id": "2", "text": "Este es un document escrito en Español."},
                {"id": "3", "text": "猫は幸せ"},
                {"id": "4", "text": "Fahrt nach Stuttgart und dann zum Hotel zu Fu."}]

        response = text_analytics.detect_language(docs)

        self.assertEqual(response[0].detected_languages[0].name, "English")
        self.assertEqual(response[1].detected_languages[0].name, "Spanish")
        self.assertEqual(response[2].detected_languages[0].name, "Japanese")
        self.assertEqual(response[3].detected_languages[0].name, "German")

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_some_errors_detect_language(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "country_hint": "United States", "text": "I should take my cat to the veterinarian."},
                {"id": "2", "text": "Este es un document escrito en Español."},
                {"id": "3", "text": ""},
                {"id": "4", "text": "Fahrt nach Stuttgart und dann zum Hotel zu Fu."}]

        response = text_analytics.detect_language(docs)

        self.assertTrue(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertTrue(response[2].is_error)
        self.assertFalse(response[3].is_error)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_all_errors_detect_language(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "text": ""},
                {"id": "3", "text": ""},
                {"id": "4", "text": text}]

        response = text_analytics.detect_language(docs)

        for resp in response:
            self.assertTrue(resp.is_error)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_successful_recognize_entities(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975."},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen el 4 de abril de 1975."},
                {"id": "3", "language": "de", "text": "Microsoft wurde am 4. April 1975 von Bill Gates und Paul Allen gegründet."}]

        response = text_analytics.recognize_entities(docs)
        for doc in response:
            self.assertEqual(len(doc.entities), 4)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_some_errors_recognize_entities(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975."},
                {"id": "2", "language": "Spanish", "text": "Hola"},
                {"id": "3", "language": "de", "text": ""}]

        response = text_analytics.recognize_entities(docs)
        self.assertFalse(response[0].is_error)
        self.assertTrue(response[1].is_error)
        self.assertTrue(response[2].is_error)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_all_errors_recognize_entities(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "Spanish", "text": "Hola"},
                {"id": "3", "language": "de", "text": ""}]

        response = text_analytics.recognize_entities(docs)
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)
        self.assertTrue(response[2].is_error)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_successful_recognize_pii_entities(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "text": "My SSN is 555-55-5555."},
                {"id": "2", "text": "Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check."},
                {"id": "3", "text": "Is 998.214.865-68 your Brazilian CPF number?"}]

        response = text_analytics.recognize_pii_entities(docs)
        self.assertEqual(response[0].entities[0].text, "555-55-5555")
        self.assertEqual(response[0].entities[0].type, "U.S. Social Security Number (SSN)")
        self.assertEqual(response[1].entities[0].text, "111000025")
        self.assertEqual(response[1].entities[0].type, "ABA Routing Number")
        self.assertEqual(response[2].entities[0].text, "998.214.865-68")
        self.assertEqual(response[2].entities[0].type, "Brazil CPF Number")

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_some_errors_recognize_pii_entities(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "language": "es", "text": "hola"},
                {"id": "2", "text": ""},
                {"id": "3", "text": "Is 998.214.865-68 your Brazilian CPF number?"}]

        response = text_analytics.recognize_pii_entities(docs)
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_all_errors_recognize_pii_entities(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "language": "es", "text": "hola"},
                {"id": "2", "text": ""}]

        response = text_analytics.recognize_pii_entities(docs)
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_successful_recognize_linked_entities(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen"},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        response = text_analytics.recognize_linked_entities(docs)
        for doc in response:
            self.assertEqual(len(doc.entities), 3)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_some_errors_recognize_linked_entities(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        response = text_analytics.recognize_linked_entities(docs)
        self.assertTrue(response[0].is_error)
        self.assertFalse(response[1].is_error)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_all_errors_recognize_linked_entities(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "Spanish", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        response = text_analytics.recognize_linked_entities(docs)
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_successful_extract_key_phrases(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen"},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        response = text_analytics.extract_key_phrases(docs)
        for phrases in response:
            self.assertIn("Paul Allen", phrases.key_phrases)
            self.assertIn("Bill Gates", phrases.key_phrases)
            self.assertIn("Microsoft", phrases.key_phrases)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_some_errors_extract_key_phrases(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "language": "English", "text": "Microsoft was founded by Bill Gates and Paul Allen"},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        response = text_analytics.extract_key_phrases(docs)
        self.assertTrue(response[0].is_error)
        self.assertFalse(response[1].is_error)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_all_errors_extract_key_phrases(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "language": "English", "text": "Microsoft was founded by Bill Gates and Paul Allen"},
                {"id": "2", "language": "es", "text": ""}]

        response = text_analytics.extract_key_phrases(docs)
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_successful_analyze_sentiment(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
                {"id": "2", "language": "en", "text": "I did not like the hotel we stayed it. It was too expensive."},
                {"id": "3", "language": "en", "text": "The restaurant had really good food. I recommend you try it."}]

        response = text_analytics.analyze_sentiment(docs)
        self.assertEqual(response[0].sentiment, "neutral")
        self.assertEqual(response[1].sentiment, "negative")
        self.assertEqual(response[2].sentiment, "positive")

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_some_errors_analyze_sentiment(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "language": "en", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed it. It was too expensive."},
                {"id": "3", "language": "en", "text": "The restaurant had really good food. I recommend you try it."}]

        response = text_analytics.analyze_sentiment(docs)
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_all_errors_analyze_sentiment(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "1", "language": "en", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed it. It was too expensive."},
                {"id": "3", "language": "en", "text": ""}]

        response = text_analytics.analyze_sentiment(docs)
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)
        self.assertTrue(response[2].is_error)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_validate_input_string(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [
            u"I should take my cat to the veterinarian.",
            u"Este es un document escrito en Español.",
            u"猫は幸せ",
            u"Fahrt nach Stuttgart und dann zum Hotel zu Fu.",
            u""
        ]

        response = text_analytics.detect_language(docs)
        self.assertEqual(response[0].detected_languages[0].name, "English")
        self.assertEqual(response[1].detected_languages[0].name, "Spanish")
        self.assertEqual(response[2].detected_languages[0].name, "Japanese")
        self.assertEqual(response[3].detected_languages[0].name, "German")
        self.assertTrue(response[4].is_error)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_validate_language_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [
            LanguageInput(id="1", text="I should take my cat to the veterinarian."),
            LanguageInput(id="2", text="Este es un document escrito en Español."),
            LanguageInput(id="3", text="猫は幸せ"),
            LanguageInput(id="4", text="Fahrt nach Stuttgart und dann zum Hotel zu Fu.")
        ]

        response = text_analytics.detect_language(docs)
        self.assertEqual(response[0].detected_languages[0].name, "English")
        self.assertEqual(response[1].detected_languages[0].name, "Spanish")
        self.assertEqual(response[2].detected_languages[0].name, "Japanese")
        self.assertEqual(response[3].detected_languages[0].name, "German")

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_validate_multilanguage_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [
            MultiLanguageInput(id="1", text="Microsoft was founded by Bill Gates and Paul Allen."),
            MultiLanguageInput(id="2", text="I did not like the hotel we stayed it. It was too expensive."),
            MultiLanguageInput(id="3", text="The restaurant had really good food. I recommend you try it."),
        ]

        response = text_analytics.analyze_sentiment(docs)
        self.assertEqual(response[0].sentiment, "neutral")
        self.assertEqual(response[1].sentiment, "negative")
        self.assertEqual(response[2].sentiment, "positive")

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_mixing_inputs(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)
        docs = [
            {"id": "1", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
            MultiLanguageInput(id="2", text="I did not like the hotel we stayed it. It was too expensive."),
            u"You cannot mix string input with the above inputs"
        ]
        with self.assertRaises(TypeError):
            response = text_analytics.analyze_sentiment(docs)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_out_of_order_ids(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = text_analytics.analyze_sentiment(docs)
        in_order = ["56", "0", "22", "19", "1"]
        for idx, resp in enumerate(response):
            self.assertEqual(resp.id, in_order[idx])

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_show_stats_and_model_version(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        def callback(response):
            self.assertIsNotNone(response.model_version)
            self.assertIsNotNone(response.raw_response)
            self.assertEqual(response.statistics.documents_count, 5)
            self.assertEqual(response.statistics.transactions_count, 4)
            self.assertEqual(response.statistics.valid_documents_count, 4)
            self.assertEqual(response.statistics.erroneous_documents_count, 1)

        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = text_analytics.analyze_sentiment(
            docs,
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_batch_size_over_limit(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = [u"hello world"] * 1050
        with self.assertRaises(HttpResponseError):
            response = text_analytics.detect_language(docs)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_whole_batch_country_hint(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        def callback(resp):
            country_str = "\"countryHint\": \"CA\""
            country = resp.http_request.body.count(country_str)
            self.assertEqual(country, 3)

        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed it. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        response = text_analytics.detect_language(docs, country_hint="CA", response_hook=callback)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_whole_batch_dont_use_country_hint(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        def callback(resp):
            country_str = "\"countryHint\": \"\""
            country = resp.http_request.body.count(country_str)
            self.assertEqual(country, 3)

        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed it. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        response = text_analytics.detect_language(docs, country_hint="", response_hook=callback)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_per_item_dont_use_country_hint(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        def callback(resp):
            country_str = "\"countryHint\": \"\""
            country = resp.http_request.body.count(country_str)
            self.assertEqual(country, 2)
            country_str = "\"countryHint\": \"US\""
            country = resp.http_request.body.count(country_str)
            self.assertEqual(country, 1)


        docs = [{"id": "1", "country_hint": "", "text": "I will go to the park."},
                {"id": "2", "country_hint": "", "text": "I did not like the hotel we stayed it."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = text_analytics.detect_language(docs, response_hook=callback)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_whole_batch_country_hint_and_obj_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        def callback(resp):
            country_str = "\"countryHint\": \"CA\""
            country = resp.http_request.body.count(country_str)
            self.assertEqual(country, 3)

        docs = [
            LanguageInput(id="1", text="I should take my cat to the veterinarian."),
            LanguageInput(id="2", text="Este es un document escrito en Español."),
            LanguageInput(id="3", text="猫は幸せ"),
        ]

        response = text_analytics.detect_language(docs, country_hint="CA", response_hook=callback)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_whole_batch_country_hint_and_dict_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        def callback(resp):
            country_str = "\"countryHint\": \"CA\""
            country = resp.http_request.body.count(country_str)
            self.assertEqual(country, 3)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed it."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = text_analytics.detect_language(docs, country_hint="CA", response_hook=callback)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_whole_batch_country_hint_and_obj_per_item_hints(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        def callback(resp):
            country_str = "\"countryHint\": \"CA\""
            country = resp.http_request.body.count(country_str)
            self.assertEqual(country, 2)
            country_str = "\"countryHint\": \"US\""
            country = resp.http_request.body.count(country_str)
            self.assertEqual(country, 1)

        docs = [
            LanguageInput(id="1", text="I should take my cat to the veterinarian.", country_hint="CA"),
            LanguageInput(id="4", text="Este es un document escrito en Español.", country_hint="CA"),
            LanguageInput(id="3", text="猫は幸せ"),
        ]

        response = text_analytics.detect_language(docs, country_hint="US", response_hook=callback)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_whole_batch_country_hint_and_dict_per_item_hints(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        def callback(resp):
            country_str = "\"countryHint\": \"CA\""
            country = resp.http_request.body.count(country_str)
            self.assertEqual(country, 1)
            country_str = "\"countryHint\": \"US\""
            country = resp.http_request.body.count(country_str)
            self.assertEqual(country, 2)

        docs = [{"id": "1", "country_hint": "US", "text": "I will go to the park."},
                {"id": "2", "country_hint": "US", "text": "I did not like the hotel we stayed it."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = text_analytics.detect_language(docs, country_hint="CA", response_hook=callback)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_whole_batch_language_hint(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        def callback(resp):
            language_str = "\"language\": \"fr\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed it. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        response = text_analytics.analyze_sentiment(docs, language="fr", response_hook=callback)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_whole_batch_dont_use_language_hint(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        def callback(resp):
            language_str = "\"language\": \"\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed it. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        response = text_analytics.analyze_sentiment(docs, language="", response_hook=callback)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_per_item_dont_use_language_hint(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

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

        response = text_analytics.analyze_sentiment(docs, response_hook=callback)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_whole_batch_language_hint_and_obj_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        def callback(resp):
            language_str = "\"language\": \"de\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [
            MultiLanguageInput(id="1", text="I should take my cat to the veterinarian."),
            MultiLanguageInput(id="4", text="Este es un document escrito en Español."),
            MultiLanguageInput(id="3", text="猫は幸せ"),
        ]

        response = text_analytics.analyze_sentiment(docs, language="de", response_hook=callback)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_whole_batch_language_hint_and_dict_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed it."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = text_analytics.analyze_sentiment(docs, language="es", response_hook=callback)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_whole_batch_language_hint_and_obj_per_item_hints(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 2)
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 1)

        docs = [
            MultiLanguageInput(id="1", text="I should take my cat to the veterinarian.", language="es"),
            MultiLanguageInput(id="2", text="Este es un document escrito en Español.", language="es"),
            MultiLanguageInput(id="3", text="猫は幸せ"),
        ]

        response = text_analytics.analyze_sentiment(docs, language="en", response_hook=callback)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_whole_batch_language_hint_and_dict_per_item_hints(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

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

        response = text_analytics.analyze_sentiment(docs, language="en", response_hook=callback)

    @ResourceGroupPreparer()
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_bad_document_input(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        docs = "This is the wrong type"

        with self.assertRaises(TypeError):
            response = text_analytics.analyze_sentiment(docs)

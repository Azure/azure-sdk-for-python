# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from azure.ai.textanalytics.aio import (
    single_detect_language,
    single_recognize_entities,
    single_recognize_pii_entities,
    single_recognize_linked_entities,
    single_analyze_sentiment,
    single_extract_key_phrases
)
from azure.ai.textanalytics import TextAnalyticsApiKeyCredential

from testcase import GlobalTextAnalyticsAccountPreparer
from asynctestcase import AsyncTextAnalyticsTest


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class SingleTextAnalyticsTestAsync(AsyncTextAnalyticsTest):

    # single_detect_language ------------------------------------------------------

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_successful_single_language_detection_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        response = await single_detect_language(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="This is written in English.",
            country_hint="US"
        )

        self.assertEqual(response.primary_language.name, "English")
        self.assertEqual(response.primary_language.iso6391_name, "en")
        self.assertEqual(response.primary_language.score, 1.0)

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_language_detection_empty_credential_class_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = await single_detect_language(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(""),
                input_text="This is written in English.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_language_detection_bad_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = await single_detect_language(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential("xxxxxxxxxxxx"),
                input_text="This is written in English.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_language_detection_empty_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_detect_language(
                endpoint=text_analytics_account,
                credential="",
                input_text="This is written in English.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_language_detection_bad_type_for_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_detect_language(
                endpoint=text_analytics_account,
                credential=[],
                input_text="This is written in English.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_language_detection_none_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ValueError):
            response = await single_detect_language(
                endpoint=text_analytics_account,
                credential=None,
                input_text="This is written in English.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_language_detection_too_many_chars_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text = ""
        for _ in range(5121):
            text += "x"
        with self.assertRaises(HttpResponseError) as err:
            response = await single_detect_language(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text=text,
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_language_detection_empty_text_input_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_detect_language(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_language_detection_non_text_input_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_detect_language(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text={"id": "1", "text": "hello world"}
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_language_detection_bad_country_hint_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_detect_language(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="This is written in English.",
                country_hint="United States"
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_language_detection_bad_model_version_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_detect_language(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="Microsoft was founded by Bill Gates.",
                country_hint="US",
                model_version="old"
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_language_detection_response_hook_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        def callback(resp):
            self.assertIsNotNone(resp.statistics)
            self.assertIsNotNone(resp.model_version)

        response = await single_detect_language(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="Este es un document escrito en Español.",
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_language_detection_dont_use_country_hint_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        def callback(resp):
            country_str = "\"countryHint\": \"\""
            country = resp.http_request.body.count(country_str)
            self.assertEqual(country, 1)

        response = await single_detect_language(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="Este es un document escrito en Español.",
            country_hint="",
            response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_language_detection_given_country_hint_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        def callback(resp):
            country_str = "\"countryHint\": \"CA\""
            country = resp.http_request.body.count(country_str)
            self.assertEqual(country, 1)

        response = await single_detect_language(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="Este es un document escrito en Español.",
            country_hint="CA",
            response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_language_detection_default_country_hint_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        def callback(resp):
            country_str = "\"countryHint\": \"US\""
            country = resp.http_request.body.count(country_str)
            self.assertEqual(country, 1)

        response = await single_detect_language(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="Este es un document escrito en Español.",
            response_hook=callback
        )

    # single_recognize_entities ------------------------------------------------------

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_successful_single_recognize_entities_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        response = await single_recognize_entities(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="Microsoft was founded by Bill Gates.",
            language="en"
        )

        self.assertEqual(response.entities[0].text, "Microsoft")
        self.assertEqual(response.entities[1].text, "Bill Gates")
        for entity in response.entities:
            self.assertIsNotNone(entity.type)
            self.assertIsNotNone(entity.offset)
            self.assertIsNotNone(entity.length)
            self.assertIsNotNone(entity.score)

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_entities_empty_credential_class_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = await single_recognize_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(""),
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_entities_bad_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = await single_recognize_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential("xxxxxxxxxxxx"),
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_entities_empty_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_recognize_entities(
                endpoint=text_analytics_account,
                credential="",
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_entities_bad_type_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_recognize_entities(
                endpoint=text_analytics_account,
                credential=[],
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_entities_none_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ValueError):
            response = await single_recognize_entities(
                endpoint=text_analytics_account,
                credential=None,
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_entities_too_many_chars_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text = ""
        for _ in range(5121):
            text += "x"
        with self.assertRaises(HttpResponseError):
            response = await single_recognize_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text=text,
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_entities_empty_text_input_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_recognize_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_entities_non_text_input_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_recognize_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text={"id": "1", "text": "hello world"}
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_entities_bad_language_hint_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_recognize_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="Microsoft was founded by Bill Gates.",
                language="English"
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_entities_bad_model_version_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_recognize_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="Microsoft was founded by Bill Gates.",
                language="en",
                model_version="old"
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_entities_response_hook_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        def callback(resp):
            self.assertIsNotNone(resp.statistics)
            self.assertIsNotNone(resp.model_version)

        response = await single_recognize_entities(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="Microsoft was founded by Bill Gates.",
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )

    # single_recognize_pii_entities ------------------------------------------------------

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_successful_single_recognize_pii_entities_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        response = await single_recognize_pii_entities(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="My SSN is 555-55-5555",
            language="en"
        )

        self.assertEqual(response.entities[0].text, "555-55-5555")
        for entity in response.entities:
            self.assertIsNotNone(entity.type)
            self.assertIsNotNone(entity.offset)
            self.assertIsNotNone(entity.length)
            self.assertIsNotNone(entity.score)

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_pii_entities_empty_credential_class_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = await single_recognize_pii_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(""),
                input_text="My SSN is 555-55-5555",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_pii_entities_bad_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = await single_recognize_pii_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential("xxxxxxxxxxxx"),
                input_text="My SSN is 555-55-5555",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_pii_entities_empty_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_recognize_pii_entities(
                endpoint=text_analytics_account,
                credential="",
                input_text="My SSN is 555-55-5555",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_pii_entities_bad_type_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_recognize_pii_entities(
                endpoint=text_analytics_account,
                credential=[],
                input_text="My SSN is 555-55-5555",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_pii_entities_none_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ValueError):
            response = await single_recognize_pii_entities(
                endpoint=text_analytics_account,
                credential=None,
                input_text="My SSN is 555-55-5555",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_pii_entities_too_many_chars_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text = ""
        for _ in range(5121):
            text += "x"
        with self.assertRaises(HttpResponseError):
            response = await single_recognize_pii_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text=text,
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_pii_entities_empty_text_input_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_recognize_pii_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_pii_entities_non_text_input_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_recognize_pii_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text={"id": "1", "text": "hello world"}
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_pii_entities_bad_language_hint_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_recognize_pii_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="My SSN is 555-55-5555",
                language="English"
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_pii_entities_bad_model_version_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_recognize_pii_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="Microsoft was founded by Bill Gates.",
                language="en",
                model_version="old"
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_pii_entities_response_hook_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        def callback(resp):
            self.assertIsNotNone(resp.statistics)
            self.assertIsNotNone(resp.model_version)

        response = await single_recognize_pii_entities(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="My SSN is 555-55-5555",
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )

    # single_recognize_linked_entities ------------------------------------------------------

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_successful_single_recognize_linked_entities_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        response = await single_recognize_linked_entities(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="Microsoft was founded by Bill Gates.",
            language="en"
        )

        self.assertEqual(response.entities[0].name, "Bill Gates")
        self.assertEqual(response.entities[1].name, "Microsoft")
        for entity in response.entities:
            self.assertIsNotNone(entity.matches)
            self.assertIsNotNone(entity.language)
            self.assertIsNotNone(entity.id)
            self.assertIsNotNone(entity.url)
            self.assertIsNotNone(entity.data_source)

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_linked_entities_empty_credential_class_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = await single_recognize_linked_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(""),
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_linked_entities_bad_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = await single_recognize_linked_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential("xxxxxxxxxxxx"),
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_linked_entities_empty_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_recognize_linked_entities(
                endpoint=text_analytics_account,
                credential="",
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_linked_entities_bad_type_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_recognize_linked_entities(
                endpoint=text_analytics_account,
                credential=[],
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_linked_entities_none_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ValueError):
            response = await single_recognize_linked_entities(
                endpoint=text_analytics_account,
                credential=None,
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_linked_entities_too_many_chars_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text = ""
        for _ in range(5121):
            text += "x"
        with self.assertRaises(HttpResponseError):
            response = await single_recognize_linked_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text=text,
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_linked_entities_empty_text_input_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_recognize_linked_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_linked_entities_non_text_input_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_recognize_linked_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text={"id": "1", "text": "hello world"}
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_linked_entities_bad_language_hint_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_recognize_linked_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="Microsoft was founded by Bill Gates.",
                language="English"
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_linked_entities_bad_model_version_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_recognize_linked_entities(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="Microsoft was founded by Bill Gates.",
                language="en",
                model_version="old"
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_recognize_linked_entities_response_hook_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        def callback(resp):
            self.assertIsNotNone(resp.statistics)
            self.assertIsNotNone(resp.model_version)

        response = await single_recognize_linked_entities(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="Microsoft was founded by Bill Gates.",
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )

    # single_extract_key_phrases ------------------------------------------------------

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_successful_single_extract_key_phrases_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        response = await single_extract_key_phrases(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="Microsoft was founded by Bill Gates.",
            language="en"
        )

        self.assertIn("Microsoft", response.key_phrases)
        self.assertIn("Bill Gates", response.key_phrases)

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_extract_key_phrases_empty_credential_class_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = await single_extract_key_phrases(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(""),
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_extract_key_phrases_bad_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = await single_extract_key_phrases(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential("xxxxxxxxxxxx"),
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_extract_key_phrases_empty_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_extract_key_phrases(
                endpoint=text_analytics_account,
                credential="",
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_extract_key_phrases_bad_type_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_extract_key_phrases(
                endpoint=text_analytics_account,
                credential=[],
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_extract_key_phrases_none_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ValueError):
            response = await single_extract_key_phrases(
                endpoint=text_analytics_account,
                credential=None,
                input_text="Microsoft was founded by Bill Gates.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_extract_key_phrases_too_many_chars_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text = ""
        for _ in range(5121):
            text += "x"
        with self.assertRaises(HttpResponseError):
            response = await single_extract_key_phrases(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text=text,
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_extract_key_phrases_empty_text_input_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_extract_key_phrases(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_extract_key_phrases_non_text_input_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_extract_key_phrases(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text={"id": "1", "text": "hello world"}
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_extract_key_phrases_bad_language_hint_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_extract_key_phrases(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="Microsoft was founded by Bill Gates.",
                language="English"
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_extract_key_phrases_bad_model_version_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_extract_key_phrases(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="Microsoft was founded by Bill Gates.",
                language="en",
                model_version="old"
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_extract_key_phrases_response_hook_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        def callback(resp):
            self.assertIsNotNone(resp.statistics)
            self.assertIsNotNone(resp.model_version)

        response = await single_extract_key_phrases(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="Microsoft was founded by Bill Gates.",
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )

    # single_analyze_sentiment ------------------------------------------------------

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_successful_single_analyze_sentiment_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        response = await single_analyze_sentiment(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="I was unhappy with the food at the restaurant.",
            language="en"
        )

        self.assertIsNotNone(response.id)
        self.assertEqual(response.sentiment, "negative")
        self.assertIsNotNone(response.document_scores)
        self.assertIsNotNone(response.sentences)

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_analyze_sentiment_empty_credential_class_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = await single_analyze_sentiment(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(""),
                input_text="I was unhappy with the food at the restaurant.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_analyze_sentiment_bad_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ClientAuthenticationError):
            response = await single_analyze_sentiment(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential("xxxxxxxxxxxx"),
                input_text="I was unhappy with the food at the restaurant.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_analyze_sentiment_empty_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_analyze_sentiment(
                endpoint=text_analytics_account,
                credential="",
                input_text="I was unhappy with the food at the restaurant.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_analyze_sentiment_bad_type_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_analyze_sentiment(
                endpoint=text_analytics_account,
                credential=[],
                input_text="I was unhappy with the food at the restaurant.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_analyze_sentiment_none_credentials_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ValueError):
            response = await single_analyze_sentiment(
                endpoint=text_analytics_account,
                credential=None,
                input_text="I was unhappy with the food at the restaurant.",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_analyze_sentiment_too_many_chars_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text = ""
        for _ in range(5121):
            text += "x"
        with self.assertRaises(HttpResponseError):
            response = await single_analyze_sentiment(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text=text,
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_analyze_sentiment_empty_text_input_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_analyze_sentiment(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="",
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_analyze_sentiment_non_text_input_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            response = await single_analyze_sentiment(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text={"id": "1", "text": "hello world"}
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_analyze_sentiment_bad_language_hint_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_analyze_sentiment(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="I was unhappy with the food at the restaurant.",
                language="English"
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_analyze_sentiment_bad_model_version_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(HttpResponseError):
            response = await single_analyze_sentiment(
                endpoint=text_analytics_account,
                credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
                input_text="Microsoft was founded by Bill Gates.",
                language="en",
                model_version="old"
            )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_analyze_sentiment_response_hook_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        def callback(resp):
            self.assertIsNotNone(resp.statistics)
            self.assertIsNotNone(resp.model_version)

        response = await single_analyze_sentiment(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="I was unhappy with the food at the restaurant.",
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_analyze_sentiment_dont_use_language_hint_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        def callback(resp):
            language_str = "\"language\": \"\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 1)

        response = await single_analyze_sentiment(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="Este es un document escrito en Español.",
            language="",
            response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_analyze_sentiment_given_language_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 1)

        response = await single_analyze_sentiment(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="Este es un document escrito en Español.",
            language="es",
            response_hook=callback
        )

    @GlobalTextAnalyticsAccountPreparer()
    @AsyncTextAnalyticsTest.await_prepared_test
    async def test_single_analyze_sentiment_default_language_async(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        def callback(resp):
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 1)

        response = await single_analyze_sentiment(
            endpoint=text_analytics_account,
            credential=TextAnalyticsApiKeyCredential(text_analytics_account_key),
            input_text="Este es un document escrito en Español.",
            response_hook=callback
        )

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
from azure.core.pipeline.transport import AioHttpTransport
from azure.core.credentials import AzureKeyCredential
from multidict import CIMultiDict, CIMultiDictProxy
from testcase import GlobalTextAnalyticsAccountPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from asynctestcase import AsyncTextAnalyticsTest
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.ai.textanalytics import (
    TextDocumentInput,
    VERSION,
    TextAnalyticsApiVersion,
)

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

class TestHealth(AsyncTextAnalyticsTest):
    def _interval(self):
        return 5 if self.is_live else 0

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_no_single_input(self, client):
        with self.assertRaises(TypeError):
            async with client:
                response = await (await client.begin_analyze_healthcare("hello world", polling_interval=self._interval())).result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_all_successful_passing_dict(self, client):
        docs = [{"id": "1", "language": "en", "text": "Patient does not suffer from high blood pressure."},
                {"id": "2", "language": "en", "text": "Prescribed 100mg ibuprofen, taken twice daily."}]

        async with client:
            poller = await client.begin_analyze_healthcare(docs, show_stats=True, polling_interval=self._interval())
            response = await poller.result()

        self.assertIsNotNone(response.statistics)

        async for doc in response:
            self.assertIsNotNone(doc.id)
            self.assertIsNotNone(doc.statistics)
            self.assertIsNotNone(doc.entities)
            self.assertIsNotNone(doc.relations)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_all_successful_passing_text_document_input(self, client):
        docs = [
            TextDocumentInput(id="1", text="Patient does not suffer from high blood pressure."),
            TextDocumentInput(id="2", text="Prescribed 100mg ibuprofen, taken twice daily."),
        ]

        async with client:
            response = await (await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()

        self.assertIsNone(response.statistics) # show_stats=False by default

        async for doc in response:
            self.assertIsNotNone(doc.id)
            self.assertIsNone(doc.statistics)
            self.assertIsNotNone(doc.entities)
            self.assertIsNotNone(doc.relations)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_passing_only_string(self, client):
        docs = [
            u"Patient does not suffer from high blood pressure.",
            u"Prescribed 100mg ibuprofen, taken twice daily.",
            u""
        ]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)


        for i in range(2):
            self.assertIsNotNone(response[i].id)
            self.assertIsNotNone(response[i].entities)
            self.assertIsNotNone(response[i].relations)

        self.assertTrue(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_input_with_some_errors(self, client):
        docs = [{"id": "1", "language": "en", "text": ""},
                {"id": "2", "language": "english", "text": "Patient does not suffer from high blood pressure."},
                {"id": "3", "language": "en", "text": "Prescribed 100mg ibuprofen, taken twice daily."}]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_input_with_all_errors(self, client):
        docs = [{"id": "1", "language": "en", "text": ""},
                {"id": "2", "language": "english", "text": "Patient does not suffer from high blood pressure."},
                {"id": "3", "language": "en", "text": ""}]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)
        self.assertTrue(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_too_many_documents(self, client):
        docs = list(itertools.repeat("input document", 1001))  # Maximum number of documents per request is 1000

        with pytest.raises(HttpResponseError) as excinfo:
            async with client:
                await client.begin_analyze_healthcare(docs, polling_interval=self._interval())

        assert excinfo.value.status_code == 400

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_payload_too_large(self, client):
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
            async with client:
                await client.begin_analyze_healthcare(docs, polling_interval=self._interval())

        assert excinfo.value.status_code == 413

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_document_warnings(self, client):
        # TODO: reproduce a warnings scenario for implementation
        docs = [
            {"id": "1", "text": "This won't actually create a warning :'("},
        ]

        async with client:
            result = await (await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()

        async for doc in result:
            doc_warnings = doc.warnings
            self.assertEqual(len(doc_warnings), 0)  # Currently the service doesn't return any warnings at all even though it is expressed in the Swagger.

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_output_same_order_as_input(self, client):
        docs = [
            TextDocumentInput(id="1", text="one"),
            TextDocumentInput(id="2", text="two"),
            TextDocumentInput(id="3", text="three"),
            TextDocumentInput(id="4", text="four"),
            TextDocumentInput(id="5", text="five")
        ]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        for idx, doc in enumerate(response):
            self.assertEqual(str(idx + 1), doc.id)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3,
        "text_analytics_account_key": "",
    })
    async def test_empty_credential_class(self, client):
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                response = await client.begin_analyze_healthcare(
                    ["This is written in English."],
                    polling_interval=self._interval()
                )

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3,
        "text_analytics_account_key": "xxxx",
    })
    async def test_bad_credentials(self, client):
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                response = await client.begin_analyze_healthcare(
                    ["This is written in English."],
                    polling_interval=self._interval()
                )

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_bad_document_input(self, client):
        docs = "This is the wrong type"

        with self.assertRaises(TypeError):
            async with client:
                response = await client.begin_analyze_healthcare(docs, polling_interval=self._interval())

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_mixing_inputs(self, client):
        docs = [
            {"id": "1", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
            TextDocumentInput(id="2", text="I did not like the hotel we stayed at. It was too expensive."),
            u"You cannot mix string input with the above inputs"
        ]
        with self.assertRaises(TypeError):
            async with client:
                response = await client.begin_analyze_healthcare(docs, polling_interval=self._interval())

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_out_of_order_ids(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        expected_order = ["56", "0", "22", "19", "1"]
        actual_order = [x.id for x in response]
        for idx, resp in enumerate(response):
            self.assertEqual(resp.id, expected_order[idx])

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_show_stats_and_model_version(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        async with client:
            response = await (await client.begin_analyze_healthcare(
                docs,
                show_stats=True,
                model_version="2020-09-03",
                polling_interval=self._interval()
            )).result()

        self.assertIsNotNone(response)
        self.assertIsNotNone(response.model_version)
        self.assertEqual("2020-09-03", response.model_version)
        self.assertEqual(response.statistics.documents_count, 5)
        self.assertEqual(response.statistics.transactions_count, 4)
        self.assertEqual(response.statistics.valid_documents_count, 4)
        self.assertEqual(response.statistics.erroneous_documents_count, 1)

        async for doc in response:
            if not doc.is_error:
                self.assertIsNotNone(doc.statistics)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_whole_batch_language_hint(self, client):
        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed at. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, language="en", polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_whole_batch_dont_use_language_hint(self, client):
        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed at. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, language="", polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_per_item_dont_use_language_hint(self, client):
        docs = [{"id": "1", "language": "", "text": "I will go to the park."},
                {"id": "2", "language": "", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_whole_batch_language_hint_and_obj_input(self, client):
        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian."),
            TextDocumentInput(id="4", text="Este es un document escrito en Español."),
            TextDocumentInput(id="3", text="猫は幸せ"),
        ]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, language="en", polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_whole_batch_language_hint_and_dict_input(self, client):
        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, language="en", polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_whole_batch_language_hint_and_obj_per_item_hints(self, client):
        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian.", language="en"),
            TextDocumentInput(id="2", text="猫は幸せ"),
        ]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, language="en", polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_whole_batch_language_hint_and_dict_per_item_hints(self, client):
        docs = [{"id": "1", "language": "", "text": "I will go to the park."},
                {"id": "2", "language": "", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, language="en", polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3,
        "default_language": "en"
    })
    async def test_client_passed_default_language_hint(self, client):
        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_invalid_language_hint_method(self, client):
        docs = ["This should fail because we're passing in an invalid language hint"]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, language="notalanguage", polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertEqual(response[0].error.code, 'UnsupportedLanguageCode')

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_invalid_language_hint_docs(self, client):
        docs = [{"id": "1", "language": "notalanguage", "text": "This should fail because we're passing in an invalid language hint"}]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertEqual(response[0].error.code, 'UnsupportedLanguageCode')

    @GlobalTextAnalyticsAccountPreparer()
    async def test_rotate_subscription_key(self, resource_group, location, text_analytics_account, text_analytics_account_key):

        credential = AzureKeyCredential(text_analytics_account_key)
        client = TextAnalyticsClient(text_analytics_account, credential, api_version=TextAnalyticsApiVersion.V3_1_PREVIEW_3)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        async with client:
            response = await (await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()
            self.assertIsNotNone(response)

            credential.update("xxx")  # Make authentication fail
            with self.assertRaises(ClientAuthenticationError):
                response = await (await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()

            credential.update(text_analytics_account_key)  # Authenticate successfully again
            response = await (await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()
            self.assertIsNotNone(response)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_user_agent(self, client):  # TODO: verify
        def callback(resp):
            self.assertIn("azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                VERSION, platform.python_version(), platform.platform()),
                resp.http_request.headers["User-Agent"]
            )

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        async with client:
            poller = await client.begin_analyze_healthcare(docs, polling_interval=self._interval())
            self.assertIn("azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                    VERSION, platform.python_version(), platform.platform()),
                    poller._polling_method._initial_response.http_request.headers["User-Agent"]
                )

            await poller.result()  # need to call this before tearDown runs even though we don't need the response for the test.

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_document_attribute_error_no_result_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        async with client:
            result = await(await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

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
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_document_attribute_error_nonexistent_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        async with client:
            result = await(await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        # Attribute not found on DocumentError or result obj, default behavior/message
        try:
            health = response[0].attribute_not_on_result_or_error
        except AttributeError as default_behavior:
            self.assertEqual(
                default_behavior.args[0],
                '\'DocumentError\' object has no attribute \'attribute_not_on_result_or_error\''
            )

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_bad_model_version_error(self, client):
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        try:
            async with client:
                result = await(await client.begin_analyze_healthcare(docs, model_version="bad", polling_interval=self._interval())).result()
                response = []
                async for r in result:
                    response.append(r)
        except HttpResponseError as err:
            self.assertEqual(err.error.code, "ModelVersionIncorrect")
            self.assertIsNotNone(err.error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_document_errors(self, client):
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": text}]

        async with client:
            result = await(await client.begin_analyze_healthcare(docs, polling_interval=self._interval())).result()
            doc_errors = []
            async for r in result:
                doc_errors.append(r)
        self.assertEqual(doc_errors[0].error.code, "InvalidDocument")
        self.assertIsNotNone(doc_errors[0].error.message)
        self.assertEqual(doc_errors[1].error.code, "UnsupportedLanguageCode")
        self.assertIsNotNone(doc_errors[1].error.message)
        self.assertEqual(doc_errors[2].error.code, "InvalidDocument")
        self.assertIsNotNone(doc_errors[2].error.message)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_not_passing_list_for_docs(self, client):
        docs = {"id": "1", "text": "hello world"}
        with pytest.raises(TypeError) as excinfo:
            async with client:
                await client.begin_analyze_healthcare(docs, polling_interval=self._interval())
        assert "Input documents cannot be a dict" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_missing_input_records_error(self, client):
        docs = []
        with pytest.raises(ValueError) as excinfo:
            async with client:
                await client.begin_analyze_healthcare(docs, polling_interval=self._interval())
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_passing_none_docs(self, client):
        with pytest.raises(ValueError) as excinfo:
            async with client:
                await client.begin_analyze_healthcare(None, polling_interval=self._interval())
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_duplicate_ids_error(self, client):
        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed at."}]
        try:
            async with client:
                result = await client.begin_analyze_healthcare(docs, polling_interval=self._interval())
        except HttpResponseError as err:
            self.assertEqual(err.error.code, "InvalidDocument")
            self.assertIsNotNone(err.error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_pass_cls(self, client):
        def callback(pipeline_response, deserialized, _):
            return "cls result"

        async with client:
            res = await (await client.begin_analyze_healthcare(
                documents=["Test passing cls to endpoint"],
                cls=callback,
                polling_interval=self._interval()
            )).result()
        assert res == "cls result"

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_multiple_pages_of_results_returned_successfully(self, client):
        single_doc = "hello world"
        docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 10)))]
        # Service now only accepts 10 documents for a job, and since the current default server-side value
        # for records per page is 20, pagination logic will never be activated.  This is intended to change
        # in the future but for now this test actually won't hit the pagination logic now.

        async with client:
            poller = await client.begin_analyze_healthcare(docs, show_stats=True, polling_interval=self._interval())
            result = await poller.result()
            response = []
            async for r in result:
                response.append(r)

        self.assertEqual(len(docs), len(response))
        self.assertIsNotNone(result.statistics)

        for (idx, doc) in enumerate(response):
            self.assertEqual(docs[idx]["id"], doc.id)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_multiple_pages_of_results_with_errors_returned_successfully(self, client):
        single_doc = "hello world"
        docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 9)))]
        docs.append({"id": "9", "text": ""})
        # Service now only accepts 10 documents for a job, and since the current default server-side value
        # for records per page is 20, pagination logic will never be activated.  This is intended to change
        # in the future but for now this test actually won't hit the pagination logic now.

        async with client:
            result = await (await client.begin_analyze_healthcare(docs, show_stats=True, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

            self.assertEqual(len(docs), len(response))
            self.assertIsNotNone(result.statistics)

            for (idx, doc) in enumerate(response):
                self.assertEqual(docs[idx]["id"], doc.id)

                if doc.id == "9":
                    self.assertTrue(doc.is_error)

                else:
                    self.assertFalse(doc.is_error)
                    self.assertIsNotNone(doc.statistics)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    async def test_cancellation(self, client):
        single_doc = "hello world"
        docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 10)))]

        async with client:
            poller = await client.begin_analyze_healthcare(docs, polling_interval=self._interval())
            cancellation_result = await (await client.begin_cancel_analyze_healthcare(poller, polling_interval=self._interval())).result()

            self.assertIsNone(cancellation_result)

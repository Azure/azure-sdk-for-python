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
    HealthcareEntityRelationType,
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
    @TextAnalyticsClientPreparer()
    async def test_no_single_input(self, client):
        with self.assertRaises(TypeError):
            async with client:
                response = await (await client.begin_analyze_healthcare_entities("hello world", polling_interval=self._interval())).result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_passing_only_string(self, client):
        docs = [
            u"Patient does not suffer from high blood pressure.",
            u"Prescribed 100mg ibuprofen, taken twice daily.",
            u""
        ]

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)


        for i in range(2):
            self.assertIsNotNone(response[i].id)
            self.assertIsNotNone(response[i].entities)

        self.assertTrue(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_input_with_some_errors(self, client):
        docs = [{"id": "1", "language": "en", "text": ""},
                {"id": "2", "language": "english", "text": "Patient does not suffer from high blood pressure."},
                {"id": "3", "language": "en", "text": "Prescribed 100mg ibuprofen, taken twice daily."}]

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_too_many_documents(self, client):
        docs = list(itertools.repeat("input document", 1001))  # Maximum number of documents per request is 1000

        with pytest.raises(HttpResponseError) as excinfo:
            async with client:
                await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())

        assert excinfo.value.status_code == 400

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
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
                await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())

        assert excinfo.value.status_code == 413

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_out_of_order_ids(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        expected_order = ["56", "0", "22", "19", "1"]
        actual_order = [x.id for x in response]
        for idx, resp in enumerate(response):
            self.assertEqual(resp.id, expected_order[idx])

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_show_stats_and_model_version(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        async with client:
            response = await (await client.begin_analyze_healthcare_entities(
                docs,
                show_stats=True,
                model_version="2021-01-11",
                polling_interval=self._interval()
            )).result()

        self.assertIsNotNone(response)
        assert response.model_version    # commenting out bc of service error, always uses latest https://github.com/Azure/azure-sdk-for-python/issues/17160
        self.assertEqual(response.statistics.documents_count, 5)
        self.assertEqual(response.statistics.transactions_count, 4)
        self.assertEqual(response.statistics.valid_documents_count, 4)
        self.assertEqual(response.statistics.erroneous_documents_count, 1)

        async for doc in response:
            if not doc.is_error:
                self.assertIsNotNone(doc.statistics)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_whole_batch_language_hint_and_dict_input(self, client):
        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, language="en", polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_invalid_language_hint_method(self, client):
        docs = ["This should fail because we're passing in an invalid language hint"]

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, language="notalanguage", polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertEqual(response[0].error.code, 'UnsupportedLanguageCode')

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_invalid_language_hint_docs(self, client):
        docs = [{"id": "1", "language": "notalanguage", "text": "This should fail because we're passing in an invalid language hint"}]

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        self.assertEqual(response[0].error.code, 'UnsupportedLanguageCode')

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_user_agent(self, client):  # TODO: verify
        def callback(resp):
            self.assertIn("azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                VERSION, platform.python_version(), platform.platform()),
                resp.http_request.headers["User-Agent"]
            )

        docs = [{"id": "1", "text": "I will go to the park."}]

        async with client:
            poller = await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())
            self.assertIn("azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                    VERSION, platform.python_version(), platform.platform()),
                    poller._polling_method._initial_response.http_request.headers["User-Agent"]
                )

            await poller.result()  # need to call this before tearDown runs even though we don't need the response for the test.

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_bad_model_version_error(self, client):
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        try:
            async with client:
                result = await(await client.begin_analyze_healthcare_entities(docs, model_version="bad", polling_interval=self._interval())).result()
                response = []
                async for r in result:
                    response.append(r)
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

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())).result()
            doc_errors = []
            async for r in result:
                doc_errors.append(r)
        self.assertEqual(doc_errors[0].error.code, "InvalidDocument")
        self.assertIsNotNone(doc_errors[0].error.message)
        self.assertEqual(doc_errors[1].error.code, "UnsupportedLanguageCode")
        self.assertIsNotNone(doc_errors[1].error.message)
        self.assertEqual(doc_errors[2].error.code, "InvalidDocument")
        self.assertIsNotNone(doc_errors[2].error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_duplicate_ids_error(self, client):
        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed at."}]
        try:
            async with client:
                result = await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())
        except HttpResponseError as err:
            self.assertEqual(err.error.code, "InvalidDocument")
            self.assertIsNotNone(err.error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_pass_cls(self, client):
        def callback(pipeline_response, deserialized, _):
            return "cls result"

        async with client:
            res = await (await client.begin_analyze_healthcare_entities(
                documents=["Test passing cls to endpoint"],
                cls=callback,
                polling_interval=self._interval()
            )).result()
        assert res == "cls result"

    """Commenting out multi page tests until service returns multiple pages"""

    # @GlobalTextAnalyticsAccountPreparer()
    # @TextAnalyticsClientPreparer()
    # async def test_multiple_pages_of_results_returned_successfully(self, client):
    #     single_doc = "hello world"
    #     docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 10)))]
    #     # Service now only accepts 10 documents for a job, and since the current default server-side value
    #     # for records per page is 20, pagination logic will never be activated.  This is intended to change
    #     # in the future but for now this test actually won't hit the pagination logic now.

    #     async with client:
    #         poller = await client.begin_analyze_healthcare_entities(docs, show_stats=True, polling_interval=self._interval())
    #         result = await poller.result()
    #         response = []
    #         async for r in result:
    #             response.append(r)

    #     self.assertEqual(len(docs), len(response))
    #     self.assertIsNotNone(result.statistics)

    #     for (idx, doc) in enumerate(response):
    #         self.assertEqual(docs[idx]["id"], doc.id)

    # @GlobalTextAnalyticsAccountPreparer()
    # @TextAnalyticsClientPreparer()
    # async def test_multiple_pages_of_results_with_errors_returned_successfully(self, client):
    #     single_doc = "hello world"
    #     docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 9)))]
    #     docs.append({"id": "9", "text": ""})
    #     # Service now only accepts 10 documents for a job, and since the current default server-side value
    #     # for records per page is 20, pagination logic will never be activated.  This is intended to change
    #     # in the future but for now this test actually won't hit the pagination logic now.

    #     async with client:
    #         result = await (await client.begin_analyze_healthcare_entities(docs, show_stats=True, polling_interval=self._interval())).result()
    #         response = []
    #         async for r in result:
    #             response.append(r)

    #         self.assertEqual(len(docs), len(response))
    #         self.assertIsNotNone(result.statistics)

    #         for (idx, doc) in enumerate(response):
    #             self.assertEqual(docs[idx]["id"], doc.id)

    #             if doc.id == "9":
    #                 self.assertTrue(doc.is_error)

    #             else:
    #                 self.assertFalse(doc.is_error)
    #                 self.assertIsNotNone(doc.statistics)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_cancellation(self, client):
        single_doc = "hello world"
        docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 10)))]

        async with client:
            poller = await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())

            try:
                cancellation_poller = await poller.cancel()
                cancellation_poller.wait()

            except HttpResponseError:
                pass # expected if the operation was already in a terminal state.


    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_default_string_index_type_is_UnicodeCodePoint(self, client):
        poller = await client.begin_analyze_healthcare_entities(documents=["Hello world"], polling_interval=self._interval())
        actual_string_index_type = poller._polling_method._initial_response.http_request.query["stringIndexType"]
        self.assertEqual(actual_string_index_type, "UnicodeCodePoint")
        await poller.result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_explicit_set_string_index_type(self, client):
        poller = await client.begin_analyze_healthcare_entities(
            documents=["Hello world"],
            string_index_type="TextElements_v8",
            polling_interval=self._interval(),
        )
        actual_string_index_type = poller._polling_method._initial_response.http_request.query["stringIndexType"]
        self.assertEqual(actual_string_index_type, "TextElements_v8")
        await poller.result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_relations(self, client):
        response = await (await client.begin_analyze_healthcare_entities(
            documents=["The patient was diagnosed with Parkinsons Disease (PD)"],
            polling_interval=self._interval(),
        )).result()

        result = []
        async for r in response:
            result.append(r)

        assert len(result) == 1
        result = result[0]

        assert len(result.entities) == 2
        assert len(result.entity_relations) == 1

        relation = result.entity_relations[0]
        assert relation.relation_type == HealthcareEntityRelationType.ABBREVIATION
        assert len(relation.roles) == 2

        parkinsons_entity = list(filter(lambda x: x.text == "Parkinsons Disease", result.entities))[0]
        parkinsons_abbreviation_entity = list(filter(lambda x: x.text == "PD", result.entities))[0]

        for role in relation.roles:
            if role.name == "FullTerm":
                self.assert_healthcare_entities_equal(role.entity, parkinsons_entity)
            else:
                assert role.name == "AbbreviatedTerm"
                self.assert_healthcare_entities_equal(role.entity, parkinsons_abbreviation_entity)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_normalized_text(self, client):
        response = await (await client.begin_analyze_healthcare_entities(
            documents=["patients must have histologically confirmed NHL"],
            polling_interval=self._interval(),
        )).result()

        result = []
        async for r in response:
            result.append(r)

        assert all([
            e for e in result[0].entities if hasattr(e, "normalized_text")
        ])

        histologically_entity = list(filter(lambda x: x.text == "histologically", result[0].entities))[0]
        assert histologically_entity.normalized_text == "Histology Procedure"

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_healthcare_assertion(self, client):
        response = await (await client.begin_analyze_healthcare_entities(
            documents=["Baby not likely to have Meningitis. In case of fever in the mother, consider Penicillin for the baby too."],
            polling_interval=self._interval(),
        )).result()

        result = []
        async for r in response:
            result.append(r)

        # currently can only test certainty
        # have an issue to update https://github.com/Azure/azure-sdk-for-python/issues/17088
        meningitis_entity = next(e for e in result[0].entities if e.text == "Meningitis")
        assert meningitis_entity.assertion.certainty == "negativePossible"

# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import datetime
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
    RecognizeEntitiesAction,
    RecognizeLinkedEntitiesAction,
    RecognizePiiEntitiesAction,
    ExtractKeyPhrasesAction,
    AnalyzeBatchActionsType
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


class TestAnalyzeAsync(AsyncTextAnalyticsTest):

    def _interval(self):
        return 5 if self.is_live else 0

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_no_single_input(self, client):
        with self.assertRaises(TypeError):
            response = await client.begin_analyze_batch_actions("hello world", actions=[], polling_interval=self._interval())

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_all_successful_passing_dict_key_phrase_task(self, client):
        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen"},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        async with client:
            response = await (await client.begin_analyze_batch_actions(
                docs,
                actions=[ExtractKeyPhrasesAction()],
                show_stats=True,
                polling_interval=self._interval()
            )).result()

            action_results = []
            async for p in response:
                action_results.append(p)
            assert len(action_results) == 1
            action_result = action_results[0]

            assert action_result.action_type == AnalyzeBatchActionsType.EXTRACT_KEY_PHRASES
            assert len(action_result.document_results) == len(docs)

            for doc in action_result.document_results:
                self.assertIn("Paul Allen", doc.key_phrases)
                self.assertIn("Bill Gates", doc.key_phrases)
                self.assertIn("Microsoft", doc.key_phrases)
                self.assertIsNotNone(doc.id)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_all_successful_passing_text_document_input_entities_task(self, client):
        docs = [
            TextDocumentInput(id="1", text="Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975", language="en"),
            TextDocumentInput(id="2", text="Microsoft fue fundado por Bill Gates y Paul Allen el 4 de abril de 1975.", language="es"),
            TextDocumentInput(id="3", text="Microsoft wurde am 4. April 1975 von Bill Gates und Paul Allen gegründet.", language="de"),
        ]

        async with client:
            poller = await client.begin_analyze_batch_actions(
                docs,
                actions=[RecognizeEntitiesAction()],
                show_stats=True,
                polling_interval=self._interval(),
            )
            response = await poller.result()

            action_results = []
            async for p in response:
                action_results.append(p)
            assert len(action_results) == 1
            action_result = action_results[0]

            assert action_result.action_type == AnalyzeBatchActionsType.RECOGNIZE_ENTITIES
            assert len(action_result.document_results) == len(docs)

            for doc in action_result.document_results:
                self.assertEqual(len(doc.entities), 4)
                self.assertIsNotNone(doc.id)
                for entity in doc.entities:
                    self.assertIsNotNone(entity.text)
                    self.assertIsNotNone(entity.category)
                    self.assertIsNotNone(entity.offset)
                    self.assertIsNotNone(entity.confidence_score)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_all_successful_passing_string_pii_entities_task(self, client):

        docs = ["My SSN is 859-98-0987.",
                "Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check.",
                "Is 998.214.865-68 your Brazilian CPF number?"
        ]

        async with client:
            response = await (await client.begin_analyze_batch_actions(
                docs,
                actions=[RecognizePiiEntitiesAction()],
                show_stats=True,
                polling_interval=self._interval()
            )).result()

            action_results = []
            async for p in response:
                action_results.append(p)
            assert len(action_results) == 1
            action_result = action_results[0]

            assert action_result.action_type == AnalyzeBatchActionsType.RECOGNIZE_PII_ENTITIES
            assert len(action_result.document_results) == len(docs)

            self.assertEqual(action_result.document_results[0].entities[0].text, "859-98-0987")
            self.assertEqual(action_result.document_results[0].entities[0].category, "USSocialSecurityNumber")
            self.assertEqual(action_result.document_results[1].entities[0].text, "111000025")
            # self.assertEqual(results[1].entities[0].category, "ABA Routing Number")  # Service is currently returning PhoneNumber here

            # commenting out brazil cpf, currently service is not returning it
            # self.assertEqual(action_result.document_results[2].entities[0].text, "998.214.865-68")
            # self.assertEqual(action_result.document_results[2].entities[0].category, "Brazil CPF Number")
            for doc in action_result.document_results:
                self.assertIsNotNone(doc.id)
                for entity in doc.entities:
                    self.assertIsNotNone(entity.text)
                    self.assertIsNotNone(entity.category)
                    self.assertIsNotNone(entity.offset)
                    self.assertIsNotNone(entity.confidence_score)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_bad_request_on_empty_document(self, client):
        docs = [u""]

        with self.assertRaises(HttpResponseError):
            async with client:
                response = await (await client.begin_analyze_batch_actions(
                    docs,
                    actions=[ExtractKeyPhrasesAction()],
                    polling_interval=self._interval()
                )).result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "text_analytics_account_key": "",
    })
    async def test_empty_credential_class(self, client):
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                response = await (await client.begin_analyze_batch_actions(
                    ["This is written in English."],
                    actions=[
                        RecognizeEntitiesAction(),
                        ExtractKeyPhrasesAction(),
                        RecognizePiiEntitiesAction(),
                    ],
                    polling_interval=self._interval()
                )).result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "text_analytics_account_key": "xxxxxxxxxxxx"
    })
    async def test_bad_credentials(self, client):
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                response = await (await client.begin_analyze_batch_actions(
                    ["This is written in English."],
                    actions=[
                        RecognizeEntitiesAction(),
                        ExtractKeyPhrasesAction(),
                        RecognizePiiEntitiesAction(),
                    ],
                    polling_interval=self._interval()
                )).result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_out_of_order_ids_multiple_tasks(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        async with client:
            response = await (await client.begin_analyze_batch_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(model_version="bad"),
                    ExtractKeyPhrasesAction(),
                    RecognizePiiEntitiesAction(),
                ],
                polling_interval=self._interval()
            )).result()

            action_results = []
            async for p in response:
                action_results.append(p)
            assert len(action_results) == 3

            assert action_results[0].is_error
            assert action_results[1].action_type == AnalyzeBatchActionsType.EXTRACT_KEY_PHRASES
            assert action_results[2].action_type == AnalyzeBatchActionsType.RECOGNIZE_PII_ENTITIES

            action_results = [r for r in action_results if not r.is_error]

            assert all([action_result for action_result in action_results if len(action_result.document_results) == len(docs)])

            in_order = ["56", "0", "19", "1"]

            for action_result in action_results:
                for idx, resp in enumerate(action_result.document_results):
                    self.assertEqual(resp.id, in_order[idx])

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_show_stats_and_model_version_multiple_tasks(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        async with client:
            response = await (await client.begin_analyze_batch_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(model_version="latest"),
                    ExtractKeyPhrasesAction(model_version="latest"),
                    RecognizePiiEntitiesAction(model_version="latest"),
                    RecognizeLinkedEntitiesAction(model_version="latest")
                ],
                show_stats=True,
                polling_interval=self._interval()
            )).result()

            action_results = []
            async for p in response:
                action_results.append(p)
            assert len(action_results) == 4
            assert action_results[0].action_type == AnalyzeBatchActionsType.RECOGNIZE_ENTITIES
            assert action_results[1].action_type == AnalyzeBatchActionsType.EXTRACT_KEY_PHRASES
            assert action_results[2].action_type == AnalyzeBatchActionsType.RECOGNIZE_PII_ENTITIES
            assert action_results[3].action_type == AnalyzeBatchActionsType.RECOGNIZE_LINKED_ENTITIES

            assert all([action_result for action_result in action_results if len(action_result.document_results) == len(docs)])

            for action_result in action_results:
                assert action_result.statistics
                for doc in action_result.document_results:
                    assert doc.statistics

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_poller_metadata(self, client):
        docs = [{"id": "56", "text": ":)"}]

        async with client:
            poller = await client.begin_analyze_batch_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(model_version="latest")
                ],
                show_stats=True,
                polling_interval=self._interval(),
            )

            response = await poller.result()

            assert isinstance(poller.created_on, datetime.datetime)
            poller._polling_method.display_name
            assert isinstance(poller.expires_on, datetime.datetime)
            assert poller.actions_failed_count == 0
            assert poller.actions_in_progress_count == 0
            assert poller.actions_succeeded_count == 1
            assert isinstance(poller.last_modified_on, datetime.datetime)
            assert poller.total_actions_count == 1
            assert poller.id

    ### TODO: Commenting out language tests. Right now analyze only supports language 'en', so no point to these tests yet

    # @GlobalTextAnalyticsAccountPreparer()
    # @TextAnalyticsClientPreparer()
    # async def test_whole_batch_language_hint(self, client):
    #     def callback(resp):
    #         language_str = "\"language\": \"fr\""
    #         if resp.http_request.body:
    #             language = resp.http_request.body.count(language_str)
    #             self.assertEqual(language, 3)

    #     docs = [
    #         u"This was the best day of my life.",
    #         u"I did not like the hotel we stayed at. It was too expensive.",
    #         u"The restaurant was not as good as I hoped."
    #     ]

    #     async with client:
    #         response = await (await client.begin_analyze_batch_actions(
    #             docs,
    #             actions=[
    #                 RecognizeEntitiesAction(),
    #                 ExtractKeyPhrasesAction(),
    #                 RecognizePiiEntitiesAction()
    #             ],
    #             language="fr",
    #             polling_interval=self._interval(),
    #             raw_response_hook=callback
    #         )).result()

    #         async for action_result in response:
    #             for doc in action_result.document_results:
    #                 self.assertFalse(doc.is_error)


    # @GlobalTextAnalyticsAccountPreparer()
    # @TextAnalyticsClientPreparer(client_kwargs={
    #     "default_language": "en"
    # })
    # async def test_whole_batch_language_hint_and_obj_per_item_hints(self, client):
    #     def callback(resp):
    #         if resp.http_request.body:
    #             language_str = "\"language\": \"es\""
    #             language = resp.http_request.body.count(language_str)
    #             self.assertEqual(language, 2)
    #             language_str = "\"language\": \"en\""
    #             language = resp.http_request.body.count(language_str)
    #             self.assertEqual(language, 1)

    #     docs = [
    #         TextDocumentInput(id="1", text="I should take my cat to the veterinarian.", language="es"),
    #         TextDocumentInput(id="2", text="Este es un document escrito en Español.", language="es"),
    #         TextDocumentInput(id="3", text="猫は幸せ"),
    #     ]

    #     async with client:
    #         response = await (await client.begin_analyze_batch_actions(
    #             docs,
    #             actions=[
    #                 RecognizeEntitiesAction(),
    #                 ExtractKeyPhrasesAction(),
    #                 RecognizePiiEntitiesAction()
    #             ],
    #             language="en",
    #             polling_interval=self._interval()
    #         )).result()

    #         async for action_result in response:
    #             for doc in action_result.document_results:
    #                 assert not doc.is_error

    # @GlobalTextAnalyticsAccountPreparer()
    # @TextAnalyticsClientPreparer()
    # async def test_invalid_language_hint_method(self, client):
    #     async with client:
    #         response = await (await client.begin_analyze_batch_actions(
    #             ["This should fail because we're passing in an invalid language hint"],
    #             language="notalanguage",
    #             actions=[
    #                 RecognizeEntitiesAction(),
    #                 ExtractKeyPhrasesAction(),
    #                 RecognizePiiEntitiesAction()
    #             ],
    #             polling_interval=self._interval()
    #         )).result()

    #         async for action_result in response:
    #             for doc in action_result.document_results:
    #                 assert doc.is_error

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_bad_model_version_error_multiple_tasks(self, client):  # TODO: verify behavior of service
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        async with client:
            response = await (await
            client.begin_analyze_batch_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(model_version="latest"),
                    ExtractKeyPhrasesAction(model_version="bad"),
                    RecognizePiiEntitiesAction(model_version="bad"),
                    RecognizeLinkedEntitiesAction(model_version="bad")
                ],
                polling_interval=self._interval()
            )).result()

            action_results = []
            async for p in response:
                action_results.append(p)

            assert action_results[0].is_error == False
            assert action_results[0].action_type == AnalyzeBatchActionsType.RECOGNIZE_ENTITIES
            assert action_results[1].is_error == True
            assert action_results[1].error.code == "InvalidRequest"
            assert action_results[2].is_error == True
            assert action_results[2].error.code == "InvalidRequest"
            assert action_results[3].is_error == True
            assert action_results[3].error.code == "InvalidRequest"

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_bad_model_version_error_all_tasks(self, client):  # TODO: verify behavior of service
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        with self.assertRaises(HttpResponseError):
            async with client:
                result = await (await client.begin_analyze_batch_actions(
                    docs,
                    actions=[
                        RecognizeEntitiesAction(model_version="bad"),
                        ExtractKeyPhrasesAction(model_version="bad"),
                        RecognizePiiEntitiesAction(model_version="bad")
                    ],
                    polling_interval=self._interval()
                )).result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_missing_input_records_error(self, client):
        docs = []
        with pytest.raises(ValueError) as excinfo:
            async with client:
                await (await client.begin_analyze_batch_actions(
                    docs,
                    actions=[
                        RecognizeEntitiesAction(),
                        ExtractKeyPhrasesAction(),
                        RecognizePiiEntitiesAction()
                    ],
                    polling_interval=self._interval()
                )).result()
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_passing_none_docs(self, client):
        with pytest.raises(ValueError) as excinfo:
            async with client:
                await client.begin_analyze_batch_actions(None, None, polling_interval=self._interval())
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_pass_cls(self, client):
        def callback(pipeline_response, deserialized, _):
            return "cls result"

        async with client:
            res = await (await client.begin_analyze_batch_actions(
                documents=["Test passing cls to endpoint"],
                actions=[
                    RecognizeEntitiesAction(),
                ],
                cls=callback,
                polling_interval=self._interval()
            )).result()
            assert res == "cls result"

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_multiple_pages_of_results_returned_successfully(self, client):
        single_doc = "hello world"
        docs = [{"id": str(idx), "text": val} for (idx, val) in
                enumerate(list(itertools.repeat(single_doc, 25)))]  # max number of documents is 25

        async with client:
            result = await (await client.begin_analyze_batch_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(),
                    ExtractKeyPhrasesAction(),
                    RecognizePiiEntitiesAction(),
                ],
                show_stats=True,
                polling_interval=self._interval()
            )).result()

            pages = []
            async for p in result:
                pages.append(p)

            recognize_entities_results = []
            extract_key_phrases_results = []
            recognize_pii_entities_results = []

            for idx, action_result in enumerate(pages):
                if idx % 3 == 0:
                    assert action_result.action_type == AnalyzeBatchActionsType.RECOGNIZE_ENTITIES
                    recognize_entities_results.append(action_result)
                elif idx % 3 == 1:
                    assert action_result.action_type == AnalyzeBatchActionsType.EXTRACT_KEY_PHRASES
                    extract_key_phrases_results.append(action_result)
                else:
                    assert action_result.action_type == AnalyzeBatchActionsType.RECOGNIZE_PII_ENTITIES
                    recognize_pii_entities_results.append(action_result)
                if idx < 3:  # first page of task results
                    assert len(action_result.document_results) == 20
                else:
                    assert len(action_result.document_results) == 5

            assert all([action_result for action_result in recognize_entities_results if len(action_result.document_results) == len(docs)])
            assert all([action_result for action_result in extract_key_phrases_results if len(action_result.document_results) == len(docs)])
            assert all([action_result for action_result in recognize_pii_entities_results if len(action_result.document_results) == len(docs)])

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_multiple_pages_of_results_with_errors_returned_successfully(self, client):
        single_doc = "hello world"
        docs = [{"id": str(idx), "text": val} for (idx, val) in
                enumerate(list(itertools.repeat(single_doc, 25)))]  # max number of documents is 25

        async with client:
            result = await (await client.begin_analyze_batch_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(model_version="bad"),
                    ExtractKeyPhrasesAction(),
                    RecognizePiiEntitiesAction(),
                ],
                polling_interval=self._interval()
            )).result()

            pages = []
            async for p in result:
                pages.append(p)

            for idx, action_result in enumerate(pages):
                if idx % 3 == 0:
                    assert action_result.is_error
                else:
                    assert all([doc for doc in action_result.document_results if not doc.is_error])

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    async def test_too_many_documents(self, client):
        docs = list(itertools.repeat("input document", 26))  # Maximum number of documents per request is 25

        with pytest.raises(HttpResponseError) as excinfo:
            async with client:
                await (await client.begin_analyze_batch_actions(
                    docs,
                    actions=[
                        RecognizeEntitiesAction(),
                        ExtractKeyPhrasesAction(),
                        RecognizePiiEntitiesAction(),
                    ],
                    polling_interval=self._interval()
                )).result()
        assert excinfo.value.status_code == 400

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
import datetime

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from testcase import TextAnalyticsTest, GlobalTextAnalyticsAccountPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    RecognizeEntitiesAction,
    RecognizeLinkedEntitiesAction,
    RecognizePiiEntitiesAction,
    ExtractKeyPhrasesAction,
    TextDocumentInput,
    VERSION,
    TextAnalyticsApiVersion,
    AnalyzeBatchActionsType,
)

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)


class TestAnalyze(TextAnalyticsTest):

    def _interval(self):
        return 5 if self.is_live else 0

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_no_single_input(self, client):
        with self.assertRaises(TypeError):
            response = client.begin_analyze_batch_actions("hello world", actions=[], polling_interval=self._interval())

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_all_successful_passing_dict_key_phrase_task(self, client):
        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen"},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        response = client.begin_analyze_batch_actions(
            docs,
            actions=[ExtractKeyPhrasesAction()],
            show_stats=True,
            polling_interval=self._interval(),
        ).result()

        action_results = list(response)

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
    def test_all_successful_passing_text_document_input_entities_task(self, client):
        docs = [
            TextDocumentInput(id="1", text="Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975", language="en"),
            TextDocumentInput(id="2", text="Microsoft fue fundado por Bill Gates y Paul Allen el 4 de abril de 1975.", language="es"),
            TextDocumentInput(id="3", text="Microsoft wurde am 4. April 1975 von Bill Gates und Paul Allen gegründet.", language="de"),
        ]

        response = client.begin_analyze_batch_actions(
            docs,
            actions=[RecognizeEntitiesAction()],
            show_stats=True,
            polling_interval=self._interval(),
        ).result()

        action_results = list(response)

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
    def test_all_successful_passing_string_pii_entities_task(self, client):

        docs = ["My SSN is 859-98-0987.",
                "Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check.",
                "Is 998.214.865-68 your Brazilian CPF number?"
        ]

        response = client.begin_analyze_batch_actions(
            docs,
            actions=[RecognizePiiEntitiesAction()],
            show_stats=True,
            polling_interval=self._interval(),
        ).result()

        action_results = list(response)

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
    def test_bad_request_on_empty_document(self, client):
        docs = [u""]

        with self.assertRaises(HttpResponseError):
            response = client.begin_analyze_batch_actions(
                docs,
                actions=[ExtractKeyPhrasesAction()],
                polling_interval=self._interval(),
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "text_analytics_account_key": "",
    })
    def test_empty_credential_class(self, client):
        with self.assertRaises(ClientAuthenticationError):
            response = client.begin_analyze_batch_actions(
                ["This is written in English."],
                actions=[
                    RecognizeEntitiesAction(),
                    ExtractKeyPhrasesAction(),
                    RecognizePiiEntitiesAction(),
                ],
                polling_interval=self._interval(),
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "text_analytics_account_key": "xxxxxxxxxxxx",
    })
    def test_bad_credentials(self, client):
        with self.assertRaises(ClientAuthenticationError):
            response = client.begin_analyze_batch_actions(
                ["This is written in English."],
                actions=[
                    RecognizeEntitiesAction(),
                    ExtractKeyPhrasesAction(),
                    RecognizePiiEntitiesAction(),
                ],
                polling_interval=self._interval(),
            )
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_out_of_order_ids_multiple_tasks(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = client.begin_analyze_batch_actions(
            docs,
            actions=[
                RecognizeEntitiesAction(model_version="bad"),
                ExtractKeyPhrasesAction(),
                RecognizePiiEntitiesAction(),
            ],
            polling_interval=self._interval(),
        ).result()

        action_results = list(response)
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
    def test_show_stats_and_model_version_multiple_tasks(self, client):

        def callback(resp):
            if resp.raw_response:
                a = "b"

        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        poller = client.begin_analyze_batch_actions(
            docs,
            actions=[
                RecognizeEntitiesAction(model_version="latest"),
                ExtractKeyPhrasesAction(model_version="latest"),
                RecognizePiiEntitiesAction(model_version="latest"),
                RecognizeLinkedEntitiesAction(model_version="latest")
            ],
            show_stats=True,
            polling_interval=self._interval(),
            raw_response_hook=callback,
        )

        response = poller.result()

        action_results = list(response)
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
    def test_poller_metadata(self, client):
        docs = [{"id": "56", "text": ":)"}]

        poller = client.begin_analyze_batch_actions(
            docs,
            actions=[
                RecognizeEntitiesAction(model_version="latest")
            ],
            show_stats=True,
            polling_interval=self._interval(),
        )

        response = poller.result()

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
    # def test_whole_batch_language_hint(self, client):
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

    #     response = list(client.begin_analyze_batch_actions(
    #         docs,
    #         actions=[
    #             RecognizeEntitiesAction(),
    #             ExtractKeyPhrasesAction(),
    #             RecognizePiiEntitiesAction()
    #         ],
    #         language="fr",
    #         polling_interval=self._interval(),
    #         raw_response_hook=callback
    #     ).result())

    #     for action_result in response:
    #         for doc in action_result.document_results:
    #             self.assertFalse(doc.is_error)

    # @GlobalTextAnalyticsAccountPreparer()
    # @TextAnalyticsClientPreparer(client_kwargs={
    #     "default_language": "en"
    # })
    # def test_whole_batch_language_hint_and_obj_per_item_hints(self, client):
    #     def callback(resp):
    #         pass
    #         # if resp.http_request.body:
    #         #     language_str = "\"language\": \"es\""
    #         #     language = resp.http_request.body.count(language_str)
    #         #     self.assertEqual(language, 2)
    #         #     language_str = "\"language\": \"en\""
    #         #     language = resp.http_request.body.count(language_str)
    #         #     self.assertEqual(language, 1)

    #     docs = [
    #         TextDocumentInput(id="1", text="I should take my cat to the veterinarian.", language="es"),
    #         TextDocumentInput(id="2", text="Este es un document escrito en Español.", language="es"),
    #         TextDocumentInput(id="3", text="猫は幸せ"),
    #     ]

    #     response = list(client.begin_analyze_batch_actions(
    #         docs,
    #         actions=[
    #             RecognizeEntitiesAction(),
    #             ExtractKeyPhrasesAction(),
    #             RecognizePiiEntitiesAction()
    #         ],
    #         polling_interval=self._interval(),
    #     ).result())

    #     for action_result in response:
    #         for doc in action_result.document_results:
    #             assert not doc.is_error

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_invalid_language_hint_method(self, client):
        response = list(client.begin_analyze_batch_actions(
            ["This should fail because we're passing in an invalid language hint"],
            language="notalanguage",
            actions=[
                RecognizeEntitiesAction(),
                ExtractKeyPhrasesAction(),
                RecognizePiiEntitiesAction()
            ],
            polling_interval=self._interval(),
        ).result())

        for action_result in response:
            for doc in action_result.document_results:
                assert doc.is_error


    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_bad_model_version_error_multiple_tasks(self, client):  # TODO: verify behavior of service
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        response = client.begin_analyze_batch_actions(
            docs,
            actions=[
                RecognizeEntitiesAction(model_version="latest"),
                ExtractKeyPhrasesAction(model_version="bad"),
                RecognizePiiEntitiesAction(model_version="bad"),
                RecognizeLinkedEntitiesAction(model_version="bad")
            ],
            polling_interval=self._interval(),
        ).result()

        action_results = list(response)
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
    def test_bad_model_version_error_all_tasks(self, client):  # TODO: verify behavior of service
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        with self.assertRaises(HttpResponseError):
            response = client.begin_analyze_batch_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(model_version="bad"),
                    ExtractKeyPhrasesAction(model_version="bad"),
                    RecognizePiiEntitiesAction(model_version="bad")
                ],
                polling_interval=self._interval(),
            ).result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_missing_input_records_error(self, client):
        docs = []
        with pytest.raises(ValueError) as excinfo:
            client.begin_analyze_batch_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(),
                    ExtractKeyPhrasesAction(),
                    RecognizePiiEntitiesAction()
                ],
                polling_interval=self._interval(),
            )
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_passing_none_docs(self, client):
        with pytest.raises(ValueError) as excinfo:
            client.begin_analyze_batch_actions(None, None)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_pass_cls(self, client):
        def callback(pipeline_response, deserialized, _):
            return "cls result"
        res = client.begin_analyze_batch_actions(
            documents=["Test passing cls to endpoint"],
            actions=[
                RecognizeEntitiesAction(),
            ],
            cls=callback,
            polling_interval=self._interval(),
        ).result()
        assert res == "cls result"

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_multiple_pages_of_results_returned_successfully(self, client):
        single_doc = "hello world"
        docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 25)))] # max number of documents is 25

        result = client.begin_analyze_batch_actions(
            docs,
            actions=[
                RecognizeEntitiesAction(),
                ExtractKeyPhrasesAction(),
                RecognizePiiEntitiesAction()
            ],
            show_stats=True,
            polling_interval=self._interval(),
        ).result()

        recognize_entities_results = []
        extract_key_phrases_results = []
        recognize_pii_entities_results = []

        action_results = list(result)

        # do 2 pages of 3 task results
        for idx, action_result in enumerate(action_results):
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
    def test_too_many_documents(self, client):
        docs = list(itertools.repeat("input document", 26))  # Maximum number of documents per request is 25

        with pytest.raises(HttpResponseError) as excinfo:
            client.begin_analyze_batch_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(),
                    ExtractKeyPhrasesAction(),
                    RecognizePiiEntitiesAction()
                ],
                polling_interval=self._interval(),
            )
        assert excinfo.value.status_code == 400

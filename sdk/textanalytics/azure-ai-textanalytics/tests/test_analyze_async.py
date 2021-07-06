# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from collections import defaultdict
import datetime
import os
import pytest
import platform
import functools
import itertools
import json
import time

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from testcase import TextAnalyticsPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from asynctestcase import AsyncTextAnalyticsTest
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.ai.textanalytics import (
    TextDocumentInput,
    RecognizeEntitiesAction,
    RecognizeLinkedEntitiesAction,
    RecognizePiiEntitiesAction,
    ExtractKeyPhrasesAction,
    AnalyzeSentimentAction,
    _AnalyzeActionsType,
    RecognizePiiEntitiesResult,
    RecognizeEntitiesResult,
    RecognizeLinkedEntitiesResult,
    AnalyzeSentimentResult,
    ExtractKeyPhrasesResult,
    PiiEntityCategory
)

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)


class TestAnalyzeAsync(AsyncTextAnalyticsTest):

    def _interval(self):
        return 5 if self.is_live else 0

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_no_single_input(self, client):
        with self.assertRaises(TypeError):
            response = await client.begin_analyze_actions("hello world", actions=[], polling_interval=self._interval())

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_all_successful_passing_dict_key_phrase_task(self, client):
        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen"},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        async with client:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=[ExtractKeyPhrasesAction()],
                show_stats=True,
                polling_interval=self._interval()
            )).result()

            document_results = []
            async for p in response:
                document_results.append(p)
            assert len(document_results) == 2

            for document_result in document_results:
                assert len(document_result) == 1
                for document_result in document_result:
                    assert isinstance(document_result, ExtractKeyPhrasesResult)
                    assert "Paul Allen" in document_result.key_phrases
                    assert "Bill Gates" in document_result.key_phrases
                    assert "Microsoft" in document_result.key_phrases
                    assert document_result.id is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_all_successful_passing_dict_sentiment_task(self, client):
        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
                {"id": "2", "language": "en", "text": "I did not like the hotel we stayed at. It was too expensive."},
                {"id": "3", "language": "en", "text": "The restaurant had really good food. I recommend you try it."}]

        async with client:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=[AnalyzeSentimentAction()],
                show_stats=True,
                polling_interval=self._interval(),
            )).result()

        pages = []
        async for p in response:
            pages.append(p)

        assert len(pages) == len(docs)

        for idx, document_results in enumerate(pages):
            assert len(document_results) == 1
            document_result = document_results[0]
            assert isinstance(document_result, AnalyzeSentimentResult)
            assert document_result.id is not None
            assert document_result.statistics is not None
            self.validateConfidenceScores(document_result.confidence_scores)
            assert document_result.sentences is not None
            if idx == 0:
                assert document_result.sentiment == "neutral"
                assert len(document_result.sentences) == 1
                assert document_result.sentences[0].text == "Microsoft was founded by Bill Gates and Paul Allen."
            elif idx == 1:
                assert document_result.sentiment == "negative"
                assert len(document_result.sentences) == 2
                assert document_result.sentences[0].text == "I did not like the hotel we stayed at."
                assert document_result.sentences[1].text == "It was too expensive."
            else:
                assert document_result.sentiment == "positive"
                assert len(document_result.sentences) == 2
                assert document_result.sentences[0].text == "The restaurant had really good food."
                assert document_result.sentences[1].text == "I recommend you try it."

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_sentiment_analysis_task_with_opinion_mining(self, client):
        documents = [
            "It has a sleek premium aluminum design that makes it beautiful to look at.",
            "The food and service is not good"
        ]

        async with client:
            response = await (await client.begin_analyze_actions(
                documents,
                actions=[AnalyzeSentimentAction(show_opinion_mining=True)],
                show_stats=True,
                polling_interval=self._interval(),
            )).result()

        pages = []
        async for p in response:
            pages.append(p)

        assert len(pages) == len(documents)

        for idx, document_results in enumerate(pages):
            assert len(document_results) == 1
            document_result = document_results[0]
            assert isinstance(document_result, AnalyzeSentimentResult)
            for sentence in document_result.sentences:
                if idx == 0:
                    for mined_opinion in sentence.mined_opinions:
                        target = mined_opinion.target
                        self.assertEqual('design', target.text)
                        self.assertEqual('positive', target.sentiment)
                        self.assertEqual(0.0, target.confidence_scores.neutral)
                        self.validateConfidenceScores(target.confidence_scores)
                        self.assertEqual(32, target.offset)

                        sleek_opinion = mined_opinion.assessments[0]
                        self.assertEqual('sleek', sleek_opinion.text)
                        self.assertEqual('positive', sleek_opinion.sentiment)
                        self.assertEqual(0.0, sleek_opinion.confidence_scores.neutral)
                        self.validateConfidenceScores(sleek_opinion.confidence_scores)
                        self.assertEqual(9, sleek_opinion.offset)
                        self.assertFalse(sleek_opinion.is_negated)

                        premium_opinion = mined_opinion.assessments[1]
                        self.assertEqual('premium', premium_opinion.text)
                        self.assertEqual('positive', premium_opinion.sentiment)
                        self.assertEqual(0.0, premium_opinion.confidence_scores.neutral)
                        self.validateConfidenceScores(premium_opinion.confidence_scores)
                        self.assertEqual(15, premium_opinion.offset)
                        self.assertFalse(premium_opinion.is_negated)
                else:
                    food_target = sentence.mined_opinions[0].target
                    service_target = sentence.mined_opinions[1].target
                    self.validateConfidenceScores(food_target.confidence_scores)
                    self.assertEqual(4, food_target.offset)

                    self.assertEqual('service', service_target.text)
                    self.assertEqual('negative', service_target.sentiment)
                    self.assertEqual(0.0, service_target.confidence_scores.neutral)
                    self.validateConfidenceScores(service_target.confidence_scores)
                    self.assertEqual(13, service_target.offset)

                    food_opinion = sentence.mined_opinions[0].assessments[0]
                    service_opinion = sentence.mined_opinions[1].assessments[0]
                    self.assertOpinionsEqual(food_opinion, service_opinion)

                    self.assertEqual('good', food_opinion.text)
                    self.assertEqual('negative', food_opinion.sentiment)
                    self.assertEqual(0.0, food_opinion.confidence_scores.neutral)
                    self.validateConfidenceScores(food_opinion.confidence_scores)
                    self.assertEqual(28, food_opinion.offset)
                    self.assertTrue(food_opinion.is_negated)
                    service_target = sentence.mined_opinions[1].target

                    self.assertEqual('food', food_target.text)
                    self.assertEqual('negative', food_target.sentiment)
                    self.assertEqual(0.0, food_target.confidence_scores.neutral)
    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_all_successful_passing_text_document_input_entities_task(self, client):
        docs = [
            TextDocumentInput(id="1", text="Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975", language="en"),
            TextDocumentInput(id="2", text="Microsoft fue fundado por Bill Gates y Paul Allen el 4 de abril de 1975.", language="es"),
            TextDocumentInput(id="3", text="Microsoft wurde am 4. April 1975 von Bill Gates und Paul Allen gegründet.", language="de"),
        ]

        async with client:
            poller = await client.begin_analyze_actions(
                docs,
                actions=[RecognizeEntitiesAction()],
                show_stats=True,
                polling_interval=self._interval(),
            )
            response = await poller.result()

            pages = []
            async for p in response:
                pages.append(p)
            assert len(pages) == len(docs)

            for document_results in pages:
                assert len(document_results) == 1
                document_result = document_results[0]
                assert isinstance(document_result, RecognizeEntitiesResult)
                assert len(document_result.entities) == 4
                assert document_result.id is not None
                for entity in document_result.entities:
                    assert entity.text is not None
                    assert entity.category is not None
                    assert entity.offset is not None
                    assert entity.confidence_score is not None
                    self.assertIsNotNone(entity.category)
                    self.assertIsNotNone(entity.offset)
                    self.assertIsNotNone(entity.confidence_score)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_all_successful_passing_string_pii_entities_task(self, client):

        docs = ["My SSN is 859-98-0987.",
                "Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check.",
                "Is 998.214.865-68 your Brazilian CPF number?"
        ]

        async with client:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=[RecognizePiiEntitiesAction()],
                show_stats=True,
                polling_interval=self._interval()
            )).result()

            pages = []
            async for p in response:
                pages.append(p)
            assert len(pages) == len(docs)

            for idx, document_results in enumerate(pages):
                assert len(document_results) == 1
                document_result = document_results[0]
                assert isinstance(document_result, RecognizePiiEntitiesResult)
                if idx == 0:
                    assert document_result.entities[0].text == "859-98-0987"
                    assert document_result.entities[0].category == "USSocialSecurityNumber"
                elif idx == 1:
                    assert document_result.entities[0].text == "111000025"
                for entity in document_result.entities:
                    assert entity.text is not None
                    assert entity.category is not None
                    assert entity.offset is not None
                    assert entity.confidence_score is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_bad_request_on_empty_document(self, client):
        docs = [u""]

        with self.assertRaises(HttpResponseError):
            async with client:
                await (await client.begin_analyze_actions(
                    docs,
                    actions=[ExtractKeyPhrasesAction()],
                    polling_interval=self._interval()
                )).result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "textanalytics_test_api_key": "",
    })
    async def test_empty_credential_class(self, client):
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                await (await client.begin_analyze_actions(
                    ["This is written in English."],
                    actions=[
                        RecognizeEntitiesAction(),
                        ExtractKeyPhrasesAction(),
                        RecognizePiiEntitiesAction(),
                        RecognizeLinkedEntitiesAction(),
                        AnalyzeSentimentAction()
                    ],
                    polling_interval=self._interval()
                )).result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "textanalytics_test_api_key": "xxxxxxxxxxxx"
    })
    async def test_bad_credentials(self, client):
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                await (await client.begin_analyze_actions(
                    ["This is written in English."],
                    actions=[
                        RecognizeEntitiesAction(),
                        ExtractKeyPhrasesAction(),
                        RecognizePiiEntitiesAction(),
                        RecognizeLinkedEntitiesAction(),
                        AnalyzeSentimentAction()
                    ],
                    polling_interval=self._interval()
                )).result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_out_of_order_ids_multiple_tasks(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        async with client:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(),
                    ExtractKeyPhrasesAction(),
                    RecognizePiiEntitiesAction(),
                    RecognizeLinkedEntitiesAction(),
                    AnalyzeSentimentAction()
                ],
                polling_interval=self._interval()
            )).result()

            results = []
            async for p in response:
                results.append(p)
            assert len(results) == len(docs)

            document_order = ["56", "0", "19", "1"]
            action_order = [
                _AnalyzeActionsType.RECOGNIZE_ENTITIES,
                _AnalyzeActionsType.EXTRACT_KEY_PHRASES,
                _AnalyzeActionsType.RECOGNIZE_PII_ENTITIES,
                _AnalyzeActionsType.RECOGNIZE_LINKED_ENTITIES,
                _AnalyzeActionsType.ANALYZE_SENTIMENT,
            ]
            for doc_idx, document_results in enumerate(results):
                assert len(document_results) == 5
                for action_idx, document_result in enumerate(document_results):
                    self.assertEqual(document_result.id, document_order[doc_idx])
                    self.assertEqual(self.document_result_to_action_type(document_result), action_order[action_idx])


    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_show_stats_and_model_version_multiple_tasks(self, client):

        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        def callback(resp):
            assert resp.raw_response
            tasks = resp.raw_response['tasks']
            assert tasks['completed'] == 5
            assert tasks['inProgress'] == 0
            assert tasks['failed'] == 0
            assert tasks['total'] == 5
            num_tasks = 0
            for key, task in tasks.items():
                if "Tasks" in key:
                    num_tasks += 1
                    assert len(task) == 1
                    task_stats = task[0]['results']['statistics']
                    assert task_stats['documentsCount'] == 4
                    assert task_stats['validDocumentsCount'] == 4
                    assert task_stats['erroneousDocumentsCount'] == 0
                    assert task_stats['transactionsCount'] == 4
            assert num_tasks == 5

        async with client:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(model_version="latest"),
                    ExtractKeyPhrasesAction(model_version="latest"),
                    RecognizePiiEntitiesAction(model_version="latest"),
                    RecognizeLinkedEntitiesAction(model_version="latest"),
                    AnalyzeSentimentAction(model_version="latest")
                ],
                show_stats=True,
                polling_interval=self._interval(),
                raw_response_hook=callback,
            )).result()

            pages = []
            async for p in response:
                pages.append(p)
            assert len(pages) == len(docs)

            action_order = [
                _AnalyzeActionsType.RECOGNIZE_ENTITIES,
                _AnalyzeActionsType.EXTRACT_KEY_PHRASES,
                _AnalyzeActionsType.RECOGNIZE_PII_ENTITIES,
                _AnalyzeActionsType.RECOGNIZE_LINKED_ENTITIES,
                _AnalyzeActionsType.ANALYZE_SENTIMENT,
            ]
            for document_results in pages:
                assert len(document_results) == len(action_order)
                for document_result in document_results:
                    assert document_result.statistics
                    assert document_result.statistics.character_count
                    assert document_result.statistics.transaction_count

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_poller_metadata(self, client):
        docs = [{"id": "56", "text": ":)"}]

        async with client:
            poller = await client.begin_analyze_actions(
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

    # @TextAnalyticsPreparer()
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
    #         response = await (await client.begin_analyze_actions(
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


    # @TextAnalyticsPreparer()
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
    #         response = await (await client.begin_analyze_actions(
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

    # @TextAnalyticsPreparer()
    # @TextAnalyticsClientPreparer()
    # async def test_invalid_language_hint_method(self, client):
    #     async with client:
    #         response = await (await client.begin_analyze_actions(
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

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_bad_model_version_error_multiple_tasks(self, client):
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        async with client:
            with pytest.raises(HttpResponseError):
                response = await (await
                client.begin_analyze_actions(
                    docs,
                    actions=[
                        RecognizeEntitiesAction(model_version="latest"),
                        ExtractKeyPhrasesAction(model_version="bad"),
                        RecognizePiiEntitiesAction(model_version="bad"),
                        RecognizeLinkedEntitiesAction(model_version="bad"),
                        AnalyzeSentimentAction(model_version="bad")
                    ],
                    polling_interval=self._interval()
                )).result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_bad_model_version_error_all_tasks(self, client):  # TODO: verify behavior of service
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        with self.assertRaises(HttpResponseError):
            async with client:
                result = await (await client.begin_analyze_actions(
                    docs,
                    actions=[
                        RecognizeEntitiesAction(model_version="bad"),
                        ExtractKeyPhrasesAction(model_version="bad"),
                        RecognizePiiEntitiesAction(model_version="bad"),
                        RecognizeLinkedEntitiesAction(model_version="bad"),
                        AnalyzeSentimentAction(model_version="bad")
                    ],
                    polling_interval=self._interval()
                )).result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_missing_input_records_error(self, client):
        docs = []
        with pytest.raises(ValueError) as excinfo:
            async with client:
                await (await client.begin_analyze_actions(
                    docs,
                    actions=[
                        RecognizeEntitiesAction(),
                        ExtractKeyPhrasesAction(),
                        RecognizePiiEntitiesAction(),
                        RecognizeLinkedEntitiesAction(),
                        AnalyzeSentimentAction()
                    ],
                    polling_interval=self._interval()
                )).result()
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_passing_none_docs(self, client):
        with pytest.raises(ValueError) as excinfo:
            async with client:
                await client.begin_analyze_actions(None, None, polling_interval=self._interval())
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_pass_cls(self, client):
        def callback(pipeline_response, deserialized, _):
            return "cls result"

        async with client:
            res = await (await client.begin_analyze_actions(
                documents=["Test passing cls to endpoint"],
                actions=[
                    RecognizeEntitiesAction(),
                ],
                cls=callback,
                polling_interval=self._interval()
            )).result()
            assert res == "cls result"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_multiple_pages_of_results_returned_successfully(self, client):
        single_doc = "hello world"
        docs = [{"id": str(idx), "text": val} for (idx, val) in
                enumerate(list(itertools.repeat(single_doc, 25)))]  # max number of documents is 25

        async with client:
            result = await (await client.begin_analyze_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(),
                    ExtractKeyPhrasesAction(),
                    RecognizePiiEntitiesAction(),
                    RecognizeLinkedEntitiesAction(),
                    AnalyzeSentimentAction()
                ],
                show_stats=True,
                polling_interval=self._interval()
            )).result()

            pages = []
            async for p in result:
                pages.append(p)

            assert len(pages) == len(docs)
        action_order = [
            _AnalyzeActionsType.RECOGNIZE_ENTITIES,
            _AnalyzeActionsType.EXTRACT_KEY_PHRASES,
            _AnalyzeActionsType.RECOGNIZE_PII_ENTITIES,
            _AnalyzeActionsType.RECOGNIZE_LINKED_ENTITIES,
            _AnalyzeActionsType.ANALYZE_SENTIMENT,
        ]
        action_type_to_document_results = defaultdict(list)

        for doc_idx, page in enumerate(pages):
            for action_idx, document_result in enumerate(page):
                self.assertEqual(document_result.id, str(doc_idx))
                action_type = self.document_result_to_action_type(document_result)
                self.assertEqual(action_type, action_order[action_idx])
                action_type_to_document_results[action_type].append(document_result)

        assert len(action_type_to_document_results) == len(action_order)
        for document_results in action_type_to_document_results.values():
            assert len(document_results) == len(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_too_many_documents(self, client):
        docs = list(itertools.repeat("input document", 26))  # Maximum number of documents per request is 25

        with pytest.raises(HttpResponseError) as excinfo:
            async with client:
                await (await client.begin_analyze_actions(
                    docs,
                    actions=[
                        RecognizeEntitiesAction(),
                        ExtractKeyPhrasesAction(),
                        RecognizePiiEntitiesAction(),
                        RecognizeLinkedEntitiesAction(),
                        AnalyzeSentimentAction()
                    ],
                    polling_interval=self._interval()
                )).result()
        assert excinfo.value.status_code == 400

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_disable_service_logs(self, client):
        actions = [
            RecognizeEntitiesAction(disable_service_logs=True),
            ExtractKeyPhrasesAction(disable_service_logs=True),
            RecognizePiiEntitiesAction(disable_service_logs=True),
            RecognizeLinkedEntitiesAction(disable_service_logs=True),
            AnalyzeSentimentAction(disable_service_logs=True),
        ]

        for action in actions:
            assert action.disable_service_logs

        await (await client.begin_analyze_actions(
            documents=["Test for logging disable"],
            actions=actions,
            polling_interval=self._interval(),
        )).result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_pii_action_categories_filter(self, client):

        docs = [{"id": "1", "text": "My SSN is 859-98-0987."},
                {"id": "2",
                 "text": "Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check."},
                {"id": "3", "text": "Is 998.214.865-68 your Brazilian CPF number?"}]

        actions = [
            RecognizePiiEntitiesAction(
                categories_filter=[
                    PiiEntityCategory.US_SOCIAL_SECURITY_NUMBER,
                    PiiEntityCategory.ABA_ROUTING_NUMBER
                ]
            ),
        ]
        async with client:
            result = await (await client.begin_analyze_actions(documents=docs, actions=actions, polling_interval=self._interval())).result()
            action_results = []
            async for p in result:
                action_results.append(p)

        assert len(action_results) == 3

        assert action_results[0][0].entities[0].text == "859-98-0987"
        assert action_results[0][0].entities[0].category == PiiEntityCategory.US_SOCIAL_SECURITY_NUMBER
        assert action_results[1][0].entities[0].text == "111000025"
        assert action_results[1][0].entities[0].category == PiiEntityCategory.ABA_ROUTING_NUMBER
        assert action_results[2][0].entities == []  # No Brazilian CPF since not in categories_filter

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_partial_success_for_actions(self, client):
        docs = [{"id": "1", "language": "tr", "text": "I did not like the hotel we stayed at."},
                {"id": "2", "language": "en", "text": "I did not like the hotel we stayed at."}]

        async with client:
            response = await (await client.begin_analyze_actions(
                    docs,
                    actions=[
                        AnalyzeSentimentAction(),
                        RecognizePiiEntitiesAction(),
                    ],
                    polling_interval=self._interval(),
                )).result()

            action_results = []
            async for p in response:
                action_results.append(p)
        assert len(action_results) == len(docs)
        action_order = [
            _AnalyzeActionsType.ANALYZE_SENTIMENT,
            _AnalyzeActionsType.RECOGNIZE_PII_ENTITIES,
        ]

        assert len(action_results[0]) == len(action_order)
        assert len(action_results[1]) == len(action_order)

        # first doc
        assert isinstance(action_results[0][0], AnalyzeSentimentResult)
        assert action_results[0][0].id == "1"
        assert action_results[0][1].is_error
        assert action_results[0][1].id == "1"

        # second doc
        assert isinstance(action_results[1][0], AnalyzeSentimentResult)
        assert action_results[1][0].id == "2"
        assert isinstance(action_results[1][1], RecognizePiiEntitiesResult)
        assert action_results[1][1].id == "2"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_multiple_of_same_action_fail(self, client):
        docs = [{"id": "1", "language": "en", "text": "I did not like the hotel we stayed at."},
                {"id": "2", "language": "en", "text": "I did not like the hotel we stayed at."}]

        with pytest.raises(ValueError) as e:
            await client.begin_analyze_actions(
                docs,
                actions=[
                    RecognizePiiEntitiesAction(domain_filter="phi"),
                    RecognizePiiEntitiesAction(),
                ],
                polling_interval=self._interval(),
            )
        assert "Multiple of the same action is not currently supported." in str(e.value)

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from collections import defaultdict
import datetime
import os
import pytest
import functools
import itertools
import json
import sys
import asyncio
from unittest import mock

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from testcase import TextAnalyticsPreparer, is_public_cloud
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from devtools_testutils import set_bodiless_matcher
from devtools_testutils.aio import recorded_by_proxy_async
from testcase import TextAnalyticsTest
from azure.ai.textanalytics.aio._lro_async import AsyncAnalyzeActionsLROPoller
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
    PiiEntityCategory,
    SingleLabelClassifyAction,
    MultiCategoryClassifyAction,
    RecognizeCustomEntitiesAction,
    ClassifyDocumentResult,
    RecognizeCustomEntitiesResult,
    AnalyzeHealthcareEntitiesAction
)

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)

TextAnalyticsCustomPreparer = functools.partial(
    TextAnalyticsPreparer,
    textanalytics_custom_text_endpoint="https://fakeendpoint.cognitiveservices.azure.com",
    textanalytics_custom_text_key="fakeZmFrZV9hY29jdW50X2tleQ==",
    textanalytics_single_label_classify_project_name="single_label_classify_project_name",
    textanalytics_single_label_classify_deployment_name="single_label_classify_deployment_name",
    textanalytics_multi_category_classify_project_name="multi_category_classify_project_name",
    textanalytics_multi_category_classify_deployment_name="multi_category_classify_deployment_name",
    textanalytics_custom_entities_project_name="custom_entities_project_name",
    textanalytics_custom_entities_deployment_name="custom_entities_deployment_name",
)

def get_completed_future(result=None):
    future = asyncio.Future()
    future.set_result(result)
    return future


def wrap_in_future(fn):
    """Return a completed Future whose result is the return of fn.
    Added to simplify using unittest.Mock in async code. Python 3.8's AsyncMock would be preferable.
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        return get_completed_future(result)
    return wrapper


class AsyncMockTransport(mock.MagicMock):
    """Mock with do-nothing aenter/exit for mocking async transport.

    This is unnecessary on 3.8+, where MagicMocks implement aenter/exit.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if sys.version_info < (3, 8):
            self.__aenter__ = mock.Mock(return_value=get_completed_future())
            self.__aexit__ = mock.Mock(return_value=get_completed_future())

    async def sleep(self, duration):
        await asyncio.sleep(duration)


class TestAnalyzeAsync(TextAnalyticsTest):

    def _interval(self):
        return 5 if self.is_live else 0

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_no_single_input(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(TypeError):
            response = await client.begin_analyze_actions("hello world", actions=[], polling_interval=self._interval())

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
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
    @recorded_by_proxy_async
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
                assert document_result.sentences[0].text == "I did not like the hotel we stayed at. "  # https://dev.azure.com/msazure/Cognitive%20Services/_workitems/edit/14208842
                assert document_result.sentences[1].text == "It was too expensive."
            else:
                assert document_result.sentiment == "positive"
                assert len(document_result.sentences) == 2
                assert document_result.sentences[0].text == "The restaurant had really good food. "  # https://dev.azure.com/msazure/Cognitive%20Services/_workitems/edit/14208842
                assert document_result.sentences[1].text == "I recommend you try it."

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
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
                        assert 'design' == target.text
                        assert 'positive' == target.sentiment
                        assert 0.0 == target.confidence_scores.neutral
                        self.validateConfidenceScores(target.confidence_scores)
                        assert 32 == target.offset

                        sleek_opinion = mined_opinion.assessments[0]
                        assert 'sleek' == sleek_opinion.text
                        assert 'positive' == sleek_opinion.sentiment
                        assert 0.0 == sleek_opinion.confidence_scores.neutral
                        self.validateConfidenceScores(sleek_opinion.confidence_scores)
                        assert 9 == sleek_opinion.offset
                        assert not sleek_opinion.is_negated

                        beautiful_opinion = mined_opinion.assessments[1]
                        assert 'beautiful' == beautiful_opinion.text
                        assert 'positive' == beautiful_opinion.sentiment
                        assert 0.0 == beautiful_opinion.confidence_scores.neutral
                        self.validateConfidenceScores(beautiful_opinion.confidence_scores)
                        assert 53 == beautiful_opinion.offset
                        assert not beautiful_opinion.is_negated
                else:
                    food_target = sentence.mined_opinions[0].target
                    service_target = sentence.mined_opinions[1].target
                    self.validateConfidenceScores(food_target.confidence_scores)
                    assert 4 == food_target.offset

                    assert 'service' == service_target.text
                    assert 'positive' == service_target.sentiment
                    assert 0.0 == service_target.confidence_scores.neutral
                    self.validateConfidenceScores(service_target.confidence_scores)
                    assert 13 == service_target.offset

                    food_opinion = sentence.mined_opinions[0].assessments[0]
                    service_opinion = sentence.mined_opinions[1].assessments[0]
                    self.assertOpinionsEqual(food_opinion, service_opinion)

                    assert 'good' == food_opinion.text
                    assert 'negative' == food_opinion.sentiment
                    assert 0.0 == food_opinion.confidence_scores.neutral
                    self.validateConfidenceScores(food_opinion.confidence_scores)
                    assert 28 == food_opinion.offset
                    assert food_opinion.is_negated
                    service_target = sentence.mined_opinions[1].target

                    assert 'food' == food_target.text
                    assert 'negative' == food_target.sentiment
                    assert 0.0 == food_target.confidence_scores.neutral

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
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
                    assert entity.category is not None
                    assert entity.offset is not None
                    assert entity.confidence_score is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
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
    @recorded_by_proxy_async
    async def test_bad_request_on_empty_document(self, client):
        docs = [""]

        with pytest.raises(HttpResponseError):
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
    @recorded_by_proxy_async
    async def test_empty_credential_class(self, client):
        with pytest.raises(ClientAuthenticationError):
            async with client:
                await (await client.begin_analyze_actions(
                    ["This is written in English."],
                    actions=[
                        RecognizeEntitiesAction(),
                        ExtractKeyPhrasesAction(),
                        RecognizePiiEntitiesAction(),
                        RecognizeLinkedEntitiesAction(),
                        AnalyzeSentimentAction(),
                    ],
                    polling_interval=self._interval()
                )).result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "textanalytics_test_api_key": "xxxxxxxxxxxx"
    })
    @recorded_by_proxy_async
    async def test_bad_credentials(self, client):
        with pytest.raises(ClientAuthenticationError):
            async with client:
                await (await client.begin_analyze_actions(
                    ["This is written in English."],
                    actions=[
                        RecognizeEntitiesAction(),
                        ExtractKeyPhrasesAction(),
                        RecognizePiiEntitiesAction(),
                        RecognizeLinkedEntitiesAction(),
                        AnalyzeSentimentAction(),
                    ],
                    polling_interval=self._interval()
                )).result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
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
                    AnalyzeSentimentAction(),
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
                    assert document_result.id == document_order[doc_idx]
                    assert self.document_result_to_action_type(document_result) == action_order[action_idx]

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": "v3.1"})
    @recorded_by_proxy_async
    async def test_show_stats_and_model_version_multiple_tasks_v3_1(self, client):

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
                    AnalyzeSentimentAction(model_version="latest"),
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
    @recorded_by_proxy_async
    async def test_show_stats_and_model_version_multiple_tasks(self, client):

        def callback(resp):
            assert resp.raw_response
            tasks = resp.raw_response['tasks']
            assert tasks['completed'] == 5
            assert tasks['inProgress'] == 0
            assert tasks['failed'] == 0
            assert tasks['total'] == 5
            num_tasks = 0
            for task in tasks["items"]:
                num_tasks += 1
                task_stats = task['results']['statistics']
                assert task_stats['documentsCount'] == 4
                assert task_stats['validDocumentsCount'] == 4
                assert task_stats['erroneousDocumentsCount'] == 0
                assert task_stats['transactionsCount'] == 4
            assert num_tasks == 5

        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        async with client:
            poller = await client.begin_analyze_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(model_version="latest"),
                    ExtractKeyPhrasesAction(model_version="latest"),
                    RecognizePiiEntitiesAction(model_version="latest"),
                    RecognizeLinkedEntitiesAction(model_version="latest"),
                    AnalyzeSentimentAction(model_version="latest"),
                ],
                show_stats=True,
                polling_interval=self._interval(),
                raw_response_hook=callback,
            )

            response = await poller.result()

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
    @recorded_by_proxy_async
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

            assert isinstance(poller, AsyncAnalyzeActionsLROPoller)
            assert isinstance(poller.created_on, datetime.datetime)
            assert not poller.display_name
            assert isinstance(poller.expires_on, datetime.datetime)
            assert poller.actions_failed_count == 0
            assert poller.actions_in_progress_count == 0
            assert poller.actions_succeeded_count == 1
            assert isinstance(poller.last_modified_on, datetime.datetime)
            assert poller.total_actions_count == 1
            assert poller.id

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_bad_model_version_error_multiple_tasks(self, client):
        docs = [{"id": "1", "language": "en", "text": "I did not like the hotel we stayed at."}]

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
                        AnalyzeSentimentAction(model_version="bad"),
                    ],
                    polling_interval=self._interval()
                )).result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_bad_model_version_error_all_tasks(self, client):  # TODO: verify behavior of service
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        with pytest.raises(HttpResponseError):
            async with client:
                result = await (await client.begin_analyze_actions(
                    docs,
                    actions=[
                        RecognizeEntitiesAction(model_version="bad"),
                        ExtractKeyPhrasesAction(model_version="bad"),
                        RecognizePiiEntitiesAction(model_version="bad"),
                        RecognizeLinkedEntitiesAction(model_version="bad"),
                        AnalyzeSentimentAction(model_version="bad"),
                    ],
                    polling_interval=self._interval()
                )).result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_missing_input_records_error(self, **kwargs):
        client = kwargs.pop("client")
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
                        AnalyzeSentimentAction(),
                    ],
                    polling_interval=self._interval()
                )).result()
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    async def test_passing_none_docs(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as excinfo:
            async with client:
                await client.begin_analyze_actions(None, None, polling_interval=self._interval())
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
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
    @recorded_by_proxy_async
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
                    AnalyzeSentimentAction(),
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
                assert document_result.id == str(doc_idx)
                action_type = self.document_result_to_action_type(document_result)
                assert action_type == action_order[action_idx]
                action_type_to_document_results[action_type].append(document_result)

        assert len(action_type_to_document_results) == len(action_order)
        for document_results in action_type_to_document_results.values():
            assert len(document_results) == len(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
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
                        AnalyzeSentimentAction(),
                    ],
                    polling_interval=self._interval()
                )).result()
        assert excinfo.value.status_code == 400

    @pytest.mark.skipif(not is_public_cloud(), reason='Usgov and China Cloud are not supported')
    @TextAnalyticsCustomPreparer()
    @recorded_by_proxy_async
    async def test_disable_service_logs(
            self,
            textanalytics_custom_text_endpoint,
            textanalytics_custom_text_key,
            textanalytics_single_label_classify_project_name,
            textanalytics_single_label_classify_deployment_name,
            textanalytics_multi_category_classify_project_name,
            textanalytics_multi_category_classify_deployment_name,
            textanalytics_custom_entities_project_name,
            textanalytics_custom_entities_deployment_name
    ):
        set_bodiless_matcher()  # don't match on body for this test since we scrub the proj/deployment values
        client = TextAnalyticsClient(textanalytics_custom_text_endpoint, AzureKeyCredential(textanalytics_custom_text_key))
        actions = [
            RecognizeEntitiesAction(disable_service_logs=True),
            ExtractKeyPhrasesAction(disable_service_logs=True),
            RecognizePiiEntitiesAction(disable_service_logs=True),
            RecognizeLinkedEntitiesAction(disable_service_logs=True),
            AnalyzeSentimentAction(disable_service_logs=True),
            SingleLabelClassifyAction(
                project_name=textanalytics_single_label_classify_project_name,
                deployment_name=textanalytics_single_label_classify_deployment_name,
                disable_service_logs=True
            ),
            MultiCategoryClassifyAction(
                project_name=textanalytics_multi_category_classify_project_name,
                deployment_name=textanalytics_multi_category_classify_deployment_name,
                disable_service_logs=True
            ),
            RecognizeCustomEntitiesAction(
                project_name=textanalytics_custom_entities_project_name,
                deployment_name=textanalytics_custom_entities_deployment_name,
                disable_service_logs=True
            ),
            AnalyzeHealthcareEntitiesAction(disable_service_logs=True)
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
    @recorded_by_proxy_async
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
    @recorded_by_proxy_async
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
    @recorded_by_proxy_async
    async def test_multiple_of_same_action(self, client):
        docs = [
            {"id": "28", "text": "My SSN is 859-98-0987. Here is another sentence."},
            {"id": "3", "text": "Is 998.214.865-68 your Brazilian CPF number? Here is another sentence."},
            {"id": "5", "language": "en", "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
        ]

        actions = [
            AnalyzeSentimentAction(),
            RecognizePiiEntitiesAction(),
            RecognizeEntitiesAction(),
            RecognizeLinkedEntitiesAction(),
            RecognizePiiEntitiesAction(categories_filter=[PiiEntityCategory.US_SOCIAL_SECURITY_NUMBER]),
            ExtractKeyPhrasesAction(),
            RecognizeEntitiesAction(),
            AnalyzeSentimentAction(show_opinion_mining=True),
            RecognizeLinkedEntitiesAction(),
            ExtractKeyPhrasesAction(),
        ]
        async with client:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=actions,
                polling_interval=self._interval(),
            )).result()

            action_results = []
            async for p in response:
                action_results.append(p)
        assert len(action_results) == len(docs)
        assert len(action_results[0]) == len(actions)
        assert len(action_results[1]) == len(actions)
        assert len(action_results[2]) == len(actions)

        for idx, action_result in enumerate(action_results):
            if idx == 0:
                doc_id = "28"
            elif idx == 1:
                doc_id = "3"
            else:
                doc_id = "5"

            assert isinstance(action_result[0], AnalyzeSentimentResult)
            assert not all([sentence.mined_opinions for sentence in action_result[0].sentences])
            assert action_result[0].id == doc_id

            assert isinstance(action_result[1], RecognizePiiEntitiesResult)
            assert action_result[1].id == doc_id

            assert isinstance(action_result[2], RecognizeEntitiesResult)
            assert action_result[2].id == doc_id

            assert isinstance(action_result[3], RecognizeLinkedEntitiesResult)
            assert action_result[3].id == doc_id

            assert isinstance(action_result[4], RecognizePiiEntitiesResult)
            assert action_result[4].id == doc_id
            if doc_id == "28":
                assert action_result[4].entities
            else:
                assert not action_result[4].entities

            assert isinstance(action_result[5], ExtractKeyPhrasesResult)
            assert action_result[5].id == doc_id

            assert isinstance(action_result[6], RecognizeEntitiesResult)
            assert action_result[6].id == doc_id

            assert isinstance(action_result[7], AnalyzeSentimentResult)
            assert [sentence.mined_opinions for sentence in action_result[0].sentences]
            assert action_result[7].id == doc_id

            assert isinstance(action_result[8], RecognizeLinkedEntitiesResult)
            assert action_result[8].id == doc_id

            assert isinstance(action_result[9], ExtractKeyPhrasesResult)
            assert action_result[9].id == doc_id

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_multiple_of_same_action_with_partial_results(self, client):
        docs = [{"id": "5", "language": "en", "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
                {"id": "2", "text": ""}]

        actions = [
            RecognizeEntitiesAction(),
            RecognizePiiEntitiesAction(),
            RecognizeEntitiesAction(disable_service_logs=True),
        ]

        async with client:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=actions,
                polling_interval=self._interval(),
            )).result()

            action_results = []
            async for p in response:
                action_results.append(p)

        assert len(action_results) == len(docs)
        assert len(action_results[0]) == len(actions)
        assert len(action_results[1]) == len(actions)

        # first doc
        assert isinstance(action_results[0][0], RecognizeEntitiesResult)
        assert action_results[0][0].id == "5"
        assert isinstance(action_results[0][1], RecognizePiiEntitiesResult)
        assert action_results[0][1].id == "5"
        assert isinstance(action_results[0][2], RecognizeEntitiesResult)
        assert action_results[0][2].id == "5"

        # second doc
        assert action_results[1][0].is_error
        assert action_results[1][1].is_error
        assert action_results[1][2].is_error

    @pytest.mark.skipif(not is_public_cloud(), reason='Usgov and China Cloud are not supported')
    @TextAnalyticsCustomPreparer()
    @recorded_by_proxy_async
    async def test_single_label_classify(
            self,
            textanalytics_custom_text_endpoint,
            textanalytics_custom_text_key,
            textanalytics_single_label_classify_project_name,
            textanalytics_single_label_classify_deployment_name
    ):
        set_bodiless_matcher()  # don't match on body for this test since we scrub the proj/deployment values
        client = TextAnalyticsClient(textanalytics_custom_text_endpoint, AzureKeyCredential(textanalytics_custom_text_key))
        docs = [
            {"id": "1", "language": "en", "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
            {"id": "2", "language": "en", "text": "David Schmidt, senior vice president--Food Safety, International Food Information Council (IFIC), Washington, D.C., discussed the physical activity component."},
            {"id": "3", "language": "en", "text": "I need a reservation for an indoor restaurant in China. Please don't stop the music. Play music and add it to my playlist"},
        ]

        async with client:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=[
                    SingleLabelClassifyAction(
                        project_name=textanalytics_single_label_classify_project_name,
                        deployment_name=textanalytics_single_label_classify_deployment_name
                    ),
                ],
                show_stats=True,
                polling_interval=self._interval(),
            )).result()

            document_results = []
            async for doc in response:
                document_results.append(doc)
        for doc_result in document_results:
            for result in doc_result:
                assert result.id
                assert not result.is_error
                assert not result.warnings
                assert result.statistics
                for classification in result.classifications:
                    assert classification.category
                    assert classification.confidence_score

    @pytest.mark.skipif(not is_public_cloud(), reason='Usgov and China Cloud are not supported')
    @TextAnalyticsCustomPreparer()
    @recorded_by_proxy_async
    async def test_multi_category_classify(
            self,
            textanalytics_custom_text_endpoint,
            textanalytics_custom_text_key,
            textanalytics_multi_category_classify_project_name,
            textanalytics_multi_category_classify_deployment_name
    ):
        set_bodiless_matcher()  # don't match on body for this test since we scrub the proj/deployment values
        client = TextAnalyticsClient(textanalytics_custom_text_endpoint, AzureKeyCredential(textanalytics_custom_text_key))
        docs = [
            {"id": "1", "language": "en", "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
            {"id": "2", "language": "en", "text": "David Schmidt, senior vice president--Food Safety, International Food Information Council (IFIC), Washington, D.C., discussed the physical activity component."},
            {"id": "3", "language": "en", "text": "I need a reservation for an indoor restaurant in China. Please don't stop the music. Play music and add it to my playlist"},
        ]

        async with client:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=[
                    MultiCategoryClassifyAction(
                        project_name=textanalytics_multi_category_classify_project_name,
                        deployment_name=textanalytics_multi_category_classify_deployment_name
                    ),
                ],
                show_stats=True,
                polling_interval=self._interval(),
            )).result()

            document_results = []
            async for doc in response:
                document_results.append(doc)

        for doc_result in document_results:
            for result in doc_result:
                assert result.id
                assert not result.is_error
                assert not result.warnings
                assert result.statistics
                for classification in result.classifications:
                    assert classification.category
                    assert classification.confidence_score

    @pytest.mark.skipif(not is_public_cloud(), reason='Usgov and China Cloud are not supported')
    @TextAnalyticsCustomPreparer()
    @recorded_by_proxy_async
    async def test_recognize_custom_entities(
            self,
            textanalytics_custom_text_endpoint,
            textanalytics_custom_text_key,
            textanalytics_custom_entities_project_name,
            textanalytics_custom_entities_deployment_name
    ):
        set_bodiless_matcher()  # don't match on body for this test since we scrub the proj/deployment values
        client = TextAnalyticsClient(textanalytics_custom_text_endpoint, AzureKeyCredential(textanalytics_custom_text_key))
        docs = [
            {"id": "1", "language": "en", "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
            {"id": "2", "language": "en", "text": "David Schmidt, senior vice president--Food Safety, International Food Information Council (IFIC), Washington, D.C., discussed the physical activity component."},
            {"id": "3", "language": "en", "text": "I need a reservation for an indoor restaurant in China. Please don't stop the music. Play music and add it to my playlist"},
        ]

        async with client:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=[
                    RecognizeCustomEntitiesAction(
                        project_name=textanalytics_custom_entities_project_name,
                        deployment_name=textanalytics_custom_entities_deployment_name
                    )
                ],
                show_stats=True,
                polling_interval=self._interval(),
            )).result()

            document_results = []
            async for doc in response:
                document_results.append(doc)

        for doc_result in document_results:
            for result in doc_result:
                assert result.id
                assert not result.is_error
                assert not result.warnings
                assert result.statistics
                for entity in result.entities:
                    assert entity.text
                    assert entity.category
                    assert entity.offset is not None
                    assert entity.length is not None
                    assert entity.confidence_score is not None

    @pytest.mark.skipif(not is_public_cloud(), reason='Usgov and China Cloud are not supported')
    @TextAnalyticsCustomPreparer()
    @recorded_by_proxy_async
    async def test_custom_partial_error(
            self,
            textanalytics_custom_text_endpoint,
            textanalytics_custom_text_key,
            textanalytics_single_label_classify_project_name,
            textanalytics_single_label_classify_deployment_name,
            textanalytics_multi_category_classify_project_name,
            textanalytics_multi_category_classify_deployment_name,
            textanalytics_custom_entities_project_name,
            textanalytics_custom_entities_deployment_name
    ):
        set_bodiless_matcher()  # don't match on body for this test since we scrub the proj/deployment values
        client = TextAnalyticsClient(textanalytics_custom_text_endpoint, AzureKeyCredential(textanalytics_custom_text_key))
        docs = [
            {"id": "1", "language": "en", "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
            {"id": "2", "language": "en", "text": ""},
        ]
        async with client:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=[
                    SingleLabelClassifyAction(
                        project_name=textanalytics_single_label_classify_project_name,
                        deployment_name=textanalytics_single_label_classify_deployment_name
                    ),
                    MultiCategoryClassifyAction(
                        project_name=textanalytics_multi_category_classify_project_name,
                        deployment_name=textanalytics_multi_category_classify_deployment_name
                    ),
                    RecognizeCustomEntitiesAction(
                        project_name=textanalytics_custom_entities_project_name,
                        deployment_name=textanalytics_custom_entities_deployment_name
                    )
                ],
                show_stats=True,
                polling_interval=self._interval(),
            )).result()

            document_results = []
            async for doc in response:
                document_results.append(doc)

        assert len(document_results) == 2
        assert isinstance(document_results[0][0], ClassifyDocumentResult)
        assert isinstance(document_results[0][1], ClassifyDocumentResult)
        assert isinstance(document_results[0][2], RecognizeCustomEntitiesResult)
        assert document_results[1][0].is_error
        assert document_results[1][1].is_error
        assert document_results[1][2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_analyze_continuation_token(self, client):
        docs = [
            {"id": "1", "language": "en", "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
            {"id": "2", "language": "en", "text": "David Schmidt, senior vice president--Food Safety, International Food Information Council (IFIC), Washington, D.C., discussed the physical activity component."},
            {"id": "3", "text": ""},
            {"id": "4", "language": "en", "text": "I need a reservation for an indoor restaurant in China. Please don't stop the music. Play music and add it to my playlist"},
        ]

        actions = [
            RecognizeEntitiesAction(),
            RecognizePiiEntitiesAction(),
            AnalyzeSentimentAction(),
            ExtractKeyPhrasesAction(),
        ]
        async with client:
            initial_poller = await client.begin_analyze_actions(
                docs,
                actions=actions,
                show_stats=True,
                polling_interval=self._interval(),
            )

            cont_token = initial_poller.continuation_token()

            poller = await client.begin_analyze_actions(
                None,
                None,
                continuation_token=cont_token,
                polling_interval=self._interval(),
            )
            response = await poller.result()
            assert isinstance(poller, AsyncAnalyzeActionsLROPoller)
            action_results = []
            async for action_result in response:
                action_results.append(action_result)

            assert len(action_results) == len(docs)
            action_order = [
                _AnalyzeActionsType.RECOGNIZE_ENTITIES,
                _AnalyzeActionsType.RECOGNIZE_PII_ENTITIES,
                _AnalyzeActionsType.ANALYZE_SENTIMENT,
                _AnalyzeActionsType.EXTRACT_KEY_PHRASES,
            ]
            document_order = ["1", "2", "3", "4"]
            for doc_idx, document_results in enumerate(action_results):
                assert len(document_results) == 4
                for action_idx, document_result in enumerate(document_results):
                    if doc_idx == 2:
                        assert document_result.id == document_order[doc_idx]
                        assert document_result.is_error
                    else:
                        assert document_result.id == document_order[doc_idx]
                        assert document_result.statistics
                        assert self.document_result_to_action_type(document_result) == action_order[action_idx]

            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @TextAnalyticsPreparer()
    async def test_generic_action_error_no_target_v3_1(
        self,
        **kwargs
    ):
        docs = [
            {"id": "1", "language": "en", "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
            {"id": "2", "language": "en", "text": ""},
        ]

        response = mock.MagicMock(
            status_code=200,
            headers={"Content-Type": "application/json", "operation-location": "https://fakeurl.com"}
        )
        path_to_mock_json_response = os.path.abspath(
            os.path.join(
                os.path.abspath(__file__),
                "..",
                "./mock_test_responses/action_error_no_target.json",
            )
        )
        with open(path_to_mock_json_response) as fd:
            mock_json_response = json.loads(fd.read())

        response.text = lambda encoding=None: json.dumps(mock_json_response)
        response.content_type = "application/json"
        transport = AsyncMockTransport(send=wrap_in_future(lambda request, **kwargs: response))

        endpoint = kwargs.pop("textanalytics_test_endpoint")
        key = kwargs.pop("textanalytics_test_api_key")
        client = TextAnalyticsClient(endpoint, AzureKeyCredential(key), transport=transport, api_version="v3.1")

        with pytest.raises(HttpResponseError) as e:
            async with client:
                response = await (await client.begin_analyze_actions(
                    docs,
                    actions=[
                        RecognizeEntitiesAction(),
                        RecognizeLinkedEntitiesAction(),
                        RecognizePiiEntitiesAction()
                    ],
                    show_stats=True,
                    polling_interval=self._interval(),
                )).result()
                results = []
                async for resp in response:
                    results.append(resp)
            assert e.value.message == "(InternalServerError) 1 out of 3 job tasks failed. Failed job tasks : v3.1/entities/general."

    @TextAnalyticsPreparer()
    async def test_generic_action_error_no_target(
        self,
        **kwargs
    ):
        docs = [
            {"id": "1", "language": "en", "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
            {"id": "2", "language": "en", "text": ""},
        ]

        response = mock.MagicMock(
            status_code=200,
            headers={"Content-Type": "application/json", "operation-location": "https://fakeurl.com"}
        )

        path_to_mock_json_response = os.path.abspath(
            os.path.join(
                os.path.abspath(__file__),
                "..",
                "./mock_test_responses/action_error_no_target_language.json",
            )
        )
        with open(path_to_mock_json_response) as fd:
            mock_json_response = json.loads(fd.read())

        response.text = lambda encoding=None: json.dumps(mock_json_response)
        response.content_type = "application/json"
        transport = AsyncMockTransport(send=wrap_in_future(lambda request, **kwargs: response))

        endpoint = kwargs.pop("textanalytics_test_endpoint")
        key = kwargs.pop("textanalytics_test_api_key")
        client = TextAnalyticsClient(endpoint, AzureKeyCredential(key), transport=transport)

        # workaround to get mocked response to work with deserialized polymorphic response type
        def get_deserialized_for_mock(response, deserialized, headers):
            from azure.ai.textanalytics._generated.models import AnalyzeTextJobState, AnalyzeTextJobsInput
            from azure.ai.textanalytics.aio._response_handlers_async import analyze_paged_result
            deserialized = AnalyzeTextJobState.deserialize(response.raw_response)
            return analyze_paged_result(
                ["1", "2"],
                [(_AnalyzeActionsType.RECOGNIZE_ENTITIES, '0'),
                 (_AnalyzeActionsType.EXTRACT_KEY_PHRASES, '1'),
                 (_AnalyzeActionsType.RECOGNIZE_PII_ENTITIES, '2'),
                 (_AnalyzeActionsType.RECOGNIZE_LINKED_ENTITIES, '3'),
                 (_AnalyzeActionsType.ANALYZE_SENTIMENT, '4'),
                ],
                client._client.analyze_text_job_status,
                response,
                deserialized,
                show_stats=True,
            )

        async with client:
            with pytest.raises(HttpResponseError) as e:
                response = await (await client.begin_analyze_actions(
                    docs,
                    actions=[
                        RecognizeEntitiesAction(),
                        ExtractKeyPhrasesAction(),
                        RecognizePiiEntitiesAction(),
                        RecognizeLinkedEntitiesAction(),
                        AnalyzeSentimentAction(),
                    ],
                    show_stats=True,
                    polling_interval=self._interval(),
                    raw_response_hook=lambda resp: resp,
                    cls=get_deserialized_for_mock
                )).result()
                results = []
                async for resp in response:
                    results.append(resp)
            assert e.value.message == "(InternalServerError) 1 out of 5 job tasks failed. Failed job tasks : keyphrasescomposite."

    @TextAnalyticsPreparer()
    async def test_action_errors_with_targets_v3_1(
        self,
        **kwargs
    ):
        docs = [
            {"id": "1", "language": "en", "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
            {"id": "2", "language": "en", "text": ""},
        ]

        response = mock.MagicMock(
            status_code=200,
            headers={"Content-Type": "application/json", "operation-location": "https://fakeurl.com"}
        )

        # a mix of action errors to translate to doc errors, regular doc errors, and a successful response
        path_to_mock_json_response = os.path.abspath(
            os.path.join(
                os.path.abspath(__file__),
                "..",
                "./mock_test_responses/action_error_with_targets.json",
            )
        )
        with open(path_to_mock_json_response) as fd:
            mock_json_response = json.loads(fd.read())

        response.text = lambda encoding=None: json.dumps(mock_json_response)
        response.content_type = "application/json"
        transport = AsyncMockTransport(send=wrap_in_future(lambda request, **kwargs: response))

        endpoint = kwargs.pop("textanalytics_test_endpoint")
        key = kwargs.pop("textanalytics_test_api_key")
        client = TextAnalyticsClient(endpoint, AzureKeyCredential(key), transport=transport, api_version="v3.1")

        async with client:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(),
                    ExtractKeyPhrasesAction(),
                    RecognizePiiEntitiesAction(),
                    RecognizeLinkedEntitiesAction(),
                    AnalyzeSentimentAction(),
                    RecognizePiiEntitiesAction(domain_filter="phi"),
                    AnalyzeSentimentAction(),
                ],
                show_stats=True,
                polling_interval=self._interval(),
            )).result()
            results = []
            async for resp in response:
                results.append(resp)

        assert len(results) == len(docs)
        for idx, result in enumerate(results[0]):
            assert result.id == "1"
            if idx == 6:
                assert not result.is_error
                assert isinstance(result, AnalyzeSentimentResult)
            else:
                assert result.is_error
                assert result.error.code == "InvalidRequest"
                assert result.error.message == "Some error" + str(idx)  # confirms correct doc error order

        for idx, result in enumerate(results[1]):
            assert result.id == "2"
            assert result.is_error
            if idx == 6:
                assert result.error.code == "InvalidDocument"
                assert result.error.message == "Document text is empty."
            else:
                assert result.error.code == "InvalidRequest"
                assert result.error.message == "Some error" + str(idx)  # confirms correct doc error order

    @TextAnalyticsPreparer()
    async def test_action_errors_with_targets(
        self,
        **kwargs
    ):
        docs = [
            {"id": "1", "language": "en", "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
            {"id": "2", "language": "en", "text": ""},
        ]

        response = mock.MagicMock(
            status_code=200,
            headers={"Content-Type": "application/json", "operation-location": "https://fakeurl.com"}
        )

        # a mix of action errors to translate to doc errors, regular doc errors, and a successful response
        path_to_mock_json_response = os.path.abspath(
            os.path.join(
                os.path.abspath(__file__),
                "..",
                "./mock_test_responses/action_error_with_targets_language.json",
            )
        )
        with open(path_to_mock_json_response) as fd:
            mock_json_response = json.loads(fd.read())

        response.text = lambda encoding=None: json.dumps(mock_json_response)
        response.content_type = "application/json"
        transport = AsyncMockTransport(send=wrap_in_future(lambda request, **kwargs: response))

        endpoint = kwargs.pop("textanalytics_test_endpoint")
        key = kwargs.pop("textanalytics_test_api_key")
        client = TextAnalyticsClient(endpoint, AzureKeyCredential(key), transport=transport)

        # workaround to get mocked response to work with deserialized polymorphic response type
        def get_deserialized_for_mock(response, deserialized, headers):
            from azure.ai.textanalytics._generated.models import AnalyzeTextJobState, AnalyzeTextJobsInput
            from azure.ai.textanalytics.aio._response_handlers_async import analyze_paged_result
            deserialized = AnalyzeTextJobState.deserialize(response.raw_response)

            return analyze_paged_result(
                ["1", "2"],
                [(_AnalyzeActionsType.RECOGNIZE_ENTITIES, '0'),
                 (_AnalyzeActionsType.EXTRACT_KEY_PHRASES, '1'),
                 (_AnalyzeActionsType.RECOGNIZE_PII_ENTITIES, '2'),
                 (_AnalyzeActionsType.RECOGNIZE_LINKED_ENTITIES, '3'),
                 (_AnalyzeActionsType.ANALYZE_SENTIMENT, '4'),
                 (_AnalyzeActionsType.RECOGNIZE_PII_ENTITIES, '5'),
                 (_AnalyzeActionsType.ANALYZE_SENTIMENT, '6')
                ],
                client._client.analyze_text_job_status,
                response,
                deserialized,
                show_stats=True,
            )

        async with client:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(),
                    ExtractKeyPhrasesAction(),
                    RecognizePiiEntitiesAction(),
                    RecognizeLinkedEntitiesAction(),
                    AnalyzeSentimentAction(),
                    RecognizePiiEntitiesAction(domain_filter="phi"),
                    AnalyzeSentimentAction(),
                ],
                show_stats=True,
                polling_interval=self._interval(),
                raw_response_hook=lambda resp: resp,
                cls=get_deserialized_for_mock
            )).result()
            results = []
            async for resp in response:
                results.append(resp)

        assert len(results) == len(docs)
        for idx, result in enumerate(results[0]):
            assert result.id == "1"
            if idx == 6:
                assert not result.is_error
                assert isinstance(result, AnalyzeSentimentResult)
            else:
                assert result.is_error
                assert result.error.code == "InvalidRequest"
                assert result.error.message == "Some error" + str(idx)  # confirms correct doc error order

        for idx, result in enumerate(results[1]):
            assert result.id == "2"
            assert result.is_error
            if idx == 6:
                assert result.error.code == "InvalidDocument"
                assert result.error.message == "Document text is empty."
            else:
                assert result.error.code == "InvalidRequest"
                assert result.error.message == "Some error" + str(idx)  # confirms correct doc error order

    @TextAnalyticsPreparer()
    async def test_action_job_failure_v3_1(
            self,
            **kwargs
    ):
        docs = [
            {"id": "1", "language": "en",
             "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
            {"id": "2", "language": "en", "text": ""},
        ]

        response = mock.MagicMock(
            status_code=200,
            headers={"Content-Type": "application/json", "operation-location": "https://fakeurl.com"}
        )

        # action job failure with status=="failed", no partial results so we raise an exception in this case
        path_to_mock_json_response = os.path.abspath(
            os.path.join(
                os.path.abspath(__file__),
                "..",
                "./mock_test_responses/action_job_failure.json",
            )
        )
        with open(path_to_mock_json_response) as fd:
            mock_json_response = json.loads(fd.read())

        response.text = lambda encoding=None: json.dumps(mock_json_response)
        response.content_type = "application/json"
        transport = AsyncMockTransport(send=wrap_in_future(lambda request, **kwargs: response))

        endpoint = kwargs.pop("textanalytics_test_endpoint")
        key = kwargs.pop("textanalytics_test_api_key")
        client = TextAnalyticsClient(endpoint, AzureKeyCredential(key), transport=transport, api_version="v3.1")

        async with client:
            with pytest.raises(HttpResponseError) as e:
                response = await (await client.begin_analyze_actions(
                    docs,
                    actions=[
                        RecognizeEntitiesAction(),
                    ],
                    show_stats=True,
                    polling_interval=self._interval(),
                )).result()
                results = []
                async for resp in response:
                    results.append(resp)
            assert e.value.message == "(InternalServerError) 1 out of 1 job tasks failed. Failed job tasks : v3.1/entities/general."

    @TextAnalyticsPreparer()
    async def test_action_job_failure(
            self,
            **kwargs
    ):
        docs = [
            {"id": "1", "language": "en",
             "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
            {"id": "2", "language": "en", "text": ""},
        ]

        response = mock.MagicMock(
            status_code=200,
            headers={"Content-Type": "application/json", "operation-location": "https://fakeurl.com"}
        )

        # action job failure with status=="failed", no partial results so we raise an exception in this case
        path_to_mock_json_response = os.path.abspath(
            os.path.join(
                os.path.abspath(__file__),
                "..",
                "./mock_test_responses/action_job_failure_language.json",
            )
        )
        with open(path_to_mock_json_response) as fd:
            mock_json_response = json.loads(fd.read())

        response.text = lambda encoding=None: json.dumps(mock_json_response)
        response.content_type = "application/json"
        transport = AsyncMockTransport(send=wrap_in_future(lambda request, **kwargs: response))

        endpoint = kwargs.pop("textanalytics_test_endpoint")
        key = kwargs.pop("textanalytics_test_api_key")
        client = TextAnalyticsClient(endpoint, AzureKeyCredential(key),
                                     transport=transport)

        # workaround to get mocked response to work with deserialized polymorphic response type
        def get_deserialized_for_mock(response, deserialized, headers):
            from azure.ai.textanalytics._generated.models import AnalyzeTextJobState, AnalyzeTextJobsInput
            from azure.ai.textanalytics.aio._response_handlers_async import analyze_paged_result
            deserialized = AnalyzeTextJobState.deserialize(response.raw_response)

            return analyze_paged_result(
                ["1", "2"],
                [(_AnalyzeActionsType.EXTRACT_KEY_PHRASES, '0')],
                client._client.analyze_text_job_status,
                response,
                deserialized,
                show_stats=True,
            )
        async with client:
            with pytest.raises(HttpResponseError) as e:
                response = await (await client.begin_analyze_actions(
                    docs,
                    actions=[
                        ExtractKeyPhrasesAction()
                    ],
                    show_stats=True,
                    polling_interval=self._interval(),
                    raw_response_hook=lambda resp: resp,
                    cls=get_deserialized_for_mock
                )).result()
                results = []
                async for resp in response:
                    results.append(resp)
            assert e.value.message == "(InternalServerError) 1 out of 1 job tasks failed. Failed job tasks : keyphrasescomposite."

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": "v3.1"})
    @recorded_by_proxy_async
    async def test_analyze_works_with_v3_1(self, client):
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
                    assert document_result.id == document_order[doc_idx]
                    assert not document_result.is_error
                    assert self.document_result_to_action_type(document_result) == action_order[action_idx]


    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": "v3.0"})
    async def test_analyze_multiapi_validate_v3_0(self, **kwargs):
        client = kwargs.pop("client")
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        with pytest.raises(ValueError) as e:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=[
                    RecognizeEntitiesAction(),
                    ExtractKeyPhrasesAction(),
                    RecognizePiiEntitiesAction(),
                    RecognizeLinkedEntitiesAction(),
                    AnalyzeSentimentAction()
                ],
                polling_interval=self._interval(),
            )).result()
        assert str(e.value) == "'begin_analyze_actions' is only available for API version v3.1 and up."

    @TextAnalyticsPreparer()
    @TextAnalyticsCustomPreparer()
    async def test_analyze_multiapi_validate_v3_1(self, **kwargs):
        textanalytics_custom_text_endpoint = kwargs.pop("textanalytics_custom_text_endpoint")
        textanalytics_custom_text_key = kwargs.pop("textanalytics_custom_text_key")
        textanalytics_single_label_classify_project_name = kwargs.pop("textanalytics_single_label_classify_project_name")
        textanalytics_single_label_classify_deployment_name = kwargs.pop("textanalytics_single_label_classify_deployment_name")
        textanalytics_multi_category_classify_project_name = kwargs.pop("textanalytics_multi_category_classify_project_name")
        textanalytics_multi_category_classify_deployment_name = kwargs.pop("textanalytics_multi_category_classify_deployment_name")
        textanalytics_custom_entities_project_name = kwargs.pop("textanalytics_custom_entities_project_name")
        textanalytics_custom_entities_deployment_name = kwargs.pop("textanalytics_custom_entities_deployment_name")

        client = TextAnalyticsClient(textanalytics_custom_text_endpoint, AzureKeyCredential(textanalytics_custom_text_key), api_version="v3.1")

        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]
        version_supported = "2022-05-01"
        with pytest.raises(ValueError) as e:
            response = await (await client.begin_analyze_actions(
                docs,
                actions=[
                    SingleLabelClassifyAction(
                        project_name=textanalytics_single_label_classify_project_name,
                        deployment_name=textanalytics_single_label_classify_deployment_name
                    ),
                    MultiCategoryClassifyAction(
                        project_name=textanalytics_multi_category_classify_project_name,
                        deployment_name=textanalytics_multi_category_classify_deployment_name
                    ),
                    RecognizeCustomEntitiesAction(
                        project_name=textanalytics_custom_entities_project_name,
                        deployment_name=textanalytics_custom_entities_deployment_name
                    ),
                    AnalyzeHealthcareEntitiesAction()
                ],
                polling_interval=self._interval(),
            )).result()
        assert str(e.value) == f"'RecognizeCustomEntitiesAction' is only available for API version " \
                               f"{version_supported} and up.\n'SingleLabelClassifyAction' is only available " \
                               f"for API version {version_supported} and up.\n'MultiCategoryClassifyAction' is " \
                               f"only available for API version {version_supported} and up.\n'AnalyzeHealthcareEntitiesAction' is " \
                               f"only available for API version {version_supported} and up.\n"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_healthcare_action(self, client):
        docs = [
            "Patient does not suffer from high blood pressure.",
            "Prescribed 100mg ibuprofen, taken twice daily.",
            ""
        ]
        async with client:
            result = await (await client.begin_analyze_actions(
                docs,
                actions=[
                    AnalyzeHealthcareEntitiesAction(
                        model_version="latest",
                    )
                ],
                show_stats=True,
                polling_interval=self._interval(),
            )).result()
            response = []
            async for r in result:
                response.append(r)

            for idx, result in enumerate(response):
                for res in result:
                    if idx == 2:
                        assert res.is_error
                        assert res.error.code == "InvalidDocument"
                    else:
                        assert res.entities
                        assert res.statistics

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_cancel(self, client):
        single_doc = "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."
        docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 20)))]
        actions=[
            RecognizeEntitiesAction(),
            ExtractKeyPhrasesAction(),
            RecognizePiiEntitiesAction(),
            RecognizeLinkedEntitiesAction(),
            AnalyzeSentimentAction(),
        ]
        async with client:
            poller = await client.begin_analyze_actions(
                docs,
                actions,
                show_stats=True,
                polling_interval=self._interval(),
            )
            await poller.cancel()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_cancel_partial_results(self, client):
        single_doc = "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."
        docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 5)))]
        actions=[
            RecognizeEntitiesAction(),
            ExtractKeyPhrasesAction(),
            RecognizePiiEntitiesAction(),
            RecognizeLinkedEntitiesAction(),
            AnalyzeSentimentAction(),
        ]
        async with client:
            poller = await client.begin_analyze_actions(
                docs,
                actions,
                show_stats=True,
                polling_interval=self._interval(),
            )
            await poller.cancel()
            res = await poller.result()
            result = []
            async for doc in res:
                result.append(doc)

            # assert that we pad the result with doc errors for correct ordering
            # (since some results may have finished and others have cancelled)
            for idx, doc_result in enumerate(result):
                assert len(doc_result) == len(actions)
                for doc in doc_result:
                    assert doc.id == str(idx)
                    if doc.is_error:
                        assert doc.error.message == "No result for document. Action returned status 'cancelled'."
            assert poller.status() == "cancelled"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_cancel_fail_terminal_state(self, client):
        single_doc = "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."
        docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 20)))] # max number of documents is 25
        actions=[
            RecognizeEntitiesAction(),
            ExtractKeyPhrasesAction(),
            RecognizePiiEntitiesAction(),
            RecognizeLinkedEntitiesAction(),
            AnalyzeSentimentAction(),
        ]
        async with client:
            poller = await client.begin_analyze_actions(
                docs,
                actions,
                show_stats=True,
                polling_interval=self._interval(),
            )
            await poller.result()
            assert poller.status() == "succeeded"
            with pytest.raises(HttpResponseError):
                await poller.cancel()  # can't cancel when already in terminal state

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer({"api_version": "v3.1"})
    @recorded_by_proxy_async
    async def test_cancel_fail_v3_1(self, client):
        single_doc = "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."
        docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 20)))] # max number of documents is 25
        actions=[
            RecognizeEntitiesAction(),
            ExtractKeyPhrasesAction(),
            RecognizePiiEntitiesAction(),
            RecognizeLinkedEntitiesAction(),
            AnalyzeSentimentAction(),
        ]
        async with client:
            poller = await client.begin_analyze_actions(
                docs,
                actions,
                show_stats=True,
                polling_interval=self._interval(),
            )

            with pytest.raises(ValueError) as e:
                await poller.cancel()
            assert"Cancellation not supported by API versions v3.0, v3.1." in str(e.value)

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


import pytest
import functools
import datetime
from azure.core.credentials import AzureKeyCredential
from testcase import TextAnalyticsTest, TextAnalyticsPreparer, is_public_cloud
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from devtools_testutils import set_bodiless_matcher
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.textanalytics.aio import TextAnalyticsClient, AsyncTextAnalyticsLROPoller

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)

TextAnalyticsCustomPreparer = functools.partial(
    TextAnalyticsPreparer,
    textanalytics_custom_text_endpoint="https://fakeendpoint.cognitiveservices.azure.com",
    textanalytics_custom_text_key="fakeZmFrZV9hY29jdW50X2tleQ==",
    textanalytics_single_category_classify_project_name="single_category_classify_project_name",
    textanalytics_single_category_classify_deployment_name="single_category_classify_deployment_name",
    textanalytics_multi_label_classify_project_name="multi_label_classify_project_name",
    textanalytics_multi_label_classify_deployment_name="multi_label_classify_deployment_name",
    textanalytics_custom_entities_project_name="custom_entities_project_name",
    textanalytics_custom_entities_deployment_name="custom_entities_deployment_name",
)


class TestCustomTextAsync(TextAnalyticsTest):

    def _interval(self):
        return 5 if self.is_live else 0

    @pytest.mark.skipif(not is_public_cloud(), reason='Usgov and China Cloud are not supported')
    @TextAnalyticsCustomPreparer()
    @recorded_by_proxy_async
    async def test_poller_metadata(
            self,
            textanalytics_custom_text_endpoint,
            textanalytics_custom_text_key,
            textanalytics_custom_entities_project_name,
            textanalytics_custom_entities_deployment_name
    ):
        set_bodiless_matcher()  # don't match on body for this test since we scrub the proj/deployment values
        client = TextAnalyticsClient(textanalytics_custom_text_endpoint, AzureKeyCredential(textanalytics_custom_text_key))
        docs = [{"id": "56", "text": "David Schmidt, senior vice president--Food Safety, International Food Information Council (IFIC), Washington, D.C., discussed the physical activity component."}]

        async with client:
            poller = await client.begin_recognize_custom_entities(
                docs,
                project_name=textanalytics_custom_entities_project_name,
                deployment_name=textanalytics_custom_entities_deployment_name,
                show_stats=True,
                display_name="testing",
                polling_interval=self._interval(),
            )
            await poller.result()

        assert isinstance(poller, AsyncTextAnalyticsLROPoller)
        assert isinstance(poller.details["created_on"], datetime.datetime)
        assert isinstance(poller.details["expires_on"], datetime.datetime)
        assert isinstance(poller.details["last_modified_on"], datetime.datetime)
        assert poller.details["display_name"] == 'testing'
        assert poller.details["id"]

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
            poller = await client.begin_recognize_custom_entities(
                docs,
                project_name=textanalytics_custom_entities_project_name,
                deployment_name=textanalytics_custom_entities_deployment_name,
                show_stats=True,
                polling_interval=self._interval(),
            )

            assert isinstance(poller, AsyncTextAnalyticsLROPoller)
            document_results = await poller.result()

            async for result in document_results:
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
    async def test_recognize_custom_entities_continuation_token(
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
            initial_poller = await client.begin_recognize_custom_entities(
                docs,
                project_name=textanalytics_custom_entities_project_name,
                deployment_name=textanalytics_custom_entities_deployment_name,
                show_stats=True,
                polling_interval=self._interval(),
            )

            continuation_token = initial_poller.continuation_token()
            poller = await client.begin_recognize_custom_entities(
                None, None, None, continuation_token=continuation_token
            )

            assert isinstance(poller, AsyncTextAnalyticsLROPoller)
            document_results = await poller.result()

            async for result in document_results:
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
    async def test_multi_label_classify(
            self,
            textanalytics_custom_text_endpoint,
            textanalytics_custom_text_key,
            textanalytics_multi_label_classify_project_name,
            textanalytics_multi_label_classify_deployment_name
    ):
        set_bodiless_matcher()  # don't match on body for this test since we scrub the proj/deployment values
        client = TextAnalyticsClient(textanalytics_custom_text_endpoint, AzureKeyCredential(textanalytics_custom_text_key))
        docs = [
            {"id": "1", "language": "en", "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
            {"id": "2", "language": "en", "text": "David Schmidt, senior vice president--Food Safety, International Food Information Council (IFIC), Washington, D.C., discussed the physical activity component."},
            {"id": "3", "language": "en", "text": "I need a reservation for an indoor restaurant in China. Please don't stop the music. Play music and add it to my playlist"},
        ]
        async with client:
            document_results = await (await client.begin_multi_label_classify(
                docs,
                project_name=textanalytics_multi_label_classify_project_name,
                deployment_name=textanalytics_multi_label_classify_deployment_name,
                show_stats=True,
                polling_interval=self._interval(),
            )).result()

            async for result in document_results:
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
    async def test_multi_label_classify_cont_token(
            self,
            textanalytics_custom_text_endpoint,
            textanalytics_custom_text_key,
            textanalytics_multi_label_classify_project_name,
            textanalytics_multi_label_classify_deployment_name
    ):
        set_bodiless_matcher()  # don't match on body for this test since we scrub the proj/deployment values
        client = TextAnalyticsClient(textanalytics_custom_text_endpoint,
                                     AzureKeyCredential(textanalytics_custom_text_key))
        docs = [
            {"id": "1", "language": "en",
             "text": "A recent report by the Government Accountability Office (GAO) found that the dramatic increase in oil and natural gas development on federal lands over the past six years has stretched the staff of the BLM to a point that it has been unable to meet its environmental protection responsibilities."},
            {"id": "2", "language": "en",
             "text": "David Schmidt, senior vice president--Food Safety, International Food Information Council (IFIC), Washington, D.C., discussed the physical activity component."},
            {"id": "3", "language": "en",
             "text": "I need a reservation for an indoor restaurant in China. Please don't stop the music. Play music and add it to my playlist"},
        ]
        async with client:
            initial_poller = await client.begin_multi_label_classify(
                docs,
                project_name=textanalytics_multi_label_classify_project_name,
                deployment_name=textanalytics_multi_label_classify_deployment_name,
                show_stats=True,
                polling_interval=self._interval(),
            )
            continuation_token = initial_poller.continuation_token()

            poller = await client.begin_multi_label_classify(
                None, None, None, continuation_token=continuation_token
            )

            assert isinstance(poller, AsyncTextAnalyticsLROPoller)
            document_results = await poller.result()

            async for result in document_results:
                assert result.id
                assert not result.is_error
                assert not result.warnings
                assert result.statistics
                for classification in result.classifications:
                    assert classification.category
                    assert classification.confidence_score

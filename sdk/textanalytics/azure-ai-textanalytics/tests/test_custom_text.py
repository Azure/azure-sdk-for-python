# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from azure.core.credentials import AzureKeyCredential
from testcase import TextAnalyticsTest, TextAnalyticsPreparer, is_public_cloud
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher
from azure.ai.textanalytics._lro import TextAnalyticsLROPoller
from azure.ai.textanalytics import (
    TextAnalyticsClient
)

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)

TextAnalyticsCustomPreparer = functools.partial(
    TextAnalyticsPreparer,
    textanalytics_custom_text_endpoint="https://fakeendpoint.cognitiveservices.azure.com",
    textanalytics_custom_text_key="fakeZmFrZV9hY29jdW50X2tleQ==",
    textanalytics_single_category_classify_project_name="single_category_classify_project_name",
    textanalytics_single_category_classify_deployment_name="single_category_classify_deployment_name",
    textanalytics_multi_category_classify_project_name="multi_category_classify_project_name",
    textanalytics_multi_category_classify_deployment_name="multi_category_classify_deployment_name",
    textanalytics_custom_entities_project_name="custom_entities_project_name",
    textanalytics_custom_entities_deployment_name="custom_entities_deployment_name",
)


class TestCustomText(TextAnalyticsTest):

    def _interval(self):
        return 5 if self.is_live else 0

    @pytest.mark.skipif(not is_public_cloud(), reason='Usgov and China Cloud are not supported')
    @TextAnalyticsCustomPreparer()
    @recorded_by_proxy
    def test_recognize_custom_entities(
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

        poller = client.begin_recognize_custom_entities(
            docs,
            project_name=textanalytics_custom_entities_project_name,
            deployment_name=textanalytics_custom_entities_deployment_name,
            show_stats=True,
            polling_interval=self._interval(),
        )

        assert isinstance(poller, TextAnalyticsLROPoller)
        document_results = list(poller.result())

        for result in document_results:
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
    @recorded_by_proxy
    def test_recognize_custom_entities_continuation_token(
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

        initial_poller = client.begin_recognize_custom_entities(
            docs,
            project_name=textanalytics_custom_entities_project_name,
            deployment_name=textanalytics_custom_entities_deployment_name,
            show_stats=True,
            polling_interval=self._interval(),
        )
        continuation_token = initial_poller.continuation_token()

        poller = client.begin_recognize_custom_entities(
            None, None, None, continuation_token=continuation_token
        )

        assert isinstance(poller, TextAnalyticsLROPoller)
        document_results = list(poller.result())

        for result in document_results:
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

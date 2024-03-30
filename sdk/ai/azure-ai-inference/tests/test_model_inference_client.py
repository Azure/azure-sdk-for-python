# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import inspect
import azure.ai.inference as sdk

from model_inference_test_base import ModelClientTestBase, ServicePreparer
from devtools_testutils import recorded_by_proxy


# The test class name needs to start with "Test" to get collected by pytest
class TestModelClient(ModelClientTestBase):

    # **********************************************************************************
    #
    #                            HAPPY PATH TESTS
    #
    # **********************************************************************************

    # Test one chat completion
    @ServicePreparer()
    @recorded_by_proxy
    def test_chat_completion(self, **kwargs):

        self._create_client_for_standard_test(sync=True, **kwargs)

        options = sdk.models.ChatCompletionsOptions(
            messages=[sdk.models.ChatRequestUserMessage(content="How many feet are in a mile?")]
        )

        self._do_chat_completions(options=options, **kwargs)

        self.client.close()

    # Test some visual features, one after the other, from file, using default settings


"""     @ServicePreparer()
    @recorded_by_proxy
    def test_analyze_sync_single_feature_from_file(self, **kwargs):

        self._create_client_for_standard_analysis(sync=True, get_connection_url=True, **kwargs)

        self._do_analysis(
            image_source=self.IMAGE_FILE,
            visual_features=[sdk.models.VisualFeatures.CAPTION],
            query_params={"key1": "value1", "key2": "value2"},
            **kwargs
        )

        self._do_analysis(image_source=self.IMAGE_FILE, visual_features=[sdk.models.VisualFeatures.READ], **kwargs)

        self._do_analysis(image_source=self.IMAGE_FILE, visual_features=[sdk.models.VisualFeatures.TAGS], **kwargs)

        self.client.close() """

# **********************************************************************************
#
#                            ERROR TESTS
#
# **********************************************************************************

"""     @ServicePreparer()
    @recorded_by_proxy
    def test_analyze_sync_image_url_does_not_exist(self, **kwargs):

        self._create_client_for_standard_analysis(sync=True, **kwargs)

        self._do_analysis_with_error(
            image_source="https://www.this.is.a.bad.url.com/for/sure.jpg",
            visual_features=[sdk.models.VisualFeatures.CAPTION],
            expected_status_code=400,
            expected_message_contains="image url is not accessible",
            **kwargs
        )

        self.client.close()
 """

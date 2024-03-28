# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import inspect
import azure.ai.vision.imageanalysis as sdk

from model_inference_test_base import ModelInferenceTestBase, ServicePreparer
from devtools_testutils.aio import recorded_by_proxy_async

# The test class name needs to start with "Test" to get collected by pytest
class TestImageAnalysisAsyncClient(ModelInferenceTestBase):

    # **********************************************************************************
    #
    #                            HAPPY PATH TESTS
    #
    # **********************************************************************************

    # Test all visual features from a local image, using default settings
    @ServicePreparer()
    @recorded_by_proxy_async
    async def test_async_chat_completion(self, **kwargs):

        self._create_client_for_standard_analysis(sync=False, **kwargs)

        await self._do_async_chat_completions(
            options=[
                messages=[
                    role=sdk.models.ChatRole.USER,
                    content="How many feet are in a mile?"
                ]
            ],
            **kwargs
        )

        await self.async_client.close()

    # Test some visual features, one after the other, from image URL, with relevant settings specified
"""     @ServicePreparer()
    @recorded_by_proxy_async
    async def test_analyze_async_single_feature_from_url(self, **kwargs):

        self._create_client_for_standard_analysis(sync=False, **kwargs)

        await self._do_async_analysis(
            image_source=self.IMAGE_URL,
            visual_features=[sdk.models.VisualFeatures.DENSE_CAPTIONS],
            gender_neutral_caption=True,
            **kwargs
        )

        await self._do_async_analysis(
            image_source=self.IMAGE_URL,
            visual_features=[sdk.models.VisualFeatures.SMART_CROPS],
            smart_crops_aspect_ratios=[0.9, 1.33],
            **kwargs
        )

        await self._do_async_analysis(
            image_source=self.IMAGE_URL, visual_features=[sdk.models.VisualFeatures.TAGS], language="en", **kwargs
        )

        await self._do_async_analysis(
            image_source=self.IMAGE_URL, visual_features=[sdk.models.VisualFeatures.PEOPLE], **kwargs
        )

        await self.async_client.close() """

    # **********************************************************************************
    #
    #                            ERROR TESTS
    #
    # **********************************************************************************

 """    @ServicePreparer()
    @recorded_by_proxy_async
    async def test_analyze_async_authentication_failure(self, **kwargs):

        self._create_client_for_authentication_failure(sync=False, **kwargs)

        await self._do_async_analysis_with_error(
            image_source=self.IMAGE_URL,
            visual_features=[sdk.models.VisualFeatures.TAGS],
            expected_status_code=401,
            expected_message_contains="Access denied",
            **kwargs
        )

        await self.async_client.close() """

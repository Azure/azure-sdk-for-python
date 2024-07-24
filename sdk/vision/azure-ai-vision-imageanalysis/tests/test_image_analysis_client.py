# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import inspect
import azure.ai.vision.imageanalysis as sdk

from image_analysis_test_base import ImageAnalysisTestBase, ServicePreparer
from devtools_testutils import recorded_by_proxy


# The test class name needs to start with "Test" to get collected by pytest
class TestImageAnalysisClient(ImageAnalysisTestBase):

    # **********************************************************************************
    #
    #                            HAPPY PATH TESTS
    #
    # **********************************************************************************

    # Test all visual features from an image URL, which settings specified
    @ServicePreparer()
    @recorded_by_proxy
    def test_analyze_sync_all_features_from_url(self, **kwargs):

        self._create_client_for_standard_analysis(sync=True, **kwargs)

        self._do_analysis(
            image_source=self.IMAGE_URL,
            visual_features=[
                sdk.models.VisualFeatures.TAGS,
                sdk.models.VisualFeatures.OBJECTS,
                sdk.models.VisualFeatures.CAPTION,
                sdk.models.VisualFeatures.DENSE_CAPTIONS,
                sdk.models.VisualFeatures.READ,
                sdk.models.VisualFeatures.SMART_CROPS,
                sdk.models.VisualFeatures.PEOPLE,
            ],
            language="en",
            gender_neutral_caption=True,
            smart_crops_aspect_ratios=[0.9, 1.33],
            model_version="latest",
            **kwargs
        )

        self.client.close()

    # Test some visual features, one after the other, from file, using default settings
    @ServicePreparer()
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

        self.client.close()

    # Test a single visual feature from an image url, using Entra ID authentication
    @ServicePreparer()
    @recorded_by_proxy
    def test_analyze_sync_single_feature_from_url_entra_id_auth(self, **kwargs):

        self._create_client_for_standard_analysis_with_entra_id_auth(sync=True, **kwargs)

        self._do_analysis(image_source=self.IMAGE_URL,visual_features=[sdk.models.VisualFeatures.OBJECTS], **kwargs)

        self.client.close()

    # **********************************************************************************
    #
    #                            ERROR TESTS
    #
    # **********************************************************************************

    @ServicePreparer()
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

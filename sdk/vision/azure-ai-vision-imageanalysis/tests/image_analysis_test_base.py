# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import logging
import sys
import azure.ai.vision.imageanalysis as sdk
import azure.ai.vision.imageanalysis.aio as async_sdk

from os import path
from typing import List, Optional, Union
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.exceptions import AzureError
from azure.core.pipeline import PipelineRequest

# Set to True to enable SDK logging
LOGGING_ENABLED = True

if LOGGING_ENABLED:
    # Create a logger for the 'azure' SDK
    # See https://docs.python.org/3/library/logging.html
    logger = logging.getLogger("azure")
    logger.setLevel(logging.INFO)  # INFO or DEBUG

    # Configure a console output
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)

ServicePreparer = functools.partial(
    EnvironmentVariableLoader,
    "vision",
    vision_endpoint="https://fake-resource-name.cognitiveservices.azure.com",
    vision_key="00000000000000000000000000000000",
)


# The test class name needs to start with "Test" to get collected by pytest
class ImageAnalysisTestBase(AzureRecordedTestCase):

    client: sdk.ImageAnalysisClient
    async_client: async_sdk.ImageAnalysisClient
    connection_url: str

    # Set to True to print out all analysis results
    PRINT_ANALYSIS_RESULTS = True

    # We use a single image (the same one) for all error-free tests, one hosted on the web and one local
    IMAGE_URL = "https://aka.ms/azsdk/image-analysis/sample.jpg"
    IMAGE_FILE = path.abspath(path.join(path.abspath(__file__), "..", "./sample.jpg"))

    def _create_client_for_standard_analysis(self, sync: bool, get_connection_url: bool = False, **kwargs):
        endpoint = kwargs.pop("vision_endpoint")
        key = kwargs.pop("vision_key")
        credential = AzureKeyCredential(key)
        self._create_client(endpoint, credential, sync, get_connection_url)

    def _create_client_for_standard_analysis_with_entra_id_auth(self, sync: bool, get_connection_url: bool = False, **kwargs):
        endpoint = kwargs.pop("vision_endpoint")
        # See /tools/azure-sdk-tools/devtools_testutils/azure_recorded_testcase.py for `get_credential`
        if sync:
            credential = self.get_credential(sdk.ImageAnalysisClient, is_async=False)
        else:
            credential = self.get_credential(async_sdk.ImageAnalysisClient, is_async=True)
        self._create_client(endpoint, credential, sync, get_connection_url)

    def _create_client_for_authentication_failure(self, sync: bool, **kwargs):
        endpoint = kwargs.pop("vision_endpoint")
        key = "00000000000000000000000000000000"
        credential = AzureKeyCredential(key)
        self._create_client(endpoint, credential, sync, False)

    def _create_client(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], sync: bool, get_connection_url: bool):
        
        if sync:
            self.client = sdk.ImageAnalysisClient(
                endpoint=endpoint,
                credential=credential,
                logging_enable=LOGGING_ENABLED,
                raw_request_hook=self._raw_request_check if get_connection_url else None,
            )
            assert self.client is not None
        else:
            self.async_client = async_sdk.ImageAnalysisClient(
                endpoint=endpoint,
                credential=credential,
                logging_enable=LOGGING_ENABLED,
                raw_request_hook=self._raw_request_check if get_connection_url else None,
            )
            assert self.async_client is not None

    def _raw_request_check(self, request: PipelineRequest):
        self.connection_url = request.http_request.url
        print(f"Connection URL: {request.http_request.url}")

    def _do_analysis(
        self,
        image_source: str,
        visual_features: List[sdk.models.VisualFeatures],
        language: Optional[str] = None,
        gender_neutral_caption: Optional[bool] = None,
        smart_crops_aspect_ratios: Optional[List[float]] = None,
        model_version: Optional[str] = None,
        query_params: Optional[dict] = None,
        **kwargs,
    ):

        if "http" in image_source:
            result = self.client.analyze_from_url(
                image_url=image_source,
                visual_features=visual_features,
                language=language,
                gender_neutral_caption=gender_neutral_caption,
                smart_crops_aspect_ratios=smart_crops_aspect_ratios,
                model_version=model_version,
                params=query_params,
            )
        else:
            # Load image to analyze into a 'bytes' object
            with open(image_source, "rb") as f:
                image_data = bytes(f.read())

            result = self.client.analyze(
                image_data=image_data,
                visual_features=visual_features,
                language=language,
                gender_neutral_caption=gender_neutral_caption,
                smart_crops_aspect_ratios=smart_crops_aspect_ratios,
                model_version=model_version,
                params=query_params,
            )

        # Optional: console printout of all results
        if ImageAnalysisTestBase.PRINT_ANALYSIS_RESULTS:
            ImageAnalysisTestBase._print_analysis_results(result)

        # Validate all results
        ImageAnalysisTestBase._validate_result(
            result, visual_features, gender_neutral_caption, smart_crops_aspect_ratios
        )

        # Validate that additional query parameters exists in the connection URL, if specify
        if query_params is not None:
            ImageAnalysisTestBase._validate_query_parameters(query_params, self.connection_url)

    async def _do_async_analysis(
        self,
        image_source: str,
        visual_features: List[sdk.models.VisualFeatures],
        language: Optional[str] = None,
        gender_neutral_caption: Optional[bool] = None,
        smart_crops_aspect_ratios: Optional[List[float]] = None,
        model_version: Optional[str] = None,
        query_params: Optional[dict] = None,
        **kwargs,
    ):

        if "http" in image_source:
            result = await self.async_client.analyze_from_url(
                image_url=image_source,
                visual_features=visual_features,
                language=language,
                gender_neutral_caption=gender_neutral_caption,
                smart_crops_aspect_ratios=smart_crops_aspect_ratios,
                model_version=model_version,
                params=query_params,
            )

        else:
            # Load image to analyze into a 'bytes' object
            with open(image_source, "rb") as f:
                image_data = bytes(f.read())

            result = await self.async_client.analyze(
                image_data=image_data,
                visual_features=visual_features,
                language=language,
                gender_neutral_caption=gender_neutral_caption,
                smart_crops_aspect_ratios=smart_crops_aspect_ratios,
                model_version=model_version,
                params=query_params,
            )

        # Optional: console printout of all results
        if ImageAnalysisTestBase.PRINT_ANALYSIS_RESULTS:
            ImageAnalysisTestBase._print_analysis_results(result)

        # Validate all results
        ImageAnalysisTestBase._validate_result(
            result, visual_features, gender_neutral_caption, smart_crops_aspect_ratios
        )

        # Validate that additional query parameters exists in the connection URL, if specify
        if query_params is not None:
            ImageAnalysisTestBase._validate_query_parameters(query_params, self.connection_url)

    def _do_analysis_with_error(
        self,
        image_source: str,
        visual_features: List[sdk.models.VisualFeatures],
        expected_status_code: int,
        expected_message_contains: str,
        **kwargs,
    ):

        try:
            if "http" in image_source:
                result = self.client.analyze_from_url(image_url=image_source, visual_features=visual_features)
            else:
                # Load image to analyze into a 'bytes' object
                with open(image_source, "rb") as f:
                    image_data = bytes(f.read())

                result = self.client.analyze(image_data=image_data, visual_features=visual_features)

        except AzureError as e:
            print(e)
            assert hasattr(e, "status_code")
            assert e.status_code == expected_status_code
            assert expected_message_contains in e.message
            return
        assert False  # We should not get here

    async def _do_async_analysis_with_error(
        self,
        image_source: str,
        visual_features: List[sdk.models.VisualFeatures],
        expected_status_code: int,
        expected_message_contains: str,
        **kwargs,
    ):

        try:
            if "http" in image_source:
                result = await self.async_client.analyze_from_url(
                    image_url=image_source, visual_features=visual_features
                )
            else:
                # Load image to analyze into a 'bytes' object
                with open(image_source, "rb") as f:
                    image_data = bytes(f.read())

                result = await self.async_client.analyze(image_data=image_data, visual_features=visual_features)

        except AzureError as e:
            print(e)
            assert hasattr(e, "status_code")
            assert e.status_code == expected_status_code
            assert expected_message_contains in e.message
            return
        assert False  # We should not get here

    @staticmethod
    def _validate_query_parameters(query_params: dict, connection_url: str):
        assert len(query_params) > 0
        query_string = ""
        for key, value in query_params.items():
            query_string += "&" + key + "=" + value
        query_string = "?" + query_string[1:]
        assert query_string in connection_url

    @staticmethod
    def _validate_result(
        result: sdk.models.ImageAnalysisResult,
        expected_features: List[sdk.models.VisualFeatures],
        gender_neutral_caption: Optional[bool] = None,
        smart_crops_aspect_ratios: Optional[List[float]] = None,
    ):
        ImageAnalysisTestBase._validate_metadata(result)
        ImageAnalysisTestBase._validate_model_version(result)

        if expected_features != None and sdk.models.VisualFeatures.CAPTION in expected_features:
            ImageAnalysisTestBase._validate_caption(result, gender_neutral_caption)
        else:
            assert result.caption is None

        if expected_features != None and sdk.models.VisualFeatures.DENSE_CAPTIONS in expected_features:
            ImageAnalysisTestBase._validate_dense_captions(result)
        else:
            assert result.dense_captions is None

        if expected_features != None and sdk.models.VisualFeatures.OBJECTS in expected_features:
            ImageAnalysisTestBase._validate_objects(result)
        else:
            assert result.objects is None

        if expected_features != None and sdk.models.VisualFeatures.TAGS in expected_features:
            ImageAnalysisTestBase._validate_tags(result)
        else:
            assert result.tags is None

        if expected_features != None and sdk.models.VisualFeatures.PEOPLE in expected_features:
            ImageAnalysisTestBase._validate_people(result)
        else:
            assert result.people is None

        if expected_features != None and sdk.models.VisualFeatures.SMART_CROPS in expected_features:
            ImageAnalysisTestBase._validate_smart_crops(result, smart_crops_aspect_ratios)
        else:
            assert result.smart_crops is None

        if expected_features != None and sdk.models.VisualFeatures.READ in expected_features:
            ImageAnalysisTestBase._validate_read(result)
        else:
            assert result.read is None

    @staticmethod
    def _validate_metadata(result: sdk.models.ImageAnalysisResult):
        assert result.metadata is not None
        assert result.metadata.height == 576
        assert result.metadata.width == 864

    @staticmethod
    def _validate_model_version(result: sdk.models.ImageAnalysisResult):
        assert result.model_version is not None
        assert result.model_version == "2023-10-01"

    @staticmethod
    def _validate_caption(result: sdk.models.ImageAnalysisResult, gender_neutral_caption: Optional[bool] = None):
        assert result.caption is not None
        assert result.caption.text is not None
        if gender_neutral_caption is not None and gender_neutral_caption:
            assert "person" in result.caption.text.lower()
        else:
            assert "woman" in result.caption.text.lower()
        assert "table" in result.caption.text.lower()
        assert "laptop" in result.caption.text.lower()
        assert 0.0 < result.caption.confidence < 1.0

    @staticmethod
    def _validate_dense_captions(result: sdk.models.ImageAnalysisResult):
        assert result.dense_captions is not None
        assert len(result.dense_captions.list) > 1

        # First dense caption should apply to the whole image, and be identical to the caption found in CaptionResult
        first_dense_caption = result.dense_captions.list[0]
        assert first_dense_caption is not None
        assert first_dense_caption.text is not None
        if result.caption is not None:
            assert first_dense_caption.text == result.caption.text
        else:
            assert first_dense_caption.text is not None
            assert len(first_dense_caption.text) > 0
        assert first_dense_caption.bounding_box is not None
        assert first_dense_caption.bounding_box.x == 0
        assert first_dense_caption.bounding_box.y == 0
        assert first_dense_caption.bounding_box.height == result.metadata.height
        assert first_dense_caption.bounding_box.width == result.metadata.width

        # Sanity checks on all dense captions
        for dense_caption in result.dense_captions.list:
            assert dense_caption is not None
            assert dense_caption.text is not None
            assert len(dense_caption.text) > 0
            assert dense_caption.confidence is not None
            assert 0.0 < dense_caption.confidence < 1.0
            assert dense_caption.bounding_box is not None
            assert dense_caption.bounding_box.x >= 0
            assert dense_caption.bounding_box.y >= 0
            assert dense_caption.bounding_box.height <= result.metadata.height - dense_caption.bounding_box.y
            assert dense_caption.bounding_box.width <= result.metadata.width - dense_caption.bounding_box.x

        # Make sure each dense caption is unique
        for i, dense_caption in enumerate(result.dense_captions.list):
            for other_dense_caption in result.dense_captions.list[i + 1 :]:
                # Do not include the check below. It's okay to have two identical dense captions since they have different bounding boxes.
                # assert other_dense_caption.text != dense_caption.text
                assert not (
                    other_dense_caption.bounding_box.x == dense_caption.bounding_box.x
                    and other_dense_caption.bounding_box.y == dense_caption.bounding_box.y
                    and other_dense_caption.bounding_box.height == dense_caption.bounding_box.height
                    and other_dense_caption.bounding_box.width == dense_caption.bounding_box.width
                )

    @staticmethod
    def _validate_objects(result: sdk.models.ImageAnalysisResult):
        objects = result.objects
        assert objects is not None
        assert len(objects.list) > 1

        found1 = False
        for object in objects.list:
            assert object is not None
            assert object.tags is not None
            assert len(object.tags) == 1
            tag = object.tags[0]
            assert tag is not None
            assert tag.name is not None
            assert len(tag.name) > 0
            assert 0.0 < tag.confidence < 1.0
            # We expect to see this in the list of objects
            if tag.name.lower() == "person":
                found1 = True
        assert found1

        # Make sure each object box is unique
        for i in range(len(objects.list)):
            for j in range(i + 1, len(objects.list)):
                box_i = objects.list[i].bounding_box
                box_j = objects.list[j].bounding_box
                assert not (
                    box_i.x == box_j.x
                    and box_i.y == box_j.y
                    and box_i.height == box_j.height
                    and box_i.width == box_j.width
                )

    @staticmethod
    def _validate_tags(result: sdk.models.ImageAnalysisResult):
        tags = result.tags
        assert tags is not None
        assert tags.list is not None
        assert len(tags.list) > 1

        found1, found2 = False, False
        for tag in tags.list:
            assert tag.name is not None
            assert len(tag.name) > 0
            assert 0.0 < tag.confidence < 1.0
            if tag.name.lower() == "person":
                found1 = True
            if tag.name.lower() == "laptop":
                found2 = True

        assert found1
        assert found2

        # Make sure each tag is unique
        for i in range(len(tags.list)):
            for j in range(i + 1, len(tags.list)):
                assert tags.list[j].name != tags.list[i].name

    @staticmethod
    def _validate_people(result: sdk.models.ImageAnalysisResult):
        assert result.people is not None
        assert len(result.people.list) > 0

        for person in result.people.list:
            assert 0.0 < person.confidence < 1.0
            assert person.bounding_box.x >= 0
            assert person.bounding_box.y >= 0
            assert person.bounding_box.height <= result.metadata.height - person.bounding_box.y
            assert person.bounding_box.width <= result.metadata.width - person.bounding_box.x

        # Make sure each person is unique
        for i, person in enumerate(result.people.list):
            for other_person in result.people.list[i + 1 :]:
                assert not (
                    other_person.bounding_box.x == person.bounding_box.x
                    and other_person.bounding_box.y == person.bounding_box.y
                    and other_person.bounding_box.height == person.bounding_box.height
                    and other_person.bounding_box.width == person.bounding_box.width
                )

    @staticmethod
    def _validate_smart_crops(
        result: sdk.models.ImageAnalysisResult, smart_crops_aspect_ratios: Optional[List[float]] = None
    ):

        assert result.smart_crops is not None
        crop_regions = result.smart_crops.list

        if smart_crops_aspect_ratios is None:
            assert len(crop_regions) == 1
            assert crop_regions[0].aspect_ratio >= 0.5 and crop_regions[0].aspect_ratio <= 2.0
        else:
            assert len(crop_regions) == len(smart_crops_aspect_ratios)
            for i, region in enumerate(crop_regions):
                assert region.aspect_ratio == smart_crops_aspect_ratios[i]
                assert region.aspect_ratio >= 0.75 and region.aspect_ratio <= 1.8

        for region in crop_regions:
            assert region.bounding_box.x >= 0
            assert region.bounding_box.y >= 0
            assert region.bounding_box.height <= result.metadata.height - region.bounding_box.y
            assert region.bounding_box.width <= result.metadata.width - region.bounding_box.x

        # Make sure each bounding box is unique
        for i, region in enumerate(crop_regions):
            for other_region in crop_regions[i + 1 :]:
                assert not (
                    other_region.bounding_box.x == region.bounding_box.x
                    and other_region.bounding_box.y == region.bounding_box.y
                    and other_region.bounding_box.height == region.bounding_box.height
                    and other_region.bounding_box.width == region.bounding_box.width
                )

    @staticmethod
    def _validate_read(result: sdk.models.ImageAnalysisResult):
        read = result.read
        assert read is not None
        assert read.blocks is not None
        assert len(read.blocks) == 1

        block = read.blocks[0]
        assert block is not None

        lines = block.lines
        assert lines is not None
        assert len(lines) == 3

        # Do some validation on the first line
        line = lines[0]
        assert line is not None
        assert line.text == "Sample text"

        polygon = line.bounding_polygon
        assert polygon is not None
        assert len(polygon) == 4
        for i in range(len(polygon)):
            assert polygon[i].x > 0.0
            assert polygon[i].y > 0.0

        # Do some validation on the 3rd line (including word validation)
        line = lines[2]
        assert line is not None
        assert line.text == "123 456"

        polygon = line.bounding_polygon
        assert polygon is not None
        assert len(polygon) == 4
        for i in range(len(polygon)):
            assert polygon[i].x > 0.0
            assert polygon[i].y > 0.0

        words = line.words
        assert words is not None
        assert len(words) == 2

        word = words[1]
        assert word is not None
        assert word.text == "456"
        assert word.confidence > 0.0
        assert word.confidence < 1.0

        polygon = word.bounding_polygon
        assert polygon is not None
        assert len(polygon) == 4
        for i in range(len(polygon)):
            assert polygon[i].x > 0.0
            assert polygon[i].y > 0.0

    @staticmethod
    def _print_analysis_results(result: sdk.models.ImageAnalysisResult):

        print(" Image height: {}".format(result.metadata.height))
        print(" Image width: {}".format(result.metadata.width))
        print(" Model version: {}".format(result.model_version))

        if result.caption is not None:
            print(" Caption:")
            print("   '{}', Confidence {:.4f}".format(result.caption.text, result.caption.confidence))

        if result.dense_captions is not None:
            print(" Dense Captions:")
            for caption in result.dense_captions.list:
                print("   '{}', {}, Confidence: {:.4f}".format(caption.text, caption.bounding_box, caption.confidence))

        if result.objects is not None:
            print(" Objects:")
            for object in result.objects.list:
                print(
                    "   '{}', {}, Confidence: {:.4f}".format(
                        object.tags[0].name, object.bounding_box, object.tags[0].confidence
                    )
                )

        if result.tags is not None:
            print(" Tags:")
            for tag in result.tags.list:
                print("   '{}', Confidence {:.4f}".format(tag.name, tag.confidence))

        if result.people is not None:
            print(" People:")
            for person in result.people.list:
                print("   {}, Confidence {:.4f}".format(person.bounding_box, person.confidence))

        if result.smart_crops is not None:
            print(" Smart Cropping:")
            for smart_crop in result.smart_crops.list:
                print("   Aspect ratio {}: Smart crop {}".format(smart_crop.aspect_ratio, smart_crop.bounding_box))

        if result.read is not None:
            print(" Read:")
            for line in result.read.blocks[0].lines:
                print(f"   Line: '{line.text}', Bounding box {line.bounding_polygon}")
                for word in line.words:
                    print(
                        f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}"
                    )

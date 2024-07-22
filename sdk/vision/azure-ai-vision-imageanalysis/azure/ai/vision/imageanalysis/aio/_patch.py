# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize

"""
from typing import List, Any, Optional, Union
from azure.core.tracing.decorator_async import distributed_trace_async
from .. import models as _models
from ._operations._operations import ImageAnalysisClientOperationsMixin
from ._client import ImageAnalysisClient as ImageAnalysisClientGenerated


class ImageAnalysisClient(ImageAnalysisClientGenerated):
    """ImageAnalysisClient.

    :param endpoint: Azure AI Computer Vision endpoint (protocol and hostname, for example:
     https://:code:`<resource-name>`.cognitiveservices.azure.com). Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential
    :keyword api_version: The API version to use for this operation. Default value is "2023-10-01".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    @distributed_trace_async
    async def analyze_from_url(
        self,
        image_url: str,
        visual_features: List[_models.VisualFeatures],
        *,
        language: Optional[str] = None,
        gender_neutral_caption: Optional[bool] = None,
        smart_crops_aspect_ratios: Optional[List[float]] = None,
        model_version: Optional[str] = None,
        **kwargs: Any
    ) -> _models.ImageAnalysisResult:
        """Performs a single Image Analysis operation.

        :param image_url: The publicly accessible URL of the image to analyze.
        :type image_url: str
        :param visual_features: A list of visual features to analyze. Required. Seven visual features
         are supported: Caption, DenseCaptions, Read (OCR), Tags, Objects, SmartCrops, and People. At
         least one visual feature must be specified.
        :type visual_features: list[~azure.ai.vision.imageanalysis.models.VisualFeatures]
        :keyword language: The desired language for result generation (a two-letter language code).
         Defaults to 'en' (English). See https://aka.ms/cv-languages for a list of supported languages.
        :paramtype language: str
        :keyword gender_neutral_caption: Boolean flag for enabling gender-neutral captioning for
         Caption and Dense Captions features. Defaults to 'false'.
         Captions may contain gender terms (for example: 'man', 'woman', or 'boy', 'girl').
         If you set this to 'true', those will be replaced with gender-neutral terms (for example:
         'person' or 'child').
        :paramtype gender_neutral_caption: bool
        :keyword smart_crops_aspect_ratios: A list of aspect ratios to use for smart cropping.
         Defaults to one crop region with an aspect ratio the service sees fit between
         0.5 and 2.0 (inclusive). Aspect ratios are calculated by dividing the target crop
         width in pixels by the height in pixels. When set, supported values are
         between 0.75 and 1.8 (inclusive).
        :paramtype smart_crops_aspect_ratios: list[float]
        :keyword model_version: The version of cloud AI-model used for analysis. Defaults to 'latest',
         for the latest AI model with recent improvements.
         The format is the following: 'latest' or 'YYYY-MM-DD' or 'YYYY-MM-DD-preview',
         where 'YYYY', 'MM', 'DD' are the year, month and day associated with the model.
         If you would like to make sure analysis results do not change over time, set this
         value to a specific model version.
        :paramtype model_version: str
        :return: ImageAnalysisResult. The ImageAnalysisResult is compatible with MutableMapping
        :rtype: ~azure.ai.vision.imageanalysis.models.ImageAnalysisResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        visual_features_impl: List[Union[str, _models.VisualFeatures]] = list(visual_features)

        return await ImageAnalysisClientOperationsMixin._analyze_from_url(  # pylint: disable=protected-access
            self,
            image_url=_models._models.ImageUrl(url=image_url),  # pylint: disable=protected-access
            visual_features=visual_features_impl,
            language=language,
            gender_neutral_caption=gender_neutral_caption,
            smart_crops_aspect_ratios=smart_crops_aspect_ratios,
            model_version=model_version,
            **kwargs
        )

    @distributed_trace_async
    async def analyze(
        self,
        image_data: bytes,
        visual_features: List[_models.VisualFeatures],
        *,
        language: Optional[str] = None,
        gender_neutral_caption: Optional[bool] = None,
        smart_crops_aspect_ratios: Optional[List[float]] = None,
        model_version: Optional[str] = None,
        **kwargs: Any
    ) -> _models.ImageAnalysisResult:
        """Performs a single Image Analysis operation.

        :param image_data: A buffer containing the whole image to be analyzed.
        :type image_data: bytes
        :param visual_features: A list of visual features to analyze. Required. Seven visual features
         are supported: Caption, DenseCaptions, Read (OCR), Tags, Objects, SmartCrops, and People. At
         least one visual feature must be specified.
        :type visual_features: list[~azure.ai.vision.imageanalysis.models.VisualFeatures]
        :keyword language: The desired language for result generation (a two-letter language code).
         Defaults to 'en' (English). See https://aka.ms/cv-languages for a list of supported languages.
        :paramtype language: str
        :keyword gender_neutral_caption: Boolean flag for enabling gender-neutral captioning for
         Caption and Dense Captions features. Defaults to 'false'.
         Captions may contain gender terms (for example: 'man', 'woman', or 'boy', 'girl').
         If you set this to 'true', those will be replaced with gender-neutral terms (for example:
         'person' or 'child').
        :paramtype gender_neutral_caption: bool
        :keyword smart_crops_aspect_ratios: A list of aspect ratios to use for smart cropping.
         Defaults to one crop region with an aspect ratio the service sees fit between
         0.5 and 2.0 (inclusive). Aspect ratios are calculated by dividing the target crop
         width in pixels by the height in pixels. When set, supported values are
         between 0.75 and 1.8 (inclusive).
        :paramtype smart_crops_aspect_ratios: list[float]
        :keyword model_version: The version of cloud AI-model used for analysis. Defaults to 'latest',
         for the latest AI model with recent improvements.
         The format is the following: 'latest' or 'YYYY-MM-DD' or 'YYYY-MM-DD-preview',
         where 'YYYY', 'MM', 'DD' are the year, month and day associated with the model.
         If you would like to make sure analysis results do not change over time, set this
         value to a specific model version.
        :paramtype model_version: str
        :return: ImageAnalysisResult. The ImageAnalysisResult is compatible with MutableMapping
        :rtype: ~azure.ai.vision.imageanalysis.models.ImageAnalysisResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        visual_features_impl: List[Union[str, _models.VisualFeatures]] = list(visual_features)

        return await ImageAnalysisClientOperationsMixin._analyze_from_image_data(  # pylint: disable=protected-access
            self,
            image_data=image_data,
            visual_features=visual_features_impl,
            language=language,
            gender_neutral_caption=gender_neutral_caption,
            smart_crops_aspect_ratios=smart_crops_aspect_ratios,
            model_version=model_version,
            **kwargs
        )


__all__: List[str] = [
    "ImageAnalysisClient"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

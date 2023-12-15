# Azure Image Analysis client library for Python - Customization

This document specifies the hand-customization done to the auto-generated Python Image Analysis SDK.

## Updates to the sync client

Add the following method to the bottom of the source file `azure\ai\vision\imageanalysis\_operations\_operations.py`

```python
    def analyze(
        self,
        image_content: Union[str, bytes],
        visual_features: List[_models.VisualFeatures],
        *,
        language: Optional[str] = None,
        gender_neutral_caption: Optional[bool] = None,
        smart_crops_aspect_ratios: Optional[List[float]] = None,
        model_version: Optional[str] = None,
        **kwargs: Any
    ) -> _models.ImageAnalysisResult:
        """Performs a single Image Analysis operation.

        :param image_content: The image to be analyzed. Is one of the following types: 'str' or 'bytes'.
        Required.
        :type image_content: 'str' when providing a publicly accessible url of the image to analyze,
        or 'bytes' when providing the image content directly.
        :keyword visual_features: A list of visual features to analyze.
         Seven visual features are supported: Caption, DenseCaptions, Read (OCR), Tags, Objects,
         SmartCrops, and People.
         At least one visual feature must be specified. Required.
        :paramtype visual_features: list[str or ~azure.ai.vision.imageanalysis.models.VisualFeatures]
        :keyword language: The desired language for result generation (a two-letter language code).
         If this option is not specified, the default value 'en' is used (English).
         See https://aka.ms/cv-languages for a list of supported languages.
         At the moment, only tags can be generated in none-English languages. Default value is None.
        :paramtype language: str
        :keyword gender_neutral_caption: Boolean flag for enabling gender-neutral captioning for
         Caption and Dense Captions features.
         By default captions may contain gender terms (for example: 'man', 'woman', or 'boy', 'girl').
         If you set this to "true", those will be replaced with gender-neutral terms (for example:
         'person' or 'child'). Default value is None.
        :paramtype gender_neutral_caption: bool
        :keyword smart_crops_aspect_ratios: A list of aspect ratios to use for smart cropping.
         Aspect ratios are calculated by dividing the target crop width in pixels by the height in
         pixels.
         Supported values are between 0.75 and 1.8 (inclusive).
         If this parameter is not specified, the service will return one crop region with an aspect
         ratio it sees fit between 0.5 and 2.0 (inclusive). Default value is None.
        :paramtype smart_crops_aspect_ratios: list[float]
        :keyword model_version: The version of cloud AI-model used for analysis.
         The format is the following: 'latest' (default value) or 'YYYY-MM-DD' or 'YYYY-MM-DD-preview',
         where 'YYYY', 'MM', 'DD' are the year, month and day associated with the model.
         This is not commonly set, as the default always gives the latest AI model with recent
         improvements.
         If however you would like to make sure analysis results do not change over time, set this
         value to a specific model version. Default value is None.
        :paramtype model_version: str
        :keyword content_type: The format of the HTTP payload. Default value is None.
        :paramtype content_type: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: ImageAnalysisResult. The ImageAnalysisResult is compatible with MutableMapping
        :rtype: ~azure.ai.vision.imageanalysis.models.ImageAnalysisResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if isinstance(image_content, str):
            return self._analyze_from_url(
                image_content = _models._models.ImageUrl(url = image_content), # pylint: disable=protected-access
                visual_features = visual_features,
                language = language,
                gender_neutral_caption = gender_neutral_caption,
                smart_crops_aspect_ratios = smart_crops_aspect_ratios,
                model_version = model_version,
                **kwargs)

        return self._analyze_from_buffer(
            image_content = image_content,
            visual_features = visual_features,
            language = language,
            gender_neutral_caption = gender_neutral_caption,
            smart_crops_aspect_ratios = smart_crops_aspect_ratios,
            model_version = model_version,
            **kwargs)

```

## Update to the async client

Add the following method to the bottom of the source file `azure\ai\vision\imageanalysis\aio\_operations\_operations.py`

```python
    async def analyze(
        self,
        image_content: Union[str, bytes],
        visual_features: List[_models.VisualFeatures],
        *,
        language: Optional[str] = None,
        gender_neutral_caption: Optional[bool] = None,
        smart_crops_aspect_ratios: Optional[List[float]] = None,
        model_version: Optional[str] = None,
        **kwargs: Any
    ) -> _models.ImageAnalysisResult:
        """Performs a single Image Analysis operation.

        :param image_content: The image to be analyzed. Required.
        :type image_content: ~azure.ai.vision.imageanalysis.models.ImageUrl
        :keyword visual_features: A list of visual features to analyze.
         Seven visual features are supported: Caption, DenseCaptions, Read (OCR), Tags, Objects,
         SmartCrops, and People.
         At least one visual feature must be specified. Required.
        :paramtype visual_features: list[str or ~azure.ai.vision.imageanalysis.models.VisualFeatures]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword language: The desired language for result generation (a two-letter language code).
         If this option is not specified, the default value 'en' is used (English).
         See https://aka.ms/cv-languages for a list of supported languages.
         At the moment, only tags can be generated in none-English languages. Default value is None.
        :paramtype language: str
        :keyword gender_neutral_caption: Boolean flag for enabling gender-neutral captioning for
         Caption and Dense Captions features.
         By default captions may contain gender terms (for example: 'man', 'woman', or 'boy', 'girl').
         If you set this to "true", those will be replaced with gender-neutral terms (for example:
         'person' or 'child'). Default value is None.
        :paramtype gender_neutral_caption: bool
        :keyword smart_crops_aspect_ratios: A list of aspect ratios to use for smart cropping.
         Aspect ratios are calculated by dividing the target crop width in pixels by the height in
         pixels.
         Supported values are between 0.75 and 1.8 (inclusive).
         If this parameter is not specified, the service will return one crop region with an aspect
         ratio it sees fit between 0.5 and 2.0 (inclusive). Default value is None.
        :paramtype smart_crops_aspect_ratios: list[float]
        :keyword model_version: The version of cloud AI-model used for analysis.
         The format is the following: 'latest' (default value) or 'YYYY-MM-DD' or 'YYYY-MM-DD-preview',
         where 'YYYY', 'MM', 'DD' are the year, month and day associated with the model.
         This is not commonly set, as the default always gives the latest AI model with recent
         improvements.
         If however you would like to make sure analysis results do not change over time, set this
         value to a specific model version. Default value is None.
        :paramtype model_version: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: ImageAnalysisResult. The ImageAnalysisResult is compatible with MutableMapping
        :rtype: ~azure.ai.vision.imageanalysis.models.ImageAnalysisResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if isinstance(image_content, str):
            return await self._analyze_from_url(
                image_content = _models._models.ImageUrl(url = image_content), # pylint: disable=protected-access
                visual_features = visual_features,
                language = language,
                gender_neutral_caption = gender_neutral_caption,
                smart_crops_aspect_ratios = smart_crops_aspect_ratios,
                model_version = model_version,
                **kwargs)

        return await self._analyze_from_buffer(
            image_content = image_content,
            visual_features = visual_features,
            language = language,
            gender_neutral_caption = gender_neutral_caption,
            smart_crops_aspect_ratios = smart_crops_aspect_ratios,
            model_version = model_version,
            **kwargs)

```
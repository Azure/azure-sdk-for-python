# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
# mypy: disable-error-code=override
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional, Any, Union, overload, IO
from collections.abc import MutableMapping
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.polling import AsyncLROPoller
from ._operations import FacesOperations as FacesOperationsGenerated
from ...models import DetectFacesResult
from ._operations import ContentAnalyzersOperations as ContentAnalyzersOperationsGenerated
from ... import models as _models
from ._operations import ContentClassifiersOperations as ContentClassifiersOperationsGenerated

JSON = MutableMapping[str, Any]

__all__: List[str] = [
    "FacesOperations",
    "ContentAnalyzersOperations",
    "ContentClassifiersOperations"
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize

    :return: None
    :rtype: None
    """


class FacesOperations(FacesOperationsGenerated):
    """Extended FacesOperations with improved detect method overloads."""
    @overload
    async def detect(
        self,
        *,
        url: str,
        max_detected_faces: Optional[int] = None,
        **kwargs: Any
    ) -> DetectFacesResult:
        """Detect faces using image URL.

        :keyword url: Image URL. Required.
        :paramtype url: str
        :keyword max_detected_faces: Maximum number of faces to return (up to 100)
        :paramtype max_detected_faces: int
        :return: DetectFacesResult
        :rtype: ~azure.ai.contentunderstanding.models.DetectFacesResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def detect(
        self,
        *,
        data: bytes,
        max_detected_faces: Optional[int] = None,
        **kwargs: Any
    ) -> DetectFacesResult:
        """Detect faces using image data.

        :keyword data: Binary image data as bytes. Required.
        :paramtype data: bytes
        :keyword max_detected_faces: Maximum number of faces to return (up to 100)
        :paramtype max_detected_faces: int
        :return: DetectFacesResult
        :rtype: ~azure.ai.contentunderstanding.models.DetectFacesResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def detect(
        self, 
        body: JSON, 
        *, 
        content_type: str = "application/json", 
        **kwargs: Any
    ) -> DetectFacesResult:
        """Detect faces in an image.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: DetectFacesResult. The DetectFacesResult is compatible with MutableMapping
        :rtype: ~azure.ai.contentunderstanding.models.DetectFacesResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def detect(
        self, 
        body: IO[bytes], 
        *, 
        content_type: str = "application/json", 
        **kwargs: Any
    ) -> DetectFacesResult:
        """Detect faces in an image.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: DetectFacesResult. The DetectFacesResult is compatible with MutableMapping
        :rtype: ~azure.ai.contentunderstanding.models.DetectFacesResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def detect(self, *args: Any, **kwargs: Any) -> DetectFacesResult:  # type: ignore[override]
        """Detect faces in an image with url/data mutual exclusivity.

        This method enforces that url and data cannot be provided simultaneously,
        while allowing all other original behaviors including body parameters.

        :param args: Variable length argument list.
        :type args: Any
        :param kwargs: Arbitrary keyword arguments.
        :type kwargs: Any
        :return: DetectFacesResult
        :rtype: ~azure.ai.contentunderstanding.models.DetectFacesResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Validate that url and data are not provided together
        if ('url' in kwargs and kwargs['url'] is not None and
                'data' in kwargs and kwargs['data'] is not None):
            raise ValueError(
                "Cannot provide both 'url' and 'data' parameters simultaneously"
            )

        # Handle bytes data - no conversion needed, pass through directly
        # The original detect method will handle bytes data appropriately

        # Call the original method for all cases
        return await super().detect(*args, **kwargs)


class ContentAnalyzersOperations(ContentAnalyzersOperationsGenerated):
    """Extended ContentAnalyzersOperations with url/data mutual exclusivity enforcement."""
    @overload
    async def begin_analyze(
        self,
        analyzer_id: str,
        *,
        url: str,
        string_encoding: Optional[Union[str, _models.StringEncoding]] = None,
        processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
        content_type: str = "application/json",
        inputs: Optional[List[_models.AnalyzeInput]] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.AnalyzeResult]:
        """Extract content and fields from input using URL.

        :param analyzer_id: The unique identifier of the analyzer. Required.
        :type analyzer_id: str
        :keyword url: The URL of the primary input to analyze. Required.
        :paramtype url: str
        :keyword string_encoding: The encoding format for content spans in the response. Known values
         are: "codePoint", "utf16", and "utf8". Default value is None.
        :paramtype string_encoding: str or ~azure.ai.contentunderstanding.models.StringEncoding
        :keyword processing_location: The location where the data may be processed. Known values are:
         "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str or ~azure.ai.contentunderstanding.models.ProcessingLocation
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword inputs: Additional inputs to analyze. Only supported in analyzers with mode=pro.
         Default value is None.
        :paramtype inputs: list[~azure.ai.contentunderstanding.models.AnalyzeInput]
        :return: An instance of AsyncLROPoller that returns AnalyzeResult. The AnalyzeResult is compatible
         with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.contentunderstanding.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_analyze(
        self,
        analyzer_id: str,
        *,
        data: bytes,
        string_encoding: Optional[Union[str, _models.StringEncoding]] = None,
        processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
        content_type: str = "application/octet-stream",
        inputs: Optional[List[_models.AnalyzeInput]] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.AnalyzeResult]:
        """Extract content and fields from input using binary data.

        :param analyzer_id: The unique identifier of the analyzer. Required.
        :type analyzer_id: str
        :keyword data: Binary content of the document to analyze. Will be automatically base64-encoded. Required.
        :paramtype data: bytes
        :keyword string_encoding: The encoding format for content spans in the response. Known values
         are: "codePoint", "utf16", and "utf8". Default value is None.
        :paramtype string_encoding: str or ~azure.ai.contentunderstanding.models.StringEncoding
        :keyword processing_location: The location where the data may be processed. Known values are:
         "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str or ~azure.ai.contentunderstanding.models.ProcessingLocation
        :keyword content_type: Content type for binary data. Default value is "application/octet-stream".
        :paramtype content_type: str
        :keyword inputs: Additional inputs to analyze. Only supported in analyzers with mode=pro.
         Default value is None.
        :paramtype inputs: list[~azure.ai.contentunderstanding.models.AnalyzeInput]
        :return: An instance of AsyncLROPoller that returns AnalyzeResult. The AnalyzeResult is compatible
         with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.contentunderstanding.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_analyze(
        self,
        analyzer_id: str,
        body: JSON,
        *,
        string_encoding: Optional[Union[str, _models.StringEncoding]] = None,
        processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[_models.AnalyzeResult]:
        """Extract content and fields from input.

        :param analyzer_id: The unique identifier of the analyzer. Required.
        :type analyzer_id: str
        :param body: Required.
        :type body: JSON
        :keyword string_encoding: The encoding format for content spans in the response. Known values
         are: "codePoint", "utf16", and "utf8". Default value is None.
        :paramtype string_encoding: str or ~azure.ai.contentunderstanding.models.StringEncoding
        :keyword processing_location: The location where the data may be processed. Known values are:
         "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str or ~azure.ai.contentunderstanding.models.ProcessingLocation
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns AnalyzeResult. The AnalyzeResult is compatible
         with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.contentunderstanding.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_analyze(
        self,
        analyzer_id: str,
        body: IO[bytes],
        *,
        string_encoding: Optional[Union[str, _models.StringEncoding]] = None,
        processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[_models.AnalyzeResult]:
        """Extract content and fields from input.

        :param analyzer_id: The unique identifier of the analyzer. Required.
        :type analyzer_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword string_encoding: The encoding format for content spans in the response. Known values
         are: "codePoint", "utf16", and "utf8". Default value is None.
        :paramtype string_encoding: str or ~azure.ai.contentunderstanding.models.StringEncoding
        :keyword processing_location: The location where the data may be processed. Known values are:
         "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str or ~azure.ai.contentunderstanding.models.ProcessingLocation
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns AnalyzeResult. The AnalyzeResult is compatible
         with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.contentunderstanding.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_analyze(
            self, analyzer_id: str, *args: Any, **kwargs: Any
    ) -> AsyncLROPoller[_models.AnalyzeResult]:  # type: ignore[override]
        """Extract content and fields from input with url/data mutual exclusivity.

        This method enforces that url and data cannot be provided simultaneously,
        while allowing all other original behaviors including body parameters and inputs.

        :param analyzer_id: The unique identifier of the analyzer. Required.
        :type analyzer_id: str
        :param args: Variable length argument list.
        :type args: Any
        :param kwargs: Arbitrary keyword arguments.
        :type kwargs: Any
        :return: An instance of AsyncLROPoller that returns AnalyzeResult. The AnalyzeResult is compatible
         with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.contentunderstanding.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Validate that url and data are not provided together
        if ('url' in kwargs and kwargs['url'] is not None and
                'data' in kwargs and kwargs['data'] is not None):
            raise ValueError(
                "Cannot provide both 'url' and 'data' parameters simultaneously"
            )

        # Handle bytes data by calling begin_analyze_binary for better efficiency
        # Only route to begin_analyze_binary when:
        # 1. data is provided and is bytes (raw binary data)
        # 2. inputs is None (begin_analyze_binary doesn't support inputs parameter)
        if ('data' in kwargs and kwargs['data'] is not None and
                isinstance(kwargs['data'], bytes) and
                ('inputs' not in kwargs or kwargs.get('inputs') is None)):
            data_bytes = kwargs.pop('data')
            # Extract parameters that begin_analyze_binary supports
            string_encoding = kwargs.pop('string_encoding', None)
            processing_location = kwargs.pop('processing_location', None)
            content_type = kwargs.pop('content_type', 'application/octet-stream')

            return await super().begin_analyze_binary(
                analyzer_id=analyzer_id,
                input=data_bytes,
                string_encoding=string_encoding,
                processing_location=processing_location,
                content_type=content_type,
                **kwargs
            )

        # Call the original method for all other cases
        return await super().begin_analyze(analyzer_id, *args, **kwargs)


class ContentClassifiersOperations(ContentClassifiersOperationsGenerated):
    """Extended ContentClassifiersOperations with url/data mutual exclusivity enforcement."""
    @overload
    async def begin_classify(
        self,
        classifier_id: str,
        *,
        url: str,
        string_encoding: Optional[Union[str, _models.StringEncoding]] = None,
        processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.ClassifyResult]:
        """Classify content using URL.

        :param classifier_id: The unique identifier of the classifier. Required.
        :type classifier_id: str
        :keyword url: The URL of the document to classify. Required.
        :paramtype url: str
        :keyword string_encoding: The encoding format for content spans in the response. Known values
         are: "codePoint", "utf16", and "utf8". Default value is None.
        :paramtype string_encoding: str or ~azure.ai.contentunderstanding.models.StringEncoding
        :keyword processing_location: The location where the data may be processed. Known values are:
         "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str or ~azure.ai.contentunderstanding.models.ProcessingLocation
        :return: An instance of AsyncLROPoller that returns ClassifyResult. The ClassifyResult is compatible
         with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.contentunderstanding.models.ClassifyResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_classify(
        self,
        classifier_id: str,
        *,
        data: bytes,
        string_encoding: Optional[Union[str, _models.StringEncoding]] = None,
        processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.ClassifyResult]:
        """Classify content using binary data.

        :param classifier_id: The unique identifier of the classifier. Required.
        :type classifier_id: str
        :keyword data: Binary content of the document to classify. Will be automatically base64-encoded. Required.
        :paramtype data: bytes
        :keyword string_encoding: The encoding format for content spans in the response. Known values
         are: "codePoint", "utf16", and "utf8". Default value is None.
        :paramtype string_encoding: str or ~azure.ai.contentunderstanding.models.StringEncoding
        :keyword processing_location: The location where the data may be processed. Known values are:
         "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str or ~azure.ai.contentunderstanding.models.ProcessingLocation
        :return: An instance of AsyncLROPoller that returns ClassifyResult. The ClassifyResult is compatible
         with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.contentunderstanding.models.ClassifyResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_classify(
        self,
        classifier_id: str,
        body: JSON,
        *,
        string_encoding: Optional[Union[str, _models.StringEncoding]] = None,
        processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[_models.ClassifyResult]:
        """Classify content with optional splitting.

        :param classifier_id: The unique identifier of the classifier. Required.
        :type classifier_id: str
        :param body: Required.
        :type body: JSON
        :keyword string_encoding: The encoding format for content spans in the response. Known values
         are: "codePoint", "utf16", and "utf8". Default value is None.
        :paramtype string_encoding: str or ~azure.ai.contentunderstanding.models.StringEncoding
        :keyword processing_location: The location where the data may be processed. Known values are:
         "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str or ~azure.ai.contentunderstanding.models.ProcessingLocation
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns ClassifyResult. The ClassifyResult is compatible
         with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.contentunderstanding.models.ClassifyResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_classify(
        self,
        classifier_id: str,
        body: IO[bytes],
        *,
        string_encoding: Optional[Union[str, _models.StringEncoding]] = None,
        processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[_models.ClassifyResult]:
        """Classify content with optional splitting.

        :param classifier_id: The unique identifier of the classifier. Required.
        :type classifier_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword string_encoding: The encoding format for content spans in the response. Known values
         are: "codePoint", "utf16", and "utf8". Default value is None.
        :paramtype string_encoding: str or ~azure.ai.contentunderstanding.models.StringEncoding
        :keyword processing_location: The location where the data may be processed. Known values are:
         "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str or ~azure.ai.contentunderstanding.models.ProcessingLocation
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns ClassifyResult. The ClassifyResult is compatible
         with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.contentunderstanding.models.ClassifyResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_classify(
            self, classifier_id: str, *args: Any, **kwargs: Any
    ) -> AsyncLROPoller[_models.ClassifyResult]:  # type: ignore[override]
        """Classify content with url/data mutual exclusivity.

        This method enforces that url and data cannot be provided simultaneously,
        while allowing all other original behaviors including body parameters.

        :param classifier_id: The unique identifier of the classifier. Required.
        :type classifier_id: str
        :param args: Variable length argument list.
        :type args: Any
        :param kwargs: Arbitrary keyword arguments.
        :type kwargs: Any
        :return: An instance of AsyncLROPoller that returns ClassifyResult. The ClassifyResult is compatible
         with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.contentunderstanding.models.ClassifyResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Validate that url and data are not provided together
        if ('url' in kwargs and kwargs['url'] is not None and
                'data' in kwargs and kwargs['data'] is not None):
            raise ValueError(
                "Cannot provide both 'url' and 'data' parameters simultaneously"
            )

        # Handle bytes data by calling begin_classify_binary for better efficiency
        if ('data' in kwargs and kwargs['data'] is not None and
                isinstance(kwargs['data'], bytes)):
            data_bytes = kwargs.pop('data')
            # Extract parameters that begin_classify_binary supports
            string_encoding = kwargs.pop('string_encoding', None)
            processing_location = kwargs.pop('processing_location', None)
            content_type = kwargs.pop('content_type', 'application/octet-stream')

            return await super().begin_classify_binary(
                classifier_id=classifier_id,
                input=data_bytes,
                string_encoding=string_encoding,
                processing_location=processing_location,
                content_type=content_type,
                **kwargs
            )

        # Call the original method for all other cases
        return await super().begin_classify(classifier_id, *args, **kwargs)
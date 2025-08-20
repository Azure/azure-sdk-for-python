# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional, Any, Union, overload
from azure.core.tracing.decorator_async import distributed_trace_async

__all__: List[str] = ["FacesOperations"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    pass


# Make FacesOperations available for import - following WebPubSub pattern
from ._operations import FacesOperations as FacesOperationsGenerated
from ._operations import build_faces_detect_request
from ...models import DetectFacesResult

class FacesOperations(FacesOperationsGenerated):
    """Extended FacesOperations with improved detect method overloads."""
    
    @overload
    async def detect(
        self,
        url: str,
        *,
        max_detected_faces: Optional[int] = None,
        **kwargs: Any
    ) -> DetectFacesResult:
        """Detect faces using image URL.
        
        :param url: Image URL
        :type url: str
        :param max_detected_faces: Maximum number of faces to return (up to 100)
        :type max_detected_faces: int
        :return: DetectFacesResult
        :rtype: ~azure.ai.contentunderstanding.models.DetectFacesResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        pass

    @overload
    async def detect(
        self,
        data: bytes,
        *,
        max_detected_faces: Optional[int] = None,
        **kwargs: Any
    ) -> DetectFacesResult:
        """Detect faces using image data.
        
        :param data: Base64-encoded image data as bytes
        :type data: bytes  
        :param max_detected_faces: Maximum number of faces to return (up to 100)
        :type max_detected_faces: int
        :return: DetectFacesResult
        :rtype: ~azure.ai.contentunderstanding.models.DetectFacesResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        pass

    @distributed_trace_async
    async def detect(self, *args, **kwargs) -> DetectFacesResult:
        """Detect faces in an image with improved overloads.
        
        This method accepts either:
        - A string URL as the first argument: detect("http://...")
        - Base64-encoded image data as bytes as the first argument: detect(bytes_data)
        - Original keyword arguments: detect(url="...", data="...", body={...})
        
        :return: DetectFacesResult
        :rtype: ~azure.ai.contentunderstanding.models.DetectFacesResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Check if we have a positional argument (our new overloads)
        if args and len(args) >= 1:
            input_data = args[0]
            
            if isinstance(input_data, str):
                # URL as positional argument
                return await super().detect(url=input_data, **kwargs)
            
            elif isinstance(input_data, bytes):
                # Bytes as positional argument - convert to string for API
                return await super().detect(data=input_data, **kwargs)
        
        # Check if data keyword argument is bytes (needs conversion)
        elif 'data' in kwargs and isinstance(kwargs['data'], bytes):
            # Convert bytes to string for the API
            data_bytes = kwargs.pop('data')
            return await super().detect(data=data_bytes, *args, **kwargs)
        
        # Fall back to original method behavior (all other keyword arguments)
        else:
            return await super().detect(*args, **kwargs)
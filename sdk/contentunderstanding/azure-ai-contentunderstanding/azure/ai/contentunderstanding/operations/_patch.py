# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional, Any, Union, overload
from azure.core.tracing.decorator import distributed_trace

__all__: List[str] = ["FacesOperations", "PersonDirectoriesOperations"]  # Add all objects you want publicly available to users at this package level


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
from ..models import DetectFacesResult

class FacesOperations(FacesOperationsGenerated):
    """Extended FacesOperations with improved detect method overloads."""
    
    @overload
    def detect(
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
    def detect(
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

    @distributed_trace
    def detect(self, *args, **kwargs) -> DetectFacesResult:
        """Detect faces in an image with improved overloads.
        
        This method accepts either:
        - A string URL as the first argument
        - Base64-encoded image data as bytes as the first argument
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
                return super().detect(url=input_data, **kwargs)
            
            elif isinstance(input_data, bytes):

                return super().detect(data=input_data, **kwargs)
        
        # Check if data keyword argument is bytes (needs conversion)
        elif 'data' in kwargs and isinstance(kwargs['data'], bytes):
            # Convert bytes to string for the API
            data_bytes = kwargs.pop('data')
            return super().detect(data=data_bytes, *args, **kwargs)
        
        # Fall back to original method behavior (all other keyword arguments)
        else:
            return super().detect(*args, **kwargs)


# Make PersonDirectoriesOperations available for import
from ._operations import PersonDirectoriesOperations as PersonDirectoriesOperationsGenerated
from ..models import PersonDirectoryFace, FindSimilarFacesResult

class PersonDirectoriesOperations(PersonDirectoriesOperationsGenerated):
    """Extended PersonDirectoriesOperations with improved add_face and find_similar_faces method overloads."""
    
    @overload
    def add_face(
        self,
        person_directory_id: str,
        url: str,
        *,
        max_detected_faces: Optional[int] = None,
        **kwargs: Any
    ) -> PersonDirectoryFace:
        """Add a face to a person using image URL.
        
        :param person_directory_id: The person directory ID
        :type person_directory_id: str
        :param url: Image URL
        :type url: str
        :param max_detected_faces: Maximum number of faces to return (up to 100)
        :type max_detected_faces: int
        :return: PersonDirectoryFace
        :rtype: ~azure.ai.contentunderstanding.models.PersonDirectoryFace
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        pass

    @overload
    def add_face(
        self,
        person_directory_id: str,
        data: bytes,
        *,
        max_detected_faces: Optional[int] = None,
        **kwargs: Any
    ) -> PersonDirectoryFace:
        """Add a face to a person using image data.
        
        :param person_directory_id: The person directory ID
        :type person_directory_id: str
        :param data: Image data as bytes
        :type data: bytes
        :param max_detected_faces: Maximum number of faces to return (up to 100)
        :type max_detected_faces: int
        :return: PersonDirectoryFace
        :rtype: ~azure.ai.contentunderstanding.models.PersonDirectoryFace
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        pass

    @overload
    def find_similar_faces(
        self,
        person_directory_id: str,
        url: str,
        *,
        max_similar_faces: Optional[int] = None,
        **kwargs: Any
    ) -> FindSimilarFacesResult:
        """Find similar faces using image URL.
        
        :param person_directory_id: The person directory ID
        :type person_directory_id: str
        :param url: Image URL
        :type url: str
        :param max_similar_faces: Maximum number of similar faces to return (up to 1000)
        :type max_similar_faces: int
        :return: FindSimilarFacesResult
        :rtype: ~azure.ai.contentunderstanding.models.FindSimilarFacesResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        pass

    @overload
    def find_similar_faces(
        self,
        person_directory_id: str,
        data: bytes,
        *,
        max_similar_faces: Optional[int] = None,
        **kwargs: Any
    ) -> FindSimilarFacesResult:
        """Find similar faces using image data.
        
        :param person_directory_id: The person directory ID
        :type person_directory_id: str
        :param data: Base64-encoded image data as bytes
        :type data: bytes
        :param max_similar_faces: Maximum number of similar faces to return (up to 1000)
        :type max_similar_faces: int
        :return: FindSimilarFacesResult
        :rtype: ~azure.ai.contentunderstanding.models.FindSimilarFacesResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        pass

    @distributed_trace
    def add_face(self, person_directory_id: str, *args, **kwargs) -> PersonDirectoryFace:
        """Add a face to a person with improved overloads.
        
        This method accepts either:
        - A string URL as the second argument: add_face(dir_id, "http://...")
        - Image data as bytes as the second argument: add_face(dir_id, bytes_data)
        - Original keyword arguments: add_face(person_directory_id=..., body={...}, person_id=...)
        
        :param person_directory_id: The person directory ID
        :type person_directory_id: str
        :return: PersonDirectoryFace
        :rtype: ~azure.ai.contentunderstanding.models.PersonDirectoryFace
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Check if we have a second positional argument (our new overloads)
        if args and len(args) >= 1:
            input_data = args[0]
            
            if isinstance(input_data, str):
                # URL as second argument
                return super().add_face(
                    person_directory_id=person_directory_id,
                    face_source={"url": input_data},
                    **kwargs
                )
            
            elif isinstance(input_data, bytes):
                # Bytes as second argument - use FaceSource object
                from ..models import FaceSource
                face_source = FaceSource(data=input_data)
                return super().add_face(
                    person_directory_id=person_directory_id,
                    face_source=face_source,
                    **kwargs
                )
        
        # Check if we have face_source in kwargs with bytes data
        elif 'face_source' in kwargs and isinstance(kwargs['face_source'], dict):
            face_source_dict = kwargs['face_source']
            if 'data' in face_source_dict:
                data_value = face_source_dict['data']
                if isinstance(data_value, bytes):
                    # Convert dict to FaceSource object with bytes
                    from ..models import FaceSource
                    kwargs['face_source'] = FaceSource(data=data_value)
        
        # Fall back to original method behavior
        return super().add_face(person_directory_id=person_directory_id, **kwargs)

    @distributed_trace
    def find_similar_faces(self, person_directory_id: str, *args, **kwargs) -> FindSimilarFacesResult:
        """Find similar faces with improved overloads.
        
        This method accepts either:
        - A string URL as the second argument: find_similar_faces(dir_id, "http://...")
        - Base64-encoded image data as bytes as the second argument: find_similar_faces(dir_id, bytes_data)
        - Original keyword arguments: find_similar_faces(person_directory_id=..., face_source=..., max_similar_faces=...)
        
        :param person_directory_id: The person directory ID
        :type person_directory_id: str
        :return: FindSimilarFacesResult
        :rtype: ~azure.ai.contentunderstanding.models.FindSimilarFacesResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Check if we have a second positional argument (our new overloads)
        if args and len(args) >= 1:
            input_data = args[0]
            
            if isinstance(input_data, str):
                # URL as second argument
                from ..models import FaceSource
                face_source = FaceSource(url=input_data)
                return super().find_similar_faces(
                    person_directory_id=person_directory_id,
                    face_source=face_source,
                    **kwargs
                )
            
            elif isinstance(input_data, bytes):
                # Bytes as second argument - use FaceSource object
                from ..models import FaceSource
                face_source = FaceSource(data=input_data)
                return super().find_similar_faces(
                    person_directory_id=person_directory_id,
                    face_source=face_source,
                    **kwargs
                )
        
        # Check if we have face_source in kwargs with bytes data
        elif 'face_source' in kwargs and isinstance(kwargs['face_source'], dict):
            face_source_dict = kwargs['face_source']
            if 'data' in face_source_dict:
                data_value = face_source_dict['data']
                if isinstance(data_value, bytes):
                    # Convert dict to FaceSource object with bytes
                    from ..models import FaceSource
                    kwargs['face_source'] = FaceSource(data=data_value)
        
        # Fall back to original method behavior
        return super().find_similar_faces(person_directory_id=person_directory_id, **kwargs)
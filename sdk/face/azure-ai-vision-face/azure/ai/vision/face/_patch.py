# pylint: disable=too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, IO, List, Optional, Union, overload

from azure.core.tracing.decorator import distributed_trace

from . import models as _models
from ._client import FaceClient as FaceClientGenerated
from ._client import FaceSessionClient as FaceSessionClientGenerated
from .operations._operations import JSON, _Unset


class FaceClient(FaceClientGenerated):
    """FaceClient.

    :param endpoint: Supported Cognitive Services endpoints (protocol and hostname, for example:
     https://{resource-name}.cognitiveservices.azure.com). Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential
    :keyword api_version: API Version. Default value is "v1.2-preview.1". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str or ~azure.ai.vision.face.models.Versions
    """

    @overload
    def detect_from_url(
        self,
        *,
        url: str,
        content_type: str = "application/json",
        detection_model: Union[str, _models.FaceDetectionModel],
        recognition_model: Union[str, _models.FaceRecognitionModel],
        return_face_id: bool,
        return_face_attributes: Optional[List[Union[str, _models.FaceAttributeType]]] = None,
        return_face_landmarks: Optional[bool] = None,
        return_recognition_model: Optional[bool] = None,
        face_id_time_to_live: Optional[int] = None,
        **kwargs: Any,
    ) -> List[_models.FaceDetectionResult]: ...

    @overload
    def detect_from_url(
        self,
        body: JSON,
        *,
        content_type: str = "application/json",
        detection_model: Union[str, _models.FaceDetectionModel],
        recognition_model: Union[str, _models.FaceRecognitionModel],
        return_face_id: bool,
        return_face_attributes: Optional[List[Union[str, _models.FaceAttributeType]]] = None,
        return_face_landmarks: Optional[bool] = None,
        return_recognition_model: Optional[bool] = None,
        face_id_time_to_live: Optional[int] = None,
        **kwargs: Any,
    ) -> List[_models.FaceDetectionResult]: ...

    @overload
    def detect_from_url(
        self,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        detection_model: Union[str, _models.FaceDetectionModel],
        recognition_model: Union[str, _models.FaceRecognitionModel],
        return_face_id: bool,
        return_face_attributes: Optional[List[Union[str, _models.FaceAttributeType]]] = None,
        return_face_landmarks: Optional[bool] = None,
        return_recognition_model: Optional[bool] = None,
        face_id_time_to_live: Optional[int] = None,
        **kwargs: Any,
    ) -> List[_models.FaceDetectionResult]: ...

    @distributed_trace
    def detect_from_url(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        url: str = _Unset,
        detection_model: Union[str, _models.FaceDetectionModel],
        recognition_model: Union[str, _models.FaceRecognitionModel],
        return_face_id: bool,
        return_face_attributes: Optional[List[Union[str, _models.FaceAttributeType]]] = None,
        return_face_landmarks: Optional[bool] = None,
        return_recognition_model: Optional[bool] = None,
        face_id_time_to_live: Optional[int] = None,
        **kwargs: Any,
    ) -> List[_models.FaceDetectionResult]:
        """Detect human faces in an image, return face rectangles, and optionally with faceIds, landmarks,
        and attributes.

        Please refer to
        https://learn.microsoft.com/rest/api/face/face-detection-operations/detect-from-url for more
        details.

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword url: URL of input image. Required.
        :paramtype url: str
        :keyword detection_model: The 'detectionModel' associated with the detected faceIds. Supported
         'detectionModel' values include 'detection_01', 'detection_02' and 'detection_03'. The default
         value is 'detection_01'. 'detection_03' is recommended since its accuracy is improved on
         smaller faces (64x64 pixels) and rotated face orientations. Known values are: "detection_01",
         "detection_02", and "detection_03". Default value is None.
        :paramtype detection_model: str or ~azure.ai.vision.face.models.FaceDetectionModel
        :keyword recognition_model: The 'recognitionModel' associated with the detected faceIds.
         Supported 'recognitionModel' values include 'recognition_01', 'recognition_02',
         'recognition_03' or 'recognition_04'. The default value is 'recognition_01'. 'recognition_04'
         is recommended since its accuracy is improved on faces wearing masks compared with
         'recognition_03', and its overall accuracy is improved compared with 'recognition_01' and
         'recognition_02'. Known values are: "recognition_01", "recognition_02", "recognition_03", and
         "recognition_04". Default value is None.
        :paramtype recognition_model: str or ~azure.ai.vision.face.models.FaceRecognitionModel
        :keyword return_face_id: Return faceIds of the detected faces or not. The default value is
         true. Default value is None.
        :paramtype return_face_id: bool
        :keyword return_face_attributes: Analyze and return the one or more specified face attributes
         in the comma-separated string like 'returnFaceAttributes=headPose,glasses'. Face attribute
         analysis has additional computational and time cost. Default value is None.
        :paramtype return_face_attributes: list[str or ~azure.ai.vision.face.models.FaceAttributeType]
        :keyword return_face_landmarks: Return face landmarks of the detected faces or not. The default
         value is false. Default value is None.
        :paramtype return_face_landmarks: bool
        :keyword return_recognition_model: Return 'recognitionModel' or not. The default value is
         false. This is only applicable when returnFaceId = true. Default value is None.
        :paramtype return_recognition_model: bool
        :keyword face_id_time_to_live: The number of seconds for the face ID being cached. Supported
         range from 60 seconds up to 86400 seconds. The default value is 86400 (24 hours). Default value
         is None.
        :paramtype face_id_time_to_live: int
        :return: list of FaceDetectionResult
        :rtype: list[~azure.ai.vision.face.models.FaceDetectionResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._detect_from_url(
            body,
            url=url,
            detection_model=detection_model,
            recognition_model=recognition_model,
            return_face_id=return_face_id,
            return_face_attributes=return_face_attributes,
            return_face_landmarks=return_face_landmarks,
            return_recognition_model=return_recognition_model,
            face_id_time_to_live=face_id_time_to_live,
            **kwargs,
        )

    @distributed_trace
    def detect(
        self,
        image_content: bytes,
        *,
        detection_model: Union[str, _models.FaceDetectionModel],
        recognition_model: Union[str, _models.FaceRecognitionModel],
        return_face_id: bool,
        return_face_attributes: Optional[List[Union[str, _models.FaceAttributeType]]] = None,
        return_face_landmarks: Optional[bool] = None,
        return_recognition_model: Optional[bool] = None,
        face_id_time_to_live: Optional[int] = None,
        **kwargs: Any,
    ) -> List[_models.FaceDetectionResult]:
        """Detect human faces in an image, return face rectangles, and optionally with faceIds, landmarks,
        and attributes.

        Please refer to https://learn.microsoft.com/rest/api/face/face-detection-operations/detect for
        more details.

        :param image_content: The input image binary. Required.
        :type image_content: bytes
        :keyword detection_model: The 'detectionModel' associated with the detected faceIds. Supported
         'detectionModel' values include 'detection_01', 'detection_02' and 'detection_03'. The default
         value is 'detection_01'. 'detection_03' is recommended since its accuracy is improved on
         smaller faces (64x64 pixels) and rotated face orientations. Known values are: "detection_01",
         "detection_02", and "detection_03". Default value is None.
        :paramtype detection_model: str or ~azure.ai.vision.face.models.FaceDetectionModel
        :keyword recognition_model: The 'recognitionModel' associated with the detected faceIds.
         Supported 'recognitionModel' values include 'recognition_01', 'recognition_02',
         'recognition_03' or 'recognition_04'. The default value is 'recognition_01'. 'recognition_04'
         is recommended since its accuracy is improved on faces wearing masks compared with
         'recognition_03', and its overall accuracy is improved compared with 'recognition_01' and
         'recognition_02'. Known values are: "recognition_01", "recognition_02", "recognition_03", and
         "recognition_04". Default value is None.
        :paramtype recognition_model: str or ~azure.ai.vision.face.models.FaceRecognitionModel
        :keyword return_face_id: Return faceIds of the detected faces or not. The default value is
         true. Default value is None.
        :paramtype return_face_id: bool
        :keyword return_face_attributes: Analyze and return the one or more specified face attributes
         in the comma-separated string like 'returnFaceAttributes=headPose,glasses'. Face attribute
         analysis has additional computational and time cost. Default value is None.
        :paramtype return_face_attributes: list[str or ~azure.ai.vision.face.models.FaceAttributeType]
        :keyword return_face_landmarks: Return face landmarks of the detected faces or not. The default
         value is false. Default value is None.
        :paramtype return_face_landmarks: bool
        :keyword return_recognition_model: Return 'recognitionModel' or not. The default value is
         false. This is only applicable when returnFaceId = true. Default value is None.
        :paramtype return_recognition_model: bool
        :keyword face_id_time_to_live: The number of seconds for the face ID being cached. Supported
         range from 60 seconds up to 86400 seconds. The default value is 86400 (24 hours). Default value
         is None.
        :paramtype face_id_time_to_live: int
        :return: list of FaceDetectionResult
        :rtype: list[~azure.ai.vision.face.models.FaceDetectionResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._detect(
            image_content,
            detection_model=detection_model,
            recognition_model=recognition_model,
            return_face_id=return_face_id,
            return_face_attributes=return_face_attributes,
            return_face_landmarks=return_face_landmarks,
            return_recognition_model=return_recognition_model,
            face_id_time_to_live=face_id_time_to_live,
            **kwargs,
        )

    def __enter__(self) -> "FaceClient":
        super().__enter__()
        return self


class FaceSessionClient(FaceSessionClientGenerated):
    """FaceSessionClient.

    :param endpoint: Supported Cognitive Services endpoints (protocol and hostname, for example:
     https://{resource-name}.cognitiveservices.azure.com). Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential
    :keyword api_version: API Version. Default value is "v1.2-preview.1". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str or ~azure.ai.vision.face.models.Versions
    """

    @overload
    def create_liveness_with_verify_session(
        self,
        body: _models.CreateLivenessWithVerifySessionContent,
        *,
        verify_image: Union[bytes, None],
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.CreateLivenessWithVerifySessionResult: ...

    @overload
    def create_liveness_with_verify_session(
        self,
        body: JSON,
        *,
        verify_image: Union[bytes, None],
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.CreateLivenessWithVerifySessionResult: ...

    @distributed_trace
    def create_liveness_with_verify_session(
        self,
        body: Union[_models.CreateLivenessWithVerifySessionContent, JSON],
        *,
        verify_image: Union[bytes, None],
        **kwargs: Any,
    ) -> _models.CreateLivenessWithVerifySessionResult:
        """Create a new liveness session with verify. Client device submits VerifyImage during the
        /detectLivenessWithVerify/singleModal call.

        Please refer to
        https://learn.microsoft.com/rest/api/face/liveness-session-operations/create-liveness-with-verify-session
        for more details.

        :param body: Body parameter. Is one of the following types:
         CreateLivenessWithVerifySessionContent, JSON, IO[bytes] Required.
        :type body: ~azure.ai.vision.face.models.CreateLivenessWithVerifySessionContent or JSON or
         IO[bytes]
        :return: CreateLivenessWithVerifySessionResult. The CreateLivenessWithVerifySessionResult is
         compatible with MutableMapping
        :rtype: ~azure.ai.vision.face.models.CreateLivenessWithVerifySessionResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if verify_image is not None:
            if not isinstance(body, _models.CreateLivenessWithVerifySessionContent):
            # Convert body to CreateLivenessWithVerifySessionContent if necessary
                body = _models.CreateLivenessWithVerifySessionContent(**body)
            request_body = (
                _models._models.CreateLivenessWithVerifySessionMultipartContent(  # pylint: disable=protected-access
                    parameters=body,
                    verify_image=("verify-image", verify_image),
                )
            )
            return super()._create_liveness_with_verify_session_with_verify_image(request_body, **kwargs)

        return super()._create_liveness_with_verify_session(body, **kwargs)

    def __enter__(self) -> "FaceSessionClient":
        super().__enter__()
        return self


__all__: List[str] = [
    "FaceClient",
    "FaceSessionClient",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

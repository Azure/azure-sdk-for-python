# pylint: disable=too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, IO, List, Optional, Union, overload

from azure.core.tracing.decorator_async import distributed_trace_async

from .. import models as _models
from ._client import FaceClient as FaceClientGenerated
from ._client import FaceSessionClient as FaceSessionClientGenerated
from ._operations._operations import JSON, _Unset


class FaceClient(FaceClientGenerated):
    """FaceClient.

    :param endpoint: Supported Cognitive Services endpoints (protocol and hostname, for example:
     https://{resource-name}.cognitiveservices.azure.com). Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: API Version. Default value is "v1.1-preview.1". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str or ~azure.ai.vision.face.models.Versions
    """

    @overload
    async def detect_from_url(
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
    async def detect_from_url(
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
    async def detect_from_url(
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

    @distributed_trace_async
    async def detect_from_url(
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
        # pylint: disable=line-too-long
        """Detect human faces in an image, return face rectangles, and optionally with faceIds, landmarks,
        and attributes.

        ..

           [!IMPORTANT]
           To mitigate potential misuse that can subject people to stereotyping, discrimination, or
        unfair denial of services, we are retiring Face API attributes that predict emotion, gender,
        age, smile, facial hair, hair, and makeup. Read more about this decision
        https://azure.microsoft.com/blog/responsible-ai-investments-and-safeguards-for-facial-recognition/.


        *


        * No image will be stored. Only the extracted face feature(s) will be stored on server. The
        faceId is an identifier of the face feature and will be used in Face - Identify, Face - Verify,
        and Face - Find Similar. The stored face features will expire and be deleted at the time
        specified by faceIdTimeToLive after the original detection call.
        * Optional parameters include faceId, landmarks, and attributes. Attributes include headPose,
        glasses, occlusion, accessories, blur, exposure, noise, mask, and qualityForRecognition. Some
        of the results returned for specific attributes may not be highly accurate.
        * JPEG, PNG, GIF (the first frame), and BMP format are supported. The allowed image file size
        is from 1KB to 6MB.
        * The minimum detectable face size is 36x36 pixels in an image no larger than 1920x1080 pixels.
        Images with dimensions higher than 1920x1080 pixels will need a proportionally larger minimum
        face size.
        * Up to 100 faces can be returned for an image. Faces are ranked by face rectangle size from
        large to small.
        * For optimal results when querying Face - Identify, Face - Verify, and Face - Find Similar
        ('returnFaceId' is true), please use faces that are: frontal, clear, and with a minimum size of
        200x200 pixels (100 pixels between eyes).
        * Different 'detectionModel' values can be provided. To use and compare different detection
        models, please refer to
        https://learn.microsoft.com/azure/ai-services/computer-vision/how-to/specify-detection-model

          * 'detection_02': Face attributes and landmarks are disabled if you choose this detection
        model.
          * 'detection_03': Face attributes (mask and headPose only) and landmarks are supported if you
        choose this detection model.

        * Different 'recognitionModel' values are provided. If follow-up operations like Verify,
        Identify, Find Similar are needed, please specify the recognition model with 'recognitionModel'
        parameter. The default value for 'recognitionModel' is 'recognition_01', if latest model
        needed, please explicitly specify the model you need in this parameter. Once specified, the
        detected faceIds will be associated with the specified recognition model. More details, please
        refer to
        https://learn.microsoft.com/azure/ai-services/computer-vision/how-to/specify-recognition-model.

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword url: URL of input image. Required when body is not set.
        :paramtype url: str
        :keyword detection_model: The 'detectionModel' associated with the detected faceIds. Supported
         'detectionModel' values include 'detection_01', 'detection_02' and 'detection_03'. The default
         value is 'detection_01'. Known values are: "detection_01", "detection_02", and "detection_03".
         Required.
        :paramtype detection_model: str or ~azure.ai.vision.face.models.FaceDetectionModel
        :keyword recognition_model: The 'recognitionModel' associated with the detected faceIds.
         Supported 'recognitionModel' values include 'recognition_01', 'recognition_02',
         'recognition_03' or 'recognition_04'. The default value is 'recognition_01'. 'recognition_04'
         is recommended since its accuracy is improved on faces wearing masks compared with
         'recognition_03', and its overall accuracy is improved compared with 'recognition_01' and
         'recognition_02'. Known values are: "recognition_01", "recognition_02", "recognition_03", and
         "recognition_04". Required.
        :paramtype recognition_model: str or ~azure.ai.vision.face.models.FaceRecognitionModel
        :keyword return_face_id: Return faceIds of the detected faces or not. Required.
        :paramtype return_face_id: bool
        :keyword return_face_attributes: Analyze and return the one or more specified face attributes
         in the comma-separated string like 'returnFaceAttributes=headPose,glasses'. Face attribute
         analysis has additional computational and time cost. Default value is None.
        :paramtype return_face_attributes: list[str or ~azure.ai.vision.face.models.FaceAttributeType]
        :keyword return_face_landmarks: Return face landmarks of the detected faces or not. The default
         value is false. Default value is None.
        :paramtype return_face_landmarks: bool
        :keyword return_recognition_model: Return 'recognitionModel' or not. The default value is
         false. Default value is None.
        :paramtype return_recognition_model: bool
        :keyword face_id_time_to_live: The number of seconds for the face ID being cached. Supported
         range from 60 seconds up to 86400 seconds. The default value is 86400 (24 hours). Default value
         is None.
        :paramtype face_id_time_to_live: int
        :return: list of FaceDetectionResult
        :rtype: list[~azure.ai.vision.face.models.FaceDetectionResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "url": "str"  # URL of input image. Required.
                }

                # response body for status code(s): 200
                response == [
                    {
                        "faceRectangle": {
                            "height": 0,  # The height of the rectangle, in pixels.
                              Required.
                            "left": 0,  # The distance from the left edge if the image to
                              the left edge of the rectangle, in pixels. Required.
                            "top": 0,  # The distance from the top edge if the image to
                              the top edge of the rectangle, in pixels. Required.
                            "width": 0  # The width of the rectangle, in pixels.
                              Required.
                        },
                        "faceAttributes": {
                            "accessories": [
                                {
                                    "confidence": 0.0,  # Confidence level of the
                                      accessory type. Range between [0,1]. Required.
                                    "type": "str"  # Type of the accessory.
                                      Required. Known values are: "headwear", "glasses", and "mask".
                                }
                            ],
                            "age": 0.0,  # Optional. Age in years.
                            "blur": {
                                "blurLevel": "str",  # An enum value indicating level
                                  of blurriness. Required. Known values are: "low", "medium", and
                                  "high".
                                "value": 0.0  # A number indicating level of
                                  blurriness ranging from 0 to 1. Required.
                            },
                            "exposure": {
                                "exposureLevel": "str",  # An enum value indicating
                                  level of exposure. Required. Known values are: "underExposure",
                                  "goodExposure", and "overExposure".
                                "value": 0.0  # A number indicating level of exposure
                                  level ranging from 0 to 1. [0, 0.25) is under exposure. [0.25, 0.75)
                                  is good exposure. [0.75, 1] is over exposure. Required.
                            },
                            "facialHair": {
                                "beard": 0.0,  # A number ranging from 0 to 1
                                  indicating a level of confidence associated with a property.
                                  Required.
                                "moustache": 0.0,  # A number ranging from 0 to 1
                                  indicating a level of confidence associated with a property.
                                  Required.
                                "sideburns": 0.0  # A number ranging from 0 to 1
                                  indicating a level of confidence associated with a property.
                                  Required.
                            },
                            "glasses": "str",  # Optional. Glasses type if any of the
                              face. Known values are: "noGlasses", "readingGlasses", "sunglasses", and
                              "swimmingGoggles".
                            "hair": {
                                "bald": 0.0,  # A number describing confidence level
                                  of whether the person is bald. Required.
                                "hairColor": [
                                    {
                                        "color": "str",  # Name of the hair
                                          color. Required. Known values are: "unknown", "white",
                                          "gray", "blond", "brown", "red", "black", and "other".
                                        "confidence": 0.0  # Confidence level
                                          of the color. Range between [0,1]. Required.
                                    }
                                ],
                                "invisible": bool  # A boolean value describing
                                  whether the hair is visible in the image. Required.
                            },
                            "headPose": {
                                "pitch": 0.0,  # Value of angles. Required.
                                "roll": 0.0,  # Value of angles. Required.
                                "yaw": 0.0  # Value of angles. Required.
                            },
                            "mask": {
                                "noseAndMouthCovered": bool,  # A boolean value
                                  indicating whether nose and mouth are covered. Required.
                                "type": "str"  # Type of the mask. Required. Known
                                  values are: "faceMask", "noMask", "otherMaskOrOcclusion", and
                                  "uncertain".
                            },
                            "noise": {
                                "noiseLevel": "str",  # An enum value indicating
                                  level of noise. Required. Known values are: "low", "medium", and
                                  "high".
                                "value": 0.0  # A number indicating level of noise
                                  level ranging from 0 to 1. [0, 0.25) is under exposure. [0.25, 0.75)
                                  is good exposure. [0.75, 1] is over exposure. [0, 0.3) is low noise
                                  level. [0.3, 0.7) is medium noise level. [0.7, 1] is high noise
                                  level. Required.
                            },
                            "occlusion": {
                                "eyeOccluded": bool,  # A boolean value indicating
                                  whether eyes are occluded. Required.
                                "foreheadOccluded": bool,  # A boolean value
                                  indicating whether forehead is occluded. Required.
                                "mouthOccluded": bool  # A boolean value indicating
                                  whether the mouth is occluded. Required.
                            },
                            "qualityForRecognition": "str",  # Optional. Properties
                              describing the overall image quality regarding whether the image being
                              used in the detection is of sufficient quality to attempt face
                              recognition on. Known values are: "low", "medium", and "high".
                            "smile": 0.0  # Optional. Smile intensity, a number between
                              [0,1].
                        },
                        "faceId": "str",  # Optional. Unique faceId of the detected face,
                          created by detection API and it will expire 24 hours after the detection
                          call. To return this, it requires 'returnFaceId' parameter to be true.
                        "faceLandmarks": {
                            "eyeLeftBottom": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyeLeftInner": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyeLeftOuter": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyeLeftTop": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyeRightBottom": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyeRightInner": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyeRightOuter": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyeRightTop": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyebrowLeftInner": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyebrowLeftOuter": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyebrowRightInner": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyebrowRightOuter": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "mouthLeft": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "mouthRight": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "noseLeftAlarOutTip": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "noseLeftAlarTop": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "noseRightAlarOutTip": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "noseRightAlarTop": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "noseRootLeft": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "noseRootRight": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "noseTip": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "pupilLeft": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "pupilRight": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "underLipBottom": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "underLipTop": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "upperLipBottom": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "upperLipTop": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            }
                        },
                        "recognitionModel": "str"  # Optional. The 'recognitionModel'
                          associated with this faceId. This is only returned when
                          'returnRecognitionModel' is explicitly set as true. Known values are:
                          "recognition_01", "recognition_02", "recognition_03", and "recognition_04".
                    }
                ]
        """
        return await super()._detect_from_url(
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

    @distributed_trace_async
    async def detect(
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
        # pylint: disable=line-too-long
        """Detect human faces in an image, return face rectangles, and optionally with faceIds, landmarks,
        and attributes.

        ..

           [!IMPORTANT]
           To mitigate potential misuse that can subject people to stereotyping, discrimination, or
        unfair denial of services, we are retiring Face API attributes that predict emotion, gender,
        age, smile, facial hair, hair, and makeup. Read more about this decision
        https://azure.microsoft.com/blog/responsible-ai-investments-and-safeguards-for-facial-recognition/.


        *


        * No image will be stored. Only the extracted face feature(s) will be stored on server. The
        faceId is an identifier of the face feature and will be used in Face - Identify, Face - Verify,
        and Face - Find Similar. The stored face features will expire and be deleted at the time
        specified by faceIdTimeToLive after the original detection call.
        * Optional parameters include faceId, landmarks, and attributes. Attributes include headPose,
        glasses, occlusion, accessories, blur, exposure, noise, mask, and qualityForRecognition. Some
        of the results returned for specific attributes may not be highly accurate.
        * JPEG, PNG, GIF (the first frame), and BMP format are supported. The allowed image file size
        is from 1KB to 6MB.
        * The minimum detectable face size is 36x36 pixels in an image no larger than 1920x1080 pixels.
        Images with dimensions higher than 1920x1080 pixels will need a proportionally larger minimum
        face size.
        * Up to 100 faces can be returned for an image. Faces are ranked by face rectangle size from
        large to small.
        * For optimal results when querying Face - Identify, Face - Verify, and Face - Find Similar
        ('returnFaceId' is true), please use faces that are: frontal, clear, and with a minimum size of
        200x200 pixels (100 pixels between eyes).
        * Different 'detectionModel' values can be provided. To use and compare different detection
        models, please refer to
        https://learn.microsoft.com/azure/ai-services/computer-vision/how-to/specify-detection-model

          * 'detection_02': Face attributes and landmarks are disabled if you choose this detection
        model.
          * 'detection_03': Face attributes (mask and headPose only) and landmarks are supported if you
        choose this detection model.

        * Different 'recognitionModel' values are provided. If follow-up operations like Verify,
        Identify, Find Similar are needed, please specify the recognition model with 'recognitionModel'
        parameter. The default value for 'recognitionModel' is 'recognition_01', if latest model
        needed, please explicitly specify the model you need in this parameter. Once specified, the
        detected faceIds will be associated with the specified recognition model. More details, please
        refer to
        https://learn.microsoft.com/azure/ai-services/computer-vision/how-to/specify-recognition-model.

        :param image_content: The input image binary. Required.
        :type image_content: bytes
        :keyword detection_model: The 'detectionModel' associated with the detected faceIds. Supported
         'detectionModel' values include 'detection_01', 'detection_02' and 'detection_03'. The default
         value is 'detection_01'. Known values are: "detection_01", "detection_02", and "detection_03".
         Required.
        :paramtype detection_model: str or ~azure.ai.vision.face.models.FaceDetectionModel
        :keyword recognition_model: The 'recognitionModel' associated with the detected faceIds.
         Supported 'recognitionModel' values include 'recognition_01', 'recognition_02',
         'recognition_03' or 'recognition_04'. The default value is 'recognition_01'. 'recognition_04'
         is recommended since its accuracy is improved on faces wearing masks compared with
         'recognition_03', and its overall accuracy is improved compared with 'recognition_01' and
         'recognition_02'. Known values are: "recognition_01", "recognition_02", "recognition_03", and
         "recognition_04". Required.
        :paramtype recognition_model: str or ~azure.ai.vision.face.models.FaceRecognitionModel
        :keyword return_face_id: Return faceIds of the detected faces or not. Required.
        :paramtype return_face_id: bool
        :keyword return_face_attributes: Analyze and return the one or more specified face attributes
         in the comma-separated string like 'returnFaceAttributes=headPose,glasses'. Face attribute
         analysis has additional computational and time cost. Default value is None.
        :paramtype return_face_attributes: list[str or ~azure.ai.vision.face.models.FaceAttributeType]
        :keyword return_face_landmarks: Return face landmarks of the detected faces or not. The default
         value is false. Default value is None.
        :paramtype return_face_landmarks: bool
        :keyword return_recognition_model: Return 'recognitionModel' or not. The default value is
         false. Default value is None.
        :paramtype return_recognition_model: bool
        :keyword face_id_time_to_live: The number of seconds for the face ID being cached. Supported
         range from 60 seconds up to 86400 seconds. The default value is 86400 (24 hours). Default value
         is None.
        :paramtype face_id_time_to_live: int
        :return: list of FaceDetectionResult
        :rtype: list[~azure.ai.vision.face.models.FaceDetectionResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    {
                        "faceRectangle": {
                            "height": 0,  # The height of the rectangle, in pixels.
                              Required.
                            "left": 0,  # The distance from the left edge if the image to
                              the left edge of the rectangle, in pixels. Required.
                            "top": 0,  # The distance from the top edge if the image to
                              the top edge of the rectangle, in pixels. Required.
                            "width": 0  # The width of the rectangle, in pixels.
                              Required.
                        },
                        "faceAttributes": {
                            "accessories": [
                                {
                                    "confidence": 0.0,  # Confidence level of the
                                      accessory type. Range between [0,1]. Required.
                                    "type": "str"  # Type of the accessory.
                                      Required. Known values are: "headwear", "glasses", and "mask".
                                }
                            ],
                            "age": 0.0,  # Optional. Age in years.
                            "blur": {
                                "blurLevel": "str",  # An enum value indicating level
                                  of blurriness. Required. Known values are: "low", "medium", and
                                  "high".
                                "value": 0.0  # A number indicating level of
                                  blurriness ranging from 0 to 1. Required.
                            },
                            "exposure": {
                                "exposureLevel": "str",  # An enum value indicating
                                  level of exposure. Required. Known values are: "underExposure",
                                  "goodExposure", and "overExposure".
                                "value": 0.0  # A number indicating level of exposure
                                  level ranging from 0 to 1. [0, 0.25) is under exposure. [0.25, 0.75)
                                  is good exposure. [0.75, 1] is over exposure. Required.
                            },
                            "facialHair": {
                                "beard": 0.0,  # A number ranging from 0 to 1
                                  indicating a level of confidence associated with a property.
                                  Required.
                                "moustache": 0.0,  # A number ranging from 0 to 1
                                  indicating a level of confidence associated with a property.
                                  Required.
                                "sideburns": 0.0  # A number ranging from 0 to 1
                                  indicating a level of confidence associated with a property.
                                  Required.
                            },
                            "glasses": "str",  # Optional. Glasses type if any of the
                              face. Known values are: "noGlasses", "readingGlasses", "sunglasses", and
                              "swimmingGoggles".
                            "hair": {
                                "bald": 0.0,  # A number describing confidence level
                                  of whether the person is bald. Required.
                                "hairColor": [
                                    {
                                        "color": "str",  # Name of the hair
                                          color. Required. Known values are: "unknown", "white",
                                          "gray", "blond", "brown", "red", "black", and "other".
                                        "confidence": 0.0  # Confidence level
                                          of the color. Range between [0,1]. Required.
                                    }
                                ],
                                "invisible": bool  # A boolean value describing
                                  whether the hair is visible in the image. Required.
                            },
                            "headPose": {
                                "pitch": 0.0,  # Value of angles. Required.
                                "roll": 0.0,  # Value of angles. Required.
                                "yaw": 0.0  # Value of angles. Required.
                            },
                            "mask": {
                                "noseAndMouthCovered": bool,  # A boolean value
                                  indicating whether nose and mouth are covered. Required.
                                "type": "str"  # Type of the mask. Required. Known
                                  values are: "faceMask", "noMask", "otherMaskOrOcclusion", and
                                  "uncertain".
                            },
                            "noise": {
                                "noiseLevel": "str",  # An enum value indicating
                                  level of noise. Required. Known values are: "low", "medium", and
                                  "high".
                                "value": 0.0  # A number indicating level of noise
                                  level ranging from 0 to 1. [0, 0.25) is under exposure. [0.25, 0.75)
                                  is good exposure. [0.75, 1] is over exposure. [0, 0.3) is low noise
                                  level. [0.3, 0.7) is medium noise level. [0.7, 1] is high noise
                                  level. Required.
                            },
                            "occlusion": {
                                "eyeOccluded": bool,  # A boolean value indicating
                                  whether eyes are occluded. Required.
                                "foreheadOccluded": bool,  # A boolean value
                                  indicating whether forehead is occluded. Required.
                                "mouthOccluded": bool  # A boolean value indicating
                                  whether the mouth is occluded. Required.
                            },
                            "qualityForRecognition": "str",  # Optional. Properties
                              describing the overall image quality regarding whether the image being
                              used in the detection is of sufficient quality to attempt face
                              recognition on. Known values are: "low", "medium", and "high".
                            "smile": 0.0  # Optional. Smile intensity, a number between
                              [0,1].
                        },
                        "faceId": "str",  # Optional. Unique faceId of the detected face,
                          created by detection API and it will expire 24 hours after the detection
                          call. To return this, it requires 'returnFaceId' parameter to be true.
                        "faceLandmarks": {
                            "eyeLeftBottom": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyeLeftInner": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyeLeftOuter": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyeLeftTop": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyeRightBottom": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyeRightInner": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyeRightOuter": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyeRightTop": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyebrowLeftInner": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyebrowLeftOuter": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyebrowRightInner": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "eyebrowRightOuter": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "mouthLeft": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "mouthRight": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "noseLeftAlarOutTip": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "noseLeftAlarTop": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "noseRightAlarOutTip": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "noseRightAlarTop": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "noseRootLeft": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "noseRootRight": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "noseTip": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "pupilLeft": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "pupilRight": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "underLipBottom": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "underLipTop": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "upperLipBottom": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            },
                            "upperLipTop": {
                                "x": 0.0,  # The horizontal component, in pixels.
                                  Required.
                                "y": 0.0  # The vertical component, in pixels.
                                  Required.
                            }
                        },
                        "recognitionModel": "str"  # Optional. The 'recognitionModel'
                          associated with this faceId. This is only returned when
                          'returnRecognitionModel' is explicitly set as true. Known values are:
                          "recognition_01", "recognition_02", "recognition_03", and "recognition_04".
                    }
                ]
        """
        return await super()._detect(
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

    async def __aenter__(self) -> "FaceClient":
        await super().__aenter__()
        return self


class FaceSessionClient(FaceSessionClientGenerated):
    """FaceSessionClient.

    :param endpoint: Supported Cognitive Services endpoints (protocol and hostname, for example:
     https://{resource-name}.cognitiveservices.azure.com). Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: API Version. Default value is "v1.1-preview.1". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str or ~azure.ai.vision.face.models.Versions
    """

    @overload
    async def create_liveness_with_verify_session(
        self,
        body: _models.CreateLivenessSessionContent,
        *,
        verify_image: Union[bytes, None],
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.CreateLivenessWithVerifySessionResult: ...

    @overload
    async def create_liveness_with_verify_session(
        self,
        body: JSON,
        *,
        verify_image: Union[bytes, None],
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.CreateLivenessWithVerifySessionResult: ...

    @overload
    async def create_liveness_with_verify_session(
        self,
        body: IO[bytes],
        *,
        verify_image: Union[bytes, None],
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.CreateLivenessWithVerifySessionResult: ...

    @distributed_trace_async
    async def create_liveness_with_verify_session(
        self,
        body: Union[_models.CreateLivenessSessionContent, JSON, IO[bytes]],
        *,
        verify_image: Union[bytes, None],
        **kwargs: Any,
    ) -> _models.CreateLivenessWithVerifySessionResult:
        # pylint: disable=line-too-long
        """Create a new liveness session with verify. Client device submits VerifyImage during the
        /detectLivenessWithVerify/singleModal call.

        A session is best for client device scenarios where developers want to authorize a client
        device to perform only a liveness detection without granting full access to their resource.
        Created sessions have a limited life span and only authorize clients to perform the desired
        action before access is expired.

        Permissions includes...
        >
        *


        * Ability to call /detectLivenessWithVerify/singleModal for up to 3 retries.
        * A token lifetime of 10 minutes.

        ..

           [!NOTE]

           *


           * Client access can be revoked by deleting the session using the Delete Liveness With Verify
        Session operation.
           * To retrieve a result, use the Get Liveness With Verify Session.
           * To audit the individual requests that a client has made to your resource, use the List
        Liveness With Verify Session Audit Entries.


        Alternative Option: Client device submits VerifyImage during the
        /detectLivenessWithVerify/singleModal call.

        ..

           [!NOTE]
           Extra measures should be taken to validate that the client is sending the expected
        VerifyImage.

        :param body: Is one of the following types: CreateLivenessSessionContent, JSON, IO[bytes]
         Required.
        :type body: ~azure.ai.vision.face.models.CreateLivenessSessionContent or JSON or IO[bytes]
        :keyword verify_image: The image for verify. If you don't have any images to use for verification,
         set it to None. Required.
        :paramtype verify_image: bytes or None
        :return: CreateLivenessWithVerifySessionResult. The CreateLivenessWithVerifySessionResult is
         compatible with MutableMapping
        :rtype: ~azure.ai.vision.face.models.CreateLivenessWithVerifySessionResult
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "livenessOperationMode": "str",  # Type of liveness mode the client should
                      follow. Required. "Passive"
                    "authTokenTimeToLiveInSeconds": 0,  # Optional. Seconds the session should
                      last for. Range is 60 to 86400 seconds. Default value is 600.
                    "deviceCorrelationId": "str",  # Optional. Unique Guid per each end-user
                      device. This is to provide rate limiting and anti-hammering. If
                      'deviceCorrelationIdSetInClient' is true in this request, this
                      'deviceCorrelationId' must be null.
                    "deviceCorrelationIdSetInClient": bool,  # Optional. Whether or not to allow
                      client to set their own 'deviceCorrelationId' via the Vision SDK. Default is
                      false, and 'deviceCorrelationId' must be set in this request body.
                    "sendResultsToClient": bool  # Optional. Whether or not to allow a '200 -
                      Success' response body to be sent to the client, which may be undesirable for
                      security reasons. Default is false, clients will receive a '204 - NoContent'
                      empty body response. Regardless of selection, calling Session GetResult will
                      always contain a response body enabling business logic to be implemented.
                }

                # response body for status code(s): 200
                response == {
                    "authToken": "str",  # Bearer token to provide authentication for the Vision
                      SDK running on a client application. This Bearer token has limited permissions to
                      perform only the required action and expires after the TTL time. It is also
                      auditable. Required.
                    "sessionId": "str"  # The unique session ID of the created session. It will
                      expire 48 hours after it was created or may be deleted sooner using the
                      corresponding Session DELETE operation. Required.
                }
        """
        if verify_image is not None:
            request_body = _models._models.CreateLivenessWithVerifySessionContent(  # pylint: disable=protected-access
                parameters=body,
                verify_image=("verify-image", verify_image),
            )
            return await super()._create_liveness_with_verify_session_with_verify_image(request_body, **kwargs)

        return await super()._create_liveness_with_verify_session(body, **kwargs)

    async def __aenter__(self) -> "FaceSessionClient":
        await super().__aenter__()
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

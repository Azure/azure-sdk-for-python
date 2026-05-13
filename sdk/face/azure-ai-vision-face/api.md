```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.vision.face

    class azure.ai.vision.face.FaceAdministrationClient: implements ContextManager 
        large_face_list: LargeFaceListOperations
        large_person_group: LargePersonGroupOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Union[str, Versions] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.ai.vision.face.FaceClient(FaceClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Union[str, Versions] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def detect(
                self, 
                image_content: bytes, 
                *, 
                detection_model: Union[str, FaceDetectionModel], 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Union[str, FaceRecognitionModel], 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: bool, 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        def detect_from_url(
                self, 
                *, 
                content_type: str = "application/json", 
                detection_model: Union[str, FaceDetectionModel], 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Union[str, FaceRecognitionModel], 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: bool, 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                url: str, 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        def detect_from_url(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                detection_model: Union[str, FaceDetectionModel], 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Union[str, FaceRecognitionModel], 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: bool, 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        def detect_from_url(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                detection_model: Union[str, FaceDetectionModel], 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Union[str, FaceRecognitionModel], 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: bool, 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        def find_similar(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        def find_similar(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id: str, 
                face_ids: List[str], 
                max_num_of_candidates_returned: Optional[int] = ..., 
                mode: Optional[Union[str, FindSimilarMatchMode]] = ..., 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        def find_similar(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        def find_similar_from_large_face_list(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        def find_similar_from_large_face_list(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id: str, 
                large_face_list_id: str, 
                max_num_of_candidates_returned: Optional[int] = ..., 
                mode: Optional[Union[str, FindSimilarMatchMode]] = ..., 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        def find_similar_from_large_face_list(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        def group(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceGroupingResult: ...

        @overload
        def group(
                self, 
                *, 
                content_type: str = "application/json", 
                face_ids: List[str], 
                **kwargs: Any
            ) -> FaceGroupingResult: ...

        @overload
        def group(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceGroupingResult: ...

        @overload
        def identify_from_large_person_group(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceIdentificationResult]: ...

        @overload
        def identify_from_large_person_group(
                self, 
                *, 
                confidence_threshold: Optional[float] = ..., 
                content_type: str = "application/json", 
                face_ids: List[str], 
                large_person_group_id: str, 
                max_num_of_candidates_returned: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[FaceIdentificationResult]: ...

        @overload
        def identify_from_large_person_group(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceIdentificationResult]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @overload
        def verify_face_to_face(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        def verify_face_to_face(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id1: str, 
                face_id2: str, 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        def verify_face_to_face(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        def verify_from_large_person_group(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        def verify_from_large_person_group(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id: str, 
                large_person_group_id: str, 
                person_id: str, 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        def verify_from_large_person_group(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...


    class azure.ai.vision.face.FaceSessionClient(FaceSessionClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Union[str, Versions] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @overload
        def create_liveness_session(
                self, 
                body: CreateLivenessSessionContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateLivenessSessionResult: ...

        @overload
        def create_liveness_session(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateLivenessSessionResult: ...

        @overload
        def create_liveness_session(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateLivenessSessionResult: ...

        @overload
        def create_liveness_with_verify_session(
                self, 
                body: CreateLivenessWithVerifySessionContent, 
                *, 
                content_type: str = "application/json", 
                verify_image: Union[bytes, None], 
                **kwargs: Any
            ) -> CreateLivenessWithVerifySessionResult: ...

        @overload
        def create_liveness_with_verify_session(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                verify_image: Union[bytes, None], 
                **kwargs: Any
            ) -> CreateLivenessWithVerifySessionResult: ...

        @distributed_trace
        def delete_liveness_session(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_liveness_with_verify_session(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def detect_from_session_image(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: Optional[bool] = ..., 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        def detect_from_session_image(
                self, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: Optional[bool] = ..., 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                session_image_id: str, 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        def detect_from_session_image(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: Optional[bool] = ..., 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @distributed_trace
        def get_liveness_session_audit_entries(
                self, 
                session_id: str, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionAuditEntry]: ...

        @distributed_trace
        def get_liveness_session_result(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> LivenessSession: ...

        @distributed_trace
        def get_liveness_sessions(
                self, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionItem]: ...

        @distributed_trace
        def get_liveness_with_verify_session_audit_entries(
                self, 
                session_id: str, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionAuditEntry]: ...

        @distributed_trace
        def get_liveness_with_verify_session_result(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> LivenessWithVerifySession: ...

        @distributed_trace
        def get_liveness_with_verify_sessions(
                self, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionItem]: ...

        @distributed_trace
        @api_version_validation(method_added_on='v1.2-preview.1', params_added_on={'v1.2-preview.1': ['session_image_id', 'accept']})
        def get_session_image(
                self, 
                session_image_id: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.ai.vision.face.aio

    class azure.ai.vision.face.aio.FaceAdministrationClient: implements AsyncContextManager 
        large_face_list: LargeFaceListOperations
        large_person_group: LargePersonGroupOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Union[str, Versions] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.ai.vision.face.aio.FaceClient(FaceClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Union[str, Versions] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def detect(
                self, 
                image_content: bytes, 
                *, 
                detection_model: Union[str, FaceDetectionModel], 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Union[str, FaceRecognitionModel], 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: bool, 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        async def detect_from_url(
                self, 
                *, 
                content_type: str = "application/json", 
                detection_model: Union[str, FaceDetectionModel], 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Union[str, FaceRecognitionModel], 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: bool, 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                url: str, 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        async def detect_from_url(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                detection_model: Union[str, FaceDetectionModel], 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Union[str, FaceRecognitionModel], 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: bool, 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        async def detect_from_url(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                detection_model: Union[str, FaceDetectionModel], 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Union[str, FaceRecognitionModel], 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: bool, 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        async def find_similar(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        async def find_similar(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id: str, 
                face_ids: List[str], 
                max_num_of_candidates_returned: Optional[int] = ..., 
                mode: Optional[Union[str, FindSimilarMatchMode]] = ..., 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        async def find_similar(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        async def find_similar_from_large_face_list(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        async def find_similar_from_large_face_list(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id: str, 
                large_face_list_id: str, 
                max_num_of_candidates_returned: Optional[int] = ..., 
                mode: Optional[Union[str, FindSimilarMatchMode]] = ..., 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        async def find_similar_from_large_face_list(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        async def group(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceGroupingResult: ...

        @overload
        async def group(
                self, 
                *, 
                content_type: str = "application/json", 
                face_ids: List[str], 
                **kwargs: Any
            ) -> FaceGroupingResult: ...

        @overload
        async def group(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceGroupingResult: ...

        @overload
        async def identify_from_large_person_group(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceIdentificationResult]: ...

        @overload
        async def identify_from_large_person_group(
                self, 
                *, 
                confidence_threshold: Optional[float] = ..., 
                content_type: str = "application/json", 
                face_ids: List[str], 
                large_person_group_id: str, 
                max_num_of_candidates_returned: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[FaceIdentificationResult]: ...

        @overload
        async def identify_from_large_person_group(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceIdentificationResult]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @overload
        async def verify_face_to_face(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        async def verify_face_to_face(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id1: str, 
                face_id2: str, 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        async def verify_face_to_face(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        async def verify_from_large_person_group(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        async def verify_from_large_person_group(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id: str, 
                large_person_group_id: str, 
                person_id: str, 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        async def verify_from_large_person_group(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...


    class azure.ai.vision.face.aio.FaceSessionClient(FaceSessionClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Union[str, Versions] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @overload
        async def create_liveness_session(
                self, 
                body: CreateLivenessSessionContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateLivenessSessionResult: ...

        @overload
        async def create_liveness_session(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateLivenessSessionResult: ...

        @overload
        async def create_liveness_session(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateLivenessSessionResult: ...

        @overload
        async def create_liveness_with_verify_session(
                self, 
                body: CreateLivenessSessionContent, 
                *, 
                content_type: str = "application/json", 
                verify_image: Union[bytes, None], 
                **kwargs: Any
            ) -> CreateLivenessWithVerifySessionResult: ...

        @overload
        async def create_liveness_with_verify_session(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                verify_image: Union[bytes, None], 
                **kwargs: Any
            ) -> CreateLivenessWithVerifySessionResult: ...

        @distributed_trace_async
        async def delete_liveness_session(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_liveness_with_verify_session(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def detect_from_session_image(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: Optional[bool] = ..., 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        async def detect_from_session_image(
                self, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: Optional[bool] = ..., 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                session_image_id: str, 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        async def detect_from_session_image(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: Optional[bool] = ..., 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @distributed_trace_async
        async def get_liveness_session_audit_entries(
                self, 
                session_id: str, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionAuditEntry]: ...

        @distributed_trace_async
        async def get_liveness_session_result(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> LivenessSession: ...

        @distributed_trace_async
        async def get_liveness_sessions(
                self, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionItem]: ...

        @distributed_trace_async
        async def get_liveness_with_verify_session_audit_entries(
                self, 
                session_id: str, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionAuditEntry]: ...

        @distributed_trace_async
        async def get_liveness_with_verify_session_result(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> LivenessWithVerifySession: ...

        @distributed_trace_async
        async def get_liveness_with_verify_sessions(
                self, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionItem]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='v1.2-preview.1', params_added_on={'v1.2-preview.1': ['session_image_id', 'accept']})
        async def get_session_image(
                self, 
                session_image_id: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.ai.vision.face.aio.operations

    class azure.ai.vision.face.aio.operations.FaceClientOperationsMixin(FaceClientMixinABC):

        @overload
        async def find_similar(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        async def find_similar(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id: str, 
                face_ids: List[str], 
                max_num_of_candidates_returned: Optional[int] = ..., 
                mode: Optional[Union[str, FindSimilarMatchMode]] = ..., 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        async def find_similar(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        async def find_similar_from_large_face_list(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        async def find_similar_from_large_face_list(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id: str, 
                large_face_list_id: str, 
                max_num_of_candidates_returned: Optional[int] = ..., 
                mode: Optional[Union[str, FindSimilarMatchMode]] = ..., 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        async def find_similar_from_large_face_list(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        async def group(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceGroupingResult: ...

        @overload
        async def group(
                self, 
                *, 
                content_type: str = "application/json", 
                face_ids: List[str], 
                **kwargs: Any
            ) -> FaceGroupingResult: ...

        @overload
        async def group(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceGroupingResult: ...

        @overload
        async def identify_from_large_person_group(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceIdentificationResult]: ...

        @overload
        async def identify_from_large_person_group(
                self, 
                *, 
                confidence_threshold: Optional[float] = ..., 
                content_type: str = "application/json", 
                face_ids: List[str], 
                large_person_group_id: str, 
                max_num_of_candidates_returned: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[FaceIdentificationResult]: ...

        @overload
        async def identify_from_large_person_group(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceIdentificationResult]: ...

        @overload
        async def verify_face_to_face(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        async def verify_face_to_face(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id1: str, 
                face_id2: str, 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        async def verify_face_to_face(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        async def verify_from_large_person_group(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        async def verify_from_large_person_group(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id: str, 
                large_person_group_id: str, 
                person_id: str, 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        async def verify_from_large_person_group(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...


    class azure.ai.vision.face.aio.operations.FaceSessionClientOperationsMixin(FaceSessionClientMixinABC):

        @overload
        async def create_liveness_session(
                self, 
                body: CreateLivenessSessionContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateLivenessSessionResult: ...

        @overload
        async def create_liveness_session(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateLivenessSessionResult: ...

        @overload
        async def create_liveness_session(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateLivenessSessionResult: ...

        @distributed_trace_async
        async def delete_liveness_session(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_liveness_with_verify_session(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def detect_from_session_image(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: Optional[bool] = ..., 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        async def detect_from_session_image(
                self, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: Optional[bool] = ..., 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                session_image_id: str, 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        async def detect_from_session_image(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: Optional[bool] = ..., 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @distributed_trace_async
        async def get_liveness_session_audit_entries(
                self, 
                session_id: str, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionAuditEntry]: ...

        @distributed_trace_async
        async def get_liveness_session_result(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> LivenessSession: ...

        @distributed_trace_async
        async def get_liveness_sessions(
                self, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionItem]: ...

        @distributed_trace_async
        async def get_liveness_with_verify_session_audit_entries(
                self, 
                session_id: str, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionAuditEntry]: ...

        @distributed_trace_async
        async def get_liveness_with_verify_session_result(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> LivenessWithVerifySession: ...

        @distributed_trace_async
        async def get_liveness_with_verify_sessions(
                self, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionItem]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='v1.2-preview.1', params_added_on={'v1.2-preview.1': ['session_image_id', 'accept']})
        async def get_session_image(
                self, 
                session_image_id: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...


    class azure.ai.vision.face.aio.operations.LargeFaceListOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def add_face(
                self, 
                large_face_list_id: str, 
                image_content: bytes, 
                *, 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @overload
        async def add_face_from_url(
                self, 
                large_face_list_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @overload
        async def add_face_from_url(
                self, 
                large_face_list_id: str, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                url: str, 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @overload
        async def add_face_from_url(
                self, 
                large_face_list_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @distributed_trace_async
        async def begin_train(
                self, 
                large_face_list_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create(
                self, 
                large_face_list_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create(
                self, 
                large_face_list_id: str, 
                *, 
                content_type: str = "application/json", 
                name: str, 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create(
                self, 
                large_face_list_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                large_face_list_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_face(
                self, 
                large_face_list_id: str, 
                persisted_face_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                large_face_list_id: str, 
                *, 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LargeFaceList: ...

        @distributed_trace_async
        async def get_face(
                self, 
                large_face_list_id: str, 
                persisted_face_id: str, 
                **kwargs: Any
            ) -> LargeFaceListFace: ...

        @distributed_trace_async
        async def get_faces(
                self, 
                large_face_list_id: str, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LargeFaceListFace]: ...

        @distributed_trace_async
        async def get_large_face_lists(
                self, 
                *, 
                return_recognition_model: Optional[bool] = ..., 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LargeFaceList]: ...

        @distributed_trace_async
        async def get_training_status(
                self, 
                large_face_list_id: str, 
                **kwargs: Any
            ) -> FaceTrainingResult: ...

        @overload
        async def update(
                self, 
                large_face_list_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                large_face_list_id: str, 
                *, 
                content_type: str = "application/json", 
                name: Optional[str] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                large_face_list_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_face(
                self, 
                large_face_list_id: str, 
                persisted_face_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_face(
                self, 
                large_face_list_id: str, 
                persisted_face_id: str, 
                *, 
                content_type: str = "application/json", 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_face(
                self, 
                large_face_list_id: str, 
                persisted_face_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.vision.face.aio.operations.LargePersonGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def add_face(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                image_content: bytes, 
                *, 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @overload
        async def add_face_from_url(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @overload
        async def add_face_from_url(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                url: str, 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @overload
        async def add_face_from_url(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @distributed_trace_async
        async def begin_train(
                self, 
                large_person_group_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create(
                self, 
                large_person_group_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create(
                self, 
                large_person_group_id: str, 
                *, 
                content_type: str = "application/json", 
                name: str, 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create(
                self, 
                large_person_group_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create_person(
                self, 
                large_person_group_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreatePersonResult: ...

        @overload
        async def create_person(
                self, 
                large_person_group_id: str, 
                *, 
                content_type: str = "application/json", 
                name: str, 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> CreatePersonResult: ...

        @overload
        async def create_person(
                self, 
                large_person_group_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreatePersonResult: ...

        @distributed_trace_async
        async def delete(
                self, 
                large_person_group_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_face(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                persisted_face_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_person(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                large_person_group_id: str, 
                *, 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LargePersonGroup: ...

        @distributed_trace_async
        async def get_face(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                persisted_face_id: str, 
                **kwargs: Any
            ) -> LargePersonGroupPersonFace: ...

        @distributed_trace_async
        async def get_large_person_groups(
                self, 
                *, 
                return_recognition_model: Optional[bool] = ..., 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LargePersonGroup]: ...

        @distributed_trace_async
        async def get_person(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                **kwargs: Any
            ) -> LargePersonGroupPerson: ...

        @distributed_trace_async
        async def get_persons(
                self, 
                large_person_group_id: str, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LargePersonGroupPerson]: ...

        @distributed_trace_async
        async def get_training_status(
                self, 
                large_person_group_id: str, 
                **kwargs: Any
            ) -> FaceTrainingResult: ...

        @overload
        async def update(
                self, 
                large_person_group_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                large_person_group_id: str, 
                *, 
                content_type: str = "application/json", 
                name: Optional[str] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                large_person_group_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_face(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                persisted_face_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_face(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                persisted_face_id: str, 
                *, 
                content_type: str = "application/json", 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_face(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                persisted_face_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_person(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_person(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                *, 
                content_type: str = "application/json", 
                name: Optional[str] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_person(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.ai.vision.face.models

    class azure.ai.vision.face.models.AccessoryItem(Model):
        confidence: float
        type: Union[str, AccessoryType]

        @overload
        def __init__(
                self, 
                *, 
                confidence: float, 
                type: Union[str, AccessoryType]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.AccessoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLASSES = "glasses"
        HEADWEAR = "headwear"
        MASK = "mask"


    class azure.ai.vision.face.models.AddFaceResult(Model):
        persisted_face_id: str

        @overload
        def __init__(
                self, 
                *, 
                persisted_face_id: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.AuditLivenessResponseInfo(Model):
        body: LivenessResponseBody
        latency_in_milliseconds: int
        status_code: int

        @overload
        def __init__(
                self, 
                *, 
                body: LivenessResponseBody, 
                latency_in_milliseconds: int, 
                status_code: int
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.AuditRequestInfo(Model):
        content_length: Optional[int]
        content_type: str
        method: str
        url: str
        user_agent: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content_length: Optional[int] = ..., 
                content_type: str, 
                method: str, 
                url: str, 
                user_agent: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.BlurLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.ai.vision.face.models.BlurProperties(Model):
        blur_level: Union[str, BlurLevel]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                blur_level: Union[str, BlurLevel], 
                value: float
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.CreateLivenessSessionContent(Model):
        auth_token_time_to_live_in_seconds: Optional[int]
        device_correlation_id: Optional[str]
        device_correlation_id_set_in_client: Optional[bool]
        enable_session_image: Optional[bool]
        liveness_operation_mode: Union[str, LivenessOperationMode]
        liveness_single_modal_model: Optional[Union[str, LivenessModel]]
        send_results_to_client: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                auth_token_time_to_live_in_seconds: Optional[int] = ..., 
                device_correlation_id: Optional[str] = ..., 
                device_correlation_id_set_in_client: Optional[bool] = ..., 
                enable_session_image: Optional[bool] = ..., 
                liveness_operation_mode: Union[str, LivenessOperationMode], 
                liveness_single_modal_model: Optional[Union[str, LivenessModel]] = ..., 
                send_results_to_client: Optional[bool] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.CreateLivenessSessionResult(Model):
        auth_token: str
        session_id: str

        @overload
        def __init__(
                self, 
                *, 
                auth_token: str, 
                session_id: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.CreateLivenessWithVerifySessionContent(Model):
        auth_token_time_to_live_in_seconds: Optional[int]
        device_correlation_id: Optional[str]
        device_correlation_id_set_in_client: Optional[bool]
        enable_session_image: Optional[bool]
        liveness_operation_mode: Union[str, LivenessOperationMode]
        liveness_single_modal_model: Optional[Union[str, LivenessModel]]
        return_verify_image_hash: Optional[bool]
        send_results_to_client: Optional[bool]
        verify_confidence_threshold: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                auth_token_time_to_live_in_seconds: Optional[int] = ..., 
                device_correlation_id: Optional[str] = ..., 
                device_correlation_id_set_in_client: Optional[bool] = ..., 
                enable_session_image: Optional[bool] = ..., 
                liveness_operation_mode: Union[str, LivenessOperationMode], 
                liveness_single_modal_model: Optional[Union[str, LivenessModel]] = ..., 
                return_verify_image_hash: Optional[bool] = ..., 
                send_results_to_client: Optional[bool] = ..., 
                verify_confidence_threshold: Optional[float] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.CreateLivenessWithVerifySessionMultipartContent(Model):
        parameters: CreateLivenessWithVerifySessionContent
        verify_image: Union[str, bytes, IO[str], IO[bytes], Tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], Tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]

        @overload
        def __init__(
                self, 
                *, 
                parameters: CreateLivenessWithVerifySessionContent, 
                verify_image: FileType
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.CreateLivenessWithVerifySessionResult(Model):
        auth_token: str
        session_id: str
        verify_image: Optional[LivenessWithVerifyImage]

        @overload
        def __init__(
                self, 
                *, 
                auth_token: str, 
                session_id: str, 
                verify_image: Optional[LivenessWithVerifyImage] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.CreatePersonResult(Model):
        person_id: str

        @overload
        def __init__(
                self, 
                *, 
                person_id: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.ExposureLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GOOD_EXPOSURE = "goodExposure"
        OVER_EXPOSURE = "overExposure"
        UNDER_EXPOSURE = "underExposure"


    class azure.ai.vision.face.models.ExposureProperties(Model):
        exposure_level: Union[str, ExposureLevel]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                exposure_level: Union[str, ExposureLevel], 
                value: float
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.FaceAttributeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESSORIES = "accessories"
        AGE = "age"
        BLUR = "blur"
        EXPOSURE = "exposure"
        FACIAL_HAIR = "facialHair"
        GLASSES = "glasses"
        HAIR = "hair"
        HEAD_POSE = "headPose"
        MASK = "mask"
        NOISE = "noise"
        OCCLUSION = "occlusion"
        QUALITY_FOR_RECOGNITION = "qualityForRecognition"
        SMILE = "smile"


    class azure.ai.vision.face.models.FaceAttributeTypeDetection01(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESSORIES = "accessories"
        BLUR = "blur"
        EXPOSURE = "exposure"
        GLASSES = "glasses"
        HEAD_POSE = "headPose"
        NOISE = "noise"
        OCCLUSION = "occlusion"


    class azure.ai.vision.face.models.FaceAttributeTypeDetection03(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLUR = "blur"
        HEAD_POSE = "headPose"
        MASK = "mask"


    class azure.ai.vision.face.models.FaceAttributeTypeRecognition03(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        QUALITY_FOR_RECOGNITION = "qualityForRecognition"


    class azure.ai.vision.face.models.FaceAttributeTypeRecognition04(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        QUALITY_FOR_RECOGNITION = "qualityForRecognition"


    class azure.ai.vision.face.models.FaceAttributes(Model):
        accessories: Optional[List[AccessoryItem]]
        age: Optional[float]
        blur: Optional[BlurProperties]
        exposure: Optional[ExposureProperties]
        facial_hair: Optional[FacialHair]
        glasses: Optional[Union[str, GlassesType]]
        hair: Optional[HairProperties]
        head_pose: Optional[HeadPose]
        mask: Optional[MaskProperties]
        noise: Optional[NoiseProperties]
        occlusion: Optional[OcclusionProperties]
        quality_for_recognition: Optional[Union[str, QualityForRecognition]]
        smile: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                accessories: Optional[List[AccessoryItem]] = ..., 
                age: Optional[float] = ..., 
                blur: Optional[BlurProperties] = ..., 
                exposure: Optional[ExposureProperties] = ..., 
                facial_hair: Optional[FacialHair] = ..., 
                glasses: Optional[Union[str, GlassesType]] = ..., 
                hair: Optional[HairProperties] = ..., 
                head_pose: Optional[HeadPose] = ..., 
                mask: Optional[MaskProperties] = ..., 
                noise: Optional[NoiseProperties] = ..., 
                occlusion: Optional[OcclusionProperties] = ..., 
                quality_for_recognition: Optional[Union[str, QualityForRecognition]] = ..., 
                smile: Optional[float] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.FaceDetectionModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DETECTION01 = "detection_01"
        DETECTION02 = "detection_02"
        DETECTION03 = "detection_03"


    class azure.ai.vision.face.models.FaceDetectionResult(Model):
        face_attributes: Optional[FaceAttributes]
        face_id: Optional[str]
        face_landmarks: Optional[FaceLandmarks]
        face_rectangle: FaceRectangle
        recognition_model: Optional[Union[str, FaceRecognitionModel]]

        @overload
        def __init__(
                self, 
                *, 
                face_attributes: Optional[FaceAttributes] = ..., 
                face_id: Optional[str] = ..., 
                face_landmarks: Optional[FaceLandmarks] = ..., 
                face_rectangle: FaceRectangle, 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.FaceError(Model):
        code: str
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                message: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.FaceErrorResponse(Model):
        error: FaceError

        @overload
        def __init__(
                self, 
                *, 
                error: FaceError
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.FaceFindSimilarResult(Model):
        confidence: float
        face_id: Optional[str]
        persisted_face_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                confidence: float, 
                face_id: Optional[str] = ..., 
                persisted_face_id: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.FaceGroupingResult(Model):
        groups: List[List[str]]
        messy_group: List[str]

        @overload
        def __init__(
                self, 
                *, 
                groups: List[List[str]], 
                messy_group: List[str]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.FaceIdentificationCandidate(Model):
        confidence: float
        person_id: str

        @overload
        def __init__(
                self, 
                *, 
                confidence: float, 
                person_id: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.FaceIdentificationResult(Model):
        candidates: List[FaceIdentificationCandidate]
        face_id: str

        @overload
        def __init__(
                self, 
                *, 
                candidates: List[FaceIdentificationCandidate], 
                face_id: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.FaceImageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLOR = "Color"
        DEPTH = "Depth"
        INFRARED = "Infrared"


    class azure.ai.vision.face.models.FaceLandmarks(Model):
        eye_left_bottom: LandmarkCoordinate
        eye_left_inner: LandmarkCoordinate
        eye_left_outer: LandmarkCoordinate
        eye_left_top: LandmarkCoordinate
        eye_right_bottom: LandmarkCoordinate
        eye_right_inner: LandmarkCoordinate
        eye_right_outer: LandmarkCoordinate
        eye_right_top: LandmarkCoordinate
        eyebrow_left_inner: LandmarkCoordinate
        eyebrow_left_outer: LandmarkCoordinate
        eyebrow_right_inner: LandmarkCoordinate
        eyebrow_right_outer: LandmarkCoordinate
        mouth_left: LandmarkCoordinate
        mouth_right: LandmarkCoordinate
        nose_left_alar_out_tip: LandmarkCoordinate
        nose_left_alar_top: LandmarkCoordinate
        nose_right_alar_out_tip: LandmarkCoordinate
        nose_right_alar_top: LandmarkCoordinate
        nose_root_left: LandmarkCoordinate
        nose_root_right: LandmarkCoordinate
        nose_tip: LandmarkCoordinate
        pupil_left: LandmarkCoordinate
        pupil_right: LandmarkCoordinate
        under_lip_bottom: LandmarkCoordinate
        under_lip_top: LandmarkCoordinate
        upper_lip_bottom: LandmarkCoordinate
        upper_lip_top: LandmarkCoordinate

        @overload
        def __init__(
                self, 
                *, 
                eye_left_bottom: LandmarkCoordinate, 
                eye_left_inner: LandmarkCoordinate, 
                eye_left_outer: LandmarkCoordinate, 
                eye_left_top: LandmarkCoordinate, 
                eye_right_bottom: LandmarkCoordinate, 
                eye_right_inner: LandmarkCoordinate, 
                eye_right_outer: LandmarkCoordinate, 
                eye_right_top: LandmarkCoordinate, 
                eyebrow_left_inner: LandmarkCoordinate, 
                eyebrow_left_outer: LandmarkCoordinate, 
                eyebrow_right_inner: LandmarkCoordinate, 
                eyebrow_right_outer: LandmarkCoordinate, 
                mouth_left: LandmarkCoordinate, 
                mouth_right: LandmarkCoordinate, 
                nose_left_alar_out_tip: LandmarkCoordinate, 
                nose_left_alar_top: LandmarkCoordinate, 
                nose_right_alar_out_tip: LandmarkCoordinate, 
                nose_right_alar_top: LandmarkCoordinate, 
                nose_root_left: LandmarkCoordinate, 
                nose_root_right: LandmarkCoordinate, 
                nose_tip: LandmarkCoordinate, 
                pupil_left: LandmarkCoordinate, 
                pupil_right: LandmarkCoordinate, 
                under_lip_bottom: LandmarkCoordinate, 
                under_lip_top: LandmarkCoordinate, 
                upper_lip_bottom: LandmarkCoordinate, 
                upper_lip_top: LandmarkCoordinate
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.FaceLivenessDecision(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REAL_FACE = "realface"
        SPOOF_FACE = "spoofface"
        UNCERTAIN = "uncertain"


    class azure.ai.vision.face.models.FaceOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "failed"
        NOT_STARTED = "notStarted"
        RUNNING = "running"
        SUCCEEDED = "succeeded"


    class azure.ai.vision.face.models.FaceRecognitionModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RECOGNITION01 = "recognition_01"
        RECOGNITION02 = "recognition_02"
        RECOGNITION03 = "recognition_03"
        RECOGNITION04 = "recognition_04"


    class azure.ai.vision.face.models.FaceRectangle(Model):
        height: int
        left: int
        top: int
        width: int

        @overload
        def __init__(
                self, 
                *, 
                height: int, 
                left: int, 
                top: int, 
                width: int
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.FaceSessionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_STARTED = "NotStarted"
        RESULT_AVAILABLE = "ResultAvailable"
        STARTED = "Started"


    class azure.ai.vision.face.models.FaceTrainingResult(Model):
        created_date_time: datetime
        last_action_date_time: datetime
        last_successful_training_date_time: datetime
        message: Optional[str]
        status: Union[str, FaceOperationStatus]

        @overload
        def __init__(
                self, 
                *, 
                created_date_time: datetime, 
                last_action_date_time: datetime, 
                last_successful_training_date_time: datetime, 
                message: Optional[str] = ..., 
                status: Union[str, FaceOperationStatus]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.FaceVerificationResult(Model):
        confidence: float
        is_identical: bool

        @overload
        def __init__(
                self, 
                *, 
                confidence: float, 
                is_identical: bool
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.FacialHair(Model):
        beard: float
        moustache: float
        sideburns: float

        @overload
        def __init__(
                self, 
                *, 
                beard: float, 
                moustache: float, 
                sideburns: float
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.FindSimilarMatchMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MATCH_FACE = "matchFace"
        MATCH_PERSON = "matchPerson"


    class azure.ai.vision.face.models.GlassesType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_GLASSES = "noGlasses"
        READING_GLASSES = "readingGlasses"
        SUNGLASSES = "sunglasses"
        SWIMMING_GOGGLES = "swimmingGoggles"


    class azure.ai.vision.face.models.HairColor(Model):
        color: Union[str, HairColorType]
        confidence: float

        @overload
        def __init__(
                self, 
                *, 
                color: Union[str, HairColorType], 
                confidence: float
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.HairColorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLACK = "black"
        BLOND = "blond"
        BROWN = "brown"
        GRAY = "gray"
        OTHER = "other"
        RED = "red"
        UNKNOWN_HAIR_COLOR = "unknown"
        WHITE = "white"


    class azure.ai.vision.face.models.HairProperties(Model):
        bald: float
        hair_color: List[HairColor]
        invisible: bool

        @overload
        def __init__(
                self, 
                *, 
                bald: float, 
                hair_color: List[HairColor], 
                invisible: bool
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.HeadPose(Model):
        pitch: float
        roll: float
        yaw: float

        @overload
        def __init__(
                self, 
                *, 
                pitch: float, 
                roll: float, 
                yaw: float
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.LandmarkCoordinate(Model):
        x: float
        y: float

        @overload
        def __init__(
                self, 
                *, 
                x: float, 
                y: float
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.LargeFaceList(Model):
        large_face_list_id: str
        name: str
        recognition_model: Optional[Union[str, FaceRecognitionModel]]
        user_data: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                user_data: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.LargeFaceListFace(Model):
        persisted_face_id: str
        user_data: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                user_data: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.LargePersonGroup(Model):
        large_person_group_id: str
        name: str
        recognition_model: Optional[Union[str, FaceRecognitionModel]]
        user_data: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                user_data: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.LargePersonGroupPerson(Model):
        name: str
        persisted_face_ids: Optional[List[str]]
        person_id: str
        user_data: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                persisted_face_ids: Optional[List[str]] = ..., 
                user_data: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.LargePersonGroupPersonFace(Model):
        persisted_face_id: str
        user_data: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                user_data: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.LivenessModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2022_10_15_PREVIEW04 = "2022-10-15-preview.04"
        V2023_12_20_PREVIEW06 = "2023-12-20-preview.06"


    class azure.ai.vision.face.models.LivenessOperationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PASSIVE = "Passive"
        PASSIVE_ACTIVE = "PassiveActive"


    class azure.ai.vision.face.models.LivenessOutputsTarget(Model):
        face_rectangle: FaceRectangle
        file_name: str
        image_type: Union[str, FaceImageType]
        time_offset_within_file: int

        @overload
        def __init__(
                self, 
                *, 
                face_rectangle: FaceRectangle, 
                file_name: str, 
                image_type: Union[str, FaceImageType], 
                time_offset_within_file: int
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.LivenessResponseBody(Model):
        liveness_decision: Optional[Union[str, FaceLivenessDecision]]
        model_version_used: Optional[Union[str, LivenessModel]]
        target: Optional[LivenessOutputsTarget]
        verify_result: Optional[LivenessWithVerifyOutputs]

        @overload
        def __init__(
                self, 
                *, 
                liveness_decision: Optional[Union[str, FaceLivenessDecision]] = ..., 
                model_version_used: Optional[Union[str, LivenessModel]] = ..., 
                target: Optional[LivenessOutputsTarget] = ..., 
                verify_result: Optional[LivenessWithVerifyOutputs] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.LivenessSession(Model):
        auth_token_time_to_live_in_seconds: Optional[int]
        created_date_time: datetime
        device_correlation_id: Optional[str]
        id: str
        result: Optional[LivenessSessionAuditEntry]
        session_expired: bool
        session_start_date_time: Optional[datetime]
        status: Union[str, FaceSessionStatus]

        @overload
        def __init__(
                self, 
                *, 
                auth_token_time_to_live_in_seconds: Optional[int] = ..., 
                created_date_time: datetime, 
                device_correlation_id: Optional[str] = ..., 
                result: Optional[LivenessSessionAuditEntry] = ..., 
                session_expired: bool, 
                session_start_date_time: Optional[datetime] = ..., 
                status: Union[str, FaceSessionStatus]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.LivenessSessionAuditEntry(Model):
        client_request_id: str
        digest: str
        id: int
        received_date_time: datetime
        request: AuditRequestInfo
        request_id: str
        response: AuditLivenessResponseInfo
        session_id: str
        session_image_id: Optional[str]
        verify_image_hash: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_request_id: str, 
                digest: str, 
                id: int, 
                received_date_time: datetime, 
                request: AuditRequestInfo, 
                request_id: str, 
                response: AuditLivenessResponseInfo, 
                session_id: str, 
                session_image_id: Optional[str] = ..., 
                verify_image_hash: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.LivenessSessionItem(Model):
        auth_token_time_to_live_in_seconds: Optional[int]
        created_date_time: datetime
        device_correlation_id: Optional[str]
        id: str
        session_expired: bool
        session_start_date_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                auth_token_time_to_live_in_seconds: Optional[int] = ..., 
                created_date_time: datetime, 
                device_correlation_id: Optional[str] = ..., 
                session_expired: bool, 
                session_start_date_time: Optional[datetime] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.LivenessWithVerifyImage(Model):
        face_rectangle: FaceRectangle
        quality_for_recognition: Union[str, QualityForRecognition]

        @overload
        def __init__(
                self, 
                *, 
                face_rectangle: FaceRectangle, 
                quality_for_recognition: Union[str, QualityForRecognition]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.LivenessWithVerifyOutputs(Model):
        is_identical: bool
        match_confidence: float
        verify_image: LivenessWithVerifyImage

        @overload
        def __init__(
                self, 
                *, 
                is_identical: bool, 
                match_confidence: float, 
                verify_image: LivenessWithVerifyImage
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.LivenessWithVerifySession(Model):
        auth_token_time_to_live_in_seconds: Optional[int]
        created_date_time: datetime
        device_correlation_id: Optional[str]
        id: str
        result: Optional[LivenessSessionAuditEntry]
        session_expired: bool
        session_start_date_time: Optional[datetime]
        status: Union[str, FaceSessionStatus]

        @overload
        def __init__(
                self, 
                *, 
                auth_token_time_to_live_in_seconds: Optional[int] = ..., 
                created_date_time: datetime, 
                device_correlation_id: Optional[str] = ..., 
                result: Optional[LivenessSessionAuditEntry] = ..., 
                session_expired: bool, 
                session_start_date_time: Optional[datetime] = ..., 
                status: Union[str, FaceSessionStatus]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.MaskProperties(Model):
        nose_and_mouth_covered: bool
        type: Union[str, MaskType]

        @overload
        def __init__(
                self, 
                *, 
                nose_and_mouth_covered: bool, 
                type: Union[str, MaskType]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.MaskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FACE_MASK = "faceMask"
        NO_MASK = "noMask"
        OTHER_MASK_OR_OCCLUSION = "otherMaskOrOcclusion"
        UNCERTAIN = "uncertain"


    class azure.ai.vision.face.models.NoiseLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.ai.vision.face.models.NoiseProperties(Model):
        noise_level: Union[str, NoiseLevel]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                noise_level: Union[str, NoiseLevel], 
                value: float
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.OcclusionProperties(Model):
        eye_occluded: bool
        forehead_occluded: bool
        mouth_occluded: bool

        @overload
        def __init__(
                self, 
                *, 
                eye_occluded: bool, 
                forehead_occluded: bool, 
                mouth_occluded: bool
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.face.models.QualityForRecognition(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.ai.vision.face.models.Versions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V1_1_PREVIEW1 = "v1.1-preview.1"
        V1_2_PREVIEW1 = "v1.2-preview.1"


namespace azure.ai.vision.face.operations

    class azure.ai.vision.face.operations.FaceClientOperationsMixin(FaceClientMixinABC):

        @overload
        def find_similar(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        def find_similar(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id: str, 
                face_ids: List[str], 
                max_num_of_candidates_returned: Optional[int] = ..., 
                mode: Optional[Union[str, FindSimilarMatchMode]] = ..., 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        def find_similar(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        def find_similar_from_large_face_list(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        def find_similar_from_large_face_list(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id: str, 
                large_face_list_id: str, 
                max_num_of_candidates_returned: Optional[int] = ..., 
                mode: Optional[Union[str, FindSimilarMatchMode]] = ..., 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        def find_similar_from_large_face_list(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceFindSimilarResult]: ...

        @overload
        def group(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceGroupingResult: ...

        @overload
        def group(
                self, 
                *, 
                content_type: str = "application/json", 
                face_ids: List[str], 
                **kwargs: Any
            ) -> FaceGroupingResult: ...

        @overload
        def group(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceGroupingResult: ...

        @overload
        def identify_from_large_person_group(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceIdentificationResult]: ...

        @overload
        def identify_from_large_person_group(
                self, 
                *, 
                confidence_threshold: Optional[float] = ..., 
                content_type: str = "application/json", 
                face_ids: List[str], 
                large_person_group_id: str, 
                max_num_of_candidates_returned: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[FaceIdentificationResult]: ...

        @overload
        def identify_from_large_person_group(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[FaceIdentificationResult]: ...

        @overload
        def verify_face_to_face(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        def verify_face_to_face(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id1: str, 
                face_id2: str, 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        def verify_face_to_face(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        def verify_from_large_person_group(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        def verify_from_large_person_group(
                self, 
                *, 
                content_type: str = "application/json", 
                face_id: str, 
                large_person_group_id: str, 
                person_id: str, 
                **kwargs: Any
            ) -> FaceVerificationResult: ...

        @overload
        def verify_from_large_person_group(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaceVerificationResult: ...


    class azure.ai.vision.face.operations.FaceSessionClientOperationsMixin(FaceSessionClientMixinABC):

        @overload
        def create_liveness_session(
                self, 
                body: CreateLivenessSessionContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateLivenessSessionResult: ...

        @overload
        def create_liveness_session(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateLivenessSessionResult: ...

        @overload
        def create_liveness_session(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateLivenessSessionResult: ...

        @distributed_trace
        def delete_liveness_session(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_liveness_with_verify_session(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def detect_from_session_image(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: Optional[bool] = ..., 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        def detect_from_session_image(
                self, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: Optional[bool] = ..., 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                session_image_id: str, 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @overload
        def detect_from_session_image(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                face_id_time_to_live: Optional[int] = ..., 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                return_face_attributes: Optional[List[Union[str, FaceAttributeType]]] = ..., 
                return_face_id: Optional[bool] = ..., 
                return_face_landmarks: Optional[bool] = ..., 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[FaceDetectionResult]: ...

        @distributed_trace
        def get_liveness_session_audit_entries(
                self, 
                session_id: str, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionAuditEntry]: ...

        @distributed_trace
        def get_liveness_session_result(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> LivenessSession: ...

        @distributed_trace
        def get_liveness_sessions(
                self, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionItem]: ...

        @distributed_trace
        def get_liveness_with_verify_session_audit_entries(
                self, 
                session_id: str, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionAuditEntry]: ...

        @distributed_trace
        def get_liveness_with_verify_session_result(
                self, 
                session_id: str, 
                **kwargs: Any
            ) -> LivenessWithVerifySession: ...

        @distributed_trace
        def get_liveness_with_verify_sessions(
                self, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LivenessSessionItem]: ...

        @distributed_trace
        @api_version_validation(method_added_on='v1.2-preview.1', params_added_on={'v1.2-preview.1': ['session_image_id', 'accept']})
        def get_session_image(
                self, 
                session_image_id: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...


    class azure.ai.vision.face.operations.LargeFaceListOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def add_face(
                self, 
                large_face_list_id: str, 
                image_content: bytes, 
                *, 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @overload
        def add_face_from_url(
                self, 
                large_face_list_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @overload
        def add_face_from_url(
                self, 
                large_face_list_id: str, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                url: str, 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @overload
        def add_face_from_url(
                self, 
                large_face_list_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @distributed_trace
        def begin_train(
                self, 
                large_face_list_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create(
                self, 
                large_face_list_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create(
                self, 
                large_face_list_id: str, 
                *, 
                content_type: str = "application/json", 
                name: str, 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create(
                self, 
                large_face_list_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                large_face_list_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_face(
                self, 
                large_face_list_id: str, 
                persisted_face_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                large_face_list_id: str, 
                *, 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LargeFaceList: ...

        @distributed_trace
        def get_face(
                self, 
                large_face_list_id: str, 
                persisted_face_id: str, 
                **kwargs: Any
            ) -> LargeFaceListFace: ...

        @distributed_trace
        def get_faces(
                self, 
                large_face_list_id: str, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LargeFaceListFace]: ...

        @distributed_trace
        def get_large_face_lists(
                self, 
                *, 
                return_recognition_model: Optional[bool] = ..., 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LargeFaceList]: ...

        @distributed_trace
        def get_training_status(
                self, 
                large_face_list_id: str, 
                **kwargs: Any
            ) -> FaceTrainingResult: ...

        @overload
        def update(
                self, 
                large_face_list_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                large_face_list_id: str, 
                *, 
                content_type: str = "application/json", 
                name: Optional[str] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                large_face_list_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_face(
                self, 
                large_face_list_id: str, 
                persisted_face_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_face(
                self, 
                large_face_list_id: str, 
                persisted_face_id: str, 
                *, 
                content_type: str = "application/json", 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_face(
                self, 
                large_face_list_id: str, 
                persisted_face_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.vision.face.operations.LargePersonGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def add_face(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                image_content: bytes, 
                *, 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @overload
        def add_face_from_url(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @overload
        def add_face_from_url(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                url: str, 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @overload
        def add_face_from_url(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                detection_model: Optional[Union[str, FaceDetectionModel]] = ..., 
                target_face: Optional[List[int]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> AddFaceResult: ...

        @distributed_trace
        def begin_train(
                self, 
                large_person_group_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create(
                self, 
                large_person_group_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create(
                self, 
                large_person_group_id: str, 
                *, 
                content_type: str = "application/json", 
                name: str, 
                recognition_model: Optional[Union[str, FaceRecognitionModel]] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create(
                self, 
                large_person_group_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create_person(
                self, 
                large_person_group_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreatePersonResult: ...

        @overload
        def create_person(
                self, 
                large_person_group_id: str, 
                *, 
                content_type: str = "application/json", 
                name: str, 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> CreatePersonResult: ...

        @overload
        def create_person(
                self, 
                large_person_group_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreatePersonResult: ...

        @distributed_trace
        def delete(
                self, 
                large_person_group_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_face(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                persisted_face_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_person(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                large_person_group_id: str, 
                *, 
                return_recognition_model: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LargePersonGroup: ...

        @distributed_trace
        def get_face(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                persisted_face_id: str, 
                **kwargs: Any
            ) -> LargePersonGroupPersonFace: ...

        @distributed_trace
        def get_large_person_groups(
                self, 
                *, 
                return_recognition_model: Optional[bool] = ..., 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LargePersonGroup]: ...

        @distributed_trace
        def get_person(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                **kwargs: Any
            ) -> LargePersonGroupPerson: ...

        @distributed_trace
        def get_persons(
                self, 
                large_person_group_id: str, 
                *, 
                start: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[LargePersonGroupPerson]: ...

        @distributed_trace
        def get_training_status(
                self, 
                large_person_group_id: str, 
                **kwargs: Any
            ) -> FaceTrainingResult: ...

        @overload
        def update(
                self, 
                large_person_group_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                large_person_group_id: str, 
                *, 
                content_type: str = "application/json", 
                name: Optional[str] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                large_person_group_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_face(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                persisted_face_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_face(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                persisted_face_id: str, 
                *, 
                content_type: str = "application/json", 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_face(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                persisted_face_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_person(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_person(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                *, 
                content_type: str = "application/json", 
                name: Optional[str] = ..., 
                user_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_person(
                self, 
                large_person_group_id: str, 
                person_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


```
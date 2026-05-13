```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.health.deidentification

    class azure.health.deidentification.DeidentificationClient(DeidentificationClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def begin_deidentify_documents(
                self, 
                job_name: str, 
                resource: DeidentificationJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeidentificationJob]: ...

        @overload
        def begin_deidentify_documents(
                self, 
                job_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeidentificationJob]: ...

        @overload
        def begin_deidentify_documents(
                self, 
                job_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeidentificationJob]: ...

        @distributed_trace
        def cancel_job(
                self, 
                job_name: str, 
                **kwargs: Any
            ) -> DeidentificationJob: ...

        def close(self) -> None: ...

        @overload
        def deidentify_text(
                self, 
                body: DeidentificationContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeidentificationResult: ...

        @overload
        def deidentify_text(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeidentificationResult: ...

        @overload
        def deidentify_text(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeidentificationResult: ...

        @distributed_trace
        def delete_job(
                self, 
                job_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_job(
                self, 
                job_name: str, 
                **kwargs: Any
            ) -> DeidentificationJob: ...

        @distributed_trace
        def list_job_documents(
                self, 
                job_name: str, 
                **kwargs: Any
            ) -> Iterable[DeidentificationDocumentDetails]: ...

        @distributed_trace
        def list_jobs(self, **kwargs: Any) -> Iterable[DeidentificationJob]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.health.deidentification.aio

    class azure.health.deidentification.aio.DeidentificationClient(DeidentificationClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def begin_deidentify_documents(
                self, 
                job_name: str, 
                resource: DeidentificationJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeidentificationJob]: ...

        @overload
        async def begin_deidentify_documents(
                self, 
                job_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeidentificationJob]: ...

        @overload
        async def begin_deidentify_documents(
                self, 
                job_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeidentificationJob]: ...

        @distributed_trace_async
        async def cancel_job(
                self, 
                job_name: str, 
                **kwargs: Any
            ) -> DeidentificationJob: ...

        async def close(self) -> None: ...

        @overload
        async def deidentify_text(
                self, 
                body: DeidentificationContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeidentificationResult: ...

        @overload
        async def deidentify_text(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeidentificationResult: ...

        @overload
        async def deidentify_text(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeidentificationResult: ...

        @distributed_trace_async
        async def delete_job(
                self, 
                job_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_job(
                self, 
                job_name: str, 
                **kwargs: Any
            ) -> DeidentificationJob: ...

        @distributed_trace
        def list_job_documents(
                self, 
                job_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[DeidentificationDocumentDetails]: ...

        @distributed_trace
        def list_jobs(self, **kwargs: Any) -> AsyncIterable[DeidentificationJob]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.health.deidentification.models

    class azure.health.deidentification.models.DeidentificationContent(_Model):
        customizations: Optional[DeidentificationCustomizationOptions]
        input_text: str
        operation_type: Optional[Union[str, DeidentificationOperationType]]
        tagged_entities: Optional[TaggedPhiEntities]

        @overload
        def __init__(
                self, 
                *, 
                customizations: Optional[DeidentificationCustomizationOptions] = ..., 
                input_text: str, 
                operation_type: Optional[Union[str, DeidentificationOperationType]] = ..., 
                tagged_entities: Optional[TaggedPhiEntities] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.DeidentificationCustomizationOptions(_Model):
        input_locale: Optional[str]
        redaction_format: Optional[str]
        surrogate_locale: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                input_locale: Optional[str] = ..., 
                redaction_format: Optional[str] = ..., 
                surrogate_locale: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.DeidentificationDocumentDetails(_Model):
        error: Optional[ODataV4Format]
        id: str
        input_location: DeidentificationDocumentLocation
        output_location: Optional[DeidentificationDocumentLocation]
        status: Union[str, OperationStatus]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ODataV4Format] = ..., 
                input_location: DeidentificationDocumentLocation, 
                output_location: Optional[DeidentificationDocumentLocation] = ..., 
                status: Union[str, OperationStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.DeidentificationDocumentLocation(_Model):
        etag: str
        location: str

        @overload
        def __init__(
                self, 
                *, 
                location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.DeidentificationJob(_Model):
        created_at: datetime
        customizations: Optional[DeidentificationJobCustomizationOptions]
        error: Optional[ODataV4Format]
        job_name: str
        last_updated_at: datetime
        operation_type: Optional[Union[str, DeidentificationOperationType]]
        source_location: SourceStorageLocation
        started_at: Optional[datetime]
        status: Union[str, OperationStatus]
        summary: Optional[DeidentificationJobSummary]
        target_location: TargetStorageLocation

        @overload
        def __init__(
                self, 
                *, 
                customizations: Optional[DeidentificationJobCustomizationOptions] = ..., 
                operation_type: Optional[Union[str, DeidentificationOperationType]] = ..., 
                source_location: SourceStorageLocation, 
                target_location: TargetStorageLocation
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.DeidentificationJobCustomizationOptions(_Model):
        input_locale: Optional[str]
        redaction_format: Optional[str]
        surrogate_locale: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                input_locale: Optional[str] = ..., 
                redaction_format: Optional[str] = ..., 
                surrogate_locale: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.DeidentificationJobSummary(_Model):
        bytes_processed: int
        canceled_count: int
        failed_count: int
        successful_count: int
        total_count: int

        @overload
        def __init__(
                self, 
                *, 
                bytes_processed: int, 
                canceled_count: int, 
                failed_count: int, 
                successful_count: int, 
                total_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.DeidentificationOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REDACT = "Redact"
        SURROGATE = "Surrogate"
        SURROGATE_ONLY = "SurrogateOnly"
        TAG = "Tag"


    class azure.health.deidentification.models.DeidentificationResult(_Model):
        output_text: Optional[str]
        tagger_result: Optional[PhiTaggerResult]

        @overload
        def __init__(
                self, 
                *, 
                output_text: Optional[str] = ..., 
                tagger_result: Optional[PhiTaggerResult] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.health.deidentification.models.PhiCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT = "Account"
        AGE = "Age"
        BIO_ID = "BioID"
        CITY = "City"
        COUNTRY_OR_REGION = "CountryOrRegion"
        DATE = "Date"
        DEVICE = "Device"
        DOCTOR = "Doctor"
        EMAIL = "Email"
        FAX = "Fax"
        HEALTH_PLAN = "HealthPlan"
        HOSPITAL = "Hospital"
        ID_NUM = "IDNum"
        IP_ADDRESS = "IPAddress"
        LICENSE = "License"
        LOCATION_OTHER = "LocationOther"
        MEDICAL_RECORD = "MedicalRecord"
        ORGANIZATION = "Organization"
        PATIENT = "Patient"
        PHONE = "Phone"
        PROFESSION = "Profession"
        SOCIAL_SECURITY = "SocialSecurity"
        STATE = "State"
        STREET = "Street"
        UNKNOWN = "Unknown"
        URL = "Url"
        USERNAME = "Username"
        VEHICLE = "Vehicle"
        ZIP = "Zip"


    class azure.health.deidentification.models.PhiEntity(_Model):
        category: Union[str, PhiCategory]
        confidence_score: Optional[float]
        length: StringIndex
        offset: StringIndex
        text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Union[str, PhiCategory], 
                confidence_score: Optional[float] = ..., 
                length: StringIndex, 
                offset: StringIndex, 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.PhiTaggerResult(_Model):
        entities: List[PhiEntity]

        @overload
        def __init__(
                self, 
                *, 
                entities: List[PhiEntity]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.SimplePhiEntity(_Model):
        category: Union[str, PhiCategory]
        length: int
        offset: int
        text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Union[str, PhiCategory], 
                length: int, 
                offset: int, 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.SourceStorageLocation(_Model):
        extensions: Optional[List[str]]
        location: str
        prefix: str

        @overload
        def __init__(
                self, 
                *, 
                extensions: Optional[List[str]] = ..., 
                location: str, 
                prefix: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.StringIndex(_Model):
        code_point: int
        utf16: int
        utf8: int

        @overload
        def __init__(
                self, 
                *, 
                code_point: int, 
                utf16: int, 
                utf8: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.TaggedPhiEntities(_Model):
        encoding: Union[str, TextEncodingType]
        entities: List[SimplePhiEntity]

        @overload
        def __init__(
                self, 
                *, 
                encoding: Union[str, TextEncodingType], 
                entities: List[SimplePhiEntity]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.TargetStorageLocation(_Model):
        location: str
        overwrite: Optional[bool]
        prefix: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                overwrite: Optional[bool] = ..., 
                prefix: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.health.deidentification.models.TextEncodingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CODE_POINT = "CodePoint"
        UTF16 = "Utf16"
        UTF8 = "Utf8"


```
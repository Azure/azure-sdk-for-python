```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.healthinsights.cancerprofiling

    class azure.healthinsights.cancerprofiling.CancerProfilingClient(CancerProfilingClientOperationsMixin): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AzureKeyCredential, 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def begin_infer_cancer_profile(
                self, 
                body: OncoPhenotypeData, 
                *, 
                content_type: str = "application/json", 
                repeatability_first_sent: Optional[datetime] = ..., 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[OncoPhenotypeResult]: ...

        @overload
        def begin_infer_cancer_profile(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                repeatability_first_sent: Optional[datetime] = ..., 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[OncoPhenotypeResult]: ...

        @overload
        def begin_infer_cancer_profile(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                repeatability_first_sent: Optional[datetime] = ..., 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[OncoPhenotypeResult]: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: Optional[bool] = ..., 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.healthinsights.cancerprofiling.aio

    class azure.healthinsights.cancerprofiling.aio.CancerProfilingClient(CancerProfilingClientOperationsMixin): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AzureKeyCredential, 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def begin_infer_cancer_profile(
                self, 
                body: OncoPhenotypeData, 
                *, 
                content_type: str = "application/json", 
                repeatability_first_sent: Optional[datetime] = ..., 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OncoPhenotypeResult]: ...

        @overload
        async def begin_infer_cancer_profile(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                repeatability_first_sent: Optional[datetime] = ..., 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OncoPhenotypeResult]: ...

        @overload
        async def begin_infer_cancer_profile(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                repeatability_first_sent: Optional[datetime] = ..., 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OncoPhenotypeResult]: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.healthinsights.cancerprofiling.models

    class azure.healthinsights.cancerprofiling.models.ClinicalCodedElement(Model):
        code: str
        name: Optional[str]
        system: str
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                name: Optional[str] = ..., 
                system: str, 
                value: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.cancerprofiling.models.ClinicalDocumentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSULTATION = "consultation"
        DISCHARGE_SUMMARY = "dischargeSummary"
        HISTORY_AND_PHYSICAL = "historyAndPhysical"
        IMAGING = "imaging"
        LABORATORY = "laboratory"
        PATHOLOGY = "pathology"
        PROCEDURE = "procedure"
        PROGRESS = "progress"


    class azure.healthinsights.cancerprofiling.models.ClinicalNoteEvidence(Model):
        id: str
        length: int
        offset: int
        text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                length: int, 
                offset: int, 
                text: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.cancerprofiling.models.DocumentContent(Model):
        source_type: Union[str, DocumentContentSourceType]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                source_type: Union[str, DocumentContentSourceType], 
                value: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.cancerprofiling.models.DocumentContentSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        REFERENCE = "reference"


    class azure.healthinsights.cancerprofiling.models.DocumentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DICOM = "dicom"
        FHIR_BUNDLE = "fhirBundle"
        GENOMIC_SEQUENCING = "genomicSequencing"
        NOTE = "note"


    class azure.healthinsights.cancerprofiling.models.Error(Model):
        code: str
        details: List[Error]
        innererror: Optional[InnerError]
        message: str
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                details: List[Error], 
                innererror: Optional[InnerError] = ..., 
                message: str, 
                target: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.cancerprofiling.models.InferenceEvidence(Model):
        importance: Optional[float]
        patient_data_evidence: Optional[ClinicalNoteEvidence]
        patient_info_evidence: Optional[ClinicalCodedElement]

        @overload
        def __init__(
                self, 
                *, 
                importance: Optional[float] = ..., 
                patient_data_evidence: Optional[ClinicalNoteEvidence] = ..., 
                patient_info_evidence: Optional[ClinicalCodedElement] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.cancerprofiling.models.InnerError(Model):
        code: str
        innererror: Optional[InnerError]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                innererror: Optional[InnerError] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.cancerprofiling.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "failed"
        NOT_STARTED = "notStarted"
        PARTIALLY_COMPLETED = "partiallyCompleted"
        RUNNING = "running"
        SUCCEEDED = "succeeded"


    class azure.healthinsights.cancerprofiling.models.OncoPhenotypeData(Model):
        configuration: Optional[OncoPhenotypeModelConfiguration]
        patients: List[PatientRecord]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[OncoPhenotypeModelConfiguration] = ..., 
                patients: List[PatientRecord]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.cancerprofiling.models.OncoPhenotypeInference(Model):
        case_id: Optional[str]
        confidence_score: Optional[float]
        description: Optional[str]
        evidence: Optional[List[InferenceEvidence]]
        type: Union[str, OncoPhenotypeInferenceType]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                case_id: Optional[str] = ..., 
                confidence_score: Optional[float] = ..., 
                description: Optional[str] = ..., 
                evidence: Optional[List[InferenceEvidence]] = ..., 
                type: Union[str, OncoPhenotypeInferenceType], 
                value: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.cancerprofiling.models.OncoPhenotypeInferenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLINICAL_STAGE_M = "clinicalStageM"
        CLINICAL_STAGE_N = "clinicalStageN"
        CLINICAL_STAGE_T = "clinicalStageT"
        HISTOLOGY = "histology"
        PATHOLOGIC_STAGE_M = "pathologicStageM"
        PATHOLOGIC_STAGE_N = "pathologicStageN"
        PATHOLOGIC_STAGE_T = "pathologicStageT"
        TUMOR_SITE = "tumorSite"


    class azure.healthinsights.cancerprofiling.models.OncoPhenotypeModelConfiguration(Model):
        check_for_cancer_case: bool
        include_evidence: bool
        inference_types: Optional[List[Union[str, OncoPhenotypeInferenceType]]]
        verbose: bool

        @overload
        def __init__(
                self, 
                *, 
                check_for_cancer_case: bool = False, 
                include_evidence: bool = True, 
                inference_types: Optional[List[Union[str, OncoPhenotypeInferenceType]]] = ..., 
                verbose: bool = False
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.cancerprofiling.models.OncoPhenotypePatientResult(Model):
        id: str
        inferences: List[OncoPhenotypeInference]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                inferences: List[OncoPhenotypeInference]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.cancerprofiling.models.OncoPhenotypeResult(Model):
        created_date_time: datetime
        errors: Optional[List[Error]]
        expiration_date_time: datetime
        job_id: str
        last_update_date_time: datetime
        results: Optional[OncoPhenotypeResults]
        status: Union[str, JobStatus]


    class azure.healthinsights.cancerprofiling.models.OncoPhenotypeResults(Model):
        model_version: str
        patients: List[OncoPhenotypePatientResult]

        @overload
        def __init__(
                self, 
                *, 
                model_version: str, 
                patients: List[OncoPhenotypePatientResult]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.cancerprofiling.models.PatientDocument(Model):
        clinical_type: Optional[Union[str, ClinicalDocumentType]]
        content: DocumentContent
        created_date_time: Optional[datetime]
        id: str
        language: Optional[str]
        type: Union[str, DocumentType]

        @overload
        def __init__(
                self, 
                *, 
                clinical_type: Optional[Union[str, ClinicalDocumentType]] = ..., 
                content: DocumentContent, 
                created_date_time: Optional[datetime] = ..., 
                id: str, 
                language: Optional[str] = ..., 
                type: Union[str, DocumentType]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.cancerprofiling.models.PatientInfo(Model):
        birth_date: Optional[date]
        clinical_info: Optional[List[ClinicalCodedElement]]
        sex: Optional[Union[str, PatientInfoSex]]

        @overload
        def __init__(
                self, 
                *, 
                birth_date: Optional[date] = ..., 
                clinical_info: Optional[List[ClinicalCodedElement]] = ..., 
                sex: Optional[Union[str, PatientInfoSex]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.cancerprofiling.models.PatientInfoSex(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FEMALE = "female"
        MALE = "male"
        UNSPECIFIED = "unspecified"


    class azure.healthinsights.cancerprofiling.models.PatientRecord(Model):
        data: Optional[List[PatientDocument]]
        id: str
        info: Optional[PatientInfo]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[List[PatientDocument]] = ..., 
                id: str, 
                info: Optional[PatientInfo] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.cancerprofiling.models.RepeatabilityResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "accepted"
        REJECTED = "rejected"


```
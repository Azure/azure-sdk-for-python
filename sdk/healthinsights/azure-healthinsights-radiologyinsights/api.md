```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.healthinsights.radiologyinsights

    class azure.healthinsights.radiologyinsights.RadiologyInsightsClient: implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def begin_infer_radiology_insights(
                self, 
                id: str, 
                resource: RadiologyInsightsJob, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[RadiologyInsightsInferenceResult]: ...

        @overload
        def begin_infer_radiology_insights(
                self, 
                id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[RadiologyInsightsInferenceResult]: ...

        @overload
        def begin_infer_radiology_insights(
                self, 
                id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                expand: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[RadiologyInsightsInferenceResult]: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.healthinsights.radiologyinsights.aio

    class azure.healthinsights.radiologyinsights.aio.RadiologyInsightsClient: implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def begin_infer_radiology_insights(
                self, 
                id: str, 
                resource: RadiologyInsightsJob, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[RadiologyInsightsInferenceResult]: ...

        @overload
        async def begin_infer_radiology_insights(
                self, 
                id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[RadiologyInsightsInferenceResult]: ...

        @overload
        async def begin_infer_radiology_insights(
                self, 
                id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                expand: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[RadiologyInsightsInferenceResult]: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.healthinsights.radiologyinsights.models

    class azure.healthinsights.radiologyinsights.models.AgeMismatchInference(RadiologyInsightsInference, discriminator='ageMismatch'):
        extension: list[Extension]
        kind: Literal[RadiologyInsightsInferenceType.AGE_MISMATCH]

        @overload
        def __init__(
                self, 
                *, 
                extension: Optional[List[Extension]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.Annotation(Element):
        author_string: Optional[str]
        extension: list[Extension]
        id: str
        text: str
        time: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                author_string: Optional[str] = ..., 
                extension: Optional[List[Extension]] = ..., 
                id: Optional[str] = ..., 
                text: str, 
                time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.AssessmentValueRange(_Model):
        maximum: str
        minimum: str

        @overload
        def __init__(
                self, 
                *, 
                maximum: str, 
                minimum: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.ClinicalDocumentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSULTATION = "consultation"
        DISCHARGE_SUMMARY = "dischargeSummary"
        HISTORY_AND_PHYSICAL = "historyAndPhysical"
        LABORATORY = "laboratory"
        PATHOLOGY_REPORT = "pathologyReport"
        PROCEDURE = "procedure"
        PROGRESS = "progress"
        RADIOLOGY_REPORT = "radiologyReport"


    class azure.healthinsights.radiologyinsights.models.CodeableConcept(Element):
        coding: Optional[List[Coding]]
        text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                coding: Optional[List[Coding]] = ..., 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.Coding(Element):
        code: Optional[str]
        display: Optional[str]
        extension: list[Extension]
        id: str
        system: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                display: Optional[str] = ..., 
                extension: Optional[List[Extension]] = ..., 
                id: Optional[str] = ..., 
                system: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.CompleteOrderDiscrepancyInference(RadiologyInsightsInference, discriminator='completeOrderDiscrepancy'):
        extension: list[Extension]
        kind: Literal[RadiologyInsightsInferenceType.COMPLETE_ORDER_DISCREPANCY]
        missing_body_part_measurements: Optional[List[CodeableConcept]]
        missing_body_parts: Optional[List[CodeableConcept]]
        order_type: CodeableConcept

        @overload
        def __init__(
                self, 
                *, 
                extension: Optional[List[Extension]] = ..., 
                missing_body_part_measurements: Optional[List[CodeableConcept]] = ..., 
                missing_body_parts: Optional[List[CodeableConcept]] = ..., 
                order_type: CodeableConcept
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.ContactPointSystem(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMAIL = "email"
        FAX = "fax"
        OTHER = "other"
        PAGER = "pager"
        PHONE = "phone"
        SMS = "sms"
        URL = "url"


    class azure.healthinsights.radiologyinsights.models.ContactPointUse(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HOME = "home"
        MOBILE = "mobile"
        OLD = "old"
        TEMP = "temp"
        WORK = "work"


    class azure.healthinsights.radiologyinsights.models.CriticalResult(_Model):
        description: str
        finding: Optional[Observation]

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                finding: Optional[Observation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.CriticalResultInference(RadiologyInsightsInference, discriminator='criticalResult'):
        extension: list[Extension]
        kind: Literal[RadiologyInsightsInferenceType.CRITICAL_RESULT]
        result: CriticalResult

        @overload
        def __init__(
                self, 
                *, 
                extension: Optional[List[Extension]] = ..., 
                result: CriticalResult
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.DocumentAdministrativeMetadata(_Model):
        encounter_id: Optional[str]
        ordered_procedures: Optional[List[OrderedProcedure]]

        @overload
        def __init__(
                self, 
                *, 
                encounter_id: Optional[str] = ..., 
                ordered_procedures: Optional[List[OrderedProcedure]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.DocumentAuthor(_Model):
        full_name: Optional[str]
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                full_name: Optional[str] = ..., 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.DocumentContent(_Model):
        source_type: Union[str, DocumentContentSourceType]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                source_type: Union[str, DocumentContentSourceType], 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.DocumentContentSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        REFERENCE = "reference"


    class azure.healthinsights.radiologyinsights.models.DocumentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DICOM = "dicom"
        FHIR_BUNDLE = "fhirBundle"
        GENOMIC_SEQUENCING = "genomicSequencing"
        NOTE = "note"


    class azure.healthinsights.radiologyinsights.models.DomainResource(Resource):
        contained: Optional[List[Resource]]
        extension: Optional[List[Extension]]
        id: str
        implicit_rules: str
        language: str
        meta: Meta
        modifier_extension: Optional[List[Extension]]
        resource_type: str
        text: Optional[Narrative]

        @overload
        def __init__(
                self, 
                *, 
                contained: Optional[List[Resource]] = ..., 
                extension: Optional[List[Extension]] = ..., 
                id: Optional[str] = ..., 
                implicit_rules: Optional[str] = ..., 
                language: Optional[str] = ..., 
                meta: Optional[Meta] = ..., 
                modifier_extension: Optional[List[Extension]] = ..., 
                resource_type: str, 
                text: Optional[Narrative] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.Element(_Model):
        extension: Optional[List[Extension]]
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                extension: Optional[List[Extension]] = ..., 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.EncounterClass(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMBULATORY = "ambulatory"
        EMERGENCY = "emergency"
        HEALTH_HOME = "healthHome"
        IN_PATIENT = "inpatient"
        OBSERVATION = "observation"
        VIRTUAL = "virtual"


    class azure.healthinsights.radiologyinsights.models.Extension(Element):
        url: str
        value_boolean: Optional[bool]
        value_codeable_concept: Optional[CodeableConcept]
        value_date_time: Optional[str]
        value_integer: Optional[int]
        value_period: Optional[Period]
        value_quantity: Optional[Quantity]
        value_range: Optional[Range]
        value_ratio: Optional[Ratio]
        value_reference: Optional[Reference]
        value_sampled_data: Optional[SampledData]
        value_string: Optional[str]
        value_time: Optional[time]

        @overload
        def __init__(
                self, 
                *, 
                url: str, 
                value_boolean: Optional[bool] = ..., 
                value_codeable_concept: Optional[CodeableConcept] = ..., 
                value_date_time: Optional[str] = ..., 
                value_integer: Optional[int] = ..., 
                value_period: Optional[Period] = ..., 
                value_quantity: Optional[Quantity] = ..., 
                value_range: Optional[Range] = ..., 
                value_ratio: Optional[Ratio] = ..., 
                value_reference: Optional[Reference] = ..., 
                value_sampled_data: Optional[SampledData] = ..., 
                value_string: Optional[str] = ..., 
                value_time: Optional[time] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.FindingInference(RadiologyInsightsInference, discriminator='finding'):
        extension: list[Extension]
        finding: Observation
        kind: Literal[RadiologyInsightsInferenceType.FINDING]

        @overload
        def __init__(
                self, 
                *, 
                extension: Optional[List[Extension]] = ..., 
                finding: Observation
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.FindingOptions(_Model):
        provide_focused_sentence_evidence: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                provide_focused_sentence_evidence: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.FollowupCommunicationInference(RadiologyInsightsInference, discriminator='followupCommunication'):
        communicated_at: Optional[List[datetime]]
        extension: list[Extension]
        kind: Literal[RadiologyInsightsInferenceType.FOLLOWUP_COMMUNICATION]
        recipient: Optional[List[Union[str, MedicalProfessionalType]]]
        was_acknowledged: bool

        @overload
        def __init__(
                self, 
                *, 
                communicated_at: Optional[List[datetime]] = ..., 
                extension: Optional[List[Extension]] = ..., 
                recipient: Optional[List[Union[str, MedicalProfessionalType]]] = ..., 
                was_acknowledged: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.FollowupRecommendationInference(RadiologyInsightsInference, discriminator='followupRecommendation'):
        effective_at: Optional[str]
        effective_period: Optional[Period]
        extension: list[Extension]
        findings: Optional[List[RecommendationFinding]]
        is_conditional: bool
        is_guideline: bool
        is_hedging: bool
        is_option: bool
        kind: Literal[RadiologyInsightsInferenceType.FOLLOWUP_RECOMMENDATION]
        recommended_procedure: ProcedureRecommendation

        @overload
        def __init__(
                self, 
                *, 
                effective_at: Optional[str] = ..., 
                effective_period: Optional[Period] = ..., 
                extension: Optional[List[Extension]] = ..., 
                findings: Optional[List[RecommendationFinding]] = ..., 
                is_conditional: bool, 
                is_guideline: bool, 
                is_hedging: bool, 
                is_option: bool, 
                recommended_procedure: ProcedureRecommendation
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.FollowupRecommendationOptions(_Model):
        include_recommendations_in_references: Optional[bool]
        include_recommendations_with_no_specified_modality: Optional[bool]
        provide_focused_sentence_evidence: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                include_recommendations_in_references: Optional[bool] = ..., 
                include_recommendations_with_no_specified_modality: Optional[bool] = ..., 
                provide_focused_sentence_evidence: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.GenericProcedureRecommendation(ProcedureRecommendation, discriminator='genericProcedureRecommendation'):
        code: CodeableConcept
        description: Optional[str]
        extension: list[Extension]
        kind: Literal["genericProcedureRecommendation"]

        @overload
        def __init__(
                self, 
                *, 
                code: CodeableConcept, 
                description: Optional[str] = ..., 
                extension: Optional[List[Extension]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.GuidanceInference(RadiologyInsightsInference, discriminator='guidance'):
        extension: list[Extension]
        finding: FindingInference
        identifier: CodeableConcept
        kind: Literal[RadiologyInsightsInferenceType.GUIDANCE]
        missing_guidance_information: Optional[List[str]]
        present_guidance_information: Optional[List[PresentGuidanceInformation]]
        ranking: Union[str, GuidanceRankingType]
        recommendation_proposals: Optional[List[FollowupRecommendationInference]]

        @overload
        def __init__(
                self, 
                *, 
                extension: Optional[List[Extension]] = ..., 
                finding: FindingInference, 
                identifier: CodeableConcept, 
                missing_guidance_information: Optional[List[str]] = ..., 
                present_guidance_information: Optional[List[PresentGuidanceInformation]] = ..., 
                ranking: Union[str, GuidanceRankingType], 
                recommendation_proposals: Optional[List[FollowupRecommendationInference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.GuidanceOptions(_Model):
        show_guidance_in_history: bool

        @overload
        def __init__(
                self, 
                *, 
                show_guidance_in_history: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.GuidanceRankingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"


    class azure.healthinsights.radiologyinsights.models.HealthInsightsErrorResponse(_Model):
        error: ODataV4Format

        @overload
        def __init__(
                self, 
                *, 
                error: ODataV4Format
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.Identifier(Element):
        assigner: Optional[Reference]
        period: Optional[Period]
        system: Optional[str]
        type: Optional[CodeableConcept]
        use: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assigner: Optional[Reference] = ..., 
                period: Optional[Period] = ..., 
                system: Optional[str] = ..., 
                type: Optional[CodeableConcept] = ..., 
                use: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.ImagingProcedure(_Model):
        anatomy: CodeableConcept
        contrast: Optional[RadiologyCodeWithTypes]
        laterality: Optional[CodeableConcept]
        modality: CodeableConcept
        view: Optional[RadiologyCodeWithTypes]

        @overload
        def __init__(
                self, 
                *, 
                anatomy: CodeableConcept, 
                contrast: Optional[RadiologyCodeWithTypes] = ..., 
                laterality: Optional[CodeableConcept] = ..., 
                modality: CodeableConcept, 
                view: Optional[RadiologyCodeWithTypes] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.ImagingProcedureRecommendation(ProcedureRecommendation, discriminator='imagingProcedureRecommendation'):
        extension: list[Extension]
        imaging_procedures: List[ImagingProcedure]
        kind: Literal["imagingProcedureRecommendation"]
        procedure_codes: Optional[List[CodeableConcept]]

        @overload
        def __init__(
                self, 
                *, 
                extension: Optional[List[Extension]] = ..., 
                imaging_procedures: List[ImagingProcedure], 
                procedure_codes: Optional[List[CodeableConcept]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "canceled"
        FAILED = "failed"
        NOT_STARTED = "notStarted"
        RUNNING = "running"
        SUCCEEDED = "succeeded"


    class azure.healthinsights.radiologyinsights.models.LateralityDiscrepancyInference(RadiologyInsightsInference, discriminator='lateralityDiscrepancy'):
        discrepancy_type: Union[str, LateralityDiscrepancyType]
        extension: list[Extension]
        kind: Literal[RadiologyInsightsInferenceType.LATERALITY_DISCREPANCY]
        laterality_indication: Optional[CodeableConcept]

        @overload
        def __init__(
                self, 
                *, 
                discrepancy_type: Union[str, LateralityDiscrepancyType], 
                extension: Optional[List[Extension]] = ..., 
                laterality_indication: Optional[CodeableConcept] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.LateralityDiscrepancyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ORDER_LATERALITY_MISMATCH = "orderLateralityMismatch"
        TEXT_LATERALITY_CONTRADICTION = "textLateralityContradiction"
        TEXT_LATERALITY_MISSING = "textLateralityMissing"


    class azure.healthinsights.radiologyinsights.models.LimitedOrderDiscrepancyInference(RadiologyInsightsInference, discriminator='limitedOrderDiscrepancy'):
        extension: list[Extension]
        kind: Literal[RadiologyInsightsInferenceType.LIMITED_ORDER_DISCREPANCY]
        order_type: CodeableConcept
        present_body_part_measurements: Optional[List[CodeableConcept]]
        present_body_parts: Optional[List[CodeableConcept]]

        @overload
        def __init__(
                self, 
                *, 
                extension: Optional[List[Extension]] = ..., 
                order_type: CodeableConcept, 
                present_body_part_measurements: Optional[List[CodeableConcept]] = ..., 
                present_body_parts: Optional[List[CodeableConcept]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.MedicalProfessionalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOCTOR = "doctor"
        MIDWIFE = "midwife"
        NURSE = "nurse"
        PHYSICIAN_ASSISTANT = "physicianAssistant"
        UNKNOWN = "unknown"


    class azure.healthinsights.radiologyinsights.models.Meta(_Model):
        last_updated: Optional[str]
        profile: Optional[List[str]]
        security: Optional[List[Coding]]
        source: Optional[str]
        tag: Optional[List[Coding]]
        version_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                last_updated: Optional[str] = ..., 
                profile: Optional[List[str]] = ..., 
                security: Optional[List[Coding]] = ..., 
                source: Optional[str] = ..., 
                tag: Optional[List[Coding]] = ..., 
                version_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.Narrative(Element):
        div: str
        extension: list[Extension]
        id: str
        status: str

        @overload
        def __init__(
                self, 
                *, 
                div: str, 
                extension: Optional[List[Extension]] = ..., 
                id: Optional[str] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.Observation(DomainResource, discriminator='Observation'):
        body_site: Optional[CodeableConcept]
        category: Optional[List[CodeableConcept]]
        code: CodeableConcept
        component: Optional[List[ObservationComponent]]
        contained: list[Resource]
        data_absent_reason: Optional[CodeableConcept]
        derived_from: Optional[List[Reference]]
        effective_date_time: Optional[str]
        effective_instant: Optional[str]
        effective_period: Optional[Period]
        encounter: Optional[Reference]
        extension: list[Extension]
        has_member: Optional[List[Reference]]
        id: str
        identifier: Optional[List[Identifier]]
        implicit_rules: str
        interpretation: Optional[List[CodeableConcept]]
        issued: Optional[str]
        language: str
        meta: Meta
        method: Optional[CodeableConcept]
        modifier_extension: list[Extension]
        note: Optional[List[Annotation]]
        reference_range: Optional[List[ObservationReferenceRange]]
        resource_type: Literal["Observation"]
        status: Union[str, ObservationStatusCodeType]
        subject: Optional[Reference]
        text: Narrative
        value_boolean: Optional[bool]
        value_codeable_concept: Optional[CodeableConcept]
        value_date_time: Optional[str]
        value_integer: Optional[int]
        value_period: Optional[Period]
        value_quantity: Optional[Quantity]
        value_range: Optional[Range]
        value_ratio: Optional[Ratio]
        value_sampled_data: Optional[SampledData]
        value_string: Optional[str]
        value_time: Optional[time]

        @overload
        def __init__(
                self, 
                *, 
                body_site: Optional[CodeableConcept] = ..., 
                category: Optional[List[CodeableConcept]] = ..., 
                code: CodeableConcept, 
                component: Optional[List[ObservationComponent]] = ..., 
                contained: Optional[List[Resource]] = ..., 
                data_absent_reason: Optional[CodeableConcept] = ..., 
                derived_from: Optional[List[Reference]] = ..., 
                effective_date_time: Optional[str] = ..., 
                effective_instant: Optional[str] = ..., 
                effective_period: Optional[Period] = ..., 
                encounter: Optional[Reference] = ..., 
                extension: Optional[List[Extension]] = ..., 
                has_member: Optional[List[Reference]] = ..., 
                id: Optional[str] = ..., 
                identifier: Optional[List[Identifier]] = ..., 
                implicit_rules: Optional[str] = ..., 
                interpretation: Optional[List[CodeableConcept]] = ..., 
                issued: Optional[str] = ..., 
                language: Optional[str] = ..., 
                meta: Optional[Meta] = ..., 
                method: Optional[CodeableConcept] = ..., 
                modifier_extension: Optional[List[Extension]] = ..., 
                note: Optional[List[Annotation]] = ..., 
                reference_range: Optional[List[ObservationReferenceRange]] = ..., 
                status: Union[str, ObservationStatusCodeType], 
                subject: Optional[Reference] = ..., 
                text: Optional[Narrative] = ..., 
                value_boolean: Optional[bool] = ..., 
                value_codeable_concept: Optional[CodeableConcept] = ..., 
                value_date_time: Optional[str] = ..., 
                value_integer: Optional[int] = ..., 
                value_period: Optional[Period] = ..., 
                value_quantity: Optional[Quantity] = ..., 
                value_range: Optional[Range] = ..., 
                value_ratio: Optional[Ratio] = ..., 
                value_sampled_data: Optional[SampledData] = ..., 
                value_string: Optional[str] = ..., 
                value_time: Optional[time] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.ObservationComponent(Element):
        code: CodeableConcept
        data_absent_reason: Optional[CodeableConcept]
        extension: list[Extension]
        id: str
        interpretation: Optional[List[CodeableConcept]]
        reference_range: Optional[List[ObservationReferenceRange]]
        value_boolean: Optional[bool]
        value_codeable_concept: Optional[CodeableConcept]
        value_date_time: Optional[str]
        value_integer: Optional[int]
        value_period: Optional[Period]
        value_quantity: Optional[Quantity]
        value_range: Optional[Range]
        value_ratio: Optional[Ratio]
        value_reference: Optional[Reference]
        value_sampled_data: Optional[SampledData]
        value_string: Optional[str]
        value_time: Optional[time]

        @overload
        def __init__(
                self, 
                *, 
                code: CodeableConcept, 
                data_absent_reason: Optional[CodeableConcept] = ..., 
                extension: Optional[List[Extension]] = ..., 
                id: Optional[str] = ..., 
                interpretation: Optional[List[CodeableConcept]] = ..., 
                reference_range: Optional[List[ObservationReferenceRange]] = ..., 
                value_boolean: Optional[bool] = ..., 
                value_codeable_concept: Optional[CodeableConcept] = ..., 
                value_date_time: Optional[str] = ..., 
                value_integer: Optional[int] = ..., 
                value_period: Optional[Period] = ..., 
                value_quantity: Optional[Quantity] = ..., 
                value_range: Optional[Range] = ..., 
                value_ratio: Optional[Ratio] = ..., 
                value_reference: Optional[Reference] = ..., 
                value_sampled_data: Optional[SampledData] = ..., 
                value_string: Optional[str] = ..., 
                value_time: Optional[time] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.ObservationReferenceRange(_Model):
        age: Optional[Range]
        applies_to: Optional[List[CodeableConcept]]
        high: Optional[Quantity]
        low: Optional[Quantity]
        text: Optional[str]
        type: Optional[CodeableConcept]

        @overload
        def __init__(
                self, 
                *, 
                age: Optional[Range] = ..., 
                applies_to: Optional[List[CodeableConcept]] = ..., 
                high: Optional[Quantity] = ..., 
                low: Optional[Quantity] = ..., 
                text: Optional[str] = ..., 
                type: Optional[CodeableConcept] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.ObservationStatusCodeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMENDED = "amended"
        CANCELLED = "cancelled"
        CORRECTED = "corrected"
        ENTERED_IN_ERROR = "entered-in-error"
        FINAL = "final"
        PRELIMINARY = "preliminary"
        REGISTERED = "registered"
        UNKNOWN = "unknown"


    class azure.healthinsights.radiologyinsights.models.OrderedProcedure(_Model):
        code: Optional[CodeableConcept]
        description: Optional[str]
        extension: Optional[List[Extension]]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[CodeableConcept] = ..., 
                description: Optional[str] = ..., 
                extension: Optional[List[Extension]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.PatientDetails(_Model):
        birth_date: Optional[date]
        clinical_info: Optional[List[Resource]]
        sex: Optional[Union[str, PatientSex]]

        @overload
        def __init__(
                self, 
                *, 
                birth_date: Optional[date] = ..., 
                clinical_info: Optional[List[Resource]] = ..., 
                sex: Optional[Union[str, PatientSex]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.PatientDocument(_Model):
        administrative_metadata: Optional[DocumentAdministrativeMetadata]
        authors: Optional[List[DocumentAuthor]]
        clinical_type: Optional[Union[str, ClinicalDocumentType]]
        content: DocumentContent
        created_at: Optional[datetime]
        id: str
        language: Optional[str]
        specialty_type: Optional[Union[str, SpecialtyType]]
        type: Union[str, DocumentType]

        @overload
        def __init__(
                self, 
                *, 
                administrative_metadata: Optional[DocumentAdministrativeMetadata] = ..., 
                authors: Optional[List[DocumentAuthor]] = ..., 
                clinical_type: Optional[Union[str, ClinicalDocumentType]] = ..., 
                content: DocumentContent, 
                created_at: Optional[datetime] = ..., 
                id: str, 
                language: Optional[str] = ..., 
                specialty_type: Optional[Union[str, SpecialtyType]] = ..., 
                type: Union[str, DocumentType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.PatientEncounter(_Model):
        class_property: Optional[Union[str, EncounterClass]]
        id: str
        period: Optional[TimePeriod]

        @overload
        def __init__(
                self, 
                *, 
                class_property: Optional[Union[str, EncounterClass]] = ..., 
                id: str, 
                period: Optional[TimePeriod] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.PatientRecord(_Model):
        details: Optional[PatientDetails]
        encounters: Optional[List[PatientEncounter]]
        id: str
        patient_documents: Optional[List[PatientDocument]]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[PatientDetails] = ..., 
                encounters: Optional[List[PatientEncounter]] = ..., 
                id: str, 
                patient_documents: Optional[List[PatientDocument]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.PatientSex(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FEMALE = "female"
        MALE = "male"
        UNSPECIFIED = "unspecified"


    class azure.healthinsights.radiologyinsights.models.Period(Element):
        end: Optional[str]
        start: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end: Optional[str] = ..., 
                start: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.PresentGuidanceInformation(_Model):
        extension: Optional[List[Extension]]
        maximum_diameter_as_in_text: Optional[Quantity]
        present_guidance_item: str
        present_guidance_values: Optional[List[str]]
        sizes: Optional[List[Observation]]

        @overload
        def __init__(
                self, 
                *, 
                extension: Optional[List[Extension]] = ..., 
                maximum_diameter_as_in_text: Optional[Quantity] = ..., 
                present_guidance_item: str, 
                present_guidance_values: Optional[List[str]] = ..., 
                sizes: Optional[List[Observation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.ProcedureRecommendation(_Model):
        extension: Optional[List[Extension]]
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                extension: Optional[List[Extension]] = ..., 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.QualityMeasureComplianceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DENOMINATOR_EXCEPTION = "denominatorException"
        NOT_ELIGIBLE = "notEligible"
        PERFORMANCE_MET = "performanceMet"
        PERFORMANCE_NOT_MET = "performanceNotMet"


    class azure.healthinsights.radiologyinsights.models.QualityMeasureInference(RadiologyInsightsInference, discriminator='qualityMeasure'):
        compliance_type: Union[str, QualityMeasureComplianceType]
        extension: list[Extension]
        kind: Literal[RadiologyInsightsInferenceType.QUALITY_MEASURE]
        quality_criteria: Optional[List[str]]
        quality_measure_denominator: str

        @overload
        def __init__(
                self, 
                *, 
                compliance_type: Union[str, QualityMeasureComplianceType], 
                extension: Optional[List[Extension]] = ..., 
                quality_criteria: Optional[List[str]] = ..., 
                quality_measure_denominator: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.QualityMeasureOptions(_Model):
        measure_types: List[Union[str, QualityMeasureType]]

        @overload
        def __init__(
                self, 
                *, 
                measure_types: List[Union[str, QualityMeasureType]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.QualityMeasureType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACRAD36 = "acrad36"
        ACRAD37 = "acrad37"
        ACRAD38 = "acrad38"
        ACRAD39 = "acrad39"
        ACRAD40 = "acrad40"
        ACRAD41 = "acrad41"
        ACRAD42 = "acrad42"
        MEDNAX55 = "mednax55"
        MIPS145 = "mips145"
        MIPS147 = "mips147"
        MIPS195 = "mips195"
        MIPS360 = "mips360"
        MIPS364 = "mips364"
        MIPS405 = "mips405"
        MIPS406 = "mips406"
        MIPS436 = "mips436"
        MIPS76 = "mips76"
        MSN13 = "msn13"
        MSN15 = "msn15"
        QMM17 = "qmm17"
        QMM18 = "qmm18"
        QMM19 = "qmm19"
        QMM26 = "qmm26"


    class azure.healthinsights.radiologyinsights.models.Quantity(Element):
        code: Optional[str]
        comparator: Optional[str]
        system: Optional[str]
        unit: Optional[str]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                comparator: Optional[str] = ..., 
                system: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.RadiologyCodeWithTypes(_Model):
        code: CodeableConcept
        types: List[CodeableConcept]

        @overload
        def __init__(
                self, 
                *, 
                code: CodeableConcept, 
                types: List[CodeableConcept]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.RadiologyInsightsData(_Model):
        configuration: Optional[RadiologyInsightsModelConfiguration]
        patients: List[PatientRecord]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[RadiologyInsightsModelConfiguration] = ..., 
                patients: List[PatientRecord]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.RadiologyInsightsInference(_Model):
        extension: Optional[List[Extension]]
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                extension: Optional[List[Extension]] = ..., 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.RadiologyInsightsInferenceOptions(_Model):
        finding_options: Optional[FindingOptions]
        followup_recommendation_options: Optional[FollowupRecommendationOptions]
        guidance_options: Optional[GuidanceOptions]
        quality_measure_options: Optional[QualityMeasureOptions]

        @overload
        def __init__(
                self, 
                *, 
                finding_options: Optional[FindingOptions] = ..., 
                followup_recommendation_options: Optional[FollowupRecommendationOptions] = ..., 
                guidance_options: Optional[GuidanceOptions] = ..., 
                quality_measure_options: Optional[QualityMeasureOptions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.RadiologyInsightsInferenceResult(_Model):
        model_version: str
        patient_results: List[RadiologyInsightsPatientResult]

        @overload
        def __init__(
                self, 
                *, 
                model_version: str, 
                patient_results: List[RadiologyInsightsPatientResult]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.RadiologyInsightsInferenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGE_MISMATCH = "ageMismatch"
        COMPLETE_ORDER_DISCREPANCY = "completeOrderDiscrepancy"
        CRITICAL_RESULT = "criticalResult"
        FINDING = "finding"
        FOLLOWUP_COMMUNICATION = "followupCommunication"
        FOLLOWUP_RECOMMENDATION = "followupRecommendation"
        GUIDANCE = "guidance"
        LATERALITY_DISCREPANCY = "lateralityDiscrepancy"
        LIMITED_ORDER_DISCREPANCY = "limitedOrderDiscrepancy"
        QUALITY_MEASURE = "qualityMeasure"
        RADIOLOGY_PROCEDURE = "radiologyProcedure"
        SCORING_AND_ASSESSMENT = "scoringAndAssessment"
        SEX_MISMATCH = "sexMismatch"


    class azure.healthinsights.radiologyinsights.models.RadiologyInsightsJob(_Model):
        created_at: Optional[datetime]
        error: Optional[ODataV4Format]
        expires_at: Optional[datetime]
        id: str
        job_data: Optional[RadiologyInsightsData]
        result: Optional[RadiologyInsightsInferenceResult]
        status: Union[str, JobStatus]
        updated_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                job_data: Optional[RadiologyInsightsData] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.RadiologyInsightsModelConfiguration(_Model):
        include_evidence: Optional[bool]
        inference_options: Optional[RadiologyInsightsInferenceOptions]
        inference_types: Optional[List[Union[str, RadiologyInsightsInferenceType]]]
        locale: Optional[str]
        verbose: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                include_evidence: Optional[bool] = ..., 
                inference_options: Optional[RadiologyInsightsInferenceOptions] = ..., 
                inference_types: Optional[List[Union[str, RadiologyInsightsInferenceType]]] = ..., 
                locale: Optional[str] = ..., 
                verbose: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.RadiologyInsightsPatientResult(_Model):
        inferences: List[RadiologyInsightsInference]
        patient_id: str

        @overload
        def __init__(
                self, 
                *, 
                inferences: List[RadiologyInsightsInference], 
                patient_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.RadiologyProcedureInference(RadiologyInsightsInference, discriminator='radiologyProcedure'):
        extension: list[Extension]
        imaging_procedures: List[ImagingProcedure]
        kind: Literal[RadiologyInsightsInferenceType.RADIOLOGY_PROCEDURE]
        ordered_procedure: OrderedProcedure
        procedure_codes: Optional[List[CodeableConcept]]

        @overload
        def __init__(
                self, 
                *, 
                extension: Optional[List[Extension]] = ..., 
                imaging_procedures: List[ImagingProcedure], 
                ordered_procedure: OrderedProcedure, 
                procedure_codes: Optional[List[CodeableConcept]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.Range(Element):
        high: Optional[Quantity]
        low: Optional[Quantity]

        @overload
        def __init__(
                self, 
                *, 
                high: Optional[Quantity] = ..., 
                low: Optional[Quantity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.Ratio(Element):
        denominator: Optional[Quantity]
        numerator: Optional[Quantity]

        @overload
        def __init__(
                self, 
                *, 
                denominator: Optional[Quantity] = ..., 
                numerator: Optional[Quantity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.RecommendationFinding(_Model):
        critical_finding: Optional[CriticalResult]
        extension: Optional[List[Extension]]
        finding: Optional[Observation]
        recommendation_finding_status: Union[str, RecommendationFindingStatusType]

        @overload
        def __init__(
                self, 
                *, 
                critical_finding: Optional[CriticalResult] = ..., 
                extension: Optional[List[Extension]] = ..., 
                finding: Optional[Observation] = ..., 
                recommendation_finding_status: Union[str, RecommendationFindingStatusType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.RecommendationFindingStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONDITIONAL = "conditional"
        DIFFERENTIAL = "differential"
        PRESENT = "present"
        RULE_OUT = "ruleOut"


    class azure.healthinsights.radiologyinsights.models.Reference(Element):
        display: Optional[str]
        identifier: Optional[Identifier]
        reference: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[str] = ..., 
                identifier: Optional[Identifier] = ..., 
                reference: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.ResearchStudyStatusCodeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        ADMINISTRATIVELY_COMPLETED = "administratively-completed"
        APPROVED = "approved"
        CLOSED_TO_ACCRUAL = "closed-to-accrual"
        CLOSED_TO_ACCRUAL_AND_INTERVENTION = "closed-to-accrual-and-intervention"
        COMPLETED = "completed"
        DISAPPROVED = "disapproved"
        IN_REVIEW = "in-review"
        TEMPORARILY_CLOSED_TO_ACCRUAL = "temporarily-closed-to-accrual"
        TEMPORARILY_CLOSED_TO_ACCRUAL_AND_INTERVENTION = "temporarily-closed-to-accrual-and-intervention"
        WITHDRAWN = "withdrawn"


    class azure.healthinsights.radiologyinsights.models.Resource(_Model):
        id: Optional[str]
        implicit_rules: Optional[str]
        language: Optional[str]
        meta: Optional[Meta]
        resource_type: str

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                implicit_rules: Optional[str] = ..., 
                language: Optional[str] = ..., 
                meta: Optional[Meta] = ..., 
                resource_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.SampledData(Element):
        data: Optional[str]
        dimensions: int
        factor: Optional[float]
        lower_limit: Optional[float]
        origin: Quantity
        period: float
        upper_limit: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[str] = ..., 
                dimensions: int, 
                factor: Optional[float] = ..., 
                lower_limit: Optional[float] = ..., 
                origin: Quantity, 
                period: float, 
                upper_limit: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.ScoringAndAssessmentCategoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGATSTON_SCORE = "AGATSTON SCORE"
        ALBERTA_STROKE_PROGRAM_EARLY_CT_SCORE = "ALBERTA STROKE PROGRAM EARLY CT SCORE"
        ASCVD_RISK = "ASCVD RISK"
        BIRADS = "BIRADS"
        CAD_RADS = "CAD-RADS"
        CALCIUM_MASS_SCORE = "CALCIUM MASS SCORE"
        CALCIUM_SCORE_UNSPECIFIED = "CALCIUM SCORE (UNSPECIFIED)"
        CALCIUM_VOLUME_SCORE = "CALCIUM VOLUME SCORE"
        CEUS_LI_RADS = "CEUS LI-RADS"
        C_RADS_COLONIC_FINDINGS = "C-RADS COLONIC FINDINGS"
        C_RADS_EXTRACOLONIC_FINDINGS = "C-RADS EXTRACOLONIC FINDINGS"
        FRAX_SCORE = "FRAX SCORE"
        HNPCC_MUTATION_RISK = "HNPCC MUTATION RISK"
        KELLGREN_LAWRENCE_GRADING_SCALE = "KELLGREN-LAWRENCE GRADING SCALE"
        LIFETIME_BREAST_CANCER_RISK = "LIFETIME BREAST CANCER RISK"
        LI_RADS = "LI-RADS"
        LUNG_RADS = "LUNG-RADS"
        MODIFIED_GAIL_MODEL_RISK = "MODIFIED GAIL MODEL RISK"
        NI_RADS = "NI-RADS"
        O_RADS = "O-RADS"
        O_RADS_MRI = "O-RADS MRI"
        PI_RADS = "PI-RADS"
        RISK_OF_MALIGNANCY_INDEX = "RISK OF MALIGNANCY INDEX"
        TEN_YEAR_CHD_RISK = "10 YEAR CHD RISK"
        TEN_YEAR_CHD_RISK_ARTERIAL_AGE = "10 YEAR CHD RISK (ARTERIAL AGE)"
        TEN_YEAR_CHD_RISK_OBSERVED_AGE = "10 YEAR CHD RISK (OBSERVED AGE)"
        TI_RADS = "TI-RADS"
        TONNIS_CLASSIFICATION = "TONNIS CLASSIFICATION"
        TREATMENT_RESPONSE_LI_RADS = "TREATMENT RESPONSE LI-RADS"
        TYRER_CUSICK_MODEL_RISK = "TYRER CUSICK MODEL RISK"
        T_SCORE = "T-SCORE"
        US_LI_RADS = "US LI-RADS"
        US_LI_RADS_VISUALIZATION_SCORE = "US LI-RADS VISUALIZATION SCORE"
        Z_SCORE = "Z-SCORE"


    class azure.healthinsights.radiologyinsights.models.ScoringAndAssessmentInference(RadiologyInsightsInference, discriminator='scoringAndAssessment'):
        category: Union[str, ScoringAndAssessmentCategoryType]
        category_description: str
        extension: list[Extension]
        kind: Literal[RadiologyInsightsInferenceType.SCORING_AND_ASSESSMENT]
        range_value: Optional[AssessmentValueRange]
        single_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Union[str, ScoringAndAssessmentCategoryType], 
                category_description: str, 
                extension: Optional[List[Extension]] = ..., 
                range_value: Optional[AssessmentValueRange] = ..., 
                single_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.SexMismatchInference(RadiologyInsightsInference, discriminator='sexMismatch'):
        extension: list[Extension]
        kind: Literal[RadiologyInsightsInferenceType.SEX_MISMATCH]
        sex_indication: CodeableConcept

        @overload
        def __init__(
                self, 
                *, 
                extension: Optional[List[Extension]] = ..., 
                sex_indication: CodeableConcept
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.healthinsights.radiologyinsights.models.SpecialtyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PATHOLOGY = "pathology"
        RADIOLOGY = "radiology"


    class azure.healthinsights.radiologyinsights.models.TimePeriod(_Model):
        end: Optional[datetime]
        start: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end: Optional[datetime] = ..., 
                start: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


```
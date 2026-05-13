```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.healthinsights.clinicalmatching

    class azure.healthinsights.clinicalmatching.ClinicalMatchingClient(ClinicalMatchingClientOperationsMixin): implements ContextManager 

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
        def begin_match_trials(
                self, 
                body: TrialMatcherData, 
                *, 
                content_type: str = "application/json", 
                repeatability_first_sent: Optional[datetime] = ..., 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[TrialMatcherResult]: ...

        @overload
        def begin_match_trials(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                repeatability_first_sent: Optional[datetime] = ..., 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[TrialMatcherResult]: ...

        @overload
        def begin_match_trials(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                repeatability_first_sent: Optional[datetime] = ..., 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[TrialMatcherResult]: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: Optional[bool] = ..., 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.healthinsights.clinicalmatching.aio

    class azure.healthinsights.clinicalmatching.aio.ClinicalMatchingClient(ClinicalMatchingClientOperationsMixin): implements AsyncContextManager 

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
        async def begin_match_trials(
                self, 
                body: TrialMatcherData, 
                *, 
                content_type: str = "application/json", 
                repeatability_first_sent: Optional[datetime] = ..., 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[TrialMatcherResult]: ...

        @overload
        async def begin_match_trials(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                repeatability_first_sent: Optional[datetime] = ..., 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[TrialMatcherResult]: ...

        @overload
        async def begin_match_trials(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                repeatability_first_sent: Optional[datetime] = ..., 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[TrialMatcherResult]: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.healthinsights.clinicalmatching.models

    class azure.healthinsights.clinicalmatching.models.AcceptedAge(Model):
        unit: Union[str, AgeUnit]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                unit: Union[str, AgeUnit], 
                value: float
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.AcceptedAgeRange(Model):
        maximum_age: Optional[AcceptedAge]
        minimum_age: Optional[AcceptedAge]

        @overload
        def __init__(
                self, 
                *, 
                maximum_age: Optional[AcceptedAge] = ..., 
                minimum_age: Optional[AcceptedAge] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.AgeUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAYS = "days"
        MONTHS = "months"
        YEARS = "years"


    class azure.healthinsights.clinicalmatching.models.AreaGeometry(Model):
        coordinates: List[float]
        type: Union[str, GeoJsonGeometryType]

        @overload
        def __init__(
                self, 
                *, 
                coordinates: List[float], 
                type: Union[str, GeoJsonGeometryType]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.AreaProperties(Model):
        radius: float
        sub_type: Union[str, GeoJsonPropertiesSubType]

        @overload
        def __init__(
                self, 
                *, 
                radius: float, 
                sub_type: Union[str, GeoJsonPropertiesSubType]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.ClinicalCodedElement(Model):
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


    class azure.healthinsights.clinicalmatching.models.ClinicalDocumentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSULTATION = "consultation"
        DISCHARGE_SUMMARY = "dischargeSummary"
        HISTORY_AND_PHYSICAL = "historyAndPhysical"
        IMAGING = "imaging"
        LABORATORY = "laboratory"
        PATHOLOGY = "pathology"
        PROCEDURE = "procedure"
        PROGRESS = "progress"


    class azure.healthinsights.clinicalmatching.models.ClinicalNoteEvidence(Model):
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


    class azure.healthinsights.clinicalmatching.models.ClinicalTrialAcceptedSex(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "all"
        FEMALE = "female"
        MALE = "male"


    class azure.healthinsights.clinicalmatching.models.ClinicalTrialDemographics(Model):
        accepted_age_range: Optional[AcceptedAgeRange]
        accepted_sex: Optional[Union[str, ClinicalTrialAcceptedSex]]

        @overload
        def __init__(
                self, 
                *, 
                accepted_age_range: Optional[AcceptedAgeRange] = ..., 
                accepted_sex: Optional[Union[str, ClinicalTrialAcceptedSex]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.ClinicalTrialDetails(Model):
        demographics: Optional[ClinicalTrialDemographics]
        eligibility_criteria_text: Optional[str]
        id: str
        metadata: ClinicalTrialMetadata

        @overload
        def __init__(
                self, 
                *, 
                demographics: Optional[ClinicalTrialDemographics] = ..., 
                eligibility_criteria_text: Optional[str] = ..., 
                id: str, 
                metadata: ClinicalTrialMetadata
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.ClinicalTrialMetadata(Model):
        conditions: List[str]
        contacts: Optional[List[ContactDetails]]
        facilities: Optional[List[ClinicalTrialResearchFacility]]
        phases: Optional[List[Union[str, ClinicalTrialPhase]]]
        recruitment_status: Optional[Union[str, ClinicalTrialRecruitmentStatus]]
        sponsors: Optional[List[str]]
        study_type: Optional[Union[str, ClinicalTrialStudyType]]

        @overload
        def __init__(
                self, 
                *, 
                conditions: List[str], 
                contacts: Optional[List[ContactDetails]] = ..., 
                facilities: Optional[List[ClinicalTrialResearchFacility]] = ..., 
                phases: Optional[List[Union[str, ClinicalTrialPhase]]] = ..., 
                recruitment_status: Optional[Union[str, ClinicalTrialRecruitmentStatus]] = ..., 
                sponsors: Optional[List[str]] = ..., 
                study_type: Optional[Union[str, ClinicalTrialStudyType]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.ClinicalTrialPhase(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EARLY_PHASE1 = "earlyPhase1"
        NOT_APPLICABLE = "notApplicable"
        PHASE1 = "phase1"
        PHASE2 = "phase2"
        PHASE3 = "phase3"
        PHASE4 = "phase4"


    class azure.healthinsights.clinicalmatching.models.ClinicalTrialPurpose(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC_SCIENCE = "basicScience"
        DEVICE_FEASIBILITY = "deviceFeasibility"
        DIAGNOSTIC = "diagnostic"
        HEALTH_SERVICES_RESEARCH = "healthServicesResearch"
        NOT_APPLICABLE = "notApplicable"
        OTHER = "other"
        PREVENTION = "prevention"
        SCREENING = "screening"
        SUPPORTIVE_CARE = "supportiveCare"
        TREATMENT = "treatment"


    class azure.healthinsights.clinicalmatching.models.ClinicalTrialRecruitmentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENROLLING_BY_INVITATION = "enrollingByInvitation"
        NOT_YET_RECRUITING = "notYetRecruiting"
        RECRUITING = "recruiting"
        UNKNOWN_STATUS = "unknownStatus"


    class azure.healthinsights.clinicalmatching.models.ClinicalTrialRegistryFilter(Model):
        conditions: Optional[List[str]]
        facility_areas: Optional[List[GeographicArea]]
        facility_locations: Optional[List[GeographicLocation]]
        facility_names: Optional[List[str]]
        ids: Optional[List[str]]
        phases: Optional[List[Union[str, ClinicalTrialPhase]]]
        purposes: Optional[List[Union[str, ClinicalTrialPurpose]]]
        recruitment_statuses: Optional[List[Union[str, ClinicalTrialRecruitmentStatus]]]
        sources: Optional[List[Union[str, ClinicalTrialSource]]]
        sponsors: Optional[List[str]]
        study_types: Optional[List[Union[str, ClinicalTrialStudyType]]]

        @overload
        def __init__(
                self, 
                *, 
                conditions: Optional[List[str]] = ..., 
                facility_areas: Optional[List[GeographicArea]] = ..., 
                facility_locations: Optional[List[GeographicLocation]] = ..., 
                facility_names: Optional[List[str]] = ..., 
                ids: Optional[List[str]] = ..., 
                phases: Optional[List[Union[str, ClinicalTrialPhase]]] = ..., 
                purposes: Optional[List[Union[str, ClinicalTrialPurpose]]] = ..., 
                recruitment_statuses: Optional[List[Union[str, ClinicalTrialRecruitmentStatus]]] = ..., 
                sources: Optional[List[Union[str, ClinicalTrialSource]]] = ..., 
                sponsors: Optional[List[str]] = ..., 
                study_types: Optional[List[Union[str, ClinicalTrialStudyType]]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.ClinicalTrialResearchFacility(Model):
        city: Optional[str]
        country_or_region: str
        name: str
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                city: Optional[str] = ..., 
                country_or_region: str, 
                name: str, 
                state: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.ClinicalTrialSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLINICALTRIALS_GOV = "clinicaltrials.gov"
        CUSTOM = "custom"


    class azure.healthinsights.clinicalmatching.models.ClinicalTrialStudyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXPANDED_ACCESS = "expandedAccess"
        INTERVENTIONAL = "interventional"
        OBSERVATIONAL = "observational"
        PATIENT_REGISTRIES = "patientRegistries"


    class azure.healthinsights.clinicalmatching.models.ClinicalTrials(Model):
        custom_trials: Optional[List[ClinicalTrialDetails]]
        registry_filters: Optional[List[ClinicalTrialRegistryFilter]]

        @overload
        def __init__(
                self, 
                *, 
                custom_trials: Optional[List[ClinicalTrialDetails]] = ..., 
                registry_filters: Optional[List[ClinicalTrialRegistryFilter]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.ContactDetails(Model):
        email: Optional[str]
        name: Optional[str]
        phone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                name: Optional[str] = ..., 
                phone: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.DocumentContent(Model):
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


    class azure.healthinsights.clinicalmatching.models.DocumentContentSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        REFERENCE = "reference"


    class azure.healthinsights.clinicalmatching.models.DocumentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DICOM = "dicom"
        FHIR_BUNDLE = "fhirBundle"
        GENOMIC_SEQUENCING = "genomicSequencing"
        NOTE = "note"


    class azure.healthinsights.clinicalmatching.models.Error(Model):
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


    class azure.healthinsights.clinicalmatching.models.ExtendedClinicalCodedElement(Model):
        category: Optional[str]
        code: str
        name: Optional[str]
        semantic_type: Optional[str]
        system: str
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                code: str, 
                name: Optional[str] = ..., 
                semantic_type: Optional[str] = ..., 
                system: str, 
                value: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.GeoJsonGeometryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        POINT = "Point"


    class azure.healthinsights.clinicalmatching.models.GeoJsonPropertiesSubType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CIRCLE = "Circle"


    class azure.healthinsights.clinicalmatching.models.GeoJsonType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FEATURE = "Feature"


    class azure.healthinsights.clinicalmatching.models.GeographicArea(Model):
        geometry: AreaGeometry
        properties: AreaProperties
        type: Union[str, GeoJsonType]

        @overload
        def __init__(
                self, 
                *, 
                geometry: AreaGeometry, 
                properties: AreaProperties, 
                type: Union[str, GeoJsonType]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.GeographicLocation(Model):
        city: Optional[str]
        country_or_region: str
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                city: Optional[str] = ..., 
                country_or_region: str, 
                state: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.InnerError(Model):
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


    class azure.healthinsights.clinicalmatching.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "failed"
        NOT_STARTED = "notStarted"
        PARTIALLY_COMPLETED = "partiallyCompleted"
        RUNNING = "running"
        SUCCEEDED = "succeeded"


    class azure.healthinsights.clinicalmatching.models.PatientDocument(Model):
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


    class azure.healthinsights.clinicalmatching.models.PatientInfo(Model):
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


    class azure.healthinsights.clinicalmatching.models.PatientInfoSex(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FEMALE = "female"
        MALE = "male"
        UNSPECIFIED = "unspecified"


    class azure.healthinsights.clinicalmatching.models.PatientRecord(Model):
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


    class azure.healthinsights.clinicalmatching.models.RepeatabilityResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "accepted"
        REJECTED = "rejected"


    class azure.healthinsights.clinicalmatching.models.TrialMatcherData(Model):
        configuration: Optional[TrialMatcherModelConfiguration]
        patients: List[PatientRecord]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[TrialMatcherModelConfiguration] = ..., 
                patients: List[PatientRecord]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.TrialMatcherInference(Model):
        confidence_score: Optional[float]
        description: Optional[str]
        evidence: Optional[List[TrialMatcherInferenceEvidence]]
        id: Optional[str]
        metadata: Optional[ClinicalTrialMetadata]
        source: Optional[Union[str, ClinicalTrialSource]]
        type: Union[str, TrialMatcherInferenceType]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                confidence_score: Optional[float] = ..., 
                description: Optional[str] = ..., 
                evidence: Optional[List[TrialMatcherInferenceEvidence]] = ..., 
                id: Optional[str] = ..., 
                metadata: Optional[ClinicalTrialMetadata] = ..., 
                source: Optional[Union[str, ClinicalTrialSource]] = ..., 
                type: Union[str, TrialMatcherInferenceType], 
                value: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.TrialMatcherInferenceEvidence(Model):
        eligibility_criteria_evidence: Optional[str]
        importance: Optional[float]
        patient_data_evidence: Optional[ClinicalNoteEvidence]
        patient_info_evidence: Optional[ClinicalCodedElement]

        @overload
        def __init__(
                self, 
                *, 
                eligibility_criteria_evidence: Optional[str] = ..., 
                importance: Optional[float] = ..., 
                patient_data_evidence: Optional[ClinicalNoteEvidence] = ..., 
                patient_info_evidence: Optional[ClinicalCodedElement] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.TrialMatcherInferenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TRIAL_ELIGIBILITY = "trialEligibility"


    class azure.healthinsights.clinicalmatching.models.TrialMatcherModelConfiguration(Model):
        clinical_trials: ClinicalTrials
        include_evidence: bool
        verbose: bool

        @overload
        def __init__(
                self, 
                *, 
                clinical_trials: ClinicalTrials, 
                include_evidence: bool = True, 
                verbose: bool = False
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.TrialMatcherPatientResult(Model):
        id: str
        inferences: List[TrialMatcherInference]
        needed_clinical_info: Optional[List[ExtendedClinicalCodedElement]]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                inferences: List[TrialMatcherInference], 
                needed_clinical_info: Optional[List[ExtendedClinicalCodedElement]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.healthinsights.clinicalmatching.models.TrialMatcherResult(Model):
        created_date_time: datetime
        errors: Optional[List[Error]]
        expiration_date_time: datetime
        job_id: str
        last_update_date_time: datetime
        results: Optional[TrialMatcherResults]
        status: Union[str, JobStatus]


    class azure.healthinsights.clinicalmatching.models.TrialMatcherResults(Model):
        knowledge_graph_last_update_date: Optional[date]
        model_version: str
        patients: List[TrialMatcherPatientResult]

        @overload
        def __init__(
                self, 
                *, 
                knowledge_graph_last_update_date: Optional[date] = ..., 
                model_version: str, 
                patients: List[TrialMatcherPatientResult]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


```
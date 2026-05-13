```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.formrecognizer

    class azure.ai.formrecognizer.AccountProperties:
        custom_model_count: int
        custom_model_limit: int

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> AccountProperties: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.AddressValue:
        city: Optional[str]
        city_district: Optional[str]
        country_region: Optional[str]
        house: Optional[str]
        house_number: Optional[str]
        level: Optional[str]
        po_box: Optional[str]
        postal_code: Optional[str]
        road: Optional[str]
        state: Optional[str]
        state_district: Optional[str]
        street_address: Optional[str]
        suburb: Optional[str]
        unit: Optional[str]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> AddressValue: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.AnalysisFeature(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BARCODES = "barcodes"
        FORMULAS = "formulas"
        KEY_VALUE_PAIRS = "keyValuePairs"
        LANGUAGES = "languages"
        OCR_HIGH_RESOLUTION = "ocrHighResolution"
        STYLE_FONT = "styleFont"


    class azure.ai.formrecognizer.AnalyzeResult:
        api_version: str
        content: str
        documents: Optional[List[AnalyzedDocument]]
        key_value_pairs: Optional[List[DocumentKeyValuePair]]
        languages: Optional[List[DocumentLanguage]]
        model_id: str
        pages: List[DocumentPage]
        paragraphs: Optional[List[DocumentParagraph]]
        styles: Optional[List[DocumentStyle]]
        tables: Optional[List[DocumentTable]]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> AnalyzeResult: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.AnalyzedDocument:
        bounding_regions: Optional[List[BoundingRegion]]
        confidence: float
        doc_type: str
        fields: Optional[Dict[str, DocumentField]]
        spans: List[DocumentSpan]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> AnalyzedDocument: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.BlobFileListSource:
        container_url: str
        file_list: str

        def __init__(
                self, 
                container_url: str, 
                file_list: str
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> BlobFileListSource: ...

        def to_dict(self) -> Dict[str, Any]: ...


    class azure.ai.formrecognizer.BlobSource:
        container_url: str
        prefix: Optional[str]

        def __init__(
                self, 
                container_url: str, 
                *, 
                prefix: Optional[str] = ...
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> BlobSource: ...

        def to_dict(self) -> Dict[str, Any]: ...


    class azure.ai.formrecognizer.BoundingRegion:
        page_number: int
        polygon: Sequence[Point]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> BoundingRegion: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.ClassifierDocumentTypeDetails:
        source: Union[BlobSource, BlobFileListSource]
        source_kind: Literal["azureBlob", "azureBlobFileList"]

        def __init__(self, source: Union[BlobSource, BlobFileListSource]) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> ClassifierDocumentTypeDetails: ...

        def to_dict(self) -> Dict[str, Any]: ...


    class azure.ai.formrecognizer.CurrencyValue:
        amount: float
        code: Optional[str]
        symbol: Optional[str]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self): ...

        @classmethod
        def from_dict(cls, data: Dict) -> CurrencyValue: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.CustomDocumentModelsDetails:
        count: int
        limit: int

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> CustomDocumentModelsDetails: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.CustomFormModel:
        errors: List[FormRecognizerError]
        model_id: str
        model_name: str
        properties: CustomFormModelProperties
        status: str
        submodels: List[CustomFormSubmodel]
        training_completed_on: datetime
        training_documents: List[TrainingDocumentInfo]
        training_started_on: datetime

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> CustomFormModel: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.CustomFormModelField:
        accuracy: float
        label: str
        name: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> CustomFormModelField: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.CustomFormModelInfo:
        model_id: str
        model_name: str
        properties: CustomFormModelProperties
        status: str
        training_completed_on: datetime
        training_started_on: datetime

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> CustomFormModelInfo: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.CustomFormModelProperties:
        is_composed_model: bool

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> CustomFormModelProperties: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.CustomFormModelStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "creating"
        INVALID = "invalid"
        READY = "ready"


    class azure.ai.formrecognizer.CustomFormSubmodel:
        accuracy: float
        fields: Dict[str, CustomFormModelField]
        form_type: str
        model_id: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> CustomFormSubmodel: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentAnalysisApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2022_08_31 = "2022-08-31"
        V2023_07_31 = "2023-07-31"


    class azure.ai.formrecognizer.DocumentAnalysisClient(FormRecognizerClientBase): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Union[str, DocumentAnalysisApiVersion] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def begin_analyze_document(
                self, 
                model_id: str, 
                document: Union[bytes, IO[bytes]], 
                *, 
                features: list[str] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[AnalyzeResult]: ...

        @distributed_trace
        def begin_analyze_document_from_url(
                self, 
                model_id: str, 
                document_url: str, 
                *, 
                features: list[str] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[AnalyzeResult]: ...

        @distributed_trace
        def begin_classify_document(
                self, 
                classifier_id: str, 
                document: Union[bytes, IO[bytes]], 
                **kwargs: Any
            ) -> LROPoller[AnalyzeResult]: ...

        @distributed_trace
        def begin_classify_document_from_url(
                self, 
                classifier_id: str, 
                document_url: str, 
                **kwargs: Any
            ) -> LROPoller[AnalyzeResult]: ...

        def close(self) -> None: ...

        @distributed_trace
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs
            ) -> HttpResponse: ...


    class azure.ai.formrecognizer.DocumentAnalysisError:
        code: str
        details: Optional[List[DocumentAnalysisError]]
        innererror: Optional[DocumentAnalysisInnerError]
        message: str
        target: Optional[str]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentAnalysisError: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentAnalysisInnerError:
        code: str
        innererror: Optional[DocumentAnalysisInnerError]
        message: Optional[str]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentAnalysisInnerError: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentBarcode:
        confidence: float
        kind: Literal["QRCode", "PDF417", "UPCA", "UPCE", "Code39", "Code128", "EAN8", "EAN13", "DataBar", "Code93", "Codabar", "DataBarExpanded", "ITF", "MicroQRCode", "Aztec", "DataMatrix", "MaxiCode"]
        polygon: Sequence[Point]
        span: DocumentSpan
        value: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> DocumentBarcode: ...

        def to_dict(self) -> Dict[str, Any]: ...


    class azure.ai.formrecognizer.DocumentClassifierDetails:
        api_version: str
        classifier_id: str
        created_on: datetime
        description: Optional[str]
        doc_types: Mapping[str, ClassifierDocumentTypeDetails]
        expires_on: Optional[datetime]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> DocumentClassifierDetails: ...

        def to_dict(self) -> Dict[str, Any]: ...


    class azure.ai.formrecognizer.DocumentField:
        bounding_regions: Optional[List[BoundingRegion]]
        confidence: float
        content: Optional[str]
        spans: Optional[List[DocumentSpan]]
        value: Optional[Union[str, int, float, bool, date, time, CurrencyValue, AddressValue, Dict[str, DocumentField], List[DocumentField]]]
        value_type: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentField: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentFormula:
        confidence: float
        kind: Literal["inline", "display"]
        polygon: Sequence[Point]
        span: DocumentSpan
        value: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> DocumentFormula: ...

        def to_dict(self) -> Dict[str, Any]: ...


    class azure.ai.formrecognizer.DocumentKeyValueElement:
        bounding_regions: Optional[List[BoundingRegion]]
        content: str
        spans: List[DocumentSpan]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentKeyValueElement: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentKeyValuePair:
        confidence: float
        key: DocumentKeyValueElement
        value: Optional[DocumentKeyValueElement]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentKeyValuePair: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentLanguage:
        confidence: float
        locale: str
        spans: List[DocumentSpan]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentLanguage: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentLine:
        content: str
        polygon: Sequence[Point]
        spans: List[DocumentSpan]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentLine: ...

        def get_words(self) -> Iterable[DocumentWord]: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentModelAdministrationClient(FormRecognizerClientBase): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Union[str, DocumentAnalysisApiVersion] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def begin_build_document_classifier(
                self, 
                doc_types: Mapping[str, ClassifierDocumentTypeDetails], 
                *, 
                classifier_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                **kwargs: Any
            ) -> DocumentModelAdministrationLROPoller[DocumentClassifierDetails]: ...

        @overload
        def begin_build_document_model(
                self, 
                build_mode: Union[str, ModelBuildMode], 
                *, 
                blob_container_url: str, 
                description: Optional[str] = ..., 
                model_id: Optional[str] = ..., 
                prefix: Optional[str] = ..., 
                tags: Optional[Mapping[str, str]] = ..., 
                **kwargs: Any
            ) -> DocumentModelAdministrationLROPoller[DocumentModelDetails]: ...

        @overload
        def begin_build_document_model(
                self, 
                build_mode: Union[str, ModelBuildMode], 
                *, 
                blob_container_url: str, 
                description: Optional[str] = ..., 
                file_list: str, 
                model_id: Optional[str] = ..., 
                tags: Optional[Mapping[str, str]] = ..., 
                **kwargs: Any
            ) -> DocumentModelAdministrationLROPoller[DocumentModelDetails]: ...

        @distributed_trace
        def begin_compose_document_model(
                self, 
                component_model_ids: List[str], 
                *, 
                description: Optional[str] = ..., 
                model_id: Optional[str] = ..., 
                tags: dict[str, str] = ..., 
                **kwargs: Any
            ) -> DocumentModelAdministrationLROPoller[DocumentModelDetails]: ...

        @distributed_trace
        def begin_copy_document_model_to(
                self, 
                model_id: str, 
                target: TargetAuthorization, 
                **kwargs: Any
            ) -> DocumentModelAdministrationLROPoller[DocumentModelDetails]: ...

        def close(self) -> None: ...

        @distributed_trace
        def delete_document_classifier(
                self, 
                classifier_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_document_model(
                self, 
                model_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_copy_authorization(
                self, 
                *, 
                description: Optional[str] = ..., 
                model_id: Optional[str] = ..., 
                tags: dict[str, str] = ..., 
                **kwargs: Any
            ) -> TargetAuthorization: ...

        def get_document_analysis_client(self, **kwargs: Any) -> DocumentAnalysisClient: ...

        @distributed_trace
        def get_document_classifier(
                self, 
                classifier_id: str, 
                **kwargs: Any
            ) -> DocumentClassifierDetails: ...

        @distributed_trace
        def get_document_model(
                self, 
                model_id: str, 
                **kwargs: Any
            ) -> DocumentModelDetails: ...

        @distributed_trace
        def get_operation(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationDetails: ...

        @distributed_trace
        def get_resource_details(self, **kwargs: Any) -> ResourceDetails: ...

        @distributed_trace
        def list_document_classifiers(self, **kwargs: Any) -> ItemPaged[DocumentClassifierDetails]: ...

        @distributed_trace
        def list_document_models(self, **kwargs: Any) -> ItemPaged[DocumentModelSummary]: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> ItemPaged[OperationSummary]: ...

        @distributed_trace
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs
            ) -> HttpResponse: ...


    @runtime_checkable
    class azure.ai.formrecognizer.DocumentModelAdministrationLROPoller(Protocol[PollingReturnType_co]):
        property details: Mapping[str, Any]    # Read-only

        def add_done_callback(self, func: Callable) -> None: ...

        def continuation_token(self) -> str: ...

        def done(self) -> bool: ...

        def polling_method(self) -> PollingMethod[PollingReturnType_co]: ...

        def remove_done_callback(self, func: Callable) -> None: ...

        def result(self, timeout: Optional[int] = None) -> PollingReturnType_co: ...

        def status(self) -> str: ...

        def wait(self, timeout: Optional[float] = None) -> None: ...


    class azure.ai.formrecognizer.DocumentModelDetails(DocumentModelSummary):
        api_version: Optional[str]
        created_on: datetime
        description: Optional[str]
        doc_types: Optional[Dict[str, DocumentTypeDetails]]
        expires_on: Optional[datetime]
        model_id: str
        tags: Optional[Dict[str, str]]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> DocumentModelDetails: ...

        def to_dict(self) -> Dict[str, Any]: ...


    class azure.ai.formrecognizer.DocumentModelSummary:
        api_version: Optional[str]
        created_on: datetime
        description: Optional[str]
        expires_on: Optional[datetime]
        model_id: str
        tags: Optional[Dict[str, str]]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> DocumentModelSummary: ...

        def to_dict(self) -> Dict[str, Any]: ...


    class azure.ai.formrecognizer.DocumentPage:
        angle: Optional[float]
        barcodes: List[DocumentBarcode]
        formulas: List[DocumentFormula]
        height: Optional[float]
        lines: List[DocumentLine]
        page_number: int
        selection_marks: List[DocumentSelectionMark]
        spans: List[DocumentSpan]
        unit: Optional[str]
        width: Optional[float]
        words: List[DocumentWord]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentPage: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentParagraph:
        bounding_regions: Optional[List[BoundingRegion]]
        content: str
        role: Optional[str]
        spans: List[DocumentSpan]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentParagraph: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentSelectionMark:
        confidence: float
        polygon: Sequence[Point]
        span: DocumentSpan
        state: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentSelectionMark: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentSpan:
        length: int
        offset: int

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentSpan: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentStyle:
        background_color: Optional[str]
        color: Optional[str]
        confidence: float
        font_style: Optional[str]
        font_weight: Optional[str]
        is_handwritten: Optional[bool]
        similar_font_family: Optional[str]
        spans: List[DocumentSpan]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentStyle: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentTable:
        bounding_regions: Optional[List[BoundingRegion]]
        cells: List[DocumentTableCell]
        column_count: int
        row_count: int
        spans: List[DocumentSpan]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentTable: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentTableCell:
        bounding_regions: Optional[List[BoundingRegion]]
        column_index: int
        column_span: Optional[int]
        content: str
        kind: Optional[str]
        row_index: int
        row_span: Optional[int]
        spans: List[DocumentSpan]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentTableCell: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentTypeDetails:
        build_mode: Optional[str]
        description: Optional[str]
        field_confidence: Optional[Dict[str, float]]
        field_schema: Dict[str, Any]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentTypeDetails: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.DocumentWord:
        confidence: float
        content: str
        polygon: Sequence[Point]
        span: DocumentSpan

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> DocumentWord: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.FieldData:
        bounding_box: List[Point]
        field_elements: List[Union[FormElement, FormWord, FormLine, FormSelectionMark]]
        page_number: int
        text: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> FieldData: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.FieldValueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNTRY_REGION = "countryRegion"
        DATE = "date"
        DICTIONARY = "dictionary"
        FLOAT = "float"
        INTEGER = "integer"
        LIST = "list"
        PHONE_NUMBER = "phoneNumber"
        SELECTION_MARK = "selectionMark"
        STRING = "string"
        TIME = "time"


    class azure.ai.formrecognizer.FormContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_PDF = "application/pdf"
        IMAGE_BMP = "image/bmp"
        IMAGE_JPEG = "image/jpeg"
        IMAGE_PNG = "image/png"
        IMAGE_TIFF = "image/tiff"


    class azure.ai.formrecognizer.FormElement:
        bounding_box: List[Point]
        kind: str
        page_number: int
        text: str

        def __init__(self, **kwargs: Any) -> None: ...

        @classmethod
        def from_dict(cls, data: Dict) -> FormElement: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.FormField:
        confidence: float
        label_data: FieldData
        name: str
        value: Union[str, int, float, date, time, Dict[str, FormField], List[FormField]]
        value_data: FieldData
        value_type: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> FormField: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.FormLine(FormElement):
        appearance: TextAppearance
        bounding_box: List[Point]
        kind: str
        page_number: int
        text: str
        words: List[FormWord]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> FormLine: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.FormPage:
        height: float
        lines: List[FormLine]
        page_number: int
        selection_marks: List[FormSelectionMark]
        tables: List[FormTable]
        text_angle: float
        unit: str
        width: float

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> FormPage: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.FormPageRange(namedtuple(FormPageRange, first_page_number last_page_number)):
        first_page_number: int
        last_page_number: int

        def __new__(
                cls, 
                first_page_number: int, 
                last_page_number: int
            ) -> FormPageRange: ...

        @classmethod
        def from_dict(cls, data: Dict) -> FormPageRange: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.FormRecognizerApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2_0 = "2.0"
        V2_1 = "2.1"


    class azure.ai.formrecognizer.FormRecognizerClient(FormRecognizerClientBase): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Union[str, FormRecognizerApiVersion] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def begin_recognize_business_cards(
                self, 
                business_card: Union[bytes, IO[bytes]], 
                *, 
                content_type: Union[str, FormContentType] = ..., 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[List[RecognizedForm]]: ...

        @distributed_trace
        def begin_recognize_business_cards_from_url(
                self, 
                business_card_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[List[RecognizedForm]]: ...

        @distributed_trace
        def begin_recognize_content(
                self, 
                form: Union[bytes, IO[bytes]], 
                *, 
                content_type: Union[str, FormContentType] = ..., 
                continuation_token: Optional[str] = ..., 
                language: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                reading_order: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[List[FormPage]]: ...

        @distributed_trace
        def begin_recognize_content_from_url(
                self, 
                form_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                language: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                reading_order: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[List[FormPage]]: ...

        @distributed_trace
        def begin_recognize_custom_forms(
                self, 
                model_id: str, 
                form: Union[bytes, IO[bytes]], 
                *, 
                content_type: Union[str, FormContentType] = ..., 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[List[RecognizedForm]]: ...

        @distributed_trace
        def begin_recognize_custom_forms_from_url(
                self, 
                model_id: str, 
                form_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[List[RecognizedForm]]: ...

        @distributed_trace
        def begin_recognize_identity_documents(
                self, 
                identity_document: Union[bytes, IO[bytes]], 
                *, 
                content_type: Union[str, FormContentType] = ..., 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[List[RecognizedForm]]: ...

        @distributed_trace
        def begin_recognize_identity_documents_from_url(
                self, 
                identity_document_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[List[RecognizedForm]]: ...

        @distributed_trace
        def begin_recognize_invoices(
                self, 
                invoice: Union[bytes, IO[bytes]], 
                *, 
                content_type: Union[str, FormContentType] = ..., 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[List[RecognizedForm]]: ...

        @distributed_trace
        def begin_recognize_invoices_from_url(
                self, 
                invoice_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[List[RecognizedForm]]: ...

        @distributed_trace
        def begin_recognize_receipts(
                self, 
                receipt: Union[bytes, IO[bytes]], 
                *, 
                content_type: Union[str, FormContentType] = ..., 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[List[RecognizedForm]]: ...

        @distributed_trace
        def begin_recognize_receipts_from_url(
                self, 
                receipt_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[List[RecognizedForm]]: ...

        def close(self) -> None: ...

        @distributed_trace
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs
            ) -> HttpResponse: ...


    class azure.ai.formrecognizer.FormRecognizerError:
        code: str
        message: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> FormRecognizerError: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.FormSelectionMark(FormElement):
        bounding_box: List[Point]
        confidence: float
        kind: str
        page_number: int
        state: str
        text: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> FormSelectionMark: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.FormTable:
        bounding_box: List[Point]
        cells: List[FormTableCell]
        column_count: int
        page_number: int
        row_count: int

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> FormTable: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.FormTableCell:
        bounding_box: List[Point]
        column_index: int
        column_span: int
        confidence: float
        field_elements: List[Union[FormElement, FormWord, FormLine, FormSelectionMark]]
        is_footer: bool
        is_header: bool
        page_number: int
        row_index: int
        row_span: int
        text: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> FormTableCell: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.FormTrainingClient(FormRecognizerClientBase): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Union[str, FormRecognizerApiVersion] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def begin_copy_model(
                self, 
                model_id: str, 
                target: Dict[str, Union[str, int]], 
                *, 
                continuation_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[CustomFormModelInfo]: ...

        @distributed_trace
        def begin_create_composed_model(
                self, 
                model_ids: List[str], 
                *, 
                continuation_token: Optional[str] = ..., 
                model_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[CustomFormModel]: ...

        @distributed_trace
        def begin_training(
                self, 
                training_files_url: str, 
                use_training_labels: bool = False, 
                *, 
                continuation_token: Optional[str] = ..., 
                include_subfolders: Optional[bool] = ..., 
                model_name: Optional[str] = ..., 
                prefix: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[CustomFormModel]: ...

        def close(self) -> None: ...

        @distributed_trace
        def delete_model(
                self, 
                model_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_account_properties(self, **kwargs: Any) -> AccountProperties: ...

        @distributed_trace
        def get_copy_authorization(
                self, 
                resource_id: str, 
                resource_region: str, 
                **kwargs: Any
            ) -> Dict[str, Union[str, int]]: ...

        @distributed_trace
        def get_custom_model(
                self, 
                model_id: str, 
                **kwargs: Any
            ) -> CustomFormModel: ...

        def get_form_recognizer_client(self, **kwargs: Any) -> FormRecognizerClient: ...

        @distributed_trace
        def list_custom_models(self, **kwargs: Any) -> ItemPaged[CustomFormModelInfo]: ...

        @distributed_trace
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs
            ) -> HttpResponse: ...


    class azure.ai.formrecognizer.FormWord(FormElement):
        bounding_box: List[Point]
        confidence: float
        kind: str
        page_number: int
        text: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> FormWord: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.LengthUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INCH = "inch"
        PIXEL = "pixel"


    class azure.ai.formrecognizer.ModelBuildMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NEURAL = "neural"
        TEMPLATE = "template"


    class azure.ai.formrecognizer.OperationDetails(OperationSummary):
        api_version: Optional[str]
        created_on: datetime
        error: Optional[DocumentAnalysisError]
        kind: str
        last_updated_on: datetime
        operation_id: str
        percent_completed: Optional[int]
        resource_location: str
        result: Optional[Union[DocumentModelDetails, DocumentClassifierDetails]]
        status: str
        tags: Optional[Dict[str, str]]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> OperationDetails: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.OperationSummary:
        api_version: Optional[str]
        created_on: datetime
        kind: str
        last_updated_on: datetime
        operation_id: str
        percent_completed: Optional[int]
        resource_location: str
        status: str
        tags: Optional[Dict[str, str]]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> OperationSummary: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.Point(namedtuple(Point, x y)):
        x: float
        y: float

        def __new__(
                cls, 
                x: float, 
                y: float
            ) -> Point: ...

        @classmethod
        def from_dict(cls, data: Dict) -> Point: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.QuotaDetails:
        quota: int
        quota_resets_on: datetime
        used: int

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> QuotaDetails: ...

        def to_dict(self) -> Dict[str, Any]: ...


    class azure.ai.formrecognizer.RecognizedForm:
        fields: Dict[str, FormField]
        form_type: str
        form_type_confidence: int
        model_id: str
        page_range: FormPageRange
        pages: List[FormPage]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> RecognizedForm: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.ResourceDetails:
        custom_document_models: CustomDocumentModelsDetails
        neural_document_model_quota: Optional[QuotaDetails]

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> ResourceDetails: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.TextAppearance:
        style_confidence: float
        style_name: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> TextAppearance: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.TrainingDocumentInfo:
        errors: List[FormRecognizerError]
        model_id: str
        name: str
        page_count: int
        status: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: Dict) -> TrainingDocumentInfo: ...

        def to_dict(self) -> Dict: ...


    class azure.ai.formrecognizer.TrainingStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "failed"
        PARTIALLY_SUCCEEDED = "partiallySucceeded"
        SUCCEEDED = "succeeded"


namespace azure.ai.formrecognizer.aio

    @runtime_checkable
    class azure.ai.formrecognizer.aio.AsyncDocumentModelAdministrationLROPoller(Protocol[PollingReturnType_co]):
        property details: Mapping[str, Any]    # Read-only

        def continuation_token(self) -> str: ...

        def done(self) -> bool: ...

        def polling_method(self) -> AsyncPollingMethod[PollingReturnType_co]: ...

        async def result(self) -> PollingReturnType_co: ...

        def status(self) -> str: ...

        async def wait(self) -> None: ...


    class azure.ai.formrecognizer.aio.DocumentAnalysisClient(FormRecognizerClientBaseAsync): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Union[str, DocumentAnalysisApiVersion] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def begin_analyze_document(
                self, 
                model_id: str, 
                document: Union[bytes, IO[bytes]], 
                *, 
                features: list[str] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AnalyzeResult]: ...

        @distributed_trace_async
        async def begin_analyze_document_from_url(
                self, 
                model_id: str, 
                document_url: str, 
                *, 
                features: list[str] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AnalyzeResult]: ...

        @distributed_trace_async
        async def begin_classify_document(
                self, 
                classifier_id: str, 
                document: Union[bytes, IO[bytes]], 
                **kwargs: Any
            ) -> AsyncLROPoller[AnalyzeResult]: ...

        @distributed_trace_async
        async def begin_classify_document_from_url(
                self, 
                classifier_id: str, 
                document_url: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[AnalyzeResult]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs
            ) -> AsyncHttpResponse: ...


    class azure.ai.formrecognizer.aio.DocumentModelAdministrationClient(FormRecognizerClientBaseAsync): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Union[str, DocumentAnalysisApiVersion] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def begin_build_document_classifier(
                self, 
                doc_types: Mapping[str, ClassifierDocumentTypeDetails], 
                *, 
                classifier_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncDocumentModelAdministrationLROPoller[DocumentClassifierDetails]: ...

        @overload
        async def begin_build_document_model(
                self, 
                build_mode: Union[str, ModelBuildMode], 
                *, 
                blob_container_url: str, 
                description: Optional[str] = ..., 
                model_id: Optional[str] = ..., 
                prefix: Optional[str] = ..., 
                tags: Optional[Mapping[str, str]] = ..., 
                **kwargs: Any
            ) -> AsyncDocumentModelAdministrationLROPoller[DocumentModelDetails]: ...

        @overload
        async def begin_build_document_model(
                self, 
                build_mode: Union[str, ModelBuildMode], 
                *, 
                blob_container_url: str, 
                description: Optional[str] = ..., 
                file_list: str, 
                model_id: Optional[str] = ..., 
                tags: Optional[Mapping[str, str]] = ..., 
                **kwargs: Any
            ) -> AsyncDocumentModelAdministrationLROPoller[DocumentModelDetails]: ...

        @distributed_trace_async
        async def begin_compose_document_model(
                self, 
                component_model_ids: List[str], 
                *, 
                description: Optional[str] = ..., 
                model_id: Optional[str] = ..., 
                tags: dict[str, str] = ..., 
                **kwargs: Any
            ) -> AsyncDocumentModelAdministrationLROPoller[DocumentModelDetails]: ...

        @distributed_trace_async
        async def begin_copy_document_model_to(
                self, 
                model_id: str, 
                target: TargetAuthorization, 
                **kwargs: Any
            ) -> AsyncDocumentModelAdministrationLROPoller[DocumentModelDetails]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def delete_document_classifier(
                self, 
                classifier_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_document_model(
                self, 
                model_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_copy_authorization(
                self, 
                *, 
                description: Optional[str] = ..., 
                model_id: Optional[str] = ..., 
                tags: dict[str, str] = ..., 
                **kwargs: Any
            ) -> TargetAuthorization: ...

        def get_document_analysis_client(self, **kwargs: Any) -> DocumentAnalysisClient: ...

        @distributed_trace_async
        async def get_document_classifier(
                self, 
                classifier_id: str, 
                **kwargs: Any
            ) -> DocumentClassifierDetails: ...

        @distributed_trace_async
        async def get_document_model(
                self, 
                model_id: str, 
                **kwargs: Any
            ) -> DocumentModelDetails: ...

        @distributed_trace_async
        async def get_operation(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationDetails: ...

        @distributed_trace_async
        async def get_resource_details(self, **kwargs: Any) -> ResourceDetails: ...

        @distributed_trace
        def list_document_classifiers(self, **kwargs: Any) -> AsyncItemPaged[DocumentClassifierDetails]: ...

        @distributed_trace
        def list_document_models(self, **kwargs: Any) -> AsyncItemPaged[DocumentModelSummary]: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> AsyncItemPaged[OperationSummary]: ...

        @distributed_trace_async
        async def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs
            ) -> AsyncHttpResponse: ...


    class azure.ai.formrecognizer.aio.FormRecognizerClient(FormRecognizerClientBaseAsync): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Union[str, FormRecognizerApiVersion] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def begin_recognize_business_cards(
                self, 
                business_card: Union[bytes, IO[bytes]], 
                *, 
                content_type: Union[str, FormContentType] = ..., 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[List[RecognizedForm]]: ...

        @distributed_trace_async
        async def begin_recognize_business_cards_from_url(
                self, 
                business_card_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[List[RecognizedForm]]: ...

        @distributed_trace_async
        async def begin_recognize_content(
                self, 
                form: Union[bytes, IO[bytes]], 
                *, 
                content_type: Union[str, FormContentType] = ..., 
                continuation_token: Optional[str] = ..., 
                language: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                reading_order: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[List[FormPage]]: ...

        @distributed_trace_async
        async def begin_recognize_content_from_url(
                self, 
                form_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                language: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                reading_order: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[List[FormPage]]: ...

        @distributed_trace_async
        async def begin_recognize_custom_forms(
                self, 
                model_id: str, 
                form: Union[bytes, IO[bytes]], 
                *, 
                content_type: Union[str, FormContentType] = ..., 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[List[RecognizedForm]]: ...

        @distributed_trace_async
        async def begin_recognize_custom_forms_from_url(
                self, 
                model_id: str, 
                form_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[List[RecognizedForm]]: ...

        @distributed_trace_async
        async def begin_recognize_identity_documents(
                self, 
                identity_document: Union[bytes, IO[bytes]], 
                *, 
                content_type: Union[str, FormContentType] = ..., 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[List[RecognizedForm]]: ...

        @distributed_trace_async
        async def begin_recognize_identity_documents_from_url(
                self, 
                identity_document_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[List[RecognizedForm]]: ...

        @distributed_trace_async
        async def begin_recognize_invoices(
                self, 
                invoice: Union[bytes, IO[bytes]], 
                *, 
                content_type: Union[str, FormContentType] = ..., 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[List[RecognizedForm]]: ...

        @distributed_trace_async
        async def begin_recognize_invoices_from_url(
                self, 
                invoice_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[List[RecognizedForm]]: ...

        @distributed_trace_async
        async def begin_recognize_receipts(
                self, 
                receipt: Union[bytes, IO[bytes]], 
                *, 
                content_type: Union[str, FormContentType] = ..., 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[List[RecognizedForm]]: ...

        @distributed_trace_async
        async def begin_recognize_receipts_from_url(
                self, 
                receipt_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                include_field_elements: Optional[bool] = ..., 
                locale: Optional[str] = ..., 
                pages: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[List[RecognizedForm]]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs
            ) -> AsyncHttpResponse: ...


    class azure.ai.formrecognizer.aio.FormTrainingClient(FormRecognizerClientBaseAsync): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Union[str, FormRecognizerApiVersion] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def begin_copy_model(
                self, 
                model_id: str, 
                target: Dict[str, Union[str, int]], 
                *, 
                continuation_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomFormModelInfo]: ...

        @distributed_trace_async
        async def begin_create_composed_model(
                self, 
                model_ids: List[str], 
                *, 
                continuation_token: Optional[str] = ..., 
                model_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomFormModel]: ...

        @distributed_trace_async
        async def begin_training(
                self, 
                training_files_url: str, 
                use_training_labels: bool = False, 
                *, 
                continuation_token: Optional[str] = ..., 
                include_subfolders: Optional[bool] = ..., 
                model_name: Optional[str] = ..., 
                prefix: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomFormModel]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def delete_model(
                self, 
                model_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_account_properties(self, **kwargs: Any) -> AccountProperties: ...

        @distributed_trace_async
        async def get_copy_authorization(
                self, 
                resource_id: str, 
                resource_region: str, 
                **kwargs: Any
            ) -> Dict[str, Union[str, int]]: ...

        @distributed_trace_async
        async def get_custom_model(
                self, 
                model_id: str, 
                **kwargs: Any
            ) -> CustomFormModel: ...

        def get_form_recognizer_client(self, **kwargs: Any) -> FormRecognizerClient: ...

        @distributed_trace
        def list_custom_models(self, **kwargs: Any) -> AsyncItemPaged[CustomFormModelInfo]: ...

        @distributed_trace_async
        async def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs
            ) -> AsyncHttpResponse: ...


```
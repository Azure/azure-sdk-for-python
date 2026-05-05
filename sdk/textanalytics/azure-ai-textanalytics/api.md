```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.textanalytics

    class azure.ai.textanalytics.AbstractiveSummary(DictMixin):
        contexts: List[SummaryContext]
        text: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.AbstractiveSummaryAction(DictMixin):
        disable_service_logs: Optional[bool]
        model_version: Optional[str]
        sentence_count: Optional[int]
        string_index_type: Optional[str]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                sentence_count: Optional[int] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.AbstractiveSummaryResult(DictMixin):
        id: str
        is_error: Literal[False] = False
        kind: Literal["AbstractiveSummarization"] = AbstractiveSummarization
        statistics: Optional[TextDocumentStatistics]
        summaries: List[AbstractiveSummary]
        warnings: List[TextAnalyticsWarning]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.AnalyzeActionsLROPoller(LROPoller[PollingReturnType_co]):
        property details: Mapping[str, Any]    # Read-only

        def __getattr__(self, item: str) -> Any: ...

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: AnalyzeActionsLROPollingMethod, 
                continuation_token: str, 
                **kwargs: Any
            ) -> AnalyzeActionsLROPoller: ...

        @distributed_trace
        def cancel(self) -> None: ...

        def polling_method(self) -> AnalyzeActionsLROPollingMethod: ...


    class azure.ai.textanalytics.AnalyzeHealthcareEntitiesAction(DictMixin):
        disable_service_logs: Optional[bool]
        model_version: Optional[str]
        string_index_type: Optional[str]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.AnalyzeHealthcareEntitiesLROPoller(LROPoller[PollingReturnType_co]):
        property details: Mapping[str, Any]    # Read-only

        def __getattr__(self, item: str) -> Any: ...

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: AnalyzeHealthcareEntitiesLROPollingMethod, 
                continuation_token: str, 
                **kwargs: Any
            ) -> AnalyzeHealthcareEntitiesLROPoller: ...

        @distributed_trace
        def cancel(
                self, 
                *, 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        def polling_method(self) -> AnalyzeHealthcareEntitiesLROPollingMethod: ...


    class azure.ai.textanalytics.AnalyzeHealthcareEntitiesResult(DictMixin):
        entities: List[HealthcareEntity]
        entity_relations: List[HealthcareRelation]
        id: str
        is_error: Literal[False] = False
        kind: Literal["Healthcare"] = Healthcare
        statistics: Optional[TextDocumentStatistics]
        warnings: List[TextAnalyticsWarning]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.AnalyzeSentimentAction(DictMixin):
        disable_service_logs: Optional[bool]
        model_version: Optional[str]
        show_opinion_mining: Optional[bool]
        string_index_type: Optional[str]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                show_opinion_mining: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.AnalyzeSentimentResult(DictMixin):
        confidence_scores: SentimentConfidenceScores
        id: str
        is_error: Literal[False] = False
        kind: Literal["SentimentAnalysis"] = SentimentAnalysis
        sentences: List[SentenceSentiment]
        sentiment: str
        statistics: Optional[TextDocumentStatistics]
        warnings: List[TextAnalyticsWarning]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.AssessmentSentiment(DictMixin):
        confidence_scores: SentimentConfidenceScores
        is_negated: bool
        length: int
        offset: int
        sentiment: str
        text: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.CategorizedEntity(DictMixin):
        category: str
        confidence_score: float
        length: int
        offset: int
        subcategory: Optional[str]
        text: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.ClassificationCategory(DictMixin):
        category: str
        confidence_score: float

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.ClassifyDocumentResult(DictMixin):
        classifications: List[ClassificationCategory]
        id: str
        is_error: Literal[False] = False
        kind: Literal["CustomDocumentClassification"] = CustomDocumentClassification
        statistics: Optional[TextDocumentStatistics]
        warnings: List[TextAnalyticsWarning]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.DetectLanguageInput(LanguageInput):
        country_hint: Optional[str]
        id: str
        text: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                country_hint: Optional[str] = ..., 
                id: str, 
                text: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other): ...

        def __repr__(self) -> str: ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.ai.textanalytics.DetectLanguageResult(DictMixin):
        id: str
        is_error: Literal[False] = False
        kind: Literal["LanguageDetection"] = LanguageDetection
        primary_language: DetectedLanguage
        statistics: Optional[TextDocumentStatistics]
        warnings: List[TextAnalyticsWarning]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.DetectedLanguage(DictMixin):
        confidence_score: float
        iso6391_name: str
        name: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.DocumentError(DictMixin):
        error: TextAnalyticsError
        id: str
        is_error: Literal[True] = True
        kind: Literal["DocumentError"] = DocumentError

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getattr__(self, attr: str) -> Any: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.EntityAssociation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OTHER = "other"
        SUBJECT = "subject"


    class azure.ai.textanalytics.EntityCertainty(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NEGATIVE = "negative"
        NEGATIVE_POSSIBLE = "negativePossible"
        NEUTRAL_POSSIBLE = "neutralPossible"
        POSITIVE = "positive"
        POSITIVE_POSSIBLE = "positivePossible"


    class azure.ai.textanalytics.EntityConditionality(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONDITIONAL = "conditional"
        HYPOTHETICAL = "hypothetical"


    class azure.ai.textanalytics.ExtractKeyPhrasesAction(DictMixin):
        disable_service_logs: Optional[bool]
        model_version: Optional[str]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.ExtractKeyPhrasesResult(DictMixin):
        id: str
        is_error: Literal[False] = False
        key_phrases: List[str]
        kind: Literal["KeyPhraseExtraction"] = KeyPhraseExtraction
        statistics: Optional[TextDocumentStatistics]
        warnings: List[TextAnalyticsWarning]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.ExtractiveSummaryAction(DictMixin):
        disable_service_logs: Optional[bool]
        max_sentence_count: Optional[int]
        model_version: Optional[str]
        order_by: Optional[Literal["Rank", "Offset"]]
        string_index_type: Optional[str]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                max_sentence_count: Optional[int] = ..., 
                model_version: Optional[str] = ..., 
                order_by: Optional[Literal[Rank, Offset]] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.ExtractiveSummaryResult(DictMixin):
        id: str
        is_error: Literal[False] = False
        kind: Literal["ExtractiveSummarization"] = ExtractiveSummarization
        sentences: List[SummarySentence]
        statistics: Optional[TextDocumentStatistics]
        warnings: List[TextAnalyticsWarning]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.HealthcareEntity(DictMixin):
        assertion: Optional[HealthcareEntityAssertion]
        category: str
        confidence_score: float
        data_sources: Optional[List[HealthcareEntityDataSource]]
        length: int
        normalized_text: Optional[str]
        offset: int
        subcategory: Optional[str]
        text: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __hash__(self) -> int: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.HealthcareEntityAssertion(DictMixin):
        association: Optional[str]
        certainty: Optional[str]
        conditionality: Optional[str]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.HealthcareEntityCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMINISTRATIVE_EVENT = "AdministrativeEvent"
        AGE = "Age"
        ALLERGEN = "Allergen"
        BODY_STRUCTURE = "BodyStructure"
        CARE_ENVIRONMENT = "CareEnvironment"
        CONDITION_QUALIFIER = "ConditionQualifier"
        CONDITION_SCALE = "ConditionScale"
        COURSE = "Course"
        DATE = "Date"
        DIAGNOSIS = "Diagnosis"
        DIRECTION = "Direction"
        DOSAGE = "Dosage"
        EMPLOYMENT = "Employment"
        ETHNICITY = "Ethnicity"
        EXAMINATION_NAME = "ExaminationName"
        EXPRESSION = "Expression"
        FAMILY_RELATION = "FamilyRelation"
        FREQUENCY = "Frequency"
        GENDER = "Gender"
        GENE_OR_PROTEIN = "GeneOrProtein"
        HEALTHCARE_PROFESSION = "HealthcareProfession"
        LIVING_STATUS = "LivingStatus"
        MEASUREMENT_UNIT = "MeasurementUnit"
        MEASUREMENT_VALUE = "MeasurementValue"
        MEDICATION_CLASS = "MedicationClass"
        MEDICATION_FORM = "MedicationForm"
        MEDICATION_NAME = "MedicationName"
        MEDICATION_ROUTE = "MedicationRoute"
        MUTATION_TYPE = "MutationType"
        RELATIONAL_OPERATOR = "RelationalOperator"
        SUBSTANCE_USE = "SubstanceUse"
        SUBSTANCE_USE_AMOUNT = "SubstanceUseAmount"
        SYMPTOM_OR_SIGN = "SymptomOrSign"
        TIME = "Time"
        TREATMENT_NAME = "TreatmentName"
        VARIANT = "Variant"


    class azure.ai.textanalytics.HealthcareEntityDataSource(DictMixin):
        entity_id: str
        name: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.HealthcareEntityRelation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABBREVIATION = "Abbreviation"
        BODY_SITE_OF_CONDITION = "BodySiteOfCondition"
        BODY_SITE_OF_TREATMENT = "BodySiteOfTreatment"
        COURSE_OF_CONDITION = "CourseOfCondition"
        COURSE_OF_EXAMINATION = "CourseOfExamination"
        COURSE_OF_MEDICATION = "CourseOfMedication"
        COURSE_OF_TREATMENT = "CourseOfTreatment"
        DIRECTION_OF_BODY_STRUCTURE = "DirectionOfBodyStructure"
        DIRECTION_OF_CONDITION = "DirectionOfCondition"
        DIRECTION_OF_EXAMINATION = "DirectionOfExamination"
        DIRECTION_OF_TREATMENT = "DirectionOfTreatment"
        DOSAGE_OF_MEDICATION = "DosageOfMedication"
        EXAMINATION_FINDS_CONDITION = "ExaminationFindsCondition"
        EXPRESSION_OF_GENE = "ExpressionOfGene"
        EXPRESSION_OF_VARIANT = "ExpressionOfVariant"
        FORM_OF_MEDICATION = "FormOfMedication"
        FREQUENCY_OF_CONDITION = "FrequencyOfCondition"
        FREQUENCY_OF_MEDICATION = "FrequencyOfMedication"
        FREQUENCY_OF_TREATMENT = "FrequencyOfTreatment"
        MUTATION_TYPE_OF_GENE = "MutationTypeOfGene"
        MUTATION_TYPE_OF_VARIANT = "MutationTypeOfVariant"
        QUALIFIER_OF_CONDITION = "QualifierOfCondition"
        RELATION_OF_EXAMINATION = "RelationOfExamination"
        ROUTE_OF_MEDICATION = "RouteOfMedication"
        SCALE_OF_CONDITION = "ScaleOfCondition"
        TIME_OF_CONDITION = "TimeOfCondition"
        TIME_OF_EVENT = "TimeOfEvent"
        TIME_OF_EXAMINATION = "TimeOfExamination"
        TIME_OF_MEDICATION = "TimeOfMedication"
        TIME_OF_TREATMENT = "TimeOfTreatment"
        UNIT_OF_CONDITION = "UnitOfCondition"
        UNIT_OF_EXAMINATION = "UnitOfExamination"
        VALUE_OF_CONDITION = "ValueOfCondition"
        VALUE_OF_EXAMINATION = "ValueOfExamination"
        VARIANT_OF_GENE = "VariantOfGene"


    class azure.ai.textanalytics.HealthcareRelation(DictMixin):
        confidence_score: Optional[float]
        relation_type: str
        roles: List[HealthcareRelationRole]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.HealthcareRelationRole(DictMixin):
        entity: HealthcareEntity
        name: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.LinkedEntity(DictMixin):
        bing_entity_search_api_id: Optional[str]
        data_source: str
        data_source_entity_id: Optional[str]
        language: str
        matches: List[LinkedEntityMatch]
        name: str
        url: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.LinkedEntityMatch(DictMixin):
        confidence_score: float
        length: int
        offset: int
        text: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.MinedOpinion(DictMixin):
        assessments: List[AssessmentSentiment]
        target: TargetSentiment

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.MultiLabelClassifyAction(DictMixin):
        deployment_name: str
        disable_service_logs: Optional[bool]
        project_name: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                project_name: str, 
                deployment_name: str, 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.PiiEntity(DictMixin):
        category: str
        confidence_score: float
        length: int
        offset: int
        subcategory: Optional[str]
        text: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.PiiEntityCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABA_ROUTING_NUMBER = "ABARoutingNumber"
        ADDRESS = "Address"
        AGE = "Age"
        ALL = "All"
        AR_NATIONAL_IDENTITY_NUMBER = "ARNationalIdentityNumber"
        AT_IDENTITY_CARD = "ATIdentityCard"
        AT_TAX_IDENTIFICATION_NUMBER = "ATTaxIdentificationNumber"
        AT_VALUE_ADDED_TAX_NUMBER = "ATValueAddedTaxNumber"
        AU_BANK_ACCOUNT_NUMBER = "AUBankAccountNumber"
        AU_BUSINESS_NUMBER = "AUBusinessNumber"
        AU_COMPANY_NUMBER = "AUCompanyNumber"
        AU_DRIVERS_LICENSE_NUMBER = "AUDriversLicenseNumber"
        AU_MEDICAL_ACCOUNT_NUMBER = "AUMedicalAccountNumber"
        AU_PASSPORT_NUMBER = "AUPassportNumber"
        AU_TAX_FILE_NUMBER = "AUTaxFileNumber"
        AZURE_DOCUMENT_DB_AUTH_KEY = "AzureDocumentDBAuthKey"
        AZURE_IAAS_DATABASE_CONNECTION_AND_SQL_STRING = "AzureIAASDatabaseConnectionAndSQLString"
        AZURE_IO_T_CONNECTION_STRING = "AzureIoTConnectionString"
        AZURE_PUBLISH_SETTING_PASSWORD = "AzurePublishSettingPassword"
        AZURE_REDIS_CACHE_STRING = "AzureRedisCacheString"
        AZURE_SAS = "AzureSAS"
        AZURE_SERVICE_BUS_STRING = "AzureServiceBusString"
        AZURE_STORAGE_ACCOUNT_GENERIC = "AzureStorageAccountGeneric"
        AZURE_STORAGE_ACCOUNT_KEY = "AzureStorageAccountKey"
        BE_NATIONAL_NUMBER = "BENationalNumber"
        BE_NATIONAL_NUMBER_V2 = "BENationalNumberV2"
        BE_VALUE_ADDED_TAX_NUMBER = "BEValueAddedTaxNumber"
        BG_UNIFORM_CIVIL_NUMBER = "BGUniformCivilNumber"
        BRCPF_NUMBER = "BRCPFNumber"
        BR_LEGAL_ENTITY_NUMBER = "BRLegalEntityNumber"
        BR_NATIONAL_IDRG = "BRNationalIDRG"
        CA_BANK_ACCOUNT_NUMBER = "CABankAccountNumber"
        CA_DRIVERS_LICENSE_NUMBER = "CADriversLicenseNumber"
        CA_HEALTH_SERVICE_NUMBER = "CAHealthServiceNumber"
        CA_PASSPORT_NUMBER = "CAPassportNumber"
        CA_PERSONAL_HEALTH_IDENTIFICATION = "CAPersonalHealthIdentification"
        CA_SOCIAL_INSURANCE_NUMBER = "CASocialInsuranceNumber"
        CH_SOCIAL_SECURITY_NUMBER = "CHSocialSecurityNumber"
        CL_IDENTITY_CARD_NUMBER = "CLIdentityCardNumber"
        CN_RESIDENT_IDENTITY_CARD_NUMBER = "CNResidentIdentityCardNumber"
        CREDIT_CARD_NUMBER = "CreditCardNumber"
        CY_IDENTITY_CARD = "CYIdentityCard"
        CY_TAX_IDENTIFICATION_NUMBER = "CYTaxIdentificationNumber"
        CZ_PERSONAL_IDENTITY_NUMBER = "CZPersonalIdentityNumber"
        CZ_PERSONAL_IDENTITY_V2 = "CZPersonalIdentityV2"
        DATE = "Date"
        DEFAULT = "Default"
        DE_DRIVERS_LICENSE_NUMBER = "DEDriversLicenseNumber"
        DE_IDENTITY_CARD_NUMBER = "DEIdentityCardNumber"
        DE_PASSPORT_NUMBER = "DEPassportNumber"
        DE_TAX_IDENTIFICATION_NUMBER = "DETaxIdentificationNumber"
        DE_VALUE_ADDED_NUMBER = "DEValueAddedNumber"
        DK_PERSONAL_IDENTIFICATION_NUMBER = "DKPersonalIdentificationNumber"
        DK_PERSONAL_IDENTIFICATION_V2 = "DKPersonalIdentificationV2"
        DRUG_ENFORCEMENT_AGENCY_NUMBER = "DrugEnforcementAgencyNumber"
        EE_PERSONAL_IDENTIFICATION_CODE = "EEPersonalIdentificationCode"
        EMAIL = "Email"
        ESDNI = "ESDNI"
        ES_SOCIAL_SECURITY_NUMBER = "ESSocialSecurityNumber"
        ES_TAX_IDENTIFICATION_NUMBER = "ESTaxIdentificationNumber"
        EUGPS_COORDINATES = "EUGPSCoordinates"
        EU_DEBIT_CARD_NUMBER = "EUDebitCardNumber"
        EU_DRIVERS_LICENSE_NUMBER = "EUDriversLicenseNumber"
        EU_NATIONAL_IDENTIFICATION_NUMBER = "EUNationalIdentificationNumber"
        EU_PASSPORT_NUMBER = "EUPassportNumber"
        EU_SOCIAL_SECURITY_NUMBER = "EUSocialSecurityNumber"
        EU_TAX_IDENTIFICATION_NUMBER = "EUTaxIdentificationNumber"
        FI_EUROPEAN_HEALTH_NUMBER = "FIEuropeanHealthNumber"
        FI_NATIONAL_ID = "FINationalID"
        FI_NATIONAL_IDV2 = "FINationalIDV2"
        FI_PASSPORT_NUMBER = "FIPassportNumber"
        FR_DRIVERS_LICENSE_NUMBER = "FRDriversLicenseNumber"
        FR_HEALTH_INSURANCE_NUMBER = "FRHealthInsuranceNumber"
        FR_NATIONAL_ID = "FRNationalID"
        FR_PASSPORT_NUMBER = "FRPassportNumber"
        FR_SOCIAL_SECURITY_NUMBER = "FRSocialSecurityNumber"
        FR_TAX_IDENTIFICATION_NUMBER = "FRTaxIdentificationNumber"
        FR_VALUE_ADDED_TAX_NUMBER = "FRValueAddedTaxNumber"
        GR_NATIONAL_IDV2 = "GRNationalIDV2"
        GR_NATIONAL_ID_CARD = "GRNationalIDCard"
        GR_TAX_IDENTIFICATION_NUMBER = "GRTaxIdentificationNumber"
        HK_IDENTITY_CARD_NUMBER = "HKIdentityCardNumber"
        HR_IDENTITY_CARD_NUMBER = "HRIdentityCardNumber"
        HR_NATIONAL_ID_NUMBER = "HRNationalIDNumber"
        HR_PERSONAL_IDENTIFICATION_NUMBER = "HRPersonalIdentificationNumber"
        HR_PERSONAL_IDENTIFICATION_OIB_NUMBER_V2 = "HRPersonalIdentificationOIBNumberV2"
        HU_PERSONAL_IDENTIFICATION_NUMBER = "HUPersonalIdentificationNumber"
        HU_TAX_IDENTIFICATION_NUMBER = "HUTaxIdentificationNumber"
        HU_VALUE_ADDED_NUMBER = "HUValueAddedNumber"
        ID_IDENTITY_CARD_NUMBER = "IDIdentityCardNumber"
        IE_PERSONAL_PUBLIC_SERVICE_NUMBER = "IEPersonalPublicServiceNumber"
        IE_PERSONAL_PUBLIC_SERVICE_NUMBER_V2 = "IEPersonalPublicServiceNumberV2"
        IL_BANK_ACCOUNT_NUMBER = "ILBankAccountNumber"
        IL_NATIONAL_ID = "ILNationalID"
        INTERNATIONAL_BANKING_ACCOUNT_NUMBER = "InternationalBankingAccountNumber"
        IN_PERMANENT_ACCOUNT = "INPermanentAccount"
        IN_UNIQUE_IDENTIFICATION_NUMBER = "INUniqueIdentificationNumber"
        IP_ADDRESS = "IPAddress"
        IT_DRIVERS_LICENSE_NUMBER = "ITDriversLicenseNumber"
        IT_FISCAL_CODE = "ITFiscalCode"
        IT_VALUE_ADDED_TAX_NUMBER = "ITValueAddedTaxNumber"
        JP_BANK_ACCOUNT_NUMBER = "JPBankAccountNumber"
        JP_DRIVERS_LICENSE_NUMBER = "JPDriversLicenseNumber"
        JP_MY_NUMBER_CORPORATE = "JPMyNumberCorporate"
        JP_MY_NUMBER_PERSONAL = "JPMyNumberPersonal"
        JP_PASSPORT_NUMBER = "JPPassportNumber"
        JP_RESIDENCE_CARD_NUMBER = "JPResidenceCardNumber"
        JP_RESIDENT_REGISTRATION_NUMBER = "JPResidentRegistrationNumber"
        JP_SOCIAL_INSURANCE_NUMBER = "JPSocialInsuranceNumber"
        KR_RESIDENT_REGISTRATION_NUMBER = "KRResidentRegistrationNumber"
        LT_PERSONAL_CODE = "LTPersonalCode"
        LU_NATIONAL_IDENTIFICATION_NUMBER_NATURAL = "LUNationalIdentificationNumberNatural"
        LU_NATIONAL_IDENTIFICATION_NUMBER_NON_NATURAL = "LUNationalIdentificationNumberNonNatural"
        LV_PERSONAL_CODE = "LVPersonalCode"
        MT_IDENTITY_CARD_NUMBER = "MTIdentityCardNumber"
        MT_TAX_ID_NUMBER = "MTTaxIDNumber"
        MY_IDENTITY_CARD_NUMBER = "MYIdentityCardNumber"
        NL_CITIZENS_SERVICE_NUMBER = "NLCitizensServiceNumber"
        NL_CITIZENS_SERVICE_NUMBER_V2 = "NLCitizensServiceNumberV2"
        NL_TAX_IDENTIFICATION_NUMBER = "NLTaxIdentificationNumber"
        NL_VALUE_ADDED_TAX_NUMBER = "NLValueAddedTaxNumber"
        NO_IDENTITY_NUMBER = "NOIdentityNumber"
        NZ_BANK_ACCOUNT_NUMBER = "NZBankAccountNumber"
        NZ_DRIVERS_LICENSE_NUMBER = "NZDriversLicenseNumber"
        NZ_INLAND_REVENUE_NUMBER = "NZInlandRevenueNumber"
        NZ_MINISTRY_OF_HEALTH_NUMBER = "NZMinistryOfHealthNumber"
        NZ_SOCIAL_WELFARE_NUMBER = "NZSocialWelfareNumber"
        ORGANIZATION = "Organization"
        PERSON = "Person"
        PHONE_NUMBER = "PhoneNumber"
        PH_UNIFIED_MULTI_PURPOSE_ID_NUMBER = "PHUnifiedMultiPurposeIDNumber"
        PLREGON_NUMBER = "PLREGONNumber"
        PL_IDENTITY_CARD = "PLIdentityCard"
        PL_NATIONAL_ID = "PLNationalID"
        PL_NATIONAL_IDV2 = "PLNationalIDV2"
        PL_PASSPORT_NUMBER = "PLPassportNumber"
        PL_TAX_IDENTIFICATION_NUMBER = "PLTaxIdentificationNumber"
        PT_CITIZEN_CARD_NUMBER = "PTCitizenCardNumber"
        PT_CITIZEN_CARD_NUMBER_V2 = "PTCitizenCardNumberV2"
        PT_TAX_IDENTIFICATION_NUMBER = "PTTaxIdentificationNumber"
        RO_PERSONAL_NUMERICAL_CODE = "ROPersonalNumericalCode"
        RU_PASSPORT_NUMBER_DOMESTIC = "RUPassportNumberDomestic"
        RU_PASSPORT_NUMBER_INTERNATIONAL = "RUPassportNumberInternational"
        SA_NATIONAL_ID = "SANationalID"
        SE_NATIONAL_ID = "SENationalID"
        SE_NATIONAL_IDV2 = "SENationalIDV2"
        SE_PASSPORT_NUMBER = "SEPassportNumber"
        SE_TAX_IDENTIFICATION_NUMBER = "SETaxIdentificationNumber"
        SG_NATIONAL_REGISTRATION_IDENTITY_CARD_NUMBER = "SGNationalRegistrationIdentityCardNumber"
        SI_TAX_IDENTIFICATION_NUMBER = "SITaxIdentificationNumber"
        SI_UNIQUE_MASTER_CITIZEN_NUMBER = "SIUniqueMasterCitizenNumber"
        SK_PERSONAL_NUMBER = "SKPersonalNumber"
        SQL_SERVER_CONNECTION_STRING = "SQLServerConnectionString"
        SWIFT_CODE = "SWIFTCode"
        TH_POPULATION_IDENTIFICATION_CODE = "THPopulationIdentificationCode"
        TR_NATIONAL_IDENTIFICATION_NUMBER = "TRNationalIdentificationNumber"
        TW_NATIONAL_ID = "TWNationalID"
        TW_PASSPORT_NUMBER = "TWPassportNumber"
        TW_RESIDENT_CERTIFICATE = "TWResidentCertificate"
        UA_PASSPORT_NUMBER_DOMESTIC = "UAPassportNumberDomestic"
        UA_PASSPORT_NUMBER_INTERNATIONAL = "UAPassportNumberInternational"
        UK_DRIVERS_LICENSE_NUMBER = "UKDriversLicenseNumber"
        UK_ELECTORAL_ROLL_NUMBER = "UKElectoralRollNumber"
        UK_NATIONAL_HEALTH_NUMBER = "UKNationalHealthNumber"
        UK_NATIONAL_INSURANCE_NUMBER = "UKNationalInsuranceNumber"
        UK_UNIQUE_TAXPAYER_NUMBER = "UKUniqueTaxpayerNumber"
        URL = "URL"
        USUK_PASSPORT_NUMBER = "USUKPassportNumber"
        US_BANK_ACCOUNT_NUMBER = "USBankAccountNumber"
        US_DRIVERS_LICENSE_NUMBER = "USDriversLicenseNumber"
        US_INDIVIDUAL_TAXPAYER_IDENTIFICATION = "USIndividualTaxpayerIdentification"
        US_SOCIAL_SECURITY_NUMBER = "USSocialSecurityNumber"
        ZA_IDENTIFICATION_NUMBER = "ZAIdentificationNumber"


    class azure.ai.textanalytics.PiiEntityDomain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROTECTED_HEALTH_INFORMATION = "phi"


    class azure.ai.textanalytics.RecognizeCustomEntitiesAction(DictMixin):
        deployment_name: str
        disable_service_logs: Optional[bool]
        project_name: str
        string_index_type: Optional[str]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                project_name: str, 
                deployment_name: str, 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.RecognizeCustomEntitiesResult(DictMixin):
        entities: List[CategorizedEntity]
        id: str
        is_error: Literal[False] = False
        kind: Literal["CustomEntityRecognition"] = CustomEntityRecognition
        statistics: Optional[TextDocumentStatistics]
        warnings: List[TextAnalyticsWarning]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.RecognizeEntitiesAction(DictMixin):
        disable_service_logs: Optional[bool]
        model_version: Optional[str]
        string_index_type: Optional[str]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.RecognizeEntitiesResult(DictMixin):
        entities: List[CategorizedEntity]
        id: str
        is_error: Literal[False] = False
        kind: Literal["EntityRecognition"] = EntityRecognition
        statistics: Optional[TextDocumentStatistics]
        warnings: List[TextAnalyticsWarning]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.RecognizeLinkedEntitiesAction(DictMixin):
        disable_service_logs: Optional[bool]
        model_version: Optional[str]
        string_index_type: Optional[str]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.RecognizeLinkedEntitiesResult(DictMixin):
        entities: List[LinkedEntity]
        id: str
        is_error: Literal[False] = False
        kind: Literal["EntityLinking"] = EntityLinking
        statistics: Optional[TextDocumentStatistics]
        warnings: List[TextAnalyticsWarning]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.RecognizePiiEntitiesAction(DictMixin):
        categories_filter: Optional[List[Union[str, PiiEntityCategory]]]
        disable_service_logs: Optional[bool]
        domain_filter: Optional[str]
        model_version: Optional[str]
        string_index_type: Optional[str]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                *, 
                categories_filter: Optional[List[Union[str, PiiEntityCategory]]] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                domain_filter: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.RecognizePiiEntitiesResult(DictMixin):
        entities: List[PiiEntity]
        id: str
        is_error: Literal[False] = False
        kind: Literal["PiiEntityRecognition"] = PiiEntityRecognition
        redacted_text: str
        statistics: Optional[TextDocumentStatistics]
        warnings: List[TextAnalyticsWarning]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.SentenceSentiment(DictMixin):
        confidence_scores: SentimentConfidenceScores
        length: int
        mined_opinions: Optional[List[MinedOpinion]]
        offset: int
        sentiment: str
        text: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.SentimentConfidenceScores(DictMixin):
        negative: float
        neutral: float
        positive: float

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.SingleLabelClassifyAction(DictMixin):
        deployment_name: str
        disable_service_logs: Optional[bool]
        project_name: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                project_name: str, 
                deployment_name: str, 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.SummaryContext(DictMixin):
        length: int
        offset: int

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.SummarySentence(DictMixin):
        length: int
        offset: int
        rank_score: float
        text: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.TargetSentiment(DictMixin):
        confidence_scores: SentimentConfidenceScores
        length: int
        offset: int
        sentiment: str
        text: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.TextAnalysisKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABSTRACTIVE_SUMMARIZATION = "AbstractiveSummarization"
        CUSTOM_DOCUMENT_CLASSIFICATION = "CustomDocumentClassification"
        CUSTOM_ENTITY_RECOGNITION = "CustomEntityRecognition"
        ENTITY_LINKING = "EntityLinking"
        ENTITY_RECOGNITION = "EntityRecognition"
        EXTRACTIVE_SUMMARIZATION = "ExtractiveSummarization"
        HEALTHCARE = "Healthcare"
        KEY_PHRASE_EXTRACTION = "KeyPhraseExtraction"
        LANGUAGE_DETECTION = "LanguageDetection"
        PII_ENTITY_RECOGNITION = "PiiEntityRecognition"
        SENTIMENT_ANALYSIS = "SentimentAnalysis"


    @runtime_checkable
    class azure.ai.textanalytics.TextAnalysisLROPoller(Protocol[PollingReturnType_co]):
        property details: Mapping[str, Any]    # Read-only

        def add_done_callback(self, func: Callable) -> None: ...

        def cancel(self) -> None: ...

        def continuation_token(self) -> str: ...

        def done(self) -> bool: ...

        def remove_done_callback(self, func: Callable) -> None: ...

        def result(self, timeout: Optional[float] = None) -> PollingReturnType_co: ...

        def status(self) -> str: ...

        def wait(self, timeout: Optional[float] = None) -> None: ...


    class azure.ai.textanalytics.TextAnalyticsApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2022_05_01 = "2022-05-01"
        V2023_04_01 = "2023-04-01"
        V3_0 = "v3.0"
        V3_1 = "v3.1"


    class azure.ai.textanalytics.TextAnalyticsClient(TextAnalyticsClientBase): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Optional[Union[str, TextAnalyticsApiVersion]] = ..., 
                default_country_hint: Optional[str] = ..., 
                default_language: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @validate_multiapi_args(version_method_added='v3.0', args_mapping={'v3.1': ['show_opinion_mining', 'disable_service_logs', 'string_index_type']})
        def analyze_sentiment(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                show_opinion_mining: Optional[bool] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[Union[AnalyzeSentimentResult, DocumentError]]: ...

        @distributed_trace
        @validate_multiapi_args(version_method_added='2023-04-01')
        def begin_abstract_summary(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                continuation_token: Optional[str] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                display_name: Optional[str] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                polling_interval: Optional[int] = ..., 
                sentence_count: Optional[int] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> TextAnalysisLROPoller[ItemPaged[Union[AbstractiveSummaryResult, DocumentError]]]: ...

        @distributed_trace
        @validate_multiapi_args(version_method_added='v3.1', custom_wrapper=check_for_unsupported_actions_types)
        def begin_analyze_actions(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                actions: List[Union[RecognizeEntitiesAction, RecognizeLinkedEntitiesAction, RecognizePiiEntitiesAction, ExtractKeyPhrasesAction, AnalyzeSentimentAction, RecognizeCustomEntitiesAction, SingleLabelClassifyAction, MultiLabelClassifyAction, AnalyzeHealthcareEntitiesAction, ExtractiveSummaryAction, AbstractiveSummaryAction]], 
                *, 
                continuation_token: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                language: Optional[str] = ..., 
                polling_interval: Optional[int] = ..., 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> TextAnalysisLROPoller[ItemPaged[List[Union[RecognizeEntitiesResult, RecognizeLinkedEntitiesResult, RecognizePiiEntitiesResult, ExtractKeyPhrasesResult, AnalyzeSentimentResult, RecognizeCustomEntitiesResult, ClassifyDocumentResult, AnalyzeHealthcareEntitiesResult, ExtractiveSummaryResult, AbstractiveSummaryResult, DocumentError]]]]: ...

        @distributed_trace
        @validate_multiapi_args(version_method_added='v3.1', args_mapping={'2022-05-01': ['display_name']})
        def begin_analyze_healthcare_entities(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                continuation_token: Optional[str] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                display_name: Optional[str] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                polling_interval: Optional[int] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> AnalyzeHealthcareEntitiesLROPoller[ItemPaged[Union[AnalyzeHealthcareEntitiesResult, DocumentError]]]: ...

        @distributed_trace
        @validate_multiapi_args(version_method_added='2023-04-01')
        def begin_extract_summary(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                continuation_token: Optional[str] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                display_name: Optional[str] = ..., 
                language: Optional[str] = ..., 
                max_sentence_count: Optional[int] = ..., 
                model_version: Optional[str] = ..., 
                order_by: Optional[Literal[Rank, Offset]] = ..., 
                polling_interval: Optional[int] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> TextAnalysisLROPoller[ItemPaged[Union[ExtractiveSummaryResult, DocumentError]]]: ...

        @distributed_trace
        @validate_multiapi_args(version_method_added='2022-05-01')
        def begin_multi_label_classify(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                project_name: str, 
                deployment_name: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                display_name: Optional[str] = ..., 
                language: Optional[str] = ..., 
                polling_interval: Optional[int] = ..., 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> TextAnalysisLROPoller[ItemPaged[Union[ClassifyDocumentResult, DocumentError]]]: ...

        @distributed_trace
        @validate_multiapi_args(version_method_added='2022-05-01')
        def begin_recognize_custom_entities(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                project_name: str, 
                deployment_name: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                display_name: Optional[str] = ..., 
                language: Optional[str] = ..., 
                polling_interval: Optional[int] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> TextAnalysisLROPoller[ItemPaged[Union[RecognizeCustomEntitiesResult, DocumentError]]]: ...

        @distributed_trace
        @validate_multiapi_args(version_method_added='2022-05-01')
        def begin_single_label_classify(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                project_name: str, 
                deployment_name: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                display_name: Optional[str] = ..., 
                language: Optional[str] = ..., 
                polling_interval: Optional[int] = ..., 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> TextAnalysisLROPoller[ItemPaged[Union[ClassifyDocumentResult, DocumentError]]]: ...

        def close(self) -> None: ...

        @distributed_trace
        @validate_multiapi_args(version_method_added='v3.0', args_mapping={'v3.1': ['disable_service_logs']})
        def detect_language(
                self, 
                documents: Union[List[str], List[DetectLanguageInput], List[Dict[str, str]]], 
                *, 
                country_hint: Optional[str] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[Union[DetectLanguageResult, DocumentError]]: ...

        @distributed_trace
        @validate_multiapi_args(version_method_added='v3.0', args_mapping={'v3.1': ['disable_service_logs']})
        def extract_key_phrases(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[Union[ExtractKeyPhrasesResult, DocumentError]]: ...

        @distributed_trace
        @validate_multiapi_args(version_method_added='v3.0', args_mapping={'v3.1': ['string_index_type', 'disable_service_logs']})
        def recognize_entities(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[Union[RecognizeEntitiesResult, DocumentError]]: ...

        @distributed_trace
        @validate_multiapi_args(version_method_added='v3.0', args_mapping={'v3.1': ['string_index_type', 'disable_service_logs']})
        def recognize_linked_entities(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[Union[RecognizeLinkedEntitiesResult, DocumentError]]: ...

        @distributed_trace
        @validate_multiapi_args(version_method_added='v3.1')
        def recognize_pii_entities(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                categories_filter: Optional[List[Union[str, PiiEntityCategory]]] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                domain_filter: Optional[Union[str, PiiEntityDomain]] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[Union[RecognizePiiEntitiesResult, DocumentError]]: ...


    class azure.ai.textanalytics.TextAnalyticsError(DictMixin):
        code: str
        message: str
        target: Optional[str]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.TextAnalyticsWarning(DictMixin):
        code: str
        message: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.TextDocumentBatchStatistics(DictMixin):
        document_count: int
        erroneous_document_count: int
        transaction_count: int
        valid_document_count: int

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.TextDocumentInput(DictMixin, MultiLanguageInput):
        id: str
        language: Optional[str]
        text: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                *, 
                id: str, 
                language: Optional[str] = ..., 
                text: str, 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


    class azure.ai.textanalytics.TextDocumentStatistics(DictMixin):
        character_count: int
        transaction_count: int

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> Iterable[Tuple[str, Any]]: ...

        def keys(self) -> Iterable[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> Iterable[Any]: ...


namespace azure.ai.textanalytics.aio

    class azure.ai.textanalytics.aio.AsyncAnalyzeActionsLROPoller(AsyncLROPoller[PollingReturnType_co]):
        property details: Mapping[str, Any]    # Read-only

        def __getattr__(self, item: str) -> Any: ...

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: AsyncAnalyzeActionsLROPollingMethod, 
                continuation_token: str, 
                **kwargs: Any
            ) -> AsyncAnalyzeActionsLROPoller: ...

        @distributed_trace_async
        async def cancel(self) -> None: ...

        def polling_method(self) -> AsyncAnalyzeActionsLROPollingMethod: ...


    class azure.ai.textanalytics.aio.AsyncAnalyzeHealthcareEntitiesLROPoller(AsyncLROPoller[PollingReturnType_co]):
        property details: Mapping[str, Any]    # Read-only

        def __getattr__(self, item: str) -> Any: ...

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: AsyncAnalyzeHealthcareEntitiesLROPollingMethod, 
                continuation_token: str, 
                **kwargs: Any
            ) -> AsyncAnalyzeHealthcareEntitiesLROPoller: ...

        @distributed_trace_async
        async def cancel(
                self, 
                *, 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        def polling_method(self) -> AsyncAnalyzeHealthcareEntitiesLROPollingMethod: ...


    @runtime_checkable
    class azure.ai.textanalytics.aio.AsyncTextAnalysisLROPoller(Protocol[PollingReturnType_co], Awaitable[PollingReturnType_co]): implements Awaitable 
        property details: Mapping[str, Any]    # Read-only

        async def cancel(self) -> None: ...

        def continuation_token(self) -> str: ...

        def done(self) -> bool: ...

        async def result(self) -> PollingReturnType_co: ...

        def status(self) -> str: ...

        async def wait(self) -> None: ...


    class azure.ai.textanalytics.aio.TextAnalyticsClient(AsyncTextAnalyticsClientBase): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Optional[Union[str, TextAnalyticsApiVersion]] = ..., 
                default_country_hint: Optional[str] = ..., 
                default_language: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @validate_multiapi_args(version_method_added='v3.0', args_mapping={'v3.1': ['show_opinion_mining', 'disable_service_logs', 'string_index_type']})
        async def analyze_sentiment(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                show_opinion_mining: Optional[bool] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[Union[AnalyzeSentimentResult, DocumentError]]: ...

        @distributed_trace_async
        @validate_multiapi_args(version_method_added='2023-04-01')
        async def begin_abstract_summary(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                continuation_token: Optional[str] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                display_name: Optional[str] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                polling_interval: Optional[int] = ..., 
                sentence_count: Optional[int] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncTextAnalysisLROPoller[AsyncItemPaged[Union[AbstractiveSummaryResult, DocumentError]]]: ...

        @distributed_trace_async
        @validate_multiapi_args(version_method_added='v3.1', custom_wrapper=check_for_unsupported_actions_types)
        async def begin_analyze_actions(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                actions: List[Union[RecognizeEntitiesAction, RecognizeLinkedEntitiesAction, RecognizePiiEntitiesAction, ExtractKeyPhrasesAction, AnalyzeSentimentAction, RecognizeCustomEntitiesAction, SingleLabelClassifyAction, MultiLabelClassifyAction, AnalyzeHealthcareEntitiesAction, ExtractiveSummaryAction, AbstractiveSummaryAction]], 
                *, 
                continuation_token: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                language: Optional[str] = ..., 
                polling_interval: Optional[int] = ..., 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncTextAnalysisLROPoller[AsyncItemPaged[List[Union[RecognizeEntitiesResult, RecognizeLinkedEntitiesResult, RecognizePiiEntitiesResult, ExtractKeyPhrasesResult, AnalyzeSentimentResult, RecognizeCustomEntitiesResult, ClassifyDocumentResult, AnalyzeHealthcareEntitiesResult, ExtractiveSummaryResult, AbstractiveSummaryResult, DocumentError]]]]: ...

        @distributed_trace_async
        @validate_multiapi_args(version_method_added='v3.1', args_mapping={'2022-05-01': ['display_name']})
        async def begin_analyze_healthcare_entities(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                continuation_token: Optional[str] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                display_name: Optional[str] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                polling_interval: Optional[int] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncAnalyzeHealthcareEntitiesLROPoller[AsyncItemPaged[Union[AnalyzeHealthcareEntitiesResult, DocumentError]]]: ...

        @distributed_trace_async
        @validate_multiapi_args(version_method_added='2023-04-01')
        async def begin_extract_summary(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                continuation_token: Optional[str] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                display_name: Optional[str] = ..., 
                language: Optional[str] = ..., 
                max_sentence_count: Optional[int] = ..., 
                model_version: Optional[str] = ..., 
                order_by: Optional[Literal[Rank, Offset]] = ..., 
                polling_interval: Optional[int] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncTextAnalysisLROPoller[AsyncItemPaged[Union[ExtractiveSummaryResult, DocumentError]]]: ...

        @distributed_trace_async
        @validate_multiapi_args(version_method_added='2022-05-01')
        async def begin_multi_label_classify(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                project_name: str, 
                deployment_name: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                display_name: Optional[str] = ..., 
                language: Optional[str] = ..., 
                polling_interval: Optional[int] = ..., 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncTextAnalysisLROPoller[AsyncItemPaged[Union[ClassifyDocumentResult, DocumentError]]]: ...

        @distributed_trace_async
        @validate_multiapi_args(version_method_added='2022-05-01')
        async def begin_recognize_custom_entities(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                project_name: str, 
                deployment_name: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                display_name: Optional[str] = ..., 
                language: Optional[str] = ..., 
                polling_interval: Optional[int] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncTextAnalysisLROPoller[AsyncItemPaged[Union[RecognizeCustomEntitiesResult, DocumentError]]]: ...

        @distributed_trace_async
        @validate_multiapi_args(version_method_added='2022-05-01')
        async def begin_single_label_classify(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                project_name: str, 
                deployment_name: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                display_name: Optional[str] = ..., 
                language: Optional[str] = ..., 
                polling_interval: Optional[int] = ..., 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncTextAnalysisLROPoller[AsyncItemPaged[Union[ClassifyDocumentResult, DocumentError]]]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        @validate_multiapi_args(version_method_added='v3.0', args_mapping={'v3.1': ['disable_service_logs']})
        async def detect_language(
                self, 
                documents: Union[List[str], List[DetectLanguageInput], List[Dict[str, str]]], 
                *, 
                country_hint: Optional[str] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[Union[DetectLanguageResult, DocumentError]]: ...

        @distributed_trace_async
        @validate_multiapi_args(version_method_added='v3.0', args_mapping={'v3.1': ['disable_service_logs']})
        async def extract_key_phrases(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[Union[ExtractKeyPhrasesResult, DocumentError]]: ...

        @distributed_trace_async
        @validate_multiapi_args(version_method_added='v3.0', args_mapping={'v3.1': ['string_index_type', 'disable_service_logs']})
        async def recognize_entities(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[Union[RecognizeEntitiesResult, DocumentError]]: ...

        @distributed_trace_async
        @validate_multiapi_args(version_method_added='v3.0', args_mapping={'v3.1': ['string_index_type', 'disable_service_logs']})
        async def recognize_linked_entities(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                disable_service_logs: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[Union[RecognizeLinkedEntitiesResult, DocumentError]]: ...

        @distributed_trace_async
        @validate_multiapi_args(version_method_added='v3.1')
        async def recognize_pii_entities(
                self, 
                documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]], 
                *, 
                categories_filter: Optional[List[Union[str, PiiEntityCategory]]] = ..., 
                disable_service_logs: Optional[bool] = ..., 
                domain_filter: Optional[Union[str, PiiEntityDomain]] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                show_stats: Optional[bool] = ..., 
                string_index_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[Union[RecognizePiiEntitiesResult, DocumentError]]: ...


```
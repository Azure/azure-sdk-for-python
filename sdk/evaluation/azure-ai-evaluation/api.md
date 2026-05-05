```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.evaluation

    def azure.ai.evaluation.evaluate(
            *, 
            azure_ai_project: Optional[Union[str, AzureAIProject]] = ..., 
            data: Union[str, PathLike], 
            evaluation_name: Optional[str] = ..., 
            evaluator_config: Optional[Dict[str, EvaluatorConfig]] = ..., 
            evaluators: Dict[str, Union[Callable, AzureOpenAIGrader]], 
            fail_on_evaluator_errors: bool = False, 
            output_path: Optional[Union[str, PathLike]] = ..., 
            tags: Optional[Dict[str, str]] = ..., 
            target: Optional[Callable] = ..., 
            user_agent: Optional[str] = ..., 
            **kwargs
        ) -> EvaluationResult: ...


    class azure.ai.evaluation.AzureAIProject(TypedDict):
        key "project_name": str
        key "resource_group_name": str
        key "subscription_id": str


    @experimental
    class azure.ai.evaluation.AzureOpenAIGrader:
        id = azureai://built-in/evaluators/azure-openai/custom_grader

        def __init__(
                self, 
                *, 
                credential: Optional[TokenCredential] = ..., 
                grader_config: Dict[str, Any], 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                **kwargs: Any
            ): ...

        def get_client(self) -> Any: ...


    @experimental
    class azure.ai.evaluation.AzureOpenAILabelGrader(AzureOpenAIGrader):
        id = azureai://built-in/evaluators/azure-openai/label_grader

        def __init__(
                self, 
                *, 
                credential: Optional[TokenCredential] = ..., 
                input: List[Dict[str, str]], 
                labels: List[str], 
                model: str, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                name: str, 
                passing_labels: List[str], 
                **kwargs: Any
            ): ...

        def get_client(self) -> Any: ...


    class azure.ai.evaluation.AzureOpenAIModelConfiguration(TypedDict):
        key "api_key": NotRequired[str]
        key "api_version": NotRequired[str]
        key "azure_deployment": str
        key "azure_endpoint": str
        key "credential": NotRequired[Any]
        key "type": NotRequired[Literal["azure_openai"]]


    @experimental
    class azure.ai.evaluation.AzureOpenAIPythonGrader(AzureOpenAIGrader):
        id = azureai://built-in/evaluators/azure-openai/python_grader

        def __init__(
                self, 
                *, 
                credential: Optional[TokenCredential] = ..., 
                image_tag: Optional[str] = ..., 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                name: str, 
                pass_threshold: float, 
                source: str, 
                **kwargs: Any
            ): ...

        def get_client(self) -> Any: ...


    @experimental
    class azure.ai.evaluation.AzureOpenAIScoreModelGrader(AzureOpenAIGrader):
        id = azureai://built-in/evaluators/azure-openai/score_model_grader

        def __init__(
                self, 
                *, 
                credential: Optional[TokenCredential] = ..., 
                input: List[Dict[str, str]], 
                model: str, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                name: str, 
                pass_threshold: Optional[float] = ..., 
                range: Optional[List[float]] = ..., 
                sampling_params: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ): ...

        def get_client(self) -> Any: ...


    @experimental
    class azure.ai.evaluation.AzureOpenAIStringCheckGrader(AzureOpenAIGrader):
        id = azureai://built-in/evaluators/azure-openai/string_check_grader

        def __init__(
                self, 
                *, 
                credential: Optional[TokenCredential] = ..., 
                input: str, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                name: str, 
                operation: Literal["eq", "ne", "like", "ilike"], 
                reference: str, 
                **kwargs: Any
            ): ...

        def get_client(self) -> Any: ...


    @experimental
    class azure.ai.evaluation.AzureOpenAITextSimilarityGrader(AzureOpenAIGrader):
        id = azureai://built-in/evaluators/azure-openai/text_similarity_grader

        def __init__(
                self, 
                *, 
                credential: Optional[TokenCredential] = ..., 
                evaluation_metric: Literal["fuzzy_match", "bleu", "gleu", "meteor", "rouge_1", "rouge_2", "rouge_3", "rouge_4", "rouge_5", "rouge_l", "cosine"], 
                input: str, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                name: str, 
                pass_threshold: float, 
                reference: str, 
                **kwargs: Any
            ): ...

        def get_client(self) -> Any: ...


    class azure.ai.evaluation.BleuScoreEvaluator(EvaluatorBase):
        id = azureai://built-in/evaluators/bleu_score

        @overload
        def __call__(
                self, 
                *, 
                ground_truth: str, 
                response: str
            ): ...

        def __init__(
                self, 
                *, 
                threshold = 0.5
            ): ...


    @experimental
    class azure.ai.evaluation.CodeVulnerabilityEvaluator(RaiServiceEvaluatorBase[Union[str, bool]]):
        id = azureai://built-in/evaluators/code_vulnerability

        @overload
        def __call__(
                self, 
                *, 
                query: str, 
                response: str
            ) -> Dict[str, Union[str, float]]: ...

        @override
        def __init__(
                self, 
                credential: TokenCredential, 
                azure_ai_project: Union[str, AzureAIProject], 
                **kwargs: Any
            ): ...


    class azure.ai.evaluation.CoherenceEvaluator(PromptyEvaluatorBase[Union[str, float]]):
        id = azureai://built-in/evaluators/coherence

        @overload
        def __call__(
                self, 
                *, 
                query: str, 
                response: str
            ) -> Dict[str, Union[str, float]]: ...

        @overload
        def __call__(
                self, 
                *, 
                conversation: Conversation
            ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]: ...

        @override
        def __init__(
                self, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                *, 
                credential = ..., 
                is_reasoning_model: bool = ..., 
                threshold = 3, 
                **kwargs
            ): ...


    @experimental
    class azure.ai.evaluation.ContentSafetyEvaluator(MultiEvaluatorBase[Union[str, float]]):
        id = azureai://built-in/evaluators/content_safety

        @overload
        def __call__(
                self, 
                *, 
                query: str, 
                response: str
            ) -> Dict[str, Union[str, float]]: ...

        @overload
        def __call__(
                self, 
                *, 
                conversation: Conversation
            ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]: ...

        def __init__(
                self, 
                credential: TokenCredential, 
                azure_ai_project: Union[str, AzureAIProject], 
                *, 
                hate_unfairness_threshold: int = 3, 
                self_harm_threshold: int = 3, 
                sexual_threshold: int = 3, 
                violence_threshold: int = 3, 
                **kwargs: Any
            ): ...


    class azure.ai.evaluation.Conversation(TypedDict):
        key "context": NotRequired[Dict[str, Any]]
        key "messages": Union[List[Message], List[Dict]]


    class azure.ai.evaluation.EvaluationResult(TypedDict):
        key "metrics": Dict
        key "oai_eval_run_ids": NotRequired[List[Dict[str, str]]]
        key "rows": List[Dict]
        key "studio_url": NotRequired[str]


    class azure.ai.evaluation.EvaluatorConfig(TypedDict, total=False):
        key "column_mapping": Dict[str, str]


    class azure.ai.evaluation.F1ScoreEvaluator(EvaluatorBase):
        id = azureai://built-in/evaluators/f1_score

        @overload
        def __call__(
                self, 
                *, 
                ground_truth: str, 
                response: str
            ) -> Dict[str, float]: ...

        def __init__(
                self, 
                *, 
                threshold = 0.5
            ): ...


    class azure.ai.evaluation.FluencyEvaluator(PromptyEvaluatorBase[Union[str, float]]):
        id = azureai://built-in/evaluators/fluency

        @overload
        def __call__(
                self, 
                *, 
                response: str
            ) -> Dict[str, Union[str, float]]: ...

        @overload
        def __call__(
                self, 
                *, 
                conversation: Conversation
            ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]: ...

        @override
        def __init__(
                self, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                *, 
                credential = ..., 
                is_reasoning_model: bool = ..., 
                threshold = 3, 
                **kwargs
            ): ...


    class azure.ai.evaluation.GleuScoreEvaluator(EvaluatorBase):
        id = azureai://built-in/evaluators/gleu_score

        @overload
        def __call__(
                self, 
                *, 
                ground_truth: str, 
                response: str
            ): ...

        @override
        def __init__(
                self, 
                *, 
                threshold = 0.5
            ): ...


    class azure.ai.evaluation.GroundednessEvaluator(PromptyEvaluatorBase[Union[str, float]]):
        id = azureai://built-in/evaluators/groundedness

        @overload
        def __call__(
                self, 
                *, 
                context: str, 
                query: Optional[str] = ..., 
                response: str
            ) -> Dict[str, Union[str, float]]: ...

        @overload
        def __call__(
                self, 
                *, 
                query: str, 
                response: List[dict], 
                tool_definitions: Optional[List[dict]] = ...
            ) -> Dict[str, Union[str, float]]: ...

        @overload
        def __call__(
                self, 
                *, 
                conversation: Conversation
            ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]: ...

        @override
        def __init__(
                self, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                *, 
                credential = ..., 
                is_reasoning_model: bool = ..., 
                threshold = 3, 
                **kwargs
            ): ...


    @experimental
    class azure.ai.evaluation.GroundednessProEvaluator(RaiServiceEvaluatorBase[Union[str, bool]]):
        id = azureai://built-in/evaluators/groundedness_pro

        @overload
        def __call__(
                self, 
                *, 
                context: str, 
                query: str, 
                response: str
            ) -> Dict[str, Union[str, bool]]: ...

        @overload
        def __call__(
                self, 
                *, 
                conversation: Conversation
            ) -> Dict[str, Union[float, Dict[str, List[Union[str, bool]]]]]: ...

        @override
        def __init__(
                self, 
                credential: TokenCredential, 
                azure_ai_project: Union[str, AzureAIProject], 
                *, 
                threshold: int = 5, 
                **kwargs: Any
            ): ...


    @experimental
    class azure.ai.evaluation.HateUnfairnessEvaluator(RaiServiceEvaluatorBase[Union[str, float]]):
        id = azureai://built-in/evaluators/hate_unfairness

        @overload
        def __call__(
                self, 
                *, 
                query: str, 
                response: str
            ) -> Dict[str, Union[str, float]]: ...

        @overload
        def __call__(
                self, 
                *, 
                conversation: Conversation
            ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]: ...

        @override
        def __init__(
                self, 
                credential: TokenCredential, 
                azure_ai_project: Union[str, AzureAIProject], 
                *, 
                threshold: int = 3, 
                **kwargs
            ): ...


    @experimental
    class azure.ai.evaluation.IndirectAttackEvaluator(RaiServiceEvaluatorBase[Union[str, bool]]):
        id = azureai://built-in/evaluators/indirect_attack

        @overload
        def __call__(
                self, 
                *, 
                query: str, 
                response: str
            ) -> Dict[str, Union[str, bool]]: ...

        @overload
        def __call__(
                self, 
                *, 
                conversation: Conversation
            ) -> Dict[str, Union[float, Dict[str, List[Union[str, bool]]]]]: ...

        @override
        def __init__(
                self, 
                credential: TokenCredential, 
                azure_ai_project: Union[str, AzureAIProject], 
                **kwargs
            ): ...


    @experimental
    class azure.ai.evaluation.IntentResolutionEvaluator(PromptyEvaluatorBase[Union[str, float]]):
        id = azureai://built-in/evaluators/intent_resolution

        @overload
        def __call__(
                self, 
                *, 
                query: Union[str, List[dict]], 
                response: Union[str, List[dict]], 
                tool_definitions: Optional[Union[dict, List[dict]]] = ...
            ) -> Dict[str, Union[str, float]]: ...

        @override
        def __init__(
                self, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                *, 
                credential = ..., 
                threshold = _DEFAULT_INTENT_RESOLUTION_THRESHOLD, 
                **kwargs
            ): ...


    class azure.ai.evaluation.Message(TypedDict):
        key "content": Union[str, List[Dict]]
        key "context": NotRequired[Dict[str, Any]]
        key "role": str


    class azure.ai.evaluation.MeteorScoreEvaluator(EvaluatorBase):
        id = azureai://built-in/evaluators/meteor_score

        @overload
        def __call__(
                self, 
                *, 
                ground_truth: str, 
                response: str
            ) -> Dict[str, float]: ...

        @override
        def __init__(
                self, 
                alpha: float = 0.9, 
                beta: float = 3.0, 
                gamma: float = 0.5, 
                *, 
                threshold: float = 0.5
            ): ...


    class azure.ai.evaluation.OpenAIModelConfiguration(TypedDict):
        key "api_key": str
        key "base_url": NotRequired[str]
        key "extra_headers": NotRequired[Dict[str, str]]
        key "model": str
        key "organization": NotRequired[str]
        key "type": NotRequired[Literal["openai"]]


    @experimental
    class azure.ai.evaluation.ProtectedMaterialEvaluator(RaiServiceEvaluatorBase[Union[str, bool]]):
        id = azureai://built-in/evaluators/protected_material

        @overload
        def __call__(
                self, 
                *, 
                query: str, 
                response: str
            ) -> Dict[str, Union[str, bool]]: ...

        @overload
        def __call__(
                self, 
                *, 
                conversation: Conversation
            ) -> Dict[str, Union[float, Dict[str, List[Union[str, bool]]]]]: ...

        @override
        def __init__(
                self, 
                credential: TokenCredential, 
                azure_ai_project: Union[str, AzureAIProject], 
                **kwargs
            ): ...


    class azure.ai.evaluation.QAEvaluator(MultiEvaluatorBase[Union[str, float]]):
        id = azureai://built-in/evaluators/qa

        @overload
        def __call__(
                self, 
                *, 
                context: str, 
                ground_truth: str, 
                query: str, 
                response: str
            ): ...

        def __init__(
                self, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                *, 
                coherence_threshold: int = 3, 
                f1_score_threshold: float = 0.5, 
                fluency_threshold: int = 3, 
                groundedness_threshold: int = 3, 
                relevance_threshold: int = 3, 
                similarity_threshold: int = 3, 
                **kwargs: Any
            ): ...


    class azure.ai.evaluation.RelevanceEvaluator(PromptyEvaluatorBase):
        id = azureai://built-in/evaluators/relevance

        @overload
        def __call__(
                self, 
                *, 
                query: str, 
                response: str
            ) -> Dict[str, Union[str, float]]: ...

        @overload
        def __call__(
                self, 
                *, 
                conversation: Conversation
            ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]: ...

        @override
        def __init__(
                self, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                *, 
                credential = ..., 
                is_reasoning_model: bool = ..., 
                threshold = 3, 
                **kwargs
            ): ...


    @experimental
    class azure.ai.evaluation.ResponseCompletenessEvaluator(PromptyEvaluatorBase[Union[str, float]]):
        id = azureai://built-in/evaluators/response_completeness

        @overload
        def __call__(
                self, 
                *, 
                ground_truth: str, 
                response: str
            ) -> Dict[str, Union[str, float]]: ...

        @overload
        def __call__(
                self, 
                *, 
                conversation: Conversation
            ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]: ...

        @override
        def __init__(
                self, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                *, 
                credential = ..., 
                threshold: Optional[float] = _DEFAULT_COMPLETENESS_THRESHOLD, 
                **kwargs
            ): ...


    class azure.ai.evaluation.RetrievalEvaluator(PromptyEvaluatorBase[Union[str, float]]):
        id = azureai://built-in/evaluators/retrieval

        @overload
        def __call__(
                self, 
                *, 
                context: str, 
                query: str
            ) -> Dict[str, Union[str, float]]: ...

        @overload
        def __call__(
                self, 
                *, 
                conversation: Conversation
            ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]: ...

        @override
        def __init__(
                self, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                *, 
                credential = ..., 
                is_reasoning_model: bool = ..., 
                threshold: float = 3, 
                **kwargs
            ) -> Callable: ...


    class azure.ai.evaluation.RougeScoreEvaluator(EvaluatorBase):
        id = azureai://built-in/evaluators/rouge_score

        @overload
        def __call__(
                self, 
                *, 
                ground_truth: str, 
                response: str
            ) -> Dict[str, float]: ...

        @override
        def __init__(
                self, 
                rouge_type: RougeType, 
                *, 
                f1_score_threshold: float = 0.5, 
                precision_threshold: float = 0.5, 
                recall_threshold: float = 0.5
            ): ...


    class azure.ai.evaluation.RougeType(str, Enum):
        ROUGE_1 = "rouge1"
        ROUGE_2 = "rouge2"
        ROUGE_3 = "rouge3"
        ROUGE_4 = "rouge4"
        ROUGE_5 = "rouge5"
        ROUGE_L = "rougeL"


    @experimental
    class azure.ai.evaluation.SelfHarmEvaluator(RaiServiceEvaluatorBase[Union[str, float]]):
        id = azureai://built-in/evaluators/self_harm

        @overload
        def __call__(
                self, 
                *, 
                query: str, 
                response: str
            ) -> Dict[str, Union[str, float]]: ...

        @overload
        def __call__(
                self, 
                *, 
                conversation: Conversation
            ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]: ...

        @override
        def __init__(
                self, 
                credential: TokenCredential, 
                azure_ai_project: Union[str, AzureAIProject], 
                *, 
                threshold: int = 3, 
                **kwargs
            ): ...


    @experimental
    class azure.ai.evaluation.SexualEvaluator(RaiServiceEvaluatorBase[Union[str, float]]):
        id = azureai://built-in/evaluators/sexual

        @overload
        def __call__(
                self, 
                *, 
                query: str, 
                response: str
            ) -> Dict[str, Union[str, float]]: ...

        @overload
        def __call__(
                self, 
                *, 
                conversation: Conversation
            ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]: ...

        @override
        def __init__(
                self, 
                credential: TokenCredential, 
                azure_ai_project: Union[str, AzureAIProject], 
                *, 
                threshold: int = 3, 
                **kwargs
            ): ...


    class azure.ai.evaluation.SimilarityEvaluator(PromptyEvaluatorBase):
        id = azureai://built-in/evaluators/similarity

        @overload
        def __call__(
                self, 
                *, 
                ground_truth: str, 
                query: str, 
                response: str
            ) -> Dict[str, float]: ...

        @override
        def __init__(
                self, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                *, 
                credential = ..., 
                is_reasoning_model: bool = ..., 
                threshold = 3, 
                **kwargs
            ): ...


    @experimental
    class azure.ai.evaluation.TaskAdherenceEvaluator(PromptyEvaluatorBase[Union[str, float]]):
        id = azureai://built-in/evaluators/task_adherence

        @overload
        def __call__(
                self, 
                *, 
                query: Union[str, List[dict]], 
                response: Union[str, List[dict]], 
                tool_definitions: Optional[Union[dict, List[dict]]] = ...
            ) -> Dict[str, Union[str, float]]: ...

        @override
        def __init__(
                self, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                *, 
                credential = ..., 
                threshold = _DEFAULT_TASK_ADHERENCE_SCORE, 
                **kwargs
            ): ...


    @experimental
    class azure.ai.evaluation.ToolCallAccuracyEvaluator(PromptyEvaluatorBase[Union[str, float]]):
        id = azureai://built-in/evaluators/tool_call_accuracy

        @overload
        def __call__(
                self, 
                *, 
                query: Union[str, List[dict]], 
                response: Union[str, List[dict]] = ..., 
                tool_calls: Union[dict, List[dict]] = ..., 
                tool_definitions: Union[dict, List[dict]]
            ) -> Dict[str, Union[str, float]]: ...

        @override
        def __init__(
                self, 
                model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
                *, 
                credential = ..., 
                threshold = _DEFAULT_TOOL_CALL_ACCURACY_SCORE, 
                **kwargs
            ): ...


    @experimental
    class azure.ai.evaluation.UngroundedAttributesEvaluator(RaiServiceEvaluatorBase[Union[str, bool]]):
        id = azureai://built-in/evaluators/ungrounded_attributes

        @overload
        def __call__(
                self, 
                *, 
                context: str, 
                query: str, 
                response: str
            ) -> Dict[str, Union[str, float]]: ...

        @override
        def __init__(
                self, 
                credential: TokenCredential, 
                azure_ai_project: Union[str, AzureAIProject], 
                **kwargs: Any
            ): ...


    @experimental
    class azure.ai.evaluation.ViolenceEvaluator(RaiServiceEvaluatorBase[Union[str, float]]):
        id = azureai://built-in/evaluators/violence

        @overload
        def __call__(
                self, 
                *, 
                query: str, 
                response: str
            ) -> Dict[str, Union[str, float]]: ...

        @overload
        def __call__(
                self, 
                *, 
                conversation: Conversation
            ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]: ...

        @override
        def __init__(
                self, 
                credential: TokenCredential, 
                azure_ai_project: Union[str, AzureAIProject], 
                *, 
                threshold: int = 3, 
                **kwargs
            ): ...


namespace azure.ai.evaluation.red_team

    @experimental
    class azure.ai.evaluation.red_team.AttackStrategy(Enum):
        AnsiAttack = "ansi_attack"
        AsciiArt = "ascii_art"
        AsciiSmuggler = "ascii_smuggler"
        Atbash = "atbash"
        Base64 = "base64"
        Baseline = "baseline"
        Binary = "binary"
        Caesar = "caesar"
        CharSwap = "char_swap"
        CharacterSpace = "character_space"
        Crescendo = "crescendo"
        DIFFICULT = "difficult"
        Diacritic = "diacritic"
        EASY = "easy"
        Flip = "flip"
        IndirectJailbreak = "indirect_jailbreak"
        Jailbreak = "jailbreak"
        Leetspeak = "leetspeak"
        MODERATE = "moderate"
        Morse = "morse"
        MultiTurn = "multi_turn"
        ROT13 = "rot13"
        StringJoin = "string_join"
        SuffixAppend = "suffix_append"
        Tense = "tense"
        UnicodeConfusable = "unicode_confusable"
        UnicodeSubstitution = "unicode_substitution"
        Url = "url"


    @experimental
    class azure.ai.evaluation.red_team.RedTeam:

        def __init__(
                self, 
                azure_ai_project: Union[dict, str], 
                credential: TokenCredential, 
                *, 
                application_scenario: Optional[str] = ..., 
                attack_success_thresholds: Optional[Dict[RiskCategory, int]] = ..., 
                custom_attack_seed_prompts: Optional[str] = ..., 
                language: SupportedLanguages = SupportedLanguages.English, 
                num_objectives: int = 10, 
                output_dir = ".", 
                risk_categories: Optional[List[RiskCategory]] = ..., 
                **kwargs
            ): ...

        async def scan(
                self, 
                target: Union[Callable, AzureOpenAIModelConfiguration, OpenAIModelConfiguration, PromptChatTarget], 
                *, 
                application_scenario: Optional[str] = ..., 
                attack_strategies: List[Union[AttackStrategy, List[AttackStrategy]]] = [], 
                max_parallel_tasks: int = 5, 
                output_path: Optional[Union[str, PathLike]] = ..., 
                parallel_execution: bool = True, 
                scan_name: Optional[str] = ..., 
                skip_evals: bool = False, 
                skip_upload: bool = False, 
                timeout: int = 3600, 
                **kwargs: Any
            ) -> RedTeamResult: ...


    @experimental
    class azure.ai.evaluation.red_team.RedTeamResult:

        def __init__(
                self, 
                scan_result: Optional[ScanResult] = None, 
                attack_details: Optional[List[AttackDetails]] = None
            ): ...

        def attack_simulation(self) -> str: ...

        def to_eval_qr_json_lines(self) -> str: ...

        def to_json(self) -> str: ...

        def to_scorecard(self) -> Optional[RedTeamingScorecard]: ...


    @experimental
    class azure.ai.evaluation.red_team.RiskCategory(str, Enum):
        CodeVulnerability = "code_vulnerability"
        HateUnfairness = "hate_unfairness"
        ProhibitedActions = "prohibited_actions"
        ProtectedMaterial = "protected_material"
        SelfHarm = "self_harm"
        SensitiveDataLeakage = "sensitive_data_leakage"
        Sexual = "sexual"
        TaskAdherence = "task_adherence"
        UngroundedAttributes = "ungrounded_attributes"
        Violence = "violence"


    @experimental
    class azure.ai.evaluation.red_team.SupportedLanguages(Enum):
        English = "en"
        French = "fr"
        German = "de"
        Italian = "it"
        Japanese = "ja"
        Korean = "ko"
        Portuguese = "pt"
        SimplifiedChinese = "zh-cn"
        Spanish = "es"


namespace azure.ai.evaluation.simulator

    @experimental
    class azure.ai.evaluation.simulator.AdversarialScenario(Enum):
        ADVERSARIAL_CODE_VULNERABILITY = "adv_code_vuln"
        ADVERSARIAL_CONTENT_GEN_GROUNDED = "adv_content_gen_grounded"
        ADVERSARIAL_CONTENT_GEN_UNGROUNDED = "adv_content_gen_ungrounded"
        ADVERSARIAL_CONTENT_PROTECTED_MATERIAL = "adv_content_protected_material"
        ADVERSARIAL_CONVERSATION = "adv_conversation"
        ADVERSARIAL_QA = "adv_qa"
        ADVERSARIAL_QA_DOCUMENTS = "adv_qa_documents"
        ADVERSARIAL_REWRITE = "adv_rewrite"
        ADVERSARIAL_SEARCH = "adv_search"
        ADVERSARIAL_SUMMARIZATION = "adv_summarization"
        ADVERSARIAL_UNGROUNDED_ATTRIBUTES = "adv_isa"


    @experimental
    class azure.ai.evaluation.simulator.AdversarialScenarioJailbreak(Enum):
        ADVERSARIAL_INDIRECT_JAILBREAK = "adv_xpia"


    @experimental
    class azure.ai.evaluation.simulator.AdversarialSimulator:

        async def __call__(
                self, 
                *, 
                api_call_delay_sec: int = 0, 
                api_call_retry_limit: int = 3, 
                api_call_retry_sleep_sec: int = 1, 
                concurrent_async_task: int = 3, 
                language: SupportedLanguages = SupportedLanguages.English, 
                max_conversation_turns: int = 1, 
                max_simulation_results: int = 3, 
                randomization_seed: Optional[int] = ..., 
                randomize_order: bool = True, 
                scenario: AdversarialScenario, 
                target: Callable, 
                **kwargs
            ) -> List[Dict[str, Any]]: ...

        def __init__(
                self, 
                *, 
                azure_ai_project: Union[str, AzureAIProject], 
                credential: TokenCredential
            ): ...

        def call_sync(
                self, 
                *, 
                api_call_delay_sec: int, 
                api_call_retry_limit: int, 
                api_call_retry_sleep_sec: int, 
                concurrent_async_task: int, 
                max_conversation_turns: int, 
                max_simulation_results: int, 
                scenario: AdversarialScenario, 
                target: Callable
            ) -> List[Dict[str, Any]]: ...


    @experimental
    class azure.ai.evaluation.simulator.DirectAttackSimulator:

        async def __call__(
                self, 
                *, 
                api_call_delay_sec: int = 0, 
                api_call_retry_limit: int = 3, 
                api_call_retry_sleep_sec: int = 1, 
                concurrent_async_task: int = 3, 
                max_conversation_turns: int = 1, 
                max_simulation_results: int = 3, 
                randomization_seed: Optional[int] = ..., 
                scenario: AdversarialScenario, 
                target: Callable
            ) -> Dict[str, [List[Dict[str, Any]]]]: ...

        def __init__(
                self, 
                *, 
                azure_ai_project: Union[str, AzureAIProject], 
                credential: TokenCredential
            ): ...


    @experimental
    class azure.ai.evaluation.simulator.IndirectAttackSimulator(AdversarialSimulator):

        async def __call__(
                self, 
                *, 
                api_call_delay_sec: int = 0, 
                api_call_retry_limit: int = 3, 
                api_call_retry_sleep_sec: int = 1, 
                concurrent_async_task: int = 3, 
                max_simulation_results: int = 3, 
                randomization_seed: Optional[int] = ..., 
                target: Callable, 
                **kwargs
            ) -> List[Dict[str, Any]]: ...

        def __init__(
                self, 
                *, 
                azure_ai_project: Union[str, AzureAIProject], 
                credential: TokenCredential
            ): ...

        def call_sync(
                self, 
                *, 
                api_call_delay_sec: int, 
                api_call_retry_limit: int, 
                api_call_retry_sleep_sec: int, 
                concurrent_async_task: int, 
                max_conversation_turns: int, 
                max_simulation_results: int, 
                scenario: AdversarialScenario, 
                target: Callable
            ) -> List[Dict[str, Any]]: ...


    @experimental
    class azure.ai.evaluation.simulator.Simulator:

        async def __call__(
                self, 
                *, 
                api_call_delay_sec: float = 1, 
                concurrent_async_tasks: int = 5, 
                conversation_turns: List[List[Union[str, Dict[str, Any]]]] = [], 
                max_conversation_turns: int = 5, 
                num_queries: int = 5, 
                query_response_generating_prompty: Optional[str] = ..., 
                query_response_generating_prompty_options: Dict[str, Any] = {}, 
                randomization_seed: Optional[int] = ..., 
                target: Callable, 
                tasks: List[str] = [], 
                text: str = "", 
                user_simulator_prompty: Optional[str] = ..., 
                user_simulator_prompty_options: Dict[str, Any] = {}, 
                **kwargs
            ) -> List[JsonLineChatProtocol]: ...

        def __init__(self, model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration]): ...


    class azure.ai.evaluation.simulator.SupportedLanguages(Enum):
        English = "en"
        French = "fr"
        German = "de"
        Italian = "it"
        Japanese = "ja"
        Korean = "ko"
        Portuguese = "pt"
        SimplifiedChinese = "zh-cn"
        Spanish = "es"


```
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, List, Optional, TypedDict
import json
from azure.ai.evaluation._common._experimental import experimental


# NOTE: The RedTeam* TypedDict classes below are being gradually deprecated in favor of
# the standard EvalRun* models from azure.ai.evaluation._common.onedp.models._models.
# New code should use EvalRunOutputItem instead of RedTeamOutputItem, etc.
# These TypedDicts are maintained for backward compatibility during the transition.


@experimental
class RiskCategorySummary(TypedDict):
    """Summary of attack success rates across risk categories.

    :param overall_asr: Overall attack success rate across all risk categories
    :type overall_asr: float
    :param overall_total: Total number of attacks across all risk categories
    :type overall_total: int
    :param overall_successful_attacks: Number of successful attacks across all risk categories
    :type overall_successful_attacks: int
    :param hate_unfairness_asr: Attack success rate for hate/unfairness risk category
    :type hate_unfairness_asr: float
    :param hate_unfairness_total: Total number of attacks for hate/unfairness risk category
    :type hate_unfairness_total: int
    :param hate_unfairness_successful_attacks: Number of successful attacks for hate/unfairness risk category
    :type hate_unfairness_successful_attacks: int
    :param violence_asr: Attack success rate for violence risk category
    :type violence_asr: float
    :param violence_total: Total number of attacks for violence risk category
    :type violence_total: int
    :param violence_successful_attacks: Number of successful attacks for violence risk category
    :type violence_successful_attacks: int
    :param sexual_asr: Attack success rate for sexual risk category
    :type sexual_asr: float
    :param sexual_total: Total number of attacks for sexual risk category
    :type sexual_total: int
    :param sexual_successful_attacks: Number of successful attacks for sexual risk category
    :type sexual_successful_attacks: int
    :param self_harm_asr: Attack success rate for self-harm risk category
    :type self_harm_asr: float
    :param self_harm_total: Total number of attacks for self-harm risk category
    :type self_harm_total: int
    :param self_harm_successful_attacks: Number of successful attacks for self-harm risk category
    :type self_harm_successful_attacks: int
    """

    overall_asr: float
    overall_total: int
    overall_successful_attacks: int
    hate_unfairness_asr: float
    hate_unfairness_total: int
    hate_unfairness_successful_attacks: int
    violence_asr: float
    violence_total: int
    violence_successful_attacks: int
    sexual_asr: float
    sexual_total: int
    sexual_successful_attacks: int
    self_harm_asr: float
    self_harm_total: int
    self_harm_successful_attacks: int


@experimental
class AttackTechniqueSummary(TypedDict):
    """Summary of attack success rates across complexity levels.

    :param overall_asr: Overall attack success rate across all complexity levels
    :type overall_asr: float
    :param overall_total: Total number of attacks across all complexity levels
    :type overall_total: int
    :param overall_successful_attacks: Number of successful attacks across all complexity levels
    :type overall_successful_attacks: int
    :param baseline_asr: Attack success rate for baseline complexity level
    :type baseline_asr: float
    :param baseline_total: Total number of attacks for baseline complexity level
    :type baseline_total: int
    :param baseline_successful_attacks: Number of successful attacks for baseline complexity level
    :type baseline_successful_attacks: int
    :param easy_complexity_asr: Attack success rate for easy complexity level
    :type easy_complexity_asr: float
    :param easy_complexity_total: Total number of attacks for easy complexity level
    :type easy_complexity_total: int
    :param easy_complexity_successful_attacks: Number of successful attacks for easy complexity level
    :type easy_complexity_successful_attacks: int
    :param moderate_complexity_asr: Attack success rate for moderate complexity level
    :type moderate_complexity_asr: float
    :param moderate_complexity_total: Total number of attacks for moderate complexity level
    :type moderate_complexity_total: int
    :param moderate_complexity_successful_attacks: Number of successful attacks for moderate complexity level
    :type moderate_complexity_successful_attacks: int
    :param difficult_complexity_asr: Attack success rate for difficult complexity level
    :type difficult_complexity_asr: float
    :param difficult_complexity_total: Total number of attacks for difficult complexity level
    :type difficult_complexity_total: int
    :param difficult_complexity_successful_attacks: Number of successful attacks for difficult complexity level
    :type difficult_complexity_successful_attacks: int
    """

    overall_asr: float
    overall_total: int
    overall_successful_attacks: int
    baseline_asr: float
    baseline_total: int
    baseline_successful_attacks: int
    easy_complexity_asr: float
    easy_complexity_total: int
    easy_complexity_successful_attacks: int
    moderate_complexity_asr: float
    moderate_complexity_total: int
    moderate_complexity_successful_attacks: int
    difficult_complexity_asr: float
    difficult_complexity_total: int
    difficult_complexity_successful_attacks: int


@experimental
class JointRiskAttackSummaryItem(TypedDict):
    """Summary of attack success rates for a specific risk category across complexity levels.

    :param risk_category: The risk category being summarized
    :type risk_category: str
    :param baseline_asr: Attack success rate for baseline complexity level
    :type baseline_asr: float
    :param easy_complexity_asr: Attack success rate for easy complexity level
    :type easy_complexity_asr: float
    :param moderate_complexity_asr: Attack success rate for moderate complexity level
    :type moderate_complexity_asr: float
    :param difficult_complexity_asr: Attack success rate for difficult complexity level
    :type difficult_complexity_asr: float
    """

    risk_category: str
    baseline_asr: float
    easy_complexity_asr: float
    moderate_complexity_asr: float
    difficult_complexity_asr: float


@experimental
class RedTeamingScorecard(TypedDict):
    """TypedDict representation of a Red Team Agent scorecard with the updated structure.

    :param risk_category_summary: Overall metrics by risk category
    :type risk_category_summary: List[RiskCategorySummary]
    :param attack_technique_summary: Overall metrics by attack technique complexity
    :type attack_technique_summary: List[AttackTechniqueSummary]
    :param joint_risk_attack_summary: Detailed metrics by risk category and complexity level
    :type joint_risk_attack_summary: List[JointRiskAttackSummaryItem]
    :param detailed_joint_risk_attack_asr: Detailed ASR information broken down by complexity level, risk category, and converter
    :type detailed_joint_risk_attack_asr: Dict[str, Dict[str, Dict[str, float]]]
    """

    risk_category_summary: List[RiskCategorySummary]
    attack_technique_summary: List[AttackTechniqueSummary]
    joint_risk_attack_summary: List[JointRiskAttackSummaryItem]
    detailed_joint_risk_attack_asr: Dict[str, Dict[str, Dict[str, float]]]


@experimental
class AttackObjectiveSource(TypedDict):
    """Information about how attack objectives were generated.

    :param application_scenario: The application scenario used for generating attack objectives
    :type application_scenario: str
    :param risk_categories: List of risk categories targeted by the attack objectives
    :type risk_categories: List[str]
    :param custom_attack_seed_prompts: Custom prompts used to seed attack objective generation
    :type custom_attack_seed_prompts: str
    :param policy_document: Policy document used for generating attack objectives
    :type policy_document: str
    """

    application_scenario: str
    risk_categories: List[str]
    custom_attack_seed_prompts: str
    policy_document: str


@experimental
class RedTeamingParameters(TypedDict):
    """TypedDict representation of parameters used in a red team evaluation with the updated structure.

    :param attack_objective_generated_from: Information about the source of attack objectives
    :type attack_objective_generated_from: AttackObjectiveSource
    :param attack_complexity: List of complexity levels used in the attacks
    :type attack_complexity: List[str]
    :param techniques_used: Dictionary mapping complexity levels to lists of converter techniques used
    :type techniques_used: Dict[str, List[str]]
    :param attack_success_thresholds: Thresholds used for determining attack success per risk category
    :type attack_success_thresholds: Dict[str, Any]
    """

    attack_objective_generated_from: AttackObjectiveSource
    attack_complexity: List[str]
    techniques_used: Dict[str, List[str]]
    attack_success_thresholds: Dict[str, Dict[str, int]]


@experimental
class RiskAssessment(TypedDict):
    """Assessment of content safety risks in a conversation.

    :param violence: Assessment of violence-related content
    :type violence: Dict[str, str]
    :param sexual: Assessment of sexual content
    :type sexual: Dict[str, str]
    :param self_harm: Assessment of self-harm content
    :type self_harm: Dict[str, str]
    :param hate_unfair: Assessment of hate or unfairness content
    :type hate_unfair: Dict[str, str]
    """

    violence: Dict[str, str]
    sexual: Dict[str, str]
    self_harm: Dict[str, str]
    hate_unfair: Dict[str, str]


@experimental
class AttackDetails(TypedDict, total=False):
    """TypedDict representation of a simulated conversation in a red team evaluation.

    :param attack_success: Whether the attack was successful
    :type attack_success: Optional[bool]
    :param attack_technique: The attack technique used in the conversation
    :type attack_technique: str
    :param attack_complexity: The complexity level of the attack
    :type attack_complexity: str
    :param risk_category: The risk category targeted by the attack
    :type risk_category: str
    :param conversation: List of messages exchanged in the conversation
    :type conversation: List[Dict[str, str]]
    :param risk_assessment: Dictionary containing content safety assessment for the conversation
    :type risk_assessment: Optional[RiskAssessment]
    :param attack_success_threshold: The threshold value used to determine attack success
    :type attack_success_threshold: Optional[int]
    :param risk_sub_type: Optional risk sub-category/sub-type for the attack
    :type risk_sub_type: Optional[str]
    """

    attack_success: Optional[bool]
    attack_technique: str
    attack_complexity: str
    risk_category: str
    conversation: List[Dict[str, str]]
    risk_assessment: Optional[RiskAssessment]
    attack_success_threshold: Optional[int]
    risk_sub_type: Optional[str]


@experimental
class RedTeamOutputResultProperties(TypedDict, total=False):
    """Additional metadata captured for each evaluation result."""

    attack_success: Optional[bool]
    attack_success_threshold: Optional[int]
    attack_technique: str
    attack_complexity: str
    risk_category: str
    risk_assessment: Optional[Dict[str, Any]]
    reason: Optional[str]
    severity_label: Optional[str]
    metadata: Optional[Dict[str, Any]]


@experimental
class EvaluationRunOutputItemMessage(TypedDict, total=False):
    """Representation of a single message within an evaluation sample."""

    role: str
    content: Any
    name: Optional[str]
    tool_calls: Optional[List[Dict[str, Any]]]


@experimental
class RedTeamRunOutputItemResult(TypedDict, total=False):
    """Flattened evaluation result for a single risk category.

    :param passed: Indicates whether the attack was unsuccessful (True) or successful (False).
                   In the context of attack success rate (ASR), passed=True means the system
                   successfully defended against the attack, while passed=False means the attack
                   succeeded in compromising the system.
    :type passed: Optional[bool]
    :param label: String label "pass" or "fail" that aligns with the passed field
    :type label: Optional[str]
    """

    # Should extend EvaluationRunOutputItemResult

    object: str
    type: str
    name: str
    passed: Optional[bool]
    label: Optional[str]
    score: Optional[float]
    metric: Optional[str]
    threshold: Optional[float]
    reason: Optional[str]
    properties: RedTeamOutputResultProperties


@experimental
class RedTeamDatasourceItem(TypedDict, total=False):
    """Metadata about the datasource item that produced this conversation."""

    id: Optional[str]
    input_data: Dict[str, Any]


@experimental
class RedTeamRunOutputItemSample(TypedDict, total=False):
    """Sample payload containing the red team conversation.

    :param error: Error information from either the evaluation step or while calling the target system.
                  Contains details about any failures that occurred during the attack simulation or
                  evaluation process.
    :type error: Optional[Dict[str, Any]]
    """

    # Should extend EvaluationRunOutputItemSample

    object: str
    input: List[EvaluationRunOutputItemMessage]
    output: List[EvaluationRunOutputItemMessage]
    finish_reason: Optional[str]
    model: Optional[str]
    error: Optional[Dict[str, Any]]
    usage: Optional[Dict[str, Any]]
    seed: Optional[int]
    temperature: Optional[float]
    top_p: Optional[float]
    max_completion_tokens: Optional[float]
    metadata: Optional[Dict[str, Any]]


@experimental
class RedTeamOutputItem(TypedDict, total=False):
    """Structured representation of a conversation and its evaluation artifacts.

    DEPRECATED: This TypedDict duplicates the EvalRunOutputItem model from
    azure.ai.evaluation._common.onedp.models._models. New code should use
    EvalRunOutputItem directly instead of this TypedDict wrapper.
    """

    object: str
    id: str
    created_time: int
    status: str
    datasource_item_id: Optional[str]
    datasource_item: Optional[RedTeamDatasourceItem]
    sample: RedTeamRunOutputItemSample
    results: List[RedTeamRunOutputItemResult]


@experimental
class ScanResult(TypedDict):
    """TypedDict representation of a Red Team Agent evaluation result with the updated structure.

    :param scorecard: Scorecard containing summary and detailed ASR information
    :type scorecard: RedTeamingScorecard
    :param parameters: Parameters containing metadata about the evaluation run
    :type parameters: RedTeamingParameters
    :param attack_details: List of AttackDetails objects representing the conversations in the evaluation
    :type attack_details: List[AttackDetails]
    :param AOAI_Compatible_Row_Results: List of evaluation results for each risk category
    :type AOAI_Compatible_Row_Results: Optional[List[RedTeamRunOutputItemResult]]
    :param AOAI_Compatible_Summary: The evaluation run metadata in eval.run format
    :type AOAI_Compatible_Summary: Optional[RedTeamRun]
    :param studio_url: Optional URL for the studio
    :type studio_url: Optional[str]
    """

    scorecard: RedTeamingScorecard
    parameters: RedTeamingParameters
    attack_details: List[AttackDetails]
    AOAI_Compatible_Row_Results: Optional[List[RedTeamRunOutputItemResult]]
    AOAI_Compatible_Summary: Optional["RedTeamRun"]
    studio_url: Optional[str]


@experimental
class ResultCount(TypedDict):
    """Count of evaluation results by status.

    :param total: Total number of evaluation results
    :type total: int
    :param passed: Number of evaluation results where the attack was unsuccessful (system defended successfully).
                   In the context of attack success rate (ASR), this represents attacks that failed.
    :type passed: int
    :param failed: Number of evaluation results where the attack was successful (system was compromised).
                   In the context of attack success rate (ASR), this represents successful attacks.
    :type failed: int
    :param errored: Number of evaluation results that failed to process due to errors.
                    Calculated from rows where the sample's error property is set, indicating failures
                    during the attack simulation or evaluation step.
    :type errored: int
    """

    total: int
    passed: int
    failed: int
    errored: int


@experimental
class PerTestingCriteriaResult(TypedDict, total=False):
    """Result count for a specific testing criteria.

    :param testing_criteria: The name of the testing criteria (e.g., risk category)
    :type testing_criteria: str
    :param attack_strategy: The attack strategy used (optional, for attack strategy summaries)
    :type attack_strategy: Optional[str]
    :param passed: Number of results where the attack was unsuccessful for this criteria.
                   In the context of attack success rate (ASR), this represents attacks that failed
                   to compromise the system for this specific testing criteria.
    :type passed: int
    :param failed: Number of results where the attack was successful for this criteria.
                   In the context of attack success rate (ASR), this represents successful attacks
                   for this specific testing criteria.
    :type failed: int
    """

    testing_criteria: str
    attack_strategy: Optional[str]
    passed: int
    failed: int


@experimental
class DataSourceItemGenerationParams(TypedDict, total=False):
    """Parameters for data source item generation.

    :param type: Type of data source generation (e.g., "red_team")
    :type type: str
    :param attack_strategies: List of attack strategies used
    :type attack_strategies: List[str]
    :param num_turns: Number of turns in the conversation
    :type num_turns: int
    """

    type: str
    attack_strategies: List[str]
    num_turns: int


@experimental
class DataSource(TypedDict, total=False):
    """Data source information for the red team evaluation.

    :param type: Type of data source (e.g., "azure_ai_red_team")
    :type type: str
    :param target: Target configuration for the data source
    :type target: Dict[str, Any]
    :param item_generation_params: Parameters used for generating data items
    :type item_generation_params: DataSourceItemGenerationParams
    """

    type: str
    target: Dict[str, Any]
    item_generation_params: DataSourceItemGenerationParams


@experimental
class OutputItemsList(TypedDict):
    """Wrapper for list of output items.

    :param object: Object type identifier (always "list")
    :type object: str
    :param data: List of red team output items
    :type data: List[RedTeamOutputItem]
    """

    object: str
    data: List[RedTeamOutputItem]


@experimental
class RedTeamRun(TypedDict, total=False):
    """TypedDict representation of a Red Team evaluation run in eval.run format.

    :param object: Object type identifier (always "eval.run")
    :type object: str
    :param id: Unique identifier for the run
    :type id: str
    :param eval_id: Identifier for the evaluation experiment
    :type eval_id: str
    :param created_at: Timestamp when the run was created (Unix epoch seconds)
    :type created_at: int
    :param status: Status of the run (e.g., "completed", "failed", "in_progress")
    :type status: str
    :param name: Display name for the run
    :type name: str
    :param report_url: URL to view the run report in Azure AI Studio
    :type report_url: Optional[str]
    :param data_source: Information about the data source used for the evaluation
    :type data_source: DataSource
    :param metadata: Additional metadata for the run
    :type metadata: Dict[str, Any]
    :param result_counts: Aggregated counts of evaluation results
    :type result_counts: ResultCount
    :param per_model_usage: Usage statistics per model (if applicable)
    :type per_model_usage: List[Any]
    :param per_testing_criteria_results: Results aggregated by testing criteria
    :type per_testing_criteria_results: List[PerTestingCriteriaResult]
    :param output_items: Wrapped list of output items from the evaluation
    :type output_items: OutputItemsList
    :param conversations: Optional list of attack details/conversations
    :type conversations: List[AttackDetails]
    """

    object: str
    id: str
    eval_id: str
    created_at: int
    status: str
    name: str
    report_url: Optional[str]
    data_source: DataSource
    metadata: Dict[str, Any]
    result_counts: ResultCount
    per_model_usage: List[Any]
    per_testing_criteria_results: List[PerTestingCriteriaResult]
    output_items: OutputItemsList
    conversations: List[AttackDetails]


@experimental
class RedTeamResult:
    def __init__(self, scan_result: Optional[ScanResult] = None, attack_details: Optional[List[AttackDetails]] = None):
        self.scan_result = scan_result
        self.attack_details = attack_details

    def to_json(self) -> str:
        """
        Converts a RedTeamResult object to a JSON-serializable dictionary.

        :returns: A string containing the RedTeamResult in JSON format.
        :rtype: str
        """
        return json.dumps(self.scan_result) if self.scan_result else ""

    def to_scorecard(self) -> Optional[RedTeamingScorecard]:
        """Extracts the scorecard from a RedTeamResult object."""
        return self.scan_result.get("scorecard", None) if self.scan_result else None

    def to_eval_qr_json_lines(self) -> List[str]:
        """Converts conversations in messages format to query-response format suitable for evaluation.

        The output format follows the JSONL pattern with each line containing:

        .. code-block:: javascript

            {
                "query": "user message content",
                "response": "assistant message content",
                "risk_category": "risk category",
                "attack_strategy": "strategy name",
                "attack_complexity": "complexity level",
                "attack_success": "true|false", // (if available from evaluation)
                "category": "risk category", // (if available from evaluation)
                "severity_level": "low|medium|high", // (if available from evaluation)
                "threshold": "threshold value" // (if available from evaluation)
            }

        :returns: A list of strings containing query-response pairs in JSONL format.
        :rtype: List[str]
        """
        if not self.attack_details:
            return []

        result_lines = []

        for conversation in self.attack_details:
            messages = conversation.get("conversation", [])
            attack_technique = conversation.get("attack_technique", "")
            attack_complexity = conversation.get("attack_complexity", "")
            risk_category = conversation.get("risk_category", "")
            attack_success = conversation.get("attack_success")
            risk_assessment: Any = conversation.get("risk_assessment", {})

            for i in range(0, len(messages) - 1, 2):
                if i + 1 < len(messages):
                    user_msg = messages[i]
                    assistant_msg = messages[i + 1]

                    if user_msg.get("role") == "user" and assistant_msg.get("role") == "assistant":
                        # Create the base query-response pair
                        qr_pair = {
                            "query": user_msg.get("content", ""),
                            "response": assistant_msg.get("content", ""),
                            "risk_category": risk_category,
                            "attack_strategy": attack_technique,
                            "attack_complexity": attack_complexity,
                        }

                        # Add evaluation data if available
                        if attack_success is not None:
                            qr_pair["attack_success"] = str(attack_success).lower()

                        # Add risk assessment data if available
                        for category, assessment in risk_assessment.items() if risk_assessment else {}:
                            if assessment and assessment.get("severity_label", None):
                                qr_pair["category"] = category
                                qr_pair["severity_level"] = assessment.get("severity_label", "").lower()
                                # Add threshold if available in the future

                        result_lines.append(json.dumps(qr_pair))

        return result_lines

    def attack_simulation(self) -> str:
        """
        Returns the attack simulation data in a human-readable format.
        :returns: A string containing the attack simulation data in a human-readable format.
        :rtype: str
        """
        if not self.attack_details:
            return ""

        result_lines = []

        for conversation in self.attack_details:
            messages = conversation.get("conversation", [])
            attack_technique = conversation.get("attack_technique", "")
            attack_complexity = conversation.get("attack_complexity", "")
            risk_category = conversation.get("risk_category", "")
            attack_success = conversation.get("attack_success")
            risk_assessment: Any = conversation.get("risk_assessment", {})

            result_lines.append(f"Attack Technique: {attack_technique}")
            result_lines.append(f"Attack Complexity: {attack_complexity}")
            result_lines.append(f"Risk Category: {risk_category}")
            result_lines.append("")

            for i in range(0, len(messages) - 1, 2):
                if i + 1 < len(messages):
                    user_msg = messages[i]
                    assistant_msg = messages[i + 1]

                    if user_msg.get("role") == "user" and assistant_msg.get("role") == "assistant":
                        result_lines.append(f"User: {user_msg.get('content', '')}")
                        result_lines.append(f"Assistant: {assistant_msg.get('content', '')}")
                        result_lines.append("")

            if attack_success is not None:
                result_lines.append(f"Attack Success: {'Successful' if attack_success else 'Failed'}")
                result_lines.append("")

            for category, assessment in risk_assessment.items() if risk_assessment else {}:
                if assessment and assessment.get("severity_label", None):
                    result_lines.append(f"Category: {category}")
                    result_lines.append(f"Severity Level: {assessment.get('severity_label', '')}")
                    result_lines.append("")

        return "\n".join(result_lines)

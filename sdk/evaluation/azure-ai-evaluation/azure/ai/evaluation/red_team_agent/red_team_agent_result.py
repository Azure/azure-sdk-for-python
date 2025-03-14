# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, List, Optional,  TypedDict

class RiskCategorySummary(TypedDict):
    """Summary of attack success rates across risk categories."""
    overall_asr: float
    hate_unfairness_asr: float
    violence_asr: float
    sexual_asr: float
    self_harm_asr: float

class AttackTechniqueSummary(TypedDict):
    """Summary of attack success rates across complexity levels."""
    baseline_asr: float
    easy_complexity_asr: float
    moderate_complexity_asr: float
    difficult_complexity_asr: float

class JointRiskAttackSummaryItem(TypedDict):
    """Summary of attack success rates for a specific risk category across complexity levels."""
    risk_category: str
    baseline_asr: float
    easy_complexity_asr: float
    moderate_complexity_asr: float
    difficult_complexity_asr: float

class RedTeamingScorecard(TypedDict):
    """TypedDict representation of a Red Team Agent scorecard with the updated structure.
    
    The scorecard contains four main sections:
    - risk_category_summary: Overall metrics by risk category
    - attack_technique_summary: Overall metrics by attack technique complexity
    - joint_risk_attack_summary: Detailed metrics by risk category and complexity level
    - detailed_joint_risk_attack_asr: Detailed ASR information broken down by complexity level, risk category, and converter
    """
    risk_category_summary: List[RiskCategorySummary]
    attack_technique_summary: List[AttackTechniqueSummary]
    joint_risk_attack_summary: List[JointRiskAttackSummaryItem]
    detailed_joint_risk_attack_asr: Dict[str, Dict[str, Dict[str, float]]]

class AttackObjectiveSource(TypedDict):
    """Information about how attack objectives were generated."""
    application_scenario: str
    risk_categories: List[str]
    custom_attack_seed_prompts: str
    policy_document: str

class RedTeamingParameters(TypedDict):
    """TypedDict representation of parameters used in a red team evaluation with the updated structure.
    
    This class defines the structure for capturing metadata about an evaluation run, including:
    - attack_objective_generated_from: Information about the source of attack objectives
    - attack_complexity: List of complexity levels used in the attacks (e.g., "Easy", "Moderate", "Difficult")
    - techniques_used: Dictionary mapping complexity levels to lists of converter techniques used
    """
    attack_objective_generated_from: AttackObjectiveSource
    attack_complexity: List[str]
    techniques_used: Dict[str, List[str]]

class RiskAssessment(TypedDict):
    """Assessment of content safety risks in a conversation."""
    violence: Dict[str, str]
    sexual: Dict[str, str]
    self_harm: Dict[str, str]
    hate_unfair: Dict[str, str]

class SimulatedConversation(TypedDict):
    """TypedDict representation of a simulated conversation in a red team evaluation.
    
    This class defines the structure for capturing information about a simulated conversation, including:
    - attack_success: Whether the attack was successful
    - attack_technique: The attack technique used in the conversation
    - attack_complexity: The complexity level of the attack
    - conversation: List of messages exchanged in the conversation
    - risk_assessment: Dictionary containing content safety assessment for the conversation
    """
    attack_success: bool
    attack_technique: str
    attack_complexity: str
    conversation: List[Dict[str, str]]
    risk_assessment: RiskAssessment

class RedTeamAgentResult(TypedDict):
    """TypedDict representation of a Red Team Agent evaluation result with the updated structure.

    This class defines the structure for capturing the results of a red team evaluation, including:
    - redteaming_scorecard: Scorecard containing summary and detailed ASR information
    - redteaming_simulation_parameters: Parameters containing metadata about the evaluation run
    - redteaming_simulation_data: List of SimulatedConversation objects representing the conversations in the evaluation
    """
    redteaming_scorecard: RedTeamingScorecard
    redteaming_simulation_parameters: RedTeamingSimulationParameters
    redteaming_simulation_data: List[SimulatedConversation]
    studio_url: Optional[str]
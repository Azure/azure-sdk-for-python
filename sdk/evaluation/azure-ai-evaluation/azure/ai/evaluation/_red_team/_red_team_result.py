# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, List, Optional,  TypedDict
import json

class _RiskCategorySummary(TypedDict):
    """Summary of attack success rates across risk categories."""
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

class _AttackTechniqueSummary(TypedDict):
    """Summary of attack success rates across complexity levels."""
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

class _JointRiskAttackSummaryItem(TypedDict):
    """Summary of attack success rates for a specific risk category across complexity levels."""
    risk_category: str
    baseline_asr: float
    easy_complexity_asr: float
    moderate_complexity_asr: float
    difficult_complexity_asr: float

class _RedTeamingScorecard(TypedDict):
    """TypedDict representation of a Red Team Agent scorecard with the updated structure.
    
    The scorecard contains four main sections:
    - risk_category_summary: Overall metrics by risk category
    - attack_technique_summary: Overall metrics by attack technique complexity
    - joint_risk_attack_summary: Detailed metrics by risk category and complexity level
    - detailed_joint_risk_attack_asr: Detailed ASR information broken down by complexity level, risk category, and converter
    """
    risk_category_summary: List[_RiskCategorySummary]
    attack_technique_summary: List[_AttackTechniqueSummary]
    joint_risk_attack_summary: List[_JointRiskAttackSummaryItem]
    detailed_joint_risk_attack_asr: Dict[str, Dict[str, Dict[str, float]]]

class _AttackObjectiveSource(TypedDict):
    """Information about how attack objectives were generated."""
    application_scenario: str
    risk_categories: List[str]
    custom_attack_seed_prompts: str
    policy_document: str

class _RedTeamingParameters(TypedDict):
    """TypedDict representation of parameters used in a red team evaluation with the updated structure.
    
    This class defines the structure for capturing metadata about an evaluation run, including:
    - attack_objective_generated_from: Information about the source of attack objectives
    - attack_complexity: List of complexity levels used in the attacks (e.g., "Easy", "Moderate", "Difficult")
    - techniques_used: Dictionary mapping complexity levels to lists of converter techniques used
    """
    attack_objective_generated_from: _AttackObjectiveSource
    attack_complexity: List[str]
    techniques_used: Dict[str, List[str]]

class _RiskAssessment(TypedDict):
    """Assessment of content safety risks in a conversation."""
    violence: Dict[str, str]
    sexual: Dict[str, str]
    self_harm: Dict[str, str]
    hate_unfair: Dict[str, str]

class _Conversation(TypedDict):
    """TypedDict representation of a simulated conversation in a red team evaluation.
    
    This class defines the structure for capturing information about a simulated conversation, including:
    - attack_success: Whether the attack was successful
    - attack_technique: The attack technique used in the conversation
    - attack_complexity: The complexity level of the attack
    - conversation: List of messages exchanged in the conversation
    - risk_assessment: Dictionary containing content safety assessment for the conversation
    """
    attack_success: Optional[bool]
    attack_technique: str
    attack_complexity: str
    risk_category: str
    conversation: List[Dict[str, str]]
    risk_assessment: Optional[_RiskAssessment]

class _RedTeamResult(TypedDict):
    """TypedDict representation of a Red Team Agent evaluation result with the updated structure.

    This class defines the structure for capturing the results of a red team evaluation, including:
    - redteaming_scorecard: Scorecard containing summary and detailed ASR information
    - redteaming_parameters: Parameters containing metadata about the evaluation run
    - redteaming_data: List of _Conversation objects representing the conversations in the evaluation
    """
    redteaming_scorecard: _RedTeamingScorecard
    redteaming_parameters: _RedTeamingParameters
    redteaming_data: List[_Conversation]
    studio_url: Optional[str]

class RedTeamOutput():
    def __init__(self, red_team_result: Optional[_RedTeamResult] = None, redteaming_data: Optional[List[_Conversation]] = None):
        self.red_team_result = red_team_result
        self.redteaming_data = redteaming_data

    def to_json(self) -> str:
        """
        Converts a _RedTeamResult object to a JSON-serializable dictionary.

        :returns: A string containing the _RedTeamResult in JSON format.
        :rtype: str
        """
        return json.dumps(self.red_team_result) if self.red_team_result else ""

    def to_scorecard(self) -> Optional[_RedTeamingScorecard]:
        """Extracts the scorecard from a _RedTeamResult object."""
        return self.red_team_result.get("redteaming_scorecard", None) if self.red_team_result else None
    
    def to_eval_qr_json_lines(self) -> str:
        """
        Converts conversations in messages format to query-response format suitable for evaluation.
        
        The output format follows the JSONL pattern with each line containing:
        {
            "query": "user message content",
            "response": "assistant message content",
            "risk_category": "risk category",
            "attack_strategy": "strategy name",
            "attack_complexity": "complexity level",  
            "attack_success": "true|false", (if available from evaluation)
            "category": "risk category", (if available from evaluation)
            "severity_level": "low|medium|high", (if available from evaluation)
            "threshold": "threshold value" (if available from evaluation)
        }
        
        :returns: A list of strings containing query-response pairs in JSONL format.
        :rtype: List[str]
        """
        if not self.redteaming_data:
            return ""
            
        result_lines = []
        
        for conversation in self.redteaming_data:
            messages = conversation.get("conversation", [])
            attack_technique = conversation.get("attack_technique", "")
            attack_complexity = conversation.get("attack_complexity", "")
            risk_category = conversation.get("risk_category", "")
            attack_success = conversation.get("attack_success")
            risk_assessment = conversation.get("risk_assessment", {})
            
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
                            "attack_complexity": attack_complexity
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
        if not self.redteaming_data:
            return ""
        
        result_lines = []
        
        for conversation in self.redteaming_data:
            messages = conversation.get("conversation", [])
            attack_technique = conversation.get("attack_technique", "")
            attack_complexity = conversation.get("attack_complexity", "")
            risk_category = conversation.get("risk_category", "")
            attack_success = conversation.get("attack_success")
            risk_assessment = conversation.get("risk_assessment", {})
            
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
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, List, Optional,  TypedDict
import json
from azure.ai.evaluation._common._experimental import experimental


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
    """
    attack_objective_generated_from: AttackObjectiveSource
    attack_complexity: List[str]
    techniques_used: Dict[str, List[str]]


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
class AttackDetails(TypedDict):
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
    """
    attack_success: Optional[bool]
    attack_technique: str
    attack_complexity: str
    risk_category: str
    conversation: List[Dict[str, str]]
    risk_assessment: Optional[RiskAssessment]


@experimental
class ScanResult(TypedDict):
    """TypedDict representation of a Red Team Agent evaluation result with the updated structure.

    :param scorecard: Scorecard containing summary and detailed ASR information
    :type scorecard: RedTeamingScorecard
    :param parameters: Parameters containing metadata about the evaluation run
    :type parameters: RedTeamingParameters
    :param attack_details: List of AttackDetails objects representing the conversations in the evaluation
    :type attack_details: List[AttackDetails]
    :param studio_url: Optional URL for the studio
    :type studio_url: Optional[str]
    """
    scorecard: RedTeamingScorecard
    parameters: RedTeamingParameters
    attack_details: List[AttackDetails]
    studio_url: Optional[str]


@experimental
class RedTeamResult():
    def __init__(
            self, 
            scan_result: Optional[ScanResult] = None, 
            attack_details: Optional[List[AttackDetails]] = None
        ):
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
        if not self.attack_details:
            return ""
            
        result_lines = []
        
        for conversation in self.attack_details:
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
        if not self.attack_details:
            return ""
        
        result_lines = []
        
        for conversation in self.attack_details:
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
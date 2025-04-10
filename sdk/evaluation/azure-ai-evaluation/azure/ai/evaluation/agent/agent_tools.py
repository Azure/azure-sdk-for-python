# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Tools for Azure AI Agents that provide evaluation and red teaming capabilities."""

import asyncio
import logging
from typing import Optional, Union, List, Dict, Any
import os
import json
import random

from azure.core.credentials import TokenCredential
from azure.ai.evaluation._common.experimental import experimental
from azure.ai.evaluation.red_team._attack_objective_generator import RiskCategory

# Setup logging
logger = logging.getLogger(__name__)


@experimental
class RedTeamToolProvider:
    """Provider for red teaming tools that can be used in Azure AI Agents.
    
    This class provides tools that can be registered with Azure AI Agents
    to enable red teaming capabilities.
    
    :param azure_ai_project: The Azure AI project configuration for accessing red team services
    :type azure_ai_project: Dict[str, Any]
    :param credential: The credential to authenticate with Azure services
    :type credential: TokenCredential
    :param application_scenario: Optional application scenario context for generating relevant prompts
    :type application_scenario: Optional[str]
    """
    
    def __init__(
        self,
        azure_ai_project: Dict[str, Any],
        credential: TokenCredential,
        *,
        application_scenario: Optional[str] = None,
    ):
        self.azure_ai_project = azure_ai_project
        self.credential = credential
        self.application_scenario = application_scenario
        
        # Lazy import RedTeam to avoid circular imports
        from azure.ai.evaluation.red_team import RedTeam
        
        # Initialize a RedTeam instance for accessing functionality
        self.red_team = RedTeam(
            azure_ai_project=azure_ai_project,
            credential=credential,
            application_scenario=application_scenario,
            risk_categories=[],  # Will be set dynamically in the tool methods
            num_objectives=20,   # Fetch more objectives to provide variety
        )
        
        # Cache for attack objectives to avoid repeated API calls
        self._attack_objectives_cache = {}
        
    @staticmethod
    def _parse_risk_category(category_text: str) -> Optional[RiskCategory]:
        """Parse a text string into a RiskCategory enum value.
        
        :param category_text: Text description of a risk category
        :type category_text: str
        :return: The corresponding RiskCategory enum value if found
        :rtype: Optional[RiskCategory]
        """
        # Convert to lowercase and remove spaces for more flexible matching
        cleaned_text = category_text.lower().strip()
        
        # Map common keywords to RiskCategory values - using only officially supported categories
        keyword_map = {
            # Hate/unfairness category
            "hate": RiskCategory.HateUnfairness,
            "unfairness": RiskCategory.HateUnfairness,
            "hate_unfairness": RiskCategory.HateUnfairness,
            "bias": RiskCategory.HateUnfairness,
            "discrimination": RiskCategory.HateUnfairness,
            "prejudice": RiskCategory.HateUnfairness,
            
            # Violence category
            "violence": RiskCategory.Violence,
            "harm": RiskCategory.Violence,
            "physical": RiskCategory.Violence,
            "weapon": RiskCategory.Violence,
            "dangerous": RiskCategory.Violence,
            
            # Sexual category
            "sexual": RiskCategory.Sexual,
            "sex": RiskCategory.Sexual,
            "adult": RiskCategory.Sexual,
            "explicit": RiskCategory.Sexual,
            
            # Self harm category
            "self_harm": RiskCategory.SelfHarm,
            "selfharm": RiskCategory.SelfHarm,
            "self-harm": RiskCategory.SelfHarm,
            "suicide": RiskCategory.SelfHarm,
            "self-injury": RiskCategory.SelfHarm,
        }
        
        # Try direct mapping first
        for key, risk_category in keyword_map.items():
            if key in cleaned_text:
                return risk_category
        
        # If the text contains an exact category name, use that
        for category in RiskCategory:
            if category.value.lower() in cleaned_text:
                return category
                
        return None

    async def fetch_harmful_prompt(
        self, 
        risk_category_text: str, 
        strategy: str = "baseline"
    ) -> Dict[str, Any]:
        """Fetch a harmful prompt for a specific risk category.
        
        This is designed to be used as a tool in Azure AI Agents for red teaming purposes.
        
        :param risk_category_text: Text description of the risk category (e.g., "violence", "hate")
        :type risk_category_text: str
        :param strategy: The attack strategy to use (default: "baseline")
        :type strategy: str
        :return: A dictionary containing the harmful prompt and metadata
        :rtype: Dict[str, Any]
        """
        try:
            # Parse the risk category from the text
            risk_category = self._parse_risk_category(risk_category_text)
            
            if not risk_category:
                supported_categories = ", ".join([rc.value for rc in RiskCategory])
                return {
                    "status": "error",
                    "message": f"Could not parse risk category from '{risk_category_text}'. Please use one of: {supported_categories}"
                }
            
            # Create a cache key from risk category and strategy
            cache_key = (risk_category.value, strategy)
            
            # Check if we already have cached objectives for this category and strategy
            if cache_key not in self._attack_objectives_cache:
                # Update the risk categories in the RedTeam instance
                self.red_team.attack_objective_generator.risk_categories = [risk_category]
                
                # Fetch the attack objectives
                objectives = await self.red_team._get_attack_objectives(
                    risk_category=risk_category,
                    application_scenario=self.application_scenario,
                    strategy=strategy
                )
                
                self._attack_objectives_cache[cache_key] = objectives
            
            objectives = self._attack_objectives_cache[cache_key]
            
            if not objectives:
                return {
                    "status": "error",
                    "message": f"No harmful prompts found for risk category '{risk_category.value}' with strategy '{strategy}'."
                }
            
            # Select a random objective from the list
            selected_objective = random.choice(objectives)
            
            return {
                "status": "success",
                "risk_category": risk_category.value,
                "strategy": strategy,
                "prompt": selected_objective,
                "note": "This prompt was generated for responsible AI testing purposes only."
            }
            
        except Exception as e:
            logger.error(f"Error fetching harmful prompt: {str(e)}")
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }

# Tool definition schema for Azure AI Agents
def get_red_team_tools() -> List[Dict[str, Any]]:
    """Get the list of red team tools that can be registered with Azure AI Agents.
    
    :return: A list of tool definitions
    :rtype: List[Dict[str, Any]]
    """
    return [
        {
            "task": "fetch_harmful_prompt",
            "description": "Fetch a harmful prompt for red teaming purposes",
            "parameters": {
                "risk_category_text": {
                    "type": "string",
                    "description": "The risk category to fetch a harmful prompt for (e.g., 'violence', 'hate_unfairness', 'sexual', 'self_harm')"
                },
                "strategy": {
                    "type": "string",
                    "description": "The attack strategy to use (e.g., 'baseline', 'jailbreak')",
                    "default": "baseline"
                }
            }
        }
    ]
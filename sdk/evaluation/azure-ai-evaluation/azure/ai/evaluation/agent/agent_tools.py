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
from azure.ai.evaluation.red_team._attack_strategy import AttackStrategy

# Import PyRIT prompt converters
from pyrit.prompt_converter import (
    MorseConverter, AnsiAttackConverter, AsciiArtConverter, 
    AsciiSmugglerConverter, AtbashConverter, Base64Converter, 
    BinaryConverter, CaesarConverter, CharacterSpaceConverter, 
    CharSwapGenerator, DiacriticConverter, LeetspeakConverter, 
    UrlConverter, UnicodeSubstitutionConverter, UnicodeConfusableConverter, 
    SuffixAppendConverter, StringJoinConverter, ROT13Converter, FlipConverter
)

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
        
        # Store fetched prompts for later conversion
        self._fetched_prompts = {}
        
        # Initialize strategy converters
        self._initialize_converters()
    
    def _initialize_converters(self):
        """Initialize all available prompt converters for strategies."""
        self.strategy_converters = {
            "morse": MorseConverter(),
            "ansi_attack": AnsiAttackConverter(),
            "ascii_art": AsciiArtConverter(),
            "ascii_smuggler": AsciiSmugglerConverter(),
            "atbash": AtbashConverter(),
            "base64": Base64Converter(),
            "binary": BinaryConverter(),
            "caesar": CaesarConverter(),
            "character_space": CharacterSpaceConverter(),
            "char_swap": CharSwapGenerator(),
            "diacritic": DiacriticConverter(),
            "leetspeak": LeetspeakConverter(),
            "rot13": ROT13Converter(),
            "suffix_append": SuffixAppendConverter(),
            "string_join": StringJoinConverter(),
            "unicode_confusable": UnicodeConfusableConverter(),
            "unicode_substitution": UnicodeSubstitutionConverter(),
            "url": UrlConverter(),
            "flip": FlipConverter()
        }
    
    def get_available_strategies(self) -> List[str]:
        """Get a list of available prompt conversion strategies.
        
        :return: List of strategy names
        :rtype: List[str]
        """
        return sorted(list(self.strategy_converters.keys()))
    
    def apply_strategy_to_prompt(self, prompt: str, strategy: str) -> str:
        """Apply a conversion strategy to a prompt.
        
        :param prompt: The prompt to convert
        :type prompt: str
        :param strategy: The strategy to apply
        :type strategy: str
        :return: The converted prompt
        :rtype: str
        :raises ValueError: If the strategy is not supported
        """
        if strategy not in self.strategy_converters:
            raise ValueError(f"Unsupported strategy: {strategy}. Available strategies: {', '.join(self.get_available_strategies())}")
        
        converter = self.strategy_converters[strategy]
        return converter.convert(prompt)
        
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
        strategy: str = "baseline",
        convert_with_strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch a harmful prompt for a specific risk category.
        
        This is designed to be used as a tool in Azure AI Agents for red teaming purposes.
        
        :param risk_category_text: Text description of the risk category (e.g., "violence", "hate")
        :type risk_category_text: str
        :param strategy: The attack strategy to use (default: "baseline")
        :type strategy: str
        :param convert_with_strategy: Optional strategy to convert the prompt (e.g., "morse", "binary")
        :type convert_with_strategy: Optional[str]
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
            
            # Create a unique ID for this prompt
            prompt_id = f"prompt_{len(self._fetched_prompts) + 1}"
            
            # Store the prompt for later conversion
            self._fetched_prompts[prompt_id] = selected_objective
            
            # Apply conversion strategy if requested
            if convert_with_strategy:
                if convert_with_strategy not in self.strategy_converters:
                    return {
                        "status": "error",
                        "message": f"Unsupported strategy: {convert_with_strategy}. Available strategies: {', '.join(self.get_available_strategies())}"
                    }
                
                try:
                    converted_prompt = self.apply_strategy_to_prompt(selected_objective, convert_with_strategy)
                    return {
                        "status": "success",
                        "risk_category": risk_category.value,
                        "strategy": strategy,
                        "conversion_strategy": convert_with_strategy,
                        "prompt_id": prompt_id,
                        "original_prompt": selected_objective,
                        "converted_prompt": converted_prompt,
                        "note": "This prompt was generated for responsible AI testing purposes only."
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Error converting prompt with strategy {convert_with_strategy}: {str(e)}"
                    }
            
            # Return with information about available strategies
            return {
                "status": "success",
                "risk_category": risk_category.value,
                "strategy": strategy,
                "prompt_id": prompt_id,
                "prompt": selected_objective,
                "available_strategies": self.get_available_strategies(),
                "note": "This prompt was generated for responsible AI testing purposes only. You can convert this prompt with a strategy by using the convert_prompt tool."
            }
            
        except Exception as e:
            logger.error(f"Error fetching harmful prompt: {str(e)}")
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }

    async def convert_prompt(
        self,
        prompt_or_id: str,
        strategy: str
    ) -> Dict[str, Any]:
        """Convert a prompt (or a previously fetched prompt by ID) using a specified strategy.
        
        :param prompt_or_id: Either a prompt text or a prompt ID from a previous fetch_harmful_prompt call
        :type prompt_or_id: str
        :param strategy: The strategy to use for conversion
        :type strategy: str
        :return: A dictionary containing the converted prompt
        :rtype: Dict[str, Any]
        """
        try:
            # Check if input is a prompt ID
            prompt_text = self._fetched_prompts.get(prompt_or_id, prompt_or_id)
            
            # Validate strategy
            if strategy not in self.strategy_converters:
                return {
                    "status": "error",
                    "message": f"Unsupported strategy: {strategy}. Available strategies: {', '.join(self.get_available_strategies())}"
                }
            
            # Convert the prompt
            converted_prompt = self.apply_strategy_to_prompt(prompt_text, strategy)
            
            return {
                "status": "success",
                "strategy": strategy,
                "original_prompt": prompt_text,
                "converted_prompt": converted_prompt,
                "note": "This prompt was converted for responsible AI testing purposes only."
            }
            
        except Exception as e:
            logger.error(f"Error converting prompt: {str(e)}")
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }

    async def red_team(
        self, 
        category: str,
        strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get a harmful prompt for a specific risk category with an optional conversion strategy.
        
        This unified tool combines fetch_harmful_prompt and convert_prompt into a single call.
        It allows users to request harmful prompts with a specific risk category and optionally apply
        a conversion strategy in one step.
        
        :param category: The risk category to get a harmful prompt for (e.g., "violence", "hate")
        :type category: str
        :param strategy: Optional conversion strategy to apply (e.g., "morse", "binary")
        :type strategy: Optional[str]
        :return: A dictionary containing the harmful prompt and metadata
        :rtype: Dict[str, Any]
        """
        try:
            # Parse input to extract risk category
            risk_category = self._parse_risk_category(category)
            
            if not risk_category:
                supported_categories = ", ".join([rc.value for rc in RiskCategory])
                return {
                    "status": "error",
                    "message": f"Could not parse risk category from '{category}'. Please use one of: {supported_categories}"
                }
            
            # First, fetch a harmful prompt (always using baseline attack strategy)
            result = await self.fetch_harmful_prompt(risk_category_text=category, strategy="baseline")
            
            if result["status"] != "success":
                return result
            
            # If no conversion strategy requested, return the prompt as is
            if not strategy:
                return {
                    "status": "success",
                    "risk_category": result["risk_category"],
                    "prompt": result["prompt"],
                    "prompt_id": result["prompt_id"],
                    "available_strategies": result["available_strategies"],
                    "note": "This prompt was generated for responsible AI testing purposes only. You can convert this prompt using one of the available strategies."
                }
            
            # If strategy is specified, convert the prompt
            if strategy not in self.strategy_converters:
                return {
                    "status": "error",
                    "message": f"Unsupported strategy: {strategy}. Available strategies: {', '.join(self.get_available_strategies())}"
                }
            
            # Convert the prompt using the specified strategy
            try:
                converted_prompt = self.apply_strategy_to_prompt(result["prompt"], strategy)
                return {
                    "status": "success",
                    "risk_category": result["risk_category"],
                    "original_prompt": result["prompt"],
                    "strategy": strategy,
                    "converted_prompt": converted_prompt,
                    "note": f"This prompt was generated for responsible AI testing purposes only and converted using the {strategy} strategy."
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error converting prompt with strategy {strategy}: {str(e)}"
                }
                
        except Exception as e:
            logger.error(f"Error in red_team: {str(e)}")
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
            "task": "red_team",
            "description": "Get a harmful prompt for a specific risk category with an optional conversion strategy",
            "parameters": {
                "category": {
                    "type": "string",
                    "description": "The risk category to get a harmful prompt for (e.g., 'violence', 'hate', 'sexual', 'self_harm')"
                },
                "strategy": {
                    "type": "string",
                    "description": "Optional strategy to convert the prompt (e.g., 'morse', 'binary', 'base64')",
                    "default": None
                }
            }
        },
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
                },
                "convert_with_strategy": {
                    "type": "string",
                    "description": "Optional strategy to convert the prompt (e.g., 'morse', 'binary'). If provided, the prompt will be automatically converted.",
                    "default": None
                }
            }
        },
        {
            "task": "convert_prompt",
            "description": "Convert a prompt using a specified strategy",
            "parameters": {
                "prompt_or_id": {
                    "type": "string",
                    "description": "Either a prompt text or a prompt ID from a previous fetch_harmful_prompt call"
                },
                "strategy": {
                    "type": "string",
                    "description": "The strategy to use for conversion (e.g., 'morse', 'binary', 'base64')"
                }
            }
        }
    ]
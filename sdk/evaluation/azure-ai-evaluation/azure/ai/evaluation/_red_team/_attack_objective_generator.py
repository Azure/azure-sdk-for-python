# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
import os
from enum import Enum
from typing import List, Optional, Dict, Any
from pathlib import Path

class RiskCategory(str, Enum):
    """Risk categories for attack objectives."""
    HateUnfairness = "hate_unfairness"
    Violence = "violence"
    Sexual = "sexual"
    SelfHarm = "self_harm"

class _AttackObjectiveGenerator:
    """Generator for creating attack objectives.

    :param risk_categories: List of risk categories to generate attack objectives for (optional if custom_attack_seed_prompts is provided)
    :type risk_categories: Optional[List[RiskCategory]]
    :param num_objectives: Number of objectives to generate per risk category
    :type num_objectives: int
    :param application_scenario: Description of the application scenario for context
    :type application_scenario: Optional[str]
    :param custom_attack_seed_prompts: Path to a JSON file containing custom attack seed prompts (can be absolute or relative path)
    :type custom_attack_seed_prompts: Optional[str]
    """
    def __init__(
        self,
        risk_categories: Optional[List[RiskCategory]] = None,
        num_objectives: int = 10,
        application_scenario: Optional[str] = None,
        custom_attack_seed_prompts: Optional[str] = None,
    ):
        self.risk_categories = risk_categories or []
        self.num_objectives = num_objectives
        self.application_scenario = application_scenario
        self.custom_attack_seed_prompts = custom_attack_seed_prompts
        self.logger = logging.getLogger("_AttackObjectiveGenerator")
        
        # If custom_attack_seed_prompts is provided, validate and load them
        self.custom_prompts = None
        self.validated_prompts = []
        self.valid_prompts_by_category = {}
        
        if custom_attack_seed_prompts:
            self._load_and_validate_custom_prompts()
            
    def _load_and_validate_custom_prompts(self) -> None:
        """Load and validate custom attack seed prompts from the provided file path."""
        if not self.custom_attack_seed_prompts:
            return
            
        # Handle both absolute and relative paths
        custom_prompts_path = Path(self.custom_attack_seed_prompts)
        
        # Convert to absolute path if it's a relative path
        if not custom_prompts_path.is_absolute():
            self.logger.info(f"Converting relative path '{custom_prompts_path}' to absolute path")
            custom_prompts_path = Path.cwd() / custom_prompts_path
            
        self.logger.debug(f"Using absolute path: {custom_prompts_path}")
        
        # Check if the file exists
        if not custom_prompts_path.exists():
            raise ValueError(f"Custom attack seed prompts file not found: {custom_prompts_path}")
            
        try:
            # Load JSON file
            with open(custom_prompts_path, 'r', encoding='utf-8') as f:
                self.custom_prompts = json.load(f)
                
            # Validate that it's a list
            if not isinstance(self.custom_prompts, list):
                raise ValueError(f"Custom attack seed prompts must be a JSON array, got {type(self.custom_prompts)}, see https://aka.ms/airedteamingagent-howtodoc for more information")
                
            self.logger.info(f"Loaded {len(self.custom_prompts)} prompts from {self.custom_attack_seed_prompts}")
                
            # Initialize dictionary for categorized prompts
            for risk_category in RiskCategory:
                self.valid_prompts_by_category[risk_category.value] = []
                
            # Process each prompt and validate format
            valid_prompts_count = 0
            invalid_prompts_count = 0
            for i, prompt in enumerate(self.custom_prompts):
                try:
                    # Check required fields
                    if not isinstance(prompt, dict):
                        self.logger.warning(f"Skipping prompt {i}: not a JSON object")
                        continue
                        
                    if "metadata" not in prompt:
                        self.logger.warning(f"Skipping prompt {i}: missing 'metadata' field")
                        continue
                        
                    if "messages" not in prompt or not prompt["messages"]:
                        self.logger.warning(f"Skipping prompt {i}: missing or empty 'messages' field")
                        continue
                        
                    # Check metadata structure
                    metadata = prompt["metadata"]
                    if not isinstance(metadata, dict):
                        self.logger.warning(f"Skipping prompt {i}: 'metadata' is not a JSON object, see https://aka.ms/airedteamingagent-howtodoc for more information")
                        continue
                        
                    if "target_harms" not in metadata or not metadata["target_harms"]:
                        self.logger.warning(f"Skipping prompt {i}: missing or empty 'target_harms' in metadata, see https://aka.ms/airedteamingagent-howtodoc for more information")
                        continue
                        
                    # Check target_harms structure
                    valid_risk_types = {cat.value for cat in RiskCategory}
                    valid_risk_found = False
                    prompt_categories = []
                    
                    for harm in metadata["target_harms"]:
                        if not isinstance(harm, dict):
                            self.logger.warning(f"Skipping harm in prompt {i}: not a JSON object, see https://aka.ms/airedteamingagent-howtodoc for more information")
                            continue
                            
                        if "risk-type" not in harm:
                            self.logger.warning(f"Skipping harm in prompt {i}: missing 'risk-type' field, see https://aka.ms/airedteamingagent-howtodoc for more information")
                            continue
                            
                        risk_type = harm.get("risk-type", "")
                        if risk_type not in valid_risk_types:
                            self.logger.warning(f"Skipping harm in prompt {i}: invalid risk-type '{risk_type}'. Valid types: {valid_risk_types}. see https://aka.ms/airedteamingagent-howtodoc for more information")
                            continue
                            
                        prompt_categories.append(risk_type)
                        valid_risk_found = True
                    
                    if not valid_risk_found:
                        self.logger.warning(f"Skipping prompt {i}: no valid risk types found. See https://aka.ms/airedteamingagent-howtodoc for more information")
                        continue
                    
                    # Check messages structure
                    messages = prompt["messages"]
                    if not isinstance(messages, list) or not messages:
                        self.logger.warning(f"Skipping prompt {i}: 'messages' is not a list or is empty, see https://aka.ms/airedteamingagent-howtodoc for more information")
                        continue
                        
                    message = messages[0]
                    if not isinstance(message, dict):
                        self.logger.warning(f"Skipping prompt {i}: first message is not a JSON object, see https://aka.ms/airedteamingagent-howtodoc for more information")
                        continue
                        
                    if "role" not in message or message["role"] != "user":
                        self.logger.warning(f"Skipping prompt {i}: first message must have role='user', see https://aka.ms/airedteamingagent-howtodoc for more information")
                        continue
                        
                    if "content" not in message or not message["content"]:
                        self.logger.warning(f"Skipping prompt {i}: first message missing or empty 'content', see https://aka.ms/airedteamingagent-howtodoc for more information")
                        continue
                    
                    # If we got here, the prompt is valid
                    self.validated_prompts.append(prompt)
                    valid_prompts_count += 1
                    
                    # Add to the appropriate categories
                    for category in prompt_categories:
                        self.valid_prompts_by_category[category].append(prompt)
                    
                except Exception as e:
                    self.logger.warning(f"Error validating prompt {i}: {str(e)}")
                    invalid_prompts_count += 1
                    
            # Check if we have at least one valid prompt
            if valid_prompts_count == 0:
                raise ValueError("No valid prompts found in custom attack seed prompts file. See https://aka.ms/airedteamingagent-howtodoc for more information")
                
            self.logger.info(f"Loaded {valid_prompts_count} valid prompts from custom attack seed prompts file")
            
            if invalid_prompts_count > 0:
                self.logger.warning(f"Skipped {invalid_prompts_count} invalid prompts")
                
            # Log the breakdown by risk category
            category_counts = {cat: len(prompts) for cat, prompts in self.valid_prompts_by_category.items() if len(prompts) > 0}
            self.logger.info(f"Prompt distribution by risk category: {category_counts}")
            
            # Automatically extract risk categories from valid prompts if not provided
            if not self.risk_categories:
                categories_with_prompts = [cat for cat, prompts in self.valid_prompts_by_category.items() if prompts]
                self.risk_categories = [RiskCategory(cat) for cat in categories_with_prompts]
                self.logger.info(f"Automatically set risk categories based on valid prompts: {[cat.value for cat in self.risk_categories]}")
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse custom attack seed prompts file: {str(e)}. See https://aka.ms/airedteamingagent-howtodoc for more information")
        except Exception as e:
            raise ValueError(f"Error loading custom attack seed prompts: {str(e)}. See https://aka.ms/airedteamingagent-howtodoc for more information")

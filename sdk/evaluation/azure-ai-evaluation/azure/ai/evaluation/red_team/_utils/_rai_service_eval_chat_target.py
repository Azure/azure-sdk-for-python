# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import uuid
import os
import json
import traceback
import asyncio
import re
from typing import Dict, Optional, Any, Tuple, List
from azure.ai.evaluation._common.rai_service import evaluate_with_rai_service
from azure.ai.evaluation.simulator._model_tools._generated_rai_client import GeneratedRAIClient
from pyrit.models import PromptRequestResponse, construct_response_from_request
from pyrit.prompt_target import PromptChatTarget
from .constants import USER_AGENT
from .metric_mapping import get_metric_from_risk_category
from .._attack_objective_generator import RiskCategory


class RAIServiceEvalChatTarget(PromptChatTarget):
    """A class to handle chat-based interactions with the RAI service for evaluation purposes."""

    def __init__(
            self, 
            credential: Any,
            azure_ai_project,
            risk_category: RiskCategory,
            logger: Optional[logging.Logger] = None,
            evaluator_name: Optional[str] = None,
        ) -> None:
        """Initialize the RAIServiceEvalChatTarget.

        :param endpoint: The endpoint URL for the RAI service.
        :type endpoint: str
        :param credential: The credential object for authentication.
        :type credential: Any
        """
        super().__init__()
        self.logger = logger
        self.risk_category = risk_category
        self.evaluator_name = evaluator_name
        self.credential = credential
        self.azure_ai_project = azure_ai_project

    async def send_prompt_async(self, *, prompt_request: PromptRequestResponse, objective: str = "") -> PromptRequestResponse:
        self.logger.info("Starting send_prompt_async operation")
        self._validate_request(prompt_request=prompt_request)
        
        thing_to_eval = prompt_request.request_pieces[0].to_dict()['original_value']

        thing_to_eval_qr = {
            "query":"",
            "response": thing_to_eval
        }

        metric_name = get_metric_from_risk_category(self.risk_category)
        
        evaluation_result = await evaluate_with_rai_service(thing_to_eval_qr,
                            metric_name=metric_name,
                            project_scope=self.azure_ai_project,
                            credential=self.credential)
        self.logger.info(f"Evaluation result: {evaluation_result}")
        
        # Extract the relevant data from evaluation_result
        score = evaluation_result.get(f"{metric_name}_score", 0)
        reason = evaluation_result.get(f"{metric_name}_reason", "")
        threshold = evaluation_result.get(f"{metric_name}_threshold", 3)
        result = evaluation_result.get(metric_name, "")
        
        # Calculate pass/fail using the same logic as in _evaluate_conversation
        # Convert to boolean then to string for PyRIT's true/false score
        # Ensure we're working with numeric values for comparison
        boolean_result = float(score) > float(threshold)
        
        # Format the response in a way that PyRIT's scorer can parse
        # Use "true"/"false" string for score_value which is required for true_false score type
        scorer_compatible_response = {
            "score_value": boolean_result,  # PyRIT requires lowercase "true" or "false" for true_false scores
            "description": f"Threshold: {threshold}, Result: {result}",
            "rationale": reason,
            "metadata": {
                "raw_score": score,
                "threshold": threshold,
                "result": result,
                "risk_category": self.risk_category
            }
        }
        
        # Convert to JSON string
        response_json = json.dumps(scorer_compatible_response)
        
        # Construct the response
        response = construct_response_from_request(
            request=prompt_request.request_pieces[0],
            response_text_pieces=[response_json],
        )
        self.logger.info(f"Constructed response: {response}")
        return response
        

    def is_json_response_supported(self) -> bool:
        """Check if JSON response is supported.
        
        :return: True if JSON response is supported, False otherwise
        """
        # This target supports JSON responses
        return True
    
    def _validate_request(self, *, prompt_request: PromptRequestResponse) -> None:
        """Validate the request.
        
        :param prompt_request: The prompt request
        """
        if len(prompt_request.request_pieces) != 1:
            raise ValueError("This target only supports a single prompt request piece.")

        if prompt_request.request_pieces[0].converted_value_data_type != "text":
            raise ValueError("This target only supports text prompt input.")


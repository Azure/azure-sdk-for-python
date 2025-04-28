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


class RAIServiceEvalChatTarget(PromptChatTarget):
    """A class to handle chat-based interactions with the RAI service for evaluation purposes."""

    def __init__(
            self, 
            credential: Any,
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
        self.evaluator_name = evaluator_name
        self.credential = credential

    async def send_prompt_async(self, *, prompt_request: PromptRequestResponse, objective: str = "") -> PromptRequestResponse:
        self.logger.info("Starting send_prompt_async operation")
        self._validate_request(prompt_request=prompt_request)
        thing_to_eval = prompt_request.request_pieces[0].to_dict()['original_value'].split("response_to_evaluate_input:")[1]
        

        self.logger.info(f"Evaluating the input: {thing_to_eval}")
        evaluation_result = await evaluate_with_rai_service(thing_to_eval, self.credential)
        self.logger.info(f"Evaluation result: {evaluation_result}")
        """
        {
            
            "score_value": "number between 0, 100",
            "description": "any text, lets not keep it empty",
            "rationale": "reason"
         
        }
        """

        my_response = PromptRequestResponse()
        import pdb; pdb.set_trace()

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
        

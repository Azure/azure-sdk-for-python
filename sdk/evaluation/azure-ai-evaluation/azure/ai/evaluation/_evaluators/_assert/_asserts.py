# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os

from typing import  Callable
from azure.ai.evaluation._model_configurations import Conversation
from ..._common.utils import construct_prompty_model_config, validate_model_config

from promptflow.core import Prompty


class LLMAssert:
    def __init__(self, assert_statement: str):
        self.assert_statement = assert_statement
       

    def _assert(self, model_config: dict, conversation: Conversation) -> bool:
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, "assert.prompty")

        prompty_model_config = construct_prompty_model_config(
                validate_model_config(model_config),
                "2024-02-15-preview",
                "NONE", # user agent
            )
        
        self._flow = Prompty.load(source=prompty_path, model=prompty_model_config)

        final_response = ""
        conversation_text = ""

        for turn in conversation["messages"]:
            if turn["role"] == "assistant":
                # Keep overriding the final response until the last assistant turn
                final_response = turn["content"]

                conversation_text += ("Assistant: " + str(turn["content"]) + "\n")
            
            elif turn["role"] == "user":
                conversation_text += ("User: " + str(turn["content"]) + "\n")

        kwargs = {
            "conversation": conversation_text,
            "response": final_response,
            "criteria": self.assert_statement
        }
        
        judge_response = self._flow(timeout=60, **kwargs)

        final_outcome = judge_response.split("**Final Outcome:**")[-1]

        if str(final_outcome).strip().lower() == "pass":
            return True
        else:
            return False


class CodeAssert:
    def __init__(self, assert_function: Callable[[Conversation], bool]):
        self.assert_function = assert_function

    def _assert(self, *, conversation: Conversation) -> bool:
                 
        return self.assert_function(conversation)
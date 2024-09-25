# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, List, Dict
from typing_extensions import override

from typing import Dict, List

import numpy as np
from azure.ai.evaluation._evaluators._common._base_eval import _BaseConversationEval

class BaseQRCEval(_BaseConversationEval):
    """Base class for all evaluators that are capable of accepting either a query and response as input,
    in addition to a conversation. The only thing that most child classes will need to implement is the _eval_qr method
    to handle a single query/response dict. Although some might need to implement the _aggregate_results method.

    param eval_last_turn: If True, only the last turn of the conversation will be evaluated, and no
        aggregation will be performed. If False, all turns will be evaluated and the numeric results will be,
        aggregated. Per-turn results are still be available in the output via the "evaluation_per_turn" key
        when this occurs. Default is False, resulting full conversation evaluation and aggregation.
    type eval_last_turn: bool
    """

    @override
    def __init__(self, eval_last_turn: bool = False):
        super().__init__()
        self._eval_last_turn = eval_last_turn

    @override
    def __call__(self, *, query: Optional[str] = None, response: Optional[str] = None, conversation: Optional[Dict] = None, **kwargs):
        """Evaluate either a query and response or a conversation. Must supply either a query AND reponse, or a conversation,
        but not both.

        param query: The query to evaluate.
        type query: Optional[str]
        param response: The response to evaluate.
        type response: Optional[str]
        param conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        type conversation: Optional[Dict]
        """
        return super().__call__(query=query, response=response, conversation=conversation, **kwargs)

    @override
    def _convert_conversation_to_eval_input(self, conversation: Dict) -> List:
        """Convert a conversation into a list of inputs for this evaluator.
        The output should always be a list, so if only one evaluation needs to be performed,
        this should return a list of length 1.

        By default, this function just returns the inputted conversation, wrapped in a list,
        and this function must be overridden by most children.

        param conversation: The conversation to convert.
        type conversation: Dict
        return: A list of arbitrary values that are valid inputs for this evaluator's do_eval function.
        rtype: List
        """
        
        messages = conversation['messages']
        # Extract queries, responses from conversation
        queries = []
        responses = []

        if self._eval_last_turn:
            # Process only the last two turns if _eval_last_turn is True
            conversation_slice = messages[-2:] if len(messages) >= 2 else messages
        else:
            conversation_slice = messages

        # Convert conversation slice into queries and responses.
        # Assume that 'user' role is asking queries and 'assistant' role is responding.
        for each_turn in conversation_slice:
            role = each_turn["role"]
            if role == "user":
                queries.append(each_turn["content"])
            elif role == "assistant":
                responses.append(each_turn["content"])

        eval_inputs = []
        for query, response in zip(queries, responses):
            eval_inputs.append({"query": query, "response": response})
        return eval_inputs

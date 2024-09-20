# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, List, Dict

from abc import ABC

from typing import Dict, List

import numpy as np

class BaseQRCEval(ABC):
    """Base class for all evaluators that are capable of accepting either a query and response as input,
    or a conversation. The only thing that most child classes will need to implement is the _eval_qr method
    to handle a single query/response pair. Although some might need to implement the _aggregate_results method.

    param eval_last_turn: If True, only the last turn of the conversation will be evaluated, and no
        aggregation will be performed. If False, all turns will be evaluated and the numeric results will be,
        aggregated. Per-turn results are still be available in the output via the "evaluation_per_turn" key
        when this occurs. Default is False, resulting full conversation evaluation and aggregation.
    type eval_last_turn: bool
    """


    def __init__(self, eval_last_turn: bool = False):
        self._eval_last_turn = eval_last_turn

    def __call__(self, query: Optional[str] = None, response: Optional[str] = None, conversation: Optional[List[Dict]] = None):
        """_summary_

        Args:
            query (Optional[str], optional): _description_. Defaults to None.
            response (Optional[str], optional): _description_. Defaults to None.
            conversation (Optional[List[Dict]], optional): _description_. Defaults to None.
        """
        if query is None and response is None and conversation is None:
            pass # TODO exception
        if query is not None and response is not None:
            if conversation is not None:
                pass # TODO another exception
            return self._eval_qr(query, response)
        elif conversation is not None:
            # Extract queries, responses from conversation
            queries = []
            responses = []

            if self._eval_last_turn:
                # Process only the last two turns if _eval_last_turn is True
                conversation_slice = conversation[-2:] if len(conversation) >= 2 else conversation
            else:
                conversation_slice = conversation

            # Convert conversation slice into queries and responses.
            # Assume that 'user' role is asking queries and 'assistant' role is responding.
            for each_turn in conversation_slice:
                role = each_turn["role"]
                if role == "user":
                    queries.append(each_turn["content"])
                elif role == "assistant":
                    responses.append(each_turn["content"])

            # Evaluate each turn
            per_turn_results = []
            for turn_num in range(len(queries)):
                per_turn_results.append(self._eval_qr(queries[turn_num], responses[turn_num]))

            # Aggregate results if there was more than 1 conversation turn, otherwise
            # Return the results directly.
            if len(per_turn_results) > 1:
                return self._aggregate_results(per_turn_results)
            elif len(per_turn_results) == 1:
                return per_turn_results[0]
            else:
                return {} # TODO should this be an exception instead
        else:
            raise NotImplementedError("Input type unrecognized by generic evaluator input parser.")

    def _eval_qr(self, query: str, response: str) -> Dict:
        """_summary_

        Args:
            query (str): _description_
            response (str): _description_

        Returns:
            Dict: _description_
        """
        raise NotImplementedError("Evaluators need to define their own query/response evaluation") # Raise not implemented error
    
    def _aggregate_results(self, per_turn_results: List[Dict]) -> Dict:
        """Aggregate the evaluation results of each conversation turn into a single result.

        Exact implementation might need to vary slightly depending on the results produced.
        Default behavior is to average the all number-based outputs, and 
        raise NotImplementedError("Evaluators need to define their own aggregation method")
        
        param per_turn_results: List of evaluation results for each turn in the conversation.
        type per_turn_results: List[Dict]
        """

        aggregated = {}
        evaluation_per_turn = {}

        for turn in per_turn_results:
            for metric, value in turn.items():
                if metric not in evaluation_per_turn.keys():
                    evaluation_per_turn[metric] = []
                evaluation_per_turn[metric].append(value)


        for metric, values in evaluation_per_turn.items():
            if all(isinstance(value, (int, float)) for value in values):
                aggregated[metric] = np.mean(values)

        aggregated["evaluation_per_turn"] = evaluation_per_turn

        return aggregated
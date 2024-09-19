# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, List, Dict

from abc import ABC

class BaseQRCEval(ABC):
    """Base class for all evaluators that are capable of accepting either a query and response as input,
    or a conversation. The only thing that most child classes will need to implement is the _eval_qr method
    to handle a single query/response pair.
    """


    def __init__(self, eval_):
        pass

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
        elif conversation is not None: # Technically not needed.
                
            # Extract queries, responses from conversation
            queries = []
            responses = []

            if self._eval_last_turn:
                # Process only the last two turns if _eval_last_turn is True
                conversation_slice = conversation[-2:] if len(conversation) >= 2 else conversation
            else:
                conversation_slice = conversation

            for each_turn in conversation_slice:
                role = each_turn["role"]
                if role == "user":
                    queries.append(each_turn["content"])
                elif role == "assistant":
                    responses.append(each_turn["content"])

            # Evaluate each turn
            per_turn_results = []
            for turn_num in range(len(queries)):
                current_turn_result = {}

                if self._parallel:
                    # Parallel execution
                    # Use a thread pool for parallel execution in the composite evaluator,
                    # as it's ~20% faster than asyncio tasks based on tests.
                    with ThreadPoolExecutor() as executor:
                        future_to_evaluator = {
                            executor.submit(self._evaluate_turn, turn_num, queries, responses, evaluator): evaluator
                            for evaluator in self._evaluators
                        }

                        for future in as_completed(future_to_evaluator):
                            result = future.result()
                            current_turn_result.update(result)
                else:
                    # Sequential execution
                    for evaluator in self._evaluators:
                        result = self._evaluate_turn(turn_num, queries, responses, evaluator)
                        current_turn_result.update(result)

                per_turn_results.append(current_turn_result)

            aggregated = self._aggregate_results(per_turn_results)
            return aggregated

    def _eval_qr(self, query: str, response: str) -> Dict:
        """_summary_

        Args:
            query (str): _description_
            response (str): _description_

        Returns:
            Dict: _description_
        """
        raise NotImplementedError("Evaluators need to define ") # Raise not implemented error
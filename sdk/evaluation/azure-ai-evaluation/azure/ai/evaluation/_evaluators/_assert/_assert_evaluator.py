# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Union, List, Callable
from typing_extensions import overload, override

from azure.ai.evaluation._model_configurations import Conversation


from ._asserts import LLMAssert, CodeAssert


class AssertEvaluator:


    id = "dummy"

    def __init__(self, model_config: dict, assert_dict: Dict[str, Union[Callable[[Conversation], bool], LLMAssert]]):
        super().__init__()

        self.model_config = model_config
        self.assert_dict = assert_dict
        

    def __call__(
        self,
        *,
        conversation: Conversation,
    ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]:
        """Evaluate if the final response meets all the assert criteria

        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The groundedness score.
        :rtype: Dict[str, Union[float, Dict[str, List[float]]]]
        """


        
        assert_results = {}

        for key, assert_obj in self.assert_dict.items():

            if type(assert_obj) is LLMAssert:
                assert_results[key] = assert_obj._assert(self.model_config, conversation=conversation) # type: ignore
            
            elif callable(assert_obj):
                assert_results[key] = assert_obj(conversation=conversation) # type: ignore
        
        assert_results["assert_score"] = sum([1 if result else 0 for result in assert_results.values()]) / len(assert_results)
        return assert_results
                


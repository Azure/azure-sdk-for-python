import os
import json
import sys
from promptflow.client import load_flow

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class FriendlinessEvaluator:
    def __init__(self, model_config):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, "friendliness.prompty")
        self._flow = load_flow(source=prompty_path, model={"configuration": model_config})

    def __call__(self, *, response: str, **kwargs):
        llm_response = self._flow(response=response)
        print(response)
        print(llm_response)
        try:
            evaluator_response = json.loads(llm_response)
        except Exception:
            evaluator_response = llm_response
        return evaluator_response
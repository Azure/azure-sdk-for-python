"""Custom evaluator that measures the length of a response."""


class AnswerLengthEvaluator:
    def __init__(self, *, model_config):
        self.model_config = model_config

    def __call__(self, *args, **kwargs):
        return {"result": evaluate_answer_length(kwargs.get("response"))}


def evaluate_answer_length(answer: str):
    return len(answer)

"""Custom evaluator that measures the length of a response."""


class AnswerLengthEvaluator:
    def __init__(self, *, config: str, threshold, **kwargs):
        self.config = config
        self.threshold = threshold

    def __call__(self, *args, **kwargs):
        return {
            "score": evaluate_answer_length(kwargs.get("response")), 
        }


def evaluate_answer_length(answer: str | None):
    return len(answer) if answer else 0

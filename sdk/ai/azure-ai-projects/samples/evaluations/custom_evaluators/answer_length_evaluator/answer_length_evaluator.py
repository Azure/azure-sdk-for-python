"""Custom evaluator that measures the length of a response."""


class AnswerLengthEvaluator:
    def __init__(self, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        length = evaluate_answer_length(kwargs.get("response"))
        return {
            "score": length,
            "label": "Pass" if length > 50 else "Fail",
        }


def evaluate_answer_length(answer: str | None):
    return len(answer) if answer else 0

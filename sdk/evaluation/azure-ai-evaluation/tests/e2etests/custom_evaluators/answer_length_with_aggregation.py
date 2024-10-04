from typing import List


def median(lst: List[str]) -> float:
    lst.sort()
    length = len(lst)
    if length % 2 == 1:
        return lst[length // 2]
    else:
        return (lst[length // 2 - 1] + lst[length // 2]) / 2


class AnswerLength:
    def __init__(self, *, return_json: bool = False, aggregate_return_json: bool = False):
        self.return_json = return_json
        self.aggregate_return_json = aggregate_return_json

    def __call__(self, response: str, **kwargs):
        return {"length": len(response)} if self.return_json else len(response)

    def __aggregate__(self, line_results: List[str]) -> dict:
        median_value = median([v.length for v in line_results]) if self.return_json else median(line_results)
        return {"median": median_value} if self.aggregate_return_json else median_value

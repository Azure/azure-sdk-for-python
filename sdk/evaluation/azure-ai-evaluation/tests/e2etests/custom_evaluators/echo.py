class EchoEvaluator:
    """Dummy evaluator that returns the query and response that's provided"""

    def __call__(self, query: str, response: str, **kwargs):
        return {"query": query, "response": response}

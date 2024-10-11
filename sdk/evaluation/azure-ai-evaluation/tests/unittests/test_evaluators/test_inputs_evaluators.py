# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# A collection of very simple evaluators designed to test column mappings.
# (aka proper data file -> _call__ input mapping)


class NonOptionalEval:
    def __init__(self):
        pass

    def __call__(self, query, response):
        return {"non_score": 0}


class HalfOptionalEval:
    def __init__(self):
        pass

    def __call__(self, query, *, response="default"):
        return {"half_score": 0 if response == "default" else 1}


class OptionalEval:
    def __init__(self):
        pass

    def __call__(self, *, query="default", response="default"):
        return {"opt_score": (0 if query == "default" else 1) + (0 if response == "default" else 2)}


class NoInputEval:
    def __init__(self):
        pass

    def __call__(self):
        return {"no_score": 0}


class EchoEval:
    def __init__(self):
        pass

    def __call__(self, *, query="default", response="default"):
        return {"echo_query": query, "echo_response": response}

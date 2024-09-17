# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# A collection of very simple evaluators designed to test column mappings.
# (aka proper data file -> _call__ input mapping)

class NonOptionalEval():
    def __init__(self):
        pass

    def __call__(self, question, answer):
        return {"non_score": 0}


class HalfOptionalEval():
    def __init__(self):
        pass

    def __call__(self, question, *, answer = "default"):
        return {"half_score": 0 if answer == "default" else 1}

    
class OptionalEval():
    def __init__(self):
        pass

    def __call__(self, *, question = "default", answer = "default"):
        return {"opt_score": (0 if question == "default" else 1) + (0 if answer == "default" else 2)}

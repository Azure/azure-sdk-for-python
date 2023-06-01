# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import Optional, Callable, TYPE_CHECKING, Union, Awaitable, Mapping, Any

class FeatureFlag:

    def __init__(self, key, evaluate, requirement_type, enabled_for):
        self.name = key
        self.evaluate = evaluate
        self.requirement_type = requirement_type
        self.enabled_for = enabled_for

class EvaluationContext:

    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from mldesigner import Output, command_component


@command_component()
def basic_component(
    output1: Output(type="boolean", is_control=True),
    output2: Output(type="boolean", is_control=True),
    output3: Output(type="boolean"),
) -> Output(type="boolean", is_control=True):
    """module run logic goes here"""
    return False

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from mldesigner import command_component, Output

@command_component
def merge_comp(output: Output, **kwargs):
    for k, v in kwargs.items():
        print(k)
        print(v)
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# This file contains mldesigner decorator-produced components
# that are used within node constructors. Keep imports and 
# general complexity in this file to a minimum.

from mldesigner import command_component, Output

@command_component
def merge_comp(output: Output, **kwargs):
    for k, v in kwargs.items():
        print(k)
        print(v)
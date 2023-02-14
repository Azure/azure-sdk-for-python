# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
from typing import List, Dict


from azure.ai.ml.entities._builders.fl_test_builders.node_builder_3 import NodeBuilder3

def Node3(
    component,
    component2,
    **kwargs,
):
    return NodeBuilder3(component, component2)
        
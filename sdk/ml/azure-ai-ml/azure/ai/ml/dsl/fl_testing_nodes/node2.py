# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
from typing import List, Dict


from azure.ai.ml.entities._builders.fl_test_builders.node_builder_2 import NodeBuilder2

def Node2(
    component,
    component2,
    **kwargs,
):
    return NodeBuilder2(component, component2)
        
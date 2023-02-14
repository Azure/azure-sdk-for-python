# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
from typing import List, Dict


from azure.ai.ml.entities._builders.fl_test_builders.node_builder_1 import NodeBuilder1

def Node1(
    component,
    **kwargs,
):
    return NodeBuilder1(component)
        
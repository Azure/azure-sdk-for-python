# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
from typing import List, Dict


from azure.ai.ml.entities._builders.fl_test_builders.node_builder_4 import NodeBuilder4

def Node4(
    component,
    compute,
    compute2,
    datastore,
    **kwargs,
):
    return NodeBuilder4(component, compute, compute2, datastore)
        
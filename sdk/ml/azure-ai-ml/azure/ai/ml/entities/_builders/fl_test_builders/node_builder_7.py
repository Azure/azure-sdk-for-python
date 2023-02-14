# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from typing import Dict, Union, List

from azure.ai.ml import Output
from azure.ai.ml.constants import JobType
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._job.pipeline._io.mixin import NodeIOMixin
from .simple_merge_comp import merge_comp

class NodeBuilder7(BaseNode, NodeIOMixin): 

    def __init__(
        self,
        component,
        iters,
        **kwargs,
    ):

        self._init = True

        outputs = {}
        for i in range(0, iters):
            next_run = component(float=i)
            outputs[f"run{i}"] = next_run.outputs["component_out_path"]
        merge_comp(**outputs)
        
        super(NodeBuilder7, self).__init__(
            type=JobType.COMPONENT,  # pylint: disable=redefined-builtin
            component=None,
            inputs= None,
            outputs= None,
            name= None,
            display_name= None,
            description= None,
            tags= None,
            properties= None,
            comment= None,
            compute= None,
            experiment_name= None,
        )

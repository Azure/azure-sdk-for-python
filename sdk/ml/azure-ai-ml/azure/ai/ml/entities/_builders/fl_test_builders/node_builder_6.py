# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from typing import Dict, Union, List

from azure.ai.ml import Output
from azure.ai.ml.constants import JobType
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._job.pipeline._io.mixin import NodeIOMixin

class NodeBuilder6(BaseNode, NodeIOMixin): 

    def __init__(
        self,
        component,
        component2,
        iters,
        **kwargs,
    ):

        self._init = True

        self.first_run = component()
        self.comp_runs = []
        previous_output = self.first_run.outputs["component_out_path"]
        for i in range(0, iters):
            next_run = component2(float=i, folder=previous_output)
            previous_output = next_run.outputs["component_out_path2"]
            self.comp_runs += [next_run]
        #@pipeline
        #def internal_pipeline():
        #     # Call component obj as function: apply given inputs & parameters to create a node in pipeline
        #    component_run = component()
        #
        #self.internal_pipeline = internal_pipeline()

        super(NodeBuilder6, self).__init__(
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
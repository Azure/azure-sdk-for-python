# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from typing import Dict, Union, List

from azure.ai.ml import Output
from azure.ai.ml.constants import JobType
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._job.pipeline._io.mixin import NodeIOMixin

class NodeBuilder2(BaseNode, NodeIOMixin): 

    def __init__(
        self,
        component,
        component2,
        **kwargs,
    ):

        self._init = True

        self.comp_run = component()
        self.comp_run2 = component2()
        #@pipeline
        #def internal_pipeline():
        #     # Call component obj as function: apply given inputs & parameters to create a node in pipeline
        #    component_run = component()
        #
        #self.internal_pipeline = internal_pipeline()

        super(NodeBuilder2, self).__init__(
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


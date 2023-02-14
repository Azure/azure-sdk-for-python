# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from typing import Dict, Union, List

from azure.ai.ml import Output
from azure.ai.ml.constants import JobType
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._job.pipeline._io.mixin import NodeIOMixin

class NodeBuilder1(BaseNode, NodeIOMixin): 

    def __init__(
        self,
        component,
        **kwargs,
    ):

        self._init = True

        self.comp_run = component()
        #@pipeline
        #def internal_pipeline():
        #     # Call component obj as function: apply given inputs & parameters to create a node in pipeline
        #    component_run = component()
        #
        #self.internal_pipeline = internal_pipeline()

        super(NodeBuilder1, self).__init__(
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


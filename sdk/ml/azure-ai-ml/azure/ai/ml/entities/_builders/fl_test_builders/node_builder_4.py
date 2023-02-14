# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from typing import Dict, Union, List

from azure.ai.ml import Output
from azure.ai.ml.constants import JobType
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._job.pipeline._io.mixin import NodeIOMixin

class NodeBuilder4(BaseNode, NodeIOMixin): 

    def __init__(
        self,
        component,
        compute1,
        compute2,
        datastore,
        **kwargs,
    ):

        self._init = True


        comp = component()
        comp2 = component()
        comp.compute = compute1
        comp2.compute = compute2

        super(NodeBuilder4, self).__init__(
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

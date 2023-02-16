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



    def custom_fl_data_path(
        datastore_name, output_name, unique_id="${{name}}", iteration_num="${{iteration_num}}"
    ):
        """Produces a path to store the data during FL training.
        Args:
            datastore_name (str): name of the Azure ML datastore
            output_name (str): a name unique to this output
            unique_id (str): a unique id for the run (default: inject run id with ${{name}})
            iteration_num (str): an iteration number if relevant
        Returns:
            data_path (str): direct url to the data path to store the data
        """
        data_path = f"azureml://datastores/{datastore_name}/paths/federated_learning/{output_name}/{unique_id}/"
        if iteration_num is not None:
            data_path += f"iteration_{iteration_num}/"

        return data_path

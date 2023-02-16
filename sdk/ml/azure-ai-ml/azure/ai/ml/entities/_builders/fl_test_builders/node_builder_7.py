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

# Output of merge_comp(**outputs)
# Command({'parameters': {}, 'init': False, 'type': 'command', 'status': None, 'log_files': None, 'name': None, 'description': None, 'tags': {}, 'properties': {}, 'print_as_yaml': True, 'id': None, 'Resource__source_path': None, 'base_path': '/home/milesholland/gh-azure/Notebooks', 'creation_context': None, 'serialize': <msrest.serialization.Serializer object at 0x7f6ca1ab50d0>, 'allowed_keys': {}, 'key_restriction': False, 'logger': <Logger attr_dict (WARNING)>, 'display_name': None, 'experiment_name': None, 'compute': None, 'services': None, 'comment': None, 'job_inputs': {'run0': <azure.ai.ml.entities._job.pipeline._io.base.NodeOutput object at 0x7f6ca1ab58b0>, 'run1': <azure.ai.ml.entities._job.pipeline._io.base.NodeOutput object at 0x7f6ca1ab59d0>, 'run2': <azure.ai.ml.entities._job.pipeline._io.base.NodeOutput object at 0x7f6ca1ab5070>, 'run3': <azure.ai.ml.entities._job.pipeline._io.base.NodeOutput object at 0x7f6ca1abd4f0>, 'run4': <azure.ai.ml.entities._job.pipeline._io.base.NodeOutput object at 0x7f6ca1abd520>}, 'job_outputs': {}, 'inputs': {'run0': <azure.ai.ml.entities._job.pipeline._io.base.NodeInput object at 0x7f6ca1abd3a0>, 'run1': <azure.ai.ml.entities._job.pipeline._io.base.NodeInput object at 0x7f6ca1abd5b0>, 'run2': <azure.ai.ml.entities._job.pipeline._io.base.NodeInput object at 0x7f6ca1abd640>, 'run3': <azure.ai.ml.entities._job.pipeline._io.base.NodeInput object at 0x7f6ca1abd610>, 'run4': <azure.ai.ml.entities._job.pipeline._io.base.NodeInput object at 0x7f6ca1abd430>}, 'outputs': {'output': <azure.ai.ml.entities._job.pipeline._io.base.NodeOutput object at 0x7f6ca1abd370>}, 'component': CommandComponent({'auto_increment_version': True, 'source': 'MLDESIGNER', 'is_anonymous': False, 'name': 'merge_comp', 'description': None, 'tags': {'codegenBy': 'mldesigner'}, 'properties': {}, 'print_as_yaml': True, 'id': None, 'Resource__source_path': '/home/milesholland/gh-azure/azure-sdk-for-python/sdk/ml/azure-ai-ml/azure/ai/ml/entities/_builders/fl_test_builders/simple_merge_comp.py', 'base_path': PosixPath('.'), 'creation_context': None, 'serialize': <msrest.serialization.Serializer object at 0x7f6ca1a5ac70>, 'command': "mldesigner execute --source simple_merge_comp.py --name merge_comp --inputs run0='${{inputs.run0}}' run1='${{inputs.run1}}' run2='${{inputs.run2}}' run3='${{inputs.run3}}' run4='${{inputs.run4}}' --outputs output='${{outputs.output}}'", 'code': '/home/milesholland/gh-azure/azure-sdk-for-python/sdk/ml/azure-ai-ml/azure/ai/ml/entities/_builders/fl_test_builders', 'environment_variables': None, 'environment': Environment({'is_anonymous': True, 'auto_increment_version': False, 'name': 'CliV2AnonymousEnvironment', 'description': None, 'tags': {}, 'properties': {}, 'print_as_yaml': True, 'id': None, 'Resource__source_path': None, 'base_path': PosixPath('.'), 'creation_context': None, 'serialize': <msrest.serialization.Serializer object at 0x7f6ca1a4b310>, 'version': '4c797784a6b680a11984cf2619bb45f7', 'latest_version': None, 'conda_file': {'name': 'default_environment', 'channels': ['defaults'], 'dependencies': ['python=3.8.12', 'pip=21.2.2', {'pip': ['--extra-index-url=https://azuremlsdktestpypi.azureedge.net/sdk-cli-v2', 'mldesigner==0.0.83671907']}]}, 'image': 'mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04', 'build': None, 'inference_config': None, 'os_type': None, 'arm_type': 'environment_version', 'conda_file_path': None, 'path': None, 'datastore': None, 'upload_hash': None, 'translated_conda_file': 'channels:\n- defaults\ndependencies:\n- python=3.8.12\n- pip=21.2.2\n- pip:\n  - --extra-index-url=https://azuremlsdktestpypi.azureedge.net/sdk-cli-v2\n  - mldesigner==0.0.83671907\nname: default_environment\n'}), 'distribution': None, 'resources': None, 'version': None, 'latest_version': None, 'schema': None, 'type': 'command', 'display_name': 'merge_comp', 'is_deterministic': True, 'inputs': {'run0': {'type': 'uri_folder'}, 'run1': {'type': 'uri_folder'}, 'run2': {'type': 'uri_folder'}, 'run3': {'type': 'uri_folder'}, 'run4': {'type': 'uri_folder'}}, 'outputs': {'output': {'type': 'uri_folder'}}, 'yaml_str': None, 'other_parameter': {}}), 'referenced_control_flow_node_instance_id': None, 'kwargs': {'services': None}, 'instance_id': '5a92cbce-3ead-4136-899b-d788191b9437', 'source': 'MLDESIGNER', 'validate_required_input_not_provided': True, 'limits': None, 'identity': None, 'distribution': None, 'environment_variables': {}, 'environment': None, 'resources': None, 'swept': False})
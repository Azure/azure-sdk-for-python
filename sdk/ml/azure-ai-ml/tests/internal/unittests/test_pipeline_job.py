# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from pathlib import Path
import pydash
import pytest
import yaml

from azure.ai.ml import load_component, Input
from azure.ai.ml._internal.entities.node import InternalBaseNode
from azure.ai.ml._internal.entities.scope import ScopeComponent
from azure.ai.ml._internal.entities.component import InternalComponent
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities import PipelineJob, CommandComponent
from tests.internal._utils import PARAMETERS_TO_TEST, set_run_settings


@pytest.mark.usefixtures("enable_internal_components")
@pytest.mark.unittest
class TestPipelineJob:
    @pytest.mark.parametrize(
        "yaml_path,inputs,runsettings_dict",
        PARAMETERS_TO_TEST,
    )
    def test_anonymous_internal_component_in_pipeline(self, yaml_path, inputs, runsettings_dict):
        # curated env with name & version
        # command_func: InternalComponent = client.components.get("ls_command", "0.0.1")
        command_func: InternalComponent = load_component(yaml_path)

        @pipeline()
        def pipeline_func():
            node = command_func(**inputs)
            set_run_settings(node, runsettings_dict)

        dsl_pipeline: PipelineJob = pipeline_func()
        result = dsl_pipeline._validate()
        assert result._to_dict() == {"result": "Succeeded"}

    @pytest.mark.skip(reason="TODO: runsettings design has been changed")
    @pytest.mark.parametrize(
        "node_func, runsettings_dict",
        [
            (
                lambda: load_component(path="./tests/test_configs/internal/helloworld_component_command.yml")(
                    training_data=Input(type=AssetTypes.MLTABLE, path="azureml:scope_tsv:1"),
                    max_epochs=3,
                ),
                {
                    "target": "aml-compute",
                    "target_selector": {
                        "compute_type": "AmlCompute",
                        "instance_types": ["STANDARD_D2_V2"],
                    },
                    "resource_layout": {
                        "node_count": 2,
                        "process_count_per_node": 2,
                    },
                    "environment_variables": {
                        "EXAMPLE_ENV_VAR": "example_value",
                    },
                    "environment": "AzureML-Designer",
                    "docker_configuration": {
                        "use_docker": True,
                        "shared_volumes": True,
                        "arguments": ["--cpus=2", "--memory=1GB"],
                        "shm_size": "4g",
                    },
                    "priority": 100,
                    "timeout_seconds": 600,
                },
            ),
            (
                lambda: load_component(path="./tests/test_configs/internal/helloworld_component_scope.yml")(
                    TextData=Input(type=AssetTypes.MLTABLE, path="azureml:scope_tsv:1"),
                    ExtractionClause="column1:string, column2:int",
                ),
                {
                    "priority": 5,
                    "scope": {
                        "adla_account_name": "adla_account_name",
                        "scope_param": "-tokens 50",
                        "custom_job_name_suffix": "component_sdk_test",
                    },
                },
            ),
        ],
    )
    def test_runsettings(self, node_func, runsettings_dict):
        @pipeline()
        def pipeline_func():
            node_with_configure_runsettings = node_func()

            self._check_and_set_run_settings(node_with_configure_runsettings.runsettings, runsettings_dict)
            self._check_and_set_run_settings(
                node_with_configure_runsettings.runsettings, runsettings_dict, with_configure=True
            )

            node_set_runsettings_with_dict = node_func()
            node_set_runsettings_with_dict.runsettings = runsettings_dict

        dsl_pipeline = pipeline_func()
        rest_obj = dsl_pipeline._to_rest_object()
        for node_name in ["node_with_configure_runsettings", "node_set_runsettings_with_dict"]:
            runsettings_rest_object = rest_obj.properties.jobs[node_name]["runsettings"]
            assert runsettings_rest_object == runsettings_dict, f"{node_name} runsettings not match"

    def test_load_pipeline_job_with_internal_components_as_node(self):
        yaml_path = Path("./tests/test_configs/internal/helloworld_component_scope.yml")
        scope_internal_func: ScopeComponent = load_component(path=yaml_path)
        with open(yaml_path, encoding="utf-8") as yaml_file:
            yaml_dict = yaml.safe_load(yaml_file)
        command_func: CommandComponent = load_component("./tests/test_configs/components/helloworld_component.yml")

        @pipeline()
        def pipeline_func():
            node = command_func(component_in_path=Input(path="./tests/test_configs/data"))
            node.compute = "cpu-cluster"

            node_internal = scope_internal_func(
                TextData=Input(type=AssetTypes.MLTABLE, path="azureml:scope_tsv:1"),
                ExtractionClause="column1:string, column2:int",
            )
            node_internal.resources.priority = 5

            node_internal.adla_account_name = "adla_account_name"
            node_internal.scope_param = "-tokens 50"
            node_internal.custom_job_name_suffix = "component_sdk_test"

        dsl_pipeline: PipelineJob = pipeline_func()
        internal_node_name = "node_internal"
        assert dsl_pipeline.jobs[internal_node_name]._component._to_dict() == yaml_dict

        scope_node: InternalBaseNode = dsl_pipeline.jobs[internal_node_name]
        # TODO: check why need to set base path manually
        scope_node._set_base_path(yaml_path.parent)
        scope_node_dict = scope_node._to_dict()
        assert scope_node_dict == {
            "$schema": "{}",
            "adla_account_name": "adla_account_name",
            "custom_job_name_suffix": "component_sdk_test",
            "scope_param": "-tokens 50",
            "component": yaml_dict,
            "type": "ScopeComponent",
            "resources": {"priority": 5},
            "inputs": {
                "ExtractionClause": "column1:string, column2:int",
                "TextData": {"path": "azureml:scope_tsv:1", "type": "mltable"},
            },
            "outputs": {},
        }
        assert pydash.omit(scope_node._to_rest_object(), "componentId") == {
            "_source": "YAML.COMPONENT",
            "adla_account_name": "adla_account_name",
            "custom_job_name_suffix": "component_sdk_test",
            "scope_param": "-tokens 50",
            "inputs": {
                "ExtractionClause": {"job_input_type": "Literal", "value": "column1:string, column2:int"},
                "TextData": {"job_input_type": "MLTable", "uri": "azureml:scope_tsv:1"},
            },
            "outputs": {},
            "resources": {"priority": 5},
            "type": "ScopeComponent",
        }
        scope_node._validate(raise_error=True)

        omit_fields = ["jobs.node.component", "jobs.node_internal.component"]
        assert pydash.omit(dsl_pipeline._to_dict(), *omit_fields) == pydash.omit(
            {
                "display_name": "pipeline_func",
                "inputs": {},
                "jobs": {"node": dsl_pipeline.jobs["node"]._to_dict(), "node_internal": scope_node._to_dict()},
                "outputs": {},
                "properties": {},
                "settings": {},
                "tags": {},
                "type": "pipeline",
            },
            *omit_fields,
        )

        dsl_pipeline._validate(raise_error=True)

        rest_object = dsl_pipeline._to_rest_object()
        assert rest_object.properties.jobs == {
            "node": dsl_pipeline.jobs["node"]._to_rest_object(),
            "node_internal": scope_node._to_rest_object(),
        }

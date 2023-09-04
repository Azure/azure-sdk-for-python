# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import pytest

from azure.ai.ml._utils.utils import is_internal_component_data
from azure.ai.ml.constants._common import AZUREML_INTERNAL_COMPONENTS_ENV_VAR
from azure.ai.ml.dsl._utils import environment_variable_overwrite
from azure.ai.ml.exceptions import ValidationException


@pytest.mark.usefixtures("disable_internal_components")
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestInternalDisabled:
    def test_load_pipeline_job_with_internal_nodes_from_rest(self):
        # this is a simplified test case which avoid constructing a complete pipeline job rest object
        from azure.ai.ml.entities._job.pipeline._load_component import pipeline_node_factory

        internal_node_type = "CommandComponent"
        with environment_variable_overwrite(AZUREML_INTERNAL_COMPONENTS_ENV_VAR, "False"):
            with pytest.raises(ValidationException, match=f"Unsupported component type: {internal_node_type}."):
                pipeline_node_factory.get_load_from_rest_object_func(internal_node_type)

        with environment_variable_overwrite(AZUREML_INTERNAL_COMPONENTS_ENV_VAR, "True"):
            pipeline_node_factory.get_load_from_rest_object_func(internal_node_type)

    def test_implicit_internal_components_enabling(self):
        from azure.ai.ml.entities._job.pipeline._load_component import pipeline_node_factory

        internal_node_type = "CommandComponent"

        target_data = {
            "$schema": "https://componentsdk.azureedge.net/jsonschema/SparkComponent.json",
        }
        with pytest.raises(ValidationException, match="Internal components is a private feature in v2"):
            is_internal_component_data(target_data, raise_if_not_enabled=True)

        from azure.ai.ml._internal._setup import enable_internal_components_in_pipeline

        # the usual implicit enabling is by importing azure.ai.ml._internal, but this is already imported in
        # fixture disable_internal_components, so we call the function directly
        enable_internal_components_in_pipeline()
        is_internal_component_data(target_data, raise_if_not_enabled=True)
        pipeline_node_factory.get_load_from_rest_object_func(internal_node_type)

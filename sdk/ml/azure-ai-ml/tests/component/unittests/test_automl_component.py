# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import pydash
import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.entities._component.automl_component import AutoMLComponent

from .._util import _COMPONENT_TIMEOUT_SECOND
from .test_component_schema import load_component_entity_from_rest_json, load_component_entity_from_yaml


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestAutoMLComponent:
    def test_serialize_deserialize_automl_component(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/automl/classification.yaml"
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client, _type="automl")
        assert isinstance(component_entity, AutoMLComponent)

        rest_path = "./tests/test_configs/components/automl/classification_rest.json"
        rest_entity = load_component_entity_from_rest_json(rest_path)

        sdk_component = AutoMLComponent(
            name="microsoft_azureml_automl_classification_component",
            version="1.0",
            task="classification",
            display_name="AutoML Classification",
            description="Component that executes an AutoML Classification task model training in a pipeline.",
        )

        omit_fields = ["name", "id", "$schema"]

        yaml_dict = pydash.omit(dict(component_entity._to_dict()), omit_fields)
        rest_dict = pydash.omit(dict(rest_entity._to_dict()), omit_fields)
        sdk_dict = pydash.omit(dict(sdk_component._to_dict()), omit_fields)

        assert yaml_dict == rest_dict
        assert sdk_dict == yaml_dict

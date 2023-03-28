import json
from pathlib import Path
from unittest import mock

import pydash
import pytest
import yaml

from azure.ai.ml import MLClient
from azure.ai.ml._restclient.v2022_05_01.models import ComponentVersionData
from azure.ai.ml._schema.component.parallel_component import ParallelComponentSchema
from azure.ai.ml._utils._arm_id_utils import PROVIDER_RESOURCE_ID_WITH_VERSION
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.entities._component.component import COMPONENT_PLACEHOLDER
from azure.ai.ml.entities._component.parallel_component import ParallelComponent

from .._util import _COMPONENT_TIMEOUT_SECOND


def load_component_entity_from_yaml(
    path: str,
    mock_machinelearning_client: MLClient,
    context={},
    is_anonymous=False,
    fields_to_override=None,
) -> ParallelComponent:
    """Component yaml -> component entity -> rest component object -> component entity"""
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    context.update({BASE_PATH_CONTEXT_KEY: Path(path).parent})
    schema = ParallelComponentSchema(context=context)
    data = dict(schema.load(cfg))
    if fields_to_override is None:
        fields_to_override = {}
    data.update(fields_to_override)
    if is_anonymous is True:
        data["name"] = None
        data["version"] = None
    internal_representation: ParallelComponent = ParallelComponent(**data)
    internal_representation._base_path = context[BASE_PATH_CONTEXT_KEY]

    def mock_get_asset_arm_id(*args, **kwargs):
        if len(args) > 0:
            arg = args[0]
            if isinstance(arg, str):
                return arg
            elif isinstance(arg, Code):
                if COMPONENT_PLACEHOLDER in str(arg.path):
                    # for generated code, return content in it
                    with open(arg.path) as f:
                        return f.read()
                return f"{str(arg.path)}:1"
        return "xxx"

    # change internal assets into arm id
    with mock.patch(
        "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
        side_effect=mock_get_asset_arm_id,
    ):
        mock_machinelearning_client.components._resolve_arm_id_or_upload_dependencies(internal_representation)
    rest_component = internal_representation._to_rest_object()
    # set arm id before deserialize
    mock_workspace_scope = mock_machinelearning_client._operation_scope
    rest_component.id = PROVIDER_RESOURCE_ID_WITH_VERSION.format(
        mock_workspace_scope.subscription_id,
        mock_workspace_scope.resource_group_name,
        mock_workspace_scope.workspace_name,
        "components",
        internal_representation.name,
        "1",
    )
    internal_component = ParallelComponent._from_rest_object(rest_component)
    return internal_component


def load_component_entity_from_rest_json(path) -> ParallelComponent:
    """Rest component json -> rest component object -> component entity"""
    with open(path, "r") as f:
        target = yaml.safe_load(f)
    rest_obj = ComponentVersionData.from_dict(json.loads(json.dumps(target)))
    internal_component = ParallelComponent._from_rest_object(rest_obj)
    return internal_component


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestParallelComponent:
    def test_serialize_deserialize_basic(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/basic_parallel_component_score.yml"
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client)
        rest_path = "./tests/test_configs/components/basic_parallel_component_score_rest.json"
        target_entity = load_component_entity_from_rest_json(rest_path)

        # skip check code and environment
        component_dict = component_entity._to_dict()
        assert component_dict["id"]
        component_dict = pydash.omit(
            dict(component_dict),
            "task.code",
            "id",
        )
        expected_dict = pydash.omit(
            dict(target_entity._to_dict()),
            "task.code",
            "creation_context",
            "id",
        )

        assert component_dict == expected_dict
        assert component_dict["logging_level"] == "INFO"

        assert component_entity.code

    def test_serialize_deserialize_partition_keys(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/parallel_component_with_partition_keys.yml"
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client)
        rest_path = "./tests/test_configs/components/parallel_component_with_partition_keys_rest.json"
        target_entity = load_component_entity_from_rest_json(rest_path)

        # skip check code and environment
        component_dict = component_entity._to_dict()
        assert component_dict["id"]
        component_dict = pydash.omit(
            dict(component_dict),
            "task.code",
            "id",
        )
        expected_dict = pydash.omit(
            dict(target_entity._to_dict()),
            "task.code",
            "creation_context",
            "id",
        )

        assert component_dict == expected_dict
        assert component_dict["partition_keys"] == ["foo", "bar"]

        assert component_entity.code

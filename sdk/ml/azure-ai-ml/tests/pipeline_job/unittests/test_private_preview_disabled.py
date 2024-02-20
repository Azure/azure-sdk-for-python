from pathlib import Path
import pytest
import yaml
from jsonschema.validators import validate
from azure.ai.ml.entities import PipelineJob
from test_utilities.json_schema import PatchedJSONSchema

from .._util import _PIPELINE_JOB_TIMEOUT_SECOND


# schema of nodes will be reloaded with private preview features disabled in unregister_internal_components
@pytest.mark.usefixtures("disable_internal_components")
@pytest.mark.timeout(_PIPELINE_JOB_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestPrivatePreviewDisabled:
    def test_public_json_schema(self):
        # public json schema is the json schema to be saved in
        # https://azuremlschemas.azureedge.net/latest/pipelineJob.schema.json
        base_dir = Path("./tests/test_configs/pipeline_jobs/json_schema_validation")
        target_schema = PatchedJSONSchema().dump(PipelineJob._create_schema_for_validation(context={"base_path": "./"}))

        with open(base_dir.joinpath("component_spec.yaml"), "r") as f:
            yaml_data = yaml.safe_load(f.read())

        validate(yaml_data, target_schema)

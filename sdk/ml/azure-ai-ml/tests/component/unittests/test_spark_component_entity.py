import pydash
import pytest

from azure.ai.ml import load_component
from azure.ai.ml._restclient.v2022_10_01_preview.models import ManagedIdentity
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.entities._component.spark_component import SparkComponent
from azure.ai.ml.entities._job.pipeline._io import PipelineInput

from .._util import _COMPONENT_TIMEOUT_SECOND


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestSparkComponentEntity:
    def test_component_load(self):
        # code is specified in yaml, value is respected
        component_yaml = "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/add_greeting_column_component.yml"
        spark_component = load_component(
            component_yaml,
        )

        assert isinstance(spark_component.py_files, list) and spark_component.py_files[0] == "utils.zip"
        assert spark_component.code == "./src"
        assert spark_component.entry._to_rest_object().as_dict() == {
            "spark_job_entry_type": "SparkJobPythonEntry",
            "file": "add_greeting_column.py",
        }
        assert spark_component.args == "--file_input ${{inputs.file_input}}"

    def test_spark_component_to_dict(self):
        # Test optional params exists in component dict
        yaml_path = "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/add_greeting_column_component.yml"
        yaml_dict = load_yaml(yaml_path)
        yaml_dict["mock_option_param"] = {"mock_key": "mock_val"}
        spark_component = SparkComponent._load(data=yaml_dict, yaml_path=yaml_path)
        assert spark_component._other_parameter.get("mock_option_param") == yaml_dict["mock_option_param"]

    def test_spark_component_entity(self):
        component = SparkComponent(
            name="add_greeting_column_spark_component",
            display_name="Aml Spark add greeting column test module",
            description="Aml Spark add greeting column test module",
            version="1",
            inputs={
                "file_input": {"type": "uri_file", "mode": "direct"},
            },
            driver_cores=2,
            driver_memory="1g",
            executor_cores=1,
            executor_memory="1g",
            executor_instances=1,
            code="./src",
            entry={"file": "add_greeting_column.py"},
            py_files=["utils.zip"],
            files=["my_files.txt"],
            args="--file_input ${{inputs.file_input}}",
            base_path="./tests/test_configs/dsl_pipeline/spark_job_in_pipeline",
        )
        omit_fields = [
            "properties.component_spec.$schema",
            "properties.component_spec._source",
        ]
        component_dict = component._to_rest_object().as_dict()
        component_dict = pydash.omit(component_dict, *omit_fields)

        yaml_path = "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/add_greeting_column_component.yml"
        yaml_component = load_component(yaml_path)
        yaml_component_dict = yaml_component._to_rest_object().as_dict()
        yaml_component_dict = pydash.omit(yaml_component_dict, *omit_fields)

        assert component_dict == yaml_component_dict

    def test_spark_component_version_as_a_function_with_inputs(self):
        expected_rest_component = {
            "type": "spark",
            "resources": {"instance_type": "Standard_E8S_V3", "runtime_version": "3.2.0"},
            "entry": {"file": "add_greeting_column.py", "spark_job_entry_type": "SparkJobPythonEntry"},
            "py_files": ["utils.zip"],
            "files": ["my_files.txt"],
            "identity": {"identity_type": "UserIdentity"},
            "conf": {
                "spark.driver.cores": 2,
                "spark.driver.memory": "1g",
                "spark.executor.cores": 1,
                "spark.executor.instances": 1,
                "spark.executor.memory": "1g",
            },
            "args": "--file_input ${{inputs.file_input}}",
            "inputs": {
                "file_input": {"job_input_type": "literal", "value": "${{parent.inputs.pipeline_input}}"},
            },
            "_source": "YAML.COMPONENT",
            "componentId": "fake_component",
        }
        yaml_path = "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/add_greeting_column_component.yml"
        yaml_component_version = load_component(yaml_path)
        pipeline_input = PipelineInput(name="pipeline_input", owner="pipeline", meta=None)
        yaml_component = yaml_component_version(file_input=pipeline_input)
        yaml_component.resources = {"instance_type": "Standard_E8S_V3", "runtime_version": "3.2.0"}
        yaml_component._component = "fake_component"
        rest_yaml_component = yaml_component._to_rest_object()

        assert rest_yaml_component == expected_rest_component

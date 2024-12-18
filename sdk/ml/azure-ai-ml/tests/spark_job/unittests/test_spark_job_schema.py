from pathlib import Path

import pytest
import yaml

from azure.ai.ml import Input, load_job
from azure.ai.ml._restclient.v2023_04_01_preview.models import InputDeliveryMode, JobOutputType, OutputDeliveryMode
from azure.ai.ml._schema import SparkJobSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities import SparkJob
from azure.ai.ml.entities._job.to_rest_functions import to_rest_job_object
from azure.ai.ml.exceptions import ValidationException
from marshmallow.exceptions import ValidationError


@pytest.mark.unittest
@pytest.mark.training_experiences_test
class TestSparkJobSchema:
    def test_deserialize(self):
        test_path = "./tests/test_configs/spark_job/spark_job_test.yml"
        with open("./tests/test_configs/spark_job/spark_job_rest.json", "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            cfg = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: Path(test_path).parent}
            schema = SparkJobSchema(context=context)
            internal_representation: SparkJob = SparkJob(**schema.load(cfg))
        source = internal_representation._to_rest_object()
        assert source.name == target["name"]
        assert source.properties.conf == target["conf"]
        assert source.properties.code_id == target["code"]

    def test_invalid_runtime_version(self):
        test_path = "./tests/test_configs/spark_job/spark_job_invalid_runtime.yml"
        with open(test_path, "r") as f:
            cfg = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: Path(test_path).parent}
            schema = SparkJobSchema(context=context)
            with pytest.raises(ValidationError) as ve:
                internal_representation: SparkJob = SparkJob(**schema.load(cfg))
                source = internal_representation._to_rest_object()
                assert ve.message == "runtime version should be either 3.3 or 3.4"

    def test_invalid_instance_type(self):
        test_path = "./tests/test_configs/spark_job/spark_job_invalid_instance_type.yml"
        with open(test_path, "r") as f:
            cfg = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: Path(test_path).parent}
            schema = SparkJobSchema(context=context)
            internal_representation: SparkJob = SparkJob(**schema.load(cfg))
            with pytest.raises(ValidationException) as ve:
                source = internal_representation._to_rest_object()
                assert (
                    ve.message
                    == "Instance type must be specified for the list of standard_e4s_v3,standard_e8s_v3,standard_e16s_v3,standard_e32s_v3,standard_e64s_v3"
                )

    def test_deserialize_inputs(self):
        test_path = "./tests/test_configs/spark_job/spark_job_inputs_outputs_test.yml"
        with open("./tests/test_configs/spark_job/spark_job_inputs_outputs_rest.json", "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            cfg = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: Path(test_path).parent}
            schema = SparkJobSchema(context=context)
            internal_representation: SparkJob = SparkJob(**schema.load(cfg))
        source = internal_representation._to_rest_object()
        assert source.properties.inputs["input1"].uri == target["inputs"]["input1"]["uri"]
        assert source.properties.inputs["input1"].mode == target["inputs"]["input1"]["mode"]

    def test_input_is_loaded_from_dictionary(self):
        spark_job = SparkJob(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            inputs={
                "input1": Input(
                    type="uri_file", path="azureml://datastores/workspaceblobstore/paths/python/data.csv", mode="direct"
                )
            },
            compute="douglassynapse",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            resources={
                "instance_type": "Standard_E8S_V3",
                "runtime_version": "3.3.0",
            },
        )
        assert isinstance(spark_job.inputs["input1"], Input)

    def test_standalone_job_inputs_outputs(self):
        original_entity = load_job(Path("./tests/test_configs/spark_job/spark_job_inputs_outputs_test.yml"))
        rest_representation = to_rest_job_object(original_entity)

        assert rest_representation.properties.inputs["input1"].mode == InputDeliveryMode.DIRECT
        assert rest_representation.properties.outputs["output1"].mode == OutputDeliveryMode.DIRECT
        assert (
            rest_representation.properties.inputs["input1"].uri
            == "https://azuremlexamples.blob.core.windows.net/datasets/iris.csv"
        )
        assert rest_representation.properties.outputs["output1"].job_output_type == JobOutputType.URI_FILE

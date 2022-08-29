import pytest

from azure.ai.ml._restclient.v2022_06_01_preview.models import AmlToken
from azure.ai.ml.entities import SparkJob
from azure.ai.ml.entities._job.job_name_generator import generate_job_name
from azure.ai.ml.entities._builders.spark_func import spark
from azure.ai.ml import Input, Output
from azure.ai.ml._ml_exceptions import ValidationException
from azure.ai.ml.entities._job.spark_resource_configuration import SparkResourceConfiguration


@pytest.mark.unittest
class TestSparkJobEntity:
    def test_job_name_generator(self):
        job_name_1 = generate_job_name()

        name_parts = job_name_1.split(sep="_")
        len(name_parts) == 3
        len(name_parts[2]) == 10

        job_name_2 = generate_job_name()
        assert job_name_2 != job_name_1

    def test_promoted_conf_serialization(self) -> None:
        node = spark(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            dynamic_allocation_enabled=True,
            dynamic_allocation_min_executors=1,
            dynamic_allocation_max_executors=3,
            resources={
                "instance_type": "Standard_E8S_V3",
                "runtime_version": "3.1.0",
            },
        )

        expected_conf = {
            "spark.driver.cores": 1,
            "spark.driver.memory": "2g",
            "spark.executor.cores": 2,
            "spark.executor.memory": "2g",
            "spark.executor.instances": 2,
            "spark.dynamicAllocation.enabled": True,
            "spark.dynamicAllocation.minExecutors": 1,
            "spark.dynamicAllocation.maxExecutors": 3,
        }
        assert node._to_job()._to_rest_object().properties.conf == expected_conf

    def test_promoted_conf_with_additional_conf_serialization(self) -> None:
        node = spark(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            dynamic_allocation_enabled=True,
            dynamic_allocation_min_executors=1,
            dynamic_allocation_max_executors=3,
            conf={
                "spark.jars.packages": "com.microsoft.ml.spark:mmlspark_2.11:0.15",
                "spark.jars.repositories": "https://mmlspark.azureedge.net/maven",
                "spark.jars.excludes": "slf4j:slf4j",
            },
            resources={
                "instance_type": "Standard_E8S_V3",
                "runtime_version": "3.1.0",
            },
        )

        expected_conf = {
            "spark.driver.cores": 1,
            "spark.driver.memory": "2g",
            "spark.executor.cores": 2,
            "spark.executor.memory": "2g",
            "spark.executor.instances": 2,
            "spark.dynamicAllocation.enabled": True,
            "spark.dynamicAllocation.minExecutors": 1,
            "spark.dynamicAllocation.maxExecutors": 3,
            "spark.jars.excludes": "slf4j:slf4j",
            "spark.jars.packages": "com.microsoft.ml.spark:mmlspark_2.11:0.15",
            "spark.jars.repositories": "https://mmlspark.azureedge.net/maven",
        }
        assert node._to_job()._to_rest_object().properties.conf == expected_conf

    def test_missing_resources_raises(self):
        with pytest.raises(ValidationException):
            node = spark(
                code="./tests/test_configs/spark_job/basic_spark_job/src",
                entry={"file": "./main.py"},
            )
            node._to_job()._to_rest_object()

    def test_missing_entry_with_dict_resources_raises(self):
        with pytest.raises(ValidationException):
            node = spark(
                code="./tests/test_configs/spark_job/basic_spark_job/src",
                resources={
                    "instance_type": "Standard_E8S_V3",
                    "runtime_version": "3.1.0",
                },
            )
            node._to_job()._to_rest_object()

    def test_missing_entry_with_SparkResourceConfiguration_resources_raises(self):
        with pytest.raises(ValidationException):
            node = spark(
                code="./tests/test_configs/spark_job/basic_spark_job/src",
                resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.1.0"),
            )
            node._to_job()._to_rest_object()

    def test_spark_job_with_invalid_input_mode(self):
        with pytest.raises(ValidationException):
            node = spark(
                code="./tests/test_configs/spark_job/basic_spark_job/src",
                entry={"file": "./main.py"},
                inputs={
                    "input1": Input(
                        type="uri_file", path="azureml://datastores/workspaceblobstore/paths/python/data.csv"
                    )
                },
                resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.1.0"),
            )
            node._to_job()._to_rest_object()

    def test_spark_job_with_invalid_output_mode(self):
        with pytest.raises(ValidationException):
            node = spark(
                code="./tests/test_configs/spark_job/basic_spark_job/src",
                entry={"file": "./main.py"},
                outputs={
                    "output1": Output(
                        type="uri_file",
                        path="azureml://datastores/workspaceblobstore/spark_titanic_output/titanic.parquet",
                    )
                },
                resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.1.0"),
            )
            node._to_job()._to_rest_object()

    def test_spark_job_builder_serialization(self) -> None:

        node = spark(
            name="builder-spark-job",
            experiment_name="builder-spark-experiment-name",
            description="simply spark description",
            environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            jars=["simple-1.1.1.jar"],
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            dynamic_allocation_min_executors=1,
            dynamic_allocation_max_executors=3,
            identity=AmlToken(),
            inputs={
                "input1": Input(
                    type="uri_file", path="azureml://datastores/workspaceblobstore/paths/python/data.csv", mode="direct"
                )
            },
            outputs={
                "output1": Output(
                    type="uri_file",
                    path="azureml://datastores/workspaceblobstore/spark_titanic_output/titanic.parquet",
                    mode="direct",
                )
            },
            args="--input1 ${{inputs.input1}} --output1 ${{outputs.output1}} --my_sample_rate 0.01",
            resources={
                "instance_type": "Standard_E8S_V3",
                "runtime_version": "3.1.0",
            },
        )

        expected_job = SparkJob(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            jars=["simple-1.1.1.jar"],
            identity=AmlToken(),
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            dynamic_allocation_min_executors=1,
            dynamic_allocation_max_executors=3,
            name="builder-spark-job",
            experiment_name="builder-spark-experiment-name",
            description="simply spark description",
            environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
            inputs={
                "input1": Input(
                    type="uri_file", path="azureml://datastores/workspaceblobstore/paths/python/data.csv", mode="direct"
                )
            },
            outputs={
                "output1": Output(
                    type="uri_file",
                    path="azureml://datastores/workspaceblobstore/spark_titanic_output/titanic.parquet",
                    mode="direct",
                )
            },
            args="--input1 ${{inputs.input1}} --output1 ${{outputs.output1}} --my_sample_rate 0.01",
            resources={
                "instance_type": "Standard_E8S_V3",
                "runtime_version": "3.1.0",
            },
        )

        expected_job_with_object_resources = SparkJob(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            jars=["simple-1.1.1.jar"],
            identity=AmlToken(),
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            dynamic_allocation_min_executors=1,
            dynamic_allocation_max_executors=3,
            name="builder-spark-job",
            experiment_name="builder-spark-experiment-name",
            description="simply spark description",
            environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
            inputs={
                "input1": Input(
                    type="uri_file", path="azureml://datastores/workspaceblobstore/paths/python/data.csv", mode="direct"
                )
            },
            outputs={
                "output1": Output(
                    type="uri_file",
                    path="azureml://datastores/workspaceblobstore/spark_titanic_output/titanic.parquet",
                    mode="direct",
                )
            },
            args="--input1 ${{inputs.input1}} --output1 ${{outputs.output1}} --my_sample_rate 0.01",
            resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.1.0"),
        )

        assert expected_job._to_dict() == node._to_job()._to_dict()
        assert expected_job_with_object_resources._to_dict() == node._to_job()._to_dict()

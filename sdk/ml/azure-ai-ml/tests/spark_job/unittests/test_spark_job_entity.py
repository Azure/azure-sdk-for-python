import pytest

from azure.ai.ml import Input, Output
from azure.ai.ml._restclient.v2023_04_01_preview.models import AmlToken, JobBase
from azure.ai.ml._restclient.v2023_04_01_preview.models import SparkJob as RestSparkJob
from azure.ai.ml._restclient.v2023_04_01_preview.models import SparkJobPythonEntry
from azure.ai.ml.entities import SparkJob
from azure.ai.ml.entities._builders.spark_func import spark
from azure.ai.ml.entities._job.job_name_generator import generate_job_name
from azure.ai.ml.entities._job.spark_resource_configuration import SparkResourceConfiguration
from azure.ai.ml.exceptions import ValidationException


@pytest.mark.unittest
@pytest.mark.training_experiences_test
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
                "runtime_version": "3.2.0",
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

    def test_attached_compute_default_managed_identity_if_empty_identity_input(self):
        node = spark(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            compute="synapsecompute",
        )
        assert node._to_job()._to_rest_object().properties.identity.identity_type == "Managed"

    def test_hobo_default_user_identity_if_empty_identity_input(self):
        node = spark(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            resources={
                "instance_type": "Standard_E8S_V3",
                "runtime_version": "3.2.0",
            },
        )
        assert node._to_job()._to_rest_object().properties.identity.identity_type == "UserIdentity"

    def test_attached_compute_obey_user_identity_input(self):
        node = spark(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            compute="synapsecompute",
            identity={"type": "user_identity"},
        )
        assert node._to_job()._to_rest_object().properties.identity.identity_type == "UserIdentity"

    def test_hobo_obey_user_identity_input(self):
        node = spark(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            resources={
                "instance_type": "Standard_E8S_V3",
                "runtime_version": "3.2.0",
            },
            identity={"type": "managed"},
        )
        assert node._to_job()._to_rest_object().properties.identity.identity_type == "Managed"

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
                "runtime_version": "3.2.0",
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

    def test_resources_instance_type(self):
        with pytest.raises(ValidationException) as ve:
            node = spark(
                code="./tests/test_configs/spark_job/basic_spark_job/src",
                entry={"file": "./main.py"},
                resources=SparkResourceConfiguration(instance_type="Standard_E128S_V3", runtime_version="3.2.0"),
                driver_cores=1,
                driver_memory="2g",
                executor_cores=2,
                executor_memory="2g",
            )
            node._to_job()._to_rest_object()
            assert (
                ve.message
                == "Instance type must be specified for the list of standard_e4s_v3,standard_e8s_v3,standard_e16s_v3,standard_e32s_v3,standard_e64s_v3"
            )

    def test_resources_34_runtime_version(self):
        with pytest.raises(ValidationException) as ve:
            node = spark(
                code="./tests/test_configs/spark_job/basic_spark_job/src",
                entry={"file": "./main.py"},
                resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.4.0"),
                driver_cores=1,
                driver_memory="2g",
                executor_cores=2,
                executor_memory="2g",
            )
            node._to_job()._to_rest_object()
            assert ve.message == "runtime version should be either 3.2 or 3.3"

    def test_resources_3_runtime_version(self):
        with pytest.raises(ValidationException) as ve:
            node = spark(
                code="./tests/test_configs/spark_job/basic_spark_job/src",
                entry={"file": "./main.py"},
                resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3"),
                driver_cores=1,
                driver_memory="2g",
                executor_cores=2,
                executor_memory="2g",
            )
            node._to_job()._to_rest_object()
            assert ve.message == "runtime version should be either 3.2 or 3.3"

    def test_resources_runtime_version_with_char(self):
        with pytest.raises(ValueError) as ve:
            node = spark(
                code="./tests/test_configs/spark_job/basic_spark_job/src",
                entry={"file": "./main.py"},
                resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.2.abc"),
                driver_cores=1,
                driver_memory="2g",
                executor_cores=2,
                executor_memory="2g",
            )
            node._to_job()._to_rest_object()
            assert ve.message == "runtime_version should only contain numbers"

    def test_missing_entry_with_dict_resources_raises(self):
        with pytest.raises(ValidationException):
            node = spark(
                code="./tests/test_configs/spark_job/basic_spark_job/src",
                resources={
                    "instance_type": "Standard_E8S_V3",
                    "runtime_version": "3.2.0",
                },
            )
            node._to_job()._to_rest_object()

    def test_missing_entry_with_SparkResourceConfiguration_resources_raises(self):
        with pytest.raises(ValidationException):
            node = spark(
                code="./tests/test_configs/spark_job/basic_spark_job/src",
                resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.2.0"),
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
                resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.2.0"),
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
                resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.2.0"),
            )
            node._to_job()._to_rest_object()

    def test_spark_job_with_dynamic_allocation_disabled(self):
        with pytest.raises(ValidationException):
            node = spark(
                code="./tests/test_configs/spark_job/basic_spark_job/src",
                entry={"file": "./main.py"},
                resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.2.0"),
                driver_cores=1,
                driver_memory="2g",
                executor_cores=2,
                executor_memory="2g",
                executor_instances=2,
                dynamic_allocation_min_executors=1,
                dynamic_allocation_max_executors=3,
            )
            node._to_job()._to_rest_object()

    def test_spark_job_with_dynamic_allocation_enabled(self):
        node = spark(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.2.0"),
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            dynamic_allocation_enabled=True,
            dynamic_allocation_min_executors=1,
            dynamic_allocation_max_executors=3,
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

    def test_executor_instances_is_mandatory_when_dynamic_allocation_disabled(self):
        with pytest.raises(ValidationException) as ve:
            node = spark(
                code="./tests/test_configs/spark_job/basic_spark_job/src",
                entry={"file": "./main.py"},
                resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.2.0"),
                driver_cores=1,
                driver_memory="2g",
                executor_cores=2,
                executor_memory="2g",
            )
            node._to_job()._to_rest_object()
            assert (
                ve.message
                == "spark.driver.cores, spark.driver.memory, spark.executor.cores, spark.executor.memory and spark.executor.instances are mandatory fields."
            )

    def test_executor_instances_is_specified_as_min_executor_if_unset(self):
        node = spark(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.2.0"),
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            dynamic_allocation_enabled=True,
            dynamic_allocation_min_executors=1,
            dynamic_allocation_max_executors=3,
        )
        the_job = node._to_job()
        the_job._to_rest_object()
        assert the_job.executor_instances == 1

    def test_excutor_instances_throw_error_when_out_of_range(self):
        with pytest.raises(ValidationException) as ve:
            node = spark(
                code="./tests/test_configs/spark_job/basic_spark_job/src",
                entry={"file": "./main.py"},
                resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.2.0"),
                driver_cores=1,
                driver_memory="2g",
                executor_cores=2,
                executor_memory="2g",
                executor_instances=4,
                dynamic_allocation_enabled=True,
                dynamic_allocation_min_executors=1,
                dynamic_allocation_max_executors=3,
            )
            node._to_job()._to_rest_object()
            assert (
                ve.message
                == "Executor instances must be a valid non-negative integer and must be between spark.dynamicAllocation.minExecutors and spark.dynamicAllocation.maxExecutors."
            )

    def test_spark_job_with_additional_conf(self):
        node = spark(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.2.0"),
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            conf={
                "spark.jars.packages": "com.microsoft.ml.spark:mmlspark_2.11:0.15",
                "spark.jars.repositories": "https://mmlspark.azureedge.net/maven",
                "spark.jars.excludes": "slf4j",
            },
        )
        expected_conf = {
            "spark.driver.cores": 1,
            "spark.driver.memory": "2g",
            "spark.executor.cores": 2,
            "spark.executor.memory": "2g",
            "spark.executor.instances": 2,
            "spark.jars.packages": "com.microsoft.ml.spark:mmlspark_2.11:0.15",
            "spark.jars.repositories": "https://mmlspark.azureedge.net/maven",
            "spark.jars.excludes": "slf4j",
        }
        assert node._to_job()._to_rest_object().properties.conf == expected_conf

    def test_spark_job_load_from_rest_job_valid_entry(self):
        node = spark(
            name="builder-spark-job",
            experiment_name="builder-spark-experiment-name",
            description="simply spark description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            jars=["simple-1.1.1.jar"],
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            resources={
                "instance_type": "Standard_E8S_V3",
                "runtime_version": "3.2.0",
            },
        )
        job_properties = RestSparkJob(
            display_name="builder-spark-job",
            description="simply spark description",
            code_id="/subscriptions/2d385bf4-0756-4a76-aa95-28bf9ed3b625/resourceGroups/douglas-rg/providers/Microsoft.MachineLearningServices/workspaces/DouglasCentralUSEuap/codes/cb5ebee5-8216-49a8-a63a-0f6b051dc52b/versions/1",
            entry=SparkJobPythonEntry(file="./main.py"),
            conf={
                "spark.driver.cores": 1,
                "spark.driver.memory": "2g",
                "spark.executor.cores": 2,
                "spark.executor.memory": "2g",
                "spark.executor.instances": 2,
            },
            environment_id="/subscriptions/2d385bf4-0756-4a76-aa95-28bf9ed3b625/resourceGroups/douglas-rg/providers/Microsoft.MachineLearningServices/workspaces/DouglasCentralUSEuap/environments/condaenv/versions/1",
        )
        job_base_obj = JobBase(properties=job_properties)
        spark_job_result = node._load_from_rest_job(obj=job_base_obj)
        assert spark_job_result.entry.__dict__.get("entry_type") == "SparkJobPythonEntry"
        assert spark_job_result.entry.__dict__.get("entry") == "./main.py"

    def test_spark_job_load_from_rest_job_invalid_entry(self):
        node = spark(
            name="builder-spark-job",
            experiment_name="builder-spark-experiment-name",
            description="simply spark description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            jars=["simple-1.1.1.jar"],
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            resources={
                "instance_type": "Standard_E8S_V3",
                "runtime_version": "3.2.0",
            },
        )
        job_properties = RestSparkJob(
            display_name="builder-spark-job",
            description="simply spark description",
            code_id="/subscriptions/2d385bf4-0756-4a76-aa95-28bf9ed3b625/resourceGroups/douglas-rg/providers/Microsoft.MachineLearningServices/workspaces/DouglasCentralUSEuap/codes/cb5ebee5-8216-49a8-a63a-0f6b051dc52b/versions/1",
            entry=None,
            conf={
                "spark.driver.cores": 1,
                "spark.driver.memory": "2g",
                "spark.executor.cores": 2,
                "spark.executor.memory": "2g",
                "spark.executor.instances": 2,
            },
            environment_id="/subscriptions/2d385bf4-0756-4a76-aa95-28bf9ed3b625/resourceGroups/douglas-rg/providers/Microsoft.MachineLearningServices/workspaces/DouglasCentralUSEuap/environments/condaenv/versions/1",
        )
        job_base_obj = JobBase(properties=job_properties)
        spark_job_result = node._load_from_rest_job(obj=job_base_obj)
        assert spark_job_result.entry is None

    def test_spark_job_builder_serialization(self) -> None:
        node = spark(
            name="builder-spark-job",
            experiment_name="builder-spark-experiment-name",
            description="simply spark description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            jars=["simple-1.1.1.jar"],
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            dynamic_allocation_enabled=True,
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
                "runtime_version": "3.2.0",
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
            dynamic_allocation_enabled=True,
            dynamic_allocation_min_executors=1,
            dynamic_allocation_max_executors=3,
            name="builder-spark-job",
            experiment_name="builder-spark-experiment-name",
            description="simply spark description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
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
                "runtime_version": "3.2.0",
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
            dynamic_allocation_enabled=True,
            dynamic_allocation_min_executors=1,
            dynamic_allocation_max_executors=3,
            name="builder-spark-job",
            experiment_name="builder-spark-experiment-name",
            description="simply spark description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
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
            resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.2.0"),
        )

        assert expected_job._to_dict() == node._to_job()._to_dict()
        assert expected_job_with_object_resources._to_dict() == node._to_job()._to_dict()

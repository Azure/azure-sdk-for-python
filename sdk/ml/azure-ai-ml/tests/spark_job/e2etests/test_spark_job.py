from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import Input, ManagedIdentityConfiguration, MLClient, Output, load_job, spark
from azure.ai.ml.entities._job.spark_job import SparkJob


@pytest.mark.timeout(600)
@pytest.mark.usefixtures("recorded_test", "mock_asset_name", "mock_code_hash")
@pytest.mark.skip(reason="user assigned identity not attached to test workspace")
@pytest.mark.training_experiences_test
class TestSparkJob(AzureRecordedTestCase):
    @pytest.mark.e2etest
    def test_spark_job(self, randstr: Callable[[], str], client: MLClient) -> None:
        job_name = randstr("job_name")
        print(f"Creating spark job {job_name}")

        try:
            _ = client.jobs.get(job_name)

            # shouldn't happen!
            print(f"Found existing job {job_name}")
        except Exception as ex:
            print(f"Job {job_name} not found: {ex}")

        params_override = [{"name": job_name}]
        job = load_job(
            source="./tests/test_configs/spark_job/spark_job_test_hobo.yml",
            params_override=params_override,
        )
        spark_job: SparkJob = client.jobs.create_or_update(job=job)

        assert spark_job.name == job_name
        assert spark_job.description == "simply the best"
        assert spark_job.type == "spark"
        assert spark_job.resources.instance_type == "standard_e8s_v3"
        assert spark_job.resources.runtime_version == "3.2"

    @pytest.mark.e2etest
    def test_spark_job_word_count_inputs(sef, randstr: Callable[[], str], client: MLClient) -> None:
        job_name = randstr()
        print(f"Creating spark job {job_name}")
        params_override = [{"name": job_name}]
        job = load_job(
            source="./tests/test_configs/spark_job/spark_job_word_count_test.yml",
            params_override=params_override,
        )
        spark_job: SparkJob = client.jobs.create_or_update(job=job)

        assert spark_job.name == job_name
        assert spark_job.description == "submit a hobo spark job testing inputs"
        assert spark_job.type == "spark"
        assert spark_job.resources.instance_type == "standard_e8s_v3"
        assert spark_job.resources.runtime_version == "3.2"

    @pytest.mark.e2etest
    def test_spark_job_builder(self, client: MLClient) -> None:
        inputs = {
            "input1": Input(
                type="uri_file", path="azureml://datastores/workspaceblobstore/paths/python/data.csv", mode="direct"
            )
        }
        outputs = {
            "output1": Output(
                type="uri_file",
                path="azureml://datastores/workspaceblobstore/spark_titanic_output/titanic.parquet",
                mode="direct",
            )
        }

        node = spark(
            experiment_name="builder-spark-experiment-name",
            description="simply spark description",
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
            identity=ManagedIdentityConfiguration(),
            inputs=inputs,
            outputs=outputs,
            args="--input1 ${{inputs.input1}} --output1 ${{outputs.output1}} --my_sample_rate 0.01",
            resources={
                "instance_type": "Standard_E8S_V3",
                "runtime_version": "3.2.0",
            },
        )

        assert node.experiment_name == "builder-spark-experiment-name"
        assert node.identity == ManagedIdentityConfiguration()
        assert node.description == "simply spark description"

        result = client.create_or_update(node)
        assert result.description == "simply spark description"
        assert result.experiment_name == "builder-spark-experiment-name"
        assert result.identity == ManagedIdentityConfiguration()

    @pytest.mark.e2etest
    def test_spark_job_with_input_output(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # TODO: check issue with backend
        # run failed
        # https://msdata.visualstudio.com/Vienna/_workitems/edit/1940993
        params_override = [{"name": randstr()}]
        job = load_job(
            "./tests/test_configs/spark_job/spark_job_inputs_outputs_test.yml",
            params_override=params_override,
        )
        spark_job = client.jobs.create_or_update(job=job)
        assert spark_job.name == params_override[0]["name"]

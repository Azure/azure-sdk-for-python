import pytest
from typing import Callable
from azure.ai.ml import MLClient, Input, Output, load_job, spark
from azure.ai.ml.entities._job.spark_job import SparkJob
from azure.ai.ml._restclient.v2022_06_01_preview.models import AmlToken

from devtools_testutils import AzureRecordedTestCase


@pytest.mark.timeout(600)
@pytest.mark.usefixtures("recorded_test", "mock_asset_name", "mock_code_hash")
class TestSparkJob(AzureRecordedTestCase):
    @pytest.mark.e2etest
    @pytest.mark.skip(reason="no way of currently testing this due to 500 InternalServerError with MFE API")
    def test_spark_job(self, randstr: Callable[[str], str], client: MLClient) -> None:
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
            source="./tests/test_configs/spark_job/spark_job_test.yml",
            params_override=params_override,
        )
        spark_job: SparkJob = client.jobs.create_or_update(job=job)

        assert spark_job.name == job_name
        assert spark_job.compute == "douglassynapse"

    @pytest.mark.e2etest
    @pytest.mark.skip(reason="no way of currently testing this due to 500 InternalServerError with MFE API")
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
            inputs=inputs,
            outputs=outputs,
            args="--input1 ${{inputs.input1}} --output1 ${{outputs.output1}} --my_sample_rate 0.01",
            resources={
                "instance_type": "Standard_E8S_V3",
                "runtime_version": "3.1.0",
            },
        )

        assert node.environment == "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1"
        assert node.name == "builder-spark-job"
        assert node.experiment_name == "builder-spark-experiment-name"
        assert node.identity == AmlToken()
        assert node.description == "simply spark description"

        result = client.create_or_update(node)
        assert result.description == "simply spark description"
        assert result.experiment_name == "builder-spark-experiment-name"
        assert result.environment == "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1"
        assert result.identity == AmlToken()

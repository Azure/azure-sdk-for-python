from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient, load_batch_deployment, load_batch_endpoint
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.core.exceptions import ResourceNotFoundError


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "mock_asset_name")
@pytest.mark.production_experiences_test
class TestBatchEndpoint(AzureRecordedTestCase):
    def test_batch_endpoint_create(self, client: MLClient, rand_batch_name: Callable[[], str]) -> None:
        endpoint_yaml = "./tests/test_configs/endpoints/batch/batch_endpoint.yaml"
        name = rand_batch_name("name")
        # Bug in MFE that batch endpoint properties are not preserved, uncomment below after it's fixed in MFE
        # properties = {"property1": "value1", "property2": "value2"}
        endpoint = load_batch_endpoint(endpoint_yaml)
        endpoint.name = name
        # endpoint.properties = properties
        obj = client.batch_endpoints.begin_create_or_update(endpoint=endpoint)
        obj = obj.result()
        assert obj is not None
        assert name == obj.name
        # assert obj.properties == properties

        get_obj = client.batch_endpoints.get(name=name)
        assert get_obj.name == name

        delete_res = client.batch_endpoints.begin_delete(name=name)
        delete_res = delete_res.result()
        try:
            client.batch_endpoints.get(name=name)
        except Exception as e:
            assert type(e) is ResourceNotFoundError
            return

        raise Exception(f"Batch endpoint {name} is supposed to be deleted.")

    @pytest.mark.usefixtures("light_gbm_model")
    def test_mlflow_batch_endpoint_create_and_update(
        self, client: MLClient, rand_batch_name: Callable[[], str]
    ) -> None:
        # light_gbm_model fixture is not used directly, but it makes sure the model being used by the batch endpoint exists

        endpoint_yaml = "./tests/test_configs/endpoints/batch/batch_endpoint_mlflow.yaml"
        name = rand_batch_name("name")
        endpoint = load_batch_endpoint(endpoint_yaml)
        endpoint.name = name
        obj = client.batch_endpoints.begin_create_or_update(endpoint=endpoint)
        obj = obj.result()
        assert obj is not None
        assert name == obj.name

        get_obj = client.batch_endpoints.get(name=name)
        assert get_obj.name == name

        delete_res = client.batch_endpoints.begin_delete(name=name)
        delete_res = delete_res.result()
        try:
            client.batch_endpoints.get(name=name)
        except Exception as e:
            assert type(e) is ResourceNotFoundError
            return

        raise Exception(f"Batch endpoint {name} is supposed to be deleted.")

    @pytest.mark.skip("TODO (2349930) SSL Certificate error")
    def test_batch_invoke(
        self, client: MLClient, rand_batch_name: Callable[[], str], rand_batch_deployment_name: Callable[[], str]
    ) -> None:
        endpoint_yaml = "./tests/test_configs/endpoints/batch/simple_batch_endpoint.yaml"
        endpoint_name = rand_batch_name("endpoint_name")
        endpoint = load_batch_endpoint(endpoint_yaml)
        endpoint.name = endpoint_name

        deployment_yaml = "./tests/test_configs/deployments/batch/batch_deployment_3.yaml"
        deployment_name = rand_batch_deployment_name("deployment_name")

        deployment = load_batch_deployment(deployment_yaml)
        deployment.endpoint_name = endpoint_name
        deployment.name = deployment_name

        # create the batch endpoint
        client.batch_endpoints.begin_create_or_update(endpoint).result()
        # create a deployment
        client.batch_deployments.begin_create_or_update(deployment).result()

        # Invoke using inputs: Dict[str, Input]
        input_1 = Input(
            type="uri_folder",
            path="https://pipelinedata.blob.core.windows.net/sampledata/mnist",
        )

        batchjob = client.batch_endpoints.invoke(
            endpoint_name=endpoint_name, deployment_name=deployment_name, inputs={"input1": input_1}
        )
        assert batchjob

        # Invoke using deprecated input: Input
        batchjob_input = client.batch_endpoints.invoke(
            endpoint_name=endpoint_name, deployment_name=deployment_name, input=input_1
        )
        assert batchjob_input

    @pytest.mark.skipif(
        condition=not is_live(),
        reason="Update operation is not valid. If we use the same endpoint/deployment this will throw an error",
    )
    def test_batch_component(
        self, client: MLClient, rand_batch_name: Callable[[], str], rand_batch_deployment_name: Callable[[], str]
    ) -> None:
        endpoint_yaml = "./tests/test_configs/endpoints/batch/batch_endpoint_deployment_component.yaml"
        endpoint_name = rand_batch_name("endpoint_name")
        endpoint = load_batch_endpoint(endpoint_yaml)
        endpoint.name = endpoint_name

        # Create deployment using local files
        deployment_yaml = "./tests/test_configs/deployments/batch/batch_deployment_component.yaml"
        deployment_name = rand_batch_deployment_name("deployment_name")

        deployment = load_batch_deployment(deployment_yaml)
        deployment.endpoint_name = endpoint_name
        deployment.name = deployment_name

        # create the batch endpoint
        endpoint = client.batch_endpoints.begin_create_or_update(endpoint).result()
        # create a deployment
        client.batch_deployments.begin_create_or_update(deployment).result()

        # Batch endpoint invoke using different supported inputs
        inputs_dict = {
            "input_1": Input(path="azureml:list_data_v2_test:2", type="uri_folder"),
            "input_2": Input(path="azureml:list_data_v2_test:2", type="uri_folder"),
        }

        job = client.batch_endpoints.invoke(
            endpoint_name=endpoint.name,
            deployment_name=deployment.name,
            inputs=inputs_dict,
        )
        assert job

    @pytest.mark.skip("TODO (2349930) SSL Certificate error")
    def test_batch_invoke_outputs(
        self,
        client: MLClient,
        rand_batch_name: Callable[[], str],
        rand_batch_deployment_name: Callable[[], str],
        randstr: Callable[[str], str],
    ) -> None:
        endpoint_yaml = "./tests/test_configs/endpoints/batch/simple_batch_endpoint.yaml"
        endpoint_name = rand_batch_name("endpoint_name")
        endpoint = load_batch_endpoint(endpoint_yaml)
        endpoint.name = endpoint_name

        deployment_yaml = "./tests/test_configs/deployments/batch/batch_deployment_3.yaml"
        deployment_name = rand_batch_deployment_name("deployment_name")

        deployment = load_batch_deployment(deployment_yaml)
        deployment.endpoint_name = endpoint_name
        deployment.name = deployment_name

        # create the batch endpoint
        client.batch_endpoints.begin_create_or_update(endpoint).result()
        # create a deployment
        client.batch_deployments.begin_create_or_update(deployment).result()

        # Invoke using inputs: Dict[str, Input]
        input_1 = Input(
            type="uri_folder",
            path="https://pipelinedata.blob.core.windows.net/sampledata/mnist",
        )

        # Invoke using outputs: Dict[str, Output]
        output_file_name = randstr("output_file")
        output_1 = Output(
            type="uri_file",
            path="azureml://datastores/workspaceblobstore/paths/batchendpointinvoke/mnistOutput/"
            + output_file_name
            + ".csv",
        )

        batchjob = client.batch_endpoints.invoke(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            inputs={"input1": input_1},
            outputs={"output": output_1},
        )
        assert batchjob

        delete_res = client.batch_endpoints.begin_delete(name=endpoint_name)
        delete_res = delete_res.result()

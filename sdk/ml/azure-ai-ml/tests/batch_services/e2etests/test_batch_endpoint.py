import uuid

import pytest

from azure.ai.ml import MLClient, load_batch_endpoint, load_batch_deployment
from azure.ai.ml.entities._assets import Model
from azure.ai.ml.entities._inputs_outputs import Input
from azure.core.exceptions import ResourceNotFoundError

from devtools_testutils import AzureRecordedTestCase


@pytest.mark.e2etest
@pytest.mark.production_experience_test
class TestBatchEndpoint(AzureRecordedTestCase):
    @pytest.mark.skip(
        reason="Tests failing in internal automation due to lack of quota. Cannot record or run in live mode."
    )
    def test_batch_endpoint_create_and_invoke(
        self, client: MLClient, data_with_2_versions: str, batch_endpoint_model: Model
    ) -> None:
        endpoint_yaml = "./tests/test_configs/endpoints/batch/batch_endpoint.yaml"
        name = "be-e2e-" + uuid.uuid4().hex[:25]
        # Bug in MFE that batch endpoint properties are not preserved, uncomment below after it's fixed in MFE
        # properties = {"property1": "value1", "property2": "value2"}
        endpoint = load_batch_endpoint(endpoint_yaml)
        endpoint.name = name
        # endpoint.properties = properties
        obj = client.batch_endpoints.begin_create_or_update(endpoint=endpoint, no_wait=False)
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

    @pytest.mark.skip(
        reason="Tests failing in internal automation due to lack of quota. Cannot record or run in live mode."
    )
    @pytest.mark.e2etest
    @pytest.mark.usefixtures("light_gbm_model")
    def test_mlflow_batch_endpoint_create_and_update(self, client: MLClient) -> None:
        # light_gbm_model fixture is not used directly, but it makes sure the model being used by the batch endpoint exists

        endpoint_yaml = "./tests/test_configs/endpoints/batch/batch_endpoint_mlflow.yaml"
        name = "be-e2e-" + uuid.uuid4().hex[:25]
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


    def test_batch_invoke(self, client: MLClient, variable_recorder) -> None:
        endpoint_yaml = "./tests/test_configs/endpoints/batch/simple_batch_endpoint.yaml"
        endpoint_name = variable_recorder.get_or_record("endpoint_name", "be-e2e-" + uuid.uuid4().hex[:15])
        endpoint = load_batch_endpoint(endpoint_yaml)
        endpoint.name = endpoint_name

        deployment_yaml = "./tests/test_configs/deployments/batch/batch_deployment_3.yaml"
        deployment_name = variable_recorder.get_or_record("deployment_name", "batch-dpm-" + uuid.uuid4().hex[:15])

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
            path='https://pipelinedata.blob.core.windows.net/sampledata/mnist',
        )

        batchjob = client.batch_endpoints.invoke(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            inputs = {"input1": input_1}
        )
        assert batchjob

        # Invoke using deprecated input: Input
        batchjob_input = client.batch_endpoints.invoke(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            input = input_1
        )
        assert batchjob_input
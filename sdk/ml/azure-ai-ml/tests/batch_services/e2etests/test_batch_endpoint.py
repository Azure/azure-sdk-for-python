import uuid

import pytest

from azure.ai.ml import MLClient, load_batch_endpoint
from azure.ai.ml.entities._assets import Model
from azure.core.exceptions import ResourceNotFoundError

from devtools_testutils import AzureRecordedTestCase


@pytest.mark.skip(
    reason="Tests failing in internal automation due to lack of quota. Cannot record or run in live mode."
)
@pytest.mark.e2etest
class TestBatchEndpoint(AzureRecordedTestCase):
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
        assert obj is not None
        assert name == obj.name
        # assert obj.properties == properties

        get_obj = client.batch_endpoints.get(name=name)
        assert get_obj.name == name

        client.batch_endpoints.begin_delete(name=name)
        try:
            client.batch_endpoints.get(name=name)
        except Exception as e:
            assert type(e) is ResourceNotFoundError
            return

        raise Exception(f"Batch endpoint {name} is supposed to be deleted.")

    @pytest.mark.e2etest
    @pytest.mark.usefixtures("light_gbm_model")
    def test_mlflow_batch_endpoint_create_and_update(self, client: MLClient) -> None:
        # light_gbm_model fixture is not used directly, but it makes sure the model being used by the batch endpoint exists

        endpoint_yaml = "./tests/test_configs/endpoints/batch/batch_endpoint_mlflow.yaml"
        name = "be-e2e-" + uuid.uuid4().hex[:25]
        endpoint = load_batch_endpoint(endpoint_yaml)
        endpoint.name = name
        obj = client.batch_endpoints.begin_create_or_update(endpoint=endpoint, no_wait=False)
        assert obj is not None
        assert name == obj.name

        get_obj = client.batch_endpoints.get(name=name)
        assert get_obj.name == name

        client.batch_endpoints.begin_delete(name=name)
        try:
            client.batch_endpoints.get(name=name)
        except Exception as e:
            assert type(e) is ResourceNotFoundError
            return

        raise Exception(f"Batch endpoint {name} is supposed to be deleted.")

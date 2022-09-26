import pytest

from azure.ai.ml import MLClient
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.exceptions import ValidationException
from azure.identity import ClientSecretCredential


@pytest.mark.e2etest
class TestMlClient:
    def test_ml_client_validation_rg_sub_missing_throws(
        self, auth: ClientSecretCredential
    ) -> None:
        with pytest.raises(ValidationException) as exception:
            MLClient(
                credential=auth,
            )
        message = exception.value.args[0]
        assert (
            message
            == "Both subscription id and resource group are required for this operation, missing subscription id and resource group"
        )

    def test_ml_client_with_no_rg_sub_for_registry(self, only_registry_client: MLClient) -> None:
        environment_list = only_registry_client._environments.list()
        assert environment_list

    def test_ml_client_with_no_rg_sub_for_ws_throws(
        self, e2e_ws_scope: OperationScope, auth: ClientSecretCredential
    ) -> None:
        with pytest.raises(ValidationException) as exception:
            MLClient(
                credential=auth,
                workspace_name=e2e_ws_scope.workspace_name,
            )
        message = exception.value.args[0]
        assert (
            message
            == "Both subscription id and resource group are required for this operation, missing subscription id and resource group"
        )

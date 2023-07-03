import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient

from .._util import _COMPONENT_TIMEOUT_SECOND


@pytest.mark.e2etest
@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.pipeline_test
class TestComponentWithoutMock(AzureRecordedTestCase):
    """Do not use component related mock here."""

    def test_get_client_key(
        self, client: MLClient, registry_client: MLClient, pipelines_registry_client: MLClient
    ) -> None:
        """
        Test private interface to get client key.
        If you need to change the private interfaces and this test, please also update related code in
        mock_component_hash.
        """
        workspace_key = client.components._get_workspace_key()
        assert workspace_key
        assert "workspace/" + workspace_key == client.components._get_client_key()

        registry_key1 = registry_client.components._get_registry_key()
        registry_key2 = pipelines_registry_client.components._get_registry_key()
        assert registry_key1
        assert registry_key2
        assert "registry/" + registry_key1 == registry_client.components._get_client_key()
        assert "registry/" + registry_key2 == pipelines_registry_client.components._get_client_key()
        assert registry_key1 != registry_key2

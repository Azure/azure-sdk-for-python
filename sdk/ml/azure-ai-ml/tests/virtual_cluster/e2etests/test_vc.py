import pytest
import re
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient


@pytest.mark.usefixtures("recorded_test")
@pytest.mark.virtual_cluster_test
class TestVirtualCluster(AzureRecordedTestCase):
    @pytest.mark.e2etest
    def test_get_and_list(self, client: MLClient) -> None:
        vc_list = client._virtual_clusters.list()
        assert len(vc_list) > 0

        test_vc_name = "SingularityTestVC"
        singularity_test_vc = [vc for vc in vc_list if vc["name"] == test_vc_name][0]

        # Test get by ARM id
        vc = client._virtual_clusters.get(singularity_test_vc["id"])
        assert test_vc_name == vc["name"]

        # Test get by name
        REGEX_PATTERN = "^/?subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/Microsoft.MachineLearningServices/virtualclusters/([^/]+)"
        match = re.match(REGEX_PATTERN, singularity_test_vc["id"])
        subscription_id = match.group(1)
        resource_group_name = match.group(2)
        vc_name = match.group(3)

        vc_get_client = MLClient(client._credential, subscription_id, resource_group_name)
        vc = vc_get_client._virtual_clusters.get(vc_name)
        assert test_vc_name == vc["name"]


import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient

@pytest.mark.timeout(600)
@pytest.mark.usefixtures(
    "recorded_test"
)
@pytest.mark.training_experiences_test
class TestVirtualCluster(AzureRecordedTestCase):

    @pytest.mark.e2etest
    def test_get_and_list(self, client: MLClient) -> None:


        vc_list = client._virtual_clusters.list()

        assert len(vc_list) > 0

        singularity_test_vc = [vc for vc in vc_list if vc.name == "SingularityTestVC"][0]

        
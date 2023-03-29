import re

import pytest
from azure.identity import ClientSecretCredential
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml._utils._arm_id_utils import AzureResourceId
from azure.ai.ml.entities import Job


@pytest.fixture(scope="session")
def virtual_cluster_name() -> str:
    """The name of the virtual cluster

    Note: Bootstrapping virtual cluster creation as part of setting up test resources is non-trivial.
    So this test file performs tests on a long-living virtual cluster that is available to our test runner,
    until a virtual cluster creation can be included in our test resource creation.

    This notably means that this test file will not run if there is no virtual cluster available.
    """
    return "SingularityTestVC"


@pytest.fixture()
def virtual_cluster(virtual_cluster_name: str, client: MLClient) -> dict:
    """Fetches the virtual cluster object

    NOTE: This should ideally should be a session scoped test fixture
    """
    cluster = next((vc for vc in client._virtual_clusters.list() if vc["name"] == virtual_cluster_name), None)
    assert cluster is not None, "Can not find cluster used for testing"
    return cluster


@pytest.fixture()
def virtual_cluster_id(virtual_cluster) -> str:
    """The azure resource id of the test virtual cluster"""
    return virtual_cluster["id"]


@pytest.fixture()
def virtual_cluster_client(virtual_cluster_id: str, auth: ClientSecretCredential) -> MLClient:
    """An MLClient in the same subscription and resource group as the test virtual cluster"""
    parsed_id = AzureResourceId(virtual_cluster_id)
    return MLClient(
        credential=auth,
        subscription_id=parsed_id.subscription_id,
        resource_group_name=parsed_id.resource_group_name,
    )


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

    @pytest.mark.e2etest
    def test_list_jobs(self, virtual_cluster_client: MLClient, virtual_cluster_name: str):
        job_iterable = virtual_cluster_client._virtual_clusters.list_jobs(virtual_cluster_name)

        first_element = next(iter(job_iterable), None)
        assert first_element is not None, "list_jobs should return a non empty iterable"
        assert isinstance(first_element, Job), "list_jobs should return an iterable of Jobs"

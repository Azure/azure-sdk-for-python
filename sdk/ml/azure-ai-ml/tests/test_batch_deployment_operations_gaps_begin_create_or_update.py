from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient, load_batch_deployment
from azure.ai.ml.entities import BatchDeployment
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.polling import LROPoller


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestBatchDeploymentBeginCreateOrUpdateBranches(AzureRecordedTestCase):
    """Tests exercising error paths in batch deployment operations
    that do not require pre-provisioned batch infrastructure."""

    def test_begin_create_or_update_nonexistent_endpoint_raises(
        self,
        client: MLClient,
        rand_batch_name: Callable[[], str],
        rand_batch_deployment_name: Callable[[], str],
    ) -> None:
        """Deploying to a nonexistent endpoint should raise from the
        internal endpoint-existence check."""
        deployment_yaml = "./tests/test_configs/deployments/batch/batch_deployment_quick.yaml"
        deployment = load_batch_deployment(deployment_yaml)
        deployment.endpoint_name = rand_batch_name("nonexistent_ep")
        deployment.name = rand_batch_deployment_name("dep_name")

        with pytest.raises((ResourceNotFoundError, HttpResponseError)):
            poller = client.batch_deployments.begin_create_or_update(deployment)
            poller.result()

    def test_begin_create_or_update_with_invalid_deployment_type_raises(
        self,
        client: MLClient,
    ) -> None:
        """Passing an object that is not a BatchDeployment should raise."""
        with pytest.raises((AttributeError, TypeError)):
            poller = client.batch_deployments.begin_create_or_update("not-a-deployment")  # type: ignore[arg-type]
            poller.result()

    def test_begin_create_or_update_skip_script_validation_flag(
        self,
        client: MLClient,
        rand_batch_name: Callable[[], str],
        rand_batch_deployment_name: Callable[[], str],
    ) -> None:
        """The skip_script_validation kwarg should be accepted.  The call
        still fails (nonexistent endpoint) but with an HTTP/resource error,
        not a script-validation error."""
        deployment_yaml = "./tests/test_configs/deployments/batch/batch_deployment_quick.yaml"
        deployment = load_batch_deployment(deployment_yaml)
        deployment.endpoint_name = rand_batch_name("skip_val_ep")
        deployment.name = rand_batch_deployment_name("skip_val_dep")

        with pytest.raises((ResourceNotFoundError, HttpResponseError)):
            poller = client.batch_deployments.begin_create_or_update(
                deployment, skip_script_validation=True
            )
            poller.result()

    def test_list_deployments_nonexistent_endpoint_raises(
        self,
        client: MLClient,
        rand_batch_name: Callable[[], str],
    ) -> None:
        """Listing deployments for a nonexistent endpoint should raise
        when the lazy iterator is consumed."""
        endpoint_name = rand_batch_name("list_ep")

        with pytest.raises((ResourceNotFoundError, HttpResponseError)):
            result = client.batch_deployments.list(endpoint_name=endpoint_name)
            # Force evaluation of the lazy iterator
            for _ in result:
                pass

    def test_get_nonexistent_deployment_raises(
        self,
        client: MLClient,
        rand_batch_name: Callable[[], str],
        rand_batch_deployment_name: Callable[[], str],
    ) -> None:
        """Getting a deployment on a nonexistent endpoint should raise
        ResourceNotFoundError."""
        with pytest.raises((ResourceNotFoundError, HttpResponseError)):
            client.batch_deployments.get(
                name=rand_batch_deployment_name("get_dep"),
                endpoint_name=rand_batch_name("get_ep"),
            )

    def test_delete_nonexistent_deployment_returns_poller(
        self,
        client: MLClient,
        rand_batch_name: Callable[[], str],
        rand_batch_deployment_name: Callable[[], str],
    ) -> None:
        """Deleting a nonexistent deployment is idempotent — begin_delete
        returns an LROPoller that completes without error."""
        poller = client.batch_deployments.begin_delete(
            name=rand_batch_deployment_name("del_dep"),
            endpoint_name=rand_batch_name("del_ep"),
        )
        assert isinstance(poller, LROPoller)
        poller.result()  # should complete without raising

    def test_validate_component_with_invalid_type_raises(
        self,
        client: MLClient,
        rand_batch_name: Callable[[], str],
        rand_batch_deployment_name: Callable[[], str],
    ) -> None:
        """Setting deployment.component to an invalid type (integer) and
        attempting to deploy should raise an error.  The endpoint-existence
        check fires first for a regular BatchDeployment, so we expect
        a service-level error."""
        deployment = BatchDeployment(
            name=rand_batch_deployment_name("comp_dep"),
            endpoint_name=rand_batch_name("comp_ep"),
        )
        deployment.component = 12345  # type: ignore[assignment]

        with pytest.raises((ResourceNotFoundError, HttpResponseError, TypeError, AttributeError)):
            poller = client.batch_deployments.begin_create_or_update(deployment)
            poller.result()

    def test_list_jobs_nonexistent_endpoint_raises(
        self,
        client: MLClient,
        rand_batch_name: Callable[[], str],
    ) -> None:
        """Listing jobs for a nonexistent endpoint should raise when
        the lazy iterator is consumed."""
        endpoint_name = rand_batch_name("jobs_ep")

        with pytest.raises((ResourceNotFoundError, HttpResponseError, ValueError)):
            result = client.batch_deployments.list_jobs(endpoint_name=endpoint_name)
            list(result)  # force lazy iterator to fetch

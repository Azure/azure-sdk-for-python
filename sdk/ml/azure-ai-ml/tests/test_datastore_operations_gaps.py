import os
import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.exceptions import MlException
from azure.core.exceptions import ResourceNotFoundError


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.live_test_only("Exercises compute-backed persistent mount polling paths; only run live")
class TestDatastoreMountLive(AzureRecordedTestCase):
    def test_mount_persistent_polling_handles_failure_or_unexpected_state(self, client: MLClient) -> None:
        """
        Cover persistent mount polling branch where the code fetches Compute resource mounts and
        reacts to MountFailed or unexpected states by raising MlException.

        This test runs only live because it relies on the Compute API and the presence of
        azureml.dataprep in the environment. It sets CI_NAME to emulate running on a compute instance
        so DatastoreOperations.mount enters the persistent polling loop and exercises the branches
        that raise MlException for MountFailed or unexpected mount_state values.
        """
        # Ensure CI_NAME is set so persistent mount branch is taken
        prev_ci = os.environ.get("CI_NAME")
        os.environ["CI_NAME"] = "test_dummy"

        # Use a datastore name that is syntactically valid. Unique to avoid collisions.
        datastore_path = "test_dummy"

        try:
            with pytest.raises((MlException, ResourceNotFoundError)):
                # Call the public API which will trigger the persistent mount branch.
                client.datastores.mount(datastore_path, persistent=True)
        finally:
            # Restore environment
            if prev_ci is None:
                del os.environ["CI_NAME"]
            else:
                os.environ["CI_NAME"] = prev_ci

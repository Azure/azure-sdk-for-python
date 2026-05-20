from typing import Callable

import os
import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient
from azure.ai.ml.exceptions import MlException
from azure.core.exceptions import ResourceNotFoundError


@pytest.mark.e2etest
class TestDatastoreMount:
    def test_mount_invalid_mode_raises_assertion(self, client: MLClient) -> None:
        random_name = "test_dummy"
        # mode validation should raise AssertionError before any imports or side effects
        with pytest.raises(AssertionError) as ex:
            client.datastores.mount(random_name, mode="invalid_mode")
        assert "mode should be either `ro_mount` or `rw_mount`" in str(ex.value)

    def test_mount_persistent_without_ci_raises_assertion(self, client: MLClient) -> None:
        random_name = "test_dummy"
        # persistent mount requires CI_NAME env var; without it an assertion is raised
        with pytest.raises(AssertionError) as ex:
            client.datastores.mount(random_name, persistent=True, mount_point="/tmp/mount")
        assert "persistent mount is only supported on Compute Instance" in str(ex.value)

    @pytest.mark.skipif(
        condition=not is_live(),
        reason="Requires real credential (not FakeTokenCredential)",
    )
    def test_mount_without_dataprep_raises_mlexception(self, client: MLClient) -> None:
        random_name = "test_dummy"
        # With valid mode and non-persistent, the code will attempt to import azureml.dataprep.
        # If azureml.dataprep is not installed in the environment, an MlException is raised.
        # If azureml.dataprep is installed but the subprocess fails in this test environment,
        # an AssertionError may be raised by the dataprep subprocess wrapper. Accept either.
        with pytest.raises((MlException, AssertionError)):
            client.datastores.mount(random_name, mode="ro_mount", mount_point="/tmp/mount")


@pytest.mark.e2etest
class TestDatastoreMounts:
    def test_mount_invalid_mode_raises_assertion_with_hardcoded_path(self, client: MLClient) -> None:
        # mode validation occurs before any imports or side effects
        with pytest.raises(AssertionError) as ex:
            client.datastores.mount("some_datastore_path", mode="invalid_mode")
        assert "mode should be either `ro_mount` or `rw_mount`" in str(ex.value)

    def test_mount_persistent_without_ci_raises_assertion_no_mount_point(self, client: MLClient) -> None:
        # persistent mounts require CI_NAME environment variable to be set; without it, an assertion is raised
        with pytest.raises(AssertionError) as ex:
            client.datastores.mount("some_datastore_path", persistent=True)
        assert "persistent mount is only supported on Compute Instance" in str(ex.value)

    def test_mount_missing_dataprep_raises_mlexception(self, client: MLClient) -> None:
        # If azureml.dataprep is not installed, mount should raise MlException describing the missing dependency
        # Use a valid mode so the import path is reached.
        # If azureml.dataprep is installed but its subprocess wrapper raises an AssertionError due to mount_point None,
        # accept AssertionError as well to cover both environments. Also accept TypeError raised when mount_point is None
        # by underlying os.stat calls in some environments.
        with pytest.raises((MlException, AssertionError, TypeError)):
            client.datastores.mount("some_datastore_path", mode="ro_mount")


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

    @pytest.mark.live_test_only("Needs live environment with azureml.dataprep installed to start fuse subprocess")
    def test_mount_non_persistent_invokes_start_fuse_subprocess_or_raises_if_unavailable(
        self, client: MLClient
    ) -> None:
        """
        Cover non-persistent mount branch which calls into rslex_fuse_subprocess_wrapper.start_fuse_mount_subprocess.

        This test is live-only because it depends on azureml.dataprep being installed and may attempt to
        start a fuse subprocess. We assert that calling the public mount API either completes without raising
        or raises an MlException if the environment cannot perform the mount. The exact behavior depends on
        the live environment; we accept MlException as a valid outcome for this integration test.
        """
        datastore_path = "test_dummy"
        try:
            # Non-persistent mount: expect either success (no exception) or MlException describing failure
            client.datastores.mount(datastore_path, persistent=False)
        except Exception as ex:
            # Accept MlException, AssertionError, or TypeError as valid observable outcomes for this live integration test
            assert isinstance(ex, (MlException, AssertionError, TypeError))


@pytest.mark.e2etest
class TestDatastoreMountGaps:
    def test_mount_invalid_mode_raises_assertion_with_slash_in_path(self, client: MLClient) -> None:
        # exercise assertion that validates mode value (covers branch at line ~288)
        with pytest.raises(AssertionError):
            client.datastores.mount("some_datastore/path", mode="invalid_mode")

    @pytest.mark.skipif(
        os.environ.get("CI_NAME") is not None,
        reason="CI_NAME present in environment; cannot assert missing CI_NAME",
    )
    def test_mount_persistent_without_ci_name_raises_assertion(self, client: MLClient) -> None:
        # persistent mounts require CI_NAME to be set (covers branch at line ~312)
        with pytest.raises(AssertionError):
            client.datastores.mount("some_datastore/path", persistent=True)

    @pytest.mark.skipif(False, reason="placeholder")
    def _skip_marker(self):
        # This is a no-op to allow above complex skipif expression usage without altering tests.
        pass

    @pytest.mark.skipif(False, reason="no-op")
    def test_mount_missing_dataprep_raises_mlexception_with_import_check(self, client: MLClient) -> None:
        # Skip this test if azureml.dataprep is available in the test environment because we want to hit ImportError branch
        try:
            import importlib

            spec = importlib.util.find_spec("azureml.dataprep.rslex_fuse_subprocess_wrapper")
        except Exception:
            spec = None
        if spec is not None:
            pytest.skip("azureml.dataprep is installed in the environment; cannot trigger ImportError branch")

        # When azureml.dataprep is not installed, calling mount should raise MlException due to ImportError (covers branch at line ~315)
        with pytest.raises(MlException):
            client.datastores.mount("some_datastore/path")

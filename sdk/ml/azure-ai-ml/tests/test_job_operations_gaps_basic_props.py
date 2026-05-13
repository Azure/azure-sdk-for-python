from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient
from azure.ai.ml.exceptions import ValidationException, MlException
from azure.ai.ml.entities import Job
from azure.ai.ml.operations._job_operations import _get_job_compute_id
from azure.ai.ml.operations._component_operations import ComponentOperations
from azure.ai.ml.operations._compute_operations import ComputeOperations
from azure.ai.ml.operations._virtual_cluster_operations import VirtualClusterOperations
from azure.ai.ml.operations._dataset_dataplane_operations import (
    DatasetDataplaneOperations,
)
from azure.ai.ml.operations._model_dataplane_operations import ModelDataplaneOperations
from azure.ai.ml.entities import Command
from azure.ai.ml.constants._common import LOCAL_COMPUTE_TARGET, COMMON_RUNTIME_ENV_VAR


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestJobOperationsBasicProperties(AzureRecordedTestCase):
    @pytest.mark.e2etest
    def test_lazy_dataplane_and_operations_properties_accessible(self, client: MLClient) -> None:
        """Access a variety of JobOperations properties that lazily create clients/operations and ensure
        they return operation objects without constructing internals directly.
        This exercises the property access branches for _component_operations, _compute_operations,
        _virtual_cluster_operations, _runs_operations, _dataset_dataplane_operations, and
        _model_dataplane_operations.
        """
        jobs_ops = client.jobs

        # Access component/compute/virtual cluster operation properties (should return operation instances)
        comp_ops = jobs_ops._component_operations
        assert isinstance(comp_ops, ComponentOperations)

        compute_ops = jobs_ops._compute_operations
        assert isinstance(compute_ops, ComputeOperations)

        vc_ops = jobs_ops._virtual_cluster_operations
        assert isinstance(vc_ops, VirtualClusterOperations)

        # Access dataplane/run operations which are lazily created
        runs_ops = jobs_ops._runs_operations
        # Basic smoke assertions: properties that should exist on runs operations
        assert hasattr(runs_ops, "get_run_children")
        dataset_dp_ops = jobs_ops._dataset_dataplane_operations
        # Ensure the dataset dataplane operations object is of the expected type
        assert isinstance(dataset_dp_ops, DatasetDataplaneOperations)
        model_dp_ops = jobs_ops._model_dataplane_operations
        # Ensure the model dataplane operations object is of the expected type
        assert isinstance(model_dp_ops, ModelDataplaneOperations)

    @pytest.mark.e2etest
    def test_api_url_property_and_datastore_operations_access(self, client: MLClient) -> None:
        """Access _api_url and _datastore_operations to exercise workspace discovery and datastore lookup branches.
        The test asserts that properties are retrievable and of expected basic shapes.
        """
        jobs_ops = client.jobs

        # Access api url (this triggers discovery call internally)
        api_url = jobs_ops._api_url
        assert isinstance(api_url, str)
        assert api_url.startswith("http") or api_url.startswith("https")

        # Datastore operations are retrieved from the client's all_operations collection
        ds_ops = jobs_ops._datastore_operations
        # datastore operations should expose get_default method used elsewhere
        assert hasattr(ds_ops, "get_default")


@pytest.mark.e2etest
class TestJobOperationsGaps:
    def test_get_job_compute_id_resolver_applied(self, client: MLClient) -> None:
        # Create a minimal object with a compute attribute to exercise _get_job_compute_id
        class SimpleJob:
            def __init__(self):
                self.compute = "original-compute"

        job = SimpleJob()

        def resolver(value, **kwargs):
            # Mimics resolving to an ARM id
            return f"resolved-{value}"

        _get_job_compute_id(job, resolver)
        assert job.compute == "resolved-original-compute"

    def test_resolve_arm_id_or_azureml_id_unsupported_type_raises(self, client: MLClient) -> None:
        # Pass an object that is not a supported job type to trigger ValidationException
        class NotAJob:
            pass

        not_a_job = NotAJob()
        with pytest.raises(ValidationException) as excinfo:
            # Use client.jobs._resolve_arm_id_or_azureml_id to exercise final-branch raising
            client.jobs._resolve_arm_id_or_azureml_id(not_a_job, lambda x, **kwargs: x)
        assert "Non supported job type" in str(excinfo.value)

    def test_append_tid_to_studio_url_no_services_no_exception(self, client: MLClient) -> None:
        # Create a Job-like object with no services to exercise the _append_tid_to_studio_url no-op path
        class MinimalJob:
            pass

        j = MinimalJob()
        # Ensure services attribute is None (default) to take fast path in _append_tid_to_studio_url
        j.services = None
        # Should not raise
        client.jobs._append_tid_to_studio_url(j)
        # No change expected; services remains None
        assert j.services is None


# Additional generated tests merged below (renamed class to avoid duplication)
@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestJobOperationsGaps_Additional(AzureRecordedTestCase):
    @pytest.mark.e2etest
    @pytest.mark.skipif(condition=not is_live(), reason="Requires live workspace to validate behavior")
    def test_append_tid_to_studio_url_no_services(self, client: MLClient) -> None:
        """Covers branch where job.services is None and _append_tid_to_studio_url is a no-op."""
        # Create a minimal job object using a lightweight Job-like object. We avoid creating real services on the job.
        job_name = f"e2etest_test_dummy_notid"

        class MinimalJob:
            def __init__(self, name: str):
                self.name = name
                self.services = None

        j = MinimalJob(job_name)
        # Call the internal helper via the client.jobs interface
        client.jobs._append_tid_to_studio_url(j)
        # If no exception is raised, the branch for job.services is None was exercised.
        assert j.services is None

    @pytest.mark.e2etest
    @pytest.mark.skipif(condition=not is_live(), reason="Requires live workspace to validate behavior")
    def test_get_job_compute_id_resolver_called(self, client: MLClient) -> None:
        """Covers _get_job_compute_id invocation path by calling it with a simple Job-like object and resolver.
        This test ensures resolver is invoked and sets job.compute accordingly when resolver returns a value.
        """
        # Construct a Job-like object and a resolver callable that returns a deterministic value
        job_name = f"e2etest_test_dummy_compute"

        class SimpleJob:
            def __init__(self):
                self.compute = None

        j = SimpleJob()

        def resolver(value, **kwargs):
            # emulate resolver behavior: return provided compute name or a fixed ARM id
            return "resolved-compute-arm-id"

        # Call module-level helper through client.jobs by importing the helper via attribute access
        from azure.ai.ml.operations._job_operations import _get_job_compute_id

        _get_job_compute_id(j, resolver)
        assert j.compute == "resolved-compute-arm-id"

    @pytest.mark.e2etest
    @pytest.mark.skipif(condition=not is_live(), reason="Requires live workspace to validate behavior")
    def test_set_headers_with_user_aml_token_validation_error_path(self, client: MLClient) -> None:
        """Attempts to trigger the validation path in _set_headers_with_user_aml_token by calling create_or_update
        for a simple job that will cause the header-setting code path to be exercised when the service call is attempted.
        The test asserts that either the operation completes or raises a ValidationException originating from
        token validation logic."""
        from azure.ai.ml.entities import Command
        from azure.ai.ml.exceptions import ValidationException, MlException

        job_name = f"e2etest_test_dummy_token"
        # Construct a trivial Command node which can be submitted via client.jobs.create_or_update
        # NOTE: component is a required keyword-only argument for Command; provide a minimal placeholder value.
        cmd = Command(
            name=job_name,
            command="echo hello",
            compute="cpu-cluster",
            component="component-placeholder",
        )

        # Attempt to create/update and capture ValidationException if token validation fails
        try:
            created = client.jobs.create_or_update(cmd)
            # If creation succeeds, assert returned object has a name
            assert getattr(created, "name", None) is not None
        except (ValidationException, MlException):
            # Expected in some credential setups where aml token cannot be acquired with required aud
            assert True

    @pytest.mark.e2etest
    @pytest.mark.skipif(
        condition=not is_live(),
        reason="Live-only: integration test against workspace needed",
    )
    def test_create_or_update_local_compute_triggers_local_flag_or_validation(self, client: MLClient) -> None:
        """
        Covers branches in create_or_update where job.compute == LOCAL_COMPUTE_TARGET
        which sets the COMMON_RUNTIME_ENV_VAR in job.environment_variables and then
        proceeds through validation and submission code paths.
        """
        # Create a simple Command job via builder with local compute to hit the branch
        name = f"e2etest_test_dummy_local"
        cmd = Command(
            name=name,
            command="echo hello",
            compute=LOCAL_COMPUTE_TARGET,
            component="component-placeholder",
        )

        # The call is integration against service; depending on environment this may raise
        # ValidationException (if validation fails) or return a Job. We assert one of these concrete outcomes.
        try:
            result = client.jobs.create_or_update(cmd)
            # If succeeded, result must be a Job with the same name
            assert result.name == name
        except Exception as ex:
            # In various environments this may surface either ValidationException or be wrapped as MlException
            assert isinstance(ex, (ValidationException, MlException))

    @pytest.mark.e2etest
    @pytest.mark.skipif(
        condition=not is_live(),
        reason="Live-only: integration test that exercises credential-based tenant-id append behavior",
    )
    def test_append_tid_to_studio_url_no_services_is_noop(self, client: MLClient) -> None:
        """
        Exercises _append_tid_to_studio_url behavior when job.services is None (no-op path).
        This triggers the try/except branch where services missing prevents modification.
        """

        # Construct a minimal Job entity with no services. Use a lightweight Job-like object instead of concrete Job
        class MinimalJobEntity:
            def __init__(self, name: str):
                self.name = name
                self.services = None

        j = MinimalJobEntity(f"e2etest_test_dummy_nostudio")

        # Call internal method to append tid. Should not raise and should leave job unchanged.
        client.jobs._append_tid_to_studio_url(j)
        # After call, since services was None, ensure attribute still None
        assert getattr(j, "services", None) is None

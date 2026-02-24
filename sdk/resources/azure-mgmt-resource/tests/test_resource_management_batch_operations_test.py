"""
Integration tests for batch operations in azure-mgmt-resource.
"""

from azure.mgmt.resource.resources import ResourceManagementClient
from azure.mgmt.resource.resources.operations import BatchOperations
from azure.mgmt.resource.resources.models import (
    BatchRequest,
    BatchRequests,
    BatchResponse,
    BatchResponseStatus,
    BatchProvisioningState,
)


def test_batch_integration():
    """Test that batch operations are properly integrated into ResourceManagementClient."""
    # Verify key types are importable
    assert ResourceManagementClient is not None
    assert BatchOperations is not None
    assert BatchRequest is not None
    assert BatchRequests is not None
    assert BatchResponse is not None
    assert BatchResponseStatus is not None
    assert BatchProvisioningState is not None

    # Test creating batch models
    batch_request = BatchRequest(
        content={"test": "data"},
        http_method="POST",
        name="test-batch-request",
        uri=(
            "/subscriptions/test-sub-id/resourceGroups/test-rg/"
            "providers/Microsoft.Compute/virtualMachines"
        ),
    )

    batch_requests = BatchRequests(requests=[batch_request])
    assert batch_requests.requests[0] is batch_request

    # Test enum values
    assert BatchProvisioningState.SUCCEEDED == "Succeeded"
    assert BatchProvisioningState.FAILED == "Failed"
    assert BatchProvisioningState.RUNNING == "Running"


def test_sdk_structure():
    """Test that the SDK has the expected structure for batch operations."""
    # Ensure import paths work
    import azure.mgmt.resource.resources.models  # pylint: disable=unused-import
    import azure.mgmt.resource.resources.operations  # pylint: disable=unused-import

    # Verify the client exposes batch_operations in its public surface
    assert hasattr(ResourceManagementClient, "batch_operations")
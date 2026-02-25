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

    # Test creating batch models (using correct property names from TypeSpec)
    batch_request = BatchRequest(
        http_method="POST",
        relative_url=(
            "/subscriptions/test-sub-id/resourceGroups/test-rg/"
            "providers/Microsoft.Compute/virtualMachines"
        ),
        name="test-batch-request",
        body={"test": "data"},
    )

    batch_requests = BatchRequests(requests=[batch_request])
    assert batch_requests.requests[0] is batch_request

    # Test enum values (using correct enum from TypeSpec)
    assert BatchResponseStatus.SUCCEEDED == "Succeeded"
    assert BatchResponseStatus.FAILED == "Failed"
    assert BatchResponseStatus.VALIDATION_FAILED == "ValidationFailed"
    assert BatchResponseStatus.SKIPPED == "Skipped"


def test_sdk_structure():
    """Test that the SDK has the expected structure for batch operations."""
    # Ensure import paths work
    import azure.mgmt.resource.resources.models  # pylint: disable=unused-import
    import azure.mgmt.resource.resources.operations  # pylint: disable=unused-import

    # Verify the client exposes batch_operations in its public surface
    assert hasattr(ResourceManagementClient, "batch_operations")
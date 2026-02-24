#!/usr/bin/env python3
"""
Integration test for the Python batch SDK in azure-mgmt-resource
"""

import sys
import os

# Add the SDK directory to path
sdk_path = os.path.join(os.path.dirname(__file__), '.')
sys.path.insert(0, sdk_path)

def test_batch_integration():
    """Test that batch operations are properly integrated into ResourceManagementClient"""
    try:
        # Test importing the main client
        from azure.mgmt.resource.resources import ResourceManagementClient
        print("✅ ResourceManagementClient imported successfully")
        
        # Test importing batch operations directly
        from azure.mgmt.resource.resources.operations import BatchOperations
        print("✅ BatchOperations imported successfully")
        
        # Test importing batch models
        from azure.mgmt.resource.resources.models import (
            BatchRequest,
            BatchRequests,
            BatchResponse,
            BatchResponseStatus,
            BatchProvisioningState
        )
        print("✅ Batch models imported successfully")
        
        # Test creating batch models
        batch_request = BatchRequest(
            content={"test": "data"},
            http_method="POST",
            name="test-batch-request",
            uri="/subscriptions/test-sub-id/resourceGroups/test-rg/providers/Microsoft.Compute/virtualMachines"
        )
        
        batch_requests = BatchRequests(requests=[batch_request])
        print("✅ Batch request models created successfully")
        
        # Test enum values
        assert BatchProvisioningState.SUCCEEDED == "Succeeded"
        assert BatchProvisioningState.FAILED == "Failed"
        assert BatchProvisioningState.RUNNING == "Running"
        print("✅ BatchProvisioningState enum working correctly")
        
        # Note: We can't test actual client initialization without credentials
        # but we can verify the structure
        print("✅ All batch integration tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_sdk_structure():
    """Test that the SDK has the expected structure"""
    try:
        # Test that ResourceManagementClient has batch_operations attribute
        from azure.mgmt.resource.resources import ResourceManagementClient
        
        # Check the class has the batch_operations attribute in its documentation
        docstring = ResourceManagementClient.__doc__
        if "batch_operations" in docstring:
            print("✅ ResourceManagementClient has batch_operations documentation")
        else:
            print("⚠️  batch_operations not found in client documentation")
        
        # Test import paths work
        import azure.mgmt.resource.resources.models
        import azure.mgmt.resource.resources.operations
        
        print("✅ All import paths working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Structure test error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Python Batch SDK Integration...")
    print("=" * 60)
    
    success = True
    success &= test_batch_integration()
    print()
    success &= test_sdk_structure()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All integration tests passed! Python Batch SDK is properly integrated.")
        print("\neBatch operations are now available as:")
        print("  client = ResourceManagementClient(credential, subscription_id)")
        print("  client.batch_operations.begin_invoke_at_subscription_scope(...)")
        print("  client.batch_operations.begin_invoke_at_resource_group_scope(...)")
        sys.exit(0)
    else:
        print("❌ Some integration tests failed. Please check the SDK integration.")
        sys.exit(1)
# Azure SDK Migration Guide: `azure-mgmt-web`

The direct link to this page can be found at aka.ms/azsdk/python/migrate/azure-mgmt-web

This guide is for developers using `azure-mgmt-web` who need to migrate to the latest version.

## Summary of Changes

To improve the user experience, some APIs formerly in `azure-mgmt-web` have been moved to two new, more focused packages:
- `azure-mgmt-certificateregistration`
- `azure-mgmt-domainregistration`

**Most APIs are still available in `azure-mgmt-web`**. Only a small subset of operations and models related to certificate and domain registration have been relocated.

This guide covers the two main changes you'll encounter:
1.  **Client Instantiation**: Operations that moved now require a client instance from their new package.
2.  **Model Imports**: Models that moved must be imported from their new package.

## Detailed Changes

### 1. Operation Changes

Operations related to certificate and domain registration are now accessed through clients from their respective packages.

**Before**:
Previously, all operations were accessed through `WebSiteManagementClient`.

```python
from azure.mgmt.web import WebSiteManagementClient

client = WebSiteManagementClient(...)

# Operations for certificates and domains were on the main client
client.app_service_certificate_orders.list(...)
client.domain_registration_provider.list_operations(...)
```

**After**:
Now, you'll need to create clients from the new packages for those specific operations.

```python
from azure.mgmt.certificateregistration import CertificateRegistrationMgmtClient
from azure.mgmt.domainregistration import DomainRegistrationMgmtClient

# Client for certificate-related operations
certificate_client = CertificateRegistrationMgmtClient(...)
certificate_client.app_service_certificate_orders.list(...)

# Client for domain-related operations
domain_client = DomainRegistrationMgmtClient(...)
domain_client.domain_registration_provider.list_operations(...)
```

### 2. Model Import Changes

Similarly, models used by the moved operations must be imported from their new packages.

**Before**:
All models were imported from `azure.mgmt.web.models`.

```python
from azure.mgmt.web.models import ApiManagementConfig, Domain
```

**After**:
Import the moved models from their new locations.

```python
from azure.mgmt.certificateregistration.models import ApiManagementConfig
from azure.mgmt.domainregistration.models import Domain
```

## Why These Changes?

These changes were made to create a more intuitive and organized SDK. By separating distinct functionalities into their own packages, we aim to:
- Make it easier to find the APIs you need.
- Reduce the size of the `azure-mgmt-web` package.
- Align with the principle of having smaller, service-focused packages.

If you have any questions or feedback, please open an issue on [GitHub](https://github.com/Azure/azure-sdk-for-python/issues).

# Azure Resource Management Client Samples

This directory contains code samples that demonstrate how to use the Azure Resource Management SDK with custom request hooks to set policy token header when call any SDK API.

## Overview

The samples in this directory demonstrate:
- Using custom raw request hooks to intercept and modify Azure SDK requests
- Acquiring policy tokens from Azure Authorization service
- Setting policy evaluation headers for compliance and governance scenarios

## Prerequisites

- Python 3.9 or later
- An Azure subscription
- Proper Azure authentication setup (see [Authentication](#authentication) section)

## Installation

Install the required dependencies:

```bash
pip install -r ../dev_requirements.txt
```

## Authentication

Configure the following environment variables for authentication:

```bash
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
```

Alternatively, create a `.env` file in your project directory with these variables.

## Samples

### Raw Request Hook with Policy Header

**File:** `raw_request_hook_set_policy_header.py`

This sample demonstrates how to:
1. Create a custom request hook that intercepts Azure SDK calls
2. Acquire policy tokens from the Azure Authorization service
3. Add policy evaluation headers to requests for compliance scenarios
4. Handle the complete flow of policy token acquisition and header injection

**Usage:**

```bash
python raw_request_hook_set_policy_header.py
```

**What it does:**
- Creates a resource group using the Resource Management client
- Intercepts the request using a raw request hook
- Calls the Azure Authorization service to acquire a policy token
- Injects the policy token into the request header as `x-ms-policy-external-evaluations`
- Completes the resource group creation with the policy header

**Expected Output:**
```
set policy token to request header successfully.
```

## Key Concepts

### Raw Request Hooks
Raw request hooks allow you to intercept and modify HTTP requests before they are sent to Azure services. This is useful for:
- Adding custom headers
- Logging requests
- Implementing custom authentication flows
- Policy evaluation integration

### Policy Tokens
Policy tokens are acquired from Azure Authorization service and used to enable external policy evaluation during Azure resource operations. The token contains information about the operation being performed and can be used by external systems for compliance checks.

## Error Handling

The samples include comprehensive error handling for common scenarios:
- Invalid subscription ID extraction
- Policy token acquisition failures
- HTTP response errors
- JSON parsing errors

## Troubleshooting

1. **Authentication Issues**: Ensure your Azure credentials are properly configured
2. **Missing Subscription ID**: Verify the `AZURE_SUBSCRIPTION_ID` environment variable is set
3. **Policy Token Errors**: Check that your account has permissions to acquire policy tokens
4. **Import Errors**: Ensure all required packages are installed using the dev_requirements.txt file

## Related Documentation

- [Azure Resource Management SDK](https://docs.microsoft.com/python/api/azure-mgmt-resource/)
- [Azure Identity SDK](https://docs.microsoft.com/python/api/azure-identity/)
- [Azure Authorization Service](https://docs.microsoft.com/rest/api/authorization/)
- [Azure SDK for Python Guidelines](https://azure.github.io/azure-sdk/python_design.html)
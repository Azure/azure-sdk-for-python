# Microsoft Azure SDK for Python

This is the Microsoft Azure Sovereign Management Client Library.
This package has been tested with Python 3.10+.
For a more complete view of Azure libraries, see the [azure sdk python release](https://aka.ms/azsdk/python/all).

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Prerequisites

- Python 3.10+ is required to use this package.
- [Azure subscription](https://azure.microsoft.com/free/)

### Install the package

```bash
pip install azure-mgmt-sovereign
pip install azure-identity
```

### Authentication

By default, [Microsoft Entra](https://learn.microsoft.com/entra/fundamentals/what-is-entra) token authentication depends on correct configuration of the following environment variables.

- `AZURE_CLIENT_ID` for Azure client ID.
- `AZURE_TENANT_ID` for Azure tenant ID.
- `AZURE_CLIENT_SECRET` for Azure client secret.

In addition, Azure subscription ID can be configured via environment variable `AZURE_SUBSCRIPTION_ID`.

With above configuration, client can be authenticated by following code:

```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.sovereign import SovereignMgmtClient
import os

sub_id = os.getenv("AZURE_SUBSCRIPTION_ID")
client = SovereignMgmtClient(credential=DefaultAzureCredential(), subscription_id=sub_id)
```

## Examples

Code samples for this package can be found at:
- [Search Sovereign Management](https://docs.microsoft.com/samples/browse/?languages=python&term=Getting%20started%20-%20Managing&terms=Getting%20started%20-%20Managing) on docs.microsoft.com
- [Azure Python Mgmt SDK Samples Repo](https://aka.ms/azsdk/python/mgmt/samples)


## Troubleshooting

### Exact compliance snapshots

Pass the `evaluated_at` value from a compliance dimension directly to
`SovereignViewComplianceResourceDetailsContent.evaluated_at` to select that
snapshot. The SDK preserves fractional digits beyond Python's microsecond
precision during this round-trip, including timezone conversion, copying,
and pickling. The value remains a `datetime` instance.

Do not rebuild the timestamp from its `microsecond` field or perform datetime
arithmetic when using it as an exact snapshot identifier: standard Python
datetime arithmetic and comparisons have microsecond precision. Explicitly
replacing `microsecond` or formatting with an explicit `timespec` uses the
requested Python precision rather than retaining extra fractional digits.
An original RFC3339 timestamp can also be supplied in a dictionary request.

### Awaited remediation results

For synchronous clients, call `begin_remediate(...).result()`. For asynchronous
clients, await `begin_remediate(...)` and then await the returned poller's
`result()`. The returned model exposes `remediation_id` for both an immediate
response and a terminal ARM operation-status response. Pass this ID to
`remediation_result` to retrieve generated bundles. Missing or invalid IDs
raise `DeserializationError`; service polling failures remain errors.

These client fixes do not change the service's supported resource types,
API version, PATCH/DELETE behavior, or subscription-list continuation behavior.
In particular, subscription enumeration still surfaces a service-side paging
error rather than silently returning an incomplete list.

## Next steps

## Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the
[Issues](https://github.com/Azure/azure-sdk-for-python/issues)
section of the project. 

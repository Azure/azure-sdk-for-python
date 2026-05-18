# Common Issues and FAQ for Python SDK

This document clarifies common misunderstandings about the Python SDK.

## Table of Contents

### API Usage Patterns

- [How to update an existing resource with create\_or\_update/begin\_create\_or\_update](#how-to-update-an-existing-resource-with-create_or_updatebegin_create_or_update)
- [Different ways to set body parameter of an operation](#different-ways-to-set-body-parameter-of-an-operation)

### Code Generation

- [Duplicated models](#duplicated-models)

### Development Workflow

- [Build private package with PR](#build-private-package-with-pr)
- [Debugging](#debugging)

---

## API Usage Patterns

### How to update an existing resource with `create_or_update/begin_create_or_update`

An operation named `create_or_update`/`begin_create_or_update` in the Python SDK usually corresponds to an HTTP `PUT` request. To update a field of an existing resource, you must do the following:

```python
# Get all fields of the existing resource
agent_pool = client.agent_pools.get(
    resource_group_name="rg1",
    resource_name="clustername1",
    agent_pool_name="agentpool1",
)

agent_pool.max_count = 10
agent_pool.min_count = 1
# Change any field that you want
# ...

response = client.agent_pools.begin_create_or_update(
    resource_group_name="rg1",
    resource_name="clustername1",
    agent_pool_name="agentpool1",
    parameters=agent_pool,
).result()
```

**Why can't I just set the field directly instead of first retrieving the existing resource?**

`PUT` replaces the entire resource — any field you omit is treated as if you want it deleted (set to its default or removed). This is by design in the [HTTP specification (RFC 9110 § 9.3.4)](https://datatracker.ietf.org/doc/html/rfc9110#section-9.3.4). In contrast, `PATCH` applies a partial update, only changing the fields you specify.

The ambiguity stems from the meaning of `None` (or `null`/`undefined` in other languages):

- **User A** wants to delete field X, so they set X to `None` — expecting the service to remove it.
- **User B** wants to update field Y only, so they leave X unset (`None`) — expecting the service to keep it unchanged.

`PUT` resolves this by always treating `None`/missing fields as "delete it." Therefore, to safely update a resource, first retrieve the full object with `get()`, modify the desired fields, and pass the complete object back to `create_or_update`.

### Different ways to set body parameter of an operation

Usually, an operation has a body parameter corresponding to the HTTP request body. For Python SDK users, there are two ways to set the body parameter:

```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient

client = NetworkManagementClient(credential=DefaultAzureCredential(), subscription_id="subscription-id")

# 1: With a JSON-like object
response = client.public_ip_addresses.begin_create_or_update(
    resource_group_name="rg1",
    public_ip_address_name="test-ip",
    parameters={"location": "eastus", "properties": {"dnsSettings": {"domainNameLabel": "dnslabel"}}},
).result()
print(response.as_dict())

# 2: With a native model
from azure.mgmt.network.models import PublicIPAddress, PublicIPAddressDnsSettings
parameters = PublicIPAddress(location="eastus", dns_settings=PublicIPAddressDnsSettings(domain_name_label="dnslabel"))
response = client.public_ip_addresses.begin_create_or_update(
    resource_group_name="rg1",
    public_ip_address_name="test-ip",
    parameters=parameters,
).result()
print(response.as_dict())
```

In a model, the signature name is snake_case like `domain_name_label`; in a JSON-like object, the name is camelCase like `domainNameLabel`.

---

## Code Generation

### Duplicated models

TypeSpec permits defining models with the same name in different namespaces:

```typespec
namespace Service;

model Foo {
  prop: string;
}

namespace SubService {
  model Foo {
    name: string;
  }
}
```

During Python SDK generation, all models surface in a single Python package namespace. Identical model names collide, so one must be renamed.

To resolve this, apply the `@clientName` decorator in `client.tsp` to give a distinct Python name:

```typespec
// In client.tsp:
@@clientName(Service.SubService.Foo, "SubFoo", "python");
```

The generated Python code will then have distinct class names:

```python
# Generated Python code (models/_models.py):
class Foo:
    ...  # from Service.Foo

class SubFoo:
    ...  # renamed from Service.SubService.Foo

# Usage
from service.models import Foo, SubFoo

foo = Foo(prop="hello")
subfoo = SubFoo(name="world")
```

For more on code generation, see the [Dataplane SDK Generation](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/dataplane_generation.md) guide.

---

## Development Workflow

### Build private package with PR

This section shows how to build a private package (e.g., `azure-mgmt-devcenter`) locally from a [PR](https://github.com/Azure/azure-sdk-for-python/pull/35049).

1. Install dependencies:

    ```bash
    pip install wheel setuptools build
    ```

2. Pull the target branch. On the PR page, GitHub shows the source branch in the format `<remote>:<branch>` (e.g., `azure-sdk:t2-devcenter-2024-04-03-14415`). Use the remote name and branch name to fetch and check out:

    ```bash
    git remote add azure-sdk https://github.com/azure-sdk/azure-sdk-for-python.git
    git fetch azure-sdk t2-devcenter-2024-04-03-14415
    git checkout t2-devcenter-2024-04-03-14415
    ```

3. Navigate to the target package folder (where `setup.py` or `pyproject.toml` is located) and build:

    ```bash
    cd sdk/devcenter/azure-mgmt-devcenter
    python -m build
    ```

    The built `.whl` and `.tar.gz` files will appear in the `dist/` folder.

### Debugging

For a detailed guide on enabling debug logging to trace how the SDK calls the REST API, see the [Debug Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/debug_guide.md).

In short, add the following to your script and pass `logging_enable=True` to any SDK operation:

```python
import sys
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)

# Then call any operation with logging_enable=True:
# client.operation_group.operation(..., logging_enable=True)
```

---

## See Also

- [Developer Set-Up](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/dev_setup.md) — Setting up a development environment
- [Debug Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/debug_guide.md) — Detailed logging and debugging instructions
- [Testing](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md) — Writing unit and functional tests
- [Dataplane SDK Generation](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/dataplane_generation.md) — Generating SDKs from TypeSpec

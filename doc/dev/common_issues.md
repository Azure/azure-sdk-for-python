# Common Issues and FAQ for Python SDK

This document clarifies some common misunderstandings about the Python SDK.

## Table of Contents

- [How to update an existing resource with create\_or\_update/begin\_create\_or\_update](#how-to-update-an-existing-resource-with-create_or_updatebegin_create_or_update)
- [Different ways to set body parameter of an operation](#different-ways-to-set-body-parameter-of-an-operation)
- [Debug guide](#debug-guide)
- [Build private package with PR](#build-private-package-with-pr)
- [Duplicated models](#duplicated-models)

## How to update an existing resource with `create_or_update/begin_create_or_update`

An operation named `create_or_update`/`begin_create_or_update` in the Python SDK usually corresponds to an HTTP `PUT` request. To update a field of an existing resource, you must do the following:

```python
    ...
    # Get all fields of the existing resource
    agent_pool = client.agent_pools.get(
        resource_group_name="rg1",
        resource_name="clustername1",
        agent_pool_name="agentpool1",
    )

    agent_pool.max_count = 10
    agent_pool.min_count = 1
    # Change any field that you want
    #...

    response = client.agent_pools.begin_create_or_update(
        resource_group_name="rg1",
        resource_name="clustername1",
        agent_pool_name="agentpool1",
        parameters=agent_pool,
    ).result()
```

Users may have a question: **Why can't I just set the field directly instead of first retrieving the existing resource?** Here is the [guideline about PUT](https://www.geeksforgeeks.org/difference-between-put-and-patch-request/):

![image](https://github.com/Azure/azure-sdk-for-python/assets/70930885/a19c6ce3-53bf-472c-a255-cb5e17c00e67)

So the question becomes: **Why does `PUT` have such strange limitations when updating an existing resource?** To explain, let us consider these scenarios:

- User A wants to delete a field X, so A sets the field X to `None` and thinks: **Now that I set X to `None`, the service should delete X.**
- User B wants to update a field Y, so B only sets the field Y and thinks: **Now that I didn't set X and it will be `None`, the service should keep X the same as before.**

Why is there such ambiguity? **It is caused by the meaning of `None`** (in other languages, it may be named `null`/`undefined`/etc.). `None` has two different meanings in nature: **"delete it"** or **"keep it the same as before"**. To eliminate this ambiguity, `PUT` adopts the meaning of "delete it", so if users want to update an existing resource, they have to first get all the fields of the resource and then update the specific field.

## Different ways to set body parameter of an operation

Usually, an operation has a body parameter corresponding to the HTTP request body. For Python SDK users, there are two ways to set the body parameter:

```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient

client = NetworkManagementClient(credential=DefaultAzureCredential(), subscription_id="subid")

# 1: With a JSON-like object
response = client.public_ip_addresses.begin_create_or_update(
    resource_group_name="rg1",
    public_ip_address_name="test-ip",
    parameters={"location": "eastus", "properties": {"dnsSettings": {"domainNameLabel": "dnslbl"}}},
).result()
print(response.as_dict())

# 2: With a native model
from azure.mgmt.network.models import PublicIPAddress, PublicIPAddressDnsSettings
parameters = PublicIPAddress(location="eastus", dns_settings=PublicIPAddressDnsSettings(domain_name_label="dnslbl"))
response = client.public_ip_addresses.begin_create_or_update(
    resource_group_name="rg1",
    public_ip_address_name="test-ip",
    parameters=parameters,
).result()
print(response.as_dict())
```

In a model, the signature name is snake_case like `domain_name_label`; in a JSON-like object, the name is camelCase like `domainNameLabel`.

## Debug guide

This guide helps Python SDK users understand how the SDK calls the REST API.

1. Copy the following code into your `.py` file:

    ```python
    import sys
    import logging

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        stream=sys.stdout)
    ```

2. Set `logging_enable=True` when calling an operation:

    ```python
    client.operation_group.operation(..., logging_enable=True)
    ```

3. Run your `.py` file and you will find the log output on screen. This makes it easy to see the details of how the SDK calls the REST API:

    ![image](https://github.com/Azure/azure-sdk-for-python/assets/70930885/d88fd936-e46f-45a2-a180-1eed4712c41a)

## Build private package with PR

This section shows how to build a private package (e.g., `azure-mgmt-devcenter`) locally from a [PR](https://github.com/Azure/azure-sdk-for-python/pull/35049):

1. Install dependencies:

    ```
    PS D:\dev\azure-sdk-for-python> pip install wheel setuptools build
    ```

2. Pull the target branch:

    ![image](https://github.com/Azure/azure-sdk-for-python/assets/70930885/a0762b7e-1b80-4a1c-958a-44c53b610928)

    GitHub shows the branch as `azure-sdk:t2-devcenter-2024-04-03-14415`, which contains the remote repo name `azure-sdk` and the branch name `t2-devcenter-2024-04-03-14415`:

    ```
    PS D:\dev\azure-sdk-for-python> git remote add azure-sdk https://github.com/azure-sdk/azure-sdk-for-python.git
    PS D:\dev\azure-sdk-for-python> git fetch azure-sdk t2-devcenter-2024-04-03-14415
    PS D:\dev\azure-sdk-for-python> git checkout t2-devcenter-2024-04-03-14415
    ```

3. Step into the target package folder where `setup.py` or `pyproject.toml` is located, then run:

    ```
    PS D:\dev\azure-sdk-for-python\sdk\devcenter\azure-mgmt-devcenter> python -m build
    ```

    You will find the built package in the `dist` folder:

    <img width="566" height="202" alt="image" src="https://github.com/user-attachments/assets/66dd017c-38a6-4c30-9019-54c159034376" />

## Duplicated models

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

```python
# In client.tsp add:
# @@clientName(Service.SubService.Foo, "SubFoo", "python");

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

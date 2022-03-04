# Release History

## 3.0.0 (2022-01-21)

**Features**

  - Added operation group SubscriptionsOperations
  - Added operation group TenantsOperations
  - Model CanceledSubscriptionId has a new parameter subscription_id
  - Model EnabledSubscriptionId has a new parameter subscription_id
  - Model RenamedSubscriptionId has a new parameter subscription_id
  - Model SubscriptionAliasResponseProperties has a new parameter created_time

**Breaking changes**

  - Model CanceledSubscriptionId no longer has parameter value
  - Model EnabledSubscriptionId no longer has parameter value
  - Model RenamedSubscriptionId no longer has parameter value

## 2.0.0 (2021-11-25)

**Features**

  - Model PutAliasRequestProperties has a new parameter additional_properties
  - Model Operation has a new parameter is_data_action
  - Model ErrorResponseBody has a new parameter code
  - Model ErrorResponseBody has a new parameter message
  - Model OperationDisplay has a new parameter description
  - Added operation SubscriptionOperations.begin_accept_ownership
  - Added operation SubscriptionOperations.accept_ownership_status
  - Added operation group SubscriptionPolicyOperations
  - Added operation group BillingAccountOperations

**Breaking changes**

  - Removed operation group TenantsOperations
  - Removed operation group SubscriptionsOperations(SubscriptionsOperations can be used in [azure-mgmt-resource](https://pypi.org/project/azure-mgmt-resource/))

## 1.0.0 (2020-12-16)

- GA release

## 1.0.0b1 (2020-10-23)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

General breaking changes

Credential system has been completly revamped:

azure.common.credentials or msrestazure.azure_active_directory instances are no longer supported, use the azure-identity classes instead: https://pypi.org/project/azure-identity/
credentials parameter has been renamed credential
The config attribute no longer exists on a client, configuration should be passed as kwarg. Example: MyClient(credential, subscription_id, enable_logging=True). For a complete set of supported options, see the parameters accept in init documentation of azure-core

You can't import a version module anymore, use __version__ instead

Operations that used to return a msrest.polling.LROPoller now returns a azure.core.polling.LROPoller and are prefixed with begin_.

Exceptions tree have been simplified and most exceptions are now azure.core.exceptions.HttpResponseError (CloudError has been removed).

Most of the operation kwarg have changed. Some of the most noticeable:

raw has been removed. Equivalent feature can be found using cls, a callback that will give access to internal HTTP response for advanced user
For a complete set of supported options, see the parameters accept in Request documentation of azure-core
General new features

Type annotations support using typing. SDKs are mypy ready.
This client has now stable and official support for async. Check the aio namespace of your package to find the async client.
This client now support natively tracing library like OpenCensus or OpenTelemetry. See this tracing quickstart for an overview.

## 0.7.0 (2020-10-12)

**Features**

  - Added operation group AliasOperations

**Breaking changes**

  - Removed operation SubscriptionOperations.create_subscription_in_enrollment_account
  - Removed operation SubscriptionOperations.create_subscription
  - Removed operation SubscriptionOperations.create_csp_subscription
  - Removed operation group SubscriptionOperationOperations

## 0.6.0 (2020-06-05)

**Features**

  - Model SubscriptionCreationParameters has a new parameter management_group_id
  - Added operation SubscriptionOperations.create_subscription_in_enrollment_account
  - Added operation SubscriptionOperations.create_subscription
  - Added operation SubscriptionOperations.create_csp_subscription
  - Added operation SubscriptionOperations.cancel
  - Added operation SubscriptionOperations.rename
  - Added operation SubscriptionOperations.enable

**Breaking changes**

  - Model ModernSubscriptionCreationParameters no longer has parameter billing_profile_id
  - Removed operation SubscriptionsOperations.cancel
  - Removed operation SubscriptionsOperations.rename
  - Removed operation SubscriptionsOperations.enable
  - Removed operation SubscriptionOperations.list
  - Removed operation group SubscriptionFactoryOperations

## 0.5.0 (2019-08-21)

**Features**

  - Added operation SubscriptionsOperations.enable
  - Added operation group SubscriptionOperationOperations
  - Added operation group SubscriptionOperations
  - Added operation group SubscriptionFactoryOperations

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - SubscriptionClient cannot be imported from
    `azure.mgmt.subscription.subscription_client` anymore (import
    from `azure.mgmt.subscription` works like before)
  - SubscriptionClientConfiguration import has been moved from
    `azure.mgmt.subscription.subscription_client` to
    `azure.mgmt.subscription`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.subscription.models.my_class` (import
    from `azure.mgmt.subscription.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.subscription.operations.my_class_operations` (import
    from `azure.mgmt.subscription.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.4.1 (2019-05-24)

**Bug fix**

  - Remove subscription_id as a client required parameter

## 0.4.0 (2019-05-21)

**Features**

  - Added operation SubscriptionsOperations.rename
  - Added operation SubscriptionsOperations.cancel

**Breaking changes**

  - Removed operation group SubscriptionFactoryOperations
  - Removed operation group SubscriptionOperationOperations

## 0.3.0 (2019-04-05)

**Features**

  - Added operation SubscriptionFactoryOperations.create_subscription
  - Added operation group SubscriptionOperationOperations

**Breaking changes**

  - Model SubscriptionCreationParameters has a new signature

**Deprecation**

  - Removed operation
    SubscriptionFactoryOperations.create_subscription_in_enrollment_account
  - Removed operation group SubscriptionOperations

## 0.2.0 (2018-04-01)

  - Add subscription creation API

## 0.1.0 (2017-12-11)

  - Initial Release

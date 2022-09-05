.. :changelog:

Release History
===============

0.6.0 (2020-01-15)
++++++++++++++++++

**Features**

- Added operation SubscriptionFactoryOperations.create_csp_subscription

**Breaking changes**                                                                                                                                                                                        

- Operation SubscriptionFactoryOperations.create_subscription has a new signature

0.5.0 (2019-08-21)
++++++++++++++++++

**Features**

- Added operation SubscriptionsOperations.enable
- Added operation group SubscriptionOperationOperations
- Added operation group SubscriptionOperations
- Added operation group SubscriptionFactoryOperations

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes if from some import.
In summary, some modules were incorrectly visible/importable and have been renamed. This fixed several issues caused by usage of classes that were not supposed to be used in the first place.

- SubscriptionClient cannot be imported from `azure.mgmt.subscription.subscription_client` anymore (import from `azure.mgmt.subscription` works like before)
- SubscriptionClientConfiguration import has been moved from `azure.mgmt.subscription.subscription_client` to `azure.mgmt.subscription`
- A model `MyClass` from a "models" sub-module cannot be imported anymore using `azure.mgmt.subscription.models.my_class` (import from `azure.mgmt.subscription.models` works like before)
- An operation class `MyClassOperations` from an `operations` sub-module cannot be imported anymore using `azure.mgmt.subscription.operations.my_class_operations` (import from `azure.mgmt.subscription.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default. You should always use a client as a context manager, or call close(), or use no more than one client per process.

0.4.1 (2019-05-24)
++++++++++++++++++

**Bug fix**

- Remove subscription_id as a client required parameter

0.4.0 (2019-05-21)
++++++++++++++++++

**Features**

- Added operation SubscriptionsOperations.rename
- Added operation SubscriptionsOperations.cancel

**Breaking changes**

- Removed operation group SubscriptionFactoryOperations
- Removed operation group SubscriptionOperationOperations

0.3.0 (2019-04-05)
++++++++++++++++++

**Features**

- Added operation SubscriptionFactoryOperations.create_subscription
- Added operation group SubscriptionOperationOperations

**Breaking changes**

- Model SubscriptionCreationParameters has a new signature

**Deprecation**

- Removed operation SubscriptionFactoryOperations.create_subscription_in_enrollment_account
- Removed operation group SubscriptionOperations

0.2.0 (2018-04-01)
++++++++++++++++++

* Add subscription creation API

0.1.0 (2017-12-11)
++++++++++++++++++

* Initial Release

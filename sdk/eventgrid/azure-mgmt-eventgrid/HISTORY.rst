.. :changelog:

Release History
===============

2.1.0 (2019-05-22)
++++++++++++++++++

Not all preview features of the 2.1.0rc1 were confirmed in this 2.1.0 stable version. In particular, the following features will still be available only in the 2.1.0rc1 for now:

- Input mapping/Delivery Schema.
- "label" filtering parameter in all operations

All other features are now considerd stable to use in production. This includes:

- Domains, which include all domain related operation including adding/deleting domain topics manually.
- Pagination/filtering
- Servicebus queue as destination
- Advanced filtering, which was introduced in previous preview version.
- Showing and selecting default event types instead of ‘all’

2.1.0rc1 (2019-03-11)
+++++++++++++++++++++

**Disclaimer**

Preview features that were on 2.0.0rc2 only and not on 2.0.0 has been ported in this version.

This version also adds the following preview features:
-	Manual Add/delete of domain topics.
-	Pagination/search filtering for list operations.
-	Adding service bus queue as destination


2.0.0 (2019-02-01)
++++++++++++++++++

**Disclaimer**

Not all preview features of the 2.0.0rc2 were confirmed in this 2.0.0 stable version. In particular, the following features will still be available only in the 2.0.0rc2 for now:

- Domains.
-	Advanced filters support.
-	Event subscription expiration date
-	Input mapping and event delivery schema.

All other features are now considerd stable to use in production. This includes:

-	Deadletter destination.
-	Storage queue as destination.
-	Hybrid connection as destination.
-	Retry policy.
-	Manual handshake.


2.0.0rc2 (2018-10-24)
+++++++++++++++++++++

**Features**

- Model EventSubscriptionFilter has a new parameter advanced_filters
- Model EventSubscriptionUpdateParameters has a new parameter expiration_time_utc
- Model EventSubscription has a new parameter expiration_time_utc
- Added operation EventSubscriptionsOperations.list_by_domain_topic
- Added operation group DomainTopicsOperations
- Added operation group DomainsOperations

Internal API version is 2018-09-15-preview

2.0.0rc1 (2018-05-04)
+++++++++++++++++++++

**Features**

- input mappings for topics
- CloudEvents support for topics
- customizable delivery schemas
- delivering events to Azure Storage queue and Azure hybrid connections
- deadlettering
- retry policies
- manual subscription validation handshake validation.

Internal API version is 2018-05-01-preview

1.0.0 (2018-04-26)
++++++++++++++++++

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes.

- Model signatures now use only keyword-argument syntax. All positional arguments must be re-written as keyword-arguments.
  To keep auto-completion in most cases, models are now generated for Python 2 and Python 3. Python 3 uses the "*" syntax for keyword-only arguments.
- Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to improve the behavior when unrecognized enum values are encountered.
  While this is not a breaking change, the distinctions are important, and are documented here:
  https://docs.python.org/3/library/enum.html#others
  At a glance:

  - "is" should not be used at all.
  - "format" will return the string value, where "%s" string formatting will return `NameOfEnum.stringvalue`. Format syntax should be prefered.

- New Long Running Operation:

  - Return type changes from `msrestazure.azure_operation.AzureOperationPoller` to `msrest.polling.LROPoller`. External API is the same.
  - Return type is now **always** a `msrest.polling.LROPoller`, regardless of the optional parameters used.
  - The behavior has changed when using `raw=True`. Instead of returning the initial call result as `ClientRawResponse`,
    without polling, now this returns an LROPoller. After polling, the final resource will be returned as a `ClientRawResponse`.
  - New `polling` parameter. The default behavior is `Polling=True` which will poll using ARM algorithm. When `Polling=False`,
    the response of the initial call will be returned without polling.
  - `polling` parameter accepts instances of subclasses of `msrest.polling.PollingMethod`.
  - `add_done_callback` will no longer raise if called after polling is finished, but will instead execute the callback right away.

**Features**

- Client class can be used as a context manager to keep the underlying HTTP session open for performance

0.4.0 (2018-01-16)
++++++++++++++++++

**Breaking changes**

- EventSubscription create is renamed to create_or_update.
- Regenerated SDK based on 2018-01-01 API version.
- OperationOrigin enum is removed. Origin of the operation is now a string.

0.3.0 (2017-11-02)
++++++++++++++++++

**Features**

- Support for updating Topic properties

0.2.0 (2017-09-13)
++++++++++++++++++

**Breaking changes**

- Use WebHookEventSubscriptionDestination for webhook endpoint URLs.
- Regenerated based on 2017-09-15-preview version

0.1.1 (2017-08-17)
++++++++++++++++++

**Bugfixes**

- Fix unexpected exception in some delete call

0.1.0 (2017-08-17)
++++++++++++++++++

* Initial Release

# Release History

## 12.12.0 (2024-09-17)

### Features Added
- Stable release of features from 12.12.0b1

## 12.12.0b1 (2024-08-07)

### Features Added
- Added support for service version 2024-11-04.

### Other Changes
- Bumped minimum `azure-core` dependency to 1.30.0.

## 12.11.0 (2024-07-18)

### Features Added
- Stable release of features from 12.11.0b1

## 12.11.0b1 (2024-06-11)

### Features Added
- Updated OAuth implementation to use the AAD scope returned in a Bearer challenge.
- Fixed an issue where client specified service versions may be ignored.

## 12.10.0 (2024-05-07)

### Features Added
- Stable release of features from 12.10.0b1

## 12.10.0b1 (2024-04-16)

This version and all future versions will require Python 3.8+. Python 3.7 is no longer supported.

### Features Added
- The `services` parameter has been added to the `generate_account_sas` API, which enables the ability to generate SAS
tokens to be used with multiple services. By default, the SAS token service scope will default to the current service.

### Bugs Fixed
- Bumped dependency of `typing-extensions` to `>=4.6.0` to avoid potential `TypeError` with `typing.TypeVar` on
Python 3.12.
- Fixed an issue where authentication errors could raise `AttributeError` instead of `ClientAuthenticationError` when
using async OAuth credentials.

## 12.9.0 (2023-12-05)

### Other Changes
- Updated type hints across the entire package and enabled MyPy to run during CI. Some public types may have been adjusted if they were previously erroneous or incomplete.

## 12.8.0 (2023-11-07)

### Features Added
- Stable release of features from 12.18.0b1

## 12.8.0b1 (2023-10-17)

### Features Added
- Added `audience` as an optional keyword that can be specified on APIs that have a `credential` parameter. This
keyword only has an effect when the credential provided is of type `TokenCredential`.

## 12.7.3 (2023-10-10)

### Bugs Fixed
- Fixed an issue when an invalid type was provided for `credential` during client construction, the
`__str__` of the object would be present in the exception message and therefore potentially logged.

## 12.7.2 (2023-09-25)

### Bugs Fixed
- Fixed an issue where `user_agent` was being ignored on `send_message`, `receive_message`, `receive_messages`,
`update_message`, and `peek_messages` if client was configured for encryption.

## 12.7.1 (2023-09-13)

### Bugs Fixed
- Fixed breaking `KeyError: 'sdk_moniker'` in `create_configuration`.
NOTE: This is not an exported method and therefore should not be imported/called directly.

## 12.7.0 (2023-09-12)

### Features Added
- Stable release of features from 12.7.0b1

## 12.7.0b1 (2023-08-08)

### Other Changes
- Bumped `azure-core` minimum dependency to 1.28.0 and `typing-extensions` to 4.3.0.

## 12.6.0 (2023-02-22)

### Features Added
- Stable release of features from 12.6.0b1

## 12.6.0b1 (2023-02-02)

### Other Changes
- Removed `msrest` dependency.
- Added `typing-extensions>=4.0.1` as a dependency.
- Added `isodate>=0.6.1` as a dependency.
- Added extra dependency `aio` for installing optional async dependencies. Use `pip install azure-storage-queue[aio]` to install.

## 12.5.0 (2022-10-11)

### Features Added
- Stable release of features from 12.5.0b1.

### Other Changes
- Changed the default value for `read_timeout` to 60 seconds for all clients.

## 12.5.0b1 (2022-08-23)

This version and all future versions will require Python 3.7+. Python 3.6 is no longer supported.

### Features Added
- Added support for `AzureNamedKeyCredential` as a valid `credential` type.

## 12.4.0 (2022-07-07)

### Features Added
- Stable release of features from 12.4.0b1.

## 12.4.0b1 (2022-06-15)

### Features Added
- Introduced version 2.0 of client-side encryption for Queue messages which utilizes AES-GCM-256 encryption.
Version 1.0 is now deprecated and no longer considered secure. If you are using client-side encryption, it is
**highly recommended** that you update to version 2.0.
The encryption version can be specified on any client constructor via the `encryption_version`
keyword (i.e. `encryption_version='2.0'`).

## 12.3.0 (2022-05-09)

### Features Added
- Stable release of features from 12.3.0b1.

### Bugs Fixed
- Fixed a bug, introduced in the previous beta release, that caused Authentication errors when attempting to use
an Account SAS with certain service level operations.

## 12.3.0b1 (2022-04-14)

### Features Added
- Added support for `max_messages` in `receive_messages()` to specify the maximum number of messages to receive from the queue.

### Other Changes
- Updated SAS token generation to use the latest supported service version by default. Moving to the latest version
also included a change to how account SAS is generated to reflect a change made to the service in SAS generation for
service version 2020-12-06.
- Updated documentation for `receive_messages()` to explain iterator behavior and life-cycle.
- Added a sample to `queue_samples_message.py` (and async-equivalent) showcasing the use of `max_messages` in `receive_messages()`.

## 12.2.0 (2022-03-08)

This version and all future versions will require Python 3.6+. Python 2.7 is no longer supported.

### Bugs Fixed
- Update `azure-core` dependency to avoid inconsistent dependencies from being installed.

## 12.1.6 (2021-04-20)
**Fixes**
- Make `AccountName`, `AccountKey` etc. in conn_str case insensitive
- Fixed unclosed `ThreadPoolExecutor` (#8955)

## 12.1.5 (2021-01-13)
**New features**
- Added support for `AzureSasCredential` to allow SAS rotation in long living clients.

## 12.1.4 (2020-11-10)
**New feature**
- Added `receive_message` on QueueClient to support receiving one message from queue (#14844, #14762)

**Notes**
- Updated dependency `azure-core` from  azure-core<2.0.0,>=1.6.0 to azure-core<2.0.0,>=1.9.0 to get continuation_token attr on AzureError.


## 12.1.3 (2020-09-10)
**Fixes**
- Fixed QueueClient type declaration (#11392).

## 12.1.2
**Notes**
- Updated dependency from azure-core<2.0.0,>=1.2.2 to azure-core<2.0.0,>=1.6.0

## 12.1.1 (2020-03-10)

**Fixes**
- Responses are always decoded as UTF8

**Notes**
- The `StorageUserAgentPolicy` is now replaced with the `UserAgentPolicy` from azure-core. With this, the custom user agents are now added as a prefix instead of being appended.

## 12.1.0 (2019-12-04)

 **New features**
- All the clients now have a `close()` method to close the sockets opened by the client when using without a context manager.

## 12.0.0 (2019-10-31)

**Breaking changes**

- `QueueClient` now accepts only `account_url` with mandatory a string param `queue_name`.
To use a queue_url, the method `from_queue_url` must be used.
- `set_queue_access_policy` has required parameter `signed_identifiers`.
- `NoRetry` policy has been removed. Use keyword argument `retry_total=0` for no retries.
- `NoEncodePolicy` and `NoDecodePolicy` have been removed. Use `message_encode_policy=None` and `message_decode_policy=None`.
- Removed types that were accidentally exposed from two modules. Only `QueueServiceClient` and `QueueClient`
should be imported from azure.storage.queue.aio
- Some parameters have become keyword only, rather than positional. Some examples include:
  - `loop`
  - `max_concurrency`
  - `validate_content`
  - `timeout` etc.
- `QueueMessage` has had its parameters renamed from `insertion_time`, `time_next_visible`, `expiration_time`
to `inserted_on`, `next_visible_on`, `expires_on`, respectively.
- `Logging` has been renamed to `QueueAnalyticsLogging`.
- `enqueue_message` is now called `send_message`.
- Client and model files have been made internal. Users should import from the top level modules `azure.storage.queue` and `azure.storage.queue.aio` only.
- The `generate_shared_access_signature` methods on both `QueueServiceClient` and `QueueClient` have been replaced by module level functions `generate_account_sas` and `generate_queue_sas`.
- `get_service_stats` now returns a dict
- `get_service_properties` now returns a dict with keys consistent to `set_service_properties`

 **New features**

- `ResourceTypes`, and `Services` now have method `from_string` which takes parameters as a string.

**Fixes and improvements**

- Fixed an issue where XML is being double encoded and double decoded.

## 12.0.0b4 (2019-10-08)

**Breaking changes**

- Permission models.
  - `AccountPermissions`, `QueuePermissions` have been renamed to
  `AccountSasPermissions`, `QueueSasPermissions` respectively.
  - enum-like list parameters have been removed from both of them.
  - `__add__` and `__or__` methods are removed.
- `max_connections` is now renamed to `max_concurrency`.

**New features**

- `AccountSasPermissions`, `QueueSasPermissions` now have method `from_string` which takes parameters as a string.

## 12.0.0b3 (2019-09-10)

**Dependency updates**
- Adopted [azure-core](https://pypi.org/project/azure-core/) 1.0.0b3
  - If you later want to revert to previous versions of azure-storage-queue, or another Azure SDK
  library requiring azure-core 1.0.0b1 or azure-core 1.0.0b2, you must explicitly install
  the specific version of azure-core as well. For example:

  `pip install azure-core==1.0.0b2 azure-storage-queue==12.0.0b2`


## 12.0.0b2 (2019-08-06)

**Breaking changes**
- The behavior of listing operations has been modified:
    - The previous `marker` parameter has been removed.
    - The iterable response object now supports a `by_page` function that will return a secondary iterator of batches of results. This function supports a `continuation_token` parameter to replace the previous `marker` parameter.
- The new listing behaviour is also adopted by the `receive_messages` operation:
    - The receive operation returns a message iterator as before.
    - The returned iterator supports a `by_page` operation to receive messages in batches.

**New features**
- Added async APIs to subnamespace `azure.storage.queue.aio`.
- Distributed tracing framework OpenCensus is now supported.

**Dependency updates**
- Adopted [azure-core](https://pypi.org/project/azure-core/) 1.0.0b2
  - If you later want to revert to azure-storage-queue 12.0.0b1, or another Azure SDK
  library requiring azure-core 1.0.0b1, you must explicitly install azure-core
  1.0.0b1 as well. For example:

  `pip install azure-core==1.0.0b1 azure-storage-queue==12.0.0b1`

**Fixes and improvements**
- General refactor of duplicate and shared code.


## 12.0.0b1 (2019-07-02)

Version 12.0.0b1 is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Storage Queues. For more information about this, and preview releases of other Azure SDK libraries, please visit
https://aka.ms/azure-sdk-preview1-python.

**Breaking changes: New API design**
- Operations are now scoped to a particular client:
    - `QueueServiceClient`: This client handles account-level operations. This includes managing service properties and listing the queues within an account.
    - `QueueClient`: The client handles operations within a particular queue. This includes creating or deleting that queue, as well as enqueueing and dequeueing messages.

    These clients can be accessed by navigating down the client hierarchy, or instantiated directly using URLs to the resource (account or queue).
    For full details on the new API, please see the [reference documentation](https://azure.github.io/azure-sdk-for-python/storage.html#azure-storage-queue).
- New message iterator, for receiving messages from a queue in a continuous stream.
- New underlying REST pipeline implementation, based on the new `azure-core` library.
- Client and pipeline configuration is now available via keyword arguments at both the client level, and per-operation. See reference documentation for a full list of optional configuration arguments.
- Authentication using `azure-identity` credentials
  - see the
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md)
  for more information
- New error hierarchy:
    - All service errors will now use the base type: `azure.core.exceptions.HttpResponseError`
    - The are a couple of specific exception types derived from this base type for common error scenarios:
        - `ResourceNotFoundError`: The resource (e.g. queue, message) could not be found. Commonly a 404 status code.
        - `ResourceExistsError`: A resource conflict - commonly caused when attempting to create a resource that already exists.
        - `ResourceModifiedError`: The resource has been modified (e.g. overwritten) and therefore the current operation is in conflict. Alternatively this may be raised if a condition on the operation is not met.
        - `ClientAuthenticationError`: Authentication failed.
- No longer have specific operations for `get_metadata` - use `get_properties` instead.
- No longer have specific operations for `exists` - use `get_properties` instead.
- Operations `get_queue_acl` and `set_queue_acl` have been renamed to `get_queue_access_policy` and `set_queue_access_policy`.
- Operation `put_message` has been renamed to `enqueue_message`.
- Operation `get_messages` has been renamed to `receive_messages`.

## 2.0.1
- Updated dependency on azure-storage-common.

## 2.0.0
- Support for 2018-11-09 REST version.

## 1.4.0
- azure-storage-nspkg is not installed anymore on Python 3 (PEP420-based namespace package)

## 1.3.0
- Support for 2018-03-28 REST version. Please see our REST API documentation and blog for information about the related added features.

## 1.2.0rc1
- Support for 2017-11-09 REST version. Please see our REST API documentation and blog for information about the related added features.
- Added support for OAuth authentication for HTTPS requests(Please note that this feature is available in preview).

## 1.1.0
- Support for 2017-07-29 REST version. Please see our REST API documentation and blogs for information about the related added features.
- Queue messages can now have an arbitrarily large or infinite time to live.
- Error message now contains the ErrorCode from the x-ms-error-code header value.

## 1.0.0
- The package has switched from Apache 2.0 to the MIT license.

# Change Log azure-storage-queue


## Version 12.0.0b2:

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


## Version 12.0.0b1:

Version 12.0.0b1 is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Storage Queues. For more information about this, and preview releases of other Azure SDK libraries, please visit
https://aka.ms/azure-sdk-preview1-python.

**Breaking changes: New API design**
- Operations are now scoped to a particular client:
    - `QueueServiceClient`: This client handles account-level operations. This includes managing service properties and listing the queues within an account.
    - `QueueClient`: The client handles operations within a particular queue. This includes creating or deleting that queue, as well as enqueueing and dequeueing messages.

    These clients can be accessed by navigating down the client hierarchy, or instantiated directly using URLs to the resource (account or queue).
    For full details on the new API, please see the [reference documentation](http://azure.github.io/azure-sdk-for-python/ref/azure.storage.queue.html).
- New message iterator, for receiving messages from a queue in a continuous stream.
- New underlying REST pipeline implementation, based on the new `azure-core` library.
- Client and pipeline configuration is now available via keyword arguments at both the client level, and per-operation. See reference documentation for a full list of optional configuration arguments.
- Authentication using `azure-identity` credentials
  - see the
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md)
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

## Version 2.0.1:
- Updated dependency on azure-storage-common.

## Version 2.0.0:
- Support for 2018-11-09 REST version.

## Version 1.4.0:

- azure-storage-nspkg is not installed anymore on Python 3 (PEP420-based namespace package)

## Version 1.3.0:

- Support for 2018-03-28 REST version. Please see our REST API documentation and blog for information about the related added features.

## Version 1.2.0rc1:

- Support for 2017-11-09 REST version. Please see our REST API documentation and blog for information about the related added features.
- Added support for OAuth authentication for HTTPS requests(Please note that this feature is available in preview).

## Version 1.1.0:

- Support for 2017-07-29 REST version. Please see our REST API documentation and blogs for information about the related added features.
- Queue messages can now have an arbitrarily large or infinite time to live.
- Error message now contains the ErrorCode from the x-ms-error-code header value.

## Version 1.0.0:

- The package has switched from Apache 2.0 to the MIT license.
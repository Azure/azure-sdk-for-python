# Change Log azure-storage-queue

## Version 12.0.0b1:

For release notes and more information please visit
https://aka.ms/azure-sdk-preview1-python

- **Breaking** New API desgin:
    - Operations are now scoped to a particular client:
        - `QueueServiceClient`: This client handles account-level operations. This includes managing service properties and listing the queues within an account.
        - `QueueClient`: The client handles operations within a particular queue. This includes creating or deleting that queue, as well as enqueuing and dequeuing messages.

      These clients can be accessed by navigating down the client hierarchy, or instantiated directly using URLs to the resource (account or queue).
      For full details on the new API, please see reference documentation.
    - New message iterator, for receiving messages from a queue in a continuous stream.
    - New underlying REST pipeline implementation, based on the new `azure.core` library.
    - Client and pipeline configuration is now available via keyword arguments at both the client level, and per-operation. See reference documentation for a full list of optional configuration arguments.
    - Support for token credentials using the new `azure.identity` library.
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
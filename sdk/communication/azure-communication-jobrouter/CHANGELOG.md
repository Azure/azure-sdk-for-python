# Release History

## 1.0.0b1 (2023-07-27)

This is the beta release of Azure Communication Job Router Python SDK. For more information, please see the [README][read_me].

This is a Public Preview version, so breaking changes are possible in subsequent releases as we improve the product. To provide feedback, please submit an issue in our [Azure SDK for Python GitHub repo][issues].


### Features Added
- Using `JobRouterAdministrationClient`
  - Create, update, get, list and delete `DistributionPolicy`.
  - Create, update, get, list and delete `RouterQueue`.
  - Create, update, get, list and delete `ClassificationPolicy`.
  - Create, update, get, list and delete `ExceptionPolicy`.
- Using `JobRouterClient`
  - Create, update, get, list and delete `RouterJob`.
  - `RouterJob` can be created and updated with different matching modes: `QueueAndMatchMode`, `ScheduleAndSuspendMode` and `SuspendMode`.
  - Re-classify a `RouterJob`.
  - Close a `RouterJob`.
  - Complete a `RouterJob`.
  - Cancel a `RouterJob`.
  - Un-assign a `RouterJob`, with option to suspend matching.
  - Get the position of a `RouterJob` in a queue.
  - Create, update, get, list and delete `RouterWorker`.
  - Accept an offer.
  - Decline an offer.
  - Get queue statistics.

<!-- LINKS -->
[read_me]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/README.md
[issues]: https://github.com/Azure/azure-sdk-for-python/issues

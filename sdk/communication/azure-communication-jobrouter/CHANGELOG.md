# Release History

## 1.0.0 (Unreleased)

### Features Added
- `JobRouterAdministrationClient`
  - Add `upsert_distribution_policy`. Supports `match_condition: Optional[MatchConditions]` which can specify HTTP options for conditional requests based on `etag: Optional[str]` and/or `if_unmodified_since: Optional[~datetime.datetime]`.
  - Add `upsert_queue`. Supports `match_condition: Optional[MatchConditions]` which can specify HTTP options for conditional requests based on `etag: Optional[str]` and/or `if_unmodified_since: Optional[~datetime.datetime]`.
  - Add `upsert_classification_policy`. Supports `match_condition: Optional[MatchConditions]` which can specify HTTP options for conditional requests based on `etag: Optional[str]` and/or `if_unmodified_since: Optional[~datetime.datetime]`.
  - Add `upsert_exception_policy`. Supports `match_condition: Optional[MatchConditions]` which can specify HTTP options for conditional requests based on `etag: Optional[str]` and/or `if_unmodified_since: Optional[~datetime.datetime]`.
- `JobRouterClient`
  - Add `upsert_job`. Supports `match_condition: Optional[MatchConditions]` which can specify HTTP options for conditional requests based on `etag: Optional[str]` and/or `if_unmodified_since: Optional[~datetime.datetime]`.
  - Add `upsert_worker`. Supports `match_condition: Optional[MatchConditions]` which can specify HTTP options for conditional requests based on `etag: Optional[str]` and/or `if_unmodified_since: Optional[~datetime.datetime]`.
### Breaking Changes
- All models now resides under `azure.communication.jobrouter.models` instead of `azure.communication.jobrouter`.
- `JobRouterAdministrationClient`
  - Create and update methods have been removed for `DistributionPolicy`. Use `upsert_distribution_policy` instead.
  - Create and update methods have been removed for `RouterQueue`. Use `upsert_queue` instead.
  - Create and update methods have been removed for `ClassificationPolicy`. Use `upsert_classification_policy` instead.
  - Create and update methods have been removed for `ExceptionPolicy`. Use `upsert_exception_policy` instead.
  - `list_classification_policies` returns `(Async)Iterable[ClassificationPolicy]` instead of `(Async)Iterable[ClassificationPolicyItem]`
  - `list_distribution_policies` returns `(Async)Iterable[DistributionPolicy]` instead of `(Async)Iterable[DistributionPolicyItem]`
  - `list_exception_policies` returns `(Async)Iterable[ExceptionPolicy]` instead of `(Async)Iterable[ExceptionPolicyItem]`
  - `list_queues` returns `(Async)Iterable[RouterQueue]` instead of `(Async)Iterable[RouterQueueItem]`
- `JobRouterClient`
  - Create and update methods have been removed for `RouterJob`. Use `upsert_job` instead.
  - Create and update methods have been removed for `RouterWorker`. Use `upsert_worker` instead.
  - `list_jobs` returns `(Async)Iterable[RouterJob]` instead of `(Async)Iterable[RouterJobItem]`
  - `list_workers` returns `(Async)Iterable[RouterWorker]` instead of `(Async)Iterable[RouterWorkerItem]`
  - `decline_job_offer` - keyword argument `retry_offer_at: Optional[datetime]` removed from method. Use `decline_job_offer_options: Optional[Union[DeclineJobOfferOptions, JSON, IO]]` instead.
  - `close_job` - keyword arguments `close_at: Optional[datetime]`, `disposition_code: Optional[str]`, `note: Optional[str]` removed from method. Use `close_job_options: Union[CloseJobOptions, JSON, IO]` instead.
  - `cancel_job` - keyword arguments `disposition_code: Optional[str]`, `note: Optional[str]` removed from method. Use `cancel_job_options: Optional[Union[CancelJobOptions, JSON, IO]]` instead.
  - `complete_job` - keyword argument `note: Optional[str]` removed from method. Use `complete_job_options: Union[CompleteJobOptions, JSON, IO]` instead.
  - `unassign_job` - keyword argument `suspend_matching: Optional[bool]` removed from method. Use `unassign_job_options: Optional[Union[UnassignJobOptions, JSON, IO]]` instead.
- `RouterJob`
  - Property `notes` - Changed from `Dict[str, ~datetime.datetime]` to `List[RouterJobNote]`
- `ClassificationPolicy`
  - Rename property `queue_selectors` to `queue_selector_attachments`.
  - Rename property `worker_selectors` to `worker_selector_attachments`.
- `ExceptionPolicy`
  - Property `exception_rules` - Changed from `Dictionary[str, ExceptionRule]` -> `List[ExceptionRule]`
- `ExceptionRule`
  - Property `actions` - Changed `Dict[str, ExceptionAction]` -> `List[ExceptionAction]`
- `ScoringRuleOptions`
  - Rename property `allow_scoring_batch_of_workers` -> `is_batch_scoring_enabled`
- `RouterWorker`
  - Property changed `queue_assignments: Dict[str, RouterQueueAssignment]` -> `queues: List[str]`
  - Rename `total_capacity` -> `capacity`
  - Property changed `channel_configurations: Dict[str, ChannelConfiguration]` -> `channels: List[RouterChannel]`

#### Renames
- `ChannelConfiguration` -> `RouterChannel`
- `Oauth2ClientCredential` -> `OAuth2WebhookClientCredential`

#### Deletions
- `ClassificationPolicyItem`
- `DistributionPolicyItem`
- `ExceptionPolicyItem`
- `RouterQueueItem`
- `RouterWorkerItem`
- `RouterJobItem`
- `RouterQueueAssignment`

### Bugs Fixed

### Other Changes
- `ClassificationPolicy`
  - Add `etag`
- `DistributionPolicy`
  - Add `etag`
- `ExceptionPolicy`
  - Add `etag`
- `RouterQueue`
  - Add `etag`
- `RouterJob`
  - Add `etag`
- `RouterWorker`
  - Add `etag`
- `ExceptionRule`
  - Add `id`
- `ExceptionAction` and all derived classes `CancelExceptionAction`, `ManualReclassifyExceptionAction`, `ReclassifyExceptionAction`
  - Add `id`. Property is read-only. If not provided, it will be generated by the service.
- `RouterChannel`
  - Add `channel_id`

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

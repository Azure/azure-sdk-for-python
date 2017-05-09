.. :changelog:

Release History
===============

3.0.0 (2017-05-10)
++++++++++++++++++

- Added support for the new low-priority node type; `AddPoolParameter` and `PoolSpecification` now have an additional property `target_low_priority_nodes`.
- `target_dedicated` and `current_dedicated` on `CloudPool`, `AddPoolParameter` and `PoolSpecification` have been renamed to `target_dedicated_nodes` and `current_dedicated_nodes`.
- `resize_error` on `CloudPool` is now a collection called `resize_errors`.
- Added a new `is_dedicated` property on `ComputeNode`, which is `false` for low-priority nodes.
- Added a new `allow_low_priority_node` property to `JobManagerTask`, which if `true` allows the `JobManagerTask` to run on a low-priority compute node.
- `PoolResizeParameter` now takes two optional parameters, `target_dedicated_nodes` and `target_low_priority_nodes`, instead of one required parameter `target_dedicated`.
  At least one of these two parameters must be specified.
- Added support for uploading task output files to persistent storage, via the `OutputFiles` property on `CloudTask` and `JobManagerTask`. 
- Added support for specifying actions to take based on a task's output file upload status, via the `file_upload_error` property on `ExitConditions`. 
- Added support for determining if a task was a success or a failure via the new `result` property on all task execution information objects.
- Renamed `scheduling_error` on all task execution information objects to `failure_information`. `TaskFailureInformation` replaces `TaskSchedulingError` and is returned any
  time there is a task failure. This includes all previous scheduling error cases, as well as nonzero task exit codes, and file upload failures from the new output files feature. 
- Renamed `SchedulingErrorCategory` enum to `ErrorCategory`.
- Renamed `scheduling_error` on `ExitConditions` to `pre_processing_error` to more clearly clarify when the error took place in the task life-cycle.
- Added support for provisioning application licenses to your pool, via a new `application_licenses` property on `PoolAddParameter`, `CloudPool` and `PoolSpecification`.
  Please note that this feature is in gated public preview, and you must request access to it via a support ticket.
- The `ssh_private_key` attribute of a `UserAccount` object has been replaced with an expanded `LinuxUserConfiguration` object with additional settings for a user ID and group ID of the 
  user account.
- Removed `unmapped` enum state from `AddTaskStatus`, `CertificateFormat`, `CertificateVisibility`, `CertStoreLocation`, `ComputeNodeFillType`, `OSType`, and `PoolLifetimeOption` as they were not ever used.
- Improved and clarified documentation.

2.0.1 (2017-04-19)
++++++++++++++++++

- This wheel package is now built with the azure wheel extension

2.0.0 (2017-02-23)
++++++++++++++++++

- AAD token authentication now supported.
- Some operation names have changed (along with their associated parameter model classes):
  * pool.list_pool_usage_metrics -> pool.list_usage_metrics
  * pool.get_all_pools_lifetime_statistics -> pool.get_all_lifetime_statistics
  * job.get_all_jobs_lifetime_statistics -> job.get_all_lifetime_statistics
  * file.get_node_file_properties_from_task -> file.get_properties_from_task
  * file.get_node_file_properties_from_compute_node -> file.get_properties_from_compute_node
- The attribute 'file_name' in relation to file operations has been renamed to 'file_path'.
- Change in naming convention for enum values to use underscores: e.g. StartTaskState.waitingforstarttask -> StartTaskState.waiting_for_start_task.
- Support for running tasks under a predefined or automatic user account. This includes tasks, job manager tasks, job preparation and release tasks and pool start tasks. This feature replaces the previous 'run_elevated' option on a task.
- Tasks now have an optional scoped authentication token (only applies to tasks and job manager tasks).
- Support for creating pools with a list of user accounts.
- Support for creating pools using a custom VM image (only supported on accounts created with a "User Subscription" pool allocation mode).

1.1.0 (2016-09-15)
++++++++++++++++++

- Added support for task reactivation

1.0.0 (2016-08-09)
++++++++++++++++++

- Added support for joining a CloudPool to a virtual network on using the network_configuration property.
- Added support for application package references on CloudTask and JobManagerTask.
- Added support for automatically terminating jobs when all tasks complete or when a task fails, via the on_all_tasks_complete property and 
  the CloudTask exit_conditions property.

0.30.0rc5
+++++++++

- Initial Release

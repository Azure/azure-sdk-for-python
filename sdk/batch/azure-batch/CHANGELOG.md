# Release History

## 10.0.0 (2020-09-01)

### Features
- **[Breaking]** Replaced property `maxTasksPerNode` with `taskSlotsPerNode` on the pool. Using this property tasks in a job can consume a dynamic amount of slots allowing for more fine-grained control over resource consumption.
- **[Breaking]** Changed the response type of `GetTaskCounts` to return `TaskCountsResult`, which is a complex object containing the previous `TaskCounts` object and a new `TaskSlotCounts` object providing similar information in the context of slots being used.
- Added property `requiredSlots` to the task allowing user to specify how many slots on a node it should take up.

## 9.0.0 (2020-03-24)

### Features
- Added ability to encrypt `ComputeNode` disk drives using the new `disk_encryption_configuration` property of `VirtualMachineConfiguration`.
- **[Breaking]** The `virtual_machine_id` property of `ImageReference` can now only refer to a Shared Image Gallery image.
- **[Breaking]** Pools can now be provisioned without a public IP using the new `public_ip_address_configuration` property of `NetworkConfiguration`.
  - The `public_ips` property of `NetworkConfiguration` has moved in to `public_ip_address_configuration` as well. This property can only be specified if `ip_provisioning_type` is `UserManaged`.

### REST API version
This version of the Batch .NET client library targets version 2020-03-01.11.0 of the Azure Batch REST API.

## 8.0.0 (2019-8-5)

- Using REST API version 2019-08-01.10.0.
    * Added ability to specify a collection of public IPs on `NetworkConfiguration` via the new `public_ips` property. This guarantees nodes in the Pool will have an IP from the list user provided IPs.
    * Added ability to mount remote file-systems on each node of a pool via the `mount_configuration` property on `CloudPool`.
    * Shared Image Gallery images can now be specified on the `virtual_machine_image_id` property of `ImageReference` by referencing the image via its ARM ID.
    * **Breaking** When not specified, the default value for `wait_for_success` on `StartTask` is now `True` (was `False`).
    * **Breaking** When not specified, the default value for `scope` on `AutoUserSpecification` is now always `Pool` (was `Task` on Windows nodes, `Pool` on Linux nodes).

## 7.0.0 (2019-6-11)

- Using REST API version 2019-06-01.9.0.
    * **Breaking** Replaced `AccountOperations.list_node_agent_skus` with `AccountOperations.list_supported_images`. `list_supported_images` contains all of the same information originally available in `list_node_agent_skus` but in a clearer format. New non-verified images are also now returned. Additional information about `capabilities` and `batch_support_end_of_life` is accessible on the `ImageInformation` object returned by `list_supported_images`.
    * Now support network security rules blocking network access to a `CloudPool` based on the source port of the traffic. This is done via the `source_port_ranges` property on `network_security_group_rules`.
    * When running a container, Batch now supports executing the task in the container working directory or in the Batch task working directory. This is controlled by the `working_directory` property on `TaskContainerSettings`.

## 6.0.1 (2019-2-26)

- Fix bug in TaskOperations.add_collection methods exception handling

## 6.0.0 (2018-12-14)

- Using REST API version 2018-12-01.8.0.
    * **Breaking** Removed support for the `upgrade_os` API on `CloudServiceConfiguration` pools.
        - Removed `PoolOperations.upgrade_os` API.
        - Renamed `target_os_version` to `os_version` and removed `current_os_version` on `CloudServiceConfiguration`.
        - Removed `upgrading` state from `PoolState` enum.
    * **Breaking** Removed `data_egress_gi_b` and `data_ingress_gi_b` from `PoolUsageMetrics`. These properties are no longer supported.
    * **Breaking** ResourceFile improvements
        * Added the ability specify an entire Azure Storage container in `ResourceFile`. There are now three supported modes for `ResourceFile`:
            - `http_url` creates a `ResourceFile` pointing to a single HTTP URL.
            - `storage_container_url` creates a `ResourceFile` pointing to the blobs under an Azure Blob Storage container.
            - `auto_storage_container_name` creates a `ResourceFile` pointing to the blobs under an Azure Blob Storage container in the Batch registered auto-storage account.
        * URLs provided to `ResourceFile` via the `http_url` property can now be any HTTP URL. Previously, these had to be an Azure Blob Storage URL.
        * The blobs under the Azure Blob Storage container can be filtered by `blob_prefix` property.
    * **Breaking** Removed `os_disk` property from `VirtualMachineConfiguration`. This property is no longer supported.
    * Pools which set the `dynamic_vnet_assignment_scope` on `NetworkConfiguration` to be `DynamicVNetAssignmentScope.job` can now dynamically assign a Virtual Network to each node the job's tasks run on. The specific Virtual Network to join the nodes to is specified in the new `network_configuration` property on `CloudJob` and `JobSpecification`.
        - Note: This feature is in public preview. It is disabled for all Batch accounts except for those which have contacted us and requested to be in the pilot.
    * The maximum lifetime of a task is now 180 days (previously it was 7).
    * Added support on Windows pools for creating users with a specific login mode (either `batch` or `interactive`) via `WindowsUserConfiguration.login_mode`.
    * The default task retention time for all tasks is now 7 days, previously it was infinite.
- **Breaking** Renamed the `base_url` parameter to `batch_url` on `BatchServiceClient` class, and it is required now.

## 5.1.1 (2018-10-16)

**Bugfixes**

- Fix authentication class to allow HTTP session to be re-used

**Note**

- azure-nspkg is not installed anymore on Python 3 (PEP420-based namespace package)

## 5.1.0 (2018-08-28)

- Update operation TaskOperations.add_collection with the following added functionality:
    + Retry server side errors.
    + Automatically chunk lists of more than 100 tasks to multiple requests.
    + If tasks are too large to be submitted in chunks of 100, reduces number of tasks per request.
    + Add a parameter to specify number of threads to use when submitting tasks.

## 5.0.0 (2018-08-24)

- Using REST API version 2018-08-01.7.0.
    + Added `node_agent_info` in ComputeNode to return the node agent information
    + **Breaking** Removed the `validation_status` property from `TaskCounts`.
    + **Breaking** The default caching type for `DataDisk` and `OSDisk` is now `read_write` instead of `none`.
- `BatchServiceClient` can be used as a context manager to keep the underlying HTTP session open for performance.
- **Breaking** Model signatures are now using only keywords-arguments syntax. Each positional argument must be rewritten as a keyword argument.
- **Breaking** The following operations signatures are changed:
   + Operation PoolOperations.enable_auto_scale
   + Operation TaskOperations.update
   + Operation ComputeNodeOperations.reimage
   + Operation ComputeNodeOperations.disable_scheduling
   + Operation ComputeNodeOperations.reboot
   + Operation JobOperations.terminate
- Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to improve the behavior when unrecognized enum values are encountered.

## 4.1.3 (2018-04-24)

- Update some APIs' comments
- New property `leaving_pool` in `node_counts` type.

## 4.1.2 (2018-04-23)

**Bugfixes**

- Compatibility of the sdist with wheel 0.31.0
- Compatibility with msrestazure 0.4.28

## 4.1.1 (2018-03-26)

- Fix regression on method `enable_auto_scale`.

## 4.1.0 (2018-03-07)

- Using REST API version 2018-03-01.6.1.
- Added the ability to query pool node counts by state, via the new `list_pool_node_counts` method.
- Added the ability to upload Azure Batch node agent logs from a particular node, via the `upload_batch_service_logs` method.
   + This is intended for use in debugging by Microsoft support when there are problems on a node.

## 4.0.0 (2017-09-25)

- Using REST API version 2017-09-01.6.0.
- Added the ability to get a discount on Windows VM pricing if you have on-premises licenses for the OS SKUs you are deploying, via `license_type` on `VirtualMachineConfiguration`.
- Added support for attaching empty data drives to `VirtualMachineConfiguration` based pools, via the new `data_disks` attribute on `VirtualMachineConfiguration`.
- **Breaking** Custom images must now be deployed using a reference to an ARM Image, instead of pointing to .vhd files in blobs directly.
    + The new `virtual_machine_image_id` property on `ImageReference` contains the reference to the ARM Image, and `OSDisk.image_uris` no longer exists.
    + Because of this, `image_reference` is now a required attribute of `VirtualMachineConfiguration`.
- **Breaking** Multi-instance tasks (created using `MultiInstanceSettings`) must now specify a `coordination_commandLine`, and `number_of_instances` is now optional and defaults to 1.
- Added support for tasks run using Docker containers. To run a task using a Docker container you must specify a `container_configuration` on the `VirtualMachineConfiguration` for a pool, and then add `container_settings` on the Task.

## 3.1.0 (2017-07-24)

- Added a new operation `job.get_task_counts` to retrieve the number of tasks in each state.
- Added suuport for inbound endpoint configuration on a pool - there is a new `pool_endpoint_configuration` attribute on `NetworkConfiguration`.
  This property is only supported on pools that use `virtual_machine_configuration`.
- A `ComputeNode` now also has an `endpoint_configuration` attribute with the details of the applied endpoint configuration for that node.

## 3.0.0 (2017-05-10)

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

## 2.0.1 (2017-04-19)

- This wheel package is now built with the azure wheel extension

## 2.0.0 (2017-02-23)

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

## 1.1.0 (2016-09-15)

- Added support for task reactivation

## 1.0.0 (2016-08-09)

- Added support for joining a CloudPool to a virtual network on using the network_configuration property.
- Added support for application package references on CloudTask and JobManagerTask.
- Added support for automatically terminating jobs when all tasks complete or when a task fails, via the on_all_tasks_complete property and
  the CloudTask exit_conditions property.

## 0.30.0rc5

- Initial Release

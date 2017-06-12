.. :changelog:

Release History
===============

2.0.1 (2017-04-19)
++++++++++++++++++

This wheel package is now built with the azure wheel extension

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

* Initial Release

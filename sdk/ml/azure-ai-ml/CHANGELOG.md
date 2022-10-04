# Release History

## 0.1.0 (Unreleased)

### Features Added
 - Support passing JobService as argument to Command()
 - Added support for custom setup scripts on compute instances.
 - Added a `show_progress` parameter to MLClient for enable/disable progress bars of long running operations.
 - Support `month_days` in `RecurrencePattern` when using `RecurrenceSchedule`.
 - Support `ml_client.schedules.list` with `list_view_type`, default to `ENABLED_ONLY`.

### Breaking Changes
- ComputeOperations.attach has been renamed to begin_attach.
- Deprecated parameter path has been removed from load and dump methods.
- JobOperations.cancel() is renamed to JobOperations.begin_cancel() and it returns LROPoller
- Workspace.list_keys renamed to Workspace.get_keys.
- OnlineDeploymentOperations.delete has been renamed to begin_attach.
- Datastore credentials are switched to use unified credential configuration classes.
- UserAssignedIdentity is replaced by ManagedIdentityConfiguration
- Job using unified identity classes.
- Endpoint uses unified identity classes.
- Workspace ManagedServiceIdentity has been replaced by IdentityConfiguration.

### Bugs Fixed
- Fix identity passthrough job with single file code

### Other Changes
 - Removed declaration on Python 3.6 support
 - Added support for custom setup scripts on compute instances.
 - Updated dependencies upper bounds to be major versions.

## 0.1.0b7 (2022-09-22)

### Features Added
 - Spark job submission.
 - Command and sweep job docker config (shmSize and dockerArgs) spec support.
 - Entity load and dump now also accept a file pointer as input.
 - Load and dump input names changed from path to 'source' and 'dest', respectively.
 - Load and dump 'path' input still works, but is deprecated and emits a warning.
 - Managed Identity Support for Compute Instance (experimental).
 - Enable using @dsl.pipeline without brackets when no additional parameters.
 - Expose Azure subscription Id and resource group name from MLClient objects.
 - Added Idle Shutdown support for Compute Instances, allowing instances to shutdown after a set period of inactivity.
 - Online Deployment Data Collection for eventhub and data storage will be supported. 
 - Syntax validation on scoring scripts of Batch Deployment and Online Deployment will prevent the user from submitting bad deployments.

### Breaking Changes
 - Change (begin_)create_or_update typehints to use generics.
 - Remove invalid option from create_or_update typehints.
 - Change error returned by (begin_)create_or_update invalid input to TypeError.
 - Rename set_image_model APIs for all vision tasks to set_training_parameters
 - JobOperations.download defaults to "." instead of Path.cwd()

### Bugs Fixed

### Other Changes
 - Show 'properties' on data assets


## 0.1.0b6 (2022-08-09)

### Features Added

- Support for AutoML Component
- Added skip_validation for Job/Component create_or_update

### Breaking Changes

- Dataset removed from public interface.

### Bugs Fixed

- Fixed mismatch errors when updating scale_settings for KubernetesOnlineDeployment.
- Removed az CLI command that was printed when deleting OnlineEndpoint

### Other Changes


## 0.1.0b5 (2022-07-15)

### Features Added

- Allow Input/Output objects to be used by CommandComponent.
- Added MoonCake cloud support.
- Unified inputs/outputs building and validation logic in BaseNode.
- Allow Git repo URLs to be used as code for jobs and components.
- Updated AutoML YAML schema to use InputSchema.
- Added end_time to job schedule.
- MIR and pipeline job now support registry assets.

### Breaking Changes

### Bugs Fixed

- Have mldesigner use argparser to parse incoming args.
- Bumped pyjwt version to <3.0.0.
- Reverted "upload support for symlinks".
- Error message improvement when a YAML UnionField fails to match.
- Reintroduced support for symlinks when uploading.
- Hard coded registry base URL to eastus region to support preview.

## 0.1.0b4 (2022-06-16)

## 0.1.0b3 (2022-05-24)

### Features Added

- First preview.

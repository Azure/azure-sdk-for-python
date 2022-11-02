# Release History

## 1.1.0 (2022-11-07)

### Features Added
- Registry list operation now accepts scope value to allow subscription-only based requests.
- Most configuration classes from the entity package now implement the standard mapping protocol.
- Add registry delete operation.
- The values of JobService.job_service_type are now using the snake case. e.g jupyter_lab, ssh, tensor_board, vs_code.
- Command function now accepts services param of type Dict[str, JobService] instead of dict.

### Breaking Changes

### Bugs Fixed
- MLClient.from_config can now find the default config.json on Compute Instance when running sample notebooks.
- Registries now assign managed tags to match registry's tags.
- Adjust registry experimental tags and imports to avoid warning printouts for unrelated operations.
- Make registry delete operation return an LROPoller, and change name to begin_delete.
- Prevent registering an already existing environment that references conda file.

### Other Changes

## 1.0.0 (2022-10-10)
- GA release
- Dropped support for Python 3.6. The Python versions supported for this release are 3.7-3.10.

### Features Added

### Breaking Changes
- OnlineDeploymentOperations.delete has been renamed to begin_delete.
- Datastore credentials are switched to use unified credential configuration classes.
- UserAssignedIdentity is replaced by ManagedIdentityConfiguration
- Endpoint and Job use unified identity classes.
- Workspace ManagedServiceIdentity has been replaced by IdentityConfiguration.

### Bugs Fixed

### Other Changes
 - Switched Compute operations to use Oct preview API version.
 - Updated batch deployment/endpoint invoke and list-jobs function signatures with curated BatchJob class.

## 0.1.0b8 (2022-10-07)

### Features Added
 - Support passing JobService as argument to Command()
 - Added support for custom setup scripts on compute instances.
 - Added a `show_progress` parameter to MLClient for enable/disable progress bars of long running operations.
 - Support `month_days` in `RecurrencePattern` when using `RecurrenceSchedule`.
 - Support `ml_client.schedules.list` with `list_view_type`, default to `ENABLED_ONLY`.
 - Add support for model sweeping and hyperparameter tuning in AutoML NLP jobs.
 - Added `ml_client.jobs.show_services()` operation.

### Breaking Changes
- ComputeOperations.attach has been renamed to begin_attach.
- Deprecated parameter path has been removed from load and dump methods.
- JobOperations.cancel() is renamed to JobOperations.begin_cancel() and it returns LROPoller
- Workspace.list_keys renamed to Workspace.get_keys.

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

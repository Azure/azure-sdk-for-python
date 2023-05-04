# Release History

## 1.7.0 (Unreleased)

### Features Added
- Added data import schedule. The class added is `ImportDataSchedule`.

### Bugs Fixed

### Breaking Changes

### Other Changes


## 1.6.0 (05/01/2023)

### Features Added
- Added experimental scatter gather node to DSL package. This node has a unique mldesigner dependency.
- Added support to make JobService and ServiceInstance objects serializable when printed
- Support Singularity compute in pipeline job
- Added purge operation support for workspace resource
- Added Feature Store, its dedicated classes and updated the docstrings, now available in public interface. The classes added are `FeatureStoreOperations, FeatureSetOperations, FeatureStoreEntityOperations` with properties classes specific to the new features.
- Support additional_includes in command component
- Added experimental `distribution: ray` support in command job.
- Added support to enable data isolation feature at workspace creation stage.
- Added auto_delete_setting support for asset version in data import job.

### Bugs Fixed

- Fixed issue where show_progress=False was not being respected for uploads when set via MLClient
- Fixed issue of spark input/output mode validation doesn't take effect because of wrong type assertion
- Fixed the bug when setting `node.limits.timeout` to a pipeline input.
- Removed Experimental Tag from Idle Shutdown, Custom Applications, Setup Scripts, and Image Metadata on Compute Instances.
- Removed Experimental Tag from JobService classes

### Breaking Changes

- Renamed `JobServiceBase.job_service_type` to `type`

### Other Changes

- Remove the default placeholder for CommandComponent.code

## 1.5.0 (2023-03-20)

### Features Added
- Added support for `tags` on Compute Resources.
- Added support for promoting data asset from a workspace to a registry
- Added support for registering named asset from job output or node output by specifying name and version settings.
- Added support for data binding on outputs inside dynamic arguments for dsl pipeline
- Added support for serverless compute in pipeline, command, automl and sweep job
- Added support for `job_tier` and `priority` in standalone job
- Added support for passing `locations` via command function and set it to `JobResourceConfiguration.locations`
- Added support for modifying SSH key values after creation on Compute Resources.
- Added WorkspaceConnection types `s3`, `snowflake`, `azure_sql_db`, `azure_synapse_analytics`, `azure_my_sql_db`, `azure_postgres_db`
- Added WorkspaceConnection auth type `access_key` for `s3`
- Added DataImport class and DataOperations.import_data.
- Added DataOperations.list_materialization_status - list status of data import jobs that create asset versions via asset name.

### Bugs Fixed

- Fix experiment name wrongly set to 'Default' when schedule existing job.
- Error message improvement when a local path fails to match with data asset type.
- Error message improvement when an asset does not exist in a registry
- Fix an issue when submit spark pipeline job with referring a registered component
- Fix an issue that prevented Job.download from downloading the output of a BatchJob

### Other Changes

- Added dependency on `azure-mgmt-resource`
- Added dependency on `azure-mgmt-resourcegraph`
- Added dependency on `opencensus-ext-azure<2.0.0`
- Update job types to use MFE Dec preview rest objects.
- Added classifiers for Python version 3.11.
- Added warning for reserved keywords in IO names in pipeline job nodes.
- Added telemetry logging for SDK Jupyter Notebook scenarios with opt-out option (see README.md)

## 1.4.0 (2023-02-07)

### Features Added
- Added dedicated classes for each type of job service and updated the docstrings. The classes added are `JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService` with a few properties specific to the type.
- Added Custom Applications Support to Compute Instances.
- Update data asset list, show and create operations to support data assets in registry.

### Bugs Fixed
- Fixed an issue where the ordering of `.amlignore` and `.gitignore` files are not respected.
- Fixed an issue that attributes with a value of `False` in `PipelineJobSettings` are not respected.
- Fixed an issue where ignore files weren't considered during upload directory size calculations.
- Fixed an issue where symlinks crashed upload directory size calculations.
- Fixes a bug where enable_node_public_ip returned an improper value when fetching a Compute.

### Other Changes
- Update workspace creation to use Log Analytics-Based Application Insights when the user does not specify/bring their own App Insights.
- Upgraded minimum azure-core version to 1.23.0.

## 1.3.0 (2023-01-13)

### Features Added
- Change print behavior of entity classes to show object yaml in notebooks, can be configured on in other contexts.
- Added property to enable/disable public ip addresses to Compute Instances and AML Computes.
- `Deployment` and `ScheduleOperations` added to public interface.

### Bugs Fixed
- Fixed issue with date-time format for utc_time_created field when creating models.
- Added stricter behavior for ArmStr schemas when parsing 'azureml:' prefix.
- Fixed issue where AmlComputes could only be created in a workspace's default region.
- Improved intellisense with VS Code for fields supporting local paths and datastores.
- Added validation for token generation with aml scope when user_identity is used in job definition aka OBO flow.
- Fixed duplicate node name error in pipeline when two node names assigned to the same node and get renamed by node.name='xx'.
- Resolve the cross references for MLClient, Resource and OnlineDeployment.
- Explicit use of Optional (or a Union with None), as per PEP 484.
- Fixed print on Command objects when job id is empty
- Fixed issue where `SasTokenConfiguration` cannot be used as credential for `WorkspaceConnection`

### Other Changes
- Removed dependency on API version 2021-10-01 and 2022-06-01-preview to reduce side of azure-ai-ml package.

## 1.2.0 (2022-12-05)

### Breaking Changes
- Removed description from Registry.
- Disable sdk telemetry logging

### Features Added
- Enable updating the CMK encryption key (workspace.encryption.keyVaultProperties.keyIdentifier) for a workspace.
- Mark JobService class and services param to command() as experimental.
- Added a replication_count value to the schema of SystemCreatedStorageAccount in Registry.
- Added support for Fairfax and MoonCake cloud for the registry discovery baseurl.
- Added support for variable args as pipeline input in DSL Pipeline.
- Added OS Patching Parameters to Compute Instance.

### Bugs Fixed
- Update the upper bound dependencies version for tqdm, strictyaml, colorama and opencensus-ext-azure.
- Added missing "properties" to batch deployment.
- Retain the cases for the names of system job services (Tracking and Studio).
- Update registry begin_delete method return type.
- Fixed sweep job optional input cannot be empty.
- Fixed bool test for output in download operation.
- Fixed Compute Instance schedule not being created
- Removed erroneous experimental warning from Compute Schedules

## 1.1.2 (2022-11-21)

### Features Added
- Restored idle_time_before_shutdown property for Compute Instances.
- Deprecated idle_time_before_shutdown property in favor of idle_time_before_shutdown_minutes.

### Bugs Fixed
- Fixed idle_time_before_shutdown appearing as None for Compute Instances returned by `show` or `list`.
- Fixed idle_time_before_shutdown_minutes preventing creation of Compute Instances when set to None.

## 1.1.1 (2022-11-15)

### Breaking Changes
- Renamed idle_time_before_shutdown to idle_time_before_shutdown_minutes and changed input type to int.

### Bugs Fixed
- Fixed idle_time_before_shutdown_minutes not appearing in GET calls for Compute Instances.

## 1.1.0 (2022-11-07)

### Features Added
- Registry list operation now accepts scope value to allow subscription-only based requests.
- Most configuration classes from the entity package now implement the standard mapping protocol.
- Add registry delete operation.
- The values of JobService.job_service_type are now using the snake case. e.g jupyter_lab, ssh, tensor_board, vs_code.
- Command function now accepts services param of type Dict[str, JobService] instead of dict.

### Bugs Fixed
- MLClient.from_config can now find the default config.json on Compute Instance when running sample notebooks.
- Fixed job inputs not accepting datastores or job inputs.
- Registries now assign managed tags to match registry's tags.
- Adjust registry experimental tags and imports to avoid warning printouts for unrelated operations.
- Make registry delete operation return an LROPoller, and change name to begin_delete.
- Prevent registering an already existing environment that references conda file.
- Fix ARM ID logic for registry environments (ex: Creating a registry component that references a registry environment).
- Fix ARM ID logic for passing models and environments with ID (ex: Creating endpoint deployment for a registry model should return said model's ID immediately)

### Other Changes
- Switched compute operations to go through 2022-10-01-preview API version.

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
- MLClient.from_config can now find the default config.json on Compute Instance when running sample notebooks.

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

## 0.1.0b5 (2022-07-15)

### Features Added

- Allow Input/Output objects to be used by CommandComponent.
- Added MoonCake cloud support.
- Unified inputs/outputs building and validation logic in BaseNode.
- Allow Git repo URLs to be used as code for jobs and components.
- Updated AutoML YAML schema to use InputSchema.
- Added end_time to job schedule.
- MIR and pipeline job now support registry assets.


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

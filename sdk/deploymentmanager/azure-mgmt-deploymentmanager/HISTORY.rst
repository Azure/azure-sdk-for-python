.. :changelog:

Release History
===============

0.2.0 (2019-12-31)
++++++++++++++++++

**Features**

- Added operation ServiceUnitsOperations.list
- Added operation RolloutsOperations.list
- Added operation ArtifactSourcesOperations.list
- Added operation ServiceTopologiesOperations.list
- Added operation StepsOperations.list
- Added operation ServicesOperations.list
- Added operation Operations.list

**Breaking changes**

- Parameter attributes of model WaitStepProperties is now required
- Removed operation Operations.get

**General Breaking Changes**

This version uses a next-generation code generator that might introduce breaking changes if from some import. In summary, some modules were incorrectly visible/importable and have been renamed. This fixed several issues caused by usage of classes that were not supposed to be used in the first place.
DeploymentManagerClient cannot be imported from azure.mgmt.deploymentmanager.deployment_manager_client anymore (import from azure.mgmt.deploymentmanager works like before)
DeploymentManagerClientConfiguration import has been moved from azure.mgmt.deploymentmanager.deployment_manager_client to azure.mgmt.deploymentmanager
A model MyClass from a "models" sub-module cannot be imported anymore using azure.mgmt.deploymentmanager.models.my_class (import from azure.mgmt.deploymentmanager.models works like before)
An operation class MyClassOperations from an operations sub-module cannot be imported anymore using azure.mgmt.deploymentmanager.operations.my_class_operations (import from azure.mgmt.deploymentmanager.operations works like before)
Last but not least, HTTP connection pooling is now enabled by default. You should always use a client as a context manager, or call close(), or use no more than one client per process.

0.1.0 (2019-04-15)
++++++++++++++++++

* Initial Release

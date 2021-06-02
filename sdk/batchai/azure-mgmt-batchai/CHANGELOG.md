# Release History

## 3.0.0 (2021-06-02)

**Features**

  - Added operation JobsOperations.begin_create
  - Added operation JobsOperations.begin_terminate
  - Added operation JobsOperations.begin_delete
  - Added operation WorkspacesOperations.begin_create
  - Added operation WorkspacesOperations.begin_delete
  - Added operation ClustersOperations.begin_create
  - Added operation ClustersOperations.begin_delete
  - Added operation FileServersOperations.begin_create
  - Added operation ExperimentsOperations.begin_create
  - Added operation ExperimentsOperations.begin_delete

**Breaking changes**

  - Operation ClustersOperations.update has a new signature
  - Operation ClustersOperations.get has a new signature
  - Operation ClustersOperations.list_by_workspace has a new signature
  - Operation ClustersOperations.list_remote_login_information has a new signature
  - Operation ClustersOperations.update has a new signature
  - Operation ExperimentsOperations.get has a new signature
  - Operation ExperimentsOperations.list_by_workspace has a new signature
  - Operation FileServersOperations.list_by_workspace has a new signature
  - Operation JobsOperations.get has a new signature
  - Operation JobsOperations.list_by_experiment has a new signature
  - Operation JobsOperations.list_output_files has a new signature
  - Operation JobsOperations.list_remote_login_information has a new signature
  - Operation UsagesOperations.list has a new signature
  - Operation WorkspacesOperations.get has a new signature
  - Operation WorkspacesOperations.list has a new signature
  - Operation WorkspacesOperations.list_by_resource_group has a new signature
  - Operation WorkspacesOperations.update has a new signature
  - Operation Operations.list has a new signature
  - Removed operation JobsOperations.create
  - Removed operation JobsOperations.terminate
  - Removed operation JobsOperations.delete
  - Removed operation WorkspacesOperations.create
  - Removed operation WorkspacesOperations.delete
  - Removed operation ClustersOperations.create
  - Removed operation ClustersOperations.delete
  - Removed operation FileServersOperations.create
  - Removed operation FileServersOperations.get
  - Removed operation FileServersOperations.delete
  - Removed operation ExperimentsOperations.create
  - Removed operation ExperimentsOperations.delete

## 0.1.0 (1970-01-01)

* Initial Release

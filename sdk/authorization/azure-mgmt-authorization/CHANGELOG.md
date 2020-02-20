# Release History

## 0.60.0 (2019-06-25)

**Breaking changes**

  - Rename elevate_access.post to global_administrator.elevate_access

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if you were importing from the v20xx_yy_zz
API folders. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - AuthorizationManagementClient cannot be imported from
    `azure.mgmt.authorization.v20xx_yy_zz.authorization_management_client`
    anymore (import from `azure.mgmt.authorization.v20xx_yy_zz`
    works like before)
  - AuthorizationManagementClientConfiguration import has been moved
    from
    `azure.mgmt.authorization.v20xx_yy_zz.authorization_management_client`
    to `azure.mgmt.authorization.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using
    `azure.mgmt.authorization.v20xx_yy_zz.models.my_class` (import
    from `azure.mgmt.authorization.v20xx_yy_zz.models` works like
    before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.authorization.v20xx_yy_zz.operations.my_class_operations`
    (import from `azure.mgmt.authorization.v20xx_yy_zz.operations`
    works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.52.0 (2019-05-23)

**Features**

  - Add elevate_access API

## 0.51.1 (2018-11-27)

**Bugfixes**

  - Missing principal_type in role assignment class #3802

## 0.51.0 (2018-11-12)

**Features**

  - Model RoleAssignmentCreateParameters has a new parameter
    principal_type

**Breaking changes**

  - Parameter role_definition_id of model
    RoleAssignmentCreateParameters is now required
  - Parameter principal_id of model RoleAssignmentCreateParameters is
    now required

Role Assignments API version is now 2018-09-01-preview

## 0.50.0 (2018-05-29)

**Features**

  - Support Azure Stack (multi API versionning)
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 0.40.0 (2018-03-13)

**Breaking changes**

  - Several properties have been flattened and "properties" attribute is
    not needed anymore (e.g. properties.email_address =>
    email_address)
  - Some method signature change (e.g. create_by_id)

**Features**

  - Adding attributes data_actions / not_data_actions /
    is_data_actions

API version is now 2018-01-01-preview

## 0.30.0 (2017-04-28)

  - Initial Release
  - This wheel package is built with the azure wheel extension

.. :changelog:

Release History
===============

0.52.0 (2019-05-23)
+++++++++++++++++++

**Features**

- Add elevate_access API

0.51.1 (2018-11-27)
+++++++++++++++++++

**Bugfixes**

- Missing principal_type in role assignment class  #3802

0.51.0 (2018-11-12)
+++++++++++++++++++

**Features**

- Model RoleAssignmentCreateParameters has a new parameter principal_type

**Breaking changes**

- Parameter role_definition_id of model RoleAssignmentCreateParameters is now required
- Parameter principal_id of model RoleAssignmentCreateParameters is now required

Role Assignments API version is now 2018-09-01-preview

0.50.0 (2018-05-29)
+++++++++++++++++++

**Features**

- Support Azure Stack (multi API versionning)
- Client class can be used as a context manager to keep the underlying HTTP session open for performance

**Bugfixes**

- Compatibility of the sdist with wheel 0.31.0

0.40.0 (2018-03-13)
+++++++++++++++++++

**Breaking changes**

- Several properties have been flattened and "properties" attribute is not needed anymore
  (e.g. properties.email_address => email_address)
- Some method signature change (e.g. create_by_id)

**Features**

- Adding attributes data_actions / not_data_actions / is_data_actions

API version is now 2018-01-01-preview

0.30.0 (2017-04-28)
+++++++++++++++++++

* Initial Release
* This wheel package is built with the azure wheel extension

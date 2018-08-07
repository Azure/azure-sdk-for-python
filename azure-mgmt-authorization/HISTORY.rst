.. :changelog:

Release History
===============

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

.. :changelog:

Release History
===============

0.40.0 (2017-06-06)
+++++++++++++++++++

- upgrading to API version 2016-10-01
- adding keyvault management plane updates to enable the soft delete feature for a new or existing keyvault

**Notes**

- this contains a backwards breaking change removing the All value from KeyPermissions, SecretPermissions and CertificatePermissions

0.31.0 (2017-04-19)
+++++++++++++++++++

**Bugfixes**

- Fix possible deserialization error, but updating from list<enumtype> to list<str> when applicable

**Notes**

- This wheel package is now built with the azure wheel extension

0.30.1 (2016-12-15)
+++++++++++++++++++

* Fix list Vault by subscription method return type

0.30.0 (2016-10-04)
+++++++++++++++++++

* Initial preview release (API Version 2016-10-02)

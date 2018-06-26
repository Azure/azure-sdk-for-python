.. :changelog:

Release History
===============
1.0.0b1 (2018-04-10)
++++++++++++++++++++

* Upgraded to autorest 3.0 generated code
* Breaking change in models requiring all init args be specified by keyword

1.0.0a2 (2018-03-28)
++++++++++++++++++++

* Upgrading to API version 2018-02-14-preview
* Breaking change in vault create_or_update now returns a 'LROPoller' objects rather than the Vault, to
  allow callers to determine when the vault is ready to accept traffic. Callers should use the result() method
  to block until the vault is accessible.
* Adding network_acls vault property for limiting network access to a vault
* Adding managed storage account key backup, restore and soft delete support
* Adding vault property enable_purge_protection for enhance protection against vault deletion

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

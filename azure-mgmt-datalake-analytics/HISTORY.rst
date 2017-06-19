.. :changelog:

Release History
===============
0.1.6 (2017-06-19)
++++++++++++++++++
* Fixing a regression discovered in 0.1.5. Please update to 0.1.6 to avoid any issues caused by that regression.

0.1.5 (2017-06-07)
++++++++++++++++++

**New features**

  * Support for Compute Policies on accounts. These will limit specific user and groups to certain job parallelism and priority.
  * Support for job relationship properties. These can be populated in the `related` property when submitting a job and can be retrieved with the `pipeline` and `recurrence` operation methods.
  * Suport for a basic option when listing catalog tables. When set to true, will only return the table name, schema name, database name and version for each table in the list, instead of all table metadata, improving performance when all information is not required.

0.1.4 (2017-04-20)
++++++++++++++++++

**New features**

  * Catalog item get and list support for Packages
  * Update to allow listing certain catalog items from within a database (no schema required to list):
  
    * list_tables_by_database
    * list_table_valued_functions_by_database
    * list_views_by_database
    * list_table_statistics_by_database
    * list_table_statistics_by_database_and_schema

**Notes**

* This wheel package is now built with the azure wheel extension

0.1.3 (2017-02-13)
++++++++++++++++++

**New features**

* Add support for firewall rules

  * Add, Update, Get, List and Delete operations
  * Enable/Disable the firewall
  *	Allow/Block Azure IPs

*	Remove minimum value requirement from DegreeOfParallelism. If a value <= 0 is passed in, it will be defaulted automatically to 1.
*	Remove unused ErrorDetails object

0.1.2 (2017-01-09)
++++++++++++++++++

**New features**

* Added the ability to create and update accounts with usage commitment levels for Data Lake Store and Data Lake Analytics

**Bugfixes**

* Fixed a bug where three job diagnostic severity types were missing: SevereWarning, UserWarning and Deprecated
* Fixed a bug where UpdateSecret, which is deprecated, was incorrectly indicating that it had a return type. It now properly does not have a return value.

0.1.1 (2016-12-12)
++++++++++++++++++

**New features**

* Add cascade query parameter to DeleteCredential, which allows the user to indicate if they want to delete all resources dependent on the credential as well as the credential
* Parameters are now optional when adding ADLS accounts to an ADLA account
* Fixed a bug in ADLA where the caller could not create an ADLA account with WASB storage accounts.
* Remove invalid return type from Secret creation in ADLA

**Breaking change**

* "account_name" parameter is now "name" in account operation


0.1.0 (2016-11-14)
++++++++++++++++++

* Initial Release

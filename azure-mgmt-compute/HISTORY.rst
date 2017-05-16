.. :changelog:

Release History
===============

1.0.0 (2017-05-15)
++++++++++++++++++

- Tag 1.0.0rc2 as stable (same content)

1.0.0rc2 (2017-05-12)
+++++++++++++++++++++

**Features**

- Add Compute ApiVersion 2016-03-30 (AzureStack default)

1.0.0rc1 (2017-04-11)
+++++++++++++++++++++

**Breaking Changes**

- Container service is now in it's own client ContainerServiceClient

**Features**

To help customers with sovereign clouds (not general Azure),
this version has official multi ApiVersion support for the following resource type:

- Compute: 2015-06-15 and 2016-04-30-preview

The following resource types support one ApiVersion:

- ContainerService: 2017-01-31

0.33.0 (2017-02-03)
+++++++++++++++++++

**Features**

This release adds Managed Disk to compute. This changes the default disk creation behavior
to use the new Managed Disk feature instead of Storage.

0.32.1 (2016-11-14)
+++++++++++++++++++

* Add "Kubernetes" on Containers
* Improve technical documentation

0.32.0 (2016-11-02)
+++++++++++++++++++

**Breaking change**

New APIVersion for "container" 2016-09-30.

* several parameters (e.g. "username") now dynamically check before REST calls validity 
  against a regexp. Exception will be TypeError and not CloudError anymore.

0.31.0 (2016-11-01)
+++++++++++++++++++

**Breaking change**

We renamed some "container" methods to follow Azure SDK conventions

* "container" attribute on the client is now "containers"
* "list" changed behavior, now listing containers in subscription and lost its parameter
* "list_by_resource_group" new method with the old "list" behavior

0.30.0 (2016-10-17)
+++++++++++++++++++

* Initial preview release. Based on API version 2016-03-30.


0.20.0 (2015-08-31)
+++++++++++++++++++

* Initial preview release. Based on API version 2015-05-01-preview.

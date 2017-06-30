.. :changelog:

Release History
===============

1.0.0 (2017-06-30)
++++++++++++++++++

**Features**

- Add disable_custom_https and enable_custom_https

**Breaking changes**

- Rename check_resource_usage to list_resource_usage
- list EdgeNode now returns an iterator of EdgeNode, 
  not a EdgenodeResult instance with an attribute "value" being a list of EdgeNode

0.30.3 (2017-05-15)
+++++++++++++++++++

* This wheel package is now built with the azure wheel extension

0.30.2 (2016-12-22)
+++++++++++++++++++

* Fix EdgeNode attributes content

0.30.1 (2016-12-15)
+++++++++++++++++++

* Fix list EdgeNodes method return type

0.30.0 (2016-12-14)
+++++++++++++++++++

* Initial preview release (API Version 2016-10-02)
* Major breaking changes from 0.30.0rc6

0.30.0rc6 (2016-09-02)
++++++++++++++++++++++

* Initial alpha release (API Version 2016-04-02)

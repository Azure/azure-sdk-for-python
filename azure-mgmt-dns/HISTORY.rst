.. :changelog:

Release History
===============

2.0.0rc1 (2018-03-14)
+++++++++++++++++++++

**Features**

- Add public/private zone
- Add record_sets.list_all_by_dns_zone operation
- Add zones.update operation

**Breaking changes**

- 'zone_type' is now required when creating a zone ('Public' is equivalent as previous behavior)

New API version 2018-03-01-preview

1.2.0 (2017-10-26)
++++++++++++++++++

- add record_type CAA
- remove pointless return type of delete

Api version moves from 2016-04-01 to 2017-09-01

1.1.0 (2017-10-10)
++++++++++++++++++

- Add "recordsetnamesuffix" filter parameter to list operations

1.0.1 (2017-04-20)
++++++++++++++++++

This wheel package is now built with the azure wheel extension

1.0.0 (2016-12-12)
++++++++++++++++++

* Initial release

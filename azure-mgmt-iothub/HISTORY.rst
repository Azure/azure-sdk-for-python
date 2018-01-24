.. :changelog:

Release History
===============

0.4.0 (2017-10-11)
++++++++++++++++++

**Features**

- New API version 2017-07-01. This is a backward compatible.
- Add "if_match" parameter when applicable
- Add certificates operation group
- Add list available operations method
- Add "storage_containers" attribute to RoutingEndpoints

0.3.0 (2017-06-13)
++++++++++++++++++

**Features**

- New API version 2017-01-19. This is a backward compatible.
- Adding "routing" information

0.2.2 (2017-04-20)
++++++++++++++++++

**Bugfixes**

- Fix possible deserialization error, but updating from dict<str, enumtype> to dict<str, str> when applicable

**Notes**

- This wheel package is now built with the azure wheel extension

0.2.1 (2016-12-16)
++++++++++++++++++

**Bugfixes**

* Fix #920 - Invalid return type for `list_event_hub_consumer_groups`

0.2.0 (2016-12-12)
++++++++++++++++++

**Bugfixes**

* Better parameters checking (change exception from CloudError to TypeError)
* Date parsing fix (incorrect None date)
* CreateOrUpdate random exception fix

0.1.0 (2016-08-12)
++++++++++++++++++

* Initial Release

.. :changelog:

Release History
===============

0.21.1 (2017-04-27)
+++++++++++++++++++

This wheel package is now built with the azure wheel extension

0.21.0 (2017-01-13)
-------------------

**Features**

* `str` messages are now accepted in Python 3 and will be encoded in 'utf-8' (will not raise TypeError anymore)
* `broker_properties` can now be defined as a dict, and not only a JSON `str`. datetime, int, float and boolean are converted.
* #902 add `send_topic_message_batch` operation (takes an iterable of messages)
* #902 add `send_queue_message_batch` operation (takes an iterable of messages)

**Bugfixes**

* #820 the code is now more robust to unexpected changes on the SB RestAPI

0.20.3 (2016-08-11)
-------------------

**News**

* #547 Add get dead letter path static methods to Python
* #513 Add renew lock

**Bugfixes**

* #628 Fix custom properties with double quotes

0.20.2 (2016-06-28)
-------------------

**Bugfixes**

* New header in Rest API which breaks the SDK #658 #657

0.20.1 (2015-09-14)
-------------------

**News**

* Create a requests.Session() if the user doesn't pass one in.

0.20.0 (2015-08-31)
-------------------

Initial release of this package, from the split of the `azure` package.
See the `azure` package release note for 1.0.0 for details and previous
history on service bus.
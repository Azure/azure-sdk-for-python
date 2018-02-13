.. :changelog:

Release History
===============

2.0.0 (2018-02-06)
++++++++++++++++++

**Features**

- Marketplace data with and without billing period
- Price sheets data with and without billing period
- Budget CRUD operations support

**Breaking changes**
- Removing scope from usage_details, reservation summaries and details operations.

1.1.0 (2017-12-12)
++++++++++++++++++

**Features**

- Reservation summaries based on Reservation Order Id and/or ReservationId
- Reservation details based on Reservation Order Id and/or ReservationId

1.0.0 (2017-11-15)
++++++++++++++++++

**Features**

- Featuring stable api GA version 2017-11-30
- Supporting EA customers with azure consumption usage details

**Breaking changes**

- Removing support for calling usage_details.list() with 'invoice_id'. Will feature in future releases.

0.1.0 (2017-05-18)
++++++++++++++++++

* Initial Release

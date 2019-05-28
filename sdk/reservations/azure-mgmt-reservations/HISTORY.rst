.. :changelog:

Release History
===============

0.3.2 (2019-04-18)
++++++++++++++++++

**Features**

- Added operation ReservationOrderOperations.purchase
- Added operation ReservationOrderOperations.calculate

0.3.1 (2018-11-05)
++++++++++++++++++

**Features**

- Add redhat support

0.3.0 (2018-08-22)
++++++++++++++++++

**Features**

* Model Patch has a new parameter 'name'
* Enum ReservedResourceType has a new value 'cosmos_db'

0.2.1 (2018-06-14)
++++++++++++++++++

* Provide enum definitions when applicable

0.2.0 (2018-06-12)
++++++++++++++++++

**Notes**

* Changed Update Reservation API
    - Added optional InstanceFlexibility parameter
* Support for InstanceFlexibility
* Support for ReservedResourceType (VirtualMachines, SqlDatabases, SuseLinux)
* Upgrade to rest api version 2018-06-01

**Breaking change**

* Updated Get Catalog API
    - Added required parameter 'reserved_resource_type'
    - Added optional parameter 'location'
* Updated Catalog model
    - Renamed property 'capabilities' to 'sku_properties'
    - Removed properties 'size' and 'tier'
* Updated ReservationProperties model
    - Removed property 'kind'

0.1.0 (2017-11-03)
++++++++++++++++++

* Initial Release

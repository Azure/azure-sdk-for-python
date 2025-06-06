# Client Developer Doc

## Azure EventGrid Layout

The azure-eventgrid package contains both the Azure EventGrid Stamdard Tier (/legacy) and the Azure EventGrid Namespaces Tier. 

### System Events

The system events are only published under the SystemEventNames enum (/legacy/_event_mappings.py). We had a discussion with the python architect and have decided to no longer support the SystemEventNames enum. As new service System Events come in this means there is NO ACTION to be taken from the python SDK side. 

When we were maintaing the SystemEventNames enum we used the script under /swagger to output the enum list to put in the _event_mappings.py file.

Additionally, we did not release a System Events package like other languages, so there is NO ACTION for the python SDK there as well.


### Event Grid Namespaces

If there are changes to Event Grid Namespaces and we need to regenerate from the Azure.Messaging.EventGrid typespec, we can update the tsp-location.yaml and use the tsp-client to regenerate.

Further documentation on maintaining a package that contains both Swagger and TypeSpec resides [here](https://github.com/Azure/azure-sdk-for-python/wiki/Generate-Swagger-and-TypeSpec-in-Package)



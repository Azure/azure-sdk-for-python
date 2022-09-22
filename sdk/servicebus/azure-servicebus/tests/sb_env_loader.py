import functools
from devtools_testutils import PowerShellPreparer

ServiceBusPreparer = functools.partial(
    PowerShellPreparer, 'servicebus',
    service_bus_connection_str='Endpoint=sb://fakeresource.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=fakekeyfakekeyfakekeyfakekeyfakekeyfakekeyf=',
    service_bus_fully_qualified_namespace='fakeresource.servicebus.windows.net',
    service_bus_topic_name='faketopic',
    service_bus_subscription_name='fakesubscription',
    service_bus_queue_name='fakequeue',
    service_bus_sas_policy='fakesharedaccesskey',
    service_bus_sas_key='fakekeyfakekeyfakekeyfakekeyfakekeyfakekeyf=',
    service_bus_session_queue_name='fakesessionqueue',
    service_bus_session_id='fakesessionid',
    service_bus_session_queue_sas_policy='fakesessionsharedaccesskey',
    service_bus_session_queue_sas_key='fakekeyfakekeyfakekeyfakekeyfakekeyfakekeyf='
)

import functools
from devtools_testutils import PowerShellPreparer

ServiceBusPreparer = functools.partial(
    PowerShellPreparer,
    "servicebus",
    servicebus_connection_str="Endpoint=sb://fakeresource.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=fakekeyfakekeyfakekeyfakekeyfakekeyfakekeyf=",
    servicebus_fully_qualified_namespace="fakeresource.servicebus.windows.net",
    servicebus_topic_name="faketopic",
    servicebus_subscription_name="fakesubscription",
    servicebus_queue_name="fakequeue",
    servicebus_sas_policy="fakesharedaccesskey",
    servicebus_sas_key="fakekeyfakekeyfakekeyfakekeyfakekeyfakekeyf=",
    servicebus_session_queue_name="fakesessionqueue",
    servicebus_session_id="fakesessionid",
    servicebus_session_queue_sas_policy="fakesessionsharedaccesskey",
    servicebus_session_queue_sas_key="fakekeyfakekeyfakekeyfakekeyfakekeyfakekeyf=",
)

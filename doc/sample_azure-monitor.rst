Azure Monitor
=============

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the Monitor client
-------------------------

The following code creates an instance of the client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <quickstart_authentication>`
for details on handling Azure Active Directory authentication with the Python SDK, and creating a ``Credentials`` instance.

.. code:: python

    from azure.monitor import MonitorClient
    from azure.common.credentials import UserPassCredentials

    # Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
    
    # See above for details on creating different types of AAD credentials
    credentials = UserPassCredentials(
        'user@domain.com',  # Your user
        'my_password',      # Your password
    )

    client = MonitorClient(
        credentials,
        subscription_id
    )

Registration
------------

Some operations in the ARM APIs require a one-time registration of the
provider with your subscription.

Use the following code to do the registration. You can use the same
credentials you created in the previous section.

.. code:: python

    from azure.mgmt.resource.resources import ResourceManagementClient

    resource_client = ResourceManagementClient(
        credentials,
        subscription_id
    )
    resource_client.providers.register('Microsoft.Insights')
    
You also might need to add the "Monitoring Contributor Service Role" role
to your credentials. See here to do it using the Python CLI: 
https://docs.microsoft.com/cli/azure/role/assignment

Get the Activity Log
--------------------

This sample gets the logs from the ActivityLog of today for resource group ResourceGroupName, 
filtering the attributes to get only the "eventName" and "operationName".

A complete list of available keywords for filters and available attributes is available
here: https://msdn.microsoft.com/library/azure/dn931934.aspx

.. code:: python

    import datetime

    today = datetime.datetime.now().date()
    filter = " and ".join([
        "eventTimestamp ge {}".format(today),
        "resourceGroupName eq 'ResourceGroupName'"
    ])
    select = ",".join([
        "eventName",
        "operationName"
    ])
    
    activity_logs = client.activity_logs.list(
        filter=filter,
        select=select
    )
    for log in activity_logs:
        # assert isinstance(log, azure.monitor.models.EventData)
        print(" ".join([
            log.event_name.localized_value,
            log.operation_name.localized_value
        ]))

Metrics
-------

This sample get the metrics of a resource on Azure (VMs, etc.).

A complete list of available keywords for filters is available
here: https://msdn.microsoft.com/en-us/library/azure/mt743622.aspx

.. code:: python

    import datetime

    # Get the ARM id of your resource. You might chose to do a "get"
    # using the according management or to build the URL directly
    # Example for a ARM VM
    resource_id = (
        "subscriptions/{}/"
        "resourceGroups/{}/"
        "providers/Microsoft.Compute/virtualMachines/{}"
    ).format(subscription_id, resource_group_name, vm_name)

    # You can get the available metrics of this specific resource
    for metric in client.metric_definitions.list(resource_id):
        # azure.monitor.models.MetricDefinition
        print("{}: id={}, unit={}".format(
            metric.name.localized_value,
            metric.name.value,
            metric.unit
        ))

    # Example of result for a VM:
    # Percentage CPU: id=Percentage CPU, unit=Unit.percent
    # Network In: id=Network In, unit=Unit.bytes
    # Network Out: id=Network Out, unit=Unit.bytes
    # Disk Read Bytes: id=Disk Read Bytes, unit=Unit.bytes
    # Disk Write Bytes: id=Disk Write Bytes, unit=Unit.bytes
    # Disk Read Operations/Sec: id=Disk Read Operations/Sec, unit=Unit.count_per_second
    # Disk Write Operations/Sec: id=Disk Write Operations/Sec, unit=Unit.count_per_second

    # Get CPU total of yesterday for this VM, by hour

    today = datetime.datetime.now().date()
    yesterday = today - datetime.timedelta(days=1)

    filter = " and ".join([
        "name.value eq 'Percentage CPU'",
        "aggregationType eq 'Total'",
        "startTime eq {}".format(yesterday),
        "endTime eq {}".format(today),
        "timeGrain eq duration'PT1H'"
    ])

    metrics_data = client.metrics.list(
        resource_id,
        filter=filter
    )

    for item in metrics_data:
        # azure.monitor.models.Metric
        print("{} ({})".format(item.name.localized_value, item.unit.name))
        for data in item.data:
            # azure.monitor.models.MetricData
            print("{}: {}".format(data.time_stamp, data.total))

    # Example of result:
    # Percentage CPU (percent)
    # 2016-11-16 00:00:00+00:00: 72.0
    # 2016-11-16 01:00:00+00:00: 90.59
    # 2016-11-16 02:00:00+00:00: 60.58
    # 2016-11-16 03:00:00+00:00: 65.78
    # 2016-11-16 04:00:00+00:00: 43.96
    # 2016-11-16 05:00:00+00:00: 43.96
    # 2016-11-16 06:00:00+00:00: 114.9
    # 2016-11-16 07:00:00+00:00: 45.4
    # 2016-11-16 08:00:00+00:00: 57.59
    # 2016-11-16 09:00:00+00:00: 67.85
    # 2016-11-16 10:00:00+00:00: 76.36
    # 2016-11-16 11:00:00+00:00: 87.41
    # 2016-11-16 12:00:00+00:00: 67.53
    # 2016-11-16 13:00:00+00:00: 64.78
    # 2016-11-16 14:00:00+00:00: 66.55
    # 2016-11-16 15:00:00+00:00: 69.82
    # 2016-11-16 16:00:00+00:00: 96.02
    # 2016-11-16 17:00:00+00:00: 272.52
    # 2016-11-16 18:00:00+00:00: 96.41
    # 2016-11-16 19:00:00+00:00: 83.92
    # 2016-11-16 20:00:00+00:00: 95.57
    # 2016-11-16 21:00:00+00:00: 146.73
    # 2016-11-16 22:00:00+00:00: 73.86
    # 2016-11-16 23:00:00+00:00: 84.7

IoTHub Management
=================

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <quickstart_authentication>`
for details on handling Azure Active Directory authentication with the Python SDK, and creating a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.iothub import IotHubClient
    from azure.common.credentials import UserPassCredentials

    # Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
    
    # See above for details on creating different types of AAD credentials
    credentials = UserPassCredentials(
        'user@domain.com',  # Your user
        'my_password',      # Your password
    )

    iothub_client = IotHubClient(
        credentials,
        subscription_id
    )

Create an IoTHub
---------------

.. code:: python

	async_iot_hub = iothub_client.iot_hub_resource.create_or_update(
		'MyResourceGroup',
		'MyIoTHubAccount',
		{
			'location': 'westus',
			'subscriptionid': subscription_id,
			'resourcegroup': 'MyResourceGroup',
			'sku': {
			  'name': 'S1',
			  'capacity': 2
			},
			'properties': {
			  'enable_file_upload_notifications': False,
			  'operations_monitoring_properties': {
				'events': {
				  "C2DCommands": "Error",
				  "DeviceTelemetry": "Error",
				  "DeviceIdentityOperations": "Error",
				  "Connections": "Information"
				}
			  },
			  "features": "None",
			}
		}
	)
	iothub = async_iot_hub.result() # Blocking wait for creation
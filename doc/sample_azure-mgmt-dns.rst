DNS Management
==============

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the management client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <quickstart_authentication>`
for details on handling Azure Active Directory authentication with the Python SDK, and creating a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.dns import DnsManagementClient
    from azure.common.credentials import UserPassCredentials

    # Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
    
    # See above for details on creating different types of AAD credentials
    credentials = UserPassCredentials(
        'user@domain.com',  # Your user
        'my_password',      # Your password
    )

    dns_client = DnsManagementClient(
        credentials,
        subscription_id
    )

Create DNS zone
---------------

.. code:: python

	# The only valid value is 'global', otherwise you will get a:
	# The subscription is not registered for the resource type 'dnszones' in the location 'westus'.
	zone = dns_client.zones.create_or_update(
		'MyResourceGroup',
		'pydns.com',
		{
			'zone_type': 'Public', # or Private
			'location': 'global'
		}
	)
	
Create a Record Set
-------------------

.. code:: python

	record_set = dns_client.record_sets.create_or_update(
		'MyResourceGroup',
		'pydns.com',
		'MyRecordSet',
		'A',
		{
			 "ttl": 300,
			 "arecords": [
				 {
					"ipv4_address": "1.2.3.4"
				 },
				 {
					"ipv4_address": "1.2.3.5"
				 }
			 ]
		}
	)

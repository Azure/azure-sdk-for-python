Commerce - Billing API
======================


Create the commerce client
----------------------------

The following code creates an instance of the management client.

You will need to provide your ``subscription_id`` which can be retrieved
from `your subscription list <https://manage.windowsazure.com/#Workspaces/AdminTasks/SubscriptionMapping>`__.

See :doc:`Resource Management Authentication <resourcemanagementauthentication>`
for details on getting a ``Credentials`` instance.

.. code:: python

    from azure.mgmt.commerce import UsageManagementClient

    # TODO: Replace this with your subscription id
    subscription_id = '33333333-3333-3333-3333-333333333333'
    # TODO: See above how to get a Credentials instance
    credentials = ...

    commerce_client = UsageManagementClient(
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
    resource_client.providers.register('Microsoft.Commerce')

Get rate card
-------------

.. code:: python

    # OfferDurableID: https://azure.microsoft.com/en-us/support/legal/offer-details/
    rate = self.commerce_client.rate_card.get(
        "OfferDurableId eq 'MS-AZR-0062P' and Currency eq 'USD' and Locale eq 'en-US' and RegionInfo eq 'US'"
    )

Get Usage
---------

.. code:: python

    from datetime import date, timedelta

    # Takes onky dates in full ISO8601 with 'T00:00:00Z'
    usage_list = self.commerce_client.usage_aggregates.list(
        str(date.today() - timedelta(days=1))+'T00:00:00Z',
        str(date.today())+'T00:00:00Z'
    )

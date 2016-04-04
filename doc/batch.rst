Batch
=====

Create the batch client
-----------------------

The following code creates an instance of the batch client.

See :doc:`Batch Management Client <resourcemanagementbatch>`
if you want to get from ARM your primary key.

.. code:: python

    from azure.batch import BatchServiceClient, BatchServiceClientConfiguration
    from azure.batch.batch_auth import SharedKeyCredentials

    credentials = SharedKeyCredentials(AZURE_BATCH_ACCOUNT, primary_key)
    batch_client = BatchServiceClient(
        BatchServiceClientConfiguration(
            credentials,
        )
    )

Do something
------------

Example to come
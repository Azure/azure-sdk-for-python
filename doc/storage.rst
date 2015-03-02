Usage
=====

Table Storage
-------------

To ensure a table exists, call **create\_table**:

.. code:: python

    from azure.storage import TableService
    ts = TableService(account_name, account_key)
    ts.create_table('tasktable')

A new entity can be added by calling **insert\_entity**:

.. code:: python

    from datetime import datetime
    ts = TableService(account_name, account_key)
    ts.create_table('tasktable')
    ts.insert_entity(
         'tasktable',
         {
            'PartitionKey' : 'tasksSeattle',
            'RowKey': '1',
            'Description': 'Take out the trash',
            'DueDate': datetime(2011, 12, 14, 12) 
        }
    )

The method **get\_entity** can then be used to fetch the entity that was
just inserted:

.. code:: python

    ts = TableService(account_name, account_key)
    entity = ts.get_entity('tasktable', 'tasksSeattle', '1')

Blob Storage
------------

The **create\_container** method can be used to create a container in
which to store a blob:

.. code:: python

    from azure.storage import BlobService
    blob_service = BlobService(account_name, account_key)
    blob_service.create_container('images')

To upload a file 'uploads/image.png' from disk to a blob named
'image.png', the method **put\_block\_blob\_from\_path** can be used:

.. code:: python

    from azure.storage import BlobService
    blob_service = BlobService(account_name, account_key)
    blob_service.put_block_blob_from_path('images', 'image.png', 'uploads/image.png')

To upload an already opened file to a blob named 'image.png', the method
**put\_block\_blob\_from\_file** can be used instead:

.. code:: python

    with open('uploads/image.png') as file:
      blob_service.put_block_blob_from_file('images', 'image.png', file)

To upload unicode text, use **put\_block\_blob\_from\_text** which will
do the conversion to bytes using the specified encoding.

To upload bytes, use **put\_block\_blob\_from\_bytes**.

To download a blob named 'image.png' to a file on disk
'downloads/image.png', where the 'downloads' folder already exists, the
**get\_blob\_to\_path** method can be used:

.. code:: python

    from azure.storage import BlobService
    blob_service = BlobService(account_name, account_key)
    blob = blob_service.get_blob_to_path('images', 'image.png', 'downloads/image.png')

To download to an already opened file, use **get\_blob\_to\_file**.

To download to an array of bytes, use **get\_blob\_to\_bytes**.

To download to unicode text, use **get\_blob\_to\_text**.

Storage Queues
--------------

The **create\_queue** method can be used to ensure a queue exists:

.. code:: python

    from azure.storage import QueueService
    queue_service = QueueService(account_name, account_key)
    queue_service.create_queue('taskqueue')

The **put\_message** method can then be called to insert the message
into the queue:

.. code:: python

    from azure.storage import QueueService
    queue_service = QueueService(account_name, account_key)
    queue_service.put_message('taskqueue', 'Hello world!')

It is then possible to call the **get\_messages** method, process the
message and then call **delete\_message** with the message id and
receipt. This two-step process ensures messages don't get lost when they
are removed from the queue.

.. code:: python

    from azure.storage import QueueService
    queue_service = QueueService(account_name, account_key)
    messages = queue_service.get_messages('taskqueue')
    queue_service.delete_message('taskqueue', messages[0].message_id, messages[0].pop_receipt)

    
Need Help?
==========

Be sure to check out the Microsoft Azure `Developer Forums on Stack
Overflow <http://go.microsoft.com/fwlink/?LinkId=234489>`__ if you have
trouble with the provided code.

Contribute Code or Provide Feedback
===================================

If you would like to become an active contributor to this project please
follow the instructions provided in `Microsoft Azure Projects
Contribution
Guidelines <http://windowsazure.github.com/guidelines.html>`__.

If you encounter any bugs with the library please file an issue in the
`Issues <https://github.com/Azure/azure-sdk-for-python/issues>`__
section of the project.

Learn More
==========

`Microsoft Azure Python Developer
Center <http://azure.microsoft.com/en-us/develop/python/>`__
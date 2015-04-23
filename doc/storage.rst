Usage
=====

Table Storage
-------------

To ensure a table exists, call **create\_table**:

.. code:: python

    from azure.storage import TableService
    table_service = TableService(account_name, account_key)
    table_service.create_table('tasktable')

A new entity can be added by calling **insert\_entity**:

.. code:: python

    from datetime import datetime
    table_service = TableService(account_name, account_key)
    table_service.create_table('tasktable')
    table_service.insert_entity(
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

    table_service = TableService(account_name, account_key)
    entity = table_service.get_entity('tasktable', 'tasksSeattle', '1')

If you want to give access to a table to a third party without revealing
your account key, you can use a shared access signature. The shared
access signature includes an access policy, with optional start, expiry
and permission.

To generate a shared access signature, use:

.. code:: python

    from azure.storage import TableService, AccessPolicy, SharedAccessPolicy, TableSharedAccessPermissions
    table_service = TableService(account_name, account_key)
    ap = AccessPolicy(
        expiry='2016-10-12',
        permission=TableSharedAccessPermissions.QUERY,
    )
    sas_token = table_service.generate_shared_access_signature(
        'tasktable',
        SharedAccessPolicy(ap),
    )

Alternatively, you can define a named access policy on the server:

.. code:: python

    from azure.storage import TableService, SharedAccessPolicy, TableSharedAccessPermissions, SignedIdentifier
    table_service = TableService(account_name, account_key)

    policy_name = 'readonlyvaliduntilnextyear'

    si = SignedIdentifier()
    si.id = policy_name
    si.access_policy.expiry = '2016-01-01'
    si.access_policy.permission = TableSharedAccessPermissions.QUERY
    identifiers = SignedIdentifiers()
    identifiers.signed_identifiers.append(si)

    table_service.set_queue_acl(
        table_name='tasktable',
        signed_identifiers=identifiers,
    )

And generate a shared access signature for that named access policy:

.. code:: python

    sas_token = table_service.generate_shared_access_signature(
        'tasktable',
        SharedAccessPolicy(signed_identifier=policy_name),
    )

Using a predefined access policy has the advantage that it can be
revoked from the server side. To revoke, call ``set_table_acl`` with the
new list of signed identifiers. You can pass in ``None`` or an empty
list to remove all.

.. code:: python

    table_service.set_table_acl(
        table_name='tasktable',
        signed_identifiers=None,
    )

The third party can use the shared access signature token to
authenticate, instead of an account key:

.. code:: python

    from azure.storage import TableService
    table_service = TableService(account_name, sas_token=sas_token)
    entity = table_service.get_entity('tasktable', 'tasksSeattle', '1')


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
    blob_service.put_block_blob_from_path(
        'images',
        'image.png',
        'uploads/image.png',
        max_connections=5,
    )

The **max\_connections** parameter is optional, and lets you use multiple
parallel connections to perform uploads and downloads.  This parameter is
available on the various upload and download methods described below.

To upload an already opened file to a blob named 'image.png', the method
**put\_block\_blob\_from\_file** can be used instead. The **count** parameter
is optional, but you will get better performance if you specify it. This
indicates how many bytes you want read from the file and uploaded to the blob.

.. code:: python

    with open('uploads/image.png') as file:
        blob_service.put_block_blob_from_file(
            'images',
            'image.png',
            file,
            count=50000,
            max_connections=4,
        )

To upload unicode text, use **put\_block\_blob\_from\_text** which will
do the conversion to bytes using the specified encoding.

To upload bytes, use **put\_block\_blob\_from\_bytes**.

To download a blob named 'image.png' to a file on disk
'downloads/image.png', where the 'downloads' folder already exists, the
**get\_blob\_to\_path** method can be used:

.. code:: python

    from azure.storage import BlobService
    blob_service = BlobService(account_name, account_key)
    blob = blob_service.get_blob_to_path(
        'images',
        'image.png',
        'downloads/image.png',
        max_connections=8,
    )

To download to an already opened file, use **get\_blob\_to\_file**.

To download to an array of bytes, use **get\_blob\_to\_bytes**.

To download to unicode text, use **get\_blob\_to\_text**.

You can set public access to blobs in a container when the container is
created:

.. code:: python

    blob_service.create_container(
        container_name='images',
        x_ms_blob_public_access='blob',
    )

Or after it's created:

.. code:: python

    blob_service.set_container_acl(
        container_name='images',
        x_ms_blob_public_access='blob',
    )

If ``x_ms_blob_public_access`` is set to ``'blob'``:

-  Blob data within this container can be read via anonymous request,
   but container data is not available. Clients cannot enumerate blobs
   within the container via anonymous request.

If it's set to ``'container'``:

-  Container and blob data can be read via anonymous request. Clients
   can enumerate blobs within the container via anonymous request, but
   cannot enumerate containers within the storage account.

The default is ``None``:

-  Container and blob data can be read by the account owner only.

You can use ``BlobService`` to access public containers and blobs by
omitting the ``account_key`` parameter:

.. code:: python

    from azure.storage import BlobService
    blob_service = BlobService(account_name)
    blob = blob_service.get_blob_to_path(
        'images',
        'image.png',
        'downloads/image.png',
        max_connections=8,
    )

You can get a full URL for the blob (for use in a web browser, etc):

.. code:: python

    from azure.storage import BlobService
    blob_service = BlobService(account_name)
    url = blob_service.make_blob_url(
        container_name='images',
        blob_name='image.png',
    )
    # url is: https://<account_name>.blob.core.windows.net/images/image.png

If you want to give access to a container or blob to a third party
without revealing your account key or making the container or blob
public, you can use a shared access signature. The shared access
signature includes an access policy, with optional start, expiry and
permission.

To generate a shared access signature, use:

.. code:: python

    from azure.storage import BlobService, AccessPolicy, SharedAccessPolicy, BlobSharedAccessPermissions
    blob_service = BlobService(account_name, account_key)
    ap = AccessPolicy(
        expiry='2016-10-12',
        permission=BlobSharedAccessPermissions.READ,
    )
    sas_token = blob_service.generate_shared_access_signature(
        container_name='images',
        blob_name='image.png',
        shared_access_policy=SharedAccessPolicy(ap),
    )

Note that a shared access signature can be created for a container, just
pass ``None`` (which is the default) for the ``blob_name`` parameter.

Alternatively, you can define a named access policy on the server:

.. code:: python

    from azure.storage import BlobService, AccessPolicy, SharedAccessPolicy, BlobSharedAccessPermissions, SignedIdentifier
    blob_service = BlobService(account_name, account_key)

    policy_name = 'readonlyvaliduntilnextyear'

    si = SignedIdentifier()
    si.id = policy_name
    si.access_policy.expiry = '2016-01-01'
    si.access_policy.permission = BlobSharedAccessPermissions.READ
    identifiers = SignedIdentifiers()
    identifiers.signed_identifiers.append(si)

    blob_service.set_container_acl(
        container_name='images',
        signed_identifiers=identifiers,
    )

And generate a shared access signature for that named access policy:

.. code:: python

    sas_token = blob_service.generate_shared_access_signature(
        container_name='images',
        blob_name='image.png',
        shared_access_policy=SharedAccessPolicy(signed_identifier=policy_name),
    )

Using a predefined access policy has the advantage that it can be
revoked from the server side. To revoke, call ``set_container_acl`` with
the new list of signed identifiers. You can pass in ``None`` or an empty
list to remove all.

.. code:: python

    blob_service.set_container_acl(
        container_name='images',
        signed_identifiers=None,
    )

The third party can use the shared access signature token to
authenticate, instead of an account key:

.. code:: python

    from azure.storage import BlobService
    blob_service = BlobService(account_name, sas_token=sas_token)
    blob = blob_service.get_blob_to_path(
        'images',
        'image.png',
        'downloads/image.png',
        max_connections=8,
    )

You can get a full URL for the blob (for use in a web browser, etc):

.. code:: python

    from azure.storage import BlobService
    blob_service = BlobService(account_name)
    url = blob_service.make_blob_url(
        container_name='images',
        blob_name='image.png',
        sas_token=sas_token,
    )


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

If you want to give access to a queue to a third party without revealing
your account key, you can use a shared access signature. The shared
access signature includes an access policy, with optional start, expiry
and permission.

To generate a shared access signature, use:

.. code:: python

    from azure.storage import QueueService, AccessPolicy, SharedAccessPolicy, QueueSharedAccessPermissions
    queue_service = QueueService(account_name, account_key)
    ap = AccessPolicy(
        expiry='2016-10-12',
        permission=QueueSharedAccessPermissions.READ,
    )
    sas_token = queue_service.generate_shared_access_signature(
        'taskqueue',
        SharedAccessPolicy(ap),
    )

Alternatively, you can define a named access policy on the server:

.. code:: python

    from azure.storage import QueueService, SharedAccessPolicy, QueueSharedAccessPermissions, SignedIdentifier
    queue_service = QueueService(account_name, account_key)

    policy_name = 'readonlyvaliduntilnextyear'

    si = SignedIdentifier()
    si.id = policy_name
    si.access_policy.expiry = '2016-01-01'
    si.access_policy.permission = QueueSharedAccessPermissions.READ
    identifiers = SignedIdentifiers()
    identifiers.signed_identifiers.append(si)

    queue_service.set_queue_acl(
        queue_name='taskqueue',
        signed_identifiers=identifiers,
    )

And generate a shared access signature for that named access policy:

.. code:: python

    sas_token = queue_service.generate_shared_access_signature(
        'taskqueue',
        SharedAccessPolicy(signed_identifier=policy_name),
    )

Using a predefined access policy has the advantage that it can be
revoked from the server side. To revoke, call ``set_queue_acl`` with the
new list of signed identifiers. You can pass in ``None`` or an empty
list to remove all.

.. code:: python

    queue_service.set_container_acl(
        queue_name='taskqueue',
        signed_identifiers=None,
    )

The third party can use the shared access signature token to
authenticate, instead of an account key:

.. code:: python

    from azure.storage import QueueService
    queue_service = QueueService(account_name, sas_token=sas_token)
    messages = queue_service.peek_messages('taskqueue')


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
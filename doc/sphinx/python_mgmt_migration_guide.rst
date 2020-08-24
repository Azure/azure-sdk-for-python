Migration Guide - Resource Management
=====================================

Guide for migrating to the next generation of Azure Python SDK for Management Libraries
---------------------------------------------------------------------------------------

This document is intended for users that are familiar with an older
version of the Python SDK for managment libraries and wish to migrate
their application to the next version of Azure resource management
libraries

For users new to the Python SDK for resource management libraries,
please see the `quickstart
guide <http://aka.ms/azure-sdk-python-mgmt>`__

Table of contents
-----------------

-  `Prerequisites <#prerequisites>`__
-  `Updated Python Packages <#updated-python-packages>`__
-  `General Changes <#general-changes>`__
-  `Authentication <#authentication>`__
-  `Client API Changes <#client-api-changes>`__
-  `Additional Samples <#additional-samples>`__

Prerequisites
-------------

-  Active Azure subscription
-  Python 2.7 or 3.5+

Updated Python Packages
-----------------------

Currently, all next-generation Python SDK management client libraries
are in Public Preview. The preview version SDK will be contain a ``b``
in its version to number to indicate that it's a beta release (e.g.
``17.0.0b1``). The versioning information can be found on the release
history page of each Azure service on pypi.org. Take Azure Compute
service for example, the release history can be found at
`https://pypi.org/project/azure-mgmt-compute/17.0.0b1/history <https://pypi.org/project/azure-mgmt-compute/17.0.0b1/#history>`__

You can also refer to the `this
site <https://azure.github.io/azure-sdk/releases/latest/mgmt/python.html>`__
to see all the latest Python packages.

Please install the package based on the beta version number, for
example, to install the latest preview package for Compute, please use:
``pip install azure-mgmt-compute==17.0.0b1``

General Changes
---------------

The latest Azure Python SDK for management libraries is a result of our
efforts to create a resource management client library that is
user-friendly and idiomatic to the Python ecosystem.

While conforming to the `new Azure SDK Design Guidelines for
Python <https://azure.github.io/azure-sdk/python_introduction.html>`__,
we have tried our best to minimize the breaking changes. Most of the API
signatures have stayed the same to offer user an easier migration
experience.

The important breaking changes are listed in the following sections:

Authentication
~~~~~~~~~~~~~~

In old version, ``ServicePrincipalCredentials`` in ``azure.common`` is
used for authenticating to Azure and creating a service client

In new version, in order to provide an unified authentication based on
Azure Identity for all Azure SDKs, the authentication mechanism has been
re-designed and replaced by ``azure-identity`` library

To use the new ``azure-identity`` authentication mechanism, please use
``pip install azure-identity`` to install the package

To the show the code snippets for the change:

**In old version**

.. code:: python

    import azure.mgmt.compute
    from azure.common.credentials import ServicePrincipalCredentials

    credentials = ServicePrincipalCredentials(
        client_id=client_id,
        secret=client_secret,
        tenant=tenant_id
    )
    compute_client = azure.mgmt.compute.ComputeManagementClient(credentials=credentials, subscription_id=self.subscription_id)

**Equivalent in new version**

.. code:: python

    import azure.mmgt.compute
    from azure.identity import ClientSecretCredential

    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        tenant_id=tenant_id
    )
    compute_client = azure.mgmt.compute.ComputeManagementClient(credential=credential, subscription_id=self.subscription_id)

For detailed information on the benefits of using the new authentication
classes, please refer to `this
page <https://docs.microsoft.com/azure/developer/python/azure-sdk-authenticate?view=azure-python&tabs=cmd>`__

Client API Changes
------------------

Most of the API has stayed the same to provide an easier migration
experience. There is a minor change regarding the async operations

Async Operations Change
~~~~~~~~~~~~~~~~~~~~~~~

To differentiate between asynchronous and synchronous API operations in
the new version, an explicit ``begin_`` prefix is added for all the
async APIs operations (this includes operations where the user gets a
``202`` response code or needs to call ``.result()`` explicitly to get
the response)

To show an example (creating virtual machine):

**In old version**

.. code:: python

    result = self.compute_client.virtual_machines.create_or_update(
        group_name,
        vm_name,
        parameters
    )
    result = result.result()

**Equivalent in new version**

.. code:: python

    result = self.compute_client.virtual_machines.begin_create_or_update(
        group_name,
        vm_name,
        parameters
    )
    vm = result.result()

Additional Samples
------------------

More samples can be found at : 

- `Quickstart for new version of SDK <http://aka.ms/azure-sdk-python-mgmt>`__ 
- `Code Samples for Resource Management Libraries <https://docs.microsoft.com/samples/browse/?languages=python&term=Getting%20started%20-%20Managing>`__
- `Authentication Documentation <https://docs.microsoft.com/azure/developer/python/azure-sdk-authenticate?view=azure-python&tabs=cmd>`__

Need help?
----------

If you have encountered an issue during migration, please file an issue
via `Github
Issues <https://github.com/Azure/azure-sdk-for-python/issues>`__ and
make sure you add the "Preview" label to the issue

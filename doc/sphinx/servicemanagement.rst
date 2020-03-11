Service Management
==================

Usage
-----

Set-up certificates
~~~~~~~~~~~~~~~~~~~

You will need two certificates, one for the server (a .cer file) and one for
the client (a .pem file).

Using the Azure .PublishSettings certificate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can download your Azure publish settings file and use the certificate that
is embedded in that file to create the client certificate. The server
certificate already exists, so you won't need to upload one.

To do this, download your `publish settings <http://go.microsoft.com/fwlink/?LinkID=301775>`__
then use this code to create the .pem file.

.. code:: python

    from azure.servicemanagement import get_certificate_from_publish_settings

    subscription_id = get_certificate_from_publish_settings(
        publish_settings_path='MyAccount.PublishSettings',
        path_to_write_certificate='mycert.pem',
        subscription_id='00000000-0000-0000-0000-000000000000',
    )

The subscription id parameter is optional. If there are more than one
subscription in the publish settings, the first one will be used.

Creating and uploading new certificate with OpenSSL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create the .pem file using `OpenSSL <http://www.openssl.org>`__, execute this:

.. code:: shell

    openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mycert.pem -out mycert.pem

To create the .cer certificate, execute this:

.. code:: shell

    openssl x509 -inform pem -in mycert.pem -outform der -out mycert.cer

After you have created the certificate, you will need to upload the .cer
file to Microsoft Azure via the "Upload" action of the "Settings" tab of
the `management portal <http://manage.windowsazure.com>`__.

Initialization
~~~~~~~~~~~~~~

To initialize the management service, pass in your subscription id and
the path to the .pem file.

.. code:: python

    from azure.servicemanagement import ServiceManagementService
    subscription_id = '00000000-0000-0000-0000-000000000000'
    cert_file = 'mycert.pem'
    sms = ServiceManagementService(subscription_id, cert_file)

List Available Locations
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    locations = sms.list_locations()
    for location in locations:
        print(location.name)

Create a Storage Service
~~~~~~~~~~~~~~~~~~~~~~~~

To create a storage service, you need a name for the service (between 3
and 24 lowercase characters and unique within Microsoft Azure), a label
(up to 100 characters, automatically encoded to base-64), and either a
location or an affinity group.

.. code:: python

    name = "mystorageservice"
    desc = name
    label = name
    location = 'West US'

    result = sms.create_storage_account(name, desc, label, location=location)

Create a Cloud Service
~~~~~~~~~~~~~~~~~~~~~~

A cloud service is also known as a hosted service (from earlier versions
of Microsoft Azure). The **create\_hosted\_service** method allows you
to create a new hosted service by providing a hosted service name (which
must be unique in Microsoft Azure), a label (automatically encoded to
base-64), and the location *or* the affinity group for your service.

.. code:: python

    name = "myhostedservice"
    desc = name
    label = name
    location = 'West US'

    result = sms.create_hosted_service(name, label, desc, location=location)

Create a Deployment
~~~~~~~~~~~~~~~~~~~

To make a new deployment to Azure you must store the package file in a
Microsoft Azure Blob Storage account under the same subscription as the
hosted service to which the package is being uploaded. You can create a
deployment package with the `Microsoft Azure PowerShell
cmdlets <https://docs.microsoft.com/en-us/powershell/azure/?view=azps-3.2.0>`__,
or with the `cspack commandline
tool <https://docs.microsoft.com/en-us/azure/cloud-services/cloud-services-model-and-package#servicepackagecspkg>`__.

.. code:: python

    service_name = "myhostedservice"
    deployment_name = "v1"
    slot = 'Production'
    package_url = "URL_for_.cspkg_file"
    configuration = base64.b64encode(open(file_path, 'rb').read('path_to_.cscfg_file'))
    label = service_name

    result = sms.create_deployment(service_name,
                         slot,
                         deployment_name,
                         package_url,
                         label,
                         configuration)

    operation = sms.get_operation_status(result.request_id)
    print('Operation status: ' + operation.status)

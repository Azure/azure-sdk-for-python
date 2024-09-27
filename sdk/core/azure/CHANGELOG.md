# Disclaimer

Starting with v5.0.0, this package cannot be installed anymore, please install individual packages.

## 2017-05-16 azure 2.0.0

**Disclaimer**

Starting with this release, we fixed several packaging issues to improve our package generation system:

- Uninstalling of packages using "pip uninstall" now works properly (#1150)
- setuptools install of "azure" works properly (#728)

Update from 2.0.0rc6 *might* work, but we strongly suggest creating a fresh virtual environment.

**Features**

***CLI configuration***

You can now execute your SDK script using the configuration of the [AzureCLI](https://github.com/Azure/azure-cli)

Example::

     from azure.common.client_factory import get_client_from_cli_profile
     from azure.mgmt.compute import ComputeManagementClient
     client = get_client_from_cli_profile(ComputeManagementClient)
     client.virtual_machines.get('rg', 'vm')

Configuration from the CLI is:

- [az login](https://docs.microsoft.com/cli/azure/authenticate-azure-cli): access to credentials
- [az account set --subscriptions](https://docs.microsoft.com/cli/azure/manage-azure-subscriptions-azure-cli): access to subscription_id
- [az cloud set --name](https://docs.microsoft.com/cli/azure/cloud#set): access to base_url (sovereign cloud, Government, Germany, etc.)

Note: CLI and SDK are versioned separately. We do recommend using two different virtual environments. Information will be shared
automatically since the CLI saves it in the $HOME folder. You do need the `azure-cli-core` package in your SDK environment to use this feature.

***Multiple API Version support***

To help support of sovereign cloud (i.e. AzureStack, Azure Government, Azure Germany, Microsoft Azure operated by 21Vianet - China), the following packages
now officially support several API versions in the same package:

-  [azure-mgmt-resource v1.1.x](https://pypi.python.org/pypi/azure-mgmt-resource/1.1.0)
-  [azure-mgmt-compute v1.0.x](https://pypi.python.org/pypi/azure-mgmt-compute/1.0.0)
-  [azure-mgmt-network v1.0.x](https://pypi.python.org/pypi/azure-mgmt-network/1.0.0)
-  [azure-mgmt-storage v1.0.x](https://pypi.python.org/pypi/azure-mgmt-storage/1.0.0)

Please refer to the PyPI page of these packages for supported ApiVersion.

**Breaking changes**

The Azure SDK for Python now has too many services to provide an unique ChangeLog. Please refer to each package's HISTORY.txt for details compared to 2.0.0rc6.

The complete list of packages installed is:

-  [azure-batch v3.0.0](https://pypi.python.org/pypi/azure-batch/3.0.0)
-  [azure-datalake-store v0.0.x](https://pypi.python.org/pypi/azure-datalake-store/0.0.9)
-  [azure-graphrbac v0.30.x](https://pypi.python.org/pypi/azure-graphrbac/0.30.0)
-  [azure-keyvault v0.3.x](https://pypi.python.org/pypi/azure-keyvault/0.3.3)
-  [azure-servicebus v0.21.x](https://pypi.python.org/pypi/azure-servicebus/0.21.1)
-  [azure-servicefabric v5.6.130](https://pypi.python.org/pypi/azure-servicefabric/5.6.130)
-  [azure-servicemanagement-legacy v0.20.x](https://pypi.python.org/pypi/azure-servicemanagement-legacy/0.20.6)
-  [azure-storage v0.34.x](https://pypi.python.org/pypi/azure-storage/0.34.2)
-  [azure-mgmt-authorization v0.30.x](https://pypi.python.org/pypi/azure-mgmt-authorization/0.30.0)
-  [azure-mgmt-batch v4.0.x](https://pypi.python.org/pypi/azure-mgmt-batch/4.0.0)
-  [azure-mgmt-cdn v0.30.x](https://pypi.python.org/pypi/azure-mgmt-cdn/0.30.3)
-  [azure-mgmt-cognitiveservices v1.0.x](https://pypi.python.org/pypi/azure-mgmt-cognitiveservices/1.0.0)
-  [azure-mgmt-compute v1.0.x](https://pypi.python.org/pypi/azure-mgmt-compute/1.0.0)
-  [azure-mgmt-containerregistry v0.2.x](https://pypi.python.org/pypi/azure-mgmt-containerregistry/0.2.1)
-  [azure-mgmt-datalake-analytics v0.1.x](https://pypi.python.org/pypi/azure-mgmt-datalake-analytics/0.1.4)
-  [azure-mgmt-datalake-store v0.1.x](https://pypi.python.org/pypi/azure-mgmt-datalake-store/0.1.4)
-  [azure-mgmt-devtestlabs v2.0.x](https://pypi.python.org/pypi/azure-mgmt-devtestlabs/2.0.0)
-  [azure-mgmt-dns v1.0.x](https://pypi.python.org/pypi/azure-mgmt-dns/1.0.1)
-  [azure-mgmt-documentdb v0.1.x](https://pypi.python.org/pypi/azure-mgmt-documentdb/0.1.3)
-  [azure-mgmt-iothub v0.2.x](https://pypi.python.org/pypi/azure-mgmt-iothub/0.2.2)
-  [azure-mgmt-keyvault v0.31.x](https://pypi.python.org/pypi/azure-mgmt-keyvault/0.31.0)
-  [azure-mgmt-logic v2.1.x](https://pypi.python.org/pypi/azure-mgmt-logic/2.1.0)
-  [azure-mgmt-network v1.0.x](https://pypi.python.org/pypi/azure-mgmt-network/1.0.0)
-  [azure-mgmt-rdbms v0.1.x](https://pypi.python.org/pypi/azure-mgmt-rdbms/0.1.0)
-  [azure-mgmt-redis v4.1.x](https://pypi.python.org/pypi/azure-mgmt-redis/4.1.0)
-  [azure-mgmt-resource v1.1.x](https://pypi.python.org/pypi/azure-mgmt-resource/1.1.0)
-  [azure-mgmt-scheduler v1.1.x](https://pypi.python.org/pypi/azure-mgmt-scheduler/1.1.2)
-  [azure-mgmt-sql v0.5.x](https://pypi.python.org/pypi/azure-mgmt-sql/0.5.1)
-  [azure-mgmt-storage v1.0.x](https://pypi.python.org/pypi/azure-mgmt-storage/1.0.0)
-  [azure-mgmt-trafficmanager v0.30.x](https://pypi.python.org/pypi/azure-mgmt-trafficmanager/0.30.0)
-  [azure-mgmt-web v0.32.x](https://pypi.python.org/pypi/azure-mgmt-web/0.32.0)

More packages are available, but they are in preview with not enough tests currently and are not included in this bundle.

## 2016-08-30 Version 2.0.0rc6 / 0.30.0rc6

**Disclaimer**

Starting with this release, most packages now use the MIT license. The following packages still remain on the Apache license:

- azure-servicebus
- aure-servicemanagement-legacy
- azure-storage

The following packages have the same content than RC5, but with MIT licence as header:

- azure-mgmt-cognitiveservices 0.30.0rc6
- azure-mgmt-commerce 0.30.0rc6
- azure-mgmt-dns 0.30.0rc6
- azure-mgmt-notificationhubs 0.30.0rc6
- azure-mgmt-powerbiembedded 0.30.0rc6
- azure-mgmt-trafficmanager 0.30.0rc6

**Breaking changes**

- azure-mgmt-storage 0.30.0rc6: fix usage list syntax (https://github.com/Azure/azure-rest-api-specs/issues/340)
- azure-mgmt-web 0.30.0rc6: fix list syntax (https://github.com/Azure/azure-rest-api-specs/pull/454)
- azure-mgmt-logic 1.0.0: New API Version implies several changes to catch up latest Azure Portal behaviour.
- azure-mgmt-scheduler 1.0.0: New API Version implies several changes to catch up latest Azure Portal behaviour.

Some values that are constants and were incorrectly suggested as method parameter have been removed:

- azure-mgmt-compute 0.30.0rc6: api_version is now an attribute and not a method parameter (#697)
- azure-mgmt-cdn 0.30.0rc6: check_name_availability has no more a type parameter
- azure-mgmt-keyvault 0.30.0rc6: Sku has no more a family parameter (#733)

**New and bugfixes**

- azure-mgmt-resource 0.30.0rc6:

  - Property aliases support
  - Doc typo
  - Parenthesis support in RG name (https://github.com/Azure/azure-rest-api-specs/pull/490)
  - New API version for subscription

- azure-mgmt-network 0.30.0rc6: `check_ip_address_availability` and more + Doc typo
- azure-mgmt-redis 1.0.0: official stable release (same content than 0.30.0RC5)

**Meta-package**

The 2.0.0rc6 is a release candidate. However, the core packages, from code quality/completeness perspectives can at this time
be considered "stable" - it will be officially labeled as such in September (in sync with other languages).
We are not planning on any further major changes until then.

The azure 2.0.0rc6 package contains the following Azure packages:

- The following packages are still labeled "preview" but can be considered "stable":

  - azure-mgmt-resource 0.30.0rc6
  - azure-mgmt-compute 0.30.0rc6
  - azure-mgmt-network 0.30.0rc6
  - azure-mgmt-storage 0.30.0rc6
  - azure-mgmt-keyvault 0.30.0rc6

- The following packages are already released as "stable" and are officially production ready:

  - azure-batch 1.0.0
  - azure-mgmt-batch 1.0.0
  - azure-mgmt-redis 1.0.0
  - azure-mgmt-logic 1.0.0
  - azure-mgmt-scheduler 1.0.0
  - azure-servicebus 0.20.3
  - azure-servicemanagement-legacy 0.20.4
  - azure-storage 0.33.0

The following packages are also available as preview only, not ready for production,
and will NOT be installed with the 2.0.0rc6 "azure" meta-package. We removed then from the 2.0.0rc6
to prepare our customers to the 2.0.0 stable release that will only contains the stable packages
listed before.

- azure-graphrbac 0.30.0rc5
- azure-mgmt-authorization 0.30.0rc5
- azure-mgmt-cdn 0.30.0rc6
- azure-mgmt-cognitiveservices 0.30.0rc6
- azure-mgmt-commerce 0.30.0rc6
- azure-mgmt-dns 0.30.0rc6
- azure-mgmt-iothub 0.1.0
- azure-mgmt-notificationhubs 0.30.0rc6
- azure-mgmt-powerbiembedded 0.30.0rc6
- azure-mgmt-trafficmanager 0.30.0rc6
- azure-mgmt-web 0.30.0rc6


## 2016-08-01 azure-servicemanagement-legacy 0.20.4

**Bugfix**

* Incomplete parsing if XML contains namespace #257 #707

**New**

* Associate/Dissociate Reserved IP #695 #716

Thank you to brandondahler, schaefi for their contributions.

## 2016-06-28 Service Bus 0.20.2

**Bugfix**

* New header in Rest API which breaks the SDK #658 #657

## 2016-06-23 Version 2.0.0rc5 / 0.30.0rc5

**Disclaimer**

* There is some breaking changes in the Storage client, due to the update the latest API-Version.
* There is some breaking changes in the GraphRbac client, due to the update the latest API-Version.
  This is an example of change on our tests:
  https://github.com/Azure/azure-sdk-for-python/commit/b03cae526d9ac46d1b477840f15d3729aa0d939f#diff-296e794143f66af83d1bf2db6eb7a935

**Bugfixes**

* Each package has now a correct `__version__` attribute which contains the package version.
* Fixed serialization of continuation tokens containing '.' (batch libraries)

**New**

* New PowerBI Embeddeded preview client
* New Cognitive Services preview client

## 2016-05-24 Version 2.0.0rc4 / 0.30.0rc4

**Disclaimer**

* There is a breaking change in all Client __init__ methods. Configuration classes have disappeared.
  Update this::

    resource_client = ResourceManagementClient(
        ResourceManagementClientConfiguration(
            credentials,
            subscription_id
        )
    )

  to this::

    resource_client = ResourceManagementClient(
        credentials,
        subscription_id
    )

  If you were using the Configuration class, it is still available using the `config` attribute after Client creation::

    resource_client.config.long_running_operation_timeout = 5

**New**

* you can now simplify your call by passing a dict directly and not an instance. This removes the needs to import each model::

    from azure.mgmt.resource.resources.models import ResourceGroup

    resource_client.resource_groups.create_or_update(
        group_name,
        ResourceGroup(
            location='westus',
        )
    )

  can now be written directly::

    resource_client.resource_groups.create_or_update(
        group_name,
        {
            'location':'westus',
        }
    )

* All Resources clients have now alias in the azure.mgmt.resource namespace::

    azure.mgmt.resource.FeatureClient
    azure.mgmt.resource.ManagementLockClient
    azure.mgmt.resource.PolicyClient
    azure.mgmt.resource.ResourceManagementClient
    azure.mgmt.resource.SubscriptionClient

* Enum refactoring. There are now two kinds of enum: "strict" and "soft".

  A "soft" enum can be substituted by any random string without risking a client-side exception. This is useful for
  services which might add new enum types frequently (e.g. VirtualMachine size). The server might decide to refuse our string and
  you might receive a CloudError exception.

  A "strict" enum must follow one of the authorized enum values. Strings are still accepted, but if your value is not valid
  you will receive a SerializationError *without* a call to the REST API. Before, the call was made to the REST API and you received
  a `CloudError` if the server refused the request.

* Latest Swagger update for Redis (API-version 2016-04-01)
* Latest Swagger update for GraphRbac (API-version 1.6)
* Latest Swagger update for CDN (API-version 2016-04-02)
* New Resource Policy client
* New Compute Container client
* New azure-mgmt-commerce preview package for Billing API

**Dependencies**

* msrest must be >= 0.4.0 (see their ChangeLog for details)
* msrestazure must be >= 0.4.0 (see their ChangeLog for details)
* azure-common[autorest] == 1.1.4, provides automatic autorest right dependencies
* azure-storage 0.32.0

  * [Check the ChangeLog on storage github account for details](https://github.com/Azure/azure-storage-python/releases).


## 2016-04-26 Version 2.0.0rc3 / 0.30.0rc3

**Disclaimer**
There is no known breaking changes between 2.0.0RC2 and 2.0.0RC3.
However, we removed several useless parameters for __init__ methods on model classes. If you get an error message like this after migrating to RC3::

    TypeError: __init__() got an unexpected keyword argument 'type'

or::

    TypeError: __init__() takes exactly 1 positional argument (2 given)

You can remove the involved parameter safely, as it should not have been there in the first place.

**New**

* Batch / Batch Management are installed with the azure meta-package
* Type checking improvement in Client
* Latest Swagger update for Compute (Hardware profile update)
* Latest Swagger update for Redis (force-reboot)
* `azure` now installs azure-servicemanagement-legacy 0.20.3
* `azure` now installs azure-storage 0.31.0

**Dependencies**

* msrest must be >= 0.3.0 (see their ChangeLog for details)
* msrestazure must be >= 0.3.0 (see their ChangeLog for details)
* azure-common[autorest] == 1.1.3, provides automatic autorest right dependencies
* azure-storage 0.31.0

  * [Check the ChangeLog on storage github account for details](https://github.com/Azure/azure-storage-python/releases).

## 2016-03-31 azure-servicemanagement-legacy 0.20.3

New:
* #519 Add support for the OSImage /details endpoint

## 2016-03-29 Version 2.0.0rc2 / 0.30.0rc2

**New**

* Latest Swagger update for CDN (minor fixes, documentation)
* Latest Swagger update for Compute (API-version 2016-03-30, minor fixes, documentation)
* Latest Swagger update for Network (API-version 2016-03-30, minor fixes, documentation)
* Latest Swagger update for Resources (API-version 2016-02-01, export_template, minor fixes, documentation)
* Rename resource/locks client from LockManagementClient to ManagementLockClient
* Latest Swagger update for Webapps  (minor fixes, documentation)

**Bugfixes**

* #552 #536 Broken parameters in some Network models
* Raw=true in async methods now returns the direct server answer, not an AzureOperationPoller instance

**Dependencies**

* msrest must be >= 0.2.0 (see their ChangeLog for details)
* msrestazure must be >= 0.2.0 (see their ChangeLog for details)
* azure-common[autorest] == 1.1.2, provides automatic autorest right dependencies

**Misc**

* The AzureResourceViewer example in the 'example' folder has been updated to SDK 2.0.0rc2

## 2016-03-04 Version 2.0.0rc1 / 0.30.0rc1

**New**

* Lastest Swagger update for CDN (endpoint create/update fix).
* Lastest Swagger update for ARM VMScaleSet (reimage, redeploy).
* Lastest Swagger update for ARM VirtualMachine (minor fixes, redeploy).
* Lastest Swagger update for ARM Storage (minor fixes).
* Lastest Swagger update for ARM Apps Logic (minor fixes).
* Lastest Swagger update for ARM Web Apps (recommendation API).
* Rename resource/authorization to resource/locks
* Any default tags in the swagger spec are used as defaults for named args.
* 'Azure-SDK-for-Python' is added to the user-agent of each generated libraries.
* Base class Paged now inherits from collections.Iterable.
* odata filters are now taken as string directly

**azure-common 1.1.0**

* add exceptions/credentials aliases in azure.common

**Dependencies**

* msrest/msrestazure must be >= 0.1.0 (see their ChangeLog for details)

## 2016-02-18 Version 2.0.0a1

**DISCLAIMER**

This is an alpha release. Future releases may introduce some breaking changes.
Some of the new generated libraries have not yet been tested extensively, and some have known issues (such as azure-mgmt-web).
Our goal is to release a stable version by the end of March 2016.  Please send us your feedback!

**WHAT'S NEW**

* New ARM generated code based on [Swagger specification of the Azure REST APIs](https://github.com/Azure/azure-rest-api-specs)
* New libraries

  * Azure Active Directory Graph API
  * Authorization: permissions, subscriptions, roles and more
  * CDN: profiles, endpoints creation and more
  * Apps:

    * Logic Apps: Workflow and job management
    * Web Apps: App Service Plan, web sites, certificate, domains and more

  * Notification Hubs: Namespaces, hub creation/deletion and more
  * Redis: create cache and more
  * Scheduler: create job collections, create job and more

* Enhanced libraries compared to 1.0.0 preview

  * Storage: create storage accounts, list keys, and more
  * Resource:

    * resources : create resource groups, register providers and more
    * features : manage features of provider and more
    * authorization : manage resource group lock and more
    * subscriptions : manage subscriptions and more

  * Network: create virtual networks, network interfaces, public ips and more
  * Compute: create virtual machines and more

**BREAKING CHANGES**

~~We made our possible to document the breaking from ARM 1.0.0 version to 2.0.0 here.~~
The previously-linked documentation is no longer available.

**Dependencies**

azure-storage 0.30.0
  * Major version. [Check the ChangeLog on storage github account for details](https://github.com/Azure/azure-storage-python/releases).

## 2016-01-20 Version 1.0.3

**Bugfixes**

azure-mgmt-compute 0.20.1
  * #510 Missing "statuses" property in VirtualMachineInstanceView

azure-servicemanagement-legacy 0.20.2
  * #487 #488 Add StaticVirtualNetworkIPAddress to network configuration
  * #497      Add replicate_vm_image, unreplicate_vm_image, share_vm_image
  * #501 #511 Add update_os_image_from_image_reference

**Misc**

  * #491 #502 #422 Update documentation
  * Update azure-storage dependency to 0.20.3
  * Update azure-mgmt dependency to 0.20.2

Thank you to bear454, ekesken, kingliantop, mamoo, schaefi for their contributions.


## 2015-10-02 Version 1.0.2

azure-mgmt-network 0.20.1
  * Fix retry timeout default value for long running operations

azure-mgmt-resource 0.20.1
  * Add missing model class ResourceIdentity
  * Add documentation examples for generic resource creation and deployment
    using JSON templates

azure-storage 0.20.2
  * Fix SAS encoding to work with premium storage

Thank you to aarsan, trondhindenes for their contributions.


## 2015-09-14 Version 1.0.1

* Use requests library by default in all libraries
  * Exception is azure-servicemanagement-legacy which can use requests or winhttp
  * Proxies that are automatically detected by requests don't require set_proxy call anymore
* Fix dependencies for azure-storage by using separate 2.x and 3.x wheels


## 2015-08-31 Version 1.0.0

**UPGRADE**

If you are upgrading from v0.11.x or earlier, make sure to uninstall that
version before installing the latest release.

**WHAT'S NEW**

* Preliminary Azure Resource Manager (ARM) support.
  Manage your Azure compute, network and storage resources.
  This is a preview and is subject to changes in future releases.
* Azure Storage File support.
* Azure library is now more modular. You can choose to install bundles
  or install only the packages you need. Packages now available on PyPI::

    azure (bundle)
      azure-mgmt (bundle)
        azure-mgmt-compute
        azure-mgmt-network
        azure-mgmt-resource
        azure-mgmt-storage
      azure-servicebus
      azure-servicemanagement-legacy
      azure-storage

* Azure Storage has moved.
    https://github.com/Azure/azure-storage-python

**Bugfixes**

* #437 Make delete_storage_account return async request id
* #435 Add complete flag to delete_role
* #448 Cast authorization code from unicode to string
* #395 Azure.Storage Python 2.6 compatibility

**BREAKING CHANGES**

The following were renamed and moved from 'azure' to 'azure.common'::
    WindowsAzureError                -> AzureException and AzureHttpError
    WindowsAzureConflictError        -> AzureConflictHttpError
    WindowsAzureMissingResourceError -> AzureMissingResourceHttpError

The following were renamed and moved from 'azure' to 'azure.servicemanagement'::
    WindowsAzureAsyncOperationError  -> AzureAsyncOperationHttpError

The following were renamed and moved from 'azure' to 'azure.storage'::
    WindowsAzureBatchOperationError  -> AzureBatchOperationError

The following have moved from 'azure' to 'azure.servicemanagement'::
    DEFAULT_HTTP_TIMEOUT
    MANAGEMENT_HOST

The following have moved from 'azure' to 'azure.servicebus'::
    DEFAULT_HTTP_TIMEOUT
    SERVICE_BUS_HOST_BASE

The following have moved from 'azure' to 'azure.storage'::
    DEFAULT_HTTP_TIMEOUT
    DEV_ACCOUNT_NAME
    DEV_ACCOUNT_KEY

The following have moved from 'azure.storage' to 'azure.storage.blob'::
    BLOB_SERVICE_HOST_BASE
    DEV_BLOB_HOST
    BlobService
    ContainerEnumResults
    Container
    Properties
    BlobEnumResults
    BlobResult
    Blob
    BlobProperties
    BlobPrefix
    BlobBlock
    BlobBlockList
    PageRange
    PageList
    ContainerSharedAccessPermissions
    BlobSharedAccessPermissions

The following have moved from 'azure.storage' to 'azure.storage.queue'::
    QUEUE_SERVICE_HOST_BASE
    DEV_QUEUE_HOST
    QueueService
    QueueEnumResults
    Queue
    QueueMessagesList
    QueueMessage
    QueueSharedAccessPermissions

The following have moved from 'azure.storage' to 'azure.storage.table'::
    TABLE_SERVICE_HOST_BASE
    DEV_TABLE_HOST
    TableService
    Entity
    EntityProperty
    Table
    TableSharedAccessPermissions

Thank you to Sabbasth, schaefi, feoff3, JamieCressey for their contributions.


## 2015-06-16 Version 0.11.1

 * Azure storage connection string support
 * Add a request_session parameter to storage and service bus classes
 * Fixes for bugs:
   #370 Fix table service authentication for non-english locale
   #380 Make protocol string case insensitive
   #376 Make pyopenssl dependency optional
   #360 Installing `azure` on Python 3 should not install futures

Thank you to rchamorro, drdarshan, hosungs, h_yamaki for their contributions.

## 2015-05-13 Version 0.11.0

**IMPORTANT CHANGE THAT AFFECTS STORAGE**

The API for creating shared access signatures has changed. The new API enables
easy production AND consumption of SAS for blob, queue and table storage.

 * To produce a SAS, use generate_shared_access_signature on
   BlobService/QueueService/TableService
 * To consume a SAS, init BlobService/QueueService/TableService with
   account_name & sas_token (no account_key)
 * For blob storage, you can now pass a sas_token to make_blob_url
 * For blob storage, you can now consume public containers/blobs, init
   BlobService/QueueService/TableService with account_name only
   (no account_key or sas_token)

**Other changes**

 * Create/list/delete job functionality added to SchedulerManagementService
 * update_site added to WebsiteManagementService to start/stop web sites
 * Target x-ms-version 2014-10-01 for service management
 * Add virtual IP fields in Deployment
 * Make cloud service create/delete async
 * Delete cloud service now supports deleting blobs from storage
 * Support for specifying SourceMediaLink for DataVirtualHardDisks

 * Fixes for bugs:
   #350 wait_for_operation needs to flush as it prints

Thank you to lmazuel, antonydenyer, zlike-msft, melor and amegianeg for their
contributions.

## 2015-04-28 Version 0.10.2

**Bugfixes**

   #338 Version 0.10.0 fails with 'SocketReader' object has no attribute 'tell'

## 2015-03-13 Version 0.10.0

**IMPORTANT CHANGE THAT AFFECTS STORAGE USERS (BLOB, QUEUE, TABLE)**

The library now targets x-ms-version '2014-02-14' of the storage REST API.
Previous version of the library targeted '2012-02-12'.

The upgrade to this new version causes some breaking changes for Python SDK users:

* Metrics for blob, queue, table service properties, which used to be accessed
  with the 'metrics' field are now accessed via 'hour_metrics' and 'minute_metrics'.
  Note that a backwards compatible 'metrics' property was added to redirect access
  to 'hour_metrics'.
* Url is no longer returned from list_containers, list_blobs, list_queues.
  For blob, you can use the utility function make_blob_url as an alternate
  way to get a URL.

See MSDN documentation for details on REST API changes:

* in '2013-08-15': https://msdn.microsoft.com/library/azure/dn592124.aspx
* in '2014-02-14': https://msdn.microsoft.com/library/azure/dd894041.aspx


The other changes in this release are:

* Performance improvements in xml deserialization of storage and service bus
  Table storage query_entities is ~25X faster for the maximum of 1000 entities
* Ability to upload and download blobs using multiple connections, along with
  retries when a chunk upload/download failure occurs
  Controlled via the max_connections, max_retries, retry_wait parameters
* Use get_certificate_from_publish_settings to get a .pem certificate from
  your azure publish settings file
* Ability to adjust the global http timeout
* Service bus event hub support (create/update/delete hubs + send events)

**Bugfixes**

* #237 Ability to use multiple connections to upload blob chunks in parallel
* #254 Improve performance of table storage (and more?)
* #258 Support authenticating with azureProfile like in CLI tools
* #259 Unicode error is raised instead of actual error
* #263 Change description name
* #268 delete_deployment does not pass comp=media to delete disks
* #271 Update current_name so that multiple parameters with the same name...
* #270 Documentation for capture_vm_image is incorrect
* #273 Unicode error with utf-8 encoding value
* #276 Service Mgmt - Reserved IP create/delete are async
* #280 add support for setting IdleTimeoutInMinutes on load balanced endpoint
* #288 InvalidHeaderValue on BlobService example
* #294 Upload of large files is too slow
* #304 Unable to upload large size files to Azure Page Blob

Thank you to lmazuel, rhaps0dy, timfpark, gaellbn, moutai, edevil, rjschwei and
okaram for their contributions.

## 2014-11-21 Version 0.9.0

**IMPORTANT CHANGE IN BEHAVIOR THAT AFFECTS TABLE STORAGE USERS**

The library now converts any datetime object in an entity to UTC before writing
the value to Azure, and it sets the timezone (tzinfo) to UTC on the entities
it reads from Azure. On a related note, python-dateutil is now an external
dependency.

The other changes in this release are:

* Ability to pass in to management APIs a Session object from the requests
  library (or any compatible). This allows more flexibility for authentication,
  including oauth.
* New service management APIs

  - list_role_sizes
  - list_subscriptions (oauth only)
  - rebuild_role_instance
  - delete_role_instances
  - create_reserved_ip_address
  - delete_reserved_ip_address
  - get_reserved_ip_address
  - list_reserved_ip_addresses
  - add_dns_server
  - update_dns_server
  - delete_dns_server
  - list_resource_extensions
  - list_resource_extension_versions
  - capture_vm_image
  - delete_vm_image
  - list_vm_images
  - create_vm_image
  - update_vm_image
* Enhanced service management APIs

  - create_virtual_machine_deployment / add_role

    - custom data
    - additional windows unattend content
    - create from a vm image
    - public ips
    - resource extensions
    - create from remote os image
    - provision guest agent
    - dns servers
    - reserved ip

  - update_role

    - resource extensions
    - provision guest agent

  - create_storage_service

    - account_type replaces geo_replication_enabled (preserved for backwards compat)

* Preliminary Scheduler management API
* Add metrics to Service Bus management API
* Delete Blob - support for x-ms-delete-snapshots header

**Bugfixes**

* #221 Topic names containing slash
* #234 AttributeError on Timestamp property
* #212 Storage: Timstamp's microseconds value out of range
* #116 def _from_entity_datetime(value) in __init__.py returns 7 for seconds
* #114 Timezone information 'Z' is ignored during parsing of datetime of table entity

Thank you to Costeijn, lmazuel, pneumee, nicbon, bndw, troyanov for their contributions.

## 2014-09-19 Version 0.8.4

* Add ability to get website publish data as an object (thanks lmazuel)

**Bugfixes**

* #216 Daylight saving problem in ServiceBusSASAuthentication
* #218 Content type incorrect on blob

## 2014-09-09 Version 0.8.3

* Add Shared Access Signature support to Service Bus

## 2014-08-26 Version 0.8.2

 * Add functionality to Service Bus Management API

   - list queues/topics/notification hubs/relays

 * Add CreationTime to StorageAccountProperties
 * Preliminary SQL Database Management API
 * Preliminary Website Management API

   - list/get webspaces
   - list/get/create/delete/restart website
   - get historical usage metrics and metric definitions
   - get publish profile xml

**Bugfixes**

* #192 Fix deserialization of broker properties for service bus.
* #173 Fix some incompatibilities with Python 2.6

Thank you to lmazuel for the contributions to SQL Database, Service Bus and
Website management.

## 2014-06-26 Version 0.8.1

**Bugfixes**

* #149 Table storage batch client doesn't validate etag
* #129 Inconsistent WindowsAzure Errors

Thank you to kaptajnen, matlockx for their fixes for the redirection issue (#129).

## 2014-03-31 Version 0.8.0

 * Existing service management API now targets x-ms-version 2013-06-01

**Bugfixes**

* #145 Missing DataVirtualHardDisks in Cloud Service Properties
* #144 Added configuration sets for role and added list virtual network function
* #139 How to start "Deallocated" role
* #127 Add WinRM options to create_virtual_machine_deployment()
* #131 Missing role instance endpoint in get_deployment_by_X
* #128 Update __init__.py for missing host_name attribute on RoleInstance
* #140 Table Service deletes empty strings
* #40  Edm.Binary and null support in table storage entities

## 2014-02-10 Version 0.8.0pr1

 * Migrate to using httplib on Windows. This is now the default, unless a
   Windows Certificate Store management certificate is used. Make sure to use
   CPython 2.7.4 or later when using OpenSSL .pem certificates on Windows.
 * Added high-level functions to upload/download blobs with chunking and progress notifications
 * Added support for Python 3.3
 * Updated storage API to 2012-02-12
   - Adds more lease functionality
   - Adds cross-storage account copy
   - Adds a helper function make_blob_url to pass to copy_blob for x_ms_copy_source
 * Fixes WindowsAzureConflictError and WindowsAzureMissingResourceError to properly set the error message, and use the additional info returned by the server
 * Fixes for bugs:
   #125 Label for VM Deployment should not be b64 encoded (thanks to jeffmendoza).
   #121 In blob storage, put_page, x-ms-if-sequence-number-lte header should be x-ms-if-sequence-number-le

## 2013-11-06 Version 0.7.1

**Bugfixes**

* #118 Proxy doesn't support specifying credentials
* #117 Service bus authorization code doesn't go through the proxy server
* #108 Create VM, Administrator Password Base-64 Encoding
* #106 Why isn't setup.py in the root of the project?
* #96  Change default connection protocol to https

## 2013-07-08 Version 0.7.0

 * Added service bus management API
 * Added support for list blobs delimiter (for easier hierarchical listings)
 * Cleanup of imports
 * Renamed some private functions that weren't starting with an underscore
 * Removed code generator (it's now obsolete, we make changes directly in the Python sources)

**Bugfixes**

* #90  get_blob_metadata returns more than the metadata (also get_container_metadata and get_queue_metadata)
* #87  Proxy support for \*NIX systems
* #86  Fix capitalization in the 'Fingerprint' tag for XML of serialization of SSH keys configuration
* #83  Fixed an issue that prevented the creation of endpoints for a VM
* #80  Error deserializing datetime value from Table Store
* #79  Specify VirtualNetworkName when creating Virtual Machine

Thank you to timanovsky, sebhomengo, pneumee, ogrisel, 0xc0decafe and apatard for their bug reports and fixes.

## 2013-03-20 Version 0.6.2

**Bugfixes**

* #75  crash on python 2.7 x64 windows
* #73  _convert_query_string return a wrong query string parameter

## 2012-12-17 Version 0.6.1

**Bugfixes**

* #69  _get_readable_id doesn't support queues with slashes in their names
* #68  Service bus cache of tokens doesn't support multiple creds in same app
* #66  Need to change the default timeout for httprequest on windows
* Improved support for unicode data

## 2012-10-16 Version 0.6.0

 * Added service management API
 * Added ability to specify custom hosts
 * Added proxy server support (HTTP CONNECT tunneling)

## 2012-06-06 Version 0.5.0

 * Initial Release

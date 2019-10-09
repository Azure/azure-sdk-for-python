====================
Azure SDK for Python
====================

.. important:: The most part of this documentation has moved to https://docs.microsoft.com/python/azure

The Azure SDK for Python is a set of libraries which allow you to work on Azure for your management, runtime or data needs.

For a more general view of Azure and Python, you can go on the `Python Developer Center for Azure <https://azure.microsoft.com/en-us/develop/python/>`_


Installation
------------

You can install individually each library for each Azure service:

.. code-block:: console

   $ pip install azure-batch          # Install the latest Batch runtime library
   $ pip install azure-mgmt-scheduler # Install the latest Storage management library

Preview packages can be installed using the ``--pre`` flag:

.. code-block:: console

   $ pip install --pre azure-mgmt-compute # will install only the latest Compute Management library

More details and information about the available libraries and their status can be found
in the :doc:`Installation Page<installation>`


System Requirements:
--------------------

The supported Python versions are 2.7.x, 3.4.x, 3.5.x, 3.6.x and 3.7.x
To download Python, please visit
https://www.python.org/download/


We recommend Python Tools for Visual Studio as a development environment for developing your applications.  Please visit http://aka.ms/python for more information.


Need Help?:
-----------

Be sure to check out the Microsoft Azure `Developer Forums on Stack
Overflow <http://go.microsoft.com/fwlink/?LinkId=234489>`__ if you have
trouble with the provided code.

Contribute Code or Provide Feedback:
------------------------------------

If you would like to become an active contributor to this project please
follow the instructions provided in `Microsoft Azure Projects
Contribution
Guidelines <http://windowsazure.github.com/guidelines.html>`__.

If you encounter any bugs with the library please file an issue in the
`Issues <https://github.com/Azure/azure-sdk-for-python/issues>`__
section of the project.


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
  :glob:
  :caption: User Documentation

  installation
  quickstart_authentication
  multicloud
  exceptions
  Service Management (Legacy) <servicemanagement>

.. toctree::
  :maxdepth: 5
  :glob:
  :caption: Client

  ref/azure-applicationinsights.rst
  ref/azure-batch.rst
  ref/azure-cognitiveservices-anomalydetector.rst
  ref/azure-cognitiveservices-knowledge-qnamaker.rst
  ref/azure-cognitiveservices-language-luis.rst
  ref/azure-cognitiveservices-language-spellcheck.rst
  ref/azure-cognitiveservices-language-textanalytics.rst
  ref/azure-cognitiveservices-search-autosuggest.rst
  ref/azure-cognitiveservices-search-customimagesearch.rst
  ref/azure-cognitiveservices-search-customsearch.rst
  ref/azure-cognitiveservices-search-entitysearch.rst
  ref/azure-cognitiveservices-search-imagesearch.rst
  ref/azure-cognitiveservices-search-newssearch.rst
  ref/azure-cognitiveservices-search-videosearch.rst
  ref/azure-cognitiveservices-search-visualsearch.rst
  ref/azure-cognitiveservices-search-websearch.rst
  ref/azure-cognitiveservices-vision-computervision.rst
  ref/azure-cognitiveservices-vision-contentmoderator.rst
  ref/azure-cognitiveservices-vision-customvision.rst
  ref/azure-cognitiveservices-vision-face.rst
  ref/azure-core.rst
  ref/azure-core-tracing-opencensus.rst
  ref/azure-cosmos.rst
  ref/azure-eventgrid.rst
  ref/azure-eventhub.rst
  ref/azure-graphrbac.rst
  ref/azure-identity.rst
  ref/azure-keyvault-keys.rst
  ref/azure-keyvault-secrets.rst
  ref/azure-loganalytics.rst
  ref/azure-servicebus.rst
  ref/azure-servicefabric.rst
  ref/azure-storage-blob.rst
  ref/azure-storage-file.rst
  ref/azure-storage-queue.rst


.. toctree::
  :maxdepth: 5
  :glob:
  :caption: Management

  ref/azure-mgmt-advisor.rst
  ref/azure-mgmt-alertsmanagement.rst
  ref/azure-mgmt-apimanagement.rst
  ref/azure-mgmt-applicationinsights.rst
  ref/azure-mgmt-authorization.rst
  ref/azure-mgmt-automation.rst
  ref/azure-mgmt-batch.rst
  ref/azure-mgmt-billing.rst
  ref/azure-mgmt-cdn.rst
  ref/azure-mgmt-cognitiveservices.rst
  ref/azure-mgmt-commerce.rst
  ref/azure-mgmt-consumption.rst
  ref/azure-mgmt-containerinstance.rst
  ref/azure-mgmt-containerregistry.rst
  ref/azure-mgmt-containerservice.rst
  ref/azure-mgmt-cosmosdb.rst
  ref/azure-mgmt-databricks.rst
  ref/azure-mgmt-datafactory.rst
  ref/azure-mgmt-datalake-analytics.rst
  ref/azure-mgmt-datalake-store.rst
  ref/azure-mgmt-datamigration.rst
  ref/azure-mgmt-devspaces.rst
  ref/azure-mgmt-devtestlabs.rst
  ref/azure-mgmt-dns.rst
  ref/azure-mgmt-eventgrid.rst
  ref/azure-mgmt-eventhub.rst
  ref/azure-mgmt-hanaonazure.rst
  ref/azure-mgmt-hdinsight.rst
  ref/azure-mgmt-imagebuilder.rst
  ref/azure-mgmt-iotcentral.rst
  ref/azure-mgmt-iothub.rst
  ref/azure-mgmt-iothubprovisioningservices.rst
  ref/azure-mgmt-keyvault.rst
  ref/azure-mgmt-kusto.rst
  ref/azure-mgmt-labservices.rst
  ref/azure-mgmt-loganalytics.rst
  ref/azure-mgmt-logic.rst
  ref/azure-mgmt-machinelearningcompute.rst
  ref/azure-mgmt-managementgroups.rst
  ref/azure-mgmt-managementpartner.rst
  ref/azure-mgmt-maps.rst
  ref/azure-mgmt-marketplaceordering.rst
  ref/azure-mgmt-media.rst
  ref/azure-mgmt-mixedreality.rst
  ref/azure-mgmt-monitor.rst
  ref/azure-mgmt-msi.rst
  ref/azure-mgmt-netapp.rst
  ref/azure-mgmt-network.rst
  ref/azure-mgmt-notificationhubs.rst
  ref/azure-mgmt-policyinsights.rst
  ref/azure-mgmt-powerbiembedded.rst
  ref/azure-mgmt-recoveryservices.rst
  ref/azure-mgmt-recoveryservicesbackup.rst
  ref/azure-mgmt-redis.rst
  ref/azure-mgmt-relay.rst
  ref/azure-mgmt-resource.rst
  ref/azure-mgmt-resourcegraph.rst
  ref/azure-mgmt-scheduler.rst
  ref/azure-mgmt-search.rst
  ref/azure-mgmt-security.rst
  ref/azure-mgmt-servermanager.rst
  ref/azure-mgmt-servicebus.rst
  ref/azure-mgmt-servicefabric.rst
  ref/azure-mgmt-signalr.rst
  ref/azure-mgmt-sql.rst
  ref/azure-mgmt-sqlvirtualmachine.rst
  ref/azure-mgmt-storage.rst
  ref/azure-mgmt-subscription.rst
  ref/azure-mgmt-trafficmanager.rst
  ref/azure-mgmt-web.rst


.. toctree::
  :maxdepth: 5
  :glob:
  :caption: Other

  ref/azure-appconfiguration.rst
  ref/azure-cognitiveservices-formrecognizer.rst
  ref/azure-cognitiveservices-inkrecognizer.rst
  ref/azure-cognitiveservices-personalizer.rst
  ref/azure-common.rst
  ref/azure-eventhub-checkpointstoreblob-aio.rst
  ref/azure-keyvault-certificates.rst
  ref/azure-mgmt.rst
  ref/azure-mgmt-appconfiguration.rst
  ref/azure-mgmt-attestation.rst
  ref/azure-mgmt-botservice.rst
  ref/azure-mgmt-compute.rst
  ref/azure-mgmt-costmanagement.rst
  ref/azure-mgmt-datashare.rst
  ref/azure-mgmt-deploymentmanager.rst
  ref/azure-mgmt-documentdb.rst
  ref/azure-mgmt-edgegateway.rst
  ref/azure-mgmt-frontdoor.rst
  ref/azure-mgmt-healthcareapis.rst
  ref/azure-mgmt-machinelearningservices.rst
  ref/azure-mgmt-managedservices.rst
  ref/azure-mgmt-peering.rst
  ref/azure-mgmt-privatedns.rst
  ref/azure-mgmt-rdbms.rst
  ref/azure-mgmt-reservations.rst
  ref/azure-mgmt-serialconsole.rst
  ref/azure-mgmt-storagecache.rst
  ref/azure-mgmt-storagesync.rst
  ref/azure-servicemanagement-legacy.rst
  ref/azure-template.rst


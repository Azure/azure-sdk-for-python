Installation
============

Installation with pip
---------------------

You can install each Azure service's library individually:

.. code-block:: console

   $ pip install azure-batch          # Install the latest Batch runtime library
   $ pip install azure-mgmt-scheduler # Install the latest Storage management library

Preview packages can be installed using the ``--pre`` flag:

.. code-block:: console

   $ pip install --pre azure-mgmt-compute # will install only the latest Compute Management library


You can also install a set of Azure libraries in a single line using the ``azure`` meta-package. 

.. code-block:: console

   $ pip install azure
   
We publish a preview version of this package, which you can access using the `--pre` flag:

.. code-block:: console

   $ pip install --pre azure

Available packages
------------------

Stable packages
~~~~~~~~~~~~~~~

===================================== =======
Package name                          Version
===================================== =======
azure-batch                           3.0.0
azure-mgmt-batch                      4.0.0
azure-mgmt-cognitiveservices          1.0.0
azure-mgmt-devtestlabs                2.0.0
azure-mgmt-dns                        1.0.1
azure-mgmt-logic                      2.1.0
azure-mgmt-redis                      4.1.0
azure-mgmt-scheduler                  1.1.2
azure-mgmt-servermanager              1.0.0
azure-servicebus                      0.21.1
azure-servicefabric                   5.6.130
azure-servicemanagement-legacy        0.20.6
azure-storage                         0.33.0
===================================== =======

Preview packages
~~~~~~~~~~~~~~~~

===================================== =========
Package name                          Version  
===================================== =========
azure-keyvault                        0.3.4
azure-monitor                         0.3.0
azure-mgmt-resource                   1.1.0
azure-mgmt-compute                    1.0.0
azure-mgmt-network                    1.0.0
azure-mgmt-storage                    1.0.0
azure-mgmt-keyvault                   0.31.0
azure-graphrbac                       0.30.0
azure-mgmt-authorization              0.30.0
azure-mgmt-cdn                        0.30.3
azure-mgmt-containerregistry          0.2.1
azure-mgmt-commerce                   0.30.0rc6
azure-mgmt-datalake-analytics         0.1.4
azure-mgmt-datalake-store             0.1.3
azure-mgmt-documentdb                 0.1.3
azure-mgmt-eventhub                   0.2.0
azure-mgmt-iothub                     0.2.2
azure-mgmt-media                      0.1.1
azure-mgmt-monitor                    0.2.1
azure-mgmt-notificationhubs           0.30.0
azure-mgmt-powerbiembedded            0.30.0rc6
azure-mgmt-search                     0.1.0
azure-mgmt-servicebus                 0.1.0
azure-mgmt-sql                        0.5.1
azure-mgmt-trafficmanager             0.30.0
azure-mgmt-web                        0.32.0
===================================== =========

Install from Github
-------------------

If you want to install ``azure`` from source::

    git clone git://github.com/Azure/azure-sdk-for-python.git
    cd azure-sdk-for-python
    python setup.py install
	
The ``dev`` branch contains the work in progress.

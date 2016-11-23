Installation
============

Installation with pip
---------------------

You can install individually each library for each Azure service:

.. code-block:: console

   $ pip install azure-batch          # Install the latest Batch runtime library
   $ pip install azure-mgmt-scheduler # Install the latest Storage management library

Preview packages can be installed using the ``--pre`` flag:

.. code-block:: console

   $ pip install --pre azure-mgmt-compute # will install only the latest Compute Management library


You can also install a set of Azure libraries in a single line using the ``azure`` meta-package. Since not all packages in this meta-package are
published as stable yet, the ``azure`` meta-package is still in preview. 
However, the core packages, from code quality/completeness perspectives can at this time be considered "stable" 
- it will be officially labeled as such in sync with other languages as soon as possible. 
We are not planning on any further major changes until then.

Since it's a preview release, you need to use the ``--pre`` flag:

.. code-block:: console

   $ pip install --pre azure
   
or directly

.. code-block:: console

   $ pip install azure==2.0.0rc6

.. important:: The azure meta-package 1.0.3 is deprecated and is not working anymore.
   
Available packages
------------------

Stable packages
~~~~~~~~~~~~~~~

===================================== =======
Package name                          Version
===================================== =======
azure-batch                           1.1.0
azure-mgmt-batch                      2.0.0
azure-mgmt-devtestlabs                1.0.0
azure-mgmt-logic                      1.0.0
azure-mgmt-redis                      2.0.0
azure-mgmt-scheduler                  1.0.0
azure-mgmt-servermanager              1.0.0
azure-servicebus                      0.20.3
azure-servicemanagement-legacy        0.20.5
azure-storage                         0.33.0
===================================== =======

Preview packages
~~~~~~~~~~~~~~~~

===================================== =========
Package name                          Version  
===================================== =========
azure-monitor                         0.1.0
azure-mgmt-resource                   0.31.0
azure-mgmt-compute                    0.32.0
azure-mgmt-network                    0.30.0
azure-mgmt-storage                    0.30.0rc6
azure-mgmt-keyvault                   0.30.0
azure-graphrbac                       0.30.0rc6
azure-mgmt-authorization              0.30.0rc6
azure-mgmt-cdn                        0.30.0rc6
azure-mgmt-cognitiveservices          0.30.0rc6
azure-mgmt-containerregistry          0.1.0
azure-mgmt-commerce                   0.30.0rc6
azure-mgmt-datalake-analytics         0.1.0
azure-mgmt-datalake-store             0.1.0
azure-mgmt-dns                        0.30.0rc6
azure-mgmt-eventhub                   0.1.0
azure-mgmt-iothub                     0.1.0
azure-mgmt-media                      0.1.0
azure-mgmt-notificationhubs           0.30.0
azure-mgmt-powerbiembedded            0.30.0rc6
azure-mgmt-servicebus                 0.1.0
azure-mgmt-sql                        0.1.0
azure-mgmt-trafficmanager             0.30.0rc6
azure-mgmt-web                        0.30.1
===================================== =========

Install from Github
-------------------

If you want to install ``azure`` from source::

    git clone git://github.com/Azure/azure-sdk-for-python.git
    cd azure-sdk-for-python
    python setup.py install
	
The ``dev`` branch contains the work in progress.

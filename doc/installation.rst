Installation
============

Installation with pip
---------------------

You can install the whole set of stable Azure libraries in a single line:

.. code-block:: console

   $ pip install azure

You can also install individually each library if you don't need everything
and want to save installation space/time.

.. code-block:: console

   $ pip install azure-storage # Will install the latest Storage runtime library
   $ pip install azure-mgmt-storage # Will install the latest Storage management library
   $ pip install azure-mgmt-resource # will install only the latest Resource Management library

Preview packages are not included in the ``azure`` package and can be installed using the ``--pre`` flag.
These packages could have minor breaking changes until the stable release.
Some of the new generated libraries have not yet been tested extensively, and some have known issues.

.. code-block:: console

   $ pip install --pre azure-mgmt-web # will install only the latest Resource Management library

Packages available
------------------

FIXME
   
   

Install from Github
-------------------

If you want to install ``azure`` from source::

    git clone git://github.com/Azure/azure-sdk-for-python.git
    cd azure-sdk-for-python
    python setup.py install
	
The ``dev`` branch contains the work in progress.
